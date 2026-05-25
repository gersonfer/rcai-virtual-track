# tests/adapters/protocol/test_parser.py

from src.adapters.protocol.parser import BinaryFrameParser
from src.adapters.protocol.messages import (
    HeartbeatFrame,
    VersionFrame,
    InputFrame,
    AnalogFrame,
    AnalogEntry,
    MalformedFrame,
)
from src.adapters.protocol.constants import Opcode, PinType, PinState, FRAME_TERMINATOR

def test_heartbeat_parser():
    parser = BinaryFrameParser()
    # 54 01 02 03 04 00 3B
    data = bytes([Opcode.HEARTBEAT, 0x01, 0x02, 0x03, 0x04, 0x00, FRAME_TERMINATOR])
    frames = parser.feed(data)
    
    assert len(frames) == 1
    assert isinstance(frames[0], HeartbeatFrame)
    assert frames[0].delta_us == 0x01020304
    assert frames[0].reset_flags == 0x00

def test_version_parser():
    parser = BinaryFrameParser()
    # 56 02 01 00 00 3B (version 2.1.0.0)
    data = bytes([Opcode.VERSION, 0x02, 0x01, 0x00, 0x00, FRAME_TERMINATOR])
    frames = parser.feed(data)
    
    assert len(frames) == 1
    assert isinstance(frames[0], VersionFrame)
    assert frames[0].major == 2
    assert frames[0].minor == 1
    assert frames[0].patch == 0
    assert frames[0].build == 0

def test_input_parser():
    parser = BinaryFrameParser()
    # 49 44 02 01 3B (digital pin D2 HIGH)
    data = bytes([Opcode.INPUT, PinType.DIGITAL, 0x02, PinState.HIGH, FRAME_TERMINATOR])
    frames = parser.feed(data)
    
    assert len(frames) == 1
    assert isinstance(frames[0], InputFrame)
    assert frames[0].pin_type == PinType.DIGITAL
    assert frames[0].pin == 2
    assert frames[0].state == PinState.HIGH

def test_analog_parser():
    parser = BinaryFrameParser()
    # 41 02 (count) 00 00 00 01 F4 (A0=500) 01 00 00 02 BC (A1=700) 3B
    data = bytes([Opcode.ANALOG, 0x02, 
                  0x00, 0x00, 0x00, 0x01, 0xF4, 
                  0x01, 0x00, 0x00, 0x02, 0xBC, 
                  FRAME_TERMINATOR])
    frames = parser.feed(data)
    
    assert len(frames) == 1
    assert isinstance(frames[0], AnalogFrame)
    assert len(frames[0].entries) == 2
    assert frames[0].entries[0].pin == 0
    assert frames[0].entries[0].value == 500
    assert frames[0].entries[1].pin == 1
    assert frames[0].entries[1].value == 700

def test_malformed_terminator_rejection():
    parser = BinaryFrameParser()
    # Missing terminator (0x3B), instead ends with 0x00
    data = bytes([Opcode.INPUT, PinType.DIGITAL, 0x02, PinState.HIGH, 0x00])
    frames = parser.feed(data)
    
    assert len(frames) == 1
    assert isinstance(frames[0], MalformedFrame)
    assert b"Invalid terminator" in frames[0].reason.encode()

def test_incremental_parsing():
    parser = BinaryFrameParser()
    data = bytes([Opcode.HEARTBEAT, 0x00, 0x00, 0x00, 0x59, 0x00, FRAME_TERMINATOR])
    
    # Feed byte by byte
    frames = []
    for byte in data:
        frames.extend(parser.feed(bytes([byte])))
        
    assert len(frames) == 1
    assert isinstance(frames[0], HeartbeatFrame)
    assert frames[0].delta_us == 89

def test_garbage_recovery():
    parser = BinaryFrameParser()
    # Insert some random bytes, then a valid heartbeat
    garbage = bytes([0xFF, 0x00, 0x3B, 0x12])
    valid_frame = bytes([Opcode.HEARTBEAT, 0x00, 0x00, 0x00, 0x01, 0x00, FRAME_TERMINATOR])
    
    frames = parser.feed(garbage + valid_frame)
    
    assert len(frames) == 1
    assert isinstance(frames[0], HeartbeatFrame)
    assert frames[0].delta_us == 1
