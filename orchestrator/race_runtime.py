# orchestrator/race_runtime.py

import threading
import time

from orchestrator.lap_generator import (
    LapGenerator,
)

# ============================================================
# RACE RUNTIME
# ============================================================

class RaceRuntime:

    def __init__(
        self,
        emulator,
        profile_manager,
        lane_assignment_manager,
        track_config,
    ):

        self.emulator = emulator

        self.profile_manager = profile_manager

        self.lane_assignment_manager = (
            lane_assignment_manager
        )

        self.track_config = track_config

        self.running = False

        self.threads = []

    # ========================================================

    def start(self):

        if self.running:

            print(
                "[RACE_RUNTIME] "
                "Already running"
            )

            return

        print(
            "[RACE_RUNTIME] "
            "Starting runtime"
        )

        self.running = True

        for lane in self.track_config["lanes"]:

            thread = threading.Thread(
                target=self.lane_loop,
                args=(lane,),
                daemon=True,
            )

            thread.start()

            self.threads.append(thread)

    # ========================================================

    def stop(self):

        print(
            "[RACE_RUNTIME] "
            "Stopping runtime"
        )

        self.running = False

    # ========================================================

    def lane_loop(
        self,
        lane,
    ):

        lane_id = lane["lane_id"]

        sensor_pin = lane["sensor_pin"]

        relay_pin = lane["relay_pin"]

        print(
            f"[LANE {lane_id}] "
            f"Runtime started"
        )

        while self.running:

            # ------------------------------------------------
            # GET ASSIGNED PROFILE
            # ------------------------------------------------

            profile_id = (
                self.lane_assignment_manager
                .get_profile_for_lane(
                    lane_id
                )
            )

            # ------------------------------------------------
            # EMPTY LANE
            # ------------------------------------------------

            if profile_id is None:

                time.sleep(1)

                continue

            # ------------------------------------------------
            # LOAD PROFILE
            # ------------------------------------------------

            profile = (
                self.profile_manager
                .get_profile(
                    profile_id
                )
            )

            if profile is None:

                print(
                    f"[LANE {lane_id}] "
                    f"Profile not found: "
                    f"{profile_id}"
                )

                time.sleep(1)

                continue

            # ------------------------------------------------
            # CHECK RELAY POWER
            # ------------------------------------------------

            powered = self.emulator.is_lane_powered(
                relay_pin
            )

            if powered is False:

                print(
                    f"[LANE {lane_id}] "
                    f"POWER OFF"
                )

                time.sleep(0.1)

                continue

            # ------------------------------------------------
            # GENERATE LAP
            # ------------------------------------------------

            generator = LapGenerator(
                profile
            )

            result = (
                generator.generate_lap()
            )

            lap_time = result.lap_time

            deslotted = result.deslotted

            recovery = (
                result.recovery_time
            )

            car_name = profile["name"]

            # ------------------------------------------------
            # WAIT LAP TIME
            # ------------------------------------------------

            time.sleep(lap_time)

            # ------------------------------------------------
            # DESLOT
            # ------------------------------------------------

            if deslotted:

                print(
                    f"[LANE {lane_id}] "
                    f"{car_name} "
                    f"DESLOT "
                    f"(recovery={recovery:.2f}s)"
                )

            # ------------------------------------------------
            # SENSOR EVENT
            # ------------------------------------------------

            print(
                f"[LANE {lane_id}] "
                f"LAP "
                f"{car_name} "
                f"{lap_time:.3f}s"
            )

            self.emulator.pulse_sensor(
                pin=sensor_pin,
                pulse_ms=30,
            )

    # ========================================================

    def dump_assignments(self):

        self.lane_assignment_manager.dump()

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    print(
        "RaceRuntime must be started "
        "from main.py"
    )
