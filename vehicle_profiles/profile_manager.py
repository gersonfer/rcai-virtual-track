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
