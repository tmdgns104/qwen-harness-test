# TP-OS-SHADOW-001D3 Evidence

All three conditions used identical Full Source + relevant-test Context
(16,617 characters of source/test material). Only output contract changed.

| Condition | Request chars | Wall latency | Prompt eval | Eval/generation | Output chars | Result |
|---|---:|---:|---:|---:|---:|---|
| A decision-only | recorded in result | 3.066 s | 1.384 s | 1.120 s | 225 | structured complete |
| B changed-function | recorded in result | 10.250 s | 0.018 s | 10.177 s | 2,429 | structured complete |
| C full-file Candidate | recorded in result | 60.010 s | unavailable | unavailable | 0 | diagnostic timeout |

The same Full Source prompt is therefore not by itself sufficient to explain
the latency: A completed quickly. Generation output size and contract appear
to dominate B, while C's full-file generation exceeded the bounded diagnostic
window. Ollama reported `prompt_eval_count=4009` for A/B and model load around
7–8 ms, so cold model loading is not the primary observed cause.

This supports `FULL_FILE_GENERATION_COST` as the leading hypothesis for the
30-second Shadow failure, with structured-output interaction still unproven
for C because it timed out. No production timeout, CandidateOperationType,
parser, validator, retry, or authority was changed. A bounded partial-edit
operation such as `REPLACE_TEXT` is a reasonable follow-up proposal, not an
implementation in this task.

