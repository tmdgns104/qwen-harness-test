# Local Worker Evolution Experiment 002

## Experiment 001 correction

Raw `result.json` contains six Minimal rows: single-function 2/2, bug-fix 0/2, multi-file 0/2, therefore **2/6 (33.3%)**. Rich is 4/6 (66.7%). The previous aggregate Minimal 4/6 was incorrect. Correction recorded separately in commit `16b4bd7`; prior commits were not rewritten.

## Design

Qwen3:8B, `think:false`, `temperature=0`, seed `424242`, `num_ctx=8192`, structured Candidate JSON, isolated temporary fixtures. Five distinct tasks covered single-file, existing-test bug fix, semantic boundary bug, multi-file implementation, and coordinated source/test/caller change. Conditions: A rich Context single pass; B rich Context plus one self-review candidate pass; C rich Context plus at most one failure-evidence revision. Each task/condition was run once; repeated identical runs were not counted as independent correctness samples. No C revision was needed because all first passes passed.

## Results

| Condition | First-pass correct | Final correct | Recovery | Mean inference latency |
|---|---:|---:|---:|---:|
| A Single Pass | 5/5 (100%) | 5/5 (100%) | N/A | 3.34s |
| B Self Review | 5/5 (100%) | 5/5 (100%) | 0/0 | 1.55s (review response) |
| C Failure Revision | 5/5 (100%) | 5/5 (100%) | 0/0 failures | included no revision |

Multi-file/ coordinated subset: A 2/2, B 2/2, C 2/2. Because no first-pass failure occurred, this experiment cannot estimate revision recovery rate or prove self-review causality. The observed B latency is not directly comparable to A total workflow latency because the self-review call was not needed for final correctness in this run.

## Failure analysis and limitations

No deterministic test failure occurred. Candidates were structured and temporary tests passed. Candidate outputs sometimes replaced test files; this was allowed by the synthetic coordinated-task definition but requires the future validator to detect weakening rather than trusting green tests. The five-task sample is too small to claim general coding capability, and no dependency-aware decomposition experiment was mixed into A/B/C.

Hardware after run: qwen3:8b, 100% GPU, context 8192, 6080/8151 MiB VRAM. No model or production Harness change.

## Recommendation

Continue Qwen3:8B as the practical baseline. Use rich provenance-preserving Context as default and retain structured Candidate plus deterministic temporary verification. Do not yet adopt self-review or failure revision as proven accuracy improvements; run a larger failure-seeded benchmark where revision is actually exercised. Dependency-aware decomposition is worth a separate experiment only if multi-file failures persist under that benchmark. No official Architecture or Task should be changed from this evidence.
