# track_interface/serial_protocol.py

from dataclasses import dataclass
from typing import Optional

# ============================================================
# CONSTANTS
# ============================================================

TERMINATOR = 0x3B  # ';'

# ============================================================
# OPCODES
# ============================================================

OPCODE_VERSION = 0x56      # 'V'
OPCODE_HEARTBEAT = 0x54    # 'T'
OPCODE_INPUT = 0x49        # 'I'

# ============================================================
# PIN TYPES
# ============================================================

DIGITAL = 0x44             # 'D'
ANALOG = 0x41              # 'A'

# ============================================================
# COMMANDS RECEIVED FROM RC AI
# ============================================================

RESET_COMMAND = bytearray([
    0x52,  # R
    0x45,  # E
    0x53,  # S
    0x45,  # E
    0x54,  # T
])

TIME_RESET_COMMAND = bytearray([
    0x54,  # T
])

# ============================================================
# MESSAGE TYPES
# ============================================================

MESSAGE_RESET = "RESET"
MESSAGE_TIME_RESET = "TIME_RESET"
MESSAGE_UNKNOWN = "UNKNOWN"

# ============================================================
# PARSED MESSAGE
# ============================================================

@dataclass
class ParsedCommand:
    message_type: str
    raw_payload: bytes

# ============================================================
# BUILDERS
# ============================================================

def build_version(
    major: int = 2,
    minor: int = 1,
    patch: int = 0,
    build: int = 1,
) -> bytes:

    return bytes([
        OPCODE_VERSION,
        major & 0xFF,
        minor & 0xFF,
        patch & 0xFF,
        build & 0xFF,
        TERMINATOR,
    ])

# ============================================================

def build_heartbeat(
    delta_us: int,
    reset_flag: int,
) -> bytes:

    return bytes([
        OPCODE_HEARTBEAT,
        (delta_us >> 24) & 0xFF,
        (delta_us >> 16) & 0xFF,
        (delta_us >> 8) & 0xFF,
        delta_us & 0xFF,
        reset_flag & 0xFF,
        TERMINATOR,
    ])

# ============================================================

def build_input_on(
    pin: int,
    is_digital: bool = True,
) -> bytes:

    pin_type = DIGITAL if is_digital else ANALOG

    return bytes([
        OPCODE_INPUT,
        pin_type,
        pin & 0xFF,
        1,
        TERMINATOR,
    ])

# ============================================================

def build_input_off(
    pin: int,
    is_digital: bool = True,
) -> bytes:

    pin_type = DIGITAL if is_digital else ANALOG

    return bytes([
        OPCODE_INPUT,
        pin_type,
        pin & 0xFF,
        0,
        TERMINATOR,
    ])

# ============================================================
# PARSER
# ============================================================

def parse_command(
    payload: bytes,
) -> ParsedCommand:

    buffer = bytearray(payload)

    # Remove terminator if present
    if len(buffer) > 0 and buffer[-1] == TERMINATOR:
        buffer = buffer[:-1]

    # RESET;
    if buffer == RESET_COMMAND:

        return ParsedCommand(
            message_type=MESSAGE_RESET,
            raw_payload=payload,
        )

    # T;
    if buffer == TIME_RESET_COMMAND:

        return ParsedCommand(
            message_type=MESSAGE_TIME_RESET,
            raw_payload=payload,
        )

    return ParsedCommand(
        message_type=MESSAGE_UNKNOWN,
        raw_payload=payload,
    )

# ============================================================
# HELPERS
# ============================================================

def bytes_to_hex(
    data: bytes,
) -> str:

    return " ".join(
        f"0x{x:02X}"
        for x in data
    )

# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    version = build_version()

    print("VERSION")
    print(bytes_to_hex(version))

    heartbeat = build_heartbeat(
        delta_us=500000,
        reset_flag=1,
    )

    print("\nHEARTBEAT")
    print(bytes_to_hex(heartbeat))

    sensor_on = build_input_on(pin=2)

    print("\nINPUT ON")
    print(bytes_to_hex(sensor_on))

    sensor_off = build_input_off(pin=2)

    print("\nINPUT OFF")
    print(bytes_to_hex(sensor_off))

    parsed = parse_command(
        b"RESET;"
    )

    print("\nPARSED")
    print(parsed)
