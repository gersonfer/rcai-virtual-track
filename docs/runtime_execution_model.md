# runtime_execution_model.md
# Virtual Slot Car Platform — Runtime Execution Model

Version: 1.0  
Status: Draft  
Derived From:
- spec.md
- architectural.md

---

# 1. Purpose

This document defines the runtime execution model of the Virtual Slot Car Platform.

The purpose of this document is to formally specify:

- runtime timing behavior
- deterministic scheduling
- event ordering
- simulation clock model
- execution flow
- concurrency boundaries
- runtime lifecycle
- event dispatching
- synchronization guarantees

This document applies exclusively to the Simulation Runtime Layer.

It does NOT define:
- RMS behavior
- hardware protocol formats
- persistence formats
- orchestration rules

---

# 2. Runtime Philosophy

The runtime engine is fundamentally:

```text
A deterministic event-driven simulation scheduler

The runtime is NOT:

* a real-time operating system
* a physics engine
* a race manager
* a hardware controller

The runtime generates:

* virtual behavior
* virtual timing
* virtual events

through deterministic scheduling.

⸻

3. Core Execution Principles

The runtime SHALL guarantee:

Principle

Description

Determinism

Same seed produces same execution

Ordered Events

Events execute in stable order

Isolation

Runtime does not manipulate RMS

Hardware Abstraction

Runtime emits abstract events only

Tick Consistency

Simulation time advances predictably

Replayability

Simulations can be reproduced

4. Simulation Clock Model

4.1 Simulation Clock

The runtime SHALL use an internal simulation clock.

The simulation clock is independent from:

* wall clock
* operating system timing
* hardware timing

⸻

4.2 Clock Unit

The simulation clock SHALL operate using:

simulation_tick

The implementation MAY internally use:

* milliseconds
* microseconds
* nanoseconds

but the runtime semantics remain tick-based.

⸻

# 4.3 Deterministic Time Representation

The runtime SHALL use deterministic internal time representation.

Recommended implementation:
- integer microseconds

Example:

lap_time_us = 4183521

The runtime MAY internally use:
- discrete ticks
- monotonic timestamps
- scheduled event queues
- priority-based scheduling

provided execution ordering remains deterministic.

The runtime does NOT require:
- realtime operating system guarantees
- cycle-accurate hardware emulation
- fixed-frequency polling loops

The purpose of the internal time model is:
- deterministic scheduling
- stable ordering
- replayability
- reproducible simulations

⸻

# 4.4 Simulation Timeline Advancement

The runtime advances simulation time according to scheduled event progression.

Implementations MAY use:
- fixed timestep advancement
- event-driven progression
- hybrid scheduling

provided deterministic ordering is preserved.

The runtime architecture does not require continuous polling execution.

⸻

4.5 Deterministic Constraint

Simulation behavior MUST NOT depend on:

* CPU speed
* thread scheduling
* frame rendering
* operating system timing precision

Only simulation ticks determine execution order.

⸻

5. Runtime Scheduler

5.1 Scheduler Purpose

The scheduler coordinates all runtime activity.

The scheduler is responsible for:

* event execution
* simulation timeline progression
* entity updates
* delayed actions
* runtime ordering

⸻

5.2 Scheduler Type

The scheduler SHALL be:

single authoritative deterministic scheduler

The scheduler owns:

* simulation time
* event ordering
* execution sequence

The scheduler is conceptually event-driven.

Implementations MAY use:

* priority queues
* scheduled event dispatching
* deterministic event pipelines

instead of continuous polling loops.

⸻

5.3 Scheduler Responsibilities

The scheduler processes:

* lap events
* pit events
* deslot events
* recovery events
* relay events
* sensor events
* delayed callbacks

⸻

5.4 Event Execution Cycle

For a given simulation timeline position:

1. collect due events
2. sort events deterministically
3. execute events
4. generate resulting events
5. commit execution ordering

The runtime MAY advance directly to the next scheduled event timestamp.

Continuous fixed-frequency polling is NOT required.

5.5 Stable Ordering Guarantee

Events scheduled for the same simulation timestamp SHALL execute in stable deterministic order.

Tie-breaking MAY use:

* event_id
* insertion_order
* lane_id
* vehicle_id

but ordering MUST remain deterministic.

⸻

6. Event Model

6.1 Abstract Runtime Events

The runtime emits abstract events only.

Examples:

vehicle_crossed_lap_sensor

vehicle_entered_pit

vehicle_deslotted

vehicle_recovered

The runtime MUST NOT emit:

* serial packets
* GPIO commands
* protocol frames

Those belong to hardware adapters.

⸻

6.2 Event Structure

Conceptual event structure:

event_id
event_type
scheduled_tick
source_entity
payload

6.3 Immutable Events

Runtime events SHALL be immutable after scheduling.

⸻

6.4 Delayed Events

The scheduler SHALL support future scheduling.

Example:

current_tick = 1000
schedule(deslot_recovery, tick=3500)

7. Runtime Event Bus

7.1 Purpose

The Runtime Event Bus transports abstract events between:

* runtime subsystems
* hardware translation layer
* orchestration systems

⸻

7.2 Architectural Role

The event bus acts as:

runtime → abstract signal transport

It is NOT:

* a hardware protocol
* a serial transport
* a network protocol

⸻

7.3 Event Bus Requirements

The event bus SHALL support:

* deterministic ordering
* queue isolation
* delayed scheduling
* priority handling
* replayability

⸻

7.4 Ordering Constraint

The event bus MUST preserve scheduler ordering guarantees.

⸻

8. Concurrency Model

8.1 Core Principle

Determinism has priority over parallelism.

⸻

8.2 Runtime Core

The authoritative runtime scheduler SHALL execute single-threaded.

This guarantees:

* deterministic ordering
* reproducible execution
* stable replay

⸻

8.3 Parallelism Boundaries

Parallelism MAY exist in:

* persistence
* telemetry
* visualization
* logging
* replay export

but NEVER inside authoritative runtime scheduling.

⸻

8.4 Shared State Restriction

Authoritative runtime state SHALL NOT use:

* shared mutable state
* unsynchronized writes
* lock-contention execution

⸻

9. Randomness Model

9.1 Deterministic Randomness

All stochastic behavior SHALL use deterministic pseudo-random generation.

⸻

9.2 Seed Control

The runtime SHALL support explicit seed injection.

Example:

seed = 123456

9.3 Replay Guarantee

Given:

* same seed
* same profiles
* same configuration
* same event ordering

the runtime MUST produce:

* identical lap timings
* identical deslots
* identical pit behavior

⸻

10. Vehicle Runtime Lifecycle

10.1 Runtime Entity Activation

Vehicle profiles become active runtime entities.

Example:

VehicleProfile → RuntimeVehicle

10.2 Runtime Responsibilities

Active runtime entities may contain:

* current fuel
* tire wear
* deslot state
* lane occupancy
* scheduled actions

⸻

10.3 Runtime Isolation

Runtime entities SHALL remain isolated from:

* hardware protocol details
* RMS internals

⸻

11. Lane Occupancy Model

11.1 Lane Ownership

The runtime owns lane occupancy state.

The infrastructure layer only defines:

* physical lanes
* sensors
* relays

⸻

11.2 Occupancy Example

Example:

Lane 2 currently occupied by Vehicle 5

This is runtime state.

Not infrastructure state.

⸻

11.3 Dynamic Assignment

Vehicle-to-lane assignment may change dynamically.

Examples:

* heat rotation
* pit exits
* endurance swaps

⸻

12. Hardware Translation Boundary

12.1 Runtime Boundary

The runtime ends at abstract event generation.

⸻

12.2 Hardware Adapter Responsibility

Hardware adapters translate abstract events into:

* serial packets
* GPIO transitions
* relay signals
* protocol timing

⸻

12.3 Fundamental Rule

The runtime MUST NEVER:

* manipulate serial ports
* toggle GPIO directly
* generate hardware packets

⸻

13. Runtime Lifecycle

13.1 Initialization

Initialization sequence:

1. load configuration
2. load infrastructure
3. load profiles
4. initialize scheduler
5. initialize runtime entities
6. start tick loop

13.2 Running State

During execution:

* scheduler advances ticks
* events execute
* runtime emits abstract events

⸻

13.3 Pause State

Pause SHALL freeze:

* tick advancement
* event execution
* delayed scheduling

without losing runtime state.

⸻

13.4 Shutdown

Shutdown SHALL:

* stop tick progression
* flush pending persistence
* terminate adapters cleanly

⸻

14. Failure Isolation

14.1 Adapter Failure

Hardware adapter failures MUST NOT corrupt:

* runtime scheduler
* simulation state
* profile state

⸻

14.2 Runtime Failure

Runtime failures MUST NOT corrupt:

* infrastructure persistence
* profile repository

⸻

14.3 Event Bus Failure

Event queue failures MUST remain isolated from:

* RMS
* persistence
* infrastructure definitions

⸻

15. Replay Architecture (Future)

Future runtime implementations MAY support:

* deterministic replay
* event recording
* simulation snapshots
* checkpoint recovery

Replay systems SHALL use:

* scheduler ticks
* deterministic seeds
* immutable event logs

⸻

16. Performance Model

16.1 Runtime Priority

Correctness has priority over throughput.

⸻

16.2 Timing Consistency

Stable deterministic execution is more important than:

* maximum FPS
* CPU utilization
* raw event throughput

⸻

16.3 Scalability

The runtime architecture SHALL scale independently from:

* lane count
* vehicle count
* adapter count

within deterministic constraints.

⸻

17. Final Runtime Statement

The runtime engine is fundamentally:

A deterministic abstract event scheduler

It is NOT:

* hardware
* RMS logic
* protocol implementation

The runtime generates reproducible virtual behavior while remaining fully isolated from hardware protocol details and RMS internals.

