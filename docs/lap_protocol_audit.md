# Lap Detection Protocol Audit

## Executive Summary

This audit traces the complete lap detection lifecycle across the real Arduino firmware, the RC AI Java layer, and the Python emulator. It identifies all divergences and ranks them by probability of causing the observed symptoms.

**Primary finding:**  
There are **two independent root causes** that together explain all four observed symptoms. GAP-001 (TIME_RESET flush) is the secondary cause. The **primary cause** is a PIN INDEX MISMATCH between what RC AI expects and what the emulator sends.

---

## 1. Real Lap Generation Sequence

### 1.1 Startup: Pin Configuration

**Java — `sendPinMode()` (ArduinoProtocol.java L609–674):**

After version verification, RC AI sends a `PI` (PIN_MODE_READ) command containing a list of pins. The **byte sent for each pin is the index `i` in the `digitalIds` list**, not the physical pin number:

```java
for (int i = 0; i < config.digitalIds.size(); i++) {
    int id = config.digitalIds.get(i);
    if (ArduinoConfig.getPinMode(id) == mode) {
        message[idx++] = DIGITAL;
        message[idx++] = (byte) i;  // ← INDEX, not physical pin number
    }
}
```

**Arduino firmware — `processPinModeRequest()` (sketch.ino L978–1022):**

The Arduino receives the `PI` command and stores the received bytes directly as physical pin numbers:

```c
int pin = inBuffer[iBufIndex + 1] TXT_TO_INT_CONVERSION;
pReadPins[i] = pin;
pinMode(pin, mode);
```

So when RC AI sends `D 0`, the Arduino configures physical pin 0 as an input. When RC AI sends `D 1`, the Arduino configures physical pin 1. The **index from the list becomes the physical pin on the Arduino**.

After configuring all read pins, the firmware sets `bReset = true`.

---

### 1.2 Initial State Broadcast

**Arduino firmware — `loop()` (sketch.ino L500–513):**

```c
for (int i = 0; i < iNumReadPins; i++) {
    handleDebounce(i, ulCurTimeUs, ulDeltaUs);
    iPinSignal = digitalRead(pReadPins[i]);

    if (bReset) {
        sendStateChange(i, iPinSignal, ulCurTimeMs);
    } else if (iPinSignal != pLastReadSignal[i]) {
        setupStateChange(i, iPinSignal, ulCurTimeMs);
    }
    pLastReadSignal[i] = iPinSignal;
}
bReset = false;
```

On the first loop iteration after pin configuration, the firmware reads each physical pin and calls `sendStateChange(i, ...)` — where `i` is the **loop index**, not the pin number.

**Arduino firmware — `sendStateChange()` (sketch.ino L641–682):**

```c
void sendStateChange(int pinIndex, int pinState, unsigned long ulCurTimeMs) {
    byte pinType = 0x44;
    byte pin = pReadPins[pinIndex];  // ← physical pin number from the array
    ...
    sendTime(ulCurTimeMs);
    inputChanged[1] = pinType;
    inputChanged[2] = pin;
    inputChanged[3] = pinState;
    Serial.write(inputChanged, sizeof(inputChanged));
}
```

The INPUT message sent to RC AI contains `pin = pReadPins[pinIndex]` — the **physical pin number** (e.g., 0, 1, 2, 3 as configured by the `PI` command, where index 0 becomes pin 0, index 1 becomes pin 1, etc.).

---

### 1.3 RC AI Pin Lookup Construction

**Java — `addPinConfigs()` (ArduinoProtocol.java L1075–1133):**

```java
for (int i = 0; i < ids.size(); i++) {
    int code = ids.get(i);
    // ... determine behavior and laneIndex from code ...
    if (behavior != null) {
        pinLookup.put(
            (isDigital ? "D" : "A") + i,  // ← key uses INDEX i
            new PinConfig(laneIndex, isDigital, i, behavior));
    }
}
```

RC AI builds its lookup table keyed by **`"D" + i`**, where `i` is the index position in `digitalIds`. The `PinConfig` also stores `i` as the pin number.

---

### 1.4 INPUT Message Reception (Lap Triggering)

**Java — `onInput()` (ArduinoProtocol.java L746–748):**

```java
private void onInput(boolean isDigital, int pin, int state) {
    String key = (isDigital ? "D" : "A") + pin;
    PinConfig pinConfig = pinLookup.get(key);
```

RC AI constructs the lookup key using **the `pin` value received from the serial message**. It expects this value to be the same index `i` that was sent in the `PI` command.

### The Round-Trip (Real Hardware):

