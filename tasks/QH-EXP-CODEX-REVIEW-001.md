# QH-EXP-CODEX-REVIEW-001 - Codex Interrupted Work Review Experiment

## Status

CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED

## Problem

Codex stopped because of usage limits while hardening Team Project OS V0.16.

The interrupted work is not committed and must not be treated as complete.

Qwen Harness is also still under development, so neither Qwen self-report nor Harness PASS alone is authoritative.

## Goal

Use Qwen3:8B only as a bounded Reviewer / Test Designer.

Review the copied Codex artifacts and create one evidence-based report evaluating whether the seven review findings appear addressed and which regression tests are still missing.

Do not modify Team Project OS or Qwen Harness production code.

## Architecture Basis

- This is an isolated experiment inside qwen-harness-test.
- GLOBALIZATION remains NOT AUTHORIZED.
- The original Team Project OS Repository is outside this Repository and must not be accessed or modified.
- Copied input artifacts are read-only Evidence.
- Qwen has no shell, Git, Architecture, or Final PASS authority.
- Harness Evidence will be independently reviewed by ChatGPT and later Codex.
- If Evidence is insufficient, report INSUFFICIENT EVIDENCE instead of guessing.

## Dependencies

Qwen Harness experiment baseline:

8cd21c5d737d683891917449efa0635731774309

Team Project OS verified V0.16 baseline:

7e4826f55603fbe290646d48533b75ed5b2406c0

Copied Evidence:

- experiments/codex-qwen-review-001/input/codex_v016_interrupted.patch
- experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

Existing Team Project OS regression Evidence before this experiment:

- Python compile PASS
- existing Python regression 64/64 PASS
- existing V0.16 Scenario A-H 10/10 PASS

These results do NOT prove the new review findings.

## Scope

Review exactly these seven findings:

1. Human Edit Preservation / DB-authoritative reconciliation
2. V0.15 -> V0.16 bootstrap of structured catalogs and Stable IDs
3. Stale Preview / Draft / Apply revision rebase and conflict handling
4. Large Conversation contiguous chunking and cursor progression
5. Distiller filesystem/tool isolation and prompt-injection resistance
6. Repeated document import non-growth
7. Session inventory performance/cache behavior

For every finding report:

- Verdict:
  - ADDRESSED
  - PARTIAL
  - NOT ADDRESSED
  - INSUFFICIENT EVIDENCE
- Exact Evidence from the copied files
- Remaining Risk
- Concrete Regression Test(s) that should exist
- Confidence:
  - HIGH
  - MEDIUM
  - LOW

Also report any cross-cutting regression or suspicious interaction found during review.

## Allowed Changes

- experiments/codex-qwen-review-001/report.md

## Forbidden Changes

- experiments/codex-qwen-review-001/input/**
- tools/**
- ops/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- README.md
- BACKLOG.md
- STATUS.md
- tasks/**
- any Team Project OS file
- any external path
- production Harness/qh/Worker/Runner/Retry behavior
- model / think / timeout / step budget / retry policy changes
- tool schema or tool authority changes
- Git operations
- shell execution
- network access
- automatic successor selection/start/close
- Globalization approval

All unlisted paths are default-denied.

## Acceptance Criteria

1. Worker writes only:
   experiments/codex-qwen-review-001/report.md

2. Report covers all seven findings.

3. Every finding contains:
   Verdict / Evidence / Risk / Regression Test / Confidence.

4. Claims must come from copied Evidence.

5. Missing context must be labeled INSUFFICIENT EVIDENCE.

6. Implementation Evidence and actual runtime/test Evidence must be clearly separated.

7. No production code, Harness code, input Evidence, lifecycle file, or Task contract is modified.

8. Report contains:

   Recommended Next Verification

9. Qwen must not claim Team Project OS is complete or merge-ready.

## Verification

Run exactly:

`python -c "from pathlib import Path; p=Path('experiments/codex-qwen-review-001/report.md'); t=p.read_text(encoding='utf-8'); required=['Human Edit Preservation','V0.15','Stale Preview','Large Conversation','Distiller','document','Session Inventory','Recommended Next Verification']; missing=[x for x in required if x.lower() not in t.lower()]; assert not missing, missing; assert len(t) >= 2500, len(t)"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Worker outcome
- Worker tool interaction result
- final changed paths
- report.md contents
- Verification exit codes
- git diff --check result
- independent ChatGPT Review
- later independent Codex Review

## Stop Conditions

Stop without widening scope if:

- Qwen requests shell, Git, network, or an external path.
- Qwen attempts to modify anything except report.md.
- Evidence is insufficient for a defensible conclusion.
- Harness returns deterministic FAIL or BLOCKED.
- unexpected Repository mutation occurs.
- Architecture, Requirements, Trust Boundary, Worker policy, or Globalization would need to change.

## Next Task

NONE.

This experiment does not authorize a successor.

Human / ChatGPT must review the result first.
