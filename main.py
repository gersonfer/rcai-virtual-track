# main.py

import json
import time

from track_interface.arduino_emulator import (
    ArduinoEmulator,
)

from vehicle_profiles.profile_manager import (
    ProfileManager,
)

from orchestrator.lane_assignment import (
    LaneAssignmentManager,
)

from orchestrator.race_runtime import (
    RaceRuntime,
)

# ============================================================
# LOAD TRACK CONFIG
# ============================================================

with open(
    "config/track.json",
    "r",
    encoding="utf-8",
) as f:

    track_config = json.load(f)

# ============================================================
# LOAD VEHICLE PROFILES
# ============================================================

profile_manager = ProfileManager(
    "vehicle_profiles/profiles.json"
)

# ============================================================
# CREATE LANE ASSIGNMENTS
# ============================================================

lane_assignment = (
    LaneAssignmentManager()
)

# ============================================================
# CREATE TRACK INTERFACE
# ============================================================

emulator = ArduinoEmulator(
    port=track_config["serial"]["port"],
    baudrate=track_config["serial"]["baudrate"],
    lanes_config=track_config.get("lanes", []),
    relay_mode=track_config.get("relay_mode", "normally_open"),
)

# ============================================================
# INITIALIZE EMULATOR
# ============================================================

emulator.start()

# ============================================================
# INITIAL LANE ASSIGNMENTS
# ============================================================

# Example:
#
# Lane 1 -> Ferrari
# Lane 2 -> Porsche
# Lane 3 -> Empty
# Lane 4 -> Cadillac

lane_assignment.assign_profile(
    lane_id=1,
    profile_id="test_light_highmag",
)

lane_assignment.assign_profile(
    lane_id=2,
    profile_id="test_light_lowmag",
)

lane_assignment.assign_profile(
    lane_id=3,
    profile_id="test_heavy_normmag",
)

lane_assignment.assign_profile(
    lane_id=4,
    profile_id="test_heavy_nomag",
)

# ============================================================
# CREATE RACE RUNTIME
# ============================================================

runtime = RaceRuntime(
    emulator=emulator,
    profile_manager=profile_manager,
    lane_assignment_manager=lane_assignment,
    track_config=track_config,
)

# ============================================================
# START RUNTIME
# ============================================================

runtime.start()

# ============================================================
# MAIN LOOP
# ============================================================

print("")
print("========================================")
print("VIRTUAL SLOT PLATFORM")
print("========================================")
print("")

runtime.dump_assignments()

print("")
print("Running...")
print("CTRL+C to stop")
print("")

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    print("")
    print("Stopping system...")
    print("")

    runtime.stop()

    emulator.stop()

    print("Shutdown complete")
