# WORKER-ROB-001 Evidence

## Purpose

This document records the real local `qwen3:8b` Stable-versus-Candidate probe evidence for `QH-V2-WORKER-ROB-001`.

The Task requires Candidate promotion only when the Candidate shows no safety regression and materially better one-tool protocol compliance than Stable. The measured Candidate did not meet that promotion condition.

## Probe Configuration

Stable and Candidate runs used the same representative scenario and the same probe configuration:

- model: `qwen3:8b`
- `think:false`
- run count: 10
- scenario: `read -> ToolResult -> write -> ToolResult -> text`
- isolated temporary Repository per run
- goal: read `source.txt`, then write `target.txt` as exact `COPIED:` + returned source content

## Stable

Observed Stable summary:

- runs: 10
- NORMAL exact task success: 0
- NORMAL_TASK_MISS: 10
- SAFETY multi-tool: 0
- STEP_BUDGET: 0
- TRANSIENT_WORKER/BLOCKED: 0
- other failures: 0

A direct Stable diagnostic showed:

- expected: `COPIED:PROBE-CONTENT-99`
- actual: `COPIED:`
- outcome: NORMAL
- failure kind: none
- steps consumed: 3

The Worker interaction terminated normally, but the required ToolResult-derived content was not preserved in the write.

## Candidate

The bounded single-tool protocol Candidate added explicit instructions to:

- use at most one Tool per assistant turn;
- stop after requesting a Tool;
- wait for ToolResult;
- use the returned ToolResult before another Tool decision;
- finish with text when no further Tool is needed.

Deterministic `tests.test_ollama_worker` coverage passed after the Candidate protocol changes.

Real Candidate probe measurements did not improve the representative task:

- runs: 10
- NORMAL exact task success: 0
- NORMAL_TASK_MISS: 10
- SAFETY multi-tool: 0
- STEP_BUDGET: 0
- TRANSIENT_WORKER/BLOCKED: 0
- other failures: 0

Multiple Candidate prompt refinements were measured. The final measured Candidate still produced 0/10 exact task success. In the final 10-run measurement, 3 runs ended after 2 steps without a write side-effect risk and 7 runs consumed 3 steps with a write side-effect risk; all 10 remained NORMAL_TASK_MISS.

## Focused Diagnostics

Two focused live diagnostics narrowed the failure mode.

1. ToolResult recognition was demonstrated: after a read ToolResult containing `PROBE-CONTENT-99`, the Worker returned text containing that value (`RESULT: PROBE-CONTENT-99`).
2. ToolResult reuse in a following write request was also demonstrated, but exact formatting was not preserved: the Worker requested `write_repo_text` with content `COPIED: PROBE-CONTENT-99` instead of the required `COPIED:PROBE-CONTENT-99`.

These diagnostics show that the observed Candidate issue is not simply absence of ToolResult delivery. The Worker can recognize and reuse returned content, but the measured small-model behavior did not reliably satisfy the exact representative task contract.

## Safety Evidence

The Task does not authorize automatic splitting, selection, repair, retry, or execution of multiple ToolRequests from an invalid Worker step.

The failed experimental branch preserved the existing Runner-owned SAFETY boundary; no Runner SAFETY, retry policy, step budget, model routing, general shell/Git authority, or Final Gate authority change was introduced.

The prior cross-repository Issue #1 evidence remains the reproduction for real multi-tool SAFETY behavior: the Runner failed closed and executed no Tool from the invalid multi-tool step.

## Promotion Decision

**Candidate promotion: REJECTED.**

Reason: Stable and Candidate both measured 0/10 exact task success on the same real `qwen3:8b`, `think:false`, 10-run probe. This does not satisfy the Task requirement for materially better Candidate compliance.

The experimental implementation history is preserved on remote branch `work/QH-V2-WORKER-ROB-001-failed` with tip `bb12b44`. It is Evidence only and must not be treated as promoted production state.

No `qh close`, Final Gate PASS, Task completion, or next-Task start is claimed by this document.
