# architectural.md
# Virtual Slot Car Platform — Architecture Document

Version: 1.0  
Status: Draft  
Derived From: spec.md

---

# 1. Purpose

This document defines the architecture of the Virtual Slot Car Platform.

The platform is designed to emulate physical slot-car track hardware while remaining fully decoupled from:

- RMS internals
- race rules
- race orchestration
- vehicle simulation logic

The architecture is modular and extensible.

---

# 2. Architectural Principles

The architecture is based on the following principles:

## 2.1 Hardware Abstraction

The RMS must believe it is connected to real hardware.

The simulator must behave like:
- an Arduino controller
- a PIC controller
- or another future embedded controller

The RMS must not know it is interacting with a simulator.

---

## 2.2 Strict Separation of Concerns

The platform is divided into isolated domains:

| Domain | Responsibility |
|---|---|
| Hardware Interface | Emulate physical controller |
| Infrastructure Model | Represent physical track |
| Vehicle Profile Repository | Store vehicle behavior data |
| Simulation Runtime | Generate virtual race behavior |
| Orchestrator | Coordinate runtime scenarios |
| RMS | Official race control |

No domain may absorb responsibilities from another domain.

---

## 2.3 RMS Independence

The simulator must not depend on:
- RC AI internals
- RC AI database structures
- RC AI runtime state

Communication must happen exclusively through hardware protocols.

---

## 2.4 Protocol Independence

The runtime engine must not know:
- serial packet structures
- GPIO details
- hardware protocol specifics

Protocols belong exclusively to hardware adapters.

---

## 2.5 Dynamic Scalability

The architecture must support:
- arbitrary lane counts
- arbitrary sensor counts
- arbitrary relay counts
- arbitrary vehicle counts

without code restructuring.

---

# 3. High-Level Architecture

```text
+---------------------------------------------------+
|                   Race Management                 |
|                       RC AI                       |
+--------------------------↑------------------------+
                           |
                           |
+--------------------------↓------------------------+
|              Hardware Interface Layer             |
|                                                   |
|   Arduino Adapter                                 |
|   PIC Adapter                                     |
|   ESP32 Adapter                                   |
|   Future Adapters                                 |
+--------------------------↑------------------------+
                           |
                           |
+--------------------------↓------------------------+
|             Track Infrastructure Layer            |
+--------------------------↑------------------------+
                           |
                           |
+--------------------------↓------------------------+
|               Simulation Runtime Layer            |
+--------------------------↑------------------------+
                           |
                           |
+--------------------------↓------------------------+
|             Vehicle Profile Repository            |
+---------------------------------------------------+
```

---

# 4. Hardware Interface Layer

# 4.1 Purpose

The Hardware Interface Layer emulates physical electronics.

It behaves like a real embedded controller.

Examples:
- Arduino
- PIC
- ESP32

---

# 4.2 Responsibilities

The Hardware Interface Layer is responsible for:

- serial communication
- packet parsing
- heartbeat exchange
- GPIO signaling
- relay signaling
- sensor signaling
- protocol timing

---

# 4.3 Non-Responsibilities

The Hardware Interface Layer must not know:

- race standings
- vehicle identities
- lap averages
- driver names
- championship logic
- heat orchestration
- race strategies

---

# 4.4 Core Concept

The Hardware Interface Layer only transports signals.

It does not understand race semantics.

Example:

The adapter knows:
- "GPIO 3 changed state"

It does not know:
- "Ferrari completed lap 17"

---

# 4.5 Adapter Interface

All adapters must expose a common abstraction.

Example conceptual interface:

```python
initialize()
shutdown()
send_sensor_event()
set_relay_state()
send_heartbeat()
```

---

# 4.6 Future Extensibility

Future adapters may include:

- Arduino
- PIC
- ESP32
- USB HID
- TCP bridge
- CAN bus
- Ethernet controller

The runtime layer must remain unchanged when adapters change.

---

# 5. Track Infrastructure Layer

# 5.1 Purpose

Represent physical track infrastructure.

This layer models:
- lanes
- sensors
- relays
- GPIO mappings

---

# 5.2 Lane Model

A lane represents physical infrastructure.

