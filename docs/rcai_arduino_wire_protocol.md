# rcai_arduino_wire_protocol.md

# RC AI Arduino Wire Protocol Specification

Version: 1.0  
Status: Reverse Engineered Specification

Derived from:
- ArduinoProtocol.java
- racecoordinatorai_sketch.ino
- README.md

---

# 1. Protocol Nature

The protocol is hardware-oriented.

It transports:
- pin transitions
- timing deltas
- relay states
- analog values
- hardware events

It does NOT transport:
- laps
- standings
- drivers
- race semantics

The RMS reconstructs race behavior from hardware signals.

---

# 2. Transport

| Parameter | Value |
|---|---|
| Transport | Serial UART |
| Baud Rate | 115200 |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |

---

# 3. Framing

All frames terminate with:

| Hex | ASCII |
|---|---|
| 0x3B | ; |

The protocol uses opcode-driven framing.

There is:
- no generic length field
- no checksum
- no CRC

---

# 4. HEARTBEAT Message

Opcode:

| Hex | ASCII |
|---|---|
| 0x54 | T |

Frame:

| Field | Size |
|---|---|
| opcode | 1 byte |
| delta_us | 4 bytes |
| reset_flags | 1 byte |
| terminator | 1 byte |

Total:
7 bytes

Encoding:

54 TT TT TT TT RR 3B

Example:

54 01 02 03 04 00 3B

Timing value is encoded MSB → LSB.

Heartbeat frequency:
~1 second.

RMS timeout:
~2000ms.

---

# 5. VERSION Message

Opcode:

| Hex | ASCII |
|---|---|
| 0x56 | V |

Frame:

56 major minor patch build 3B

Example:

56 02 01 00 00 3B

Meaning:

Version 2.1.0.0

---

# 6. INPUT Message

Opcode:

| Hex | ASCII |
|---|---|
| 0x49 | I |

Frame:

49 type pin state 3B

Pin types:

| Value | Meaning |
|---|---|
| 0x44 | Digital |
| 0x41 | Analog |

States:

| Value | Meaning |
|---|---|
| 0x00 | LOW |
| 0x01 | HIGH |

Example:

49 44 02 01 3B

Meaning:
Digital pin D2 HIGH.

This message represents an electrical transition event.

It does NOT represent a lap event.

---

# 7. ANALOG DATA Message

Opcode:

| Hex | ASCII |
|---|---|
| 0x41 | A |

Frame:

41 count [pin value32]* 3B

Each analog entry:

| Field | Size |
|---|---|
| pin | 1 byte |
| value | 4 bytes |

Example:

41 02
00 00 00 01 F4
01 00 00 02 BC
3B

Meaning:
A0 = 500
A1 = 700

Analog polling interval:
~10ms.

---

# 8. RESET Command

Encoding:

52 45 53 45 54 3B

ASCII:

R E S E T ;

Behavior:
Forces firmware reboot.

---

# 9. VERSION Request

Encoding:

56 3B

ASCII:

V ;

Behavior:
Arduino replies with VERSION frame.

---

# 10. TIME RESET Command

Encoding:

54 3B

ASCII:

T ;

Behavior:
Requests timing synchronization reset.

---

# 11. PIN MODE READ

Encoding:

50 49 NN [TYPE PIN]... 3B

ASCII:

P I

Example:

50 49 02 44 02 44 03 3B

Meaning:
Configure D2 and D3 as input pins.

Configured mode:
INPUT_PULLUP.

---

# 12. PIN MODE WRITE

Encoding:

50 4F NN [TYPE PIN]... 3B

ASCII:

P O

Example:

50 4F 01 44 0A 3B

Meaning:
Configure D10 as output.

---

# 13. ANALOG PIN MODE

Encoding:

70 NN [TYPE PIN]... 3B

ASCII:

p

Meaning:
Configure analog acquisition pins.

---

# 14. WRITE DIGITAL PIN

Encoding:

4F 44 pin state 3B

ASCII:

O D

Example:

4F 44 0A 01 3B

Meaning:
Set D10 HIGH.

---

# 15. DEBOUNCE Command

Opcode:

| Hex | ASCII |
|---|---|
| 0x64 | d |

Encoding:

64 Hms Hus Lms Lus 3B

Formula:

high_us = (Hms * 1000) + (Hus * 4)

low_us = (Lms * 1000) + (Lus * 4)

Debounce belongs to the hardware layer.

---

# 16. Extended Protocol

Opcode:

| Hex | ASCII |
|---|---|
| 0x45 | E |

Sub-opcodes:

| Opcode | Meaning |
|---|---|
| 0 | Race State |
| 1 | Heat Leader |
| 2 | Heat Standings |
| 3 | Fuel Level |
| 4 | Refueling |
| 5 | Race Time |
| 6 | Deslot |
| 7 | Lap Performance |

---

# 17. Startup Sequence

Serial Open
↓
Arduino sends VERSION
↓
RMS validates firmware
↓
RMS sends PIN MODE READ
↓
RMS sends PIN MODE WRITE
↓
RMS sends ANALOG PIN MODE
↓
RMS sends DEBOUNCE
↓
RMS sends TIME RESET
↓
RUNNING

---

# 18. Protocol Semantics

The protocol is edge-triggered.

The firmware emits events only on pin transitions.

Virtual adapters must emulate:
- pulses
- transitions
- debounce behavior
- timing deltas

NOT:
- logical laps
- standings
- race events

---

# 19. Architectural Statement

The RC AI Arduino protocol fundamentally represents:

virtual electrical behavior

NOT:

virtual race semantics.
