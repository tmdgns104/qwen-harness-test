# QH-V2-EDIT-001 - Harness-owned Scoped Edit Tools

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-004 - Post-HC-007 Worker Integration Architecture
FR-005 - Change scope contract
FR-008 - Failure stop behavior
FR-012 - Harness-owned tool boundary
QH-V2-READ-001 - Harness-owned Repository Read Tools

## Problem

The Harness can now read Repository text through a deterministic Repository-owned boundary, but the local Worker still has no controlled way to create or modify Repository files. Granting Qwen direct filesystem or shell write authority would violate ADR-004 and FR-012.

## Goal

Implement the smallest deterministic Harness-owned scoped text edit capability that can create or replace one approved Repository-relative UTF-8 text file while enforcing Task change scope before any write occurs.

## Scope

Extend `tools/repo_tools.py` with one deterministic scoped text-write primitive.

Initial V1 capability:

- accept one Repository-relative target path
- accept exact UTF-8 text content to write
- allow creation or full-content replacement of one text file
- require the target path to be permitted by deterministic Allowed Changes scope
- reject any target matched by Forbidden Changes
- reject absolute paths
- reject paths that escape the Repository root
- reject directory targets
- fail closed before mutation when validation or scope checks fail
- return deterministic success information without model reasoning

The exact Python function signature is an implementation detail of this Task.

## Trust Boundary

Qwen must never receive direct filesystem, shell, Git, subprocess, verification, or completion authority.

The intended boundary is:

Worker proposes an edit -> deterministic Harness validates Repository path and Task scope -> Harness performs the approved text write -> Git/Test Evidence independently verifies the result.

This Task implements only the deterministic scoped edit primitive. It does not connect Qwen tool calls to Repository editing.

## Scope Boundary

The edit primitive must enforce both Repository path safety and Task change scope before writing.

A model request alone must never authorize a write.

Allowed/Forbidden scope evaluation must be deterministic and backend-independent.

If the target is outside Repository root, outside Allowed Changes, or inside Forbidden Changes, the operation must fail without modifying Repository content.

## Edit Boundary

V1 supports UTF-8 text creation or full-content replacement only.

The following are outside this Task:

- delete operations
- rename or move operations
- directory creation
- binary editing
- patch/diff generation
- search or glob tools
- shell or subprocess execution
- Git operations
- Qwen tool-call orchestration
- Single-Task Runner
- retry logic

## Allowed Changes

- `tools/repo_tools.py`
- `tests/test_repo_tools.py`
- `tasks/QH-V2-EDIT-001.md`
- `STATUS.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tools/qh.py`
- `tests/test_harness_core.py`
- `tests/test_ollama_worker.py`
- `tests/test_qh.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- One approved Repository-relative UTF-8 text file can be created.
- One approved existing UTF-8 text file can have its full content replaced exactly.
- The written content exactly matches the requested content.
- Absolute paths are rejected before mutation.
- Repository path traversal is rejected before mutation.
- Directory targets are rejected before mutation.
- A path outside Allowed Changes is rejected before mutation.
- A path matched by Forbidden Changes is rejected before mutation.
- Failed validation leaves existing file content unchanged.
- No shell, subprocess, Git, model, Ollama, verification, or completion authority is added.
- No Qwen tool-call orchestration is added.
- Existing Repository read behavior remains passing.
- Existing Harness Core regression remains passing.
- Existing qh regression remains passing.
- No third-party dependency is added.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_repo_tools`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`python -m unittest tests.test_qh`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after implementation, Verification, independent review, commit, lifecycle close, and clean working tree.

Do not start Qwen tool-call orchestration, Single-Task Runner, retry, Minimal CLI, or E2E work.
