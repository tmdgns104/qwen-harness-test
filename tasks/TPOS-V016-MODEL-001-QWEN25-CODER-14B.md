# TPOS-V016-MODEL-001-QWEN25-CODER-14B - Qwen2.5 Coder 14B Worker Benchmark

## Status

CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED

## Problem

The existing `qwen3:8b` Local Worker completed the deterministic
`TPOS-V016-REG-002` Harness interaction with outcome `NORMAL`, but its negative
fixture violated the exact Task contract and the independently executed focused
test failed. That result is preserved as Worker capability failure Evidence.

The previously observed CPU-only behavior of
`qwen2.5-coder:14b-instruct-q3_K_S` was caused by an incomplete Ollama CUDA
payload and is not model-performance Evidence. Ollama 0.33.1 GPU repair and
partial offload are now verified, so the model can be evaluated on the same
deterministic Task.

## Goal

Run exactly one model-replacement benchmark of
`qwen2.5-coder:14b-instruct-q3_K_S` against the original
`TPOS-V016-REG-002` deterministic regression Task, preserve the first Harness
result without repair, independently verify its generated test and scope, and
classify the result using exactly one authorized final verdict.

## Architecture Basis

- This is a model benchmark, not a Harness Architecture change.
- The production Worker, Runner, Retry, tool schema, tool authority, write
  scope, Verification, Final Gate, lifecycle, and Git authority remain
  unchanged.
- Model selection is permitted only through the existing `run_single_task`
  session-factory seam in a standalone experiment driver.
- Production defaults and timeout policy remain unchanged: `think:false`,
  30-second initial timeout, 60-second continuation timeout, eight Worker steps,
  and two bounded Retry attempts for eligible transient failures.
- Harness `NORMAL` is interaction status only and is never benchmark PASS.
- Codex is the independent verifier and final classifier.
- Team Project OS production files are never modified directly.
- GLOBALIZATION remains NOT AUTHORIZED.

## Dependencies

- Qwen Harness benchmark baseline: `67fa6e4`.
- GPU diagnostic Evidence: commit `67fa6e4` and
  `docs/QWEN_14B_GPU_OFFLOAD_DIAGNOSTIC_2026-08-28.md`.
- Original Team Project OS repository: `D:\team_project_os\team_project_os-main`
  (read-only for this experiment).
- Preserved failure bundle:
  `D:\team_project_os\TPOS-V016-REG-002-worker-capability-failure.bundle`.
- Canonical Task contract commit:
  `748b77391f2b545e75943f1fefeb9f18277c446f`.
- Prior qwen3:8b failure Evidence commit:
  `30e762d28597cdedcaf3d2176d1cc4a28e2d83c7`.
- Canonical Task SHA-256:
  `b4ea3b067e897da23b7ef6f2f61f75daf677ecae081bc30d751e7b255c56c7a0`.
- Canonical deterministic Worker Brief SHA-256:
  `cd5f861fce3288d68edde4850d61c73677e7e5b9c5ca7252c1b9f8c0eb545081`.

## Scope

Recover and preserve the exact ACTIVE `TPOS-V016-REG-002` Task from commit
`748b773`. Generate its Worker Brief only with the production deterministic
exact-section projector. Record the original qwen3:8b generated test only as
comparison Evidence.

Create a new isolated snapshot at the canonical Task commit. Run the production
Harness interaction against that snapshot with only the runtime model argument
changed to `qwen2.5-coder:14b-instruct-q3_K_S` through the existing
session-factory seam.

The benchmark input is immutable after hashing. Do not modify the prompt,
fixture, Task, tools, timeout, Retry, or context to obtain PASS. Preserve the
first bounded Harness result even when it fails.

Record:

- exact model tag, Ollama model ID/digest, quantization, and disk size;
- actual context and `ollama ps` processor split;
- GPU offload layers when observable and `nvidia-smi` memory;
- initial response elapsed, every continuation elapsed, and total wall-clock;
- Harness outcome, attempts, failure kind, and write-side-effect risk;
- tool sequence, created/changed paths, and scope classification;
- complete generated test and independent Verification output.

Independently verify the exact positive and negative semantics, `ref` identity,
`requirements.REQ-HUMAN-001` conflict path, production/existing-test immutability,
scope, and absence of test weakening.

## Allowed Changes

