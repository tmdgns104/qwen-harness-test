# VNEXT-007 — Synthetic Bounded Worker Benchmark

## Task Status

ACTIVE

Ten distinct synthetic Tasks were sent through the unchanged official bounded adapter: ContextPack → BoundedWorkerRequest → Qwen3:8B → strict parser → validator. No retry, repair, tools, apply, or verification fallback was used.

## Funnel

| Stage | Count | Rate |
|---|---:|---:|
| Total Tasks | 10 | 100% |
| Ollama transport OK | 10 | 100% |
| Strict Candidate parse OK | 0 | 0% |
| Candidate validation PASS | 0 | 0% |
| Snapshot apply PASS | 0 | 0% |
| Visible verification PASS | 0 | 0% |
| Independent verification PASS | 0 | 0% |
| Final `COMPLETED` | 0 | 0% |

All ten failures were `CANDIDATE_PARSE`. Seven responses were non-JSON explanatory text; three reached JSON-like content but failed the strict operation schema. No Candidate reached validator or snapshot application, so no correctness claim can be made.

## Runtime

Qwen3:8B, `think=false`, `temperature=0`, seed `424242`, `num_ctx=8192`, 100% GPU. Inference mean 1.628s, median 1.531s. Context Pack content was 89 characters per task; serialized context request was approximately 220 characters. Candidate response sizes and token usage were not available from the adapter metadata. Ollama runtime after execution reported qwen3:8b at 6.2GB and NVIDIA memory approximately 6.1GB / 8.15GB.

## Experiment 006 comparison

The official adapter smoke and this benchmark both fail strict parsing. Worker Evolution Experiments 001–003 used a stronger prompt containing an explicit `Return ONLY JSON` Candidate contract plus full source/test content; those experiment prompts are not the official adapter's current request serialization. This is an evidence-level prompt/task representation difference, not proof that parser relaxation or a production adapter change is safe. The adapter correctly preserves transport success separately from parse failure.

## Judgment

Operational transport is reliable, but official Candidate Protocol Reliability is 0/10 and official E2E correctness is 0/10. The dominant bottleneck is structured output emission under the current bounded request representation. VNEXT-008 Team Project OS pilot is not recommended. A separately approved prompt/serialization hardening benchmark is required; do not loosen parsing, add repair, retry, or modify the official adapter in this Task. Qwen3:8B remains a useful hardware baseline, but not yet an operational bounded coding Worker through this official path.