A lane contains:
- lap sensor
- relay
- GPIO mapping
- optional segment sensors
- optional pit sensors

A lane does not represent:
- a car
- a driver
- a team

---

# 5.3 Sensor Model

Sensors represent physical detection points.

Examples:
- lap sensor
- pit sensor
- split sensor

---

# 5.4 Relay Model

Relays represent physical outputs.

Examples:
- lane power
- race lights
- external actuators

---

# 5.5 Dynamic Infrastructure

The infrastructure layer must support:

- 2 lanes
- 4 lanes
- 6 lanes
- 8 lanes
- arbitrary future lane counts

without architectural changes.

---

# 5.6 Example Configuration

```yaml
track:
  lanes:
    - lane_id: 1
      lap_sensor_pin: D2
      relay_pin: D10

    - lane_id: 2
      lap_sensor_pin: D3
      relay_pin: D11
```

---

# 6. Vehicle Profile Repository

# 6.1 Purpose

Store behavioral definitions for virtual vehicles.

This is a persistence domain.

Not a runtime domain.

---

# 6.2 Responsibilities

The repository manages:

- profile creation
- profile editing
- profile persistence
- profile validation
- import/export
- presets

---

# 6.3 Vehicle Profile Example

```json
{
  "name": "Ferrari 499P",
  "avg_lap": 4.2,
  "min_lap": 4.0,
  "max_lap": 4.8,
  "consistency": 0.93,
  "deslot_probability": 0.01
}
```

---

# 6.4 Important Constraint

Profiles are static data.

Profiles do not:
- generate laps
- inject events
- communicate with RMS

---

# 7. Simulation Runtime Layer

# 7.1 Purpose

Transform static profiles into active behavior.

This is the core simulation engine.

---

# 7.2 Responsibilities

The runtime engine generates:

- lap timing
- stochastic variation
- deslots
- pit events
- fuel events
- tire degradation
- runtime event scheduling

---

# 7.3 Runtime Flow

Correct runtime flow:

```text
Vehicle Profile
      ↓
Simulation Runtime
      ↓
Hardware Adapter
      ↓
RC AI
```

Incorrect flow:

```text
Vehicle Profile
      ↓
RC AI directly
```

---

# 7.4 Runtime Independence

The runtime must not:
- access RMS internals
- manipulate RMS state
- alter RMS databases

The runtime only emits hardware events.

---

# 7.5 Deterministic Execution

The runtime must support deterministic execution.

Given:
- same seed
- same configuration
- same profiles

the runtime must reproduce identical behavior.

This enables:
- regression testing
- replay systems
- benchmarking

---

# 8. Event Architecture

# 8.1 Abstract Runtime Events

The runtime generates abstract events.

Examples:

```text
vehicle crossed lap sensor
vehicle entered pit
vehicle deslotted
```

---

# 8.2 Hardware Translation

Hardware adapters translate runtime events into:
- serial packets
- GPIO transitions
- relay changes

---

# 8.3 Example Translation

Runtime event:

```text
Vehicle crossed lane 2 lap sensor
```

Hardware translation:

```text
GPIO HIGH
GPIO LOW
```

Serial translation:

```text
DIGITAL_INPUT packet
```

---

# 9. Race Orchestrator Layer

# 9.1 Purpose

Coordinate simulation scenarios.

This layer is optional.

---

# 9.2 Responsibilities

The orchestrator may manage:
- assigning vehicles to lanes
- endurance rotations
- scripted race scenarios
- multi-car coordination

---

# 9.3 Important Constraint

The orchestrator does not replace the RMS.

The RMS remains authoritative for:
- official timing
- race control
- standings
- penalties

---

# 10. RMS Boundary

# 10.1 RMS Role

The RMS remains external.

The RMS owns:
- race lifecycle
- heat management
- timing
- race state
- championship logic

---

# 10.2 Simulator Role

The simulator owns:
- virtual electronics
- virtual infrastructure
- virtual sensors
- virtual relay behavior

---

# 10.3 Fundamental Rule

The simulator must behave like hardware.

Not like a race manager.

---

# 11. Persistence Architecture

# 11.1 Infrastructure Persistence

Stores:
- track definitions
- lane mappings
- sensor mappings
- relay mappings

