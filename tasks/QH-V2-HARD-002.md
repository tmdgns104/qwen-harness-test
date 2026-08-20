# QH-V2-HARD-002 - Verification Contract Fail-Closed Hardening

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Architecture Basis

- ADR-001 - Deterministic Harness Core authority
- ADR-007 - Verification Performance Optimization
- ADR-010 - Post-Milestone 1 Hardening Priority
- QH-V2-HARD-001 - COMPLETE - VERIFIED

ADR-010 classification: REQUIRED-BEFORE-NEXT-MILESTONE.

## Problem

During QH-V2-CLI-001, nine Verification commands were intended, but only the first command followed an explicit Verification marker.

The existing parser silently ignored the remaining command-looking lines. As a result, `qh close` executed only one intended Verification command and still reported `Final Gate: PASS`.

The lifecycle change was reverted before completion. The Task contract was then corrected to use explicit repeated markers, after which all intended Verification commands were parsed and executed.

The Harness must not silently weaken an intended Verification contract.

## Goal

Harden `parse_verification_commands()` so obvious unmarked Verification commands fail closed instead of being silently ignored.

Add focused Harness Core and `qh close` regression Evidence.

Do not broaden Verification authority or redesign the Task markdown format.

## Existing Supported Syntax

Preserve these explicit markers:

- `Run exactly:`
- `Run:`
- `Then run:`

Each marker authorizes exactly one command represented as either:

- one standalone inline-code command; or
- one fenced block containing exactly one non-empty command line.

Existing command ordering semantics remain unchanged.

## Required Fail-Closed Behavior

### Unmarked standalone inline-code command

This must fail:

Run exactly:

`python first.py`

`python second.py`

The second command must not be silently ignored.

### Unmarked fenced command block

This must fail:

Run exactly:

`python first.py`

```text
python second.py
```

The unmarked fenced block must not be silently ignored.

### One marker, one command

One marker continues to authorize exactly one command. Additional standalone command-shaped code tokens require another supported marker.

## Prose Compatibility

Ordinary descriptive prose after a valid command remains allowed.

Example:

Run exactly:

`python check.py`

Then verify actual changed paths against scope.

The prose line is not executed and must not itself cause failure.

## Execution Safety

Parsing must complete successfully before any Verification command executes.

A malformed Verification contract must not partially execute an accepted prefix and then fail later.

`parse_verification_commands()` must either:

- return the complete valid `VerificationContract`; or
- raise before command execution begins.

## qh close Safety Regression

Add a focused regression proving that malformed Verification with an unmarked additional command:

1. makes `qh close` return non-zero;
2. leaves `STATUS.md` unchanged;
3. leaves the active Task markdown unchanged.

No production change to `tools/qh.py` is expected unless RED/GREEN Evidence proves it necessary.

## Existing Behavior To Preserve

- valid `Run exactly:` inline command;
- valid single-command fenced block;
- `Run:` + `Then run:` ordered commands;
- descriptive prose after valid command is ignored;
- missing Verification section fails;
- empty Verification section fails;
- marker without command fails;
- multi-command fenced block fails;
- malformed marker spacing fails closed;
- frozen `VerificationContract` behavior;
- existing qh lifecycle behavior.

## No Command Expansion

This Task does not add:

- shell authority;
- new Verification command types;
- command inference from prose;
- automatic Task repair;
- automatic Verification marker insertion;
- Task scaffold generation.

## Required Tests

At minimum verify:

1. one explicitly marked command remains valid;
2. multiple explicitly marked commands remain valid and ordered;
3. prose after a valid command remains allowed;
4. a second standalone inline-code command without a marker fails;
5. an unmarked fenced command block fails;
6. malformed contract raises before Verification execution;
7. `qh close` returns non-zero for malformed Verification;
8. `qh close` leaves `STATUS.md` unchanged;
9. `qh close` leaves the active Task markdown unchanged;
10. existing Harness Core Verification parser regression remains PASS;
11. existing qh regression remains PASS.

Tests must not require live Ollama.

## Implementation Preference

Prefer a small deterministic parser-state hardening inside the existing `parse_verification_commands()` implementation.

Do not replace it with a new parsing framework.

Do not duplicate Verification parsing in qh.

## Safety Boundary

- HC-004 remains the owner of approved Verification command execution.
- Final Gate authority remains unchanged.
- Worker authority remains unchanged.
- Retry policy remains unchanged.
- qh lifecycle authority remains unchanged.
- no model/backend changes;
- no automatic commit or Task completion.

## Allowed Changes

- `tools/harness_core.py`
- `tests/test_harness_core.py`
- `tests/test_qh.py`
- `STATUS.md`
- `tasks/QH-V2-HARD-002.md`

## Forbidden Changes

- `tools/qh.py`
- `tools/task_runner.py`
- `tests/test_task_runner.py`
- `tools/retry_runner.py`
- `tests/test_retry_runner.py`
- `tools/ollama_worker.py`
- `tests/test_ollama_worker.py`
- `tools/repo_tools.py`
- `tests/test_repo_tools.py`
- `DECISIONS.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- Repository fixture files
- other Task files
- unrelated files

## Acceptance Criteria

1. unmarked standalone Verification commands are not silently ignored;
2. unmarked fenced command blocks fail closed;
3. explicit multi-command marker syntax remains supported;
4. ordinary prose remains compatible;
5. malformed Verification fails before command execution;
6. malformed Verification cannot produce successful Task completion;
7. `qh close` malformed-contract regression preserves lifecycle files;
8. existing Harness Core tests remain PASS;
9. existing qh tests remain PASS;
10. no Architecture change occurs;
11. no forbidden file changes occur.

## Verification

Run exactly:

`python -m unittest tests.test_harness_core.VerificationCommandContractTests`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Conditions

STOP if implementation requires:

- changing Verification authority;
- changing Final Gate semantics;
- changing Worker or Retry behavior;
- modifying `tools/qh.py` production behavior;
- broad Markdown parser replacement;
- Architecture modification.

The next required Hardening item after this Task remains Duplicate `qh start` / Lifecycle Guard.

## Implementation Result

- `parse_verification_commands()` now rejects standalone inline-code tokens and
  backtick-fenced blocks that appear without a supported Verification marker.
- Supported markers, command ordering, single-command fenced blocks, and ordinary
  prose (including inline code inside a prose sentence) remain compatible.
- The `qh close` regression proves that malformed Verification is reported before
  an accepted prefix command can create a side effect.
- `STATUS.md` and the active Task markdown remain unchanged when that malformed
  contract is rejected.
- `tools/qh.py` and all other Forbidden Changes remain untouched.
- Three existing Git process-failure tests now inject `OSError` directly instead
  of relying on Windows `PATH` lookup behavior, preserving their fail-closed intent
  across environments.

## Verification Evidence

- Verification parser contract tests: 16 PASS.
- Malformed `qh close` focused regression: PASS.
- Existing Windows Git failure regressions: 3 PASS.
- `tests.test_qh`: 23 PASS.
- `tests.test_harness_core`: 117 PASS.
- `git diff --check`: PASS.
- Deterministic Task-range scope check: no unexpected changed paths.
- No live Ollama dependency was used.

## Conclusion

The implementation and required regressions are ready for the human-controlled
commit and `qh close` lifecycle steps. This Task remains ACTIVE until those steps
are performed; no next Task was started.
