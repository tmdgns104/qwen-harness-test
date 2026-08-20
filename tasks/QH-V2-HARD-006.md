# QH-V2-HARD-006 - Windows Path Canonicalization Hardening

## Status

PLANNED

## Problem

The generic scope matcher normalizes slash direction but compares path text with
case-sensitive semantics. On a case-insensitive Windows filesystem, a case alias
can therefore disagree with Allowed/Forbidden precedence. Repository-root escape
checks and Runner lifecycle-file aliases already have separate resolved-path
defenses, so the remaining boundary must be isolated without duplicating them.

## Goal

Make write authorization use platform-correct path identity so Windows case and
resolved aliases cannot bypass Task scope, while preserving POSIX semantics and
the existing root and lifecycle protections.

## Architecture Basis

- ADR-001 assigns HC-002 ChangeScope matching, Forbidden-first precedence, and
  default-deny authorization to deterministic Harness Core.
- ADR-005 requires Automation V1 to reuse HC-001 through HC-007 rather than create
  a second policy engine.
- ADR-006 and completed QH-V2-EDIT-002 support unified edit authorization through
  the shared ChangeScope authority.
- ADR-008 requires Runner authorization and Repository-root safety before side effects.
- Existing Repository tools resolve targets and reject Repository-root escape.
- Existing Runner checks protect STATUS and current-Task lifecycle targets through
  resolved path identity and `os.path.normcase()`.
- This is audit-derived Hardening, not an ADR-010 classified item.

## Dependencies

- QH-V2-HARD-005 must be COMPLETE - VERIFIED.
- QH-V2-ARCH-008 must be COMPLETE - VERIFIED as a proposal, and the separate Human
  One-Time Autonomous Queue Gate outcome must be recorded.
- A rejected or deferred Gate leaves only the ordinary Human-controlled path.
- Autonomous activation additionally requires committed Requirement/Accepted Decision
  updates and a Human-approved G1 manifest covering this exact unchanged Task and
  queue blob identity.
- The queue serializes trust-boundary Hardening even though this path issue is
  technically separable from post-Verification Evidence refresh.

## Scope

- Add RED tests for Windows case aliases and resolved in-Repository aliases.
- Define platform-native path identity: case-insensitive on Windows and
  case-sensitive on POSIX.
- Preserve exact-path and trailing `/**` pattern semantics and slash normalization.
- Apply Forbidden-first/default-deny behavior to canonical target identity before write.
- Reuse a shared authorization helper at Repository-tool and Runner boundaries only
  where required to prevent a pre-write alias bypass.
- Preserve existing root-escape and lifecycle-file protections.

## Allowed Changes

- `tools/harness_core.py`
- `tools/repo_tools.py`
- `tools/task_runner.py`
- `tests/test_harness_core.py`
- `tests/test_repo_tools.py`
- `tests/test_task_runner.py`
- `STATUS.md`
- `tasks/QH-V2-HARD-006.md`

## Forbidden Changes

- `tools/qh.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. Platform-native identity is case-insensitive on Windows and remains case-sensitive
   on POSIX; tests do not impose Windows semantics globally.
2. Slash normalization, exact-path patterns, and trailing `/**` patterns keep their
   existing meanings; no new wildcard grammar is introduced.
3. A Windows case alias of a Forbidden path is rejected even when an Allowed
   recursive path would otherwise match.
4. A resolved in-Repository alias that identifies an out-of-scope or Forbidden
   target is rejected before any filesystem write and leaves the original bytes unchanged.
5. Rejected Runner authorization remains a deterministic safety failure with
   `write_attempted` false.
6. Absolute paths, `..` traversal, symlink or junction root escape, and resolved
   containment defenses continue to reject escape from Repository root.
7. Existing STATUS/current-Task case-alias lifecycle tests remain GREEN and their
   protection is not reimplemented in a conflicting layer.
8. Allowed in-scope writes still work on supported platforms.
9. No new tool, shell authority, Git authority, wildcard syntax, or Task permission
   is added.

## Verification

Run exactly:

`python -m unittest tests.test_harness_core.PathScopeMatcherTests`

Then run:

`python -m unittest tests.test_repo_tools`

Then run:

`python -m unittest tests.test_task_runner`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused RED reproduces a Windows case-alias Forbidden-precedence bypass.
- Focused GREEN records native Windows and POSIX comparison behavior separately.
- Before/after bytes prove rejected writes have zero side effects.
- Root-escape, Repository-tool, Runner lifecycle-alias, and scope regression tests pass.
- If a real symlink or junction test is unavailable due to host permissions, a
  deterministic helper test is mandatory and the capability-based skip is recorded.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`, whose output shows all
  Verification commands exit 0, no unexpected path, Diff Check 0, and Final Gate PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- an OS ACL, junction, reparse-point, or filesystem sandbox redesign;
- global case-folding that changes POSIX authorization semantics;
- new wildcard syntax or broader Task authority;
- an external dependency or general shell/Git authority;
- Retry, Worker, Adapter, or Architecture changes.

## Next Task

Queue successor candidate: QH-V2-HARD-007.

Until committed Requirement/Accepted Decision updates and the Human-approved G1
manifest cover the exact unchanged queue and successor contract blob, Human approval
is required and the successor must not be auto-started.
