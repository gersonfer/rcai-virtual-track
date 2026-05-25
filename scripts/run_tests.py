import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tests.adapters.protocol.test_parser import (
    test_heartbeat_parser,
    test_version_parser,
    test_input_parser,
    test_analog_parser,
    test_malformed_terminator_rejection,
    test_incremental_parsing,
    test_garbage_recovery,
)

tests = [
    test_heartbeat_parser,
    test_version_parser,
    test_input_parser,
    test_analog_parser,
    test_malformed_terminator_rejection,
    test_incremental_parsing,
    test_garbage_recovery,
]

def run_all():
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASSED: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAILED: {test.__name__}")
            traceback.print_exc()
            failed += 1
            
    print(f"\nTotal: {passed + failed}, Passed: {passed}, Failed: {failed}")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all()
