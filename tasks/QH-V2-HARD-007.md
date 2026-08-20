# QH-V2-HARD-007 - Test Execution Integrity / Zero-Test Guard

## Status

PLANNED

## Problem

From Repository root, default unittest discovery currently finds zero tests while
explicit `python -m unittest discover -s tests` finds the real suite. In the audited
Python 3.13 environment zero discovery exits non-zero with `NO TESTS RAN`; other
tooling or a cursory report can still mistake a command that exercised no regression
tests for useful Evidence. The explicit suite also contains three known historical
QH-V2-MD-001 RED fixtures that must not be conflated with a new regression.

## Goal

Make Repository-root test discovery execute the real suite and add a deterministic
meta-regression that fails when representative tests become undiscoverable, without
changing Harness result semantics or repairing the historical RED fixture.

## Architecture Basis

- ADR-001 requires objective Test Evidence rather than Worker self-report.
- ADR-003 supports reusing verified resolutions and promoting repeated,
  error-prone procedures into deterministic utilities.
- ADR-007 makes full Verification authoritative and rejects stale or partial Evidence.
- The backlog-design audit measured default discovery count 0 and explicit discovery
  count 233; HARD-007 must recapture the then-current counts at its own baseline.
- This is audit-derived Hardening, not an ADR-010 classified item.

## Dependencies

- QH-V2-HARD-006 must be COMPLETE - VERIFIED in the deterministic queue.
- The implementation is technically independent of Windows scope matching but is
  sequenced after the trust-boundary Hardening set.
- Until committed Requirement/Accepted Decision updates and the Human-approved G1
  manifest cover this exact unchanged Task and queue blob identity, explicit Human
  approval is required before activation.

## Scope

- Make the `tests` tree discoverable from Repository root using standard unittest layout.
- Add a discovery-integrity test that inspects test names/count without executing the
  discovered suite or contacting Ollama.
- Require representative core modules and the historical markdown module to appear.
- Document the canonical regression commands and the known three QH-V2-MD-001 failures.
- Record before/after discovery counts as Evidence.

## Allowed Changes

- `tests/__init__.py`
- `tests/test_test_discovery.py`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-HARD-007.md`

## Forbidden Changes

- `tools/**`
- `tests/test_markdown_append.py`
- `docs/long_decisions.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. Standard unittest discovery from Repository root reports a discovered count greater
   than zero and includes the real `tests` suite.
2. Discovery includes representative modules for qh, Harness Core, Repository tools,
   Task Runner, and `test_markdown_append`.
3. Explicit `discover -s tests` continues to discover the suite.
4. The discovery-integrity meta-test passes without executing the discovered test
   cases and without live Ollama, network, Worker, or Repository mutation.
5. An unqualified discovery command can no longer exercise zero Repository tests.
6. The three historical QH-V2-MD-001 RED fixtures are excluded from GREEN claims and
   unchanged by Task-range Git Evidence. Any additional failure observed in an
   optional full discovery run is treated as a current regression and stops completion.
7. `tests/test_markdown_append.py` and `docs/long_decisions.md` are unchanged from the
   Task baseline.
8. No unittest-output string heuristic, Verification result reinterpretation, Python
   version pin, or Final Gate change is introduced.

## Verification

Run exactly:

`python -m unittest tests.test_test_discovery`

Then run:

`python -m unittest tests.test_qh tests.test_harness_core tests.test_repo_tools tests.test_task_runner tests.test_retry_runner tests.test_ollama_worker tests.test_qh_worker_run tests.test_text_utils tests.test_report_utils`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Before Evidence recaptures default and explicit discovery counts at the HARD-007
  Task baseline. The backlog-design counts 0 and 233 are historical context, not
  future expected constants, and do not claim that zero discovery returned `OK`.
- Focused GREEN records the meta-test count and exit 0.
- Test-name Evidence shows each required representative module is discoverable.
- Git diff from the Task baseline proves the two historical RED fixture files are unchanged.
- Known QH-V2-MD-001 failures are reported separately from current-Task regressions.
- The listed GREEN regression modules pass without live Ollama.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`, which reports no unexpected path,
  Diff Check 0, all contract commands exit 0, and Final Gate PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- fixing, deleting, skipping, or weakening the QH-V2-MD-001 RED fixture;
- interpreting generic unittest output inside Harness Core;
- changing Verification or Final Gate semantics;
- pinning Python, adding a dependency, or requiring live Ollama;
- production-code or Architecture changes.

## Next Task

Queue successor candidate: QH-V2-OPS-001.

Until committed Requirement/Accepted Decision updates and the Human-approved G1
manifest cover the exact unchanged queue and successor contract blob, Human approval
is required and the successor must not be auto-started.
