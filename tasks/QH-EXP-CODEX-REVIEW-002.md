# QH-EXP-CODEX-REVIEW-002 - Single-Finding Sequential Review Experiment

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

QH-EXP-CODEX-REVIEW-001 ended as CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED because the Worker emitted more than one ToolRequest in a single step.

The Harness failed closed and no Repository mutation occurred.

This successor experiment must not retry the same broad seven-finding review. It reduces the scope to one finding and one input file so that Qwen can be evaluated under the existing one-ToolRequest-per-step protocol without changing Harness architecture or tool authority.

## Goal

Evaluate only Finding 1:

Human Edit Preservation / DB-authoritative reconciliation.

Use only this copied Evidence file:

- experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

Create one report:

- experiments/codex-qwen-review-002/report.md

Do not evaluate the other six findings.

Do not modify Team Project OS or Qwen Harness production code.

## Required Worker Protocol

The first Worker step must request exactly one ToolRequest:

- read_repo_text for experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

Do not request any write in the first Worker step.

After the read result is returned, a later Worker step may request exactly one ToolRequest:

- write_repo_text for experiments/codex-qwen-review-002/report.md

Never emit more than one ToolRequest in a single Worker step.

Do not request shell, Git, network, another file, or an external path.

## Architecture Basis

- Qwen is a bounded Reviewer, not Final Authority.
- GLOBALIZATION remains NOT AUTHORIZED.
- The original Team Project OS Repository is outside this Repository and must not be accessed.
- Copied Evidence is read-only.
- Harness tool and safety boundaries remain unchanged.
- Qwen self-report is not Evidence.
- If this one file is insufficient for a claim, the report must say INSUFFICIENT EVIDENCE.

## Dependencies

Predecessor experiment:

- QH-EXP-CODEX-REVIEW-001 = CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED
- Failure Evidence: experiments/codex-qwen-review-001/report.md
- Predecessor lifecycle commit: e5e8d4b64407887cbb437d85505603ca4b8e436d

Input Evidence:

- experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

## Scope

Review only whether the copied structured-state implementation appears to address Human Edit Preservation / DB-authoritative reconciliation.

The report must answer:

1. What appears to be treated as official Source of Truth?
2. What role does project_structured_states appear to have after the change?
3. Does reconcile_structured_state rebuild requirements, decisions, designs, and structured catalogs from official DB/doc sources?
4. What evidence suggests stale cached structured state should no longer overwrite human edits?
5. What cannot be proven from this file alone?
6. What regression tests are still required?

Use one verdict:

- ADDRESSED
- PARTIAL
- NOT ADDRESSED
- INSUFFICIENT EVIDENCE

Include confidence:

- HIGH
- MEDIUM
- LOW

## Allowed Changes

- experiments/codex-qwen-review-002/report.md

## Forbidden Changes

- experiments/codex-qwen-review-001/input/**
- experiments/codex-qwen-review-001/report.md
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
- any additional experiment file
- production Harness/qh/Worker/Runner/Retry behavior
- model / think / timeout / Worker step budget / Retry policy changes
- tool schema or tool authority changes
- Git operations
- shell execution
- network access
- automatic successor selection/start/close
- Globalization approval

All unlisted paths are default-denied.

## Acceptance Criteria

1. Worker reads only the specified structured_state_v016_interrupted.py Evidence.
2. First Worker step contains exactly one read ToolRequest.
3. No step contains more than one ToolRequest.
4. Worker writes only experiments/codex-qwen-review-002/report.md.
5. Report covers only Human Edit Preservation / DB-authoritative reconciliation.
6. Report contains Verdict, Evidence, Remaining Risk, Regression Tests, Confidence, and Recommended Next Verification.
7. Claims unsupported by the single Evidence file are labeled INSUFFICIENT EVIDENCE.
8. No production, lifecycle, Task, input, or Harness files are modified.
9. Qwen must not claim Team Project OS is complete or merge-ready.

## Verification

Run exactly:

`python -c "from pathlib import Path; p=Path('experiments/codex-qwen-review-002/report.md'); t=p.read_text(encoding='utf-8'); required=['Human Edit Preservation','Verdict','Evidence','Remaining Risk','Regression','Confidence','Recommended Next Verification']; missing=[x for x in required if x.lower() not in t.lower()]; assert not missing, missing; assert len(t) >= 1200, len(t)"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Worker outcome
- number of attempts
- Failure Kind if any
- Worker tool interaction sequence
- final changed paths
- report.md contents if created
- independent Git state check
- independent ChatGPT Review
- later independent Codex Review

## Stop Conditions

Stop without retry or scope widening if:

- Harness returns deterministic FAIL or BLOCKED.
- Worker emits more than one ToolRequest in one step.
- Worker requests any file other than the specified input and report output.
- Worker requests shell, Git, network, or an external path.
- unexpected Repository mutation occurs.
- Architecture, Requirements, Trust Boundary, Worker policy, or Globalization would need to change.

## Next Task

NONE.

Human / ChatGPT must review the result before any successor is authorized.
