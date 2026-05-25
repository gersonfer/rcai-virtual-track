# Virtual Track Hardware Platform — Specification

Version: 1.0  
Status: Draft  
Scope: Foundational Platform Specification

---

# 1. Purpose

The purpose of this project is to create a modular virtual slot-car track hardware platform capable of emulating physical track infrastructure for integration with external Race Management Systems (RMS).

The platform does NOT replace the RMS.

The RMS remains the authoritative source for:
- race control
- heats
- lane assignments
- penalties
- fuel management
- race states
- timing
- leaderboard
- officiating

The platform behaves as:
- virtual hardware
- virtual sensors
- virtual relays
- virtual track electronics

The first supported RMS is:
- RC AI

The first supported hardware adapter is:
- Arduino-compatible serial protocol

Future adapters may include:
- PIC
- ESP32
- TCP bridges
- USB HID
- CAN bus
- OXIGEN bridges

---

# 2. Architectural Principles

The platform SHALL be modular.

The following concerns MUST remain separated:

| Concern | Responsibility |
|---|---|
| Hardware Emulation | Protocol + GPIO + relays |
| Track Infrastructure | Lanes + sensors + mappings |
| Vehicle Profiles | Persistent behavioral definitions |
| Runtime Simulation | Dynamic vehicle behavior |
| Race Orchestration | Race scenario coordination |
| RMS | Official race control |

The system SHALL NOT collapse these responsibilities into a single runtime process.

---

# 3. System Overview

The platform is composed of independent bounded contexts.

## 3.1 Hardware Interface Layer

### Responsibility

Emulate physical track controller hardware.

### Responsibilities Include

- serial communication
- protocol compatibility
- heartbeat handling
- GPIO abstraction
- relay abstraction
- sensor signaling
- hardware timing behavior

### Examples

- Arduino Adapter
- PIC Adapter
- ESP32 Adapter

### Non-Responsibilities

The hardware layer SHALL NOT know:
- car profiles
- race standings
- heat rotation
- driver information
- leaderboard
- race strategy

It behaves exactly like physical hardware.

---

## 3.2 Track Infrastructure Model

### Responsibility

Represent physical track infrastructure.

### Concepts

- lanes
- lap sensors
- pit sensors
- segment sensors
- relays
- external outputs
- GPIO mappings

### Example

```yaml
track:
  name: "4 Lane Test Track"

  lanes:
    - lane_id: 1
      lap_sensor_pin: D2
      relay_pin: D10

    - lane_id: 2
      lap_sensor_pin: D3
      relay_pin: D11
```

### Important Constraint

The infrastructure layer SHALL NOT know:
- vehicles
- race schedules
- pilots
- race control

It models only infrastructure.

---

# 4. Vehicle Profile Repository

## Purpose

Store behavioral definitions for virtual vehicles.

This module is persistence-only.

It does NOT execute simulation.

---

## Responsibilities

- CRUD
- import/export
- validation
- persistence
- presets

---

## Example Vehicle Profile

```json
{
  "name": "Ferrari 499P",
  "avg_lap": 4.2,
  "min_lap": 4.0,
  "max_lap": 4.8,
  "consistency": 0.92,
  "deslot_probability": 0.01,
  "fuel_factor": 1.0,
  "tire_wear": 0.2
}
```

---

## Non-Responsibilities

The repository SHALL NOT:
- generate laps
- communicate with RMS
- inject sensor events
- execute runtime behavior

---

# 5. Simulation Runtime Engine

## Purpose

Provide dynamic behavior to vehicle profiles.

The runtime engine is responsible for transforming static vehicle profiles into active simulation behavior.

---

## Responsibilities

- lap generation
- stochastic timing
- deslot simulation
- fuel consumption
- tire degradation
- pit behavior
- runtime scheduling
- event generation
- sensor triggering

---

## Runtime Flow

Correct architecture:

```text
Simulation Runtime
        ↓
Hardware Adapter
        ↓
RC AI
```

Incorrect architecture:

```text
Simulation Runtime
        ↓
RC AI directly
```

---

## Critical Rule

The runtime SHALL NOT directly communicate with the RMS.

All interaction occurs through hardware abstraction.

The RMS must believe it is connected to real hardware.

