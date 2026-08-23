# QH-V2-WORKER-ROB-002 - Deterministic Worker Brief and One-Step Interaction Experiment

## Status

DRAFT - HUMAN REVIEW REQUIRED

This Task is an Evidence-driven experiment only. It does not authorize production Worker prompt/runtime integration or Candidate promotion.

## Problem

QH-V2-WORKER-DIAG-001 established that the current local Worker is responsive for short requests but unstable when asked to solve a full Repository Task.

Observed Evidence includes:

- short prompt, no tools: 5/5 transport success;
- short prompt with the current Worker tool schema: 5/5 transport success;
- representative full Task prompt, no tools: 0/5 completed before the existing 30-second timeout;
- the same full Task input constrained to return exactly `OK`: 3/3 completed quickly;
- representative full Task plus the current tool schema: useful one-tool next actions were sometimes produced quickly, but repeated 30-second timeouts remained;
- input length alone therefore does not explain the failure shape;
- increasing timeout alone is not established as a correct fix.

The Human proposed reducing the amount of semantic work given to the local Worker when a Task is long. A free-form LLM summary is unsafe because it may omit or alter scope, safety, or Acceptance Criteria. The Candidate must therefore be deterministic and must preserve the original Task as the only Source of Truth.

## Goal

Determine with objective Stable-versus-Candidate Evidence whether a deterministic Harness-produced Worker Brief improves local Qwen interaction reliability without weakening Task constraints.

Compare exactly three variants:

1. **Stable - Full Task**
   - whole tracked current Task text;
   - current native Ollama Worker tool schema;
   - no new prompt policy.

2. **Candidate A - Deterministic Worker Brief**
   - exact section projection from the tracked Task;
   - no LLM paraphrasing or semantic summarization;
   - original Task remains Source of Truth.

3. **Candidate B - Deterministic Worker Brief + One-Step Instruction**
   - same deterministic Worker Brief as Candidate A;
   - add a fixed instruction to choose only one next Worker action / one ToolRequest in the current turn rather than attempting to solve the whole Task at once.

The Task may recommend a later production promotion Task only if the Candidate is materially better by the predefined Evidence criteria. This Task itself must not integrate the Candidate into production runtime behavior.

## Architecture Basis

This Task operates under:

- ADR-001 - deterministic Harness authority remains final;
- ADR-002 - native Ollama + Qwen3:8B remains the current default local Worker path and `think:false` remains the current fast path;
- ADR-008 - backend-neutral Worker/tool interaction contract remains unchanged;
- ADR-009 - bounded Retry/safe-stop semantics remain unchanged;
- ADR-011 - prompt/context policy is Evidence-driven and `GLOBALIZATION = NOT AUTHORIZED` remains unchanged;
- ADR-014 - more than one ToolRequest in one WorkerStep remains deterministic SAFETY failure and must not be repaired or split;
- ADR-015 - QH-V2-WORKER-ROB-001 remains `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`;
- ADR-016 - WORKER-DIAG-001 Evidence may justify WORKER-ROB-002 only after Human review;
- `docs/WORKER_DIAG_001_EVIDENCE.md` - direct experimental basis for this Task.

No Architecture or Trust Boundary change is authorized.

## Dependencies

Required predecessor Evidence:

- QH-V2-WORKER-DIAG-001 = `COMPLETE - VERIFIED`;
- `docs/WORKER_DIAG_001_EVIDENCE.md` is tracked at the current Repository history;
- QH-V2-WORKER-ROB-001 remains the exact unsuccessful terminal state and is not treated as successful implementation Evidence.

## Candidate Definition

### Deterministic Worker Brief

The experimental projector must build the Worker Brief only from exact tracked Task text.

It must copy, without paraphrasing, the Task identity/title plus the bodies of these required sections:

- `Goal`
- `Architecture Basis`
- `Dependencies`
- `Scope`
- `Allowed Changes`
- `Forbidden Changes`
- `Acceptance Criteria`
- `Stop Conditions`

The Brief must also include a fixed statement that:

- the original tracked Task remains the Source of Truth;
- the Brief grants no authority beyond the original Task;
- Verification and Final Gate remain Harness-owned.

The projector must fail closed if any required projected section is missing or duplicated.

The projector must not use another LLM to summarize, rewrite, rank, omit, or infer Task requirements.

### One-Step Instruction

Candidate B may prepend or append one fixed instruction equivalent to:

`Choose exactly one next Worker action for this turn. Do not attempt to solve the entire Task in one response. If a tool action is needed, issue no more than one ToolRequest.`

The exact experimental string must be recorded in Evidence.

This instruction does not change Runner authority: more than one ToolRequest remains invalid and none may be silently split or repaired.

## Experimental Procedure

Use the same runtime settings for all three variants:

