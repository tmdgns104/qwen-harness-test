# QH-V2-OPS-002 - qh doctor

## Status

COMPLETE - VERIFIED

## Problem

Beginners currently diagnose Python, Git, Repository-root, lifecycle, Ollama, and
model readiness through separate commands. One missing prerequisite can obscure the
remaining state, while unsafe automatic repair or unsanitized errors could create
new risk.

## Goal

Add a read-only `qh doctor` command that continues through independent checks,
reports stable PASS/WARN/FAIL results, returns an overall status, and never changes
the Repository, environment, Ollama, Git remote, or credentials.

## Architecture Basis

- ADR-002 defines native Ollama with default Qwen model as the local Worker backend.
- ADR-003 favors deterministic, inspectable CLI behavior.
- ADR-005 preserves lifecycle and Human authority.
- ADR-006 identifies environment diagnostics as an operations candidate.
- ADR-010 lists `qh doctor` as NEXT-HARDENING work.
- Local-first operation means a missing remote is diagnostic, not a universal failure.

## Dependencies

- QH-V2-OPS-001 must be COMPLETE - VERIFIED in the deterministic queue.
- The scaffold is not a technical prerequisite for diagnostics, but the queue keeps
  one Human-approved operations change active at a time.
- Until committed Requirement/Accepted Decision updates and the Human-approved G1
  manifest cover this exact unchanged Task and queue blob identity, explicit Human
  approval is required before activation.

## Scope

- Add a flat read-only `doctor` qh command.
- Report Python runtime information without inventing an unsupported minimum version.
- Check Git availability, Repository root, required existing Source-of-Truth files,
  lifecycle shape, current Task file, ChangeScope, Verification parse, working tree,
  optional Git remote, Ollama endpoint, and configured/default model.
- Treat required Repository/Worker-readiness failures as FAIL and nonessential local
  conditions such as dirty worktree or missing remote as explicitly defined WARNs.
- Continue remaining independent checks after a single check exception.
- Sanitize credential-bearing URLs, authorization data, and backend errors.
- Use fake transports and isolated fixtures in unit tests.

## Allowed Changes

- `tools/qh.py`
- `tools/qh_doctor.py`
- `tests/test_qh_doctor.py`
- `tests/test_qh.py`
- `README.md`
- `docs/QUICKSTART.md`
- `docs/HOW_IT_WORKS.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-002.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/repo_tools.py`
- `.env`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. `qh doctor` prints one stable label and PASS, WARN, or FAIL for every specified check.
2. Python output is factual runtime information and does not claim an unverified
   compatibility range or minimum.
3. Required Source-of-Truth checks use files that actually exist: PROJECT,
   REQUIREMENTS, DECISIONS, and STATUS; absent `AGENTS.md` or `ARCHITECTURE.md` is not
   invented as a required-file failure.
4. Lifecycle, current Task, scope, and Verification parse failures produce overall
   non-zero status.
5. Dirty working tree and missing optional remote have documented WARN semantics.
6. Ollama/model unavailable cases produce clear readiness results without pull,
   server start, model change, or other repair.
7. One check exception does not hide later independent checks.
8. Success, warning, and failure paths leave Repository bytes and Git state unchanged.
9. Output does not reveal credentials, bearer values, or credential-bearing URLs.
10. Unit tests require no live network, Ollama installation, model, or credential.
11. Existing qh and Ollama adapter behavior remains compatible.

## Verification

Run exactly:

`python -m unittest tests.test_qh_doctor`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_ollama_worker`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- A fixture matrix records output labels, overall exits, and PASS/WARN/FAIL meaning.
- Fake Ollama transport covers reachable, unreachable, model-present, model-missing,
  timeout, and sanitized-error cases.
- Malformed lifecycle, scope, and Verification cases demonstrate fail-closed reporting.
- Before/after Repository snapshots prove zero mutation for every outcome.
- Existing qh and Ollama adapter regressions pass without a live backend.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`; all Verification exits are 0,
  unexpected paths are absent, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- automatic repair, model pull, server start, remote change, or credential storage;
- inventing a Python, Git, Ollama, or model version requirement;
- a new dependency, network authority, or destructive diagnostic;
- broad CLI, Adapter, Worker, Runner, Retry, or Repository-tool changes;
- Architecture or Requirements changes.

## Next Task

Queue successor candidate: QH-V2-OPS-003.

Until committed Requirement/Accepted Decision updates and the Human-approved G1
manifest cover the exact unchanged queue and successor contract blob, Human approval
is required and the successor must not be auto-started.
