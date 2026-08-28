# QH-EXP-CODEX-REVIEW-004 - Post-Parent-Fix Single-Finding Review Experiment

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

QH-EXP-CODEX-REVIEW-003 confirmed that the continuation-timeout fix worked but
did not create its report because the authorized nested output directory was
missing. That experiment is preserved as `CLOSED - UNSUCCESSFUL - EVIDENCE
RECORDED`.

QH-V2-EDIT-003 now permits `write_repo_text` to create missing parents only
after the final target passes existing Repository-root and ChangeScope checks.
This successor must verify the complete real Harness path without reusing or
overwriting 003.

## Goal

Run the same single-Finding review through the real Qwen Harness and create only:

- experiments/codex-qwen-review-004/report.md

The Worker must first read the copied implementation Evidence, analyze only
Human Edit Preservation / DB-authoritative reconciliation, and then write the
report through `write_repo_text`.

## Architecture Basis

- Qwen is a bounded Reviewer, not Final Authority.
- Qwen self-report and `qh run` outcome `NORMAL` are not Task PASS.
- Deterministic Harness code owns tool authorization and Repository writes.
- QH-V2-EDIT-003 changes only missing-parent materialization after final target
  authorization; production write scope and Worker authority remain unchanged.
- Team Project OS must not be accessed directly or modified.
- Copied input Evidence is read-only.
- Existing model `qwen3:8b`, `think:false`, retry, timeout, step budget, tool
  schema, and tool authority remain unchanged.
- GLOBALIZATION remains NOT AUTHORIZED.

## Dependencies

- QH-EXP-CODEX-REVIEW-003 = CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED
- 003 Evidence commit: 0938bfe29641efdfaf40d56b48c48c6dac04b170
- 003 lifecycle commit: 8b5a4ac
- QH-V2-WORKER-TIMEOUT-001 = COMPLETE - VERIFIED
- QH-V2-EDIT-003 = COMPLETE - VERIFIED
- EDIT-003 implementation commit: 22ed216ba4bd6cd4fe3d4ec8e748dbc90aac9214
- EDIT-003 lifecycle commit: 5b81aad523f0e44ec90091082bb785f34f7cfabd

Input Evidence:

- experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py

## Scope

Review only whether the copied structured-state implementation appears to
address Human Edit Preservation / DB-authoritative reconciliation.

Required Worker protocol:

1. The first Worker step requests exactly one `read_repo_text` ToolRequest for
   `experiments/codex-qwen-review-001/input/structured_state_v016_interrupted.py`.
2. Analyze the returned file content. Do not request another source.
3. A later Worker step requests exactly one `write_repo_text` ToolRequest for
   `experiments/codex-qwen-review-004/report.md` with the complete report.
4. Never emit more than one ToolRequest in one Worker step.
5. Do not request shell, Git, network, another file, or an external path.

The report must use these sections:

- Human Edit Preservation
- Verdict
- Evidence
- Remaining Risk
- Regression Tests
- Confidence
- Recommended Next Verification

It must answer:

1. What appears to be treated as official Source of Truth?
2. What role does `project_structured_states` appear to have after the change?
3. Does `reconcile_structured_state` rebuild requirements, decisions, designs,
   and structured catalogs from official DB/doc sources?
4. What code evidence suggests stale cached structured state should no longer
   overwrite human edits?
5. What cannot be proven from this single file?
6. What regression tests are still required?

Use one verdict: ADDRESSED, PARTIAL, NOT ADDRESSED, or INSUFFICIENT EVIDENCE.
Use confidence HIGH, MEDIUM, or LOW. Label claims unsupported by this single
file as INSUFFICIENT EVIDENCE. Do not claim Team Project OS is complete or
merge-ready.

## Allowed Changes

- experiments/codex-qwen-review-004/report.md
- tasks/QH-EXP-CODEX-REVIEW-004.md
- STATUS.md

## Forbidden Changes

