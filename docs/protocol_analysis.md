# Protocol Analysis — RC AI / Arduino / Python Emulator

## 1. Overview

The system is a serial communication protocol operating at **115200 baud** between:

- **RC AI (Java)** — the race management application running on a PC
- **Arduino Firmware** — the physical hardware (V2.1.0.0 sketch)
- **Python Emulator** — this project, replacing the physical Arduino

All messages are terminated by `0x3B` (`;`).

---

## 2. Direction Conventions

| Direction | Meaning |
|---|---|
| **Arduino → PC** | Messages sent from Arduino to RC AI |
| **PC → Arduino** | Commands sent from RC AI to Arduino |

---

## 3. Messages: Arduino → PC (Emulator → RC AI)

### 3.1 VERSION — `0x56 V`

**Format:**
```
0x56  major  minor  patch  build  0x3B
```
Total: 6 bytes.

**When sent:** Immediately on Arduino `setup()` boot. Also re-sent on demand if RC AI sends a `VERSION_COMMAND` (`V;`).

**Purpose:** Announces firmware version. RC AI uses this to verify it is speaking with compatible firmware.

**RC AI response:** If `major == 2` and `minor == 1` and `patch == 0`, sets `versionVerified = true` and proceeds to full initialization sequence. If version does not match, RC AI logs an error and does **not** proceed.

**Emulator:** Sends `0x56 02 01 00 01 0x3B` upon receiving a `RESET;` command. This triggers `versionVerified = True` inside the emulator.

> **NOTE:** The Arduino sends version on boot *before* any command. The emulator sends version only *in response* to RESET.

---

### 3.2 HEARTBEAT — `0x54 T`

**Format:**
```
0x54  deltaUs[3]  deltaUs[2]  deltaUs[1]  deltaUs[0]  reset_flag  0x3B
```
Total: 7 bytes.

- `deltaUs` — 4 bytes MSB-first, microseconds since last heartbeat
- `reset_flag` — 1 byte: `1` if this heartbeat follows a reset, `0` otherwise

**When sent:** Every ~1 second (Arduino `keepAlive()` / emulator `heartbeat_loop()` at 0.5s interval).

**Purpose:** Two functions:
1. Keeps the serial connection alive (RC AI disconnects if no heartbeat for >2s)
2. Accumulates hardware lap timing — RC AI integrates `deltaUs` values into `hwLapTime` for each active lane

**RC AI behavior:**
- If `reset_flag == hwReset` (expected), integrates `deltaUs` into all `hwLapTime[]` and `hwSegmentTime[]` accumulators, then clears `hwReset = 0`.
- If `reset_flag != hwReset` (mismatch), clears pin state cache and reinitializes hardware.

**Critical timing role:** The heartbeat is the **only clock source** RC AI uses to measure lap times. If a heartbeat is missing or malformed, the timing accumulator is not updated.

---

### 3.3 INPUT — `0x49 I`

**Format:**
```
0x49  pin_type  pin  state  0x3B
```
Total: 5 bytes.

- `pin_type` — `0x44` (D = Digital) or `0x41` (A = Analog)
- `pin` — pin number (0-indexed)
- `state` — `0` or `1`

**When sent:** When a monitored pin changes state (car crosses sensor) or immediately after pin configuration (initial state broadcast due to `bReset = true`).

**Purpose:** Reports physical pin state changes. When `state == 0` (LOW, normally-open sensor triggered), RC AI fires a lap event.

**RC AI lap detection logic (`onLapCounter`):**
- Looks up pin from its internal `pinLookup` map
- `wantState = 0` (normally-open sensors, which is the default)
- If `state == wantState` → calls `listener.onLap()` with accumulated `hwLapTime` for that lane
- After lap event, `hwLapTime[laneIndex]` is **reset** by the `startTimer()` call

---

## 4. Commands: PC → Arduino (RC AI → Emulator)

### 4.1 RESET — `0x52 0x45 0x53 0x45 0x54 0x3B` (RESET;)

**When sent:** Immediately on `open()` (connection start).

**Arduino behavior:** Calls `softwareReboot()` — performs a full MCU reset. After reboot, Arduino immediately sends `VERSION` message.

**Emulator behavior:** Sets `versionVerified = True`, sends `VERSION` message back to RC AI. Does **not** reboot.

---

### 4.2 VERSION — `0x56 0x3B` (V;)

**When sent:** RC AI sends this on demand to request firmware version.

**Arduino behavior:** Re-sends `rcVersion` bytes.

---

### 4.3 PIN_MODE_READ — `0x50 0x49 count [type pin]... 0x3B` (PI...)

**When sent:** After `versionVerified`, RC AI sends this to configure which pins Arduino should monitor as inputs.

**Arduino behavior:**
1. Frees previous pin configuration
2. Allocates and populates `pReadPins[]` with the listed pins
3. Sets `bReset = true` → Arduino **immediately broadcasts current state** of all configured pins

**Emulator behavior:** Not handled. The emulator does not process `PI` commands.

---

### 4.4 PIN_MODE_WRITE — `0x50 0x4F count [type pin]... 0x3B` (PO...)

**When sent:** After `versionVerified`, to configure output pins (relays, LEDs).

**Arduino behavior:** Sets `pinMode(pin, OUTPUT)` for each listed pin.

**Emulator behavior:** Not handled.

---

### 4.5 ANALOG_PIN_MODE — `0x70 count [type pin]... 0x3B` (p...)

**When sent:** After `versionVerified`, to configure analog read pins.

**Arduino behavior:** Sets up periodic analog reads. Sends `ANALOG_DATA` messages.

**Emulator behavior:** Not handled.

---

### 4.6 DEBOUNCE — `0x64 Hms Hus Lms Lus 0x3B` (d...)

