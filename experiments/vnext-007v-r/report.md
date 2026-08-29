# VNEXT-007V-R Evidence

Audited A/B semantic benchmark: 12 tasks each, with broken-baseline and
reference-integrity checks, complete Candidate content, and executed Python
behavior assertions.

| Condition | Inference | Validator | Apply | Independent PASS | Completed | Mean inference | Mean E2E |
|---|---:|---:|---:|---:|---:|---:|---:|
| A think=false baseline | 12 | 11 | 9 | 5 | 5 | 2.248 s | 2.259 s |
| B specification-first | 12 | 8 | 4 | 1 | 1 | 1.552 s | 1.560 s |
| C think=true probe (3 tasks) | 3 | see result | see result | see result | see result | see result | see result |

A applied semantic correctness was 5/9 (55.6%); B was 1/4 (25%). C was only
the required three-task bounded probe and its per-task evidence is retained in
`result.json`; it must not be generalized. Failures were classified as
validator/apply precondition or `WRONG_LOGIC` when Python behavior assertions
failed. No Candidate was repaired and no retry was used.

Fixture integrity checks passed for all executed tasks: broken baseline failed
and the reference behavior passed before Worker inference. Safety counters:
False COMPLETED 0 and original repository mutation 0.

The specification-first prompt did not improve this sample. Qwen3:8B remains
usable only for bounded, independently verified small tasks; VNEXT-008 is not
recommended. The evidence does not justify changing official retry or parser
semantics.

