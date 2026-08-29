# VNEXT-007R Hardened Bounded E2E Revalidation

## Benchmark

Twelve distinct synthetic tasks were run with Qwen3:8B, `think=false`,
temperature 0, seed 424242, and `num_ctx=8192`. Context Packs contained goal,
acceptance criteria, allowed/forbidden paths, provenance-preserving source and
visible-test items, and the strict Candidate output contract.

## Funnel

| Stage | Result |
|---|---:|
| Total | 12 |
| Transport OK | 12/12 |
| Strict parse OK | 12/12 |
| Validator PASS | 2/12 |
| Snapshot apply PASS | 0/12 |
| Visible verification PASS | 0/12 |
| Independent verification PASS | 0/12 |
| Final COMPLETED | 0/12 |

The hardened protocol reliability was therefore 100% (12/12 transport-success
responses parsed strictly). Only two candidates passed the declared scope
validator; the synthetic repository did not contain the model-selected target
files, so no candidate was applied or marked completed. No malformed candidate
was promoted, no scope-violating candidate was applied, no original repository
mutation occurred, and false COMPLETED was zero.

The run is protocol and pipeline evidence, not a correctness PASS: independent
verification was not reached, so overall, single-file, multi-file, and hidden
edge correctness are 0 reached/0 passed (UNVERIFIED rather than evidence of
semantic inability). This also shows that strict protocol reliability alone
does not establish usable task correctness; context/fixture alignment and
independent verification remain required.

## Latency and hardware

Mean inference was 1.459 s (median 1.055 s); mean end-to-end was 2.078 s
(median 1.602 s). Context/request sizes are recorded per task in
`result.json` (`context_chars` and `request_chars`); they are not token counts.
The run used Qwen3:8B with 8192 context. Hardware snapshots in `result.json`
show the local Ollama/GPU state; no original repository files were changed.

## Gate decision

Protocol hardening is confirmed and the safety counters meet zero-promotion and
zero-mutation requirements. However, the final correctness gate is not met and
VNEXT-008 Team Project OS Pilot is **not recommended yet**. A follow-up should
use real isolated synthetic fixture files and approved independent tests so
apply, visible, and hidden verification stages can be measured; this task did
not add retry, parser fallback, or architecture changes.

