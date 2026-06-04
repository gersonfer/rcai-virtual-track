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

### TASK-004 — VehicleState

Status: Completed
Homologation: Approved

Behavior validated:
- VehicleState abstraction created.
- Race runtime explicitly tracks states (STOPPED, POWERED, DESLOTTED) avoiding log spam.

### TASK-005 — Persistent Driver Model

Status: Completed
Homologation: Approved

Behavior validated:
- Persistent `DriverModel` introduced.
- Single instance per lane successfully persists across laps without being recreated.
- Existing lap generation functionality completely preserved.

### TASK-006 — DriverModel

Status: Completed
Homologation: Pending Approval

Behavior validated:
- `LapGenerator` component created in `orchestrator/lap_generator.py`.
- Driver behavior and lap calculation logic successfully separated.
- `DriverModel` delegates statistical calculations to `LapGenerator`, while retaining behavioral decision ownership (e.g., deslotting).
- Functionality preserved with no behavioral regressions.

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

