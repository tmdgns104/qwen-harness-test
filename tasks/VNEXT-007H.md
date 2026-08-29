# VNEXT-007H — Bounded Candidate Protocol Hardening

## Status

COMPLETE - VERIFIED

## Baseline

Baseline: 9fbadebf87c3c02c56bc37f3654170ec76a6718

## Goal

Compare the current bounded adapter with an explicit output prompt and Ollama
JSON Schema structured output for Qwen3:8B. Preserve strict parsing and all
existing authority and safety boundaries.

## Allowed Changes

- `tools/ollama_worker.py`
- `tests/test_bounded_ollama_worker.py`
- `tasks/VNEXT-007H.md`
- `STATUS.md`
- `experiments/vnext-007h/probe.py`
- `experiments/vnext-007h/result.json`
- `experiments/vnext-007h/rerun.py`
- `experiments/vnext-007h/rerun_result.json`
- `experiments/vnext-007h/report.md`

## Forbidden Changes

- Native Agent, strict parser semantics, Candidate Validator
- Retry policy, production timeout, authority boundaries
- VNEXT-008 and unrelated files

## Verification

Run:

`python -m unittest discover -s tests -p "test_bounded_ollama_worker.py"`

Then run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_context_pack tests.test_candidate_validator tests.test_candidate_apply tests.test_bounded_verification tests.test_harness_core tests.test_ollama_worker -q`

Then run:

`git diff --check`
