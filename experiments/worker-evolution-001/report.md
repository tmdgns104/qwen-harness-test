# Local Worker Evolution Experiment 001

## Scope

Research-only experiment; official VNext Tasks and Architecture were not modified. Model: `qwen3:8b`, `think:false`, `temperature=0`, `seed=424242`, `num_ctx=8192`, Direct Ollama `/api/chat`, no tools. Candidate operations were applied only to temporary synthetic fixtures and tested independently.

## Hypotheses and benchmark

H1: explicit acceptance/allowed scope/tests and complete source context improve correctness versus a minimal source-only prompt. H2: deterministic structured JSON Candidate output is measurable and safe. Three tasks were used: single-file whitespace function, existing parser bug fix, and multi-file function+tests. Each variant ran twice with identical fixed settings.

| Task | Minimal | Rich Context + acceptance/tests | Mean response seconds (minimal/rich) |
|---|---:|---:|---:|
| single-function | 2/2 | 2/2 | 5.22 / 0.83 |
| bug-fix | 0/2 | 2/2 | 1.62 / 3.96 |
| multi-file | 0/2 | 0/2 | 1.30 / 0.90 |
| **Total** | **2/6 (33.3%)** | **4/6 (66.7%)** | **2.71 / 1.90** |

All successful candidates were parsed as structured JSON and passed the temporary fixture tests. The original report incorrectly summed Minimal as 4/6; raw `result.json` shows 2/6 (single-function 2/2, bug-fix 0/2, multi-file 0/2). Rich context achieved 4/6 (66.7%). Multi-file work remained unsuccessful; the sample is intentionally small and exploratory.

## Hardware and bottlenecks

During/after the run `ollama ps` reported qwen3:8b at 100% GPU, context 8192, 6.2 GB resident; `nvidia-smi` reported 6078 MiB / 8151 MiB. Primary bottleneck is semantic multi-file planning/candidate fidelity, not transport. Prompt/context completeness affected one task; latency varied and should not be optimized ahead of correctness.

## Recommendation

Adopt rich, provenance-preserving Context Packs with explicit acceptance criteria, allowed paths, relevant tests, and a strict structured Candidate contract as the next experiment baseline. Keep deterministic Harness validation and temporary apply; never promote text imitation or Worker self-report. Add bounded critic/revision only as a separate A/B experiment with the same task set. Do not change official Architecture or mark any VNext Task complete from this result.

Full raw inputs, candidates, evaluations, hashes, and elapsed timings: `result.json`. Experiment script: `experiment.py`.
