# orchestrator/lap_generator.py

import random

# ============================================================
# LAP GENERATOR
# ============================================================

class LapGenerator:

    def generate_base_time(
        self,
        avg_lap: float,
        variation: float,
        min_lap: float,
        max_lap: float,
    ) -> float:
        """
        Calculates a base lap time using gaussian distribution, 
        clamped to the provided bounds.
        """

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

        return lap_time
