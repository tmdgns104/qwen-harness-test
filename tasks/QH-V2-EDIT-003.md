# QH-V2-EDIT-003 - Safe Missing Parent Creation for Scoped Writes

## Status

COMPLETE - VERIFIED

## Problem

QH-EXP-CODEX-REVIEW-003 proved that `write_repo_text` cannot create an
authorized new nested file when its parent directory is missing. The function
successfully resolves and authorizes the target, then calls `Path.write_text`
without creating the parent. The real Harness run therefore ended `NORMAL` but
did not create the required report.

The failed experiment is preserved as `CLOSED - UNSUCCESSFUL - EVIDENCE
RECORDED`; this Task must not reinterpret it as success.

## Goal

Allow `write_repo_text` to create missing parent directories for one final file
target only after that target has passed the existing Repository-root and
ChangeScope authorization checks.

Do not broaden production write scope, Worker tool authority, or accepted path
semantics.

## Architecture Basis

- ADR-004 and ADR-008 keep Repository write execution and authorization inside
  deterministic Harness code.
- FR-005 requires Task ChangeScope enforcement.
- FR-012 keeps tool permission and execution authority Harness-owned.
- QH-V2-EDIT-001 defines the scoped UTF-8 create/replace primitive.
- QH-V2-EDIT-002 makes Harness Core ChangeScope plus
  `resolve_scoped_write_target` the authoritative write authorization path.
- Qwen supplies only a Repository-relative path and content. It receives no
  directory, shell, Git, lifecycle, or general filesystem authority.

This Task is a narrow implementation completion of an already authorized file
creation. It does not introduce a directory tool or allow a directory to be an
independent write target.

## Dependencies

- QH-V2-EDIT-001 = COMPLETE - VERIFIED
- QH-V2-EDIT-002 = COMPLETE - VERIFIED
- QH-EXP-CODEX-REVIEW-003 = CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED
- Failure Evidence: experiments/codex-qwen-review-003/report.md
- Failure Evidence commit: 0938bfe29641efdfaf40d56b48c48c6dac04b170
- Failure lifecycle commit: 8b5a4ac

## Scope

Change only `write_repo_text` and its focused regression tests.

Required operation order:

1. Reject absolute paths using the existing check.
2. Construct the existing `ChangeScope`.
3. Call `resolve_scoped_write_target` and require all existing lexical,
   resolved-identity, Repository-root, allowed, forbidden, and default-deny
   checks to pass.
4. Preserve rejection when the authorized target already is a directory.
5. Only then create the authorized file target's missing parent directories.
6. Write the requested UTF-8 content using the existing full-replacement
   behavior.

Use the minimum implementation. Do not add a new public API, scope engine,
dependency, cleanup authority, or generalized directory operation.

## Allowed Changes

- tools/repo_tools.py
- tests/test_repo_tools.py
- tasks/QH-V2-EDIT-003.md
- STATUS.md

## Forbidden Changes

- tools/harness_core.py
- tools/task_runner.py
- tools/retry_runner.py
- tools/ollama_worker.py
- tools/qh.py
- all other tools/**
- all other tests/**
- experiments/**
- ops/**
- PROJECT.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- DECISIONS.md
- README.md
- BACKLOG.md
- all existing Task files
- any Team Project OS file
- any external path
- model / think / timeout / step budget / retry policy changes
- tool schema or tool authority changes
- production write-scope expansion
- Globalization approval

All unlisted paths are default-denied.

## Acceptance Criteria

1. An allowed nested new UTF-8 file succeeds when one or more parent
   directories are missing.
2. Missing parents are created only after the final target passes
   `resolve_scoped_write_target`.
3. A forbidden target with missing parents fails and creates no directory.
4. A Repository-escape target with missing parents fails and creates no
   external directory.
5. An absolute target with missing parents remains rejected and creates no
   external directory.
6. Existing file full replacement still writes exact UTF-8 content.
7. Existing recursive allow, forbidden-first, resolved-alias, default-deny,
   directory-target, and Repository-root protections remain passing.
8. No new independent directory operation or Worker authority is exposed.
9. No production write scope, retry, model, think, timeout, step-budget, or
   tool schema changes occur.
10. Focused RED Evidence is recorded before production implementation.
11. Focused and related full tests pass after the minimum implementation.
12. `python -m compileall` and `git diff --check` pass.
13. Task-range changed paths contain no unexpected file.

## Verification

Run exactly:

`python -m unittest tests.test_repo_tools -v`

Then run:

`python -m unittest tests.test_harness_core tests.test_task_runner tests.test_retry_runner tests.test_qh_worker_run -v`

Then run:

`python -m compileall tools tests/test_repo_tools.py`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- exact pre-implementation RED command and expected failure
- exact code and test diff
- focused test output and exit code
- related full test output and exit code
- compileall output and exit code
- `git diff --check` output and exit code
- Task-range changed paths and scope classification
- implementation commit
- authoritative `qh close` output and Final Gate result
- lifecycle commit and clean Git state
- optional real Harness probe result if unit/integration Evidence is
  insufficient

## Implementation Result

- `write_repo_text` still calls `resolve_scoped_write_target` before any new
  directory mutation.
- After the authorized target's existing-directory rejection, the function
  creates only `path.parent` with `parents=True` and `exist_ok=True`, then uses
  the existing UTF-8 full-content write.
- No public API, Worker tool schema, ChangeScope rule, write scope, retry,
  model, think, timeout, or step budget changed.

## Verification Evidence

- Pre-implementation focused RED: 5 tests ran; the allowed nested missing-parent
  case failed with the expected `FileNotFoundError`; forbidden, absolute,
  Repository-escape, and existing-file replacement cases passed.
- Post-implementation focused GREEN: the same 5 tests PASS.
- `python -m unittest tests.test_repo_tools -v`: 21 tests ran, PASS with one
  existing Windows symlink-permission SKIP. The separate resolved-identity
  helper test PASSed.
- Related full regression: 169 tests PASS across `tests.test_harness_core`,
  `tests.test_task_runner`, `tests.test_retry_runner`, and
  `tests.test_qh_worker_run`.
- `python -m compileall tools tests/test_repo_tools.py`: exit 0.
- `git diff --check`: exit 0.
- Pre-commit changed production/test paths are exactly
  `tools/repo_tools.py` and `tests/test_repo_tools.py`.

## Stop Conditions

Stop and report if:

- implementation requires changing Architecture or Requirements;
- directory creation would occur before final target authorization;
- an absolute, forbidden, default-denied, resolved-forbidden, or
  Repository-escape target can create a directory;
- production write scope, tool authority, retry, model, think, timeout, or step
  budget must change;
- tests must be weakened;
- any unexpected path changes;
- Team Project OS access or modification is required;
- Globalization approval is required.

## Next Task

After this Task is COMPLETE - VERIFIED, the Supervisor may create and run the
separately authorized successor experiment QH-EXP-CODEX-REVIEW-004. The Qwen
Worker must not select, start, close, or otherwise control that successor.
