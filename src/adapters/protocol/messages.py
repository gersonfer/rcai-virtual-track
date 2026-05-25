# src/adapters/protocol/messages.py
import dataclasses
from typing import List

@dataclasses.dataclass(frozen=True)
class HeartbeatFrame:
    delta_us: int
    reset_flags: int

@dataclasses.dataclass(frozen=True)
class VersionFrame:
    major: int
    minor: int
    patch: int
    build: int

@dataclasses.dataclass(frozen=True)
class InputFrame:
    pin_type: int
    pin: int
    state: int

@dataclasses.dataclass(frozen=True)
class AnalogEntry:
    pin: int
    value: int

@dataclasses.dataclass(frozen=True)
class AnalogFrame:
    entries: List[AnalogEntry]

@dataclasses.dataclass(frozen=True)
class MalformedFrame:
    reason: str
    raw_data: bytes
