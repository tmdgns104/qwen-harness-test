# VNEXT-007 — Synthetic Bounded Worker Benchmark

## Status
APPROVED - READY FOR CONTRACT BASELINE

## Goal

Measure the official bounded_stateless Qwen3:8B pipeline funnel on synthetic software-engineering Tasks without changing the adapter or adding retry.

## Architecture Basis

`docs/ARCHITECTURE-VNEXT.md`, ADR-019, and VNEXT-001 through VNEXT-006.

## Dependencies

VNEXT-006 completion commit `9269c8f9a864f857086cc6278eef4b0b9ba29205`.

## Scope

Experiment-only orchestration under `experiments/vnext-007/`; direct use of existing Context Pack, bounded adapter, validator, isolated apply, and verification contracts. Measure transport, strict parse, validation, apply, visible/independent verification, latency, sizes, and hardware metadata.

## Allowed Changes

- `experiments/vnext-007/`
- `tasks/VNEXT-007.md`
- `STATUS.md`

## Forbidden Changes

- `tools/**`, Native Agent, Adapter, parser, retry, self-review, model tuning
- Production timeout, Tool/Write Authority, Security Boundary
- `docs/**`, `DECISIONS.md`, VNEXT-008, Team Project OS, unrelated files

## Acceptance Criteria

- At least 10 distinct synthetic Tasks are measured with a deterministic funnel.
- Strict Candidate parsing remains unchanged; no repair or text promotion.
- Independent verifier is separate from Worker-visible tests.
- Results preserve stage failures, latency, request/response sizes, and hardware evidence.
- No official pipeline or Task semantics are changed.

## Verification

Run:

`python experiments/vnext-007/benchmark.py`

Then run:

`python -m py_compile experiments/vnext-007/benchmark.py`

Then run:

`git diff --check`

## Evidence Requirements

Record raw funnel results, stage classifications, latency statistics, context/request/response sizes, and pilot recommendation.

## Stop Conditions

Stop on any need to modify Adapter/parser, add retry, or connect Team Project OS.
