from dataclasses import dataclass

@dataclass(frozen=True)
class VehiclePhysics:
    scale: str
    mass_grams: float
    grip_multiplier: float
    magnet_downforce_grams: float
    rear_tire_diameter_mm: float
