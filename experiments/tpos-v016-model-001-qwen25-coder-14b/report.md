# TPOS-V016-MODEL-001-QWEN25-CODER-14B Evidence

## Final Disposition

**FAIL — TOOL_CALLING**

`qwen2.5-coder:14b-instruct-q3_K_S` returned the required first
`read_repo_text` action as ordinary JSON text instead of an Ollama native tool
call. The production Runner therefore observed zero ToolRequests and correctly
ended the interaction as `NORMAL` without executing a read or creating the
regression test.

This is not a performance failure: the only model response completed within the
production initial timeout. It is not a scope failure: no target file changed.
It is not classified as Worker semantic capability failure because the model
never reached the source-reading or test-authoring phases.

## Preserved GPU Diagnostic

The pre-benchmark GPU repair and offload diagnostic was reviewed and preserved
separately before this experiment:

- evidence commit: `67fa6e4`
- evidence file: `docs/QWEN_14B_GPU_OFFLOAD_DIAGNOSTIC_2026-08-28.md`
- prior CPU-only latency/performance observations: excluded
- repaired GPU-offload resume gate: PASS

No unrelated working-tree changes were included in that commit.

## Canonical Input Recovery

Source bundle:

`D:\team_project_os\TPOS-V016-REG-002-worker-capability-failure.bundle`

Recovered commits:

- Task contract: `748b77391f2b545e75943f1fefeb9f18277c446f`
- prior qwen3:8b failure Evidence:
  `30e762d28597cdedcaf3d2176d1cc4a28e2d83c7`

Canonical artifacts:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| ACTIVE `TPOS-V016-REG-002` Task | 7,495 | `b4ea3b067e897da23b7ef6f2f61f75daf677ecae081bc30d751e7b255c56c7a0` |
| Deterministic Worker Brief | 6,223 | `cd5f861fce3288d68edde4850d61c73677e7e5b9c5ca7252c1b9f8c0eb545081` |
| Prior qwen3:8b output source blob | 2,387 | `5f84467497e5ccd729b8033066bc20495a3560585cc88fc96c89e876dfc6f156` |

The Worker Brief was regenerated with production
`tools.worker_brief.build_worker_brief`. All eight required section bodies match
the recovered Task exactly. No summary, repair instruction, one-step suffix, or
model-favoring prompt change was added.

Pre-run canonical-input/driver commit: `df086df`.

## Isolation and Authority

- Original Team Project OS:
  `D:\team_project_os\team_project_os-main`
- Isolated run snapshot:
  `%LOCALAPPDATA%\Temp\TPOS-V016-MODEL-001-QWEN25-CODER-14B-20260829-003606\target-run`
- Isolated pre-run HEAD: exact `748b77391f2b545e75943f1fefeb9f18277c446f`
- Isolated pre-run status: clean
- Generated-test path before run: absent
- Original repository pre/post status: identical
  (`main...origin/main` plus the same pre-existing untracked
  `team_project_os-main.zip`)

The benchmark used the existing `run_single_task(..., session_factory=...)`
seam and production `run_with_retry`. Only the runtime `model` constructor
argument changed. The following remained unchanged:

- `think:false`
- initial timeout: 30.0 seconds
- continuation timeout: 60.0 seconds
- `MAX_WORKER_STEPS = 8`
- `MAX_RUNNER_ATTEMPTS = 2`
- production `read_repo_text` and `write_repo_text` schemas
- tool execution authority and ChangeScope enforcement
- production defaults and files

No Architecture, authentication, security, migration, write-scope, Retry,
timeout, step-budget, or Globalization change occurred.

## Runtime and Hardware Evidence

| Measurement | Observed value |
|---|---|
| Exact model tag | `qwen2.5-coder:14b-instruct-q3_K_S` |
| Ollama model ID / digest | `ff7e2b2086f712b6825d425ef5258234de6814b69cf4cf8b52cebcfef5a5396a` |
| Parameter size | 14.8B |
| Quantization | `Q3_K_S` |
| Model disk size | 6,659,609,738 bytes (6.202 GiB; `ollama list` rounds to 6.7 GB) |
| Ollama allocation display | 10 GB |
| Actual context | 16,384 |
| `ollama ps` PROCESSOR | `39%/61% CPU/GPU` |
| GPU offload | 30/49 layers |
| CUDA model buffer | 3,882.02 MiB |
| Host model buffer | 2,463.37 MiB |
| Post-response GPU memory | 6,060 MiB used / 8,151 MiB total; 1,832 MiB free |
| GPU | NVIDIA GeForce RTX 5070 Laptop GPU |
| Driver | 610.71 |
| Ollama | 0.33.1 |

The PROCESSOR value is an Ollama CPU/GPU allocation split, not CPU utilization.
The system still carries a material CPU/host-memory share while consuming about
74% of reported GPU memory. The raw post-response utilization snapshot was 15%;
an idle follow-up was 0%, so neither is treated as sustained-load utilization.

