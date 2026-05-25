# src/adapters/protocol/parser.py
from typing import List, Optional, Union, Tuple
import struct
from .constants import Opcode, FRAME_TERMINATOR
from .messages import (
    HeartbeatFrame,
    VersionFrame,
    InputFrame,
    AnalogFrame,
    AnalogEntry,
    MalformedFrame,
)

ParsedFrame = Union[HeartbeatFrame, VersionFrame, InputFrame, AnalogFrame, MalformedFrame]

class BinaryFrameParser:
    def __init__(self):
        self._buffer = bytearray()

    def feed(self, data: bytes) -> List[ParsedFrame]:
        """
        Feeds bytes into the parser and returns any complete frames decoded.
        """
        self._buffer.extend(data)
        frames = []

        while True:
            # Drop bytes until we see a valid opcode
            if not self._sync_to_opcode():
                break
            
            frame, consumed = self._try_parse_frame()
            if frame is None:
                # Not enough data yet
                break
            
            # Remove consumed bytes
            self._buffer = self._buffer[consumed:]
            
            if frame:
                frames.append(frame)

        return frames

    def _sync_to_opcode(self) -> bool:
        """
        Drops bytes from the front of the buffer until a valid opcode is found.
        Returns True if a valid opcode is at the front, False if buffer is empty or no opcode found.
        """
        valid_opcodes = {Opcode.HEARTBEAT, Opcode.VERSION, Opcode.INPUT, Opcode.ANALOG}
        
        while self._buffer:
            if self._buffer[0] in valid_opcodes:
                return True
            # Discard unrecognized byte
            self._buffer.pop(0)
        return False

    def _try_parse_frame(self) -> Tuple[Optional[ParsedFrame], int]:
        """
        Attempts to parse a frame from the current buffer.
        Returns (Frame, consumed_bytes).
        If frame is incomplete, returns (None, 0).
        If frame is malformed (invalid terminator), returns (MalformedFrame, consumed_bytes).
        """
        if not self._buffer:
            return None, 0

        opcode = self._buffer[0]
        
        if opcode == Opcode.HEARTBEAT:
            return self._parse_heartbeat()
        elif opcode == Opcode.VERSION:
            return self._parse_version()
        elif opcode == Opcode.INPUT:
            return self._parse_input()
        elif opcode == Opcode.ANALOG:
            return self._parse_analog()
        else:
            # Should not happen if _sync_to_opcode works, but to be safe:
            self._buffer.pop(0)
            return None, 1

    def _parse_heartbeat(self) -> Tuple[Optional[ParsedFrame], int]:
        expected_len = 7
        if len(self._buffer) < expected_len:
            return None, 0
        
        frame_bytes = bytes(self._buffer[:expected_len])
        if frame_bytes[-1] != FRAME_TERMINATOR:
            return MalformedFrame("Invalid terminator for HEARTBEAT", frame_bytes), expected_len
            
        # 54 TT TT TT TT RR 3B
        delta_us, = struct.unpack('>I', frame_bytes[1:5])
        reset_flags = frame_bytes[5]
        
        return HeartbeatFrame(delta_us, reset_flags), expected_len

    def _parse_version(self) -> Tuple[Optional[ParsedFrame], int]:
        expected_len = 6
        if len(self._buffer) < expected_len:
            return None, 0
        
        frame_bytes = bytes(self._buffer[:expected_len])
        if frame_bytes[-1] != FRAME_TERMINATOR:
            return MalformedFrame("Invalid terminator for VERSION", frame_bytes), expected_len
            
        return VersionFrame(
            major=frame_bytes[1],
            minor=frame_bytes[2],
            patch=frame_bytes[3],
            build=frame_bytes[4]
        ), expected_len

    def _parse_input(self) -> Tuple[Optional[ParsedFrame], int]:
        expected_len = 5
        if len(self._buffer) < expected_len:
            return None, 0
            
        frame_bytes = bytes(self._buffer[:expected_len])
        if frame_bytes[-1] != FRAME_TERMINATOR:
            return MalformedFrame("Invalid terminator for INPUT", frame_bytes), expected_len
            
        return InputFrame(
            pin_type=frame_bytes[1],
            pin=frame_bytes[2],
            state=frame_bytes[3]
        ), expected_len

    def _parse_analog(self) -> Tuple[Optional[ParsedFrame], int]:
        # 41 count [pin value32]* 3B
        if len(self._buffer) < 2:
            return None, 0
            
        count = self._buffer[1]
        expected_len = 2 + (count * 5) + 1
        
        if len(self._buffer) < expected_len:
            return None, 0
            
        frame_bytes = bytes(self._buffer[:expected_len])
        if frame_bytes[-1] != FRAME_TERMINATOR:
            return MalformedFrame("Invalid terminator for ANALOG", frame_bytes), expected_len
            
        entries = []
        offset = 2
        for _ in range(count):
            pin = frame_bytes[offset]
            value, = struct.unpack('>I', frame_bytes[offset+1:offset+5])
            entries.append(AnalogEntry(pin, value))
            offset += 5
            
        return AnalogFrame(entries), expected_len
