# QH-V2-HARD-008 - Cross-Repository Runtime Portability

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

GitHub Issue #1 proves that the documented `python tools\qh.py run TASK-ID` entry
path can fail with `ModuleNotFoundError: No module named 'tools'` unless the operator
manually sets `PYTHONPATH`. `qh doctor` and `qh preflight` can still report readiness
because the delayed `run` import chain is not exercised.

This is a runtime/import portability defect. It is separate from Worker prompting,
multi-tool SAFETY behavior, model choice, and formal Globalization.

## Goal

Make the existing Repository-copied Qwen Harness runtime support the documented
`python tools\qh.py ...` entry path without operator-set `PYTHONPATH`, and make
`qh doctor` detect structural readiness of the delayed Worker/run import chain.

## Scope

- Define one minimal supported internal import strategy for the existing
  Repository-copied runtime.
- Preserve the documented `python tools\qh.py ...` invocation.
- Remove any requirement for the operator to set `PYTHONPATH` before `qh run`.
- Add a focused external-style Repository regression that traverses the real delayed
  `run` import chain without contacting live Ollama.
- Extend `qh doctor` so structural Worker/run import readiness is checked.
- Preserve Worker, Runner, Retry, tool, model, step-budget, Verification, and Final
  Gate semantics.

## Allowed Changes

- `tools/qh.py`
- `tools/retry_runner.py`
- `tools/task_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `tests/test_qh.py`
- `tests/test_qh_doctor.py`
- `tests/test_qh_worker_run.py`
- `tests/test_retry_runner.py`
- `tests/test_task_runner.py`
- `tests/test_ollama_worker.py`
- `tests/test_runtime_portability.py`
- `STATUS.md`
- `tasks/QH-V2-HARD-008.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `README.md`
- `docs/**`
- `ops/**`
- `qh.cmd`

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. From a clean Repository root, `python tools\qh.py run <ACTIVE-TASK-ID>` reaches
   the Runner import path without operator-set `PYTHONPATH`.
2. A focused regression constructs an external-style Repository-copied runtime and
   exercises the actual documented qh entry path without live Ollama.
3. `qh doctor` includes a required readiness check for the delayed Worker/run import
   chain and cannot report overall PASS when that chain is structurally broken.
4. Existing qh direct invocation, Worker run, Retry, Runner, and Ollama adapter tests
   continue to pass.
5. No packaging/global-install redesign, machine-wide PATH change, or operator
   environment-variable requirement is introduced.
6. Worker authority, prompt/model behavior, multi-tool SAFETY semantics, retry policy,
   step budget, and Final Gate authority are unchanged.

## Verification

Run exactly:

`python -m unittest tests.test_runtime_portability`

Then run:

`python -m unittest tests.test_qh_doctor`

Then run:

`python -m unittest tests.test_qh_worker_run tests.test_retry_runner tests.test_task_runner tests.test_ollama_worker`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused RED reproduces the documented import failure before the production fix.
- Focused GREEN proves the same external-style entry path is structurally ready after
  the fix, without operator-set `PYTHONPATH`.
- Doctor regression proves a broken delayed run import chain yields required-check
  failure rather than false overall readiness.
- Existing Worker/Runner/Retry tests prove no behavior or Trust Boundary change.
- Exact implementation HEAD is used by Human-invoked `qh close`; authoritative
  Verification, Diff Check, changed-path Evidence, and Final Gate all PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP and report `DESIGN CHANGE REQUIRED` if:

- a package manager, global install, registry, profile, or machine-wide PATH change
  is required;
- the documented direct Python qh entry path must be removed;
- the fix requires changing Worker prompt/model behavior, Runner multi-tool semantics,
  Retry policy, step budget, tool authority, or Final Gate authority;
- a general shell/Git/network authority expansion is required;
- formal Globalization approval would be required to complete this defect fix.

## Next Task

QH-V2-WORKER-ROB-001 - Human-controlled candidate only. Do not auto-start.
