# orchestrator/race_runtime.py

import threading
import time

from orchestrator.driver_model import (
    DriverModel,
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

        from orchestrator.vehicle_state import VehicleState
        current_state = None

        driver = DriverModel()
        pending_lap = None

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

            if not self.profile_manager.exists(profile_id):

                print(
                    f"[LANE {lane_id}] "
                    f"Profile not found: "
                    f"{profile_id}"
                )

                time.sleep(1)

                continue
            
            profile = self.profile_manager.get_profile(profile_id)
            params = self.profile_manager.get_driver_parameters(profile_id)

            driver.set_parameters(params)

            # ------------------------------------------------
            # CHECK RELAY POWER
            # ------------------------------------------------

            powered = self.emulator.is_lane_powered(
                relay_pin
            )

            if powered is False:

                if current_state != VehicleState.STOPPED:
                    print(f"[LANE {lane_id}] STATE -> STOPPED")
                    current_state = VehicleState.STOPPED

                time.sleep(0.1)

                continue

            was_stopped = (current_state == VehicleState.STOPPED or current_state is None)

            if current_state != VehicleState.POWERED:
                print(f"[LANE {lane_id}] STATE -> POWERED")
                current_state = VehicleState.POWERED

            # ------------------------------------------------
            # GENERATE OR RESUME LAP
            # ------------------------------------------------

            if pending_lap is not None:
                lap_time = pending_lap["lap_time"]
                original_time = pending_lap.get("original_time", lap_time)
                car_name = profile["name"]
                
                print(
                    f"[PARTIAL LAP RESUME]\n"
                    f"lane={lane_id}\n"
                    f"original={original_time:.3f}\n"
                    f"remaining={lap_time:.3f}"
                )
                
                # Flag to know if this lap was resumed so we can log PARTIAL LAP COMPLETE
                is_resumed_lap = True
                resumed_original_time = original_time
                
                if was_stopped:
                    reaction = driver.generate_reaction_time()
                    lap_time += reaction
                    resumed_original_time += reaction
                    print(f"[LANE {lane_id}] Reaction Time Applied: {reaction:.3f}s")
                
                pending_lap = None
            else:
                is_resumed_lap = False
                result = driver.generate_lap()
                lap_time = result.lap_time
                deslotted = result.deslotted
                recovery = result.recovery_time
                car_name = profile["name"]
                
                if was_stopped:
                    reaction = driver.generate_reaction_time()
                    lap_time += reaction
                    print(f"[LANE {lane_id}] Reaction Time Applied: {reaction:.3f}s")

                # ------------------------------------------------
                # DESLOT LOGGING (IMMEDIATE)
                # ------------------------------------------------
                if deslotted:
                    if current_state != VehicleState.DESLOTTED:
                        print(f"[LANE {lane_id}] STATE -> DESLOTTED")
                        current_state = VehicleState.DESLOTTED

                    print(
                        f"[LANE {lane_id}] "
                        f"{car_name} "
                        f"DESLOT "
                        f"(recovery={recovery:.2f}s)"
                    )

            # ------------------------------------------------
            # WAIT LAP TIME (INTERRUPTIBLE / COASTING)
            # ------------------------------------------------

            start_time = time.monotonic()
            coasting_duration = self.track_config.get("coasting_duration", 0.5)
            lap_aborted = False

            while time.monotonic() - start_time < lap_time:
                
                time.sleep(0.05)
                
                if not self.emulator.is_lane_powered(relay_pin):
                    
                    if current_state != VehicleState.COASTING:
                        print(f"[LANE {lane_id}] STATE -> COASTING (Power Lost)")
                        current_state = VehicleState.COASTING
                        
                        elapsed = time.monotonic() - start_time
                        remaining = lap_time - elapsed
                        print(
                            f"[COASTING]\n"
                            f"lane={lane_id}\n"
                            f"lap_time={lap_time:.3f}\n"
                            f"elapsed={elapsed:.3f}\n"
                            f"remaining={remaining:.3f}\n"
                            f"coasting_duration={coasting_duration:.3f}"
                        )
                        
                    coasting_start = time.monotonic()
                    
                    while True:
                        elapsed_coasting = time.monotonic() - coasting_start
                        elapsed_lap = time.monotonic() - start_time
                        
                        if elapsed_lap >= lap_time:
                            # Momentum carried vehicle over the finish line
                            print("[COASTING RESULT] LAP_COMPLETED")
                            break
                            
                        if elapsed_coasting >= coasting_duration:
                            # Ran out of momentum
                            print("[COASTING RESULT] MOMENTUM_LOST")
                            lap_aborted = True
                            
                            # Persist partial lap
                            remaining_time = lap_time - elapsed_lap
                            if remaining_time > 0:
                                
                                # Track original time for telemetry
                                original = pending_lap["original_time"] if (pending_lap and "original_time" in pending_lap) else lap_time
                                
                                pending_lap = {
                                    "lap_time": remaining_time,
                                    "original_time": original
                                }
                                
                                print(
                                    f"[PARTIAL LAP SAVE]\n"
                                    f"lane={lane_id}\n"
                                    f"original={original:.3f}\n"
                                    f"remaining={remaining_time:.3f}"
                                )
                            break
                            
                        if self.emulator.is_lane_powered(relay_pin):
                            print(f"[LANE {lane_id}] STATE -> POWERED (Power Restored)")
                            current_state = VehicleState.POWERED
                            break
                            
                        time.sleep(0.05)
                        
                    if lap_aborted:
                        break

            if lap_aborted:
                if current_state != VehicleState.STOPPED:
                    print(f"[LANE {lane_id}] STATE -> STOPPED (Momentum Lost)")
                    current_state = VehicleState.STOPPED
                continue

            # ------------------------------------------------
            # SENSOR EVENT
            # ------------------------------------------------

            final_logged_time = resumed_original_time if is_resumed_lap else lap_time

            if is_resumed_lap:
                print(
                    f"[PARTIAL LAP COMPLETE]\n"
                    f"lane={lane_id}\n"
                    f"original={resumed_original_time:.3f}\n"
                    f"published={final_logged_time:.3f}"
                )

            print(
                f"[LANE {lane_id}] "
                f"LAP "
                f"{car_name} "
                f"{final_logged_time:.3f}s"
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
