# QH-V2-OPS-004 - Worker Smoke / E2E Standardization

## Status

PLANNED

## Problem

Evidence for deterministic unit tests, adapter behavior, live Ollama connectivity,
and the real Qwen Worker E2E is spread across completed Task records. Without a
standard taxonomy, a live smoke response can be overstated as Repository completion,
or every local regression can be slowed by an unnecessary live dependency.

## Goal

Standardize four distinct test tiers and add an opt-in, bounded, Repository-read-only
live Worker smoke entry point while keeping real Repository-mutating E2E work behind
its own Human-approved Task, Git Evidence, Verification, and `qh close`.

## Architecture Basis

- ADR-002 defines native Ollama and Qwen as the default local backend.
- ADR-004 separates the backend-neutral Worker contract from local orchestration.
- ADR-006 identifies a repeatable smoke/E2E workflow as an operations candidate.
- ADR-008 defines the bounded tool loop and harness-owned Repository tools.
- ADR-009 defines bounded Retry semantics.
- ADR-010 recognizes that real M1 E2E Evidence is now sufficient to standardize the flow.
- QH-V2-E2E-001 is the historical real-Worker completion Evidence baseline.

## Dependencies

- QH-V2-OPS-003 must be COMPLETE - VERIFIED in the deterministic queue.
- Technically, completed M1 E2E and required Hardening are the core prerequisites;
  the operations queue remains serialized for reproducibility.
- Until committed Requirement/Accepted Decision updates and the Human-approved G1
  manifest cover this exact unchanged Task and queue blob identity, explicit Human
  approval is required before activation.

## Scope

- Define four tiers: deterministic unit, adapter test, opt-in live Ollama smoke,
  and real Worker E2E.
- Add a small `tools/worker_smoke.py` entry point that reuses the existing Ollama
  endpoint/model defaults, uses bounded timeout, and checks transport plus a non-empty
  model response without Repository tools.
- Add mocked unit tests for smoke success and failure paths.
- Create `docs/WORKER_TESTING.md` with exact commands, prerequisites, authority,
  expected results, and failure interpretation for each tier.
- Document real E2E as a separate Human-approved Task lifecycle, not an automatic script.

## Allowed Changes

- `tools/worker_smoke.py`
- `tests/test_worker_smoke.py`
- `docs/WORKER_TESTING.md`
- `README.md`
- `docs/QUICKSTART.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-004.md`

## Forbidden Changes

- `tools/ollama_worker.py`
- `tools/qh.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/repo_tools.py`
- `tools/harness_core.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. Documentation names and distinguishes deterministic unit, adapter, opt-in live
   Ollama smoke, and real Worker E2E tiers.
2. Each tier states its dependency, authority, command, Evidence value, and what it
   cannot prove.
3. The live smoke uses a bounded timeout and returns non-zero on transport failure,
   timeout, malformed response, or empty response.
4. The live smoke gives no Repository tool, write, Git, lifecycle, or general shell authority.
5. Smoke unit tests use fake transport only and require no live Ollama or model.
6. Ordinary unit regression never invokes the opt-in live smoke automatically.
7. A real E2E is documented as a separate Human-approved Task using qh run, scoped
   changes, Git/Test Evidence, exact implementation commit, and authoritative close.
8. Worker/model self-report and live smoke response are explicitly not Final PASS.
9. No model, Retry, tool, Runner, or Adapter authority changes.

## Verification

Run exactly:

`python -m unittest tests.test_worker_smoke`

Then run:

`python -m unittest tests.test_ollama_worker`

Then run:

`python -m unittest tests.test_qh_worker_run tests.test_task_runner tests.test_retry_runner`

Then run:

`python -c "from pathlib import Path; s=Path('docs/WORKER_TESTING.md').read_text(encoding='utf-8'); assert all(x in s for x in ('Deterministic Unit','Adapter Test','Live Ollama Smoke','Real Worker E2E'))"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Mocked tests cover success, timeout, transport error, malformed/empty response,
  non-zero exit, and zero Repository mutation.
- The documentation records exact commands and a four-tier authority matrix.
- Existing Ollama adapter, qh Worker-run, Runner, and Retry regressions pass.
- An optional manual live result may be recorded separately with environment/time,
  but is not an ordinary deterministic Verification dependency or completion authority.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`; contract commands exit 0,
  unexpected paths are absent, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- forcing live Ollama/model access into the normal unit gate;
- automatic model pull, server start, Repository write, or E2E lifecycle mutation;
- general shell/Git authority or expanded Worker tools;
- changes to Runner, Retry, Adapter, qh, or Harness semantics;
- Architecture or model-routing changes.

## Next Task

Queue successor candidate: QH-V2-OPS-005.

Until committed Requirement/Accepted Decision updates and the Human-approved G1
manifest cover the exact unchanged queue and successor contract blob, Human approval
is required and the successor must not be auto-started.
