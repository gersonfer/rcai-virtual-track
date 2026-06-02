# TASK-006.1 Protocol Differential Analysis

## Objective
Determine why RC AI continues to ignore lap events after dynamic pin mapping (GAP-A fix) was successfully implemented.

## 1. Trace: Real Arduino Firmware (INPUT path)
1. **Physical Read**: `iPinSignal = digitalRead(pReadPins[i])` is polled continuously in the `loop()`. The pin is configured as `INPUT_PULLUP`, so its default idle state is `HIGH`.
2. **Debounce Validation**: Transitions are passed to `setupStateChange` and `handleDebounce`. The firmware waits for `ulDebounceLowUs` or `ulDebounceHighUs` to elapse without bouncing.
3. **Time Flush**: Once debounced, `sendStateChange()` is called. The very first action inside this function is **`sendTime(ulCurTimeMs)`**. This forces a `T` (Heartbeat) packet to be transmitted over serial, carrying the exact microsecond delta up to the moment the pin changed.
4. **INPUT Transmission**: Immediately after the heartbeat, the firmware builds the `I` array (`[0x49, pinType, pinIndex, pinState, 0x3B]`) and calls `Serial.write`. 

## 2. Trace: Emulator (INPUT path)
1. **Trigger**: `pulse_sensor(pin, pulse_ms)` is called by the `LapGenerator`.
2. **Initial State**: Calls `sensor_on()`, transmitting `[0x49, 0x44, proto_idx, 1, 0x3B]`.
3. **Wait**: Sleeps for `pulse_ms` (default 30ms).
4. **Active State**: Calls `sensor_off()`, transmitting `[0x49, 0x44, proto_idx, 0, 0x3B]`.
5. **Time Flush**: **None**. The emulator relies entirely on the background `heartbeat_loop` (which fires every 500ms) to update Java's clock.

## 3. Byte Comparison (build_input_on / off)

| Byte Index | Purpose | Real Arduino (sendStateChange) | Emulator (build_input_*) | Match? |
|------------|---------|--------------------------------|--------------------------|---------|
| 0 | Opcode | `0x49` ('I') | `0x49` ('I') | ✅ Yes |
| 1 | Pin Type | `0x44` ('D') | `0x44` ('D') | ✅ Yes |
| 2 | Pin Index| Logical index matching `PI` list | `proto_idx` from `PI` map | ✅ Yes |
| 3 | State | `0x01` (HIGH) or `0x00` (LOW) | `1` or `0` | ✅ Yes |
| 4 | Terminator| `0x3B` (';') | `0x3B` (';') | ✅ Yes |

**Conclusion on Bytes:** The payload of the `INPUT` messages is perfectly identical. GAP-A correctly fixed the `Pin Index` mapping, so the issue is not in the `INPUT` packet formatting.

## 4. Java Protocol Expectations (RC AI)
By analyzing `ArduinoProtocol.java`:
- **Lap Detection:** Handled in `onLapCounter()`. It registers a lap when `state == wantState`. For default settings (`INPUT_PULLUP`), `wantState = 0` (LOW).
- **Time Calculation:** When the lap is triggered, Java calculates the lap's absolute timestamp using: `double time = hwLapTime[laneIndex].time();`
- **Time Accumulation:** `hwLapTime` is strictly updated by incoming Heartbeat (`T`) packets in `onHeartbeat()`. It accumulates the `timeInUse` delta from each heartbeat.
- **Time Correction:** Java blindly subtracts the configured debounce delay from this time: `time -= (config.debounceUs / 1000000.0)`.

## 5. Ranked Hypotheses

### 1. Hypothesis: The Missing Preceding Heartbeat (GAP-B)
**Severity: CRITICAL**
Because the real Arduino calls `sendTime()` immediately before sending the `INPUT` message, Java's `hwLapTime` clock is perfectly synchronized to the exact microsecond of the sensor event. 
The emulator does **not** send a heartbeat before pulsing the sensor. Consequently, when Java evaluates `hwLapTime[laneIndex].time()`, it uses a stale timestamp from the last background heartbeat (which could be up to 500ms old).
- **Why this rejects laps:** If a lap occurs shortly after a race start (or a T; reset), before the first 500ms heartbeat fires, `hwLapTime` is exactly `0`. Java then subtracts `debounceUs` (e.g., 20ms), resulting in a **negative absolute lap time** (e.g., `-0.020s`). Race Coordinator's RMS core silently rejects laps with negative or logically impossible timestamps.

### 2. Hypothesis: GAP-001 Sync Delay
**Severity: HIGH**
When RC AI sends `T;` (TIME_RESET), the real Arduino immediately flushes its current time delta `sendTime(0xffffffff)`, and marks the *next* heartbeat to carry `reset_flag = 1`. 
The emulator currently sets `self.reset_flag = 1` but does **not** perform an immediate flush. Java sets `hwReset = 1` internally and waits for the matching heartbeat. This creates a synchronization window where Java's clock is frozen until the emulator's 500ms loop finally broadcasts the reset flag. Any laps generated during this frozen window are evaluated against a broken clock.

### 3. Hypothesis: Missing `INPUT` State Bouncing
**Severity: LOW**
The emulator manually sends `HIGH` then `LOW` then `HIGH` artificially. The real firmware only sends the debounced state. Given Java only reacts to `state == wantState`, redundant `HIGH` messages before the `LOW` pulse are harmless.

## Conclusion
The `INPUT` messages themselves are structurally perfect. The root cause of the missing laps is entirely temporal: **Java's hardware clock (`hwLapTime`) is stale or broken at the exact moment the `INPUT` message arrives**, because the emulator fails to prefix sensor events with a Heartbeat update (GAP-B), and fails to immediately flush time upon receiving a `T;` command (GAP-001).
