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

Task-005
Status: Not Started