TASK-005.1 — Protocol Reverse Engineering

Problem

The emulator generates lap pulses correctly, but RC AI does not count laps immediately after race start.

Observed behavior:

Race Start
→ emulator generates laps
→ RC AI counts 0 laps

Pause / Restart
→ RC AI starts counting laps

Result:
2 laps counted instead of ~15 laps in a 60s heat.

Race Start
→ emulator generates laps
→ RC AI counts 0 laps

Pause / Restart
→ RC AI starts counting laps

Result:
2 laps counted instead of ~15 laps in a 60s heat.

This indicates a possible protocol synchronization mismatch between:

RC AI Java
↔
Arduino Firmware
↔
Python Emulator

RC AI Java
↔
Arduino Firmware
↔
Python Emulator

Inputs

Mandatory analysis sources:

- docs/arduino-java-protocol.md (Explain the protocol)
- docs/ArduinoProtocol.java (Java integration classes)
- docs/racecoordinatorai_sketch.ino (Arduino firmware)
- Current Python emulator

Objectives

1. Reconstruct the protocol

Document:

* startup sequence
* reset sequence
* race start sequence
* lap detection sequence
* pause sequence
* restart sequence
* heat over sequence
* race over sequence

⸻

2. Build protocol state machine

Identify all states.

Example:

BOOT
↓
RESET
↓
READY
↓
POWERED
↓
RACING
↓
PAUSED
↓
RACING
↓
HEAT_OVER

(Example only.)

⸻

3. Explain all commands

For each command:

Sender
Receiver
Purpose
State changes
Expected response

Including currently unknown commands.

Example:

RESET;
T;
OD;
PID;
PO;
0x70;
0x64;

4. Compare real implementation versus emulator

Produce a gap analysis.

Example:

Real firmware:
...

Emulator:
...

Impact:
...

Suggested correction:
...

Deliverables

protocol_analysis.md

Technical protocol documentation.

⸻

protocol_walkthrough.md

Human-readable explanation of the complete protocol lifecycle.

⸻

protocol_gap_analysis.md

Differences between:

Real Arduino
vs
Current Emulator

Including proposed fixes.

⸻

Constraints

NO CODE CHANGES
NO COMMITS
NO IMPLEMENTATION

nalysis only.

⸻

Acceptance Criteria

The reviewer can understand:

RC AI
↓
Java
↓
Arduino
↓
Lap pulse
↓
RC AI lap counting

without reading the original source code.

All protocol states, commands, and transitions are documented.

All suspected causes for the lap-counting issue are identified and accompanied by proposed corrective actions.

- docs/protocol_analysis.md
- docs/protocol_walkthrough.md
- docs/protocol_gap_analysis.md

No code changes.
No commits.
Analysis only.