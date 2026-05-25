# deterministic_scheduler.md
# Virtual Slot Car Platform — Deterministic Scheduler

Version: 1.0  
Status: Draft  
Derived From:
- spec.md
- architectural.md
- runtime_execution_model.md
- event_bus.md

---

# 1. Purpose

This document defines the deterministic scheduler architecture used by the Virtual Slot Car Platform.

The scheduler is the authoritative execution coordinator of the simulation runtime.

The scheduler is responsible for:
- simulation ordering
- event execution sequencing
- simulation timeline ownership
- deterministic progression
- delayed event execution

The scheduler is NOT:
- a hardware controller
- a serial protocol implementation
- an RMS
- a realtime operating system

---

# 2. Core Philosophy

The scheduler is fundamentally:

```text
A deterministic discrete-event execution coordinator
```

The scheduler coordinates:
- runtime events
- simulation time progression
- event ordering
- delayed execution

through deterministic scheduling rules.

---

# 3. Architectural Position

High-level architecture:

```text
Vehicle Profiles
        ↓
Simulation Runtime
        ↓
Deterministic Scheduler
        ↓
Event Bus
        ↓
Hardware Adapter
        ↓
RC AI
```

The scheduler is the authoritative owner of:
- simulation ordering
- simulation timeline
- event execution sequence

---

# 4. Core Responsibilities

The scheduler is responsible for:

| Responsibility | Description |
|---|---|
| Timeline Ownership | Own simulation progression |
| Event Ordering | Execute events deterministically |
| Delayed Scheduling | Execute future events |
| Stable Replay | Guarantee reproducibility |
| Runtime Coordination | Coordinate runtime execution |
| Timestamp Ordering | Resolve simultaneous events |

---

# 5. Simulation Timeline

# 5.1 Timeline Ownership

The scheduler owns the authoritative simulation timeline.

Only the scheduler may:
- advance simulation time
- commit event ordering
- dispatch authoritative runtime events

---

# 5.2 Deterministic Time Representation

Recommended implementation:
- integer microseconds

Example:

```text
simulation_timestamp_us = 4183521
```

---

# 5.3 Timeline Independence

Simulation time MUST remain independent from:
- wall clock
- operating system timing
- rendering framerate
- hardware polling frequency

---

# 5.4 Event-Driven Progression

The scheduler MAY advance directly to the next scheduled event timestamp.

Example:

```text
4183521 → 4189024
```

without intermediate polling loops.

Continuous fixed-frequency execution is NOT required.

---

# 6. Event Scheduling Model

# 6.1 Discrete Event Scheduling

The scheduler operates using discrete scheduled events.

Examples:
- lap completed
- pit entered
- deslot occurred
- recovery completed

---

# 6.2 Scheduled Event Structure

Conceptual scheduled event:

```text
event_id
event_type
scheduled_timestamp
source_entity
payload
```

---

# 6.3 Immutable Scheduling

Scheduled events SHALL become immutable after insertion into the scheduler queue.

---

# 6.4 Delayed Scheduling

The scheduler SHALL support future execution.

Example:

```text
schedule(
    event="recovery_complete",
    timestamp=5218000
)
```

---

# 7. Queue Architecture

# 7.1 Scheduler Queue

The scheduler queue SHALL maintain:
- deterministic ordering
- timestamp ordering
- stable insertion behavior

---

# 7.2 Recommended Implementation

Recommended implementations:
- priority queue
- binary heap
- ordered event queue

provided deterministic ordering is preserved.

---

# 7.3 Stable Ordering

Events with identical timestamps SHALL execute in deterministic stable order.

Tie-breaking MAY use:
- insertion_order
- event_id
- lane_id
- entity_id

but ordering MUST remain reproducible.

---

# 8. Execution Cycle

# 8.1 Scheduler Execution Cycle

Conceptual execution cycle:

```text
1. select next scheduled event
2. advance simulation timeline
3. dispatch event
4. execute runtime consequences
5. generate resulting events
6. enqueue resulting events
7. commit ordering
```