---

# 11.2 Profile Persistence

Stores:
- vehicle profiles
- presets
- simulation templates

---

# 11.3 Future Persistence

Future capabilities:
- telemetry history
- replay systems
- deterministic replay snapshots

---

# 12. Failure Isolation

# 12.1 Adapter Isolation

Adapter failures must not corrupt:
- profiles
- runtime state
- orchestration state

---

# 12.2 Runtime Isolation

Runtime failures must not corrupt:
- hardware definitions
- infrastructure mappings

---

# 12.3 RMS Isolation

RMS failures must not corrupt:
- simulator state
- profile repository
- infrastructure configuration

---

# 13. Scalability Model

# 13.1 Lane Scaling

The architecture must scale independently of:
- car count
- driver count
- team count

---

# 13.2 Vehicle Scaling

Vehicle count is independent from lane count.

Examples:

| Lanes | Vehicles |
|---|---|
| 4 | 2 |
| 4 | 6 |
| 8 | 12 |

The runtime decides active occupancy.

The hardware adapter only sees lanes.

---

# 14. Future Architecture Evolution

Potential future systems:

- AI driver models
- distributed runtimes
- telemetry dashboards
- replay viewers
- hybrid physical/virtual tracks
- cloud-based simulation clusters

The current architecture must not block future evolution.

---

# 15. Final Architectural Statement

The platform is fundamentally:

```text
A virtual hardware infrastructure platform
```

It is not:
- an RMS
- a race director
- a championship manager

The RMS remains authoritative.

The platform provides virtual electronics and virtual track behavior through strict hardware abstraction.

# 16. Technical Stack and Implementation Standards

16.1 Primary Language

The platform SHALL use:

* Python 3.13+

The implementation SHALL remain compatible with:

* CPython

Alternative runtimes are out of scope.

⸻

# 16.2 Runtime Model

The platform SHALL use:

* single-process architecture
* event-driven execution
* deterministic scheduler

The platform SHALL prioritize:

* deterministic execution
* reproducibility
* protocol correctness

over:

* framework convenience
* distributed execution
* microservice decomposition

⸻

# 16.3 Async Architecture

The platform SHALL use:

* asyncio

Async execution SHALL be used for:

* serial communication
* timers
* protocol adapters
* websocket communication
* future TCP adapters

⸻

# 16.4 Persistence

Initial persistence SHALL use:

* SQLite

Persistence responsibilities include:

* vehicle profiles
* infrastructure configuration
* deterministic replay metadata
* runtime snapshots

⸻

# 16.5 Database Access

The implementation SHOULD prefer:

* sqlite3 standard library

ORM frameworks are optional.

The platform SHALL prioritize:

* deterministic behavior
* low abstraction
* explicit SQL behavior

⸻

# 16.6 Configuration and Validation

The platform SHALL use:

* Pydantic v2

for:

* configuration loading
* validation
* serialization
* schema enforcement

⸻

# 16.7 Serial Communication

Serial communication SHALL use:

* pyserial
* pyserial-asyncio

⸻

# 16.8 Repository Structure

Recommended repository structure:

src/

  domain/
  application/
  adapters/
  infrastructure/
  interfaces/
  tests/

# 16.9 Testing Strategy

The platform SHALL use:

* pytest

Testing MUST include:

* deterministic replay validation
* protocol compatibility tests
* scheduler reproducibility tests
* hardware adapter integration tests

⸻
16.10 Static Analysis

The platform SHALL use:

* ruff
* mypy

⸻

# 16.11 Dependency Management

The platform SHALL use:

* uv
* pyproject.toml

⸻

# 16.12 Architectural Constraints

The platform SHALL avoid:

* framework-driven architecture
* hidden runtime state
* implicit scheduling
* non-deterministic execution models

The platform SHALL prioritize:

* explicit execution flow
* deterministic scheduling
* protocol isolation
* reproducible simulation behavior

⸻  

# 16.13 Target Runtime Environments

Primary development environment:

- macOS Apple Silicon (M1)
- Python 3.13+
- uv-based environment

Primary execution environment:

- Raspberry Pi 4
- Raspberry Pi OS 64-bit
- ARM64
- Python 3.13+

