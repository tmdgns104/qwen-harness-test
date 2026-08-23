# QH-V2-WORKER-ROB-001 - Single-Tool Worker Protocol Robustness

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

GitHub Issue #1 records two controlled real `qwen3:8b` runs in which the Worker
returned more than one ToolRequest in one WorkerStep. The Runner correctly returned
SAFETY with no Tool execution from the invalid step and zero Repository mutation, but
normal Repository work could not progress.

The safety boundary is correct; Worker interaction reliability inside that boundary
needs improvement.

## Goal

Strengthen the native Ollama Worker protocol so Qwen is explicitly instructed to use
at most one Tool per assistant turn, stop after requesting it, wait for ToolResult,
use that result before deciding the next action, and finish with text when no further
Tool is needed.

Preserve deterministic multi-tool SAFETY failure exactly as the fallback boundary.

## Scope

- Add an explicit bounded Worker protocol to the native Ollama adapter/context.
- Require at most one ToolRequest per assistant turn.
- Require the Worker to stop after requesting a Tool and wait for ToolResult.
- Require the next decision to use the returned ToolResult.
- Preserve normal text completion when no further Tool is required.
- Add deterministic/mock coverage for protocol construction and sequential multi-step
  interactions.
- Add deterministic Runner tests proving multi-tool SAFETY still causes no Tool
  execution from the invalid step.
- Collect Stable-versus-Candidate real `qwen3:8b` Evidence on the same small
  representative sequential tool scenario.

## Allowed Changes

- `tools/ollama_worker.py`
- `tests/test_ollama_worker.py`
- `tests/test_task_runner.py`
- `tests/test_qh_worker_run.py`
- `tests/worker_protocol_probe.py`
- `docs/WORKER_ROB_001_EVIDENCE.md`
- `STATUS.md`
- `tasks/QH-V2-WORKER-ROB-001.md`

## Forbidden Changes

- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/harness_core.py`
- `tools/repo_tools.py`
- `tools/qh.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `ops/**`
- `qh.cmd`

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. Worker instructions explicitly state `at most one` Tool per assistant turn, STOP
   after requesting it, wait for ToolResult, and use the result before another Tool.
2. Deterministic tests prove a compliant sequential read -> ToolResult -> write ->
   ToolResult -> text-completion interaction is representable.
3. Existing Runner behavior remains unchanged: multiple ToolRequests in one step
   produce SAFETY with no Tool execution from that invalid step.
4. No automatic splitting, selection, repair, or execution of multiple ToolRequests
   is introduced.
5. Stable and Candidate real `qwen3:8b` runs use the same representative probe,
   model, `think:false` policy, tool schema, and run count.
6. Evidence records NORMAL, multi-tool SAFETY, STEP_BUDGET,
   TRANSIENT_WORKER/BLOCKED, and any other outcomes for both Stable and Candidate.
7. Candidate promotion requires no safety regression and materially better compliance
   with the one-tool-per-turn protocol than Stable.
8. No general shell/Git authority, retry-policy change, model-routing change, step
   budget increase, Final Gate change, or formal Globalization is introduced.

## Verification

Run exactly:

`python -m unittest tests.test_ollama_worker`

Then run:

`python -m unittest tests.test_task_runner`

Then run:

`python -m unittest tests.test_qh_worker_run`

Then run:

`python -c "from pathlib import Path; p=Path('docs/WORKER_ROB_001_EVIDENCE.md'); s=p.read_text(encoding='utf-8'); required=('Stable','Candidate','qwen3:8b','NORMAL','SAFETY','STEP_BUDGET','TRANSIENT_WORKER'); assert p.is_file() and all(x in s for x in required)"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Before production prompt/context change, the probe is run repeatedly against the
  Stable adapter and results are recorded.
- After the Candidate change, the exact same probe/run count is repeated.
- Stable-versus-Candidate comparison reports counts/rates for NORMAL, multi-tool
  SAFETY, STEP_BUDGET, TRANSIENT_WORKER/BLOCKED, and any other outcome.
- Deterministic/mock tests prove the existing no Tool execution safety boundary.
- Exact implementation HEAD is used by Human-invoked `qh close`; all deterministic
  Verification commands pass, Unexpected Changed Paths is no, Diff Check is 0, and
  Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP and request Human Architecture review if useful robustness requires:

- turning a multi-tool violation into automatic continuation or retry;
- automatically splitting, selecting, repairing, or executing one request from an
  invalid multi-tool step;
- changing Runner SAFETY classification or Retry policy;
- increasing the Worker step budget;
- changing model routing or default model;
- adding general shell, Git, network, or filesystem authority;
- changing Verification, Evidence, Final Gate, or lifecycle authority.

## Next Task

QH-V2-OPS-003 - Human-controlled candidate only. Do not auto-start.