```
RC AI sends: PI ... D 0 D 1 D 2 D 3  (indices 0, 1, 2, 3)
Arduino stores: pReadPins[0]=0, pReadPins[1]=1, pReadPins[2]=2, pReadPins[3]=3
Arduino bReset: sends INPUT D pin=0, INPUT D pin=1, ...
RC AI receives: pin=0 → key="D0" → found in pinLookup ✓
```

In real hardware: **the index sent by RC AI becomes the physical Arduino pin number**, and the physical pin number is sent back in INPUT messages. **The round-trip is self-consistent because the Arduino uses index-as-pin.**

---

### 1.5 Sensor Event Sequence (Real Hardware)

```
1. Car crosses sensor → physical pin goes LOW (INPUT_PULLUP, active low)
2. Arduino calls setupStateChange() → starts debounce timer
3. Debounce timer expires → sendStateChange(pinIndex, LOW, time)
4. sendStateChange sends TIME message (time delta since last event)
5. sendStateChange sends INPUT message: 0x49 0x44 pinNumber 0 0x3B
6. RC AI receives INPUT: key = "D" + pinNumber → looks up PinConfig
7. PinConfig.behavior == LAP_COUNTER → calls onLapCounter(laneIndex, 0, interfaceId)
8. onLapCounter: state=0 == wantState=0 → fires onLap(laneIndex, hwLapTime.time())
9. hwLapTime[laneIndex] is reset
```

---

## 2. Sensor Timing Analysis

### 2.1 Real Arduino Debounce

**Firmware constants and logic (sketch.ino L148–158, L613–638):**

- `ulDebounceHighUs` and `ulDebounceLowUs` — set by the `d...` command from RC AI
- Default: 0 (no debounce) until RC AI sends the `DEBOUNCE` command
- Standard RC AI debounce config: `debounceUs` from `ArduinoConfig`

**Debounce flow (sketch.ino L613–638):**
```c
void handleDebounce(int pinIndex, unsigned long ulCurTimeMs, unsigned long ulDeltaUs) {
    if (pDebounceTime[pinIndex] != 0xffffffff) {
        pDebounceTime[pinIndex] += ulDeltaUs;
        unsigned long time = ulDebounceHighUs;
        if (pDebounceNextState[pinIndex] == LOW) {
            time = ulDebounceLowUs;
        }
        if (pDebounceTime[pinIndex] >= time) {
            sendStateChange(pinIndex, pDebounceNextState[pinIndex], ulCurTimeMs);
            pDebounceState[pinIndex] = pDebounceNextState[pinIndex];
            pDebounceTime[pinIndex] = 0xffffffff;
        }
    }
}
```

- A pin must remain in the new state for `ulDebounceHighUs` (if going HIGH) or `ulDebounceLowUs` (if going LOW) before the state change is sent.
- If debounce = 0, the state change is sent immediately on the next loop iteration.

### 2.2 Emulator Pulse Timing

**Emulator — `pulse_sensor()` (arduino_emulator.py L308–320):**

```python
def pulse_sensor(self, pin, pulse_ms=30):
    self.sensor_on(pin)   # sends INPUT state=1 (HIGH)
    time.sleep(pulse_ms / 1000.0)
    self.sensor_off(pin)  # sends INPUT state=0 (LOW)
```

- HIGH duration: 30ms
- LOW duration: until next lap (several seconds)
- No debounce
- Pulse direction: HIGH first, then LOW

**Sensor timing comparison:**

| Parameter | Real Arduino | Emulator |
|---|---|---|
| Debounce | Configurable (set by RC AI) | None |
| Pulse direction | LOW triggers lap (active low, pullup) | LOW triggers lap ✓ |
| Pulse width | Physical, ~ms | 30ms (software) |
| Multiple edges sent | Yes (HIGH and LOW both sent) | Yes (HIGH then LOW) ✓ |

---

## 3. Serial Protocol Audit

### 3.1 Which message represents a lap

A lap is registered in RC AI when:
1. An `INPUT` message is received (`0x49`)
2. The pin field maps to a `LAP_COUNTER` entry in `pinLookup`
3. The state field equals `wantState` (0 for normally-open sensors)

Evidence: `onLapCounter()` (ArduinoProtocol.java L872–930).

### 3.2 How lap detection works

- **Edge detection (falling edge):** A lap fires when the state transitions to `wantState = 0` (LOW).
- `lastLapPinState` is tracked but only used for pit lane behavior, not for lap debounce.
- There is no requirement for a preceding HIGH state — any LOW on a LAP_COUNTER pin counts.