## Exact Execution Result

The actual model benchmark ran once through the module entry point. An earlier
direct-file invocation failed immediately with `ModuleNotFoundError: tools`
before importing the driver, contacting Ollama, consuming a Harness attempt, or
touching the target. It is an operational invocation error, not a model run.

Actual measured run:

- UTC start: `2026-08-28T15:46:02.571251+00:00`
- UTC finish: `2026-08-28T15:46:12.719210+00:00`
- total wall-clock: 10.147933 seconds
- initial response elapsed: 10.146650 seconds, including cold model load
- continuation elapsed: not applicable; no native ToolRequest was returned
- Harness outcome: `NORMAL`
- attempts: 1
- Failure Kind: `NONE`
- Write Side Effect Risk: `NO`
- Worker-created/changed paths: none
- scope violation: no

Initial native response trace:

- transport: OK
- native ToolRequests: 0
- ordinary content length: 104 characters
- content SHA-256:
  `09a11f371eb4c6c14458148feab38f79d5da98ace6f4f4a26b6d3dc9479f336f`
- ordinary content:

```json
{
  "name": "read_repo_text",
  "arguments": {
    "relative_path": "app/structured_state_v016.py"
  }
}
```

The response described the correct next action but placed it in the content
channel. The Runner correctly did not reinterpret text as authority-bearing tool
input.

Raw result SHA-256:
`07b8d10212b1a40be93a9720ace38b372cdbbc8680783d7038245d9935b05c93`.

## Independent Codex Verification

The canonical fixtures were executed directly against the real production
`app.structured_state_v016.rebase_conflicts` without writing a test file:

- positive canonical case: PASS,
  `['requirements.REQ-HUMAN-001']`
- negative canonical case: PASS, `[]`
- stable requirement identity: confirmed `ref`, not `id`
- expected conflict path: confirmed exactly
  `requirements.REQ-HUMAN-001`
- fixture contract meaning: PASS

Worker-output verification:

- generated regression test: absent
- Worker positive case: FAIL / not implemented
- Worker negative case: FAIL / not implemented
- focused generated-test command: exit 1, module absent
- generated-test compile command: printed `Can't list`; its incidental exit 0
  is not treated as PASS

Regression and scope verification:

- exact dotted-module V0.16 command: exit 1 because the local `tests` namespace
  was shadowed by another installed `tests` package in this Python environment
- V0.16 file discovery diagnostic: 10/10 PASS
- full Python discovery: 64/64 PASS
- `git diff --check`: PASS
- isolated target `git status --short`: empty
- changed paths against `748b773`: none
- production files changed: no
- existing tests changed: no
- allowed scope exceeded: no
- test weakening: no test change, but the required new test is missing
- original Team Project OS status changed: no

Verification-result SHA-256:
`d16e7681f5702a079af693ab638a30d60fc85af4f36d953b224179db36cc6d7e`.

Harness `NORMAL` was not treated as Task PASS.

Qwen Harness evidence-artifact verification:

- Worker Brief, Task Runner, Retry Runner, and Ollama Worker focused regression:
  62/62 PASS
- benchmark driver and independent verifier compile: PASS
- canonical manifest, raw result, and verification-result JSON parse: PASS
- Qwen Harness `git diff --check`: PASS

## Comparison with qwen3:8b

| Criterion | Existing qwen3:8b TPOS-V016-REG-002 | Qwen2.5 Coder 14B Q3_K_S |
|---|---|---|
| Harness outcome | `NORMAL`, 1 attempt | `NORMAL`, 1 attempt |
| Native read/write tool path | Reached read and authorized write | Did not produce the first native tool call |
| Worker-created file | One new allowed test | None |
| Positive case | PASS | Not implemented |
| Negative case | FAIL: changed both identities | Not implemented |
| Independent final class | Worker capability failure | **Tool-calling failure** |
| Same-task elapsed | Not recorded in preserved qwen3 Evidence | 10.147933 s total |

The 14B model cannot be claimed more accurate than qwen3:8b on this benchmark.
qwen3:8b at least completed the bounded read/write protocol and implemented one
case correctly; the 14B model failed before semantic implementation. The older
qwen3 Evidence did not record same-task timing, so no valid speed ratio is
available. Results from unrelated qwen3 probes are not substituted.

## Practical Value on This PC

Under the unchanged Harness prompt, native Ollama tool schema, authority, and
timeouts, this exact 14B tag is not usable as the current bounded implementation
Worker. Its 10.15-second cold initial response is within the performance budget,
and the repaired GPU path is operational, but it consumes roughly 6.06 GiB of
8.15 GiB VRAM plus a 39% CPU-side allocation share and still fails the first
authority-bearing action.

The benchmark does not authorize prompt repair, alternate tool-call parsing,
architecture changes, timeout changes, or another model run. No claim is made
about non-tool generation use cases.

`GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
