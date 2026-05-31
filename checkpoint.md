# Checkpoint

## Current Status

### Task-001
Status: Completed
Homologation: Approved

### Task-002
Status: Completed
Homologation: Approved

### Task-003
Status: Completed
Homologation: Approved

Behavior validated:

- Relay ON allows lap generation.
- Relay OFF blocks lap generation.
- Vehicle may finish current lap after relay OFF.
- Immediate power-loss reaction not yet implemented.

## Known Limitations

### Immediate Power Loss

Current behavior:

Relay OFF
→ finish current lap
→ stop

Future task required.

### Vehicle Coasting

Not implemented.

Future task required.

### TASK-003.1 — Remove Hardcoded Serial Configuration

## Objective

Remove the hardcoded serial configuration from arduino_emulator.py.
The emulator must obtain
- serial.port
- serial.baudrate
from config/track.json instead of using fixed constants.

## Current Situation

arduino_emulator.py currently contains:
PORT = "/dev/pts/4"
BAUDRATE = 115200
This duplicates configuration that already exists in:
config/track.json

## Required Changes

1. Eliminate the hardcoded PORT constant.
2. Eliminate the hardcoded BAUDRATE constant.
3. Load both values from:
config/track.json
using the existing configuration mechanism already present in the project whenever possible.
4. The ArduinoEmulator must use:
config["serial"]["port"]
config["serial"]["baudrate"]
as its serial configuration source.

## Validation

If you open config/track.json and change the block:

json
"serial": {
    "port": "/dev/pts/5",
    "baudrate": 115200
  },
The next time you run arduino_emulator.py, the __main__ loop will parse the JSON, extract "/dev/pts/5", and initialize the emulator via:

python
emulator = ArduinoEmulator(
        port="/dev/pts/5",
        baudrate=115200,
    )
No Python files need to be modified. You will see [EMULATOR] Starting on /dev/pts/5 automatically logged.

Status: Completed
Homologation: Approved

### TASK-004 — Introduce VehicleState
Status: Completed
Homologation: Pending Approval

Files modified:
- `orchestrator/vehicle_state.py` (Created)

Architectural decisions:
- Introduced `VehicleState` Enum (`STOPPED`, `POWERED`, `DESLOTTED`) in a dedicated file `orchestrator/vehicle_state.py`.
- Intentionally kept `RaceRuntime` and `LapGenerator` unmodified for this step to strictly adhere to the rule of keeping implementation minimal and preserving TASK-003 homologated behavior. The structure is now prepared to be integrated in future tasks.

Validation steps executed:
- Confirmed that by creating a new standalone module without changing `race_runtime.py` or `lap_generator.py`, the existing runtime compiles successfully and homologation behavior from TASK-003 remains functionally identical. 
- Relay ON still generates laps, and Relay OFF still blocks new lap generation.

## Next Task

### TASK-004.1 — Runtime Logging Cleanup
Status: Completed
Homologation: Pending Approval

Files modified:
- `orchestrator/race_runtime.py`

Architectural decisions:
- Introduced a local `current_state` variable in the `lane_loop` to track transitions using the `VehicleState` enum.
- Replaced the repetitive `POWER OFF` log with event-oriented logs (`STATE -> STOPPED`, `STATE -> POWERED`, `STATE -> DESLOTTED`) that only trigger on transitions.
- Kept the detection local to the loop without creating any new managers or state machines.
- Retained the existing relay and lap logic unmodified.

Validation steps executed:
- Confirmed that starting the runtime with relays OFF outputs a single `STATE -> STOPPED` message per lane.
- Confirmed that toggling the relay ON outputs a single `STATE -> POWERED` message per lane.
- Confirmed that deslotting outputs a single `STATE -> DESLOTTED` message per lane.

## Next Task

### TASK-005 — Persistent Driver Model
Status: Completed
Homologation: Pending Approval

Files modified:
- `orchestrator/lap_generator.py` (renamed to `orchestrator/driver_model.py`)
- `orchestrator/driver_model.py` (refactored `LapGenerator` to `DriverModel` and added `set_profile`)
- `orchestrator/race_runtime.py`

Architectural decisions:
- Transformed the transient `LapGenerator` into a persistent `DriverModel` object.
- Created a single `DriverModel` instance per lane before the `while self.running:` loop.
- The runtime dynamically injects the lane's profile into the `DriverModel` using `set_profile` on every iteration, instead of reconstructing the object.
- Existing behaviors remain unmodified.

Validation steps executed:
- Confirmed that the runtime compiles successfully with the renamed module and refactored class.
- Confirmed that lap generation output is functionally identical to previous tasks.
- Confirmed that `driver.generate_lap()` runs seamlessly with dynamic profile assignment.

## Next Task

### TASK-004.2 — Configurable Serial Debug Logging
Status: Completed
Homologation: Pending Approval

Files modified:
- `track_interface/arduino_emulator.py`

Architectural decisions:
- Introduced a `DEBUG_SERIAL = False` flag in `arduino_emulator.py`.
- Wrapped the highly verbose `[TX]`, `[RX]`, `[RX COMMAND]`, and `[COMMAND RAW]` logs in a conditional check against `DEBUG_SERIAL`.
- Did not change any protocol behavior, runtime timing, or execution logic.
- Kept other diagnostic logs (LAP, STATE, DESLOT, OUTPUT) unmodified.

Validation steps executed:
- Confirmed that setting `DEBUG_SERIAL = False` suppresses the raw byte streams and command logs, leaving only event-oriented behavior logs.
- Confirmed that setting `DEBUG_SERIAL = True` restores all original verbose RX/TX messages.
- Confirmed no lap generation or race execution flow was altered.

## Next Task

### TASK-005.2 — GAP-001 Validation
Status: Completed
Homologation: Pending Approval

Files modified:
- `track_interface/arduino_emulator.py`

Changes:
- Added `DEBUG_GAP001 = True` config flag.
- Added `_last_time_reset_ts` instance variable to track when the last T; was received.
- Modified `heartbeat_loop` to snapshot `reset_flag` before clearing it, then log heartbeat timing and `reset_flag` value relative to last T; reception.
- Modified `handle_command` (TIME_RESET branch) to record the reception timestamp and log at +0 ms.

Expected log output (hypothesis: CONFIRMED gap):
```
[GAP001] T; received at +0 ms (reset_flag currently=0)
[GAP001] HEARTBEAT sent +487.3ms after T; reset_flag=1
[GAP001] HEARTBEAT sent +986.5ms after T; reset_flag=0
```

Expected log output (hypothesis: gap NOT present):
```
[GAP001] T; received at +0 ms (reset_flag currently=0)
[GAP001] HEARTBEAT sent +11.2ms after T; reset_flag=1
```

No behavior changes were made. This is instrumentation only.

## Next Task

Task-006
Status: Not Started