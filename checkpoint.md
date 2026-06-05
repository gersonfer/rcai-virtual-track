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
Homologation: Approved

Behavior validated:
- `LapGenerator` component created in `orchestrator/lap_generator.py`.
- Driver behavior and lap calculation logic successfully separated.
- `DriverModel` delegates statistical calculations to `LapGenerator`, while retaining behavioral decision ownership (e.g., deslotting).
- Functionality preserved with no behavioral regressions.

## Phase 5 — Physics Layer

### TASK-012 — Vehicle Physics Model

Status: Completed
Homologation: Pending Approval

Behavior validated:
- `physics` block added to all vehicle profiles containing `scale`, `mass_grams`, `magnet_downforce_grams`, `grip_multiplier`, and `rear_tire_diameter_mm`.
- `VehiclePhysics` frozen dataclass created.
- `ProfileManager.get_vehicle_physics()` successfully parses the new parameters.
- No runtime behavior changes introduced (as requested).

## Phase 4 — Driver Behavior

### TASK-011 — Starting Model

Status: Completed
Homologation: Approved

Behavior validated:
- `reaction_time` added to profiles under `behavior`.
- `DriverModel.generate_reaction_time()` applies deterministic random variance to the profile baseline.
- `RaceRuntime` detects when the vehicle transitions from `STOPPED` (or starts the session).
- Adds `reaction_time` to both the active lap wait loop and the final published telemetry log.
- Correctly applies penalty to both grid starts and resumes from power loss.

### TASK-010 — Partial Lap Persistence

Status: Completed
Homologation: Approved

Behavior validated:
- Added `pending_lap` dictionary to `lane_loop`.
- System tracks `remaining_time = lap_time - elapsed_lap` upon `MOMENTUM_LOST`.
- Skips generating a new lap if `pending_lap` is present, resuming exactly where it left off.
- Deslot penalties intrinsically preserved during multiple pause/resume cycles.

### TASK-009 — Coasting

Status: Completed
Homologation: Approved

Behavior validated:
- `COASTING` state added to `VehicleState`.
- `coasting_duration` successfully externalized to `track.json`.
- Loss of track power places vehicles into the `COASTING` state.
- Time-based model perfectly handles "carry-over" lap finishes if momentum is sufficient.
- Insufficient momentum correctly transitions to `STOPPED` and discards the lap.

### TASK-009.1 — Coasting Instrumentation & Log Cleanup

Status: Completed
Homologation: Approved

Behavior validated:
- `[COASTING]` decision block outputs exact values.
- `[COASTING RESULT]` strictly logs `LAP_COMPLETED` or `MOMENTUM_LOST`.
- Background noise (heartbeats, repetitive relay states) eliminated from terminal output.

### TASK-009.2 — Improve Event Visibility

Status: Completed
Homologation: Approved

Behavior validated:
- `DESLOT` log moved to immediately follow lap generation.
- Deslot events are fully visible even if the lap is subsequently aborted.

### TASK-007 — ProfileManager Helpers

Status: Completed
Homologation: Approved

Behavior validated:
- Added `DriverParameters` dataclass to orchestrator.
- `ProfileManager` extended with `get_driver_parameters()`.
- `DriverModel` fully isolated from raw profile dictionaries, taking `DriverParameters` instead.
- Functionality preserved with strong architectural foundation for fatigue and learning.

### TASK-008 — Immediate Power Loss

Status: Completed
Homologation: Pending Approval

Behavior validated:
- Monolithic `time.sleep` replaced with an interruptible polling loop using `time.monotonic()`.
- Power loss correctly triggers an immediate `STATE -> STOPPED` transition mid-lap.
- Laps interrupted by power loss are completely discarded (no trailing sensor pulse).



