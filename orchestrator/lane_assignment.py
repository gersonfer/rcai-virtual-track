# orchestrator/lane_assignment.py

from dataclasses import dataclass
from typing import Dict
from typing import Optional

# ============================================================
# LANE ASSIGNMENT
# ============================================================

@dataclass
class LaneAssignment:

    lane_id: int

    profile_id: Optional[str]

# ============================================================
# LANE ASSIGNMENT MANAGER
# ============================================================

class LaneAssignmentManager:

    def __init__(self):

        self._assignments: Dict[
            int,
            LaneAssignment
        ] = {}

    # ========================================================

    def assign_profile(
        self,
        lane_id: int,
        profile_id: str,
    ):

        self._assignments[lane_id] = LaneAssignment(
            lane_id=lane_id,
            profile_id=profile_id,
        )

        print(
            f"[LANE_ASSIGNMENT] "
            f"Lane {lane_id} -> "
            f"{profile_id}"
        )

    # ========================================================

    def clear_lane(
        self,
        lane_id: int,
    ):

        self._assignments[lane_id] = LaneAssignment(
            lane_id=lane_id,
            profile_id=None,
        )

        print(
            f"[LANE_ASSIGNMENT] "
            f"Lane {lane_id} cleared"
        )

    # ========================================================

    def get_profile_for_lane(
        self,
        lane_id: int,
    ) -> Optional[str]:

        assignment = self._assignments.get(
            lane_id
        )

        if assignment is None:
            return None

        return assignment.profile_id

    # ========================================================

    def get_all_assignments(self):

        return dict(
            self._assignments
        )

    # ========================================================

    def lane_has_car(
        self,
        lane_id: int,
    ) -> bool:

        profile_id = self.get_profile_for_lane(
            lane_id
        )

        return profile_id is not None

    # ========================================================

    def remove_profile(
        self,
        profile_id: str,
    ):

        for lane_id, assignment in list(
            self._assignments.items()
        ):

            if assignment.profile_id == profile_id:

                self.clear_lane(
                    lane_id
                )

    # ========================================================

    def dump(self):

        print(
            "========== LANE ASSIGNMENTS =========="
        )

        if not self._assignments:

            print("No assignments")

        for lane_id in sorted(
            self._assignments.keys()
        ):

            assignment = self._assignments[
                lane_id
            ]

            profile = (
                assignment.profile_id
                if assignment.profile_id
                else "EMPTY"
            )

            print(
                f"Lane {lane_id} -> "
                f"{profile}"
            )

        print(
            "======================================"
        )

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    manager = LaneAssignmentManager()

    manager.assign_profile(
        lane_id=1,
        profile_id="ferrari_499p",
    )

    manager.assign_profile(
        lane_id=2,
        profile_id="porsche_963",
    )

    manager.assign_profile(
        lane_id=3,
        profile_id="toyota_gr010",
    )

    manager.dump()

    print()

    print(
        manager.get_profile_for_lane(2)
    )

    print()

    manager.clear_lane(2)

    manager.dump()
