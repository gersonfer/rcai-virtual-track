# event_bus.md
# Virtual Slot Car Platform — Event Bus Architecture

Version: 1.0  
Status: Draft  
Derived From:
- spec.md
- architectural.md
- runtime_execution_model.md

---

# 1. Purpose

This document defines the Event Bus architecture of the Virtual Slot Car Platform.

The Event Bus is responsible for transporting abstract runtime events between isolated runtime domains while preserving:

- deterministic ordering
- execution isolation
- replayability
- runtime decoupling
- hardware abstraction

The Event Bus is NOT:
- a hardware protocol
- a serial transport
- a network protocol
- a message broker
- an RMS integration layer

---

# 2. Core Philosophy

The Event Bus exists to transport abstract simulation events.

The Event Bus does NOT transport:
- serial packets
- GPIO transitions
- RMS commands
- hardware frames

The Event Bus transports only:

```text
runtime domain events
```

Examples:
- vehicle crossed lap sensor
- vehicle entered pit
- vehicle deslotted
- relay activation requested

---

# 3. Architectural Position

High-level flow:

```text
Simulation Runtime
        ↓
Event Bus
        ↓
Hardware Adapter
        ↓
RC AI
```

The Event Bus is the formal boundary between:
- runtime behavior
- hardware translation

---

# 4. Architectural Principles

The Event Bus SHALL guarantee:

| Principle | Description |
|---|---|
| Deterministic Ordering | Stable execution ordering |
| Immutable Events | Events cannot mutate after dispatch |
| Runtime Isolation | Producers do not manipulate consumers |
| Replayability | Event flow can be reproduced |
| Hardware Independence | Runtime unaware of hardware details |
| RMS Independence | No RMS semantics inside bus |

---

# 5. Event Model

# 5.1 Abstract Events

All transported events SHALL be abstract runtime events.

Examples:

```text
vehicle_crossed_lap_sensor
vehicle_entered_pit
vehicle_deslotted
vehicle_recovered
```

---

# 5.2 Forbidden Event Types

The Event Bus MUST NOT transport:
- COM packets
- serial bytes
- GPIO HIGH/LOW commands
- RMS API requests
- protocol-specific frames

Those belong exclusively to hardware adapters.

---

# 5.3 Event Structure

Conceptual event structure:

```text
event_id
event_type
simulation_timestamp
source_entity
payload
```

---

# 5.4 Immutable Event Rule

Events SHALL become immutable immediately after dispatch.

Consumers MUST NOT mutate:
- payload
- timestamps
- event identifiers

---

# 6. Event Ownership

# 6.1 Producer Ownership

The producer owns event creation.

The producer does NOT own:
- event execution order
- consumer lifecycle
- dispatch timing

---

# 6.2 Scheduler Ownership

The scheduler owns:
- ordering
- dispatch sequence
- execution timeline

---

# 6.3 Consumer Ownership

Consumers own:
- event interpretation
- local reaction
- local state updates

Consumers do NOT own:
- event ordering
- simulation time
- runtime scheduling

---

# 7. Event Ordering

# 7.1 Deterministic Ordering

Events MUST execute in deterministic order.

Given:
- same seed
- same configuration
- same event sequence

the Event Bus MUST produce identical dispatch ordering.

---

# 7.2 Same Timestamp Ordering

Events sharing the same simulation timestamp SHALL execute in stable deterministic order.

Tie-breaking MAY use:
- insertion order
- event_id
- lane_id
- entity_id

but ordering MUST remain reproducible.

---

# 7.3 Ordering Ownership

Only the scheduler controls authoritative ordering.

Consumers MUST NOT reorder events.

---

# 8. Event Dispatching

# 8.1 Dispatch Model

The Event Bus is conceptually event-driven.

Implementations MAY use:
- priority queues
- append-only queues
- deterministic pipelines
- scheduled dispatch queues

provided deterministic ordering is preserved.

---

# 8.2 Continuous Polling

The architecture does NOT require:
- high-frequency polling loops
- realtime polling execution
- busy waiting

---

# 8.3 Event Timestamping

All events SHALL contain deterministic simulation timestamps.

Recommended implementation:
- integer microseconds

Example:

```text
simulation_timestamp_us = 4183521
```

---

# 9. Event Categories

# 9.1 Runtime Events

Examples:
- lap completed
- pit entry
- pit exit
- deslot
- recovery

---

# 9.2 Infrastructure Events

Examples:
- relay requested
- lane power change
- external signal activation

---

# 9.3 Future Event Categories

Future systems MAY introduce:
- telemetry events
- replay events
- analytics events
- orchestration events

provided abstraction boundaries remain preserved.

---

# 10. Hardware Translation Boundary

# 10.1 Runtime Boundary

The runtime ends at abstract event emission.

---

# 10.2 Adapter Responsibility

Hardware adapters translate abstract events into:
- GPIO transitions
- serial packets
- protocol frames
- relay signaling

---

# 10.3 Fundamental Rule

The Event Bus MUST remain protocol-agnostic.

The Event Bus MUST NOT know:
- RC AI packet formats
- Arduino protocol details
- serial transport structures

---

# 11. Concurrency Model

# 11.1 Deterministic Priority

Determinism has priority over parallelism.

---

# 11.2 Authoritative Ordering

Authoritative dispatch ordering SHALL remain single-threaded.

This guarantees:
- replayability
- stable execution
- reproducible simulations

---

# 11.3 Parallel Consumers

Non-authoritative consumers MAY operate asynchronously.

Examples:
- telemetry exporters
- logging systems
- visualization systems

provided they do not alter authoritative runtime ordering.

---

# 12. Failure Isolation

# 12.1 Consumer Failure Isolation

Consumer failures MUST NOT corrupt:
- scheduler state
- event ordering
- runtime state

---

# 12.2 Adapter Failure Isolation

Hardware adapter failures MUST NOT corrupt:
- event queues
- runtime entities
- scheduler ownership

---

# 12.3 Queue Failure Isolation

Queue failures MUST remain isolated from:
- RMS
- persistence
- infrastructure definitions

---

# 13. Replay Support

# 13.1 Replayability

The Event Bus architecture SHALL support deterministic replay.

Replay systems MAY reconstruct:
- runtime behavior
- event ordering
- simulation progression

using:
- immutable event logs
- deterministic timestamps
- deterministic seeds

---

# 13.2 Replay Constraints

Replay correctness requires:
- immutable events
- deterministic ordering
- stable timestamps

---

# 14. Persistence Integration

# 14.1 Event Persistence

Future implementations MAY persist:
- runtime event streams
- replay logs
- analytics streams

---

# 14.2 Persistence Isolation

Persistence systems MUST remain external to:
- scheduler ownership
- dispatch ordering
- runtime authority

---

# 15. Future Evolution

Future Event Bus capabilities MAY include:
- distributed runtime nodes
- remote telemetry consumers
- replay streaming
- simulation clustering
- analytics pipelines

provided deterministic execution remains preserved.

---

# 16. Final Architectural Statement

The Event Bus is fundamentally:

```text
A deterministic abstract event transport layer
```

It is NOT:
- hardware
- RMS integration
- serial communication
- network middleware

The Event Bus exists to preserve strict separation between:
- runtime behavior
- hardware translation
- orchestration
- RMS integration
while maintaining deterministic execution guarantees.
