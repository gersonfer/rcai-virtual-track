# manual_homologation.py

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapters.protocol.parser import BinaryFrameParser

def run_manual_homologation():
    print("--- Manual Homologation: TASK-001 Binary Frame Parser ---\n")
    
    parser = BinaryFrameParser()
    
    # Test 1: Deterministic decoding of Heartbeat Frame
    # 54 01 02 03 04 00 3B (Heartbeat with delta_us = 16909060, flags = 0)
    print("[Test 1] Deterministic decoding of Heartbeat Frame")
    print("Expected: HeartbeatFrame(delta_us=16909060, reset_flags=0)")
    data = bytes.fromhex("5401020304003b")
    frames = parser.feed(data)
    print(f"Result:   {frames[0]}\n")
    
    # Test 2: Invalid terminator rejection
    # 56 02 01 00 00 FF (Version frame but terminating with FF instead of 3B)
    print("[Test 2] Invalid terminator rejection")
    print("Expected: MalformedFrame(reason='Invalid terminator for VERSION', raw_data=...)")
    data = bytes.fromhex("5602010000ff")
    frames = parser.feed(data)
    print(f"Result:   {frames[0]}\n")
    
    # Test 3: Opcode validation (discarding invalid opcodes until sync)
    # FF AA 54 00 00 00 0A 00 3B (Garbage followed by Heartbeat 10us)
    print("[Test 3] Opcode validation and sync recovery")
    print("Expected: HeartbeatFrame(delta_us=10, reset_flags=0)")
    data = bytes.fromhex("ffaa540000000a003b")
    frames = parser.feed(data)
    print(f"Result:   {frames[0]}\n")

    # Test 4: Analog Data Frame Parsing
    # 41 01 00 00 00 01 F4 3B (Analog frame with 1 entry: A0 = 500)
    print("[Test 4] Analog Data Parsing")
    print("Expected: AnalogFrame(entries=[AnalogEntry(pin=0, value=500)])")
    data = bytes.fromhex("410100000001f43b")
    frames = parser.feed(data)
    print(f"Result:   {frames[0]}\n")

if __name__ == "__main__":
    run_manual_homologation()
