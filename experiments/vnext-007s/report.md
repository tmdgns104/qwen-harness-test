# VNEXT-007S Semantic E2E Evidence

Two sets of twelve distinct synthetic tasks were run with the frozen Qwen3:8B
configuration and target-state/write-authority contract. Fixture integrity
passed for every task: provenance paths, existing targets, read-only visible
tests, and independent verifier boundaries were checked before inference.

| Set | Transport | Parse | Validator | Apply | Visible | Independent | Completed |
|---|---:|---:|---:|---:|---:|---:|---:|
| A existing regression | 12/12 | 12/12 | 10/12 | 10/12 | 10/12 | 9/12 | 9/12 |
| B unseen generalization | 12/12 | 12/12 | 9/12 | 9/12 | 9/12 | 4/12 | 4/12 |

Applied-candidate semantic correctness was 9/10 (90%) for Set A and 4/9
(44.4%) for Set B. Overall completion was 13/24 (54.2%). Set B therefore
shows a substantial generalization gap; the Worker is not ready for the
VNEXT-008 pilot.

The independent verifier rejected one Set A visible-pass candidate and five
Set B visible-pass candidates. These were not marked `COMPLETED`. Safety
counters were all zero: malformed promotion, read-only path, scope-violating
apply, original mutation, and false COMPLETED. Protocol and application
reliability were strong, but semantic correctness is the limiting stage.

Mean/median inference latency was 1.659/1.131 seconds and E2E latency was
1.667/1.141 seconds. Raw per-task context/request sizes and hardware metadata
are retained in `result.json` where available.

