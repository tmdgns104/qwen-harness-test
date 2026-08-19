# QH-V2-READ-001 - Harness-owned Repository Read Tools

## Status

COMPLETE - VERIFIED

## Parent

ADR-004 - Post-HC-007 Worker Integration Architecture
QH-V2-WC-001 - Worker Contract / Backend-Independent Boundary
QH-V2-OWA-001 - Native Ollama Worker Adapter
QH-V2-AUTO-002 - Deterministic Task Lifecycle Assistance

## Problem

The Native Ollama Worker Adapter can exchange WorkerRequest and WorkerResponse with Qwen3:8B, but Qwen still has no controlled way to obtain Repository file content. Granting direct filesystem or shell access would violate the Harness trust boundary.

## Goal

Implement the smallest Harness-owned Repository read capability that can return approved Repository text content while keeping all filesystem authority inside deterministic Harness code.

## Scope

Implement a deterministic read-only Repository tool in `tools/repo_tools.py`.

Initial V1 capability:

- read one Repository-relative text file
- return its text content to Harness-controlled callers
- reject absolute paths
- reject paths that escape the Repository root
- reject missing files
- reject directories
- fail closed on invalid paths or decoding failures

The read tool itself performs no model reasoning and makes no PASS/FAIL decision.

## Trust Boundary

Qwen must never receive direct filesystem, shell, Git, or subprocess authority.

The intended boundary is:

Qwen requests Repository content -> deterministic Harness validates path -> Harness reads approved file -> content may be returned to Worker orchestration.

This Task implements only the deterministic Repository read primitive. It does not yet connect Qwen tool calls to that primitive.

## Path Boundary

Input paths are Repository-relative only.

The implementation must:

- resolve paths against the supplied Repository root
- prevent `..` or equivalent traversal from escaping Repository root
- prevent absolute-path access outside the Repository
- fail closed if the resolved target is outside Repository root
- avoid shell execution

## Read Boundary

V1 reads UTF-8 text files only. Binary-file handling, search, glob, recursive directory listing, and large-context policy are outside this Task unless required by tests for safe rejection.

## Allowed Changes

- `tools/repo_tools.py`
- `tests/test_repo_tools.py`
- `tasks/QH-V2-READ-001.md`
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
- `ARCHITECTURE.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- A Repository-relative UTF-8 text file can be read successfully.
- Returned content exactly matches Repository file content.
- Absolute paths are rejected.
- Path traversal outside Repository root is rejected.
- Missing paths are rejected.
- Directories are rejected.
- Invalid UTF-8 fails closed.
- No shell, subprocess, Git, model, Ollama, edit, or verification authority is added.
- No Qwen tool-call orchestration is added in this Task.
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

Do not start scoped edit tools, Worker tool-call orchestration, Runner, retry, or later Milestone 1 Tasks.
