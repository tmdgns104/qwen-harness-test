# Worker Model Decision Benchmark

Installed candidates: qwen3:8b and qwen2.5-coder:7b (no model installed).
Target baseline: `3c05219d50a51f2bdad8e6671e702e8c5d575e50`; target mutation 0.

Four frozen bounded tasks were run once per model with identical REPLACE_TEXT
contract, context, schema, timeout, and no retry.

| Model | Samples | Semantic PASS | Parse | Validator | Apply | Avg latency |
|---|---:|---:|---:|---:|---:|---:|
| qwen3:8b | 4 | 1 (25%) | 4/4 | 4/4 | 4/4 | 10.61s |
| qwen2.5-coder:7b | 4 | 0 (0%) | 4/4 | 4/4 | 4/4 | 17.10s |

qwen3 completed the `_clip` scalar task. Its other three Candidates failed
semantic assertions. qwen2.5-coder:7b parsed and applied all four Candidates
but failed every independent semantic assertion. No syntax failures or
performance failures occurred in this run.

Target regression invocation was independently established as:
`python -m unittest discover -s tests -p "test_conversation.py" -q` (6 tests,
PASS) from the Target repository. This command was read-only and did not alter
the Target.

The model itself is the present capability bottleneck: protocol and safety
stages are stable, while semantic correctness is low for both models. qwen3:8b
remains the better local candidate by accuracy and latency, but it is not a
general-purpose coding Worker. Green routing is not established; bounded
single-file utility tasks are Yellow, semantic/multi-file tasks Red.

No official baseline, architecture, timeout, retry, authority, or
GLOBALIZATION state changed. VNEXT-008 remains not started.
