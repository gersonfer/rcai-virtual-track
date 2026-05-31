# Protocol Gap Analysis — Real Arduino vs Python Emulator

## Purpose

This document compares the real Arduino firmware behavior against the current Python emulator implementation, identifies all deviations, and proposes corrective actions for each gap.

---

## GAP-001 — TIME_RESET: Missing Flush + Reset Flag

### Severity: CRITICAL — ROOT CAUSE OF LAP-COUNTING BUG

---

### Real Arduino

When `T;` is received:

1. Calls `sendTime(0xffffffff)` — which sends a **flush time message** with the current accumulated delta
2. Sets `timeResponse[5] = (1 << lane)` — the **reset flag bit**
3. On the next `sendTime()` call (heartbeat or sensor event), the reset flag is included
4. After sending, the flag is cleared: `timeResponse[5] = 0`

The heartbeat structure is actually the same time message. The Arduino's `keepAlive()` calls `sendPing()`, which calls `sendTime(0xffffffff)`. Every heartbeat is the same time-response packet.

**Firmware heartbeat format:**
```
0x54  deltaUs[3..0]  reset_flag  0x3B
```
Where `reset_flag` is `1` on the heartbeat immediately following a `T;`, and `0` thereafter.

---

### Python Emulator

When `T;` is received, `handle_command()` is called:

```python
if parsed.message_type == MESSAGE_TIME_RESET:
    print("[COMMAND] TIME RESET")
    self.reset_flag = 1
    return
```

The emulator sets `self.reset_flag = 1`. This is correct in intent.

However, the heartbeat loop runs independently at 0.5s intervals:

```python
def heartbeat_loop(self):
    while self.running:
        ...
        msg = build_heartbeat(
            delta_us=delta_us,
            reset_flag=self.reset_flag,
        )
        self.send(msg)
        self.reset_flag = 0
        time.sleep(HEARTBEAT_INTERVAL)
```

**Problem:** The heartbeat loop runs on its own timer. When `T;` arrives, `reset_flag` is set to `1`, but the **next heartbeat may not fire for up to 0.5 seconds**. More critically: the emulator does **not** send a flush time message immediately upon receiving `T;`.

**RC AI's reaction on the real hardware:**

```
T; received by Arduino
Arduino: sendTime(0xffffffff) → immediate flush time message sent
RC AI: receives the flush, notes the time
Next heartbeat: reset_flag = 1
RC AI: hwReset == isReset → accepted, hwReset = 0, timing resumes
```

**RC AI's reaction with the emulator:**

```
T; received by emulator
Emulator: sets reset_flag = 1 internally, sends nothing immediately
RC AI: receives nothing, waits
RC AI sends T; at race start → hwReset = 1
Next emulator heartbeat (up to 0.5s later): reset_flag = 1 ← (correct if timing is right)
OR: if T; arrives between heartbeats and hwReset was already 0:
  reset_flag = 0 arrives → mismatch → RC AI clears pin cache, reinitializes
```

**Why the mismatch happens in practice:**

The emulator sends `reset_flag = 1` only on the **very first heartbeat after `start()`** (because `self.reset_flag = 1` is set once at construction). After that, `reset_flag` is always `0`.

If RC AI sends `T;` **after** the first heartbeat has already been sent, the emulator's `reset_flag` is already `0`. Setting it to `1` in `handle_command()` only works if the heartbeat fires before the next `T;` arrives, which is a race condition.

In the common case (RC AI sends `T;` during race start, well after initial connection), the emulator heartbeat has already fired with `reset_flag = 1` and cleared it. Subsequent `T;` commands set it back, but the next heartbeat may or may not fire before RC AI gives up.

---

### Impact

RC AI receives a heartbeat with `reset_flag = 0` when it expected `reset_flag = 1`.

```java
// ArduinoProtocol.java L563-577
if (isReset == hwReset) {
    hwReset = 0;
    for (int i = 0; i < numLanes; i++) {
        hwLapTime[i].add(timeInUse);
        hwSegmentTime[i].add(timeInUse);
    }
} else {
    logger.warn("Reset mismatch: got {}, expected {}. Clearing pin cache.", isReset, hwReset);
    pinStateCache.clear();
    hwReset = isReset;
    initializeHardwareState();
}
```

- `hwReset = 1`, `isReset = 0` → mismatch
- `pinStateCache.clear()` is called
- `hwReset = isReset` → `hwReset = 0`
- `initializeHardwareState()` → `syncPower()` → resends relay states
- On the **next** heartbeat, `isReset = 0` and `hwReset = 0` → match → timing begins

**Net result:** Lap accumulation starts only after the second heartbeat following race start. If only 2 seconds elapse before a lap is counted, it fires correctly. If 13-14 laps worth of time pass during the mismatch window (e.g., a 60-second heat), those laps are **entirely lost** because the accumulators were not running.

---

### Proposed Fix

In `handle_command()` (or `serial_listener_loop()`), when `MESSAGE_TIME_RESET` is detected:

1. Immediately send a flush heartbeat with the current delta_us and `reset_flag = 0` (just to flush)
2. Set `reset_flag = 1` for the **next** scheduled heartbeat

Alternatively, send the flush heartbeat immediately with `reset_flag = 1` and then set `reset_flag = 0` so the next periodic heartbeat is clean.

The key insight: **the flush must happen immediately**, not at the next heartbeat interval.

---

## GAP-002 — Initial Pin State Broadcast Missing

