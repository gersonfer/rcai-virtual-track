# GAP-B Validation Plan (TASK-006.2)

## Objective
Validate the hypothesis (GAP-B) that RC AI drops/ignores lap events because it evaluates timestamps using a stale clock, caused by the emulator's failure to send an immediate Heartbeat flush prior to `INPUT` messages.

## Files Modified
- `track_interface/arduino_emulator.py`

## Exact Behavior Added
- Added an internal `_flush_heartbeat()` method to `ArduinoEmulator` that calculates the delta elapsed since `self.last_heartbeat`, packages it into a `T` message, clears the `reset_flag`, and transmits it over serial.
- Injected `self._flush_heartbeat()` immediately before the transmission of the `I` (INPUT) packet in both `sensor_on()` and `sensor_off()`.
- Added the diagnostic log `[GAP-B] HEARTBEAT FLUSH BEFORE INPUT` to track execution.
- Maintained all existing pin mappings, debounce configurations, pulse widths, and the asynchronous `heartbeat_loop`.

## Expected Protocol Sequence (Before Change)
```
... (up to 500ms elapse)
[TX] I D 2 1 ;   (INPUT ON)
... (30ms sleep)
[TX] I D 2 0 ;   (INPUT OFF)
...
[TX] T ... ;     (Asynchronous Heartbeat loop wakes up and sends time)
```
Java `onInput` processes the events using `hwLapTime` calculated from the last, potentially 500ms-old heartbeat.

## Expected Protocol Sequence (After Change)
```
[TX] T ... ;     (Flush heartbeat with exact elapsed microseconds since last heartbeat)
[TX] I D 2 1 ;   (INPUT ON)
... (30ms sleep)
[TX] T ... ;     (Flush heartbeat with exact elapsed 30ms)
[TX] I D 2 0 ;   (INPUT OFF)
```
Java `onInput` processes the events with a perfectly synchronized `hwLapTime`.

## Expected Observations During Manual Homologation
1. Start the emulator and connect RC AI.
2. Start a race heat.
3. Observe the emulator logs. You should see the `[GAP-B] HEARTBEAT FLUSH BEFORE INPUT` message immediately preceding any sensor `[TX] I D ...` output.
4. **Validation Target:** RC AI should now correctly register the laps and increase the lap counter for the active lanes on the screen.
5. If the lap counter increases successfully, GAP-B is the confirmed root cause of the missing laps.

## Rollback Instructions
To remove the instrumentation and revert to the previous state:
1. Open `track_interface/arduino_emulator.py`.
2. Remove the `_flush_heartbeat()` method completely.
3. Remove the `self._flush_heartbeat()` call inside `sensor_on()`.
4. Remove the `self._flush_heartbeat()` call inside `sensor_off()`.
