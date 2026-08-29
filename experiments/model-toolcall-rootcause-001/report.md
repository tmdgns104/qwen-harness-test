# QH-V2-MODEL-TOOLCALL-ROOTCAUSE-001

## Status
UNSUCCESSFUL

Fixed direct Ollama and unchanged `OllamaToolSession` probes used identical prompt, tool schema, `think:false`, `stream:false`, and `num_ctx=8192`; no production code or policy changed.

| Model | Direct Initial | Direct Continuation | Harness Initial | Harness Continuation | Native loop | Primary root cause | Confidence |
|---|---|---|---|---|---|---|---|
| qwen3:8b | NATIVE_TOOL_CALL | PLAIN_TEXT | native (1) | final plain text | No | multi-turn model/template behavior; no general adapter fault shown | Medium |
| qwen2.5-coder:14b | TEXT_JSON_IMITATION | N/A | none | N/A | No | model/template/parser protocol emission | High |
| mistral-nemo:12b | PLAIN_TEXT | N/A | none | N/A | No | model/template/parser protocol emission | High |
| command-r7b:7b | PLAIN_TEXT | N/A | none | N/A | No | model/template/parser protocol emission | High |

Initial elapsed (direct / Harness): qwen3 5.25/6.63s, qwen2.5 11.63/8.15s, Mistral 10.29/8.11s, Command 8.48/0.31s. No native call means continuation was not applicable for the last three. Qwen3 emits an initial native call in both paths, but this minimal probe did not prove a complete second native call. The adapter preserves assistant tool-call objects and sends `role=tool`, `tool_name`, and content; direct/Harness initial request structures match in roles/tools/options.

Mistral's prior 60-second full-task continuation timeout is not reproduced here because this minimal probe produced no initial call; it remains unresolved between full-task performance and multi-turn behavior. Quantization was not isolated; no A/B claim is justified.

Conclusion: qwen2.5, Mistral, and Command failures are upstream protocol emission failures; evidence does not justify changing Harness or converting text imitation. No prior benchmark verdict is overturned. Keep qwen3 only as a tightly supervised limited Worker; prefer Codex/API for contract-sensitive work. Next step requires separately approved continuation matrix with captured raw structures. GLOBALIZATION=NOT AUTHORIZED.
