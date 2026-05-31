# TODO

## 1. Simulation Improvements

### [ ] Immediate Power Loss Handling

Problem

The current simulation allows a vehicle to complete its current lap even after the lane relay has been switched OFF.

Current behavior:

text Relay OFF ↓ Vehicle continues current lap ↓ Lap is generated ↓ Vehicle stops on next loop iteration 

This behavior is acceptable for validating relay control but is not physically realistic.

Expected Behavior

text Relay OFF ↓ Vehicle immediately detects power loss ↓ Vehicle leaves POWERED state ↓ Vehicle enters COASTING or STOPPED state 

Technical Notes

Current implementation blocks inside:

python time.sleep(lap_time) 

A future implementation should allow the vehicle runtime to react to relay state changes immediately rather than only after lap completion.

RC AI

↓ Relay ON
↓ Throttle Enabled
↓ Car generates sensor passes
RC AI
↓ Relay OFF
↓ Throttle Disabled
↓ Car enters coasting
↓ profile data determines how much longer it can coast
↓ Car stops

Acceptance Criteria

- Vehicle detects relay OFF without waiting for lap completion.
- POWERED state is interrupted immediately.
- No artificial delay caused by lap simulation timing.


---

### [ ] Vehicle Coasting Model

Depends On

- Immediate Power Loss Handling

Problem

After relay power is removed, vehicles currently stop according to simulation timing rather than vehicle dynamics.

A dedicated post-power-loss model is required.

####  Physics-Based Coasting

text Relay OFF ↓ Vehicle decelerates according to speed, mass, grip, magnet strength ↓ Vehicle stops 

Most realistic 

Acceptance Criteria

- Vehicle behavior after power loss is deterministic.
- Selected coasting model is documented.
- Simulation remains reproducible for testing and homologation.

### [ ] Vehicle Starting Model

It defines how the vehicle starts when it is stopped.
This gets especially interesting at the starting light of the race.

Imagine:
5, 4, 3, 3, 1, GO!
RC AI powers the track.
The cars don't need to start exactly together.
We already have:
"aggression"
which could influence:
reaction time

Vehicle accelerate according to speed, mass, grip, magnet strength ↓ Vehicle start

example:
Ferrari:
Reaction time = formula
Toyota:
Reaction time = formula
Porsche:
Reaction time = formula

Architecturally, this means that RaceRuntime shouldn't think:
sleep(lap_time)
pulse_sensor()

But something closer to:
Driver
 ├─ throttle enabled?
 ├─ relay energized?
 ├─ coasting?
 ├─ deslotted?
 └─ actual spped, mass grip, magnet strength


## 2. Profile Manager

profile_manager.py

Perhaps create helpers:
get_consistency()
get_aggression()

## 3. Lap Generator

This is where the conceptual shift occurs.
Today:
generate_lap() returns 
4.22
4.31
4.18
I would rename it in the future to:
driver_model.py
The objective becomes:
generate pilot behavior
and not only that:
generate lap time

## 4. Race Run Time

race_runtime.py
This is the second file that changes the most.
Today:

while running:

    lap_time = generator.generate_lap()

    sleep(lap_time)

    pulse_sensor()


It becomes:

while running:

    if not lane_power:
        sleep(0.1)
        continue

    if race_state != RACING:
        sleep(0.1)
        continue

    lap_time = generator.generate_lap()

    sleep(lap_time)

    pulse_sensor()

I.e: 
The vehicle only moves when it receives energy.

## 5. Main

main.py

Small change.

Today:
runtime.start()
It all starts here.

Future:
runtime.start()
It only creates the threads.
But:
no vehicle moves until the RC AI energizes the lanes.


### SUMMARY

## Vehicle Simulation

- VehicleState
- DriverModel
- Immediate Power Loss
- Coasting
- Starting Model

## Runtime

- Remove blocking sleeps
- Event driven simulation

## Physics

- Mass
- Grip
- Magnet
- Acceleration





