# QH-V2-EDIT-002 - Unify Edit Tool Scope Evaluation

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

QH-V2-PRR-001 - Pre-Runner Safety/UX Review

## Goal

Make Repository scoped edit authorization use the same authoritative scope semantics as Harness Core before Single-Task Runner integration.

## Problem

Harness Core scope evaluation supports:

- exact path matching;
- trailing /** recursive matching;
- forbidden-first precedence;
- default deny.

write_repo_text currently performs only exact tuple membership checks.

This creates inconsistent authorization semantics between edit-time enforcement and final Harness review.

## Scope

- Preserve the existing write_repo_text public API.
- Reuse Harness Core ChangeScope and is_path_allowed.
- Do not create a second scope engine.
- Preserve repository-root escape protection.
- Preserve directory rejection and UTF-8 text write behavior.
- Add regression tests for recursive allowed and forbidden patterns.

## Allowed Changes

- tools/repo_tools.py
- tests/test_repo_tools.py
- STATUS.md
- tasks/QH-V2-EDIT-002.md

## Forbidden Changes

- tools/harness_core.py
- tests/test_harness_core.py
- tools/qh.py
- tests/test_qh.py
- tools/ollama_worker.py
- tests/test_ollama_worker.py
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- existing Task files
- all other Repository files

## Acceptance Criteria

1. write_repo_text uses the authoritative Harness Core scope evaluator.
2. Existing exact allowed and forbidden behavior remains unchanged.
3. Allowed recursive /** patterns permit matching descendants.
4. Forbidden recursive /** patterns override allowed matches.
5. Unmatched paths remain denied.
6. Path traversal and absolute-path protections remain unchanged.
7. All repo_tools regressions PASS.
8. Harness Core regressions PASS.
9. git diff --check PASS.
10. No unexpected changed paths.

## Verification

Run exactly:

`python -m unittest tests.test_repo_tools`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop on scope-semantic ambiguity, regression, architecture change, or any authorization weakening.