### Severity: HIGH

---

### Real Arduino

After receiving `PIN_MODE_READ` (`PI...`), the Arduino sets `bReset = true`. On the next `loop()` iteration, every configured input pin's current state is sent via `sendStateChange()`. This gives RC AI an initial snapshot of all pin states.

```c
// processPinModeRequest()
bReset = true;

// loop()
if (bReset) {
    sendStateChange(i, iPinSignal, ulCurTimeMs);
}
```

---

### Python Emulator

The emulator does not process `PI` (PIN_MODE_READ) commands at all. It does not track which pins are configured as inputs. It does not broadcast initial pin states.

---

### Impact

RC AI never receives the initial `INPUT state=HIGH` broadcast for sensor pins. RC AI's `lastLapPinState[]` array is initialized to `-1`. The first lap pulse (HIGH→LOW) may not be processed correctly because the previous state is unknown.

This may contribute to the first lap being missed or counted incorrectly.

---

### Proposed Fix

Process the `PI` command in the emulator. After receiving it, broadcast `INPUT state=HIGH` for every configured sensor pin (since sensor pins default to HIGH when idle).

Alternatively, since the emulator is not physically polling real pins, send an initial HIGH state for each known sensor pin immediately after version handshake completes.

---

## GAP-003 — Heartbeat Timing: True Delta vs Wall Clock Delta

### Severity: MEDIUM

---

### Real Arduino

The Arduino uses `micros()` to measure the exact elapsed time between heartbeats. The `deltaUs` in the heartbeat is microsecond-accurate hardware timing.

---

### Python Emulator

The emulator uses `time.monotonic()` to compute delta:

```python
now = time.monotonic()
delta_us = int((now - self.last_heartbeat) * 1_000_000)
self.last_heartbeat = now
```

This is mathematically correct. However, `time.sleep(HEARTBEAT_INTERVAL)` does not guarantee exactly 0.5s intervals on macOS. The actual interval may drift depending on system load.

---

### Impact

Lap time accuracy may drift slightly from real wall clock time. On a 60-second heat, the accumulated `deltaUs` may not sum to exactly 60 seconds. This is a measurement precision issue, not a lap-counting issue.

---

### Proposed Fix

No fix required for lap counting. If lap time precision becomes important in future tasks, replace `time.sleep()` with a more accurate interval mechanism (e.g., calculate the next target time and sleep the exact remaining delta).

---

## GAP-004 — PIN_MODE_WRITE / DEBOUNCE / ANALOG_PIN_MODE Not Handled

### Severity: LOW (for current simulation scope)

---

### Real Arduino

After version verification, RC AI sends:
- `PO...` — Output pin mode configuration
- `d...` — Debounce timing
- `p...` — Analog pin mode configuration

These configure the hardware for relay control and voltage sensing.

---

### Python Emulator

These commands are received but not parsed. The emulator has no understanding of which pins are outputs vs inputs, and applies no debounce logic.

---

### Impact

**Relay control (`OD...`)** is correctly handled independently. The emulator parses `0x4F 0x44` and updates `output_states[]`. This works.

**Debounce** is irrelevant for the emulator since it generates clean digital pulses via software. No false bouncing occurs.

**Analog reads** are not used in the current simulation.

For the current use case, these gaps do not cause functional problems.

---

### Proposed Fix

Not required for current scope. If voltage-level sensing or complex relay configurations are needed in the future, these commands should be parsed.

---

## GAP-005 — Extended Protocol Not Handled

### Severity: LOW (for current simulation scope)

---

### Real Arduino

Handles `E` messages for race state, heat standings, fuel levels, lap performance, etc.

The most important sub-opcode is `extRaceState` (state = 4 = RUNNING), which is used by the fuel stutter feature to determine when to energize relays.

---

### Python Emulator

Extended protocol messages are received but not processed. The emulator determines lane power directly from `output_states[]` (relay pin state), not from the extended race state.

---

### Impact

None for current scope. The relay mechanism (`OD...`) works correctly and is the correct way to control lane power.

---

## Summary Table

| Gap ID | Area | Severity | Lap-Counting Impact | Fix Required Now |
|---|---|---|---|---|
| GAP-001 | TIME_RESET flush + reset_flag | **CRITICAL** | **YES — Root cause** | **YES** |
| GAP-002 | Initial pin state broadcast | HIGH | Partial (first lap only) | Recommended |
| GAP-003 | Heartbeat timing precision | MEDIUM | No | No |
| GAP-004 | PIN_MODE_WRITE / DEBOUNCE | LOW | No | No |
| GAP-005 | Extended Protocol | LOW | No | No |

---

## Primary Recommended Fix: GAP-001

The fix for GAP-001 is small and surgical:

**Current `handle_command()` on TIME_RESET:**
```python
if parsed.message_type == MESSAGE_TIME_RESET:
    print("[COMMAND] TIME RESET")
    self.reset_flag = 1
    return
```

**Required behavior:**
1. Compute current delta_us
2. Immediately send a heartbeat/time flush with `reset_flag = 1`
3. Update `self.last_heartbeat` so the periodic heartbeat loop does not double-count the interval
4. Set `self.reset_flag = 0` (the flush already carried the flag)

This ensures RC AI receives the reset confirmation within milliseconds of sending `T;`, rather than waiting up to 0.5 seconds for the next periodic heartbeat — which may arrive with the wrong flag value.
