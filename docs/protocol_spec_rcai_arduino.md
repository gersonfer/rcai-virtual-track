# protocol_spec_rcai_arduino.md
# Virtual Slot Car Platform — RC AI Arduino Protocol Specification

Version: 1.0  
Status: Draft  
Derived From:
- spec.md
- architectural.md
- hardware_adapter_contract.md
- event_bus.md
- deterministic_scheduler.md

---

# 1. Purpose

This document defines the protocol specification for the RC AI Arduino-compatible Hardware Adapter.

The purpose of this protocol is to allow the Virtual Slot Car Platform to emulate a physical Arduino-based track controller compatible with RC AI.

The adapter SHALL make RC AI believe it is connected to real track electronics.

---

# 2. Scope

This document defines:

- protocol architecture
- transport assumptions
- adapter responsibilities
- sensor signaling semantics
- relay signaling semantics
- heartbeat behavior
- timing constraints
- mapping behavior
- lifecycle expectations

This document does NOT define:
- RC AI internal implementation
- RC AI database structures
- simulation runtime behavior
- vehicle logic
- orchestration logic

---

# 3. Architectural Position

```text
Simulation Runtime
        ↓
Deterministic Scheduler
        ↓
Event Bus
        ↓
RC AI Arduino Adapter
        ↓
Serial Transport
        ↓
RC AI
```

The adapter translates abstract runtime events into Arduino-compatible protocol behavior.

---

# 4. Protocol Philosophy

The adapter SHALL emulate:

```text
physical Arduino track electronics
```

The adapter SHALL NOT expose:
- simulator semantics
- runtime internals
- virtual vehicle state
- replay semantics

The protocol SHALL appear identical to real hardware behavior from the perspective of RC AI.

---

# 5. Transport Layer

# 5.1 Transport Type

Initial transport:

```text
serial communication
```

---

# 5.2 Recommended Serial Parameters

Recommended defaults:

| Parameter | Value |
|---|---|
| Baud Rate | 115200 |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |

Actual implementation MAY vary according to RC AI requirements.

---

# 5.3 Transport Independence

The runtime and scheduler SHALL remain transport-independent.

Future transports MAY include:
- TCP bridge
- USB HID
- CAN bus
- virtual COM bridge

without altering runtime architecture.

---

# 6. Protocol Responsibilities

The adapter SHALL support:

- heartbeat communication
- lap sensor signaling
- pit sensor signaling
- relay signaling
- GPIO abstraction
- dynamic lane mapping
- dynamic pin mapping
- runtime event translation

---

# 7. Non-Responsibilities

The adapter SHALL NOT:
- calculate lap times
- simulate vehicle behavior
- manage race standings
- manage heat rotation
- interpret championship rules
- own official race timing

Those responsibilities belong to:
- runtime
- scheduler
- RC AI

---

# 8. Sensor Signaling Model

# 8.1 Conceptual Sensor Model

The adapter emulates physical sensor activation.

Examples:
- lap sensor triggered
- pit sensor triggered
- segment sensor triggered

---

# 8.2 Runtime Input

Runtime input example:

```json
{
  "event_type": "vehicle_crossed_lap_sensor",
  "simulation_timestamp_us": 4183521,
  "payload": {
    "lane_id": 2
  }
}
```

---

# 8.3 Hardware Translation

The adapter translates the abstract event into protocol-compatible hardware behavior.

Conceptually:

```text
sensor active
sensor inactive
```

This may become:
- serial packet
- GPIO transition
- digital input signal

depending on protocol implementation.

---

# 8.4 Sensor Pulse Behavior

The adapter SHALL define:
- pulse activation
- pulse duration
- pulse release
- debounce behavior
- minimum pulse interval

The exact values MAY depend on:
- RC AI protocol expectations
- hardware compatibility behavior

---

# 8.5 Sensor Isolation

The adapter SHALL NOT know:
- which vehicle triggered the sensor
- race standings
- driver names

The adapter only knows:
- lane
- sensor type
- activation timing

---

# 9. Relay Signaling Model

# 9.1 Relay Purpose

The protocol SHALL support relay state changes.

Examples:
- lane power on/off
- race start lights
- external outputs

---

# 9.2 Relay Ownership

RC AI MAY be the authoritative owner of relay behavior.

The adapter SHALL expose relay state transitions to the platform when required.

---

# 9.3 Relay Mapping

Relay outputs SHALL be dynamically mapped through infrastructure configuration.

Example:

```yaml
lane_id: 2
relay_pin: D11
```

---

# 10. Dynamic Infrastructure Mapping

# 10.1 No Hardcoded Lane Count

The adapter SHALL NOT hardcode:
- lane count
- pin count
- race structure

---

# 10.2 Supported Configurations

The adapter SHALL support:
- 2 lanes
- 4 lanes
- 6 lanes
- 8 lanes
- arbitrary future configurations

through configuration only.

---

# 10.3 Dynamic Sensor Mapping

Example:

```yaml
lanes:
  - lane_id: 1
    lap_sensor_pin: D2

  - lane_id: 2
    lap_sensor_pin: D3
```

The adapter SHALL dynamically resolve runtime events to configured protocol outputs.

