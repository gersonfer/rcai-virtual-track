# vehicle_profiles/profile_manager.py

import json
from pathlib import Path
from typing import Optional

# ============================================================
# PROFILE MANAGER
# ============================================================

class ProfileManager:

    def __init__(
        self,
        profiles_path: str,
    ):

        self.profiles_path = Path(
            profiles_path
        )

        self._profiles = {}

        self.load()

    # ========================================================

    def load(self):

        if not self.profiles_path.exists():

            raise FileNotFoundError(
                f"profiles.json not found: "
                f"{self.profiles_path}"
            )

        with open(
            self.profiles_path,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)

        self._profiles.clear()

        for profile in data.get("profiles", []):

            profile_id = profile["id"]

            self._profiles[profile_id] = profile

        print(
            f"[PROFILE_MANAGER] "
            f"Loaded "
            f"{len(self._profiles)} profiles"
        )

    # ========================================================

    def reload(self):

        self.load()

    # ========================================================

    def get_profile(
        self,
        profile_id: str,
    ) -> Optional[dict]:

        return self._profiles.get(
            profile_id
        )

    # ========================================================

    def get_all_profiles(self):

        return list(
            self._profiles.values()
        )

    # ========================================================

    def list_profile_ids(self):

        return list(
            self._profiles.keys()
        )

    # ========================================================

    def exists(
        self,
        profile_id: str,
    ) -> bool:

        return (
            profile_id in self._profiles
        )

    # ========================================================

    def get_avg_lap(
        self,
        profile_id: str,
    ) -> float:

        profile = self.require_profile(
            profile_id
        )

        return profile["performance"][
            "avg_lap"
        ]

    # ========================================================

    def get_variation(
        self,
        profile_id: str,
    ) -> float:

        profile = self.require_profile(
            profile_id
        )

        return profile["performance"][
            "variation"
        ]

    # ========================================================

    def get_deslot_probability(
        self,
        profile_id: str,
    ) -> float:

        profile = self.require_profile(
            profile_id
        )

        return profile["behavior"][
            "deslot_probability"
        ]

    # ========================================================

    def require_profile(
        self,
        profile_id: str,
    ) -> dict:

        profile = self.get_profile(
            profile_id
        )

        if profile is None:

            raise ValueError(
                f"Profile not found: "
                f"{profile_id}"
            )

        return profile

    # ========================================================

    def get_driver_parameters(
        self,
        profile_id: str,
    ):
        from orchestrator.driver_parameters import DriverParameters

        profile = self.require_profile(
            profile_id
        )

        perf = profile["performance"]
        beh = profile["behavior"]

        return DriverParameters(
            avg_lap=perf["avg_lap"],
            variation=perf["variation"],
            min_lap=perf["min_lap"],
            max_lap=perf["max_lap"],
            consistency=perf.get("consistency", 1.0),
            aggression=beh.get("aggression", 1.0),
            deslot_probability=beh["deslot_probability"],
            recovery_time=beh["recovery_time_avg"],
            reaction_time=beh.get("reaction_time", 0.250),
        )

    # ========================================================

    def get_vehicle_physics(
        self,
        profile_id: str,
    ):
        from orchestrator.vehicle_physics import VehiclePhysics

        profile = self.require_profile(
            profile_id
        )

        phys = profile.get("physics", {})

        return VehiclePhysics(
            scale=phys.get("scale", "1/32"),
            mass_grams=phys.get("mass_grams", 90.0),
            magnet_downforce_grams=phys.get("magnet_downforce_grams", 100.0),
            grip_multiplier=phys.get("grip_multiplier", 1.0),
            rear_tire_diameter_mm=phys.get("rear_tire_diameter_mm", 21.0),
        )

    # ========================================================

    def dump(self):

        print(
            "========== PROFILES =========="
        )

        for profile_id, profile in self._profiles.items():

            print(
                f"{profile_id}"
            )

            print(
                f"  Name: "
                f"{profile['name']}"
            )

            print(
                f"  Avg Lap: "
                f"{profile['performance']['avg_lap']}"
            )

            print(
                f"  Variation: "
                f"{profile['performance']['variation']}"
            )

            print(
                f"  Deslot: "
                f"{profile['behavior']['deslot_probability']}"
            )

            if "physics" in profile:
                print(
                    f"  Physics: "
                    f"{profile['physics']['mass_grams']}g, "
                    f"Scale {profile['physics']['scale']}"
                )

            print()

        print(
            "=============================="
        )

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    manager = ProfileManager(
        "profiles.json"
    )

    manager.dump()

    ferrari = manager.get_profile(
        "ferrari_499p"
    )

    print(
        "\nFERRARI PROFILE\n"
    )

    print(
        json.dumps(
            ferrari,
            indent=2,
        )
    )

    ferrari_physics = manager.get_vehicle_physics(
        "ferrari_499p"
    )

    print(
        "\nFERRARI PHYSICS\n"
    )

    print(
        ferrari_physics
    )
