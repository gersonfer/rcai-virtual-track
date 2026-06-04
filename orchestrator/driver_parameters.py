# orchestrator/driver_parameters.py

from dataclasses import dataclass

@dataclass(frozen=True)
class DriverParameters:

    avg_lap: float
    variation: float
    min_lap: float
    max_lap: float

    consistency: float
    aggression: float
    
    deslot_probability: float
    recovery_time: float
