# QH-V2-PRR-001 - Pre-Runner Safety/UX Review

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-006 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints
QH-V2-ARCH-004 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints

## Goal

Review known safety, usability, automation, and troubleshooting candidates before Single-Task Runner implementation and classify each candidate without implementing it.

## Scope

Classify each known candidate as one of:

- REQUIRED BEFORE RUNNER
- SAFE TO DEFER UNTIL AFTER E2E
- DEFERRED PENDING MORE EVIDENCE

Candidates:

1. Automatic Task baseline recording and reuse by review.
2. Unification of Harness Core and Repository Edit Tool scope evaluation.
3. Reduction of long Windows CMD / inline Python workflows.
4. Deterministic qh doctor environment/state troubleshooting.
5. Clearer qh status current-state, progress, next-gate, and historical-handoff presentation.
6. Human-approved Task scaffold generation.
7. Worker smoke-test standardization after sufficient repeated Evidence.

The review must use existing Repository Evidence and current interfaces. It must identify any candidate whose absence creates a concrete safety or correctness risk for Single-Task Runner.

## Boundaries

- No candidate is implemented in this Task.
- No Runner, retry, CLI, E2E, Worker Adapter, Repository tool, or Harness Core code is changed.
- No Architecture is changed unless a conflict is discovered; if a conflict is found, STOP and report it instead of changing Architecture.
- Human approval remains required for any follow-up implementation Task.

## Allowed Changes

- `STATUS.md`
- `tasks/QH-V2-PRR-001.md`

## Forbidden Changes

- `DECISIONS.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `tools/**`
- `tests/**`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- All seven candidates are classified.
- Every REQUIRED BEFORE RUNNER classification includes concrete Repository Evidence or interface risk.
- Every deferred classification states why Runner safety/correctness does not currently depend on it.
- Follow-up implementation Tasks are identified only where justified.
- No implementation occurs.
- No file outside Allowed Changes is modified.
- The review produces an explicit GO or BLOCKED recommendation for Single-Task Runner.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after classification, recommendation, independent review, commit, lifecycle close, and clean working tree.

Do not begin Single-Task Runner or any improvement implementation in this Task.

## Review Result

### REQUIRED BEFORE RUNNER

1. Automatic Task baseline recording and reuse by review.
   - Evidence: `qh.py start` does not persist a Task baseline.
   - Evidence: `qh.py review` falls back to current HEAD when no baseline is supplied.
   - Evidence: `qh.py close` calls review without an explicit Task baseline.
   - Risk: committed Task-range changes can be absent from final lifecycle review unless the Human manually supplies the correct baseline.

2. Unification of Harness Core and Repository Edit Tool scope evaluation.
   - Evidence: Harness Core uses `ChangeScope`, `path_matches`, and `is_path_allowed`, including recursive `/**` patterns and forbidden-first precedence.
   - Evidence: `write_repo_text` currently uses exact tuple membership for allowed and forbidden paths.
   - Risk: Runner-connected edits could be authorized by different semantics than final Harness scope review.

### SAFE TO DEFER UNTIL AFTER E2E

3. Reduction of long Windows CMD / inline Python workflows.
   - Reason: repeated operator friction and quoting failures are real, but Runner safety can remain deterministic without this convenience improvement.

4. Deterministic `qh doctor` environment/state troubleshooting.
   - Reason: useful for recurrent setup and state failures, but current safety gates already fail closed and Runner correctness does not depend on a doctor command.

5. Clearer `qh status` current-state, progress, next-gate, and historical-handoff presentation.
   - Reason: improves usability and reduces confusion but does not change Runner execution authority or correctness.

6. Human-approved Task scaffold generation.
   - Reason: reduces repetitive Task preparation but does not affect Runner safety when Task contracts already exist and are Human approved.

### DEFERRED PENDING MORE EVIDENCE

7. Worker smoke-test standardization after sufficient repeated Evidence.
   - Reason: Adapter unit tests and one verified real qwen3:8b smoke already exist. Standardization should wait until Runner/E2E provides repeated smoke-test Evidence.

## Runner Recommendation

BLOCKED

Single-Task Runner must not begin until the two REQUIRED BEFORE RUNNER items are implemented and independently verified through separate approved Tasks.

Recommended follow-up Tasks:

- Task baseline lifecycle/review integration.
- Repository Edit Tool scope-engine unification.
