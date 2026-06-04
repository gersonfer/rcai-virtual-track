# orchestrator/vehicle_state.py

from enum import Enum

class VehicleState(Enum):
    STOPPED = "STOPPED"
    POWERED = "POWERED"
    COASTING = "COASTING"
    DESLOTTED = "DESLOTTED"