---

# 11. Heartbeat Contract

# 11.1 Heartbeat Responsibility

The adapter SHALL implement protocol heartbeat behavior required by RC AI.

---

# 11.2 Heartbeat Ownership

Heartbeat handling belongs exclusively to the adapter layer.

The runtime SHALL remain unaware of:
- heartbeat packets
- serial keepalive behavior
- connection liveness details

---

# 11.3 Heartbeat Failure

Heartbeat failure MAY move the adapter into:
- degraded state
- reconnecting state
- failed state

according to adapter policy.

---

# 12. Timing Model

# 12.1 Runtime Timing Source

The runtime produces deterministic simulation timestamps.

Recommended representation:
- integer microseconds

---

# 12.2 Adapter Timing Responsibility

The adapter translates deterministic simulation events into realistic protocol timing behavior.

The adapter does NOT require:
- cycle-accurate emulation
- hard realtime guarantees
- microcontroller-level timing fidelity

unless explicitly required by RC AI behavior.

---

# 12.3 Priority

The adapter SHOULD prioritize:
- protocol validity
- stable ordering
- pulse consistency

over ultra-high timing precision.

---

# 12.4 Timing Ownership Split

| Layer | Responsibility |
|---|---|
| Scheduler | deterministic simulation ordering |
| Event Bus | ordered event transport |
| Adapter | protocol emission timing |
| RC AI | official race timing interpretation |

---

# 13. Adapter Lifecycle

# 13.1 Lifecycle States

Conceptual lifecycle:

```text
created
configured
initialized
running
paused
stopping
stopped
failed
```

---

# 13.2 Running State

When running, the adapter MAY:
- emit sensor events
- process relay changes
- maintain heartbeat
- exchange protocol messages

---

# 13.3 Paused State

During pause:
- runtime-generated sensor events stop
- protocol heartbeat MAY continue

---

# 13.4 Failed State

Adapter failure MUST remain isolated from:
- runtime scheduler
- profile repository
- infrastructure persistence

---

# 14. Event Translation Contract

# 14.1 Runtime Events

Input:

```text
vehicle_crossed_lap_sensor
```

---

# 14.2 Protocol Translation

Translated into:

```text
digital sensor pulse
```

---

# 14.3 RMS Interpretation

RC AI interprets the resulting hardware signal as:
- physical sensor activation
- lane passage
- lap completion

The adapter does NOT send:
- lap times
- standings
- rankings

Only hardware behavior.

---

# 15. Deterministic Ordering

# 15.1 Ordering Guarantee

The adapter SHALL preserve runtime event ordering.

Events emitted by the Event Bus MUST remain ordered when translated into protocol behavior.

---

# 15.2 Same Timestamp Events

Events sharing the same simulation timestamp SHALL preserve deterministic ordering defined by the scheduler.

---

# 15.3 No Adapter Reordering

The adapter MUST NOT reorder authoritative runtime events.

---

# 16. Error Handling

# 16.1 Error Categories

The adapter SHOULD distinguish:

| Error Type | Description |
|---|---|
| Transport Error | Serial communication failure |
| Protocol Error | Invalid protocol exchange |
| Heartbeat Error | Connection timeout |
| Mapping Error | Missing lane/sensor mapping |
| Timing Error | Missed emission window |
| Fatal Error | Adapter cannot continue |

---

# 16.2 Error Isolation

Adapter failures MUST NOT corrupt:
- runtime scheduler
- event ordering
- deterministic guarantees
- infrastructure persistence

---

# 16.3 Recovery

The adapter MAY support:
- reconnect
- reinitialize
- resume
- degraded mode

Recovery behavior SHALL remain adapter-local.

---

# 17. Capability Reporting

Example capability report:

```json
{
  "adapter_name": "rcai_arduino_serial",
  "transport": "serial",
  "supports_heartbeat": true,
  "supports_lap_sensors": true,
  "supports_pit_sensors": true,
  "supports_relays": true,
  "supports_dynamic_mapping": true,
  "max_lanes": null
}
```

---

# 18. Testing Requirements

The adapter SHOULD support testing for:

- heartbeat behavior
- sensor pulse generation
- relay signaling
- mapping validation
- deterministic ordering preservation
- failure isolation
- reconnect behavior

---

# 19. Future Evolution

Future protocol capabilities MAY include:
- additional sensor types
- segmented track support
- hybrid physical/virtual tracks
- distributed adapters
- multi-controller synchronization

provided protocol abstraction remains preserved.

---

# 20. Fundamental Constraint

The RC AI Arduino adapter MUST remain independently usable.

It SHALL support:
- protocol testing
- RC AI compatibility validation
- firmware validation
- integration testing

without requiring:
- runtime simulation
- vehicle profiles
- orchestrator systems

---

# 21. Final Architectural Statement

The RC AI Arduino Adapter is fundamentally:

```text
A protocol-compatible virtual hardware controller
```

It is NOT:
- an RMS extension
- a runtime engine
- a race manager
- a telemetry engine

Its sole responsibility is to translate abstract runtime events into valid RC AI-compatible hardware behavior through Arduino-style protocol emulation.
