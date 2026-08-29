# VNEXT-006 — Stateless Ollama Adapter

## Status
COMPLETE - VERIFIED

## Goal

Connect `BoundedWorkerRequest` to Qwen3:8B through a separate stateless Ollama adapter that returns a strict structured Candidate.

## Architecture Basis

`docs/ARCHITECTURE-VNEXT.md`, ADR-019, and VNEXT-001 through VNEXT-005.

## Dependencies

VNEXT-005 completion commit `05f17a47ec901d31aac119f852de582431835adc`.

## Scope

Implement bounded request serialization, no-tools Ollama call, strict Candidate JSON parsing, and transport/structured-response error separation.

## Allowed Changes

- `tools/ollama_worker.py`
- `tests/test_bounded_ollama_worker.py`
- `tasks/VNEXT-006.md`
- `STATUS.md`
- `experiments/vnext-006/report.md`

## Forbidden Changes

- Native Agent/OllamaToolSession semantics, tools, Worker authority, retry, inference orchestration
- Candidate validation/application, verification orchestration, model routing
- Production timeout, Tool Authority, Write Authority, Security Boundary
- `docs/**`, `DECISIONS.md`, VNEXT-007+, Team Project OS, unrelated files

## Acceptance Criteria

- Bounded request includes task/context/output contract in deterministic prompt serialization.
- Ollama payload has no native `tools` field and uses bounded model/options.
- Only strict JSON Candidate operations CREATE_FILE/REPLACE_FILE parse successfully.
- Malformed/schema/unsupported output fails closed while transport success remains distinguishable.
- Native adapter and all prior contracts remain compatible.

## Verification

Run:

`python -m unittest discover -s tests -p "test_bounded_ollama_worker.py"`

Then run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_context_pack tests.test_candidate_validator tests.test_candidate_apply tests.test_bounded_verification tests.test_harness_core tests.test_ollama_worker -q`

Then run:

`git diff --check`

## Evidence Requirements

Record request shape, parser cases, no-tools authority, smoke output, timing, and regressions.

## Stop Conditions

Stop if Native Agent behavior, production policy, or Worker authority must change.