---

# 6. Race Orchestrator (Future Module)

## Purpose

Coordinate large simulation scenarios.

---

## Future Responsibilities

- assigning cars to lanes
- endurance rotations
- automated heat flows
- scenario scripting
- multi-car orchestration

---

## Important Constraint

The orchestrator SHALL remain optional.

RC AI continues being:
- the authoritative RMS
- the race controller

---

# 7. Hardware Adapter Specification

## Initial Adapter

### Arduino-Compatible Adapter

The first implementation SHALL emulate:
- RC AI Arduino serial protocol
- heartbeat protocol
- digital inputs
- relay outputs
- GPIO behavior

---

## Adapter Requirements

The adapter SHALL support:
- dynamic lane counts
- dynamic pin mappings
- multiple sensor types
- multiple relay types
- runtime pin reconfiguration

The adapter SHALL NOT hardcode:
- number of lanes
- number of vehicles
- race structures

---

# 8. Dynamic Lane Model

The system SHALL support:
- any number of lanes
- any sensor mapping
- any relay mapping

Examples:
- 2 lanes
- 4 lanes
- 6 lanes
- 8 lanes

without code changes.

---

# 9. Dynamic Vehicle Model

Vehicle count is independent from lane count.

Example:

| Physical Lanes | Active Vehicles |
|---|---|
| 4 | 2 |
| 4 | 4 |
| 4 | 6 |
| 8 | 12 |

The runtime decides:
- which vehicle occupies which lane
- when rotations occur
- which profiles are active

The hardware layer does not know this.

---

# 10. Conceptual Separation

## Physical Layer

```text
Lane = physical infrastructure
```

Examples:
- GPIO
- sensors
- relays
- track wiring

---

## Logical Layer

```text
Vehicle = behavioral profile
```

Examples:
- Ferrari 499P
- Porsche 963
- Aston Martin Valkyrie

---

## Runtime Layer

```text
Runtime Engine = entity that gives life to profiles
```

The runtime:
- activates profiles
- calculates behavior
- injects virtual sensor events

through the hardware abstraction layer.

---

# 11. Deterministic Execution

The runtime SHALL support deterministic execution.

Given:
- identical seed
- identical profiles
- identical runtime settings

the simulation SHALL produce reproducible results.

This enables:
- testing
- benchmarking
- regression validation
- repeatable simulations

---

# 12. Initial Development Phases

## Phase 1 — Hardware Adapter Emulator

Deliverables:
- Arduino-compatible serial emulator
- heartbeat support
- GPIO emulation
- relay emulation
- pin mapping
- RC AI compatibility

No vehicle simulation yet.

---

## Phase 2 — Track Infrastructure Model

Deliverables:
- lane modeling
- sensor configuration
- relay configuration
- persistence
- infrastructure UI

Still no vehicle simulation.

---

## Phase 3 — Vehicle Profile Repository

Deliverables:
- profile CRUD
- JSON import/export
- persistence layer
- validation

Still no runtime behavior.

---

## Phase 4 — Simulation Runtime Engine

Deliverables:
- lap generation
- stochastic timing
- deslot simulation
- runtime scheduler
- event injection

---

## Phase 5 — Race Orchestrator

Deliverables:
- multi-vehicle orchestration
- endurance scenarios
- automated rotations
- scripted simulation flows

---

# 13. Non-Goals

The platform SHALL NOT:
- replace RC AI
- become a full RMS
- control official timing
- manage official leaderboard
- implement officiating
- implement championship logic

Those remain RMS responsibilities.

---

# 14. Fundamental Constraint

The hardware adapter layer MUST remain independently usable.

It must support:
- protocol testing
- firmware validation
- RMS testing
- integration testing

without requiring:
- vehicle profiles
- runtime simulation
- orchestration engine

This guarantees:
- modularity
- replaceability
- protocol isolation
- future extensibility

---

# 15. Long-Term Vision

The final platform SHALL support:

- interchangeable hardware adapters
- interchangeable RMS systems
- deterministic simulation
- endurance race simulation
- profile-driven vehicle behavior
- scalable lane counts
- scalable vehicle counts
- modular runtime orchestration

while preserving strict separation between:
- hardware
- runtime
- orchestration
- RMS.
