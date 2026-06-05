# orchestrator/physics_engine.py

from dataclasses import dataclass
from orchestrator.vehicle_physics import VehiclePhysics

# ============================================================
# CONSTANTS
# ============================================================

# Normalized calibration constants
BASE_TORQUE = 5000.0
PENALTY_MULTIPLIER = 0.005 # converts wheelspin deficit to seconds of delay

# ============================================================
# ACCELERATION RESULT
# ============================================================

@dataclass
class AccelerationResult:
    wheelspin: bool
    penalty_seconds: float
    traction_limit: float
    torque_demand: float

# ============================================================
# PHYSICS ENGINE
# ============================================================

class PhysicsEngine:
    
    def calculate_acceleration(self, physics: VehiclePhysics) -> AccelerationResult:
        
        # 1. Compute Traction Limit
        traction_limit = physics.grip_multiplier * (physics.mass_grams + physics.magnet_downforce_grams)
        
        # 2. Compute Torque Demand
        # Smaller tire = higher torque demand/launch force
        torque_demand = BASE_TORQUE / physics.rear_tire_diameter_mm
        
        # 3. Detect Wheelspin
        wheelspin = torque_demand > traction_limit
        
        penalty_seconds = 0.0
        
        if wheelspin:
            wheelspin_deficit = torque_demand - traction_limit
            penalty_seconds = wheelspin_deficit * PENALTY_MULTIPLIER
            
        return AccelerationResult(
            wheelspin=wheelspin,
            penalty_seconds=penalty_seconds,
            traction_limit=traction_limit,
            torque_demand=torque_demand
        )
