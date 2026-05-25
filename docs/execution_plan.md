# execution_plan.md
# Virtual Track Hardware Platform — Execution Plan

Version: 1.0
Status: Draft

Derived From:
- spec.md
- architectural.md
- protocol_spec_rcai_arduino.md
- rcai_arduino_wire_protocol.md

---

# 1. Purpose

This document defines the execution strategy for implementing the Virtual Track Hardware Platform.

The purpose of this document is to:

- define implementation order
- minimize architectural ambiguity
- reduce AI hallucination risk
- establish validation checkpoints
- enforce deterministic development

This document does NOT redefine:
- architecture
- protocol semantics
- runtime theory

Those belong to other documents.

---

# 2. Execution Principles

The platform SHALL be developed incrementally.

Each phase MUST:
- compile
- execute
- be testable
- be independently validated

before the next phase begins.

---

# 3. Development Priorities

The project SHALL prioritize:

- protocol correctness
- deterministic behavior
- hardware compatibility
- runtime reproducibility
- modular isolation

over:

- UI
- optimization
- distributed execution
- feature quantity
- premature abstraction

---

# 4. Architectural Constraints

The implementation SHALL:

- preserve strict separation of concerns
- preserve hardware abstraction boundaries
- avoid RMS coupling
- avoid framework-driven architecture
- avoid hidden runtime state

The implementation SHALL prioritize:

- explicit execution flow
- deterministic scheduling
- protocol isolation
- reproducible execution

---

# 5. Technical Stack

## 5.1 Language

The platform SHALL use:

- Python 3.13+

---

## 5.2 Runtime Model

The platform SHALL use:

- single-process execution
- event-driven architecture
- deterministic scheduling

---

## 5.3 Async Model

The platform SHALL use:

- asyncio

---

## 5.4 Persistence

Initial persistence SHALL use:

- SQLite

---

## 5.5 Database Access

The implementation SHOULD prefer:

- sqlite3 standard library

ORM frameworks are optional.

---

## 5.6 Serial Communication

The platform SHALL use:

- pyserial
- pyserial-asyncio

---

## 5.7 Validation

The platform SHALL use:

- pytest
- ruff
- mypy

---

## 5.8 Dependency Management

The platform SHALL use:

- uv
- pyproject.toml

---

# 6. Repository Structure

Recommended repository structure:

```text
src/

  domain/
  application/
  adapters/
  infrastructure/
  interfaces/
  tests/

```

---

# 7. Development Phases
```
Phase                         Goal

Phase 1                       RC AI Protocol Core

Phase 2                       Hardware Adapter Foundation

Phase 3                       Deterministic Scheduler

Phase 4                       Runtime Event System

Phase 5                       Vehicle Runtime Engine

Phase 6                       Infrastructure Persistence

Phase 7                       Vehicle Profile Persistence

Phase 8                       Runtime Simulation

Phase 9                       Orchestrator

Phase 10                      Replay and Deterministic Validation
```

⸻

# 8. Phase 1 — RC AI Protocol Core

Objective

Implement deterministic RC AI wire protocol support.

Scope

This phase includes:

* binary framing
* parser
* serializer
* heartbeat handling
* version negotiation
* protocol validation

This phase does NOT include:

* vehicle simulation
* runtime behavior
* scheduler
* orchestration

⸻

## TASK-001 — Binary Frame Parser

Goal

Implement deterministic parsing of RC AI protocol frames.

Deliverables

* heartbeat parser
* version parser
* input parser
* analog parser
* malformed frame rejection

Validation

* deterministic decoding
* invalid terminator rejection
* opcode validation
* binary fixture tests

Dependencies

None.

⸻

## TASK-002 — Binary Frame Serializer

Goal

Implement deterministic frame serialization.

Deliverables

* heartbeat serializer
* input serializer
* analog serializer
* command serializer

Validation

* byte-perfect output
* deterministic serialization
* fixture validation

Dependencies

* TASK-001

⸻

## TASK-003 — Protocol Constants

Goal

Centralize all protocol opcodes and constants.

Deliverables

* opcode registry
* protocol enums
* framing constants

Validation

* compatibility with protocol documentation

Dependencies

* TASK-001

⸻

## TASK-004 — Virtual Clock Foundation

Goal

Implement deterministic timing abstraction.

Deliverables

* monotonic virtual clock
* delta tracking
* deterministic advancement

Validation

* reproducible timing
* deterministic replay

Dependencies

None.

⸻

## TASK-005 — Heartbeat Engine

Goal

Implement RC AI-compatible heartbeat generation.

Deliverables

* heartbeat scheduler
* reset flag handling
* delta_us generation

Validation

* heartbeat interval validation
* RC AI compatibility

Dependencies

* TASK-002
* TASK-004

⸻

## TASK-006 — Serial Transport Abstraction

Goal

Implement transport-independent serial abstraction.

Deliverables

