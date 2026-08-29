# VNEXT-007E Evidence

Twelve synthetic tasks used exact fixture paths, writable source files, a
read-only visible-test context item, and an independent verifier rule. The
official ContextPack, hardened bounded adapter, strict parser, Validator,
isolated apply, and BoundedOutcome verifier were used.

| Stage | Result |
|---|---:|
| Transport | 12/12 |
| Strict parse | 12/12 |
| Validator | 11/12 |
| Snapshot apply | 1/12 |
| Visible verification | 1/12 |
| Independent verification | 1/12 |
| Final COMPLETED | 1/12 |

The one completed task passed valid Candidate, exact path comparison, isolated
apply, visible verification, independent verification, and original-repo
invariance. The other ten validator/apply failures were preserved as failures;
no Candidate was repaired or promoted. Overall semantic correctness was
therefore 1/12 (8.3%); single-file and multi-file correctness are reported in
the per-task rows and are not generalized from this small synthetic sample.

Safety counters were all zero: malformed promotion, read-only path Candidate,
scope-violating apply, original mutation, visible-pass/hidden-fail, and false
COMPLETED. This validates the fail-closed gate, but correctness is below the
70% limited-pilot signal and VNEXT-008 is not recommended.

Mean/median inference latency was 1.426/1.321 seconds; end-to-end was
1.435/1.333 seconds. Hardware/model settings were Qwen3:8B, 8192 context,
think=false, temperature 0, seed 424242; raw hardware state is retained in
`result.json` where available.