The implementation SHALL remain compatible across:
- macOS ARM64
- Linux ARM64

The implementation SHALL avoid:
- platform-specific dependencies
- x86-only dependencies
- OS-specific execution assumptions

All tasks MUST include:
- macOS validation
- Raspberry Pi reproducibility instructions

The implementation AI SHALL provide:
- environment setup commands
- dependency installation commands
- execution commands
- reproducibility steps

for both environments whenever runtime behavior is affected.

# 17. Project Structure and Control Artifacts

The repository SHALL follow a deterministic and stable structure.

The implementation AI SHALL NOT create arbitrary files outside the defined structure.

---

# 17.1 Root Documents

Mandatory root-level documents:

| File | Responsibility |
|---|---|
| spec.md | Product specification |
| architectural.md | System architecture |
| execution_plan.md | Task sequencing |
| protocol_spec_rcai_arduino.md | Wire protocol specification |
| deterministic_scheduler.md | Scheduler specification |
| runtime_execution_model.md | Runtime execution model |
| hardware_adapter_contract.md | Adapter abstraction contract |
| event_bus.md | Runtime event architecture |

---

# 17.2 Source Tree

Application source code SHALL exist under:

```text
src/

Example:
```
src/
  adapters/
  runtime/
  infrastructure/
  scheduler/
  events/
  profiles/

# 17.3 Test Tree

All automated tests SHALL exist under:

tests/

Mirroring source structure.

Example:
```
tests/
  adapters/
  runtime/
  scheduler/
```

⸻

17.4 Manual Homologation Artifacts

Manual homologation utilities SHALL exist under:

tools/

Example:
```
tools/
  manual_homologation.py
  serial_monitor.py
  protocol_debugger.py
```

These tools are operational artifacts.

They are NOT production runtime components.

⸻

# 17.5 Validation Scripts

Repository-level validation scripts SHALL exist under:

scripts/

Example:
```
scripts/
  run_tests.py
  validate_protocol.py
  deterministic_replay_check.py


⸻

# 17.6 Runtime Fixtures

Protocol fixtures and deterministic replay fixtures SHALL exist under:

fixtures/

Example:
```
fixtures/
  protocol/
  scheduler/
  replay/
```

# 17.7 Documentation Stability

The implementation AI SHALL NOT:

* duplicate specifications
* create competing protocol documents
* create redundant architecture documents
* create undocumented helper scripts

without explicit task requirements.

⸻

# 17.8 Temporary Files

Temporary artifacts SHALL NOT remain committed.

Examples:

* tmp/
* debug.log
* test.bin
* replay.tmp

must remain excluded.

⸻

# 17.9 Python Cache Artifacts

The repository SHALL exclude:

```
__pycache__/
*.pyc
```
via .gitignore.

# 17.10 Deterministic Repository Structure

The repository structure itself is considered part of the architecture.

Structural drift is considered architectural drift.

# 17.11 Checkpoint Authority and Repository Discipline

The file:

`docs/checkpoint.md`

is the authoritative operational state document for the project.

The implementation AI MUST update `checkpoint.md` after every completed task.

Prohibition: No alternative task tracking or progress files shall be created inside the repository or in external structures.

Repository Discipline Rules:
1. No undocumented files may be added outside the defined repository structure.
2. Every structural change requires an update to the "Current Repository Structure" in `checkpoint.md`.
3. Manual homologation procedures MUST be documented in `checkpoint.md` and not only implemented in tooling scripts.

---

# 17.12 Future Task Discipline

Every future task executed by the AI MUST perform the following operations before conclusion:

1. Update `docs/checkpoint.md` with the new task state.
2. Register automated validation results in the Validation History.
3. Register manual verification results in the Manual Homologation History. Every future task MUST append its executable homologation procedure, expected runtime behavior, and expected failure conditions before the task may be considered DONE.
4. Register any newly introduced Architectural Decisions (ADs).
5. Define the Next Recommended Task to ensure continuity.

---

# 17.13 Definition of Done Update

Task completion is strictly INVALID if any of the following conditions are met:

- `docs/checkpoint.md` is not updated.
- Validation history is missing for the executed task.
- Homologation history is missing for the executed task.
