# EXECUTION PLAN

PHASE 1
Virtual Track Foundation

TASK-001 Bootstrap
TASK-002 Hardware Transport
TASK-003 Relay Driven Runtime

(HOMOLOGATED)

## Phase 2 — Vehicle State Architecture

### [ ] TASK-004 — VehicleState

Problem

The current runtime only distinguishes between:

- relay ON
- relay OFF

The vehicle itself has no explicit state.

Expected State Model

text STOPPED POWERED DESLOTTED 

Future states may include:

text COASTING ACCELERATING 

but should not be implemented yet.

Acceptance Criteria

- Create VehicleState abstraction.
- Vehicle state is explicit.
- Runtime no longer infers state solely from relay status.
- No behavior changes compared to current implementation.

---

### [ ] TASK-004.1 — Runtime Logging Cleanup

Problem

Excessive debug log verbosity

Reduce log verbosity by emitting lane state messages
only when a VehicleState transition occurs.

Current behavior:
POWER OFF logged continuously.

New behavior:
Log only when VehicleState changes.

Examples:

STOPPED -> POWERED
POWERED -> STOPPED
POWERED -> DESLOTTED
DESLOTTED -> POWERED

Restrictions:

- No behavior changes.
- No lap generation changes.
- No relay logic changes.
- No deslot logic changes.
- Logging only.

Additional restrictions:

- Do not create new managers.
- Do not create new threads.
- Do not create new state machines.
- Reuse VehicleState introduced in TASK-004.
- Logging transition detection must remain local to the existing runtime flow.

Expected outcome:

Runtime logs become event-oriented instead of polling-oriented.

Example:

Current:

[LANE 1] POWER OFF
[LANE 1] POWER OFF
[LANE 1] POWER OFF
[LANE 1] POWER OFF

Desired:

[LANE 1] STATE -> STOPPED

Homologation criteria:

1. Start runtime with relays OFF.
2. Verify a single STOPPED/OFF message per lane.
3. Turn relay ON.
4. Verify a single POWERED message.
5. Verify laps continue normally.
6. Turn relay OFF.
7. Verify a single STOPPED/OFF message.
8. No repeated spam messages.

---

### [ ] TASK-005 — Persistent Driver Model

Problem

Today a new LapGenerator instance is created every lap.

Current

generator = LapGenerator(profile)
result = generator.generate_lap()

This prevents future stateful driver behavior.

Goal

Introduce a persistent DriverModel object per lane.

A DriverModel instance must be created once when the lane runtime starts and reused for the entire lane lifetime.

Conceptually

Lane 1
 └─ DriverModel

Lane 2
 └─ DriverModel

Lane 3
 └─ DriverModel

Lane 4
 └─ DriverModel

Acceptance Criteria

- DriverModel instance persists for the lifetime of the lane.
- DriverModel survives multiple laps.
- DriverModel is created once per lane.
- Lap generation continues to work.
- No behavior changes.
- No deslot changes.
- No relay changes.
- No state machine changes.

Homologation

1. Runtime starts normally.
2. Laps continue being generated.
3. No observable behavior changes from TASK-004.1.
4. Existing homologation remains valid.

---

### [ ] TASK-006 — DriverModel

Problem

Lap generation currently contains the first pieces of driver behavior.

Examples:

- consistency
- aggression
- deslot probability
- recovery time

A dedicated DriverModel should become the owner of driver behavior.

Target Architecture

text RaceRuntime     |     +-- DriverModel             |             +-- LapGenerator 

Acceptance Criteria

- DriverModel introduced.
- Existing functionality preserved.
- LapGenerator remains internal implementation detail.

---

### [ ] TASK-007 — ProfileManager Helpers

Add helpers:

text get_consistency() get_aggression() get_deslot_probability() get_recovery_time() 

Acceptance Criteria

- Runtime no longer accesses raw profile fields.
- DriverModel consumes helper API.

---

## Phase 3 — Power Management

### [ ] TASK-008 — Immediate Power Loss 

Problem

Current behavior:

text Relay OFF ↓ Current lap finishes ↓ Vehicle stops 

Expected behavior:

text Relay OFF ↓ Vehicle immediately detects power loss ↓ Current movement interrupted 

Acceptance Criteria

- Relay OFF detected without waiting for lap completion.
- Vehicle leaves POWERED state immediately.
- No dependency on lap_time sleep completion.

---

### [ ] TASK-009 — Coasting

Depends On

- TASK-007

Problem

Vehicle should not instantly stop when power disappears.

Expected

text POWERED ↓ Relay OFF ↓ COASTING ↓ STOPPED 

Acceptance Criteria

- Coasting state implemented.
- Behavior deterministic.
- Reproducible during testing.

---

## Phase 4 — Driver Behavior

### [ ] TASK-010 — Starting Model

Problem

All vehicles effectively start instantly.

Expected

Reaction time should vary according to profile.

Example

text 5 4 3 2 1 GO 

Driver A:
Reaction = 0.12s

Driver B:
Reaction = 0.28s

Driver C:
Reaction = 0.41s

Acceptance Criteria

- Configurable reaction time.
- Deterministic when seed is fixed.
- Profile influences launch behavior.

---

## Phase 5 — Physics Layer

### [ ] TASK-011 — Vehicle Physics Model

Introduce:

- mass
- grip
- magnet strength

Purpose

Provide a foundation for future acceleration and coasting calculations.

Acceptance Criteria

- Physics parameters defined.
- No runtime behavior changes yet.

---

### [ ] TASK-012 — Acceleration Model

Depends On

- Vehicle Physics Model

Expected

text STOPPED ↓ ACCELERATING ↓ CRUISING 

Acceptance Criteria

- Vehicle speed becomes stateful.
- Vehicle no longer jumps directly to lap speed.

---

## Phase 6 — Runtime Refactor

### [ ] TASK-013 — Replace Long Blocking Sleeps

Problem

Current architecture:

python sleep(lap_time) pulse_sensor() 

prevents real-time state transitions.

Acceptance Criteria

- Runtime operates using small simulation ticks.
- Vehicle state can change at any moment.
- Relay changes are processed immediately.

---

### [ ] TASK-014 — Event-Driven Vehicle Simulation

Final Objective

Move from:

text generate lap sleep pulse sensor 

to:

text simulate vehicle update state generate events pulse sensors 

Acceptance Criteria

- Lap becomes an emergent event.
- Runtime is state-driven.
- Vehicle behavior is fully modeled.
```
:::

A principal mudança é que eu colocaria VehicleState → DriverModel → Power Loss → Coasting nessa ordem. O TODO original já falava em coasting e física antes de existir uma entidade que representasse o veículo ou o piloto, o que tende a gerar refatorações posteriores.