- experiments/codex-qwen-review-001/input/**
- experiments/codex-qwen-review-001/report.md
- experiments/codex-qwen-review-002/**
- experiments/codex-qwen-review-003/**
- all other experiments/**
- tools/**
- tests/**
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
- Git, shell, network, lifecycle, commit, or successor operations by Qwen
- Globalization approval

All unlisted paths are default-denied. Although this contract permits normal
Supervisor lifecycle changes to its own Task and STATUS, the Runner's separate
lifecycle-control guard must continue to deny those paths to the Worker.

## Acceptance Criteria

1. Before `qh run`, `experiments/codex-qwen-review-004` does not exist and Git is
   clean.
2. The first Worker action is the exact required `read_repo_text` request.
3. No Worker step contains more than one ToolRequest.
4. The Worker later requests the exact required `write_repo_text` target.
5. `qh run` completes without timeout or deterministic SAFETY failure.
6. The missing output parent is created only as a consequence of the authorized
   report write.
7. The Worker-created report is at least 1200 characters and contains all
   required sections.
8. The report covers only Human Edit Preservation / DB-authoritative
   reconciliation and grounds its analysis in the copied file.
9. Unsupported completion, runtime, test, integration, and merge-readiness
   claims are labeled INSUFFICIENT EVIDENCE.
10. The Worker changes only the report; no production, input, prior experiment,
    lifecycle, Task, or external file is modified by Qwen.
11. Independent Supervisor review finds the verdict, evidence, limitations, and
    proposed regression tests logically adequate and not overstated.
12. All Verification commands exit 0 and authoritative `qh close` reaches Final
    Gate PASS before successful completion.

## Verification

Run exactly:

`python -c "from pathlib import Path; p=Path('experiments/codex-qwen-review-004/report.md'); t=p.read_text(encoding='utf-8'); required=['Human Edit Preservation','Verdict','Evidence','Remaining Risk','Regression','Confidence','Recommended Next Verification']; missing=[x for x in required if x.lower() not in t.lower()]; assert not missing, missing; assert len(t) >= 1200, len(t)"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- pre-run branch, HEAD, clean Git state, and absent output directory
- `qh run` exit code, outcome, attempts, Failure Kind, Write Side Effect Risk,
  and Worker output
- observed tool sequence Evidence or the strongest available deterministic and
  content-grounded evidence, with any observability limitation stated
- actual Worker-changed paths
- report bytes, length, and full content
- independent source-to-report comparison
- verification command exit codes
- implementation/report commit
- authoritative `qh close` output and Final Gate result
- lifecycle commit and final clean Git state

## Experiment Result

- `qh run QH-EXP-CODEX-REVIEW-004`: exit 0
- Outcome: NORMAL
- Attempts: 1
- Failure Kind: NONE
- Write Side Effect Risk: YES
- Pre-run output directory: absent
- Post-run Worker-created path:
  `experiments/codex-qwen-review-004/report.md`
- Report raw bytes: 2704
- Report SHA-256:
  `eb08a5171d642d37762041a0ea6b4a15d0361e97f5c118a40fc7c4c199dcd240`
- Structural/length Verification: PASS, 2663 normalized text characters
- `git diff --check`: PASS
- Worker changed no production, input, prior-experiment, lifecycle, Task, or
  external path.

`NORMAL` confirms only a normal Worker interaction. It is not Task PASS.

## Independent Supervisor Review

Final disposition: **TASK ACCEPTANCE NOT MET**.

The run provides strong evidence for the intended read/analyze/write path:

- The report names `source_of_truth_revision`, correctly notes that its hash
  excludes the cache row, and names `rebase_conflicts`; those details are in the
  copied source but not supplied in the Worker Brief.
- The Runner would deterministically return SAFETY rather than NORMAL if any
  Worker step contained multiple ToolRequests.
- The previously absent nested directory and report were created, and the only
  Worker-created Repository path is the authorized report.

The current CLI does not persist a per-step tool trace, so exact first-step
ordering is inferred from enforced single-request steps, source-specific report
content, and the write result rather than a durable call transcript. This
observability limitation is not hidden or treated as stronger Evidence.

The Qwen review itself is logically inadequate and overstated:

1. It states that the implementation "does not provide a mechanism to detect or
   handle concurrent edits that target the same stable identity." The same
   source file defines `rebase_conflicts` with the explicit purpose of returning
   concurrent edits that target the same stable identity. The report is
   contradicted by its only Evidence file and then inconsistently recommends a
   regression test for that function.
2. It assigns `ADDRESSED` with `HIGH` confidence without explaining that
   `merge_structured_states` is imported, so its precedence behavior cannot be
   proven from this file alone.
3. It describes `project_structured_states` as merging with official sources
   but omits the material nuance that cached decision refs and design keys are
   reused, and that cached project-update fields outside the explicit DB
   overwrites can survive reconciliation.
4. It does not answer what cannot be proven from the file alone and contains no
   `INSUFFICIENT EVIDENCE` label, contrary to the Task contract.
5. Its regression tests are generic and do not directly prove stale-cache versus
   human-edited DB/document precedence for requirements, decisions, designs,
   catalogs, and retained cache metadata.

Acceptance Criteria 8, 9, and 11 therefore FAIL. The report must be preserved as
failed experiment Evidence and must not be promoted, rewritten as success, or
used to claim Team Project OS completion or merge readiness.

## Stop Conditions

Stop without retry or policy change if:

- Harness returns deterministic FAIL, BLOCKED, or SAFETY failure;
- any Worker step emits more than one ToolRequest;
- the Worker requests an unauthorized path or tool;
- an unexpected Repository mutation occurs;
- the report is missing, under-length, off-scope, materially unsupported, or
  logically inadequate;
- Architecture, Requirements, tool authority, write scope, retry, model, think,
  timeout, step budget, test strength, Team Project OS, or Globalization would
  need to change.

## Next Task

NONE.

Report results before any Architecture expansion or Team Project OS decision.