* abstract transport interface
* pyserial implementation
* mock transport

Validation

* transport isolation
* mock compatibility

Dependencies

* TASK-001
* TASK-002

⸻

## TASK-007 — RC AI Compatibility Harness

Goal

Validate compatibility against RC AI.

Deliverables

* protocol harness
* fixture replay
* compatibility tests

Validation

* successful RC AI connection
* successful version negotiation
* successful heartbeat recognition

Dependencies

* TASK-005
* TASK-006

⸻

# 9. Phase 2 — Hardware Adapter Foundation

Objective

Implement virtual hardware abstraction.

⸻

## TASK-008 — Virtual GPIO Model

Deliverables

* virtual digital pins
* pin state transitions
* pin listeners

⸻

## TASK-009 — Virtual Sensor Model

Deliverables

* lap sensor abstraction
* pit sensor abstraction
* segment sensor abstraction

⸻

## TASK-010 — Relay Abstraction

Deliverables

* relay states
* relay transitions
* lane power abstraction

⸻

## TASK-011 — Pin Mapping System

Deliverables

* dynamic pin assignment
* infrastructure mapping
* lane mapping

⸻

## TASK-012 — Edge Trigger Engine

Deliverables

* HIGH→LOW transitions
* LOW→HIGH transitions
* deterministic pulse generation

⸻

## TASK-013 — Debounce Emulation

Deliverables

* configurable debounce
* stable signal validation
* deterministic filtering

⸻

# 10. Phase 3 — Deterministic Scheduler

Objective

Implement deterministic runtime execution.

⸻

## TASK-014 — Scheduler Core

Deliverables

* event queue
* virtual time ownership
* stable ordering

⸻

## TASK-015 — Delayed Event System

Deliverables

* delayed execution
* scheduled callbacks
* cancellation support

⸻

## TASK-016 — Stable Ordering Guarantees

Deliverables

* deterministic tie-breaking
* reproducible execution ordering

⸻

## TASK-017 — Seeded Randomness

Deliverables

* deterministic RNG
* reproducible runtime variance

⸻

# 11. Phase 4 — Runtime Event System

Objective

Implement runtime event flow.

⸻

## TASK-018 — Event Bus

Deliverables

* runtime events
* subscriptions
* deterministic dispatch

⸻

## TASK-019 — Hardware Translation Layer

Deliverables

* runtime event translation
* GPIO pulse emission
* protocol packet generation

⸻

# 12. Phase 5 — Vehicle Runtime Engine

Objective

Implement active vehicle simulation.

⸻

## TASK-020 — Vehicle Runtime State

⸻

## TASK-021 — Lap Generation Engine

⸻

## TASK-022 — Stochastic Timing Engine

⸻

## TASK-023 — Pit Behavior Engine

⸻

## TASK-024 — Deslot Engine

⸻

## TASK-025 — Runtime Sensor Injection

⸻

# 13. Phase 6 — Infrastructure Persistence

Objective

Persist infrastructure definitions.

⸻

## TASK-026 — SQLite Infrastructure Repository

⸻

## TASK-027 — Track Configuration Persistence

⸻

# 14. Phase 7 — Vehicle Profile Persistence

Objective

Persist vehicle definitions.

⸻

## TASK-028 — Vehicle Profile Repository

⸻

## TASK-029 — Profile Validation

⸻

## TASK-030 — JSON Import/Export

⸻

# 15. Phase 8 — Runtime Simulation

Objective

Integrate runtime with hardware layer.

⸻

## TASK-031 — Runtime-to-Hardware Integration

⸻

## TASK-032 — Multi-Vehicle Runtime

⸻

## TASK-033 — Runtime Lane Occupancy

⸻

# 16. Phase 9 — Orchestrator

Objective

Coordinate complex simulation scenarios.

⸻

## TASK-034 — Vehicle Assignment

⸻

## TASK-035 — Rotation Scheduling

⸻

## TASK-036 — Endurance Flow Coordination

⸻

# 17. Phase 10 — Deterministic Replay

Objective

Guarantee deterministic reproducibility.

⸻

## TASK-037 — Replay Snapshot System

⸻

## TASK-038 — Deterministic Replay Validation

⸻

## TASK-039 — Regression Replay Harness

⸻

# 18. Validation Gates

The project SHALL NOT advance to the next phase unless:

* all tasks compile
* all tests pass
* deterministic validation succeeds
* protocol compatibility remains intact

⸻

# 19. Non-Negotiable Rules

The implementation SHALL NOT:

* directly manipulate RMS state
* bypass hardware abstraction
* couple runtime to RC AI internals
* introduce non-deterministic scheduling
* introduce hidden global state

⸻

# 20. Final Execution Statement

The platform SHALL evolve incrementally.

Each phase MUST remain:

* independently executable
* independently testable
* independently reproducible

The architecture SHALL remain modular throughout all implementation phases.