---

# 8.2 Continuous Polling

The scheduler architecture does NOT require:
- busy waiting
- realtime polling
- fixed-frequency loops

---

# 8.3 Timeline Advancement

The simulation timeline advances according to:
- scheduled event timestamps
- deterministic execution ordering

not according to CPU cycles.

---

# 9. Deterministic Guarantees

# 9.1 Core Guarantee

Given:
- same seed
- same profiles
- same infrastructure
- same scheduling inputs

the scheduler MUST produce:
- identical event ordering
- identical dispatch timing
- identical runtime progression

---

# 9.2 Replayability

The scheduler SHALL support deterministic replay.

Replay systems MAY reconstruct:
- runtime progression
- lap sequences
- deslot behavior
- pit behavior

using:
- immutable event logs
- deterministic timestamps
- deterministic seeds

---

# 9.3 Floating Point Restriction

Authoritative scheduler timing SHOULD avoid floating-point arithmetic.

Recommended:
- integer timestamps

This avoids:
- floating point drift
- replay divergence
- nondeterministic ordering

---

# 10. Randomness Integration

# 10.1 Deterministic Randomness

All stochastic behavior SHALL use deterministic pseudo-random generation.

---

# 10.2 Seed Ownership

The scheduler owns the authoritative simulation seed context.

Example:

```text
seed = 123456
```

---

# 10.3 Reproducibility

Random generation MUST remain reproducible across:
- replay sessions
- benchmark sessions
- regression validation

---

# 11. Runtime Entity Coordination

# 11.1 Runtime Ownership

The scheduler coordinates active runtime entities.

Examples:
- active vehicles
- pit states
- deslot states
- lane occupancy

---

# 11.2 Entity Isolation

Runtime entities MUST NOT manipulate:
- simulation timeline
- event ordering
- dispatch sequence

Those belong exclusively to the scheduler.

---

# 12. Concurrency Model

# 12.1 Determinism Priority

Determinism has priority over parallel execution.

---

# 12.2 Authoritative Execution

Authoritative scheduler execution SHALL remain single-threaded.

This guarantees:
- stable ordering
- replayability
- deterministic execution

---

# 12.3 Non-Authoritative Parallelism

Parallelism MAY exist in:
- telemetry
- logging
- analytics
- persistence
- visualization

provided those systems do not alter authoritative ordering.

---

# 13. Hardware Isolation

# 13.1 Scheduler Boundary

The scheduler does NOT know:
- serial protocols
- GPIO structures
- RC AI packets
- adapter internals

---

# 13.2 Hardware Translation

Hardware translation occurs only after:
- scheduler ordering
- event dispatch
- Event Bus transport

---

# 13.3 Fundamental Rule

The scheduler operates exclusively on:
- abstract runtime events
- simulation timestamps
- runtime entities

---

# 14. Failure Isolation

# 14.1 Scheduler Isolation

Scheduler failures MUST NOT corrupt:
- infrastructure persistence
- profile repository
- RMS state

---

# 14.2 Queue Isolation

Queue corruption MUST remain isolated from:
- hardware adapters
- telemetry systems
- replay systems

---

# 14.3 Adapter Isolation

Hardware adapter failures MUST NOT alter:
- scheduler ordering
- simulation timeline
- deterministic guarantees

---

# 15. Future Evolution

Future scheduler capabilities MAY include:
- distributed scheduling
- clustered simulation
- deterministic rollback
- snapshot recovery
- replay acceleration
- hybrid physical/virtual runtime

provided deterministic guarantees remain preserved.

---

# 16. Final Architectural Statement

The deterministic scheduler is fundamentally:

```text
The authoritative owner of simulation ordering and timeline progression
```

It is NOT:
- hardware
- RMS logic
- protocol implementation
- realtime firmware

The scheduler exists to preserve:
- deterministic execution
- stable ordering
- replayability
- simulation consistency

while remaining fully isolated from hardware protocols and RMS internals.
