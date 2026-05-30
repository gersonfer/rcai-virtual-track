# RCai Virtual Track

Virtual simulated racing platform ("Virtual Slot Platform") that connects vehicle profiles with data-emitting components via a serial interface, acting as an Arduino emulator.

The system manages track configurations, the assignment of vehicles to different lanes, detailed vehicle data and profiles, as well as the real-time execution of the race.

## 🚀 Features

- **Arduino Emulator:** Simulates the serial communication of physical hardware.
- **Vehicle Profiles Management:** Allows fetching, loading, and defining unique configurations for different cars (e.g., Ferrari 499P, Porsche 963, Cadillac V-Series.R).
- **Lane Assignment System:** Dynamically maps vehicles to the track lanes, avoiding conflicts.
- **Simulation Engine (Race Runtime):** Controls the lifecycle of the race and integrates all subsystems in real time.

## 📂 Project Structure

The project is organized into the following main modules:

- `config/` - Contains track configurations and serial ports (e.g., `track.json`).
- `orchestrator/` - Core logic, responsible for the simulation engine (`race_runtime.py`) and assigning vehicles to lanes (`lane_assignment.py`).
- `track_interface/` - Integrations and external communication, such as the hardware emulator (`arduino_emulator.py`).
- `vehicle_profiles/` - Module for managing car characteristics (`profile_manager.py` and `profiles.json`).
- `main.py` - Entry point and main script for initializing the platform.
- `discover_socat.py` - Utility script for virtual serial connections.
- `architectural.md` - Base documentation of the system's architecture.

## ⚙️ Prerequisites

- Python 3.8+
- [pySerial](https://pypi.org/project/pyserial/) (depending on the emulator communication implementation)
- [socat](http://www.dest-unreach.org/socat/) (required for creating virtual serial connections)
- Virtual environment (recommended to use the existing `venv/` folder).

## 🛠️ How to Run

1. **Activate the virtual environment (if applicable):**
   ```bash
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Configure Virtual Serial Ports:**
   Before running the main platform, execute the `discover_socat.py` script. It automatically manages `socat` to create virtual serial connections and updates your `config/track.json` with the correct port.
   ```bash
   python discover_socat.py
   ```

3. **Start the system:**
   ```bash
   python main.py
   ```

During execution, the project will assign the lanes, start the serial communications through the emulator, and maintain the continuous racing loop until the simulation is interrupted (`CTRL+C`).

## 📜 Architecture

To get an in-depth understanding of the operational flow, components, and extension points of the system, please refer to the detailed documentation in the [`architectural.md`](architectural.md) file.
