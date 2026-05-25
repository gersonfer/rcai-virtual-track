# src/adapters/protocol/constants.py

import enum

FRAME_TERMINATOR = 0x3B  # ';'

class Opcode(enum.IntEnum):
    HEARTBEAT = 0x54  # 'T'
    VERSION = 0x56    # 'V'
    INPUT = 0x49      # 'I'
    ANALOG = 0x41     # 'A'
    RESET = 0x52      # 'R'
    EXTENDED = 0x45   # 'E'

class PinType(enum.IntEnum):
    DIGITAL = 0x44    # 'D'
    ANALOG = 0x41     # 'A'

class PinState(enum.IntEnum):
    LOW = 0x00
    HIGH = 0x01
