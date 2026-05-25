# hardware_adapter_contract.md
# Virtual Slot Car Platform — Hardware Adapter Contract

Version: 1.0  
Status: Draft  
Derived From:
- spec.md
- architectural.md
- runtime_execution_model.md
- event_bus.md
- deterministic_scheduler.md

---

# 1. Purpose

This document defines the formal contract for Hardware Adapters in the Virtual Slot Car Platform.

A Hardware Adapter is responsible for translating abstract runtime events into hardware-compatible behavior.

The adapter is the boundary between:

```text
abstract simulation behavior
```

and

```text
RMS-compatible hardware signals
```

The first supported adapter is:

```text
Arduino-compatible serial adapter for RC AI
```

Future adapters may include:
- PIC
- ESP32
- TCP bridge
- USB HID
- CAN bus
- OXIGEN bridge

---

# 2. Core Principle

The Hardware Adapter SHALL behave like physical hardware.

The RMS must believe it is connected to a real hardware controller.

The adapter SHALL NOT expose simulator semantics to the RMS.

---

# 3. Architectural Position

```text
Simulation Runtime
        ↓
Deterministic Scheduler
        ↓
Event Bus
        ↓
Hardware Adapter
        ↓
RMS
```

The Hardware Adapter receives abstract events and emits hardware/protocol-specific signals.

---

# 4. Responsibilities

A Hardware Adapter is responsible for:

- protocol compatibility
- serial or transport communication
- heartbeat handling
- GPIO abstraction
- relay signaling
- sensor signaling
- hardware timing behavior
- adapter lifecycle
- capability reporting
- protocol error handling

---

# 5. Non-Responsibilities

A Hardware Adapter SHALL NOT know:

- vehicle profiles
- driver names
- teams
- standings
- leaderboard
- heat rotation
- race strategy
- fuel strategy
- penalties
- championship rules

The adapter only understands hardware-level signals.

---

# 6. Adapter Boundary

The adapter receives:

```text
abstract runtime events
```

Examples:
- vehicle_crossed_lap_sensor
- vehicle_entered_pit
- vehicle_exited_pit
- relay_activation_requested
- lane_power_change_requested

The adapter emits:

```text
hardware-compatible signals
```

Examples:
- serial packet
- GPIO transition
- relay output change
- input pulse
- heartbeat response

---

# 7. Forbidden Coupling

The adapter MUST NOT:

- call RMS APIs directly
- modify RMS databases
- inspect RMS internals
- understand race standings
- manipulate simulation runtime state
- generate vehicle behavior
- schedule laps
- decide race strategy

---

# 8. Adapter Lifecycle

# 8.1 Lifecycle States

An adapter SHALL support the following conceptual lifecycle states:

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

# 8.2 Created

The adapter object exists but has no active hardware or transport connection.

---

# 8.3 Configured

The adapter has received:
- adapter configuration
- track infrastructure mapping
- transport settings
- protocol settings

---

# 8.4 Initialized

The adapter has prepared:
- serial port or transport
- internal buffers
- GPIO abstractions
- relay abstractions
- protocol state

but has not yet started active communication.

---

# 8.5 Running

The adapter actively communicates with the RMS.

It may:
- send sensor events
- receive relay changes
- maintain heartbeat
- process protocol messages

---

# 8.6 Paused

The adapter remains connected but does not emit runtime-generated sensor events.

Heartbeat behavior MAY continue if required by the protocol.

---

# 8.7 Stopping

The adapter is shutting down cleanly.

It SHOULD:
- flush pending output
- close transport cleanly
- release resources

---

# 8.8 Stopped

The adapter is inactive and has released resources.

---

# 8.9 Failed

The adapter encountered an unrecoverable error.

Failure MUST remain isolated from:
- scheduler state
- profile repository
- infrastructure persistence
- RMS internal state

---

# 9. Required Adapter Interface

Conceptual interface:

```text
configure(adapter_config, infrastructure_config)
initialize()
start()
pause()
resume()
stop()
shutdown()
handle_runtime_event(event)
get_status()
get_capabilities()
```

This is a conceptual contract, not a required programming-language interface.

---

# 10. Event Handling Contract

# 10.1 Input

The adapter receives immutable abstract events from the Event Bus.

Example:

```json
{
  "event_id": "evt-000001",
  "event_type": "vehicle_crossed_lap_sensor",
  "simulation_timestamp_us": 4183521,
  "payload": {
    "lane_id": 2,
    "sensor_type": "lap"
  }
}
```

---

# 10.2 Output

The adapter translates the event into protocol-specific behavior.

Example conceptual output:

```text
lane 2 lap sensor pulse
```

For an Arduino-compatible adapter, this may become:
- digital input state transition
- serial event packet
- protocol-specific message

---

# 10.3 Event Immutability

The adapter MUST NOT mutate runtime events.

The adapter MAY create adapter-local derived commands.

---

# 11. Sensor Signaling Contract

# 11.1 Sensor Events

The adapter SHALL support sensor signaling for:

- lap sensors
- pit sensors
- segment sensors
- future sensor types

---

# 11.2 Sensor Pulse Behavior

The adapter SHALL define protocol-specific pulse behavior.

This MAY include:
- active state
- inactive state
- pulse duration
- debounce simulation
- minimum interval

---

# 11.3 Sensor Mapping

The adapter SHALL use infrastructure configuration to map:

```text
lane_id + sensor_type
```

to hardware/protocol output.

Example:

```yaml
lane_id: 2
sensor_type: lap
pin: D3
```

