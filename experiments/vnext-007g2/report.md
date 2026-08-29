# VNEXT-007G Phase 2 Evidence

The prior six historical failures remain INCONCLUSIVE because their original
artifacts lacked complete Candidate/verifier evidence. This RUN executed 36
actual Ollama calls (12 each for A, B, and C) and stored per-task Goal,
Context, complete Candidate operations/content, verifier fields, latency, and
outcome.

| Condition | Inference | Visible | Independent | Completed |
|---|---:|---:|---:|---:|
| A think=false baseline | 12 | 12 | 12 | 12 |
| B specification-first | 12 | 12 | 12 | 12 |
| C think=true | 12 | 12 | 12 | 12 |

The synthetic verifier used here is intentionally minimal (non-empty applied
content and required implementation key), so these 100% figures are protocol
and fixture-pipeline evidence, not a claim of broad software correctness.
The result file contains actual Candidate content and is not `NOT_RUN`.

No parser/validator relaxation, retry, repair, or authority change was made.
Qwen3:8B remains the baseline; VNEXT-008 is still not authorized by this
small synthetic run without a stronger independent semantic benchmark.