- model: current Stable default `qwen3:8b`;
- think mode: current Stable `False`;
- timeout: current Stable `30.0` seconds;
- tools: current Worker tool schema from the production Runner;
- no timeout increase;
- no model change;
- no Retry-policy change;
- no production prompt change.

Run the three variants in interleaved order for **10 measured runs per variant** so warm-up/order effects are not concentrated in one variant.

The experiment must request only the initial Worker step. Returned ToolRequests must be inspected but not executed. Repository writes through Worker tools are therefore forbidden during the benchmark.

For every measured run record at minimum:

- variant;
- run index;
- elapsed seconds;
- transport success or exception/failure classification;
- timeout occurrence;
- number of ToolRequests;
- ToolRequest name(s);
- ToolRequest arguments sufficient for deterministic validity review;
- output length when applicable;
- whether a multi-tool SAFETY shape occurred;
- whether requested paths comply with the current tool's own read/write authorization semantics;
- whether any Repository write was executed (`false` for this experiment).

For `write_repo_text`, raw generated file content does not need to be persisted in benchmark Evidence when path plus content length/hash is sufficient for deterministic review. This avoids unnecessary Evidence bloat while preserving the requested-path and schema checks.

Record the raw measured results in `docs/WORKER_ROB_002_RESULTS.json` and the reviewed interpretation in `docs/WORKER_ROB_002_EVIDENCE.md`.

## Evaluation Metrics

For each variant calculate at minimum:

- transport-success rate;
- timeout rate;
- valid-one-ToolRequest rate;
- zero-tool terminal-response rate;
- multi-tool SAFETY-shape rate;
- invalid/unknown tool-request rate;
- scope-incompatible requested-path rate;
- median elapsed time for completed calls;
- p95 or maximum elapsed time;
- count of executed Repository writes, which must remain zero.

For this experiment, a **valid bounded first step** means all of the following:

- the call completes within the existing timeout;
- exactly one ToolRequest is returned;
- the ToolRequest name exists in the current Worker tool schema;
- its argument object satisfies the current schema shape;
- path validity is evaluated according to that tool's actual authority: `read_repo_text` requires a Repository-relative path that remains inside the Repository, while `write_repo_text` additionally requires the target to satisfy the original Task's Allowed/Forbidden ChangeScope;
- no tool is executed by the benchmark itself.

A read of a file that is forbidden to change is not automatically a scope violation when the current read tool contract permits that Repository-relative read. A write request is judged against the original Task ChangeScope.

This metric is an interaction-quality benchmark, not Repository Task PASS and not Final Gate PASS.

## Promotion Recommendation Threshold

This Task cannot promote production behavior. It may only recommend a later promotion/implementation Task.

A Candidate is eligible for that recommendation only if all are true across the 10 measured runs:

1. zero multi-tool SAFETY shapes;
2. zero scope-incompatible or unauthorized requested paths;
3. zero executed Repository writes during the experiment;
4. at least 9/10 valid bounded first steps;
5. no more than 1/10 timeouts;
6. no correctness/safety metric is worse than Stable;
7. it demonstrates a material reliability or latency improvement over Stable rather than only benefiting from a longer timeout.

If neither Candidate meets the threshold, record `NO PROMOTION RECOMMENDATION` and preserve the failed Evidence without changing production runtime.

If both meet the threshold, recommend the simpler Candidate unless Evidence clearly justifies Candidate B's additional one-step instruction.

## Scope

Implement only a reproducible, isolated experiment and its tests/Evidence.

The experimental code may:

- deterministically project the approved sections from the current Task text;
- construct the three benchmark request variants;
- call the existing native Ollama session for only the initial Worker step;
- inspect returned ToolRequests without executing them;
- record raw JSON results and an Evidence summary;
- expose pure helper functions that can be unit tested without live Ollama.

The experimental code must not be imported or invoked by the normal production qh/Runner path.

## Allowed Changes

- `experiments/worker_rob_002.py`
- `tests/test_worker_rob_002.py`
- `docs/WORKER_ROB_002_RESULTS.json`
- `docs/WORKER_ROB_002_EVIDENCE.md`
- `STATUS.md`
- `tasks/QH-V2-WORKER-ROB-002.md`

## Forbidden Changes

