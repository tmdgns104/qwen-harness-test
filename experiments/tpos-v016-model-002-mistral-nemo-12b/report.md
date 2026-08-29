# TPOS-V016-MODEL-002-MISTRAL-NEMO-12B Evidence

## Final Disposition

**FAIL — TOOL_CALLING**

The first attempt produced one genuine native `read_repo_text` ToolRequest and
received its ToolResult, but the continuation exceeded the unchanged 60-second
timeout. The normal bounded retry then emitted a `[TOOL_CALLS]` description as
ordinary text with zero native ToolRequests. No regression test was written, so
the complete native protocol was not reliable.

The timeout is recorded separately as a performance observation. No timeout,
prompt, parser, fixture, Harness, Architecture, or authority change was made.

## Frozen Input and Isolation

MODEL-001 canonical input was reused without modification:

- Task source commit: `748b77391f2b545e75943f1fefeb9f18277c446f`
- prior qwen3 failure Evidence: `30e762d28597cdedcaf3d2176d1cc4a28e2d83c7`
- Task SHA-256: `b4ea3b067e897da23b7ef6f2f61f75daf677ecae081bc30d751e7b255c56c7a0`
- Worker Brief SHA-256: `cd5f861fce3288d68edde4850d61c73677e7e5b9c5ca7252c1b9f8c0eb545081`
- canonical paths: `experiments/tpos-v016-model-001-qwen25-coder-14b/canonical/`

The isolated target was `%LOCALAPPDATA%\Temp\TPOS-V016-MODEL-002-MISTRAL-NEMO-12B-20260829-094851\target-run`, clean at `748b773`, with the required output test absent. The original `D:\team_project_os\team_project_os-main` status was identical before and after. MODEL-001 files and results were not modified.

The existing `run_single_task(..., session_factory=...)` seam selected only the
runtime model. `think:false`, 30-second initial timeout, 60-second continuation
timeout, eight Worker steps, two Retry attempts, tool schema, authority, and
ChangeScope remained unchanged. GLOBALIZATION remains NOT AUTHORIZED.

## Model and Hardware

| Measurement | Result |
|---|---|
| Exact tag | `mistral-nemo:12b-instruct-2407-q3_K_S` |
| Ollama ID / digest | `5bba7a13afefd3f2f58abe383c4f775d9238e0b4f2c24e56b72b33290fef719d` |
| Parameters / quantization | 12.2B / `Q3_K_S` |
| Model disk size | 5,534,238,669 bytes (5.154 GiB; list display 5.5 GB) |
| Ollama allocation | 8.4 GB |
| Actual context | 16,384 |
| `ollama ps` PROCESSOR | `26%/74% CPU/GPU` |
| GPU offload | 31/41 layers |
| CUDA / host model buffers | 3,877.75 / 1,392.58 MiB |
| `nvidia-smi` after run | 6,110 MiB used / 8,151 MiB total; 1,782 MiB free |
| GPU / driver / Ollama | RTX 5070 Laptop GPU / 610.71 / 0.33.1 |

The PROCESSOR value is allocation, not sustained CPU utilization. The post-run
GPU utilization snapshot was 0% and is not treated as a workload average.

## Harness Timing and Tool Trace

Run window: `2026-08-29T00:48:59.115837+00:00` to
`2026-08-29T00:50:14.818698+00:00`.

Attempt 1:

- initial response: 9.173129 seconds
- one native `read_repo_text` request for `app/structured_state_v016.py`
- ToolResult delivered successfully, 16,036 characters
- continuation: 60.014106 seconds, `TimeoutError: timed out`
- Runner result: `TRANSIENT_WORKER`, no write

Attempt 2 (unchanged bounded retry):

- initial response: 6.510767 seconds
- native ToolRequests: zero
- ordinary output: 428 characters beginning `[TOOL_CALLS]`
- output described the same read action in Markdown/JSON text
- Runner result: `NORMAL`, no write

Total wall-clock: 75.702831 seconds. Harness summary: `NORMAL`, 2 attempts,
Failure Kind `NONE` (the first transient was retried), Write Side Effect Risk
`NO`. Worker-created/changed paths: none. Scope violation: no.

The model’s second response was not reinterpreted as an authority-bearing tool
call. Raw result SHA-256:
`be388923c8e7e2b2e4256646445775ac906ad4f873f1cfa4cf867cdbc8551a12`.

## Independent Codex Verification

Direct execution of the canonical production fixture passed both cases without
writing a test file:

- positive: `['requirements.REQ-HUMAN-001']`
- negative: `[]`
- stable identity: `ref`, not `id`
- expected path: `requirements.REQ-HUMAN-001`
- fixture semantics: PASS

The Worker-generated regression test is absent; Worker positive and negative
cases are therefore not implemented. The exact generated-test module command
exited 1 because the module is absent. The exact V0.16 dotted-module command
also exited 1 because this Python environment’s installed `tests` package
shadowed the repository namespace; the discovery diagnostic ran the V0.16 file
successfully 10/10. Full isolated discovery passed 64/64.

Target `git diff --check` passed; target status and changed paths were empty.
No production file, existing test, or original Team Project OS file changed.
The generated-test compile command printed `Can't list`; its incidental exit 0
was not treated as a pass. Harness focused checks passed 62/62; both benchmark
scripts compile and all JSON artifacts parse.

Verification result SHA-256:
`ede3c0c773818f1d0d2bdadaa95290f78c653774d45dc7736025dc96b210baca`.

Harness `NORMAL` was not treated as Task PASS.

## Three-Model Comparison

| Criterion | qwen3:8b | qwen2.5-coder:14b | mistral-nemo:12b |
|---|---|---|---|
| Final result | `FAIL — WORKER_CAPABILITY` | `FAIL — TOOL_CALLING` | **`FAIL — TOOL_CALLING`** |
| Native protocol | Read/write completed | No native first call | Native read once; continuation timeout; retry text imitation |
| Positive / negative | PASS / wrong negative fixture | Not implemented / not implemented | Not implemented / not implemented |
| Harness | NORMAL, 1 attempt | NORMAL, 1 attempt | NORMAL, 2 attempts |
| Same-task time | Not recorded | 10.147933s | 75.702831s |
| GPU allocation | Not recorded | 39%/61%, 30/49 layers | 26%/74%, 31/41 layers |

Mistral Nemo shows stronger first-step native behavior than MODEL-001, but it
does not complete the bounded continuation and falls back to non-native text.
It does not improve deterministic accuracy or contract completion. qwen3:8b
remains the only control that completed read/write, although its negative case
was wrong. No qwen3 same-task timing was preserved, so no speed ratio is claimed.

## Practical Value

Under the unchanged Harness, Mistral Nemo is not suitable as the bounded
implementation Worker. It fits the repaired GPU environment at context 16384,
but uses a 60-second continuation budget without completing it and then fails to
emit native tool calls on retry. The 75.7-second result is not a usable one-shot
Worker. No claim is made about non-tool generation use cases.
