# orchestrator/lap_generator.py

import random
from dataclasses import dataclass

# ============================================================
# LAP RESULT
# ============================================================

@dataclass
class LapResult:

    lap_time: float

    deslotted: bool

    recovery_time: float

# ============================================================
# LAP GENERATOR
# ============================================================

class LapGenerator:

    def __init__(
        self,
        profile: dict,
    ):

        self.profile = profile

        self.performance = profile["performance"]

        self.behavior = profile["behavior"]

    # ========================================================

    def generate_lap(self) -> LapResult:

        avg_lap = self.performance[
            "avg_lap"
        ]

        variation = self.performance[
            "variation"
        ]

        min_lap = self.performance[
            "min_lap"
        ]

        max_lap = self.performance[
            "max_lap"
        ]

        deslot_probability = self.behavior[
            "deslot_probability"
        ]

        recovery_time_avg = self.behavior[
            "recovery_time_avg"
        ]

        # ----------------------------------------------------
        # BASE LAP GENERATION
        # ----------------------------------------------------

        lap_time = random.gauss(
            avg_lap,
            variation,
        )

        lap_time = max(
            min_lap,
            min(
                lap_time,
                max_lap,
            ),
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

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    example_profile = {
        "name": "Ferrari 499P",

        "performance": {
            "avg_lap": 4.2,
            "variation": 0.12,
            "min_lap": 4.0,
            "max_lap": 4.8,
        },

        "behavior": {
            "deslot_probability": 0.03,
            "recovery_time_avg": 2.0,
        },
    }

    generator = LapGenerator(
        example_profile
    )

    for i in range(20):

        result = generator.generate_lap()

        print(
            f"LAP {i+1:02d} | "
            f"time={result.lap_time:.3f}s | "
            f"deslot={result.deslotted} | "
            f"recovery={result.recovery_time:.2f}s"
        )
