# TPOS-V016-MODEL-003-COMMAND-R7B

## Verdict
**FAIL — TOOL_CALLING**

First response was ordinary explanatory text with zero native ToolRequests; no ToolResult, continuation, or write occurred. Harness NORMAL is not a pass.

Canonical MODEL-001 input was reused unchanged (task `b4ea3b067e897da23b7ef6f2f61f75daf677ecae081bc30d751e7b255c56c7a0`, brief `cd5f861fce3288d68edde4850d61c73677e7e5b9c5ca7252c1b9f8c0eb545081`). Model digest `ff4e9696ef9f19b62e3f7d7261c95dcc9bb15a7c0398493366d851119fe2e1ef`, Q4_K_M, 5,057,031,198 bytes (4.71 GiB), Ollama context 8192. `ollama ps`: 100% GPU; nvidia-smi 5774/8151 MiB used/total. Initial 7.928364s; total 7.930260s; attempts 1; no changed paths; no scope violation.

Codex verification: positive/negative probes PASS, exact conflict `requirements.REQ-HUMAN-001`, identity `ref`, full regression 64/64 PASS, target/original unchanged. Raw SHA256 `caca08aa1e8138eec4ce21f79ade6b078cf4e72ac150a1cef6c6e6d762616c6`.

| Model | Result | Observation |
|---|---|---|
| qwen3:8b | FAIL — WORKER_CAPABILITY | Native path, negative semantics wrong |
| qwen2.5-coder:14b | FAIL — TOOL_CALLING | JSON text instead of native request |
| mistral-nemo:12b | FAIL — TOOL_CALLING | Retry used `[TOOL_CALLS]` imitation |
| command-r7b:7b | FAIL — TOOL_CALLING | No native request initially |

No practical bounded Worker was found. Keep qwen3 only for tightly supervised, independently verified limited tasks; prefer Codex/API for contract-sensitive work and end this candidate search for now. GLOBALIZATION remains NOT AUTHORIZED.
