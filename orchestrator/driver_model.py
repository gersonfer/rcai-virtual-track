# orchestrator/driver_model.py

import random
from dataclasses import dataclass

from orchestrator.lap_generator import LapGenerator
from orchestrator.driver_parameters import DriverParameters

# ============================================================
# LAP RESULT
# ============================================================

@dataclass
class LapResult:

    lap_time: float

    deslotted: bool

    recovery_time: float

# ============================================================
# DRIVER MODEL
# ============================================================

class DriverModel:

    def __init__(self):

        self.params: DriverParameters = None
        self.lap_generator = LapGenerator()

    def set_parameters(
        self,
        params: DriverParameters,
    ):

        self.params = params

    # ========================================================

    def generate_lap(self) -> LapResult:

        avg_lap = self.params.avg_lap
        variation = self.params.variation
        min_lap = self.params.min_lap
        max_lap = self.params.max_lap
        deslot_probability = self.params.deslot_probability
        recovery_time_avg = self.params.recovery_time

        # ----------------------------------------------------
        # BASE LAP GENERATION
        # ----------------------------------------------------

        lap_time = self.lap_generator.generate_base_time(
            avg_lap=avg_lap,
            variation=variation,
            min_lap=min_lap,
            max_lap=max_lap,
        )

        # ----------------------------------------------------
        # DESLOT SIMULATION
        # ----------------------------------------------------

        deslotted = False

        recovery_time = 0.0

        if random.random() < deslot_probability:

            deslotted = True

            recovery_time = random.uniform(
                recovery_time_avg * 0.5,
                recovery_time_avg * 1.5,
            )

            lap_time += recovery_time

        # ----------------------------------------------------

        return LapResult(
            lap_time=lap_time,
            deslotted=deslotted,
            recovery_time=recovery_time,
        )

    # ========================================================

    def generate_reaction_time(self) -> float:

        if not self.params:
            return 0.25

        reaction_time = self.params.reaction_time

        return random.uniform(
            reaction_time * 0.9,
            reaction_time * 1.5,
        )

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    example_params = DriverParameters(
        avg_lap=4.2,
        variation=0.12,
        min_lap=4.0,
        max_lap=4.8,
        consistency=0.93,
        aggression=0.70,
        deslot_probability=0.03,
        recovery_time=2.0,
    )

    driver = DriverModel()
    driver.set_parameters(example_params)

    for i in range(20):

        result = driver.generate_lap()

        print(
            f"LAP {i+1:02d} | "
            f"time={result.lap_time:.3f}s | "
            f"deslot={result.deslotted} | "
            f"recovery={result.recovery_time:.2f}s"
        )

