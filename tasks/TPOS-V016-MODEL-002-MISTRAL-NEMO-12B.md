# TPOS-V016-MODEL-002-MISTRAL-NEMO-12B - Mistral Nemo 12B Worker Benchmark

## Status

ACTIVE

## Problem

The MODEL-001 benchmark recorded `qwen2.5-coder:14b-instruct-q3_K_S` as
`FAIL — TOOL_CALLING` after it returned a tool request as ordinary text. This
Task evaluates exactly one new model against the same frozen deterministic
regression input. MODEL-001 and qwen3:8b evidence remain immutable controls.

## Goal

Measure whether `mistral-nemo:12b-instruct-2407-q3_K_S` can execute the existing
bounded Local Worker protocol and, if it reaches the write step, independently
verify the unchanged TPOS-V016-REG-002 positive and negative cases.

## Architecture Basis

- This is model comparison only; Harness Architecture is unchanged.
- Production Worker, Runner, Retry, timeout, step budget, tool schema, tool
  authority, ChangeScope, Verification, Final Gate, lifecycle, and Git authority
  remain unchanged.
- Runtime model selection uses only the existing isolated
  `run_single_task(..., session_factory=...)` seam.
- `think:false`, 30-second initial timeout, 60-second continuation timeout,
  eight Worker steps, and two bounded Retry attempts remain fixed.
- Harness `NORMAL` is interaction status, never Task PASS.
- Codex independently verifies all results.
- GLOBALIZATION remains NOT AUTHORIZED.

## Dependencies

- Clean MODEL-001 close: `2b7998b`.
- Frozen canonical input and driver baseline: `df086df`.
- Canonical Task source commit: `748b77391f2b545e75943f1fefeb9f18277c446f`.
- Prior failure Evidence: `30e762d28597cdedcaf3d2176d1cc4a28e2d83c7`.
- Canonical Task SHA-256:
  `b4ea3b067e897da23b7ef6f2f61f75daf677ecae081bc30d751e7b255c56c7a0`.
- Canonical Worker Brief SHA-256:
  `cd5f861fce3288d68edde4850d61c73677e7e5b9c5ca7252c1b9f8c0eb545081`.
- Reusable canonical files:
  `experiments/tpos-v016-model-001-qwen25-coder-14b/canonical/`.

## Scope

Use the canonical Task, exact-section Worker Brief, tool schema, fixture
semantics, and verification contract from MODEL-001 without modification. Run
only `mistral-nemo:12b-instruct-2407-q3_K_S` in a fresh isolated snapshot of the
Team Project OS at commit `748b773`.

The required protocol is exactly:

`user → native ToolRequest → ToolResult → continuation`

JSON or text that merely describes a tool call is not native tool calling. If
the first native probe fails, stop and classify `FAIL — TOOL_CALLING`; do not
change the prompt, fixture, parser, production code, timeout, or Harness.

If native tool calling reaches the pilot, preserve the first result and use the
normal production bounded retry behavior only. Never issue a repair prompt,
modify a fixture, weaken a test, or run another model.

Record exact model metadata, context, Ollama processor split, CPU/GPU allocation,
offload layers when available, nvidia-smi memory, every response timing, Harness
outcome/attempts/tool sequence, created paths, and scope status. The original
Team Project OS path is read-only; all Worker writes go only to the isolated
snapshot.

## Allowed Changes

- `tasks/TPOS-V016-MODEL-002-MISTRAL-NEMO-12B.md`
- `STATUS.md`
- `experiments/tpos-v016-model-002-mistral-nemo-12b/**`

## Forbidden Changes

- all `tools/**`, `tests/**`, `ops/**`, `src/**`
- `PROJECT.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `DECISIONS.md`,
  `BACKLOG.md`, `README.md`
- all MODEL-001 evidence and all previous experiments
- any file under `D:\team_project_os\team_project_os-main`
- Harness Architecture, tool authority, write scope, Retry, timeout, step
  budget, authentication, security, migration, or model policy changes
- prompt repair, fixture changes, test weakening, parser changes, or a second
  Mistral run
- Command-R7B or any other model benchmark
- Globalization approval or global Skill changes

All unlisted paths are default-denied.

## Acceptance Criteria

1. Working tree is clean before execution and MODEL-001 evidence is unchanged.
2. Canonical Task/Brief hashes and projected sections match MODEL-001 exactly.
3. Exact Mistral tag and digest are recorded; no alternate model is used.
4. The isolated target starts clean at `748b773` with no generated regression
   test.
5. Native tool calling is distinguished from JSON/text imitation.
6. Context, Ollama processor, CPU/GPU allocation, offload, memory, timing,
   Harness, tool sequence, paths, and scope are recorded or marked unavailable.
7. Codex independently verifies `ref`, both deterministic cases,
   `requirements.REQ-HUMAN-001`, fixture meaning, diff, scope, immutability, and
   test strength.
8. `NORMAL` is never treated as PASS.
9. Final classification is exactly one of: `PASS — PRACTICAL WORKER`, `PASS —
   SLOW BUT USABLE`, `FAIL — WORKER_CAPABILITY`, `FAIL — TOOL_CALLING`, `FAIL —
   PERFORMANCE`, `FAIL — SAFETY/SCOPE`, `INCONCLUSIVE`.

## Verification

Run the MODEL-002 independent verifier. If a generated test exists, run the
original TPOS-V016-REG-002 commands unchanged. Always run the canonical direct
production positive/negative probe, full isolated regression, diff/scope checks,
and Qwen Harness focused checks. Record all exit codes and limitations.

## Evidence Requirements

Preserve canonical references, pre-run states, exact model metadata, raw Harness
trace, timing and GPU observations, generated content if any, independent
verification output, qwen3/qwen2.5 control comparison, final verdict, and
unsuccessful lifecycle evidence when applicable.

## Stop Conditions

Stop without repair or policy change if canonical input differs, the original
repository would be modified, model/context cannot be confirmed, native tool
calling fails, an unauthorized tool/path is requested, a scope violation occurs,
or any correctness failure would require prompt/fixture/test/parser/Harness
changes.

## Next Task

NONE. Command-R7B is not part of this Task.