- `tasks/TPOS-V016-MODEL-001-QWEN25-CODER-14B.md`
- `STATUS.md`
- `experiments/tpos-v016-model-001-qwen25-coder-14b/**`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `ops/**`
- `src/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `README.md`
- all other Task files
- all other experiment Evidence
- any file in `D:\team_project_os\team_project_os-main`
- production Architecture, authentication, security, migration, lifecycle,
  tool authority, write scope, model routing, Retry, timeout, or step-budget
  changes
- prompt repair, repair attempt, fixture repair, or test weakening
- another model benchmark
- Globalization approval or global Skill changes

All unlisted Repository paths are default-denied.

## Acceptance Criteria

1. The original Team Project OS working tree remains byte-for-byte untouched by
   the benchmark.
2. The canonical Task and Worker Brief hashes match the Dependencies above and
   the projected section bodies exactly match the source Task.
3. The isolated target begins clean at commit `748b773` with the Task ACTIVE and
   without `tests/test_structured_state_v016_ref_identity.py`.
4. Exactly the requested model tag is used and the actual loaded context is
   16384.
5. Production tool schema, authority, write scope, Retry, step budget, initial
   timeout, and continuation timeout are unchanged.
6. One bounded Harness run is performed; production Retry may consume its normal
   attempts only for an eligible transient failure.
7. No prompt, fixture, repair follow-up, or second model run occurs after the
   first result.
8. All required runtime, latency, Harness, path, scope, and GPU measurements are
   recorded or explicitly marked unavailable with reason.
9. Codex independently executes the exact Task Verification commands that are
   applicable to the generated result and records actual exit codes.
10. Codex independently reviews both deterministic cases, `ref` identity, exact
    conflict path, fixture meaning, diff, scope, production immutability,
    existing-test immutability, and test strength.
11. The prior qwen3:8b failure remains preserved and is compared without being
    rewritten.
12. The final verdict is exactly one of: `PASS — PRACTICAL WORKER`, `PASS — SLOW
    BUT USABLE`, `FAIL — WORKER_CAPABILITY`, `FAIL — TOOL_CALLING`, `FAIL —
    PERFORMANCE`, `FAIL — SAFETY/SCOPE`, or `INCONCLUSIVE`.

## Verification

For canonical-input integrity, run the experiment's deterministic hash and
section-projection check.

In the isolated target, run exactly the original contract commands when the new
test exists:

`python -m unittest tests.test_structured_state_v016_ref_identity -v`

Then run:

`python -m unittest tests.test_conversation_import_v016 -v`

Then run:

`python -m unittest discover -s tests -v`

Then run:

`python -m compileall tests/test_structured_state_v016_ref_identity.py`

Then run:

`git diff --check`

Then run:

`git status --short`

Finally, inspect the exact diff against `748b773`, verify changed paths, confirm
the original Team Project OS status is unchanged, compile the experiment driver,
and run `git diff --check` in Qwen Harness.

## Evidence Requirements

- GPU diagnostic evidence commit
- bundle heads and recovered commit identities
- canonical Task, Worker Brief, fixture, and SHA-256 manifest
- prior qwen3:8b generated test and failure classification
- isolated snapshot path, pre-run HEAD/status, and output-file absence
- exact runtime policy and model metadata
- timestamped timing/tool trace and raw Harness result
- `ollama ps`, GPU offload, and `nvidia-smi` observations
- generated source, diff, changed paths, and scope review
- independent Verification command output and exit codes
- final verdict and qwen3:8b comparison
- final Qwen Harness changed paths and evidence commit

## Stop Conditions

Stop without repair or policy change if:

- the canonical input cannot be recovered or its hashes do not match;
- safe isolated runtime model selection cannot use the existing session-factory
  seam without production changes;
- the original Team Project OS repository would need to be modified;
- the requested model or context is not actually used;
- Harness returns deterministic SAFETY/FAIL, an unexpected path changes, or a
  scope violation occurs;
- a required correctness test fails;
- Architecture, authority, production write scope, Retry, timeout, step budget,
  security, migration, or Globalization would need to change;
- another prompt, repair, fixture alteration, or model run would be needed to
  obtain PASS.

## Benchmark Result

Final disposition: **FAIL — TOOL_CALLING**.

Evidence commit: `e1f207bcc6bce5c41c68c9377215f171180c61f8`.

The single actual model run completed in 10.147933 seconds with Harness outcome
`NORMAL`, one attempt, Failure Kind `NONE`, and no write-side-effect risk. The
model returned the required `read_repo_text` action as 104 characters of ordinary
JSON content with zero native ToolRequests. The Runner therefore performed no
tool action and created no regression test.

Independent verification confirmed the canonical production positive and
negative fixtures both behave exactly as contracted, the target and original
repositories are unchanged, V0.16 file discovery passes 10/10, and full Python
discovery passes 64/64. The required Worker test is absent, so neither Worker
case is implemented. Harness `NORMAL` was not treated as PASS.

Runtime Evidence records exact tag/digest, Q3_K_S, 6,659,609,738-byte model,
context 16384, `39%/61% CPU/GPU`, 30/49 GPU-offloaded layers, and 6,060 MiB GPU
memory after the response. No continuation occurred.

Qwen Harness focused verification passed 62/62 tests across Worker Brief, Task
Runner, Retry Runner, and Ollama Worker. Both experiment scripts compile, all
three JSON artifacts parse, and `git diff --check` passes.

Canonical input, raw result, independent verification, exact measurements, and
the qwen3:8b comparison are preserved under
`experiments/tpos-v016-model-001-qwen25-coder-14b/`.

## Next Task

NONE. Complete and report this one model benchmark only.
