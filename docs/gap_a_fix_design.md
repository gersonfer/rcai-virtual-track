# GAP-A Fix Design — PIN INDEX MISMATCH

---

## 1. Restatement of GAP-A

### What RC AI expects

RC AI (Java) builds a pin lookup table keyed by **list index**, not by physical pin number.

In `addPinConfigs()` ([ArduinoProtocol.java L1075–1133](file:///Users/gersonferreira/projetos/rcai-virtual-track/docs/ArduinoProtocol.java#L1075-L1133)):

```java
for (int i = 0; i < ids.size(); i++) {
    int code = ids.get(i);
    // ... determine behavior and laneIndex ...
    pinLookup.put(
        (isDigital ? "D" : "A") + i,   // key = "D0", "D1", "D2", "D3"
        new PinConfig(laneIndex, isDigital, i, behavior));
}
```

When RC AI sends the `PI` (PIN_MODE_READ) command, it sends the **index `i`** as the pin byte:

In `sendPinMode()` ([ArduinoProtocol.java L650–657](file:///Users/gersonferreira/projetos/rcai-virtual-track/docs/ArduinoProtocol.java#L650-L657)):

```java
for (int i = 0; i < config.digitalIds.size(); i++) {
    int id = config.digitalIds.get(i);
    if (ArduinoConfig.getPinMode(id) == mode) {
        message[idx++] = DIGITAL;
        message[idx++] = (byte) i;  // ← sends index, not physical pin
    }
}
```

When receiving an INPUT message, RC AI looks up by `pin` received in the message:

In `onInput()` ([ArduinoProtocol.java L746–748](file:///Users/gersonferreira/projetos/rcai-virtual-track/docs/ArduinoProtocol.java#L746-L748)):

```java
String key = (isDigital ? "D" : "A") + pin;
PinConfig pinConfig = pinLookup.get(key);
```

**RC AI expects:** INPUT messages carry `pin = i` (the same index it sent in the PI command). The lookup key `"D" + pin` must match `"D" + i`.

---

### What the real Arduino does

In `processPinModeRequest()` ([sketch.ino L1012–1019](file:///Users/gersonferreira/projetos/rcai-virtual-track/docs/racecoordinatorai_sketch.ino#L1012-L1019)):

```c
int pin = inBuffer[iBufIndex + 1] TXT_TO_INT_CONVERSION;
pReadPins[i] = pin;   // stores the received index value as the pin number
```

In `sendStateChange()` ([sketch.ino L653–681](file:///Users/gersonferreira/projetos/rcai-virtual-track/docs/racecoordinatorai_sketch.ino#L653-L681)):

```c
byte pin = pReadPins[pinIndex];   // reads back the stored value
inputChanged[2] = pin;            // sends it in the INPUT message
```

**Real Arduino behavior:** The Arduino receives index `i` from the PI command, stores it as `pReadPins[i]`, and echoes it back in INPUT messages. The round-trip is: RC AI sends index → Arduino stores index → Arduino sends index back → RC AI looks up by index. **Self-consistent.**

---

### What the emulator currently does

The emulator:

1. **Never receives or processes the `PI` command.** The `parse_command()` function in [serial_protocol.py L140–181](file:///Users/gersonferreira/projetos/rcai-virtual-track/track_interface/serial_protocol.py#L140-L181) does not recognize it; it falls through to `MESSAGE_UNKNOWN`.

2. **Uses physical pin numbers from `track.json`** when generating sensor events:

   In [race_runtime.py L90](file:///Users/gersonferreira/projetos/rcai-virtual-track/orchestrator/race_runtime.py#L90):
   ```python
   sensor_pin = lane["sensor_pin"]   # values: 2, 3, 4, 5 from track.json
   ```

   In [race_runtime.py L226–228](file:///Users/gersonferreira/projetos/rcai-virtual-track/orchestrator/race_runtime.py#L226-L228):
   ```python
   self.emulator.pulse_sensor(
       pin=sensor_pin,   # sends physical pin number
   )
   ```

3. **`build_input_on`/`build_input_off`** in [serial_protocol.py L104–134](file:///Users/gersonferreira/projetos/rcai-virtual-track/track_interface/serial_protocol.py#L104-L134) embed the pin number directly in the INPUT message:
   ```python
   return bytes([OPCODE_INPUT, pin_type, pin & 0xFF, 1, TERMINATOR])
   ```

**Emulator sends:** `INPUT D pin=2` for lane 1, `INPUT D pin=3` for lane 2, `INPUT D pin=4` for lane 3, `INPUT D pin=5` for lane 4.

---

### Why lap events are lost or misrouted

RC AI's `pinLookup` contains keys `"D0"`, `"D1"`, `"D2"`, `"D3"` (for a 4-lane configuration, indices 0–3).

| Emulator sends | RC AI builds key | pinLookup has | Result |
|---|---|---|---|
| `INPUT D pin=2` | `"D2"` | `"D2"` → lane index 2 | **Misrouted** — lane 1 sensor attributed to lane 3 |
| `INPUT D pin=3` | `"D3"` | `"D3"` → lane index 3 | **Misrouted** — lane 2 sensor attributed to lane 4 |
| `INPUT D pin=4` | `"D4"` | Not found | **Lost** — no pinConfig, no lap |
| `INPUT D pin=5` | `"D5"` | Not found | **Lost** — no pinConfig, no lap |

---

## 2. Correct Behavior

The emulator must reproduce the following Arduino behavior:

### 2.1 PI Command Processing

When RC AI sends `PI count [D index]... ;`:

1. Extract the count byte
2. For each pair `[type, index]`:
   - Store the index as the "pin number" that this lane uses
   - Record the mapping: `list_position → index_received`
3. After processing, send the initial state of each configured pin (all HIGH, since sensors are idle at startup)

### 2.2 Pin Index Assignment

The mapping must work as follows:

```
RC AI sends: PI 4 D 0 D 1 D 2 D 3 ;

Emulator stores:
  read_pin[0] = 0   (lane 1 sensor uses index 0)
  read_pin[1] = 1   (lane 2 sensor uses index 1)
  read_pin[2] = 2   (lane 3 sensor uses index 2)
  read_pin[3] = 3   (lane 4 sensor uses index 3)
```

### 2.3 Internal Pin Mapping

The emulator must maintain a bidirectional mapping between:

- **Internal lane sensor pin** (physical, from `track.json`: 2, 3, 4, 5)
- **Protocol pin index** (logical, from PI command: 0, 1, 2, 3)

When generating a sensor event for `sensor_pin=2`, the emulator must translate `2` → the corresponding protocol index before building the INPUT message.

### 2.4 INPUT Message Generation

When pulsing a sensor:

```
pulse_sensor(pin=2)
→ translate pin 2 to protocol index (e.g., 0)
→ build_input_on(pin=0)   ← sends protocol index, not physical pin
→ build_input_off(pin=0)
```

### 2.5 Lane-to-Pin Relationship

```
track.json:
  lane 1 → sensor_pin=2, relay_pin=6
  lane 2 → sensor_pin=3, relay_pin=7
  lane 3 → sensor_pin=4, relay_pin=8
  lane 4 → sensor_pin=5, relay_pin=9

After PI command with indices [0, 1, 2, 3]:
  emulator must map:
    sensor_pin 2 → protocol index 0
    sensor_pin 3 → protocol index 1
    sensor_pin 4 → protocol index 2
    sensor_pin 5 → protocol index 3
```

### 2.6 Sequence Diagram: Correct Behavior

```
RC AI                              Emulator
│                                     │
│──── RESET; ─────────────────────────►│
│◄─── VERSION (56 02 01 00 00 3B) ────│
│                                     │
│  versionVerified = true             │
│                                     │
│──── PI 4 D0 D1 D2 D3 ; ────────────►│
│                                     │ stores mapping:
│                                     │   list[0]=0, list[1]=1, list[2]=2, list[3]=3
│                                     │ builds reverse map:
│                                     │   internal_pin_2 → protocol_index_0
│                                     │   internal_pin_3 → protocol_index_1
│                                     │   internal_pin_4 → protocol_index_2
│                                     │   internal_pin_5 → protocol_index_3
│                                     │
│◄─── HEARTBEAT (reset_flag=1) ───────│  (initial state broadcast via heartbeat)
│◄─── INPUT D pin=0 state=1 ─────────│  (pin 0 = HIGH, sensor idle)
│◄─── INPUT D pin=1 state=1 ─────────│  (pin 1 = HIGH, sensor idle)
│◄─── INPUT D pin=2 state=1 ─────────│  (pin 2 = HIGH, sensor idle)
│◄─── INPUT D pin=3 state=1 ─────────│  (pin 3 = HIGH, sensor idle)
│                                     │
│  [race starts]                      │
│                                     │
│  [lane 1 completes a lap]           │
│                                     │
│◄─── HEARTBEAT (delta) ─────────────│
│◄─── INPUT D pin=0 state=1 ─────────│  (HIGH — sensor_on)
│◄─── INPUT D pin=0 state=0 ─────────│  (LOW — sensor_off → lap triggered)
│                                     │
│  onInput(digital, pin=0, state=0)   │
│  key = "D0" → pinLookup hit        │
│  laneIndex = 0 → lap for lane 1 ✓  │
```

---

## 3. Alternative Fix Evaluation

---

### Option A: Process PI command and dynamically build pin index mapping

**Description:** Parse the `PI` command in the emulator. When RC AI sends `PI 4 D0 D1 D2 D3 ;`, the emulator stores the list of protocol indices received. A reverse mapping is built from `track.json` sensor pins to protocol indices (using list position correspondence). When `pulse_sensor(physical_pin)` is called, the physical pin is translated to the protocol index before building the INPUT message.

| Criterion | Assessment |
|---|---|
| Complexity | **Medium.** Requires parsing a new command type, building a mapping, and modifying `pulse_sensor` or `build_input_*`. |
| Risk | **Low.** No changes to the race_runtime logic. The mapping is a simple dict lookup. |
| Compatibility with profiles | **Full.** `track.json` keeps physical pin numbers. No profile changes needed. |
| Future hardware emulation | **Excellent.** When a real Arduino is used, the same PI command is processed naturally by firmware. The emulator mirrors this exactly. |
| Maintainability | **Good.** The PI handling is self-documenting and matches the protocol spec. |
| Protocol fidelity | **Highest.** Exactly replicates what the real Arduino does. |

---

### Option B: Change track.json sensor pins to logical indices (0, 1, 2, 3)

**Description:** Modify `track.json` so that `sensor_pin` values become 0, 1, 2, 3 instead of physical pins 2, 3, 4, 5. The emulator sends these values directly in INPUT messages. No PI parsing needed.

| Criterion | Assessment |
|---|---|
| Complexity | **Lowest.** Just change 4 numbers in a JSON file. |
| Risk | **Medium.** `track.json` now contains protocol-level semantics (indices) mixed with physical semantics (relay pins). Confusing for maintainers. |
| Compatibility with profiles | **Breaking.** Changes the meaning of `sensor_pin` from physical to logical. If the system later moves to real hardware, `sensor_pin` must be reverted to physical values. |
| Future hardware emulation | **Poor.** Physical Arduino uses real pin numbers. This approach diverges from reality. |
| Maintainability | **Poor.** The JSON mixes physical relay pins with logical sensor indices. A maintainer reading `sensor_pin: 0` would not understand why lane 1 uses pin 0. |
| Protocol fidelity | **Low.** Does not replicate the real PI command processing. Works only by coincidence of values matching. |

---

### Option C: Internal translation layer between track.json and serial protocol

**Description:** Introduce a mapping layer inside the emulator that translates physical sensor pins from `track.json` to protocol indices before building INPUT messages. The mapping is hardcoded or configured statically, without processing the PI command.

| Criterion | Assessment |
|---|---|
| Complexity | **Low.** A simple dict: `{2: 0, 3: 1, 4: 2, 5: 3}`. |
| Risk | **Medium.** The mapping is hardcoded, so if RC AI sends different indices in the PI command, the mapping is wrong. Fragile. |
| Compatibility with profiles | **Full.** `track.json` unchanged. |
| Future hardware emulation | **Poor.** Hardcoded mapping cannot adapt to different RC AI configurations. |
| Maintainability | **Poor.** Magic numbers. Breaks if RC AI uses a different pin configuration. |
| Protocol fidelity | **Low.** Does not react to the actual PI command. |

---

## 4. Recommendation

**Option A — Process the PI command and dynamically build pin index mapping.**

### Justification

1. **Protocol fidelity:** The emulator must behave like the real Arduino. The real Arduino processes the PI command and echoes received indices back in INPUT messages. Option A replicates this exactly.

2. **Architectural correctness:** The PI command is the canonical source of truth for pin assignments. Processing it is the only approach that correctly handles any RC AI configuration, regardless of how many lanes are configured or which indices are assigned.

3. **Future maintainability:** When adding support for new sensor types (segment counters, pit sensors), the same PI command processing naturally covers them. No hardcoded mappings to maintain.

4. **Compatibility:** `track.json` retains its current physical pin semantics. The mapping is built dynamically at runtime from the PI command + `track.json` correlation.

---

## 5. Impact Analysis

### Files expected to change

| File | Change | Purpose |
|---|---|---|
| [serial_protocol.py](file:///Users/gersonferreira/projetos/rcai-virtual-track/track_interface/serial_protocol.py) | Add `MESSAGE_PIN_MODE_READ` constant and parsing logic for the `PI` command | Recognize the PI command |
| [arduino_emulator.py](file:///Users/gersonferreira/projetos/rcai-virtual-track/track_interface/arduino_emulator.py) | Add `handle_pin_mode_read()` method, store protocol index mapping, add `get_protocol_index(physical_pin)` method | Process PI command and translate pins |
| [arduino_emulator.py](file:///Users/gersonferreira/projetos/rcai-virtual-track/track_interface/arduino_emulator.py) | Modify `sensor_on()`, `sensor_off()`, `pulse_sensor()` to translate physical pin → protocol index before building INPUT messages | Use protocol indices in serial messages |
| [arduino_emulator.py](file:///Users/gersonferreira/projetos/rcai-virtual-track/track_interface/arduino_emulator.py) | After PI command processing, broadcast initial INPUT state for each configured pin | Initial state broadcast (mirrors `bReset = true`) |

### Estimated implementation complexity

**Small.** Approximately 40–60 new lines of code across two files.

The PI command has a known, fixed structure. Parsing is straightforward. The mapping is a simple dict. The translation in `sensor_on`/`sensor_off` is a one-line lookup.

### Expected side effects

1. **The emulator will now print `[COMMAND] UNKNOWN` less frequently** during startup, because the PI command will be recognized instead of falling through to the unknown handler.

2. **The `PO` (PIN_MODE_WRITE) and other unrecognized commands will still produce `[COMMAND] UNKNOWN`** unless also parsed. This is acceptable — they don't affect lap counting.

3. **Sensor events will use protocol indices (0, 1, 2, 3) instead of physical pin numbers (2, 3, 4, 5)** in the serial stream. This changes the raw bytes sent to RC AI, which is the intended correction.

### Potential regressions

1. **If the PI command is not received** (e.g., RC AI not connected, standalone testing), the mapping will be empty and `pulse_sensor()` will have no translation available. **Mitigation:** If no mapping exists, fall back to sending the physical pin number (current behavior). This preserves standalone testing.

2. **If RC AI sends a different number of pins than `track.json` has lanes**, the mapping may be partial. **Mitigation:** Log a warning when the mapping size doesn't match the track configuration. Map by list position (first PI entry → first track.json lane, etc.).

### Required homologation steps

See Section 6.

---

## 6. Homologation Plan

### Test 1 — PI Command Recognized

**Procedure:**
1. Start emulator with `DEBUG_SERIAL = True`
2. Connect RC AI
3. Observe logs

**Expected:**
```
[COMMAND] RESET
[COMMAND] PIN_MODE_READ count=4 pins=[D0, D1, D2, D3]
```

The `PI` command is no longer reported as `[COMMAND] UNKNOWN`.

**Verification:** Visual log inspection.

---

### Test 2 — Index Mapping Stored

**Procedure:**
1. Start emulator
2. Connect RC AI
3. Observe logs after PI command

**Expected:**
```
[PIN MAP] sensor_pin 2 → protocol index 0
[PIN MAP] sensor_pin 3 → protocol index 1
[PIN MAP] sensor_pin 4 → protocol index 2
[PIN MAP] sensor_pin 5 → protocol index 3
```

**Verification:** Visual log inspection.

---

### Test 3 — Initial State Broadcast

**Procedure:**
1. Start emulator with `DEBUG_SERIAL = True`
2. Connect RC AI
3. Observe TX messages immediately after PI command

**Expected (serial bytes):**
```
[TX] 0x49 0x44 0x00 0x01 0x3B    ← INPUT D pin=0 state=1
[TX] 0x49 0x44 0x01 0x01 0x3B    ← INPUT D pin=1 state=1
[TX] 0x49 0x44 0x02 0x01 0x3B    ← INPUT D pin=2 state=1
[TX] 0x49 0x44 0x03 0x01 0x3B    ← INPUT D pin=3 state=1
```

**Verification:** Serial byte inspection.

---

### Test 4 — Lane 1 Lap Generates Correct Protocol Index

**Procedure:**
1. Start full system (emulator + race_runtime + RC AI)
2. Assign a vehicle to lane 1
3. RC AI powers lane 1 relay
4. Wait for one lap to generate

**Expected:**
- Emulator sends `INPUT D pin=0 state=1` then `INPUT D pin=0 state=0`
- RC AI `onInput()` receives pin=0 → key=`"D0"` → pinLookup hit → lane index 0 → lap counted for lane 1

**Verification:** RC AI lap counter increments for lane 1.

---

### Test 5 — All Four Lanes Generate Laps

**Procedure:**
1. Start full system
2. Assign vehicles to all 4 lanes
3. RC AI powers all relays
4. Run for 30 seconds

**Expected:**
- RC AI records laps for all 4 lanes
- No `[COMMAND] UNKNOWN` for PI
- Emulator internal lap count approximately matches RC AI lap count

**Verification:** RC AI lap counters > 0 for all lanes. No silent drops.

---

### Test 6 — 60-Second Heat

**Procedure:**
1. Start full system
2. Assign 4 vehicles
3. RC AI starts a 60-second heat
4. Run to completion without Pause/Restart

**Expected:**
- Each lane records approximately 12–15 laps (matching profile `avg_lap` of ~4–5 seconds)
- Lap times are approximately 4–5 seconds (within profile variation bounds)
- No laps lost
- No laps misrouted between lanes

**Verification:** RC AI heat results show realistic lap counts and lap times.

---

### Test 7 — Standalone Mode (No RC AI)

**Procedure:**
1. Start emulator + race_runtime without RC AI connected
2. Let it run for 30 seconds

**Expected:**
- Emulator generates laps internally (visible in logs)
- `pulse_sensor()` falls back to physical pin number (no mapping available)
- No crashes, no errors

**Verification:** No exceptions in logs. System runs cleanly.

---

### Test 8 — GAP-001 Regression Check

**Procedure:**
1. After implementing GAP-A fix, verify GAP-001 instrumentation still works
2. Observe `[GAP001]` log lines

**Expected:**
- GAP-001 instrumentation still fires
- T; timing relationship to heartbeats is unchanged

**Verification:** `[GAP001]` log lines present and consistent.

---

## 7. Execution Plan Update

### Current task sequence (before this analysis):

```
TASK-004    ✓  VehicleState
TASK-004.1  ✓  Runtime Logging Cleanup
TASK-004.2  ✓  Configurable Serial Debug Logging
TASK-005    ✓  Persistent Driver Model
TASK-005.1  ✓  Protocol Reverse Engineering
TASK-005.2  ✓  GAP-001 Validation (instrumentation)
TASK-005.3  ✓  Lap Detection Protocol Audit
TASK-005.5  ✓  GAP-A Fix Design (this document)
```

### Revised recommended task sequence:

```
TASK-006    GAP-A Fix Implementation
            → Process PI command
            → Build physical-to-protocol pin mapping
            → Translate sensor pins in pulse_sensor()
            → Broadcast initial pin states after PI

TASK-006.1  GAP-A Homologation
            → Run Tests 1–8 from Section 6
            → Verify RC AI lap counts

TASK-007    GAP-001 Fix Implementation
            → Send immediate flush heartbeat on T; reception
            → Correct reset_flag timing

TASK-007.1  GAP-001 Homologation
            → Run full 60-second heat
            → Verify lap times match expected ~4–5 second range

TASK-008    Remove GAP-001 Instrumentation
            → Remove DEBUG_GAP001 flag and associated log lines
            → Clean up _last_time_reset_ts
```

### Rationale for ordering:

1. **GAP-A must be fixed first** because it causes complete lap loss. Without this fix, laps are silently dropped or misrouted. GAP-001 causes timing inaccuracies that are impossible to observe if no laps are being counted at all.

2. **GAP-001 remains relevant after GAP-A** because even with correct pin indexing, the timing resync issue will produce wrong lap times and a brief initial blackout window.

3. **Instrumentation removal is deferred** until after both fixes are validated, so the diagnostic logs are available during testing.

### Does GAP-A need a dedicated task?

**Yes.** GAP-A is a protocol-level fix affecting three code layers (parser, emulator, sensor events). It must be implemented, tested, and committed atomically. It cannot be bundled with GAP-001 because the changes are independent and affect different code paths.