---

# 12. Relay Contract

# 12.1 Relay Events

The adapter SHALL support relay state changes.

Examples:
- lane power on/off
- external light control
- actuator control

---

# 12.2 Relay Ownership

The RMS may be the source of relay commands.

The adapter SHALL expose relay state changes to the platform when required.

The runtime MUST NOT assume that it owns official race power control.

---

# 12.3 Relay Mapping

Relay outputs SHALL be mapped through infrastructure configuration.

Example:

```yaml
lane_id: 2
relay_pin: D11
```

---

# 13. Heartbeat Contract

# 13.1 Heartbeat Responsibility

If the target protocol requires heartbeat behavior, the adapter SHALL implement it.

---

# 13.2 Heartbeat Isolation

Heartbeat behavior belongs to the adapter.

The runtime scheduler and Event Bus SHALL NOT manage protocol heartbeat details.

---

# 13.3 Heartbeat Failure

Heartbeat failure SHALL move the adapter to a degraded or failed state according to adapter policy.

---

# 14. Timing Contract

# 14.1 Runtime Timestamp

Runtime events contain deterministic simulation timestamps.

Recommended representation:
- integer microseconds

---

# 14.2 Adapter Emission Timing

The adapter translates deterministic simulation timing into real transport behavior.

The adapter does NOT need to provide cycle-accurate hardware emulation unless the protocol explicitly requires it.

---

# 14.3 Real-Time Precision

The adapter SHALL aim for realistic hardware behavior, but the platform does NOT require hard real-time guarantees.

The adapter SHOULD preserve:
- event order
- pulse consistency
- protocol validity

over microsecond-level real-time precision.

---

# 14.4 Timing Responsibility Split

| Layer | Owns |
|---|---|
| Scheduler | simulation ordering and timestamps |
| Event Bus | ordered event transport |
| Adapter | hardware/protocol emission timing |
| RMS | official race timing interpretation |

---

# 15. Capability Reporting

Each adapter SHALL report its capabilities.

Example capabilities:

```json
{
  "adapter_name": "rcai_arduino_serial",
  "transport": "serial",
  "supports_heartbeat": true,
  "supports_lap_sensors": true,
  "supports_pit_sensors": true,
  "supports_segment_sensors": false,
  "supports_relays": true,
  "supports_dynamic_pin_mapping": true,
  "max_lanes": null
}
```

`max_lanes = null` means no adapter-level fixed limit.

---

# 16. Configuration Contract

# 16.1 Adapter Configuration

Adapter configuration MAY include:
- adapter type
- transport type
- serial port
- baud rate
- heartbeat interval
- protocol variant
- timeout values

---

# 16.2 Infrastructure Configuration

Infrastructure configuration SHALL define:
- lanes
- sensors
- relays
- mappings
- pin assignments
- external outputs

---

# 16.3 No Hardcoded Lane Count

Adapters SHALL NOT hardcode:
- lane count
- vehicle count
- heat count
- race structure

---

# 17. Error Handling

# 17.1 Error Categories

Adapters SHOULD distinguish:

| Error Type | Description |
|---|---|
| Configuration Error | Invalid adapter setup |
| Transport Error | Serial/network failure |
| Protocol Error | Invalid protocol exchange |
| Timing Error | Missed emission deadline |
| Mapping Error | Missing sensor/relay mapping |
| Fatal Error | Adapter cannot continue |

---

# 17.2 Error Isolation

Adapter errors MUST NOT corrupt:
- deterministic scheduler state
- runtime entities
- vehicle profiles
- infrastructure persistence

---

# 17.3 Recovery

Adapters MAY support:
- reconnect
- reinitialize
- resume
- degraded mode

Recovery behavior MUST be explicit per adapter.

---

# 18. Adapter Independence

The Hardware Adapter layer MUST remain independently usable.

It must support:

- RMS protocol testing
- firmware validation
- hardware integration testing
- RC AI compatibility testing

without requiring:
- vehicle profiles
- simulation runtime
- race orchestrator

---

# 19. Testing Requirements

Each adapter SHOULD support tests for:

- lifecycle transitions
- configuration validation
- sensor mapping
- relay mapping
- heartbeat behavior
- protocol message generation
- failure isolation
- deterministic event ordering preservation

---

# 20. Initial Adapter: RC AI Arduino Serial

# 20.1 Scope

The first adapter SHALL emulate an Arduino-compatible serial controller compatible with RC AI.

---

# 20.2 Required Behavior

The adapter SHALL support:
- RC AI Arduino serial protocol
- heartbeat behavior
- digital input simulation
- relay output behavior
- dynamic lane mappings
- dynamic sensor mappings

---

# 20.3 Boundary Rule

Even for the RC AI Arduino adapter, the adapter SHALL NOT depend on:
- RC AI database
- RC AI internal state
- RC AI race model

It communicates only through the expected hardware protocol.

---

# 21. Future Adapter Support

Future adapters MAY include:
- PIC controller adapter
- ESP32 bridge adapter
- TCP adapter
- USB HID adapter
- CAN bus adapter
- OXIGEN bridge adapter

The runtime and scheduler MUST remain unchanged when adapters are replaced.

---

# 22. Final Architectural Statement

The Hardware Adapter is fundamentally:

```text
A protocol-specific hardware behavior translator
```

It is NOT:
- a simulator runtime
- a race manager
- a vehicle model
- an RMS plugin

Its responsibility is to make abstract simulation events appear to the RMS as valid physical hardware signals.
