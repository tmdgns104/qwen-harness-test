# QH-V2-MODEL-PROTOCOL-CAPABILITY-002

## Status
UNSUCCESSFUL

All probes used one fixed prompt/schema, Direct Ollama only, `stream:false`, `num_ctx=8192`, no production changes. Five default runs and five `temperature=0, seed=424242` runs were collected per model; `think=false/true` was sampled once each.

| Model | Default 5x | Fixed 5x | think=false / true | qwen3 multi-turn |
|---|---|---|---|---|
| qwen3:8b | 5 native | 5 native | native / native | single 5/5; two-read 0/5; read-write 0/5 |
| qwen2.5-coder:14b-instruct-q3_K_S | 5 JSON imitation | 5 JSON imitation | JSON / ERROR | N/A |
| mistral-nemo:12b-instruct-2407-q3_K_S | 5 plain text | 5 plain text | plain / ERROR | N/A |
| command-r7b:7b-12-2024-q4_K_M | 5 plain text | 5 plain text | plain / ERROR | N/A |

Exact artifact `/api/show` metadata: qwen3 family `qwen3`, Q4_K_M, capabilities `completion, tools, thinking`; qwen2.5 family `qwen2`, Q3_K_S, `completion, tools, insert`; Mistral family `llama`, Q3_K_S, `completion, tools`; Command family `cohere2`, Q4_K_M, `completion, tools`. `ollama show --modelfile` indicated tool-aware templates for all four (template hashes and previews are in `result.json`). Thus all advertise tools; advertising capability does not imply reliable emission.

## Root-cause assessment

qwen2.5, Mistral, and Command failures reproduce in Direct Ollama, so they are not explained by Harness serialization. Their exact tags/templates/parser-rendering or model tool training are primary suspects. Mistral's historical native call is consistent with behavior outside this fixed prompt, but this matrix found no nondeterminism (5/5 plain). qwen3 is deterministic for one tool (5/5 in both matrices), while multi-turn scenarios failed after the first call (0/5), so it is not a general multi-step guarantee. `think=true` was rejected by the three non-qwen3 models; qwen3 remained native. Quantization is only correlational and was not isolated.

No prior benchmark verdict is overturned. No adapter fix, parser fallback, timeout change, prompt tuning, model install, or fine-tuning was performed. Follow-up should capture raw renderer/parser traces for qwen3 multi-turn and test a separately approved compatible template/config; do not infer that Q3 alone is causal.
