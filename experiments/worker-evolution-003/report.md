# Local Worker Evolution Experiment 003

## Scope and settings

Research-only; official VNext Architecture/Tasks unchanged. Qwen3:8B, `think=false`, `temperature=0`, seed `424242`, `num_ctx=8192`, Rich Context, structured Candidate, and `validate_candidate()` against a single allowed source path. Twelve distinct synthetic Tasks covered None/empty input, boundaries, exception semantics, state, off-by-one, parsers, negative values, multi-file API, coordinated caller changes, and edge cases. Worker-visible tests were separate from hidden independent checks; hidden tests and test paths were not supplied to the Worker.

## Results

| Metric | Result |
|---|---:|
| Task count | 12 |
| First-pass PASS | 9/12 (75.0%) |
| First-pass FAIL | 3/12 |
| Revision attempted | 3 |
| Revision recovered | 1/3 (33.3%) |
| Final PASS | 10/12 (83.3%) |
| Hidden-test correctness first pass | 9/12 (75.0%) |
| Hidden-test correctness after revision | 10/12 (83.3%) |
| Multi-file/coordinated first pass | 2/3 (66.7%) |
| Multi-file/coordinated final | 2/3 (66.7%) |
| Candidate validator rejection | 0/12 |

Failures were visible-test failures for `off-by-one`, `coordinated`, and `multi-api`. One `multi-api` revision recovered; `off-by-one` revision passed visible tests but still failed hidden edge semantics; `coordinated` remained failed. Failure Evidence was bounded to test result/category, candidate path summary, and no repository-wide context.

## Latency and hardware

Initial inference mean 1.121s, median 0.792s. Revision inference mean 0.795s; failed-task end-to-end mean (initial + revision) 1.618s. qwen3:8b remained 100% GPU at context 8192; VRAM 6080/8151 MiB after the run. Revision adds roughly one extra inference only for failures, but this run did not measure a matched A control rerun, so causal latency comparison is limited.

## Test mutation and safety

No Candidate included a test path because the allowed scope was source-only; validator rejected any out-of-scope test operation by policy. This demonstrates boundary enforcement, not semantic test-weakening detection. Hidden tests caught the remaining edge-case failure and prevented visible-test success from being treated as sufficient.

## Judgment

Qwen3:8B is a viable first-pass baseline for bounded small tasks (75% on this deliberately harder set). One bounded Failure Evidence revision raised final correctness to 83.3%, but recovery was only 33.3% and multi-file correctness did not improve. The result supports a proposal to study bounded revision, not an official retry-policy change. Next experiment should use failure-seeded tasks, preserve hidden verifiers, and compare full end-to-end cost against a single-pass control. Dependency-aware decomposition remains a separate hypothesis. No larger model was compared and no official Architecture was changed.
