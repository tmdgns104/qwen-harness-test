# QH-V2-SPEC-002 - Development Support Utility Boundary Specification

## Status

APPROVED - CONTRACT DRAFT IN PROGRESS

## Problem

Repeated Windows CMD quoting, multiline, escaping, encoded-payload, accidental-artifact, and candidate-application procedures have produced verified operational failures. ADR-003 requires repeated or error-prone manual procedures to become automation candidates through a separate approved Task.

## Goal

Define the Problem, Requirements, safety boundary, and future implementation contract for a small reusable Python development-support utility.

This Task is specification only. Do not implement Python code.

The utility must remain separate from Harness Core responsibilities and must not become a Worker Adapter.

## Architecture Boundary

- Preserve the HC-001 through HC-007 implementation sequence.
- Do not invoke Ollama, Qwen, OpenCode, or Codex.
- Do not implement an LLM tool-call loop.
- Do not determine final Task PASS or FAIL.
- Do not replace Harness Core Git, Verification, Evidence, or Final Gate components.


## Utility Scope

### In Scope

- Create or update text files from explicit source files without embedding large multiline or encoded payloads in CMD.
- Inspect unexpected changed or untracked Repository paths and report path, size, and a bounded text preview before any cleanup decision.
- Compare a candidate file with its target and report syntax, top-level definition preservation, and diff information when applicable.
- Check whether actual changed paths are inside an explicitly supplied expected path set.
- Produce human-readable diagnostic output for the above development-support operations.

### Out of Scope

- Automatically delete unexpected Repository files.
- Automatically commit, reset, restore, checkout, or clean Git state.
- Execute implementation or verification commands on behalf of Harness Core.
- Decide whether a Task is complete.
- Generate implementation code with an LLM.
- Call Ollama, Qwen, OpenCode, Codex, or any other model backend.
- Implement retry orchestration, Worker Adapter behavior, or final deterministic gates.
- Modify Architecture or Task scope.

The initial utility should remain a small developer-safety helper, not a second Harness.


## Functional Requirements

### FR-U001 - Readable file-based input

The utility must prefer explicit file paths and readable text inputs over long inline CMD payloads or opaque Base64/zlib transport.

### FR-U002 - Safe text write support

The utility may create or update a requested text file only when the destination path is explicitly supplied by the Human or current approved Task procedure.

### FR-U003 - Unexpected path inspection

The utility must be able to inspect unexpected changed or untracked paths and report at minimum the path and file size. For text-like files it may show only a bounded preview.

### FR-U004 - No automatic cleanup

The utility must not delete, restore, reset, checkout, clean, or otherwise remove unexpected Repository changes automatically. Cleanup remains an explicit Human action.

### FR-U005 - Candidate syntax inspection

For Python candidate files, the utility must be able to perform syntax parsing before any target-file application.

### FR-U006 - Candidate structure comparison

For Python candidate files, the utility must be able to compare existing top-level definitions between the target and candidate and report missing or unexpected definitions without silently repairing them.

### FR-U007 - Diff visibility

The utility must provide a readable diff or diff summary before a candidate is manually accepted for Repository application.

### FR-U008 - Expected-path check

The utility must be able to compare actual Git changed paths with an explicitly supplied expected path set and report mismatches. It must not redefine Allowed or Forbidden scope itself.

### FR-U009 - Diagnostic only

Inspection failures must produce explicit non-zero failure or diagnostic output. The utility must not convert failed checks into PASS.

### FR-U010 - No model backend

The utility must not invoke any LLM, Ollama, Qwen, OpenCode, Codex, or other model backend.

### FR-U011 - No Harness Core authority

The utility must not execute Harness Core final verification, assemble authoritative Evidence, or decide final Task PASS, FAIL, or BLOCKED.

### FR-U012 - Minimal implementation

The first implementation must use the Python standard library unless a later approved Task demonstrates a necessary dependency.


## Future Implementation Acceptance Criteria

A later implementation Task may be approved only if it preserves this specification and verifies at minimum:

- File-based text operations work without long inline CMD or encoded payloads.
- Unexpected paths can be inspected without automatic deletion or cleanup.
- Python candidate syntax failures are detected before target application.
- Missing or unexpected top-level Python definitions are reported.
- Candidate diff information is visible before manual acceptance.
- Changed-path mismatches against an explicitly supplied expected set are reported as failure.
- Failure paths return explicit diagnostics and do not silently PASS.
- No Git cleanup, commit, reset, restore, or checkout is performed automatically.
- No model backend is invoked.
- No final Harness Task verdict is produced.
- Tests demonstrate the safety boundaries above.

The concrete module name, CLI shape, and Repository path are deferred to that separate implementation Task.

## Allowed Changes

- `tasks/QH-V2-SPEC-002.md`
- `STATUS.md`

## Forbidden Changes

- `tools/**`
- `src/**`
- `tests/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- all other Task files
- all implementation code

## Acceptance Criteria

- The repeated operational problem is documented.
- Utility In Scope and Out of Scope boundaries are explicit.
- FR-U001 through FR-U012 are defined exactly once.
- Future implementation Acceptance Criteria are defined.
- HC-001 through HC-007 ordering remains unchanged.
- Worker Adapter implementation is not authorized.
- No Python implementation code is added.
- Only this Task file and STATUS.md are changed.

## Verification

Verify with:

- content assertions for FR-U001 through FR-U012 and required boundary text;
- `git diff --check`;
- `git status --short`;
- changed-path comparison against the two Allowed Changes.

## Stop Condition

Stop after this specification is verified and committed.

Do not implement the utility.
Do not implement Worker Adapter code.
Do not start HC-004 automatically.
