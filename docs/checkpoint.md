# Project Checkpoint

Version: 1.1

---

# Current Status

Current Phase:
- Phase 1 — Hardware Adapter Emulator

Current Task:
- TASK-002 — Hardware Transport Layer

Status:
- READY_FOR_NEXT_TASK

---

# Completed Tasks

| Task | Status | Notes |
|---|---|---|
| TASK-000 | DONE | Repository normalization completed |
| TASK-001 | DONE | RC AI protocol parser |

---

# In Progress Tasks

| Task | Status | Notes |
|---|---|---|

---

# Pending Tasks

| Task | Status |
|---|---|
| TASK-002 | PENDING |
| TASK-003 | PENDING |

---

# Architectural Decisions

## AD-001

The simulator communicates with RC AI exclusively through hardware protocol emulation.

Direct RMS integration is forbidden.

---

## AD-002

The runtime scheduler is deterministic and single-authoritative.

---

## AD-003

Repository structure is part of the architecture.

---

## AD-004

docs/checkpoint.md is the authoritative operational project state document.

---

## AD-005

No undocumented files may be added outside the defined repository structure.

---

# Validation History

| Task | Automated | Manual | Result |
|---|---|---|---|
| TASK-000 | PASS | PASS | APPROVED |
| TASK-001 | PASS | PASS | APPROVED |

---

# Manual Homologation History

## TASK-001 — Binary Frame Parser

- **Objective**: Validate the byte-by-byte deterministic decoding of RC AI protocol frames.
- **Execution command**: `python3 -B tools/manual_homologation.py`
- **Validation procedure**:
  The operator must execute the homologation artifact. The script feeds pre-defined raw hexadecimal byte arrays directly into the parser and prints the decoded output. The operator must manually verify that the output exactly matches the expected dataclass structures for the following scenarios:
  1. **Heartbeat frame parsing**: Input `5401020304003b`. Verifies exact extraction of `delta_us` and `reset_flags`.
  2. **Invalid terminator rejection**: Input `5602010000ff`. Verifies that frames ending in anything other than `0x3B` are explicitly rejected as `MalformedFrame`.
  3. **Sync recovery**: Input `ffaa540000000a003b`. Verifies that the parser correctly discards garbage bytes (`ffaa`) and successfully locks onto the subsequent valid Heartbeat frame.
  4. **Analog frame parsing**: Input `410100000001f43b`. Verifies correct parsing of variable-length analog sensor arrays based on the embedded count parameter.
- **Expected behavior**: All four test scenarios successfully print matching "Expected" and "Result" strings. No exceptions, stack traces, or silent failures are emitted.
- **Failure conditions**: The parser crashes on unexpected bytes, incorrectly splits payload bytes containing `0x3B`, or drops valid frames following a malformed sequence.
- **Final result**: APPROVED
- **Observed issues**: None.

---

# Known Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Unbounded parsing buffer | Potential memory leak on serial desync | Implement buffer limits at transport integration |
| Path Injection Drifts | Test tools rely on sys.path injection | Centralize execution tools via uv/pyproject.toml scripts |

---

# Current Repository Structure

```text
rcai-virtual-track/
├── .gitignore
├── README.md
├── architectural.md
├── pyproject.toml
├── spec.md
├── docs/
│   ├── checkpoint.md
│   ├── deterministic_scheduler.md
│   ├── event_bus.md
│   ├── execution_plan.md
│   ├── hardware_adapter_contract.md
│   ├── protocol_spec_rcai_arduino.md
│   ├── rcai_arduino_wire_protocol.md
│   └── runtime_execution_model.md
├── fixtures/
├── scripts/
│   └── run_tests.py
├── src/
│   └── adapters/
│       └── protocol/
│           ├── constants.py
│           ├── messages.py
│           └── parser.py
├── tests/
│   └── adapters/
│       └── protocol/
│           └── test_parser.py
└── tools/
    └── manual_homologation.py
```

---

# Next Recommended Task

TASK-002 — Hardware Transport Layer