### 3.3 PIN number sent in INPUT messages

Both real Arduino and emulator send `INPUT` messages with a pin field. The meaning of this pin field is critical:

| Source | Pin field value in INPUT message |
|---|---|
| Real Arduino | `pReadPins[pinIndex]` — the value received in the `PI` command |
| Emulator | `sensor_pin` from `config/track.json` (physical pin number) |

This is the source of the mismatch.

---

## 4. Emulator Comparison Table

| Behavior | Real Arduino | Emulator | Match? |
|---|---|---|---|
| Version announcement | Sent on boot without prompt | Sent in response to RESET | Functionally OK |
| `PI` command received | Stores indices as physical pins, sets `bReset=true` | Not processed | **NO** |
| Initial pin state broadcast | Sends INPUT for each pin after `PI` | Never sent | **NO** |
| `d` (debounce) command | Configures debounce timers | Not processed | No (acceptable — software pulses don't bounce) |
| `T;` (TIME_RESET) received | Sends flush time + sets reset flag on next heartbeat immediately | Sets reset_flag=1, waits up to 500ms | **NO** |
| Heartbeat reset_flag timing | Sent within ~1ms of `T;` (next loop iteration) | Sent 0–500ms after `T;` (periodic timer) | **NO** |
| PIN in INPUT message | Index `i` sent in the `PI` command | Physical pin from `track.json` (2, 3, 4, 5) | **CRITICAL MISMATCH** |
| Pulse direction | LOW = car detected (INPUT_PULLUP) | LOW = car detected ✓ | OK |
| `wantState` for lap | 0 (LOW) for normally-open | Sends state=0 for sensor_off ✓ | OK in isolation |
| Lap fires on | LOW edge | LOW edge ✓ | OK in isolation |
| Relay control | Via `OD pin state` command | Fully implemented ✓ | OK |

---

## 5. Root Cause Ranking

---

### GAP-A — PIN INDEX MISMATCH

**Probability: 95%**

**Evidence:**

Java `sendPinMode()` (ArduinoProtocol.java L655):
```java
message[idx++] = (byte) i;  // sends index i
```

Java `addPinConfigs()` (ArduinoProtocol.java L1131):
```java
pinLookup.put("D" + i, new PinConfig(...));  // keyed by index i
```

Java `onInput()` (ArduinoProtocol.java L747):
```java
String key = "D" + pin;  // looks up by the pin value received in INPUT message
```

Emulator `pulse_sensor()` (arduino_emulator.py L308):
```python
self.sensor_on(pin)  # pin = sensor_pin from track.json = 2, 3, 4, 5
```

Emulator `build_input_on()` (serial_protocol.py L111–117):
```python
return bytes([OPCODE_INPUT, pin_type, pin & 0xFF, 1, TERMINATOR])
```

So the emulator sends `INPUT D pin=2` for lane 1, `INPUT D pin=3` for lane 2, etc.

RC AI looks up `"D2"`, `"D3"`, `"D4"`, `"D5"` in `pinLookup`.

The real Arduino would have been configured by RC AI to respond with index 0, 1, 2, 3 — and `pinLookup` contains keys `"D0"`, `"D1"`, `"D2"`, `"D3"`.

The lookup for the emulator's `"D2"` → finds **lane index 2** (not lane 1). The lookup for `"D3"` → **lane index 3** (not lane 2). The lookup for `"D4"` → **not found** (only 4 lanes, indices 0–3). The lookup for `"D5"` → **not found**.

**Result:**
- Lane 1 sensor (pin 2) → resolves as lane index 2 instead of lane 0
- Lane 2 sensor (pin 3) → resolves as lane index 3 instead of lane 1
- Lane 3 sensor (pin 4) → **not found, no lap registered**
- Lane 4 sensor (pin 5) → **not found, no lap registered**

Lanes 1 and 2 laps are registered, but attributed to the wrong lanes. Lanes 3 and 4 laps are silently dropped.

Additionally, RC AI sends `PI ... D 0 D 1 D 2 D 3` expecting Arduino pins 0–3 to be sensors. The emulator never receives or processes this, so it pulses pins 2–5 (from `track.json`), which are the wrong indices from RC AI's perspective.

**Impact:** Most laps silently discarded. Some laps misattributed.

**Proposed Fix:** The emulator must respond to the `PI` command and record which index maps to which sensor intent. When pulsing a sensor, the emulator must send the **index** received in the `PI` command, not the physical pin number from `track.json`. Alternatively, `track.json` should use indices 0, 1, 2, 3 for sensor pins instead of physical pin numbers.

---

### GAP-001 — TIME_RESET: Missing Immediate Flush + Reset Flag

**Probability: 70%**

**Evidence:**

Java `startTimer()` (ArduinoProtocol.java L352–358):
```java
public void startTimer() {
    sendTimeReset();
    for (int i = 0; i < numLanes; i++) {
        hwLapTime[i].reset();
        hwSegmentTime[i].reset();
    }
    hwReset = 1;
}
```

Java `onHeartbeat()` (ArduinoProtocol.java L560–578):
```java
if (isReset == hwReset) {
    hwReset = 0;
    for (int i = 0; i < numLanes; i++) {
        hwLapTime[i].add(timeInUse);
        hwSegmentTime[i].add(timeInUse);
    }
} else {
    pinStateCache.clear();
    hwReset = isReset;
    initializeHardwareState();
}
```

When `T;` is sent, RC AI sets `hwReset = 1`. The emulator's next heartbeat carries `reset_flag = 1` **only if** the heartbeat loop fires before `reset_flag` is cleared. The heartbeat loop sleeps 500ms. If `T;` arrives mid-sleep, `reset_flag` becomes 1 and the next heartbeat correctly carries it. But if RC AI times out or sends another `T;` before the heartbeat fires, the accumulator never starts.

More critically, the `hwLapTime.time()` method returns the accumulated delta. If accumulation is delayed, the lap time is artificially small or zero.

**Impact:**
- Timing accumulation may start late or not start at all
- Lap times are wrong (accumulated too few deltas before the sensor fires)
- This does NOT prevent laps from being counted — it only affects timing accuracy and the initial sync window

**Proposed Fix:** On `T;` reception, immediately send a heartbeat message with `reset_flag=1` and update `last_heartbeat`. This mirrors firmware behavior where `sendTime(0xffffffff)` is called immediately.

---

### GAP-002 — Missing Initial Pin State Broadcast

**Probability: 30%**

**Evidence:**

Arduino firmware `processPinModeRequest()` (sketch.ino L1023–1024):
```c
// Force send the initial pin states
bReset = true;
```

`loop()` (sketch.ino L506–507):
```c
if (bReset) {
    sendStateChange(i, iPinSignal, ulCurTimeMs);
}
```

The real Arduino sends an initial `INPUT state=HIGH` for every configured pin immediately after `PI`. The emulator never sends this.

Java `lastLapPinState[]` is initialized to `-1` (ArduinoProtocol.java L131). For the first lap, RC AI compares incoming `state=0` against `wantState=0` — the initial state of `lastLapPinState` is not used for lap counting itself. Therefore this gap does NOT prevent laps from being counted.

However, this initial broadcast is tied to the TIME message (`sendStateChange` calls `sendTime` first). This means the initial broadcast from the real Arduino establishes the first `deltaUs` reference point, which contributes to the first lap's timing accuracy.

**Impact:** First lap timing is slightly inaccurate. Does not prevent lap detection.

**Proposed Fix:** After version handshake, send `INPUT D pin=0 state=1` for each configured sensor pin.

---

### GAP-003 — Heartbeat Interval Accuracy

**Probability: 10%**

**Evidence:**

The emulator uses `time.sleep(0.5)` between heartbeats. On macOS, `time.sleep()` is not guaranteed to be exact. Under load, intervals can be 10–50ms late.

The real Arduino uses hardware `micros()` for precise timing, and its keepAlive fires every 1,000,000 µs.

**Impact:** Lap time accumulation may drift from real wall clock time by a few percent over a 60-second heat. Does not prevent laps from being counted.

**Proposed Fix:** Not required for lap counting. If lap time accuracy matters, use a monotonic timer with deadline-based sleeping.

---

## 6. Symptom Explanation

---

### Symptom A: RC AI records 0 laps during a complete heat

**Observed:** Emulator generates ~14–15 laps internally. RC AI records 0.

**Code evidence:**

1. Track.json configures `sensor_pin: 2, 3, 4, 5` (four lanes).
2. Emulator sends `INPUT D pin=2`, `INPUT D pin=3`, `INPUT D pin=4`, `INPUT D pin=5`.
3. RC AI `pinLookup` is built with keys `"D0"`, `"D1"`, `"D2"`, `"D3"` (assuming 4 lanes configured in RC AI with indices 0–3).
4. RC AI `onInput()` (L747): `key = "D" + pin`.
5. For pin=4 → key `"D4"` → `pinLookup.get("D4")` → `null`.
6. For pin=5 → key `"D5"` → `null`.
7. For pin=2 → key `"D2"` → `PinConfig(laneIndex=2, ...)` (lane 3 in RC AI, 0-indexed).
8. For pin=3 → key `"D3"` → `PinConfig(laneIndex=3, ...)` (lane 4 in RC AI, 0-indexed).

If the race has only lanes 1 and 2 active (assigned vehicles), and their sensor pins are 2 and 3, they resolve to RC AI lanes 2 and 3 (0-indexed). If RC AI is monitoring lanes 0 and 1 for those vehicles, the `onLap` call fires for the wrong lanes — which may have no vehicle registered, causing those laps to be counted in the wrong lane or silently dropped.

**Result:** 0 laps counted for the expected lanes. Possibly some laps counted in wrong lanes.

---

### Symptom B: After Pause/Restart, laps begin to appear

**Observed:** After Pause/Restart, RC AI starts counting some laps.

**Code evidence:**

The pause/restart cycle sends `T;` again (Java `startTimer()` L352–358). This triggers a fresh `hwReset = 1` cycle. If the emulator's heartbeat happens to fire within milliseconds of the `T;`, the reset confirmation succeeds and timing begins cleanly.

More importantly: during Pause, RC AI may resend `PI` commands via `updateConfig()` or `initializeHardwareState()` (ArduinoProtocol.java L1064–1067). If `syncPower()` is called, relay states are resent. The net effect is the system attempts a partial re-initialization.

Even if the PIN INDEX MISMATCH remains, after Pause/Restart RC AI's `hwLapTime` accumulators are now running (second `T;` sync succeeded). So laps can now be counted — but still for the wrong lanes.

**Result:** A small number of laps appear because the timing sync works on the second attempt, but most are still miscounted or misrouted.

---

### Symptom C: Lap times are 23–38 seconds instead of 4–5 seconds

**Observed:** When laps do appear, they have inflated times.

**Code evidence:**

Java `onLapCounter()` (ArduinoProtocol.java L886–891):
```java
double time = hwLapTime[laneIndex].time();
time -= (config.debounceUs / (1000.0 * 1000.0));
listener.onLap(laneIndex, time, interfaceId, getInterfaceIndex());
```

`hwLapTime[laneIndex].time()` returns the total accumulated delta since the last reset.

If the TIME_RESET resync failed (GAP-001), the accumulator may have been running since **before** the race start — accumulating time from the initial connection, through the UI interaction, through the start button press. The first lap fires with all that accumulated time, yielding a lap time of 20–40 seconds.

Additionally, due to GAP-A (pin mismatch), RC AI counts laps on wrong lanes. If lane 2 (RC AI index 1) has an emulator pulsing it every 4–5 seconds, RC AI may accumulate multiple pulse intervals before a "lap" is registered on the mismatched lane, making the elapsed time = (n × 4s), where n is the number of pulses received before the accumulators reset.

**Result:** First lap has inflated time due to pre-race accumulation. Subsequent laps may also be inflated due to lane misattribution spanning multiple real lap intervals.

---

### Symptom D: Emulator logs many laps while RC AI records only a few

**Observed:** Emulator prints 14–15 LAP lines. RC AI shows 0–2.

**Code evidence:**

The emulator's lap count is tracked internally in `race_runtime.py`. Each time `driver.generate_lap()` returns and `pulse_sensor()` is called, a `LAP` line is printed. This is pure simulation bookkeeping — it has no dependency on RC AI confirmation.

RC AI only counts laps when `listener.onLap()` is called from `onLapCounter()`. This requires:
1. An INPUT message with the correct pin index (failing — GAP-A)
2. A running `hwLapTime` accumulator (failing or delayed — GAP-001)

**Result:** Emulator internal counter runs correctly. RC AI counter stays at 0 or increments rarely because the pin lookup fails for most sensor pins.

---

## 7. Summary

| Gap | Description | Impact | Priority |
|---|---|---|---|
| **GAP-A** | Emulator sends physical pin numbers; RC AI expects indices | All laps silently dropped or misrouted | **CRITICAL — Fix first** |
| **GAP-001** | TIME_RESET response delayed up to 500ms | Wrong lap times, delayed start of accumulation | **HIGH — Fix second** |
| **GAP-002** | No initial pin state broadcast | Slight first-lap timing inaccuracy | Low |
| **GAP-003** | Heartbeat interval imprecision | Sub-percent timing drift over 60s | Negligible |

**The fix for GAP-A alone is expected to restore lap counting to near-correct behavior. GAP-001 must also be fixed to get correct lap times.**
