# QH-EXP-CODEX-REVIEW-003 - Post-Timeout-Fix Single-Finding Review Experiment

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

QH-EXP-CODEX-REVIEW-002 reached the Worker continuation phase but ended BLOCKED because the native Ollama continuation request timed out under the former fixed 30 second timeout.

QH-V2-WORKER-TIMEOUT-001 then separated Worker timeouts:

- initial Worker request default: 30 seconds
- tool-result continuation default: 60 seconds

That timeout Task is COMPLETE - VERIFIED.

A read-only real Ollama probe using the same QH-EXP-CODEX-REVIEW-002 Worker Brief showed:

- first step requested exactly one read_repo_text
- continuation completed in 36.78 seconds
- continuation requested exactly one write_repo_text
- generated report payload: 3126 characters
- no Repository write was executed by the probe

This experiment verifies the same behavior through the real `qh.cmd run` path.

## Goal

Evaluate only Finding 1:

Human Edit Preservation / DB-authoritative reconciliation.

Use only:

- experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

Create only:

- experiments/codex-qwen-review-003/report.md

Do not evaluate the other six findings.

Do not modify Team Project OS or Qwen Harness production code.

## Architecture Basis

- Qwen is a bounded Reviewer, not Final Authority.
- GLOBALIZATION remains NOT AUTHORIZED.
- Team Project OS must not be accessed directly.
- Copied input Evidence is read-only.
- Qwen self-report is not final Evidence.
- Existing Harness safety, scope, retry, model, think, and tool-authority rules remain unchanged.
- The 60 second continuation timeout from QH-V2-WORKER-TIMEOUT-001 is the only relevant runtime change from QH-EXP-CODEX-REVIEW-002.

## Dependencies

- QH-EXP-CODEX-REVIEW-001 = CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED
- QH-EXP-CODEX-REVIEW-002 = CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED
- QH-V2-WORKER-TIMEOUT-001 = COMPLETE - VERIFIED
- Timeout implementation commit: a80d2aecdefb9cdcf58ede1c6d97065f1b230a82
- Timeout lifecycle commit: 784f9b7872ef2c3474126e86c8777c55c554f9ca

Input Evidence:

- experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

## Required Worker Protocol

The first Worker step must request exactly one ToolRequest:

- read_repo_text for experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

After the ToolResult is returned, a later Worker step may request exactly one ToolRequest:

- write_repo_text for experiments/codex-qwen-review-003/report.md

Never emit more than one ToolRequest in a single Worker step.

Do not request shell, Git, network, another file, or an external path.

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

- experiments/codex-qwen-review-003/report.md

## Forbidden Changes

- experiments/codex-qwen-review-001/input/**
- experiments/codex-qwen-review-001/report.md
- experiments/codex-qwen-review-002/**
- tools/**
- ops/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- DECISIONS.md
- README.md
- BACKLOG.md
- STATUS.md
- tasks/**
- any Team Project OS file
- any external path
- any additional experiment file
- model / think / timeout / step budget / retry policy changes
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
3. No Worker step contains more than one ToolRequest.
4. Worker writes only experiments/codex-qwen-review-003/report.md.
5. `qh.cmd run` completes without continuation timeout.
6. Report covers only Human Edit Preservation / DB-authoritative reconciliation.
7. Report contains Verdict, Evidence, Remaining Risk, Regression Tests, Confidence, and Recommended Next Verification.
8. Claims unsupported by the single Evidence file are labeled INSUFFICIENT EVIDENCE.
9. No production, lifecycle, Task, input, or Harness files are modified by the Worker.
10. Qwen must not claim Team Project OS is complete or merge-ready.

## Verification

Run exactly:

`python -c "from pathlib import Path; p=Path('experiments/codex-qwen-review-003/report.md'); t=p.read_text(encoding='utf-8'); required=['Human Edit Preservation','Verdict','Evidence','Remaining Risk','Regression','Confidence','Recommended Next Verification']; missing=[x for x in required if x.lower() not in t.lower()]; assert not missing, missing; assert len(t) >= 1200, len(t)"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Worker outcome
- attempts
- Failure Kind if any
- Write Side Effect Risk
- actual changed paths
- report.md contents
- verification command exit codes
- independent Git state check
- independent ChatGPT review
- later independent Codex review

## Stop Conditions

Stop without retry or scope widening if:

- Harness returns deterministic FAIL or BLOCKED.
- Worker requests more than one ToolRequest in one step.
- Worker requests any file other than the specified input and report output.
- Worker requests shell, Git, network, or external access.
- unexpected Repository mutation occurs.
- timeout, retry, model, think, scope, tool authority, Architecture, Requirements, or Globalization would need another change.

## Next Task

NONE.

Human / ChatGPT must review the result before any successor or Team Project OS decision is authorized.
