# QH-V2-OPS-003 - Windows Workflow Simplification

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

Windows CMD beginners repeatedly type long `python tools\qh.py ...` commands and
can make quoting or working-directory mistakes. A convenience layer must not bundle
lifecycle operations, hide Verification, or gain authority beyond the existing CLI.

## Goal

Provide one transparent Repository-root `qh.cmd` launcher that forwards all arguments
and the child exit code to the existing Python qh CLI, including when the Repository
path contains spaces.

## Architecture Basis

- ADR-003 records Windows command reliability incidents and favors small deterministic tools.
- ADR-006 identifies Windows workflow simplification as an operations candidate.
- ADR-010 lists Windows workflow simplification as NEXT-HARDENING work while preserving
  the existing lifecycle and Verification authority.
- The Python qh CLI remains the sole command implementation and output authority.

## Dependencies

- QH-V2-LIFECYCLE-001 must be COMPLETE - VERIFIED.
- QH-V2-WORKER-ROB-001 remains `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` and is not
  required or permitted to become successful dependency Evidence.
- QH-V2-WORKER-DIAG-001 must reach a Human-reviewed disposition before this Task may
  be activated. If QH-V2-WORKER-ROB-002 is selected from that diagnosis, its terminal
  outcome and the Human decision to resume Operations must also be recorded first.
- Doctor remains a separate diagnostic command; the launcher does not combine it
  with lifecycle steps.
- The reprioritized queue uses the ordinary Human-controlled lifecycle. No autonomous
  manifest covers this Task after ADR-016.

## Scope

- Add a Repository-root `qh.cmd` thin launcher.
- Forward the complete argument vector unchanged to `tools\qh.py`.
- Preserve the Python child process exit code.
- Resolve the launcher-relative Repository path safely when it contains spaces.
- Document equivalent direct-Python and launcher commands for Windows CMD users.
- Add platform-independent static contract tests and Windows-only execution tests
  without allowing a non-Windows run to discover zero tests.

## Allowed Changes

- `qh.cmd`
- `tests/test_windows_workflow.py`
- `README.md`
- `docs/QUICKSTART.md`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-003.md`

## Forbidden Changes

- `tools/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. `qh.cmd status` and every existing qh command reach the same Python CLI parser.
2. Task ID, baseline commit, and completion commit arguments are forwarded unchanged.
3. The launcher returns the exact child process exit code for success and failure.
4. Invocation works when the Repository absolute path contains spaces.
5. Output meaning and qh authority remain unchanged; the wrapper adds no PASS inference.
6. Direct `python tools\qh.py ...` usage remains supported and regression-tested.
7. The launcher does not sequence commands, skip gates, edit files, modify PATH, or
   invoke Git independently.
8. Non-Windows test runs still execute deterministic static assertions rather than
   reporting an empty skipped module.
9. No shell, Git, Worker, or filesystem authority is added.

## Verification

Run exactly:

`python -m unittest tests.test_windows_workflow`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_qh_worker_run`

Then run:

`cmd /d /c qh.cmd --help`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Argument-forwarding and exit-code matrices cover no argument, Task ID, commit,
  unknown command, and child failure cases.
- A path-containing-spaces fixture proves launcher-relative quoting.
- Static contract assertions run on every platform; Windows execution assertions are
  capability-gated and their environment is recorded.
- Before/after Git state proves the wrapper itself adds no lifecycle or Repository mutation.
- Existing qh and qh Worker-run regression modules pass.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`; all Verification commands exit 0,
  no unexpected path appears, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- changing qh command semantics or combining lifecycle gates;
- automatic start, run, review, close, commit, or push;
- machine-wide installation, profile, registry, or PATH modification;
- a new dependency or cross-platform launcher redesign;
- general shell/Git authority or Architecture changes.
- `cmd.exe` is unavailable in the execution environment; report BLOCKED and do not
  delete, skip, or weaken the real Windows launcher Verification.

## Next Task

Queue successor candidate: QH-V2-OPS-004.

Until committed Requirement/Accepted Decision updates and the Human-approved G1
manifest cover the exact unchanged queue and successor contract blob, Human approval
is required and the successor must not be auto-started.