- `tools/ollama_worker.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/qh.py`
- `tools/harness_core.py`
- `tools/repo_tools.py`
- `ops/qhops/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- any Task file other than `tasks/QH-V2-WORKER-ROB-002.md`
- production Worker prompt/runtime integration
- timeout duration changes
- model changes or model routing
- `think` policy changes
- Worker step-budget changes
- Retry-attempt or Retry-classification changes
- tool schema or tool authority changes
- multi-tool split/repair/continuation behavior
- Verification or Final Gate changes
- lifecycle semantics changes
- Git authority changes
- Globalization authorization

## Acceptance Criteria

1. The Worker Brief is generated deterministically from exact tracked Task sections with no LLM summarization.
2. The original Task remains the only Source of Truth and the Brief grants no new authority.
3. Missing or duplicated required projected sections fail closed in unit tests.
4. Stable, Candidate A, and Candidate B are compared under the same model, think mode, timeout, and tool schema.
5. Exactly 10 measured runs per variant are recorded in the raw results artifact.
6. Variant order is interleaved or otherwise controlled so a one-time cold start is not assigned only to one variant.
7. The benchmark requests only the initial Worker step and executes no returned Worker ToolRequest.
8. Raw Evidence records elapsed time, transport/timeout classification, ToolRequest count/name/arguments or a deterministic bounded representation, output length, safety shape, tool-aware path/scope compatibility, and write-executed=false.
9. The Evidence summary reports every metric listed in Evaluation Metrics.
10. The Evidence explicitly distinguishes interaction-quality success from Repository PASS / Verification / Final Gate PASS.
11. Promotion recommendation uses the predefined threshold and does not reinterpret failure as success.
12. QH-V2-WORKER-ROB-001 remains unsuccessful historical Evidence.
13. No production Worker/Runner/Retry/qh/qhops behavior changes in this Task.
14. No timeout increase is used as the experimental fix.
15. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.

## Verification

Run exactly these deterministic verification commands after the experiment artifacts are committed:

1. `python -m unittest tests.test_worker_rob_002`
2. `python -c "import json; from pathlib import Path; p=Path('docs/WORKER_ROB_002_RESULTS.json'); assert p.is_file(); d=json.loads(p.read_text(encoding='utf-8')); runs=d['runs']; assert len(runs)==30, len(runs); counts={v:sum(1 for r in runs if r['variant']==v) for v in ('stable_full_task','candidate_worker_brief','candidate_worker_brief_one_step')}; assert counts=={'stable_full_task':10,'candidate_worker_brief':10,'candidate_worker_brief_one_step':10}, counts; assert all(r.get('write_executed') is False for r in runs)"`
3. `python -c "from pathlib import Path; s=Path('docs/WORKER_ROB_002_EVIDENCE.md').read_text(encoding='utf-8'); required=['Stable - Full Task','Candidate A - Deterministic Worker Brief','Candidate B - Deterministic Worker Brief + One-Step Instruction','transport-success rate','timeout rate','valid bounded first step','multi-tool','median','Promotion Recommendation','Repository PASS','Final Gate','GLOBALIZATION = NOT AUTHORIZED']; missing=[x for x in required if x not in s]; assert not missing, missing"`
4. `git diff --check`
5. `git status --short`

The live 30-run benchmark is Evidence collection, not a nondeterministic command to be rerun automatically inside authoritative `qh close`.

## Evidence Requirements

Before successful close, Evidence must include:

- exact experiment command/procedure;
- exact Stable runtime settings used;
- exact one-step instruction string;
- projector unit-test Evidence;
- raw 30-run JSON results;
- summary table for all three variants;
- timeout and latency comparison;
- tool correctness and safety comparison;
- explicit confirmation that no returned ToolRequest was executed;
- explicit promotion recommendation or `NO PROMOTION RECOMMENDATION` based only on the predefined threshold;
- `git diff --check` PASS;
- only Allowed Changes in the implementation diff;
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS before successful lifecycle completion;
- separate lifecycle commit after Final Gate PASS.

## Stop Conditions

STOP and request Human/ChatGPT Architecture review if the experiment appears to require any of the following:

- changing the production Worker Adapter or Runner to perform the comparison;
- increasing timeout as the primary fix;
- changing model or enabling a new reasoning/model-routing path;
- changing `think` policy;
- changing Worker step budget or Retry attempts/classification;
- executing or silently repairing a multi-tool step;
- broadening Worker tools or filesystem/shell/Git authority;
- changing Verification, Final Gate, lifecycle, or Git authority;
- allowing an LLM-generated summary to replace exact deterministic Task projection;
- making the Worker Brief a second Source of Truth;
- automatically promoting a Candidate;
- starting another Task automatically;
- authorizing Globalization.

Unexpected Repository mutation or benchmark write execution is a STOP condition and must be investigated before continuing.

## Next Task

No automatic successor.

After objective Evidence and Human review, possible dispositions are:

- recommend a separate production Worker-Brief integration Task;
- recommend a narrower one-step interaction policy Task;
- recommend both only if Architecture and Evidence justify separation;
- `NO PROMOTION RECOMMENDATION` and return to diagnosis/design;
- separately schedule the already-identified global-use configuration/portability Task;
- separately schedule the already-identified transport `TimeoutError` normalization Task;
- resume OPS-003 only after the ADR-016-required Human-reviewed Worker disposition is recorded.
