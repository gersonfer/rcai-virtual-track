# Behavioral Specification: Virtual Track Coasting (TASK-009)

## 1. Concept Definition
In physical slot car racing, a vehicle does not stop instantly when track power is cut (Relay OFF). Instead, the vehicle's kinetic energy carries it forward for a brief period. This is known as "coasting." In the Virtual Track, simulating coasting is essential for realistic race pauses, finishes, and lap timing.

## 2. State Transitions
The introduction of Coasting expands the `VehicleState` enum and creates the following transition matrix:

- **`POWERED` → `COASTING`**: Triggered immediately when track power drops (`is_lane_powered() == False`).
- **`COASTING` → `STOPPED`**: Triggered when the vehicle's simulated momentum runs out (e.g., after a predefined `coasting_duration` of 0.5s to 1.0s).
- **`COASTING` → `POWERED`**: Triggered if track power is restored *before* the coasting duration expires. The vehicle regains speed without ever coming to a full halt.
- **`STOPPED` → `POWERED`**: Triggered when power is restored after the vehicle has completely stopped.

## 3. Lap Completion Rules
When a vehicle enters the `COASTING` state, its elapsed lap progress must be compared against the generated total `lap_time`.

- **Successful Coasting Finish**: If the remaining time to complete the lap is **less than or equal to** the `coasting_duration`, the vehicle's momentum successfully carries it over the sensor. The lap is completed, the sensor pulse is emitted, and the lap is registered *despite power being OFF*.
- **Failed Coasting Finish**: If the remaining time is **greater than** the `coasting_duration`, the vehicle stops short of the finish line. No sensor pulse is emitted, and the vehicle enters the `STOPPED` state.

## 4. Interaction with Power Loss
Power loss is the sole trigger for the `COASTING` state. Unlike the implementation in TASK-008 (which discarded the lap immediately upon power loss), the runtime must now smoothly bleed off time/distance during the power loss event to see if the finish line is reached.

## 5. Interaction with Pause/Resume
- **Pause (Heat Suspended)**: Relays go OFF. Vehicles enter `COASTING`. Some vehicles might cross the line while coasting. The rest come to a `STOPPED` state on the track.
- **Resume (Heat Restarted)**: Relays go ON. Because physical slot cars stay on the track where they stopped, the virtual track must now **resume the discarded lap**. The runtime must calculate the remaining lap time (Total Lap Time - Elapsed Powered Time - Coasting Distance Traveled) and resume waiting for that remaining duration. This is a deliberate behavioral shift from TASK-008, where paused laps were completely wiped.

## 6. Interaction with Future Deslot Logic
- **Deslot Preemption**: If a vehicle deslots (`deslotted == True` on the current lap generation) and the deslot event occurs *before* power is lost, the vehicle enters `DESLOTTED` immediately. Coasting physics do not apply to crashed cars.
- **Coasting Safety**: Vehicles cannot trigger a new deslot event while in the `COASTING` state. Because speed is rapidly decreasing, cornering forces drop, effectively nullifying the probability of a deslot during the coasting phase.
