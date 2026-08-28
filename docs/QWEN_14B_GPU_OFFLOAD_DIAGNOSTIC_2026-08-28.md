# Qwen 14B GPU Offload Diagnostic Evidence - 2026-08-28

## Disposition

- Benchmark state: **GPU OFFLOAD GATE PASSED / READY TO RESUME**
- Observed run classification: **CPU-only diagnostic evidence**
- Model performance verdict: **NOT EVALUATED / NO FAIL RECORDED**
- Resume gate: **PASSED** after repair; the same model and context now show
  non-zero GPU offload.

This note does not change Worker policy, model authority, Harness Architecture,
or Globalization authorization.

## Interrupted observation

The active process was the interactive command:

`ollama run qwen2.5-coder:14b-instruct-q3_K_S`

Immediately before interruption, `ollama ps` reported:

- model: `qwen2.5-coder:14b-instruct-q3_K_S`
- model allocation shown by Ollama: `10 GB`
- processor: `100% CPU`
- context: `16384`
- GPU use: `0%`

The exact client process was stopped and the model was unloaded. `ollama ps`
then returned no loaded model. The background Ollama server was left running.
No latency or throughput observed in this CPU-only state is eligible as model
performance Evidence.

## GPU offload diagnosis

### Host and model

- GPU: NVIDIA GeForce RTX 5070 Laptop GPU
- NVIDIA driver: `610.71`
- reported VRAM: `8151 MiB`; `7891 MiB` free after model unload
- Ollama: `0.33.1`
- model: Qwen2.5 Coder 14.8B, `Q3_K_S`
- GGUF model tensor file: `6.20 GiB`
- configured context: `16384`
- CPU-only KV cache observed in the loader log: `3072 MiB`

The GPU and driver are visible to `nvidia-smi`. The following process-level
overrides were unset: `OLLAMA_LLM_LIBRARY`, `OLLAMA_NUM_GPU`,
`OLLAMA_MAX_VRAM`, `OLLAMA_GPU_OVERHEAD`, `CUDA_VISIBLE_DEVICES`,
`GGML_CUDA_FORCE_MMQ`, and `GGML_CUDA_FORCE_CUBLAS`.

### Ollama runtime selection Evidence

The Ollama server log records the decisive runtime state:

- server startup at `2026-08-28T19:34:10+09:00` began GPU discovery;
- discovery registered only the CPU inference backend;
- total detected VRAM was `0 B`;
- the 14B load used `reason=cpu` and a CPU-only `llama-server` command;
- the model buffer (`6345.39 MiB`), KV cache (`3072 MiB`), and compute buffer
  (`274.02 MiB`) were all allocated on the host.

A standalone child-process diagnostic with the installed base and `cuda_v12`
directories on `PATH` returned:

```text
Available devices:
  (none)
EXIT=0
```

### Incomplete CUDA payload Evidence

The Ollama automatic upgrade log opened at
`2026-08-28T19:31:14+09:00` and ends during installation of
`cuda_v12/cublasLt64_12.dll`, without a normal setup-completion record.

The installed `cuda_v12` directory contains only:

- `concrt140.dll`
- `cublas64_12.dll`
- `is-AJI2GWYF9M.tmp` (an installer temporary file)

The GPU backend/runtime payload is therefore incomplete; in particular the
installed directory has no `ggml-cuda.dll`, `cublasLt64_12.dll`, or
`cudart64_12.dll`. The original installer executable is no longer present and
no installer process remains active.

## Conclusion

Diagnostic classification: **GPU_RUNTIME_INSTALL_INCOMPLETE**.

The observed 100% CPU execution is explained by Ollama starting with no usable
GPU backend after an incomplete update. It is not valid Evidence of the
model's GPU-offloaded latency, throughput, correctness, or production fitness.
The model performance result remains open.

The required recovery path was to repair the Ollama installation from an
official distribution, restart the server, and verify the following under the
benchmark's actual execution environment:

1. server startup registers the RTX 5070 as an NVIDIA/CUDA inference device;
2. `ollama ps` for this model reports non-zero GPU offload;
3. `nvidia-smi` shows Ollama/llama-server VRAM allocation;
4. the benchmark uses the intended unchanged model and context, with the
   actual offload split recorded before timing begins.

## Repair and post-repair verification

The official Windows installer was downloaded from
`https://ollama.com/download/OllamaSetup.exe` and verified before execution:

- size: `1565341264` bytes
- product/file version: `0.33.1`
- Authenticode: `Valid`
- signer: `Ollama Inc.`
- SHA-256:
  `5065F5C3D9D50C2039E070A637E373DAE8310D4E7CDB80443AF832568E7B812B`

The repair log records `Installation process succeeded`, no Windows restart
required, and a normal closed log. The repaired installation contains complete
`cuda_v12` and `cuda_v13` backends. Ollama selected `cuda_v13` for this RTX
5070.

Post-repair server discovery at `2026-08-28T23:31:52+09:00` registered:

- library: `CUDA`
- compute capability: `12.0`
- device: NVIDIA GeForce RTX 5070 Laptop GPU
- driver exposed to Ollama: `13.3`
- total VRAM: `8.0 GiB`; available at discovery: `6.8 GiB`

A bounded smoke request, `Reply with OK only.`, then loaded the unchanged model
at context `16384`. This request was only an offload verification and its
24.416-second cold load plus generation time is not benchmark Evidence.

Actual load Evidence:

- `ollama ps`: `39%/61% CPU/GPU`
- loader log: `offloaded 30/49 layers to GPU`
- CUDA model buffer: `3882.02 MiB`
- host model buffer: `2463.37 MiB`
- CUDA KV cache: `1856.00 MiB`
- CPU KV cache: `1216.00 MiB`
- CUDA compute buffer: `164.02 MiB`
- `nvidia-smi`: `llama-server.exe` present and total GPU memory use
  `6038 MiB`

The offload resume gate is therefore **PASS**. A standalone direct
`llama-server --list-devices` invocation was not used as a gate because it does
not reproduce Ollama's internal backend-selection environment; the actual
Ollama server discovery and model load are authoritative for this benchmark.

The performance benchmark may now resume under the recorded 39% CPU / 61% GPU
condition. No model performance PASS or FAIL has been recorded by this
diagnostic, and the earlier CPU-only observation remains excluded from model
performance evaluation.
