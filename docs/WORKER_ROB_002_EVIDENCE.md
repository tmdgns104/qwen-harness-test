# QH-V2-WORKER-ROB-002 Evidence

## Procedure

Exact experiment command: `python -m experiments.worker_rob_002 --repo-root . --task-id QH-V2-WORKER-ROB-002 --results docs/WORKER_ROB_002_RESULTS.json --evidence docs/WORKER_ROB_002_EVIDENCE.md`

The three variants were run in rotating interleaved order for 10 measured runs each. Only `OllamaToolSession.start()` was requested. Returned ToolRequests were inspected but never executed.

Stable runtime settings:

- model: `qwen3:8b`
- think: `False`
- timeout: `30.0` seconds
- tools: current production `read_repo_text` and `write_repo_text` schema

Exact one-step instruction:

`Choose exactly one next Worker action for this turn. Do not attempt to solve the entire Task in one response. If a tool action is needed, issue no more than one ToolRequest.`

The Worker Brief is a deterministic exact-section projection. The original tracked Task remains the Source of Truth and Verification / Final Gate authority remains Harness-owned.

## Summary

| Variant | transport-success rate | timeout rate | valid bounded first step | zero-tool terminal | multi-tool | invalid tool | scope-incompatible | median completed s | max s | Worker writes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stable - Full Task | 60.0% | 40.0% | 6/10 | 0.0% | 0.0% | 0.0% | 0.0% | 10.529492 | 30.038475 | 0 |
| Candidate A - Deterministic Worker Brief | 100.0% | 0.0% | 10/10 | 0.0% | 0.0% | 0.0% | 0.0% | 2.013165 | 4.816314 | 0 |
| Candidate B - Deterministic Worker Brief + One-Step Instruction | 70.0% | 30.0% | 2/10 | 50.0% | 0.0% | 0.0% | 0.0% | 20.778239 | 30.023746 | 0 |

## Safety / Interpretation

- No returned ToolRequest was executed by this benchmark; `write_executed` is false for every run.
- Read-path validity and write ChangeScope/lifecycle-path validity were reviewed against existing Harness contracts without invoking the production tool executor.
- A valid bounded first step is an interaction-quality metric only. It is not Repository PASS, Verification PASS, or Final Gate PASS.
- QH-V2-WORKER-ROB-001 remains CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED and is not reinterpreted as success.
- For the deterministic recommendation calculation, material improvement means at least +2 valid bounded first steps, at least -2 timeouts, or at least 25% lower completed-call median latency, while the approved fixed safety/reliability thresholds must also pass.

## Promotion Recommendation

RECOMMEND SEPARATE PRODUCTION TASK: Candidate A - Deterministic Worker Brief

The recommendation is only for a separate future production Task. This experiment performs no production promotion.

`GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
