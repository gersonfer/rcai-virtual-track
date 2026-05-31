# orchestrator/vehicle_state.py

from enum import Enum

class VehicleState(Enum):
    STOPPED = "STOPPED"
    POWERED = "POWERED"
    DESLOTTED = "DESLOTTED"