**When sent:** After `versionVerified`, sets debounce timing for sensor pins.

**Arduino behavior:** Configures `ulDebounceHighUs` and `ulDebounceLowUs`. Prevents false laps from contact bounce.

**Emulator behavior:** Not handled.

---

### 4.7 TIME_RESET — `0x54 0x3B` (T;)

**When sent:** On race start (`startTimer()`), pause, and configuration changes.

**Arduino behavior:**
1. Immediately sends the current accumulated time (as a "flush")
2. Sets `timeResponse[5] = (1 << lane)` — the **reset flag bit**
3. On the next `sendTime()` call, this reset flag is transmitted in the heartbeat-like time response

**Java behavior (caller side, `startTimer()`):**
- Sends `T;`
- Resets `hwLapTime[i].reset()` and `hwSegmentTime[i].reset()` for all lanes
- Sets `hwReset = 1`

**Emulator behavior:** Recognized as `MESSAGE_TIME_RESET`. Does **not** send a flush time message. Does **not** set a reset flag on the next heartbeat.

---

### 4.8 WRITE_DIGITAL_PIN — `0x4F 0x44 pin state 0x3B` (OD...)

**When sent:** To control relay state (lane power on/off), LED state.

**Arduino behavior:** `digitalWrite(pin, state)`.

**Emulator behavior:** Fully implemented. Updates `output_states[pin]`, which `is_lane_powered()` reads.

---

### 4.9 EXTENDED PROTOCOL — `0x45 opcode ... 0x3B` (E...)

**When sent:** Various race lifecycle events (race state, heat leader, standings, fuel, etc.).

**Arduino behavior:** Passes to `processExtendedRequest()`. Mainly used for fuel stutter and LED animations.

**Emulator behavior:** Not handled.

**Race state sub-opcodes (byte 2):**

| Value | Meaning |
|---|---|
| `0` | Heat not started |
| `1` | Heat not restarted |
| `2` | Heat starting (countdown) |
| `3` | Heat re-started |
| `4` | Heat running |
| `5` | Heat paused |
| `6` | Heat ended |
| `7` | Race ended |
| `8` | RC AI closing |

---

## 5. Hardware Lap Timing Mechanism

The RC AI uses **hardware-accumulator timing**, not wall clock timing.

### How it works:

1. Each heartbeat increments `hwLapTime[i]` by `deltaUs` for every lane
2. On `TIME_RESET` (`T;`), RC AI resets all `hwLapTime[]` accumulators to 0 and sets `hwReset = 1`
3. On the next heartbeat after a TIME_RESET, the firmware sends `reset_flag = 1`
4. RC AI sees `reset_flag == hwReset` (both are 1), accepts the heartbeat, clears `hwReset = 0`
5. Lap time accumulation resumes
6. When a sensor fires (`INPUT state=0`), RC AI reads `hwLapTime[lane].time()` as the lap time and resets it

### Consequence:
If the emulator does not correctly implement the TIME_RESET response (flush + next heartbeat with reset_flag=1), the RC AI will **reject heartbeats** because `reset_flag != hwReset`.

---

## 6. Initialization Sequence (Full)

After `open()` is called:

```
PC                          Arduino/Emulator
│                                │
│──── RESET; ────────────────────►│
│                                │ (reboot / set versionVerified)
│◄─── VERSION (56 02 01 00 00 3B)─│
│                                │
│ onVersion() → versionVerified=true
│                                │
│──── PIN_MODE_READ (PI...) ─────►│  ← configures input pins
│──── PIN_MODE_WRITE (PO...) ────►│  ← configures output pins
│──── ANALOG_PIN_MODE (p...) ────►│  ← configures analog pins
│──── DEBOUNCE (d...) ───────────►│  ← sets debounce timing
│──── TIME_RESET (T;) ───────────►│  ← resets lap timing accumulators
│                                │
│ Arduino sets bReset=true → sends initial pin states
│◄─── INPUT (pin=X, state=HIGH) ──│  (initial state broadcast)
│◄─── INPUT (pin=Y, state=HIGH) ──│
│                                │
│◄─── HEARTBEAT (reset_flag=1) ───│  ← confirms TIME_RESET
│◄─── HEARTBEAT (reset_flag=0) ───│  ← normal operation
```

---

## 7. Lap Detection Sequence (Normal Race)

```
PC                          Arduino/Emulator
│                                │
│◄─── HEARTBEAT (delta) ──────────│  ─┐
│  hwLapTime[lane] += delta        │   │ Time accumulating
│◄─── HEARTBEAT (delta) ──────────│  ─┘
│                                │
│  [car crosses sensor]           │
│◄─── INPUT (D, pin=X, state=0) ──│  ← LOW = car detected
│  onLapCounter(lane, state=0)    │
│  lap_time = hwLapTime[lane].time()
│  listener.onLap(lane, lap_time)  │
│  hwLapTime[lane].reset()         │
│                                │
│◄─── INPUT (D, pin=X, state=1) ──│  ← HIGH = car passed
```

---

## 8. Pause / Restart Sequence

```
PC                          Arduino/Emulator
│                                │
│──── E 0 5 ... (PAUSED) ────────►│
│──── TIME_RESET (T;) ───────────►│  ← pause resets accumulators
│  hwReset = 1                    │
│                                │
│ [race resumes]                  │
│──── E 0 3 ... (RESTARTED) ─────►│
│──── TIME_RESET (T;) ───────────►│  ← restart resets accumulators
│  hwReset = 1                    │
│                                │
│◄─── HEARTBEAT (reset_flag=1) ───│  ← resync accepted
│  hwReset = 0                    │
│  hwLapTime accumulation resumes │
```
