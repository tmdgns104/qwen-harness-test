# Local Worker Cascade Feasibility

Four frozen tasks used Coder 7B Profile first and an independent Qwen3:8B
fallback only after semantic failure. No failure evidence was passed between
workers; each stage used a fresh snapshot from Target baseline
`3c05219d50a51f2bdad8e6671e702e8c5d575e50`.

| Task | Coder 7B | Qwen3 fallback | Final | Total latency |
|---|---|---|---|---:|
| SHADOW-003R | FAIL | FAIL | FAIL | 37.1s |
| SHADOW-005 | FAIL | FAIL | FAIL | 37.8s |
| SHADOW-006 | FAIL | FAIL | FAIL | 37.0s |
| SHADOW-007 | FAIL | PASS | PASS | 38.5s |

Coder-only historical result: 1/4; Qwen3-only historical result: 1/4.
Cascade result: **1/4 (25%)**. Fallback was invoked 4/4 times and recovered
1/4. There is complementary recovery but no net accuracy gain on this frozen
set. Total latency is approximately the sum of both calls; model-switch cost
was not separately exposed and is included in timings.

Strict parsing, validation, isolated apply, and safety boundaries remained
intact. False COMPLETED and original Target mutation were both 0. No automatic
cascade Architecture change is justified; this remains a routing proposal.
