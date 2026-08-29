# VNEXT-006 — Stateless Ollama Adapter

## Task Status

ACTIVE

Added `call_bounded_stateless_worker()` in `tools/ollama_worker.py`. It serializes `BoundedWorkerRequest` as stable JSON containing task/context/output contract, sends `stream:false`, `think:false`, fixed `num_ctx=8192`, temperature/seed, and deliberately omits native `tools`. Response parsing is strict: only an object containing an operations list with exact CREATE_FILE/REPLACE_FILE operation fields becomes a VNEXT-001 `Candidate`. No markdown repair, text imitation promotion, scope validation, apply, or retry is performed.

Transport failures return `transport_ok=False`; HTTP/Ollama success with malformed or unsupported Candidate returns `transport_ok=True`, `candidate=None`, and `parse_ok=False` metadata.

Focused adapter tests: 4/4 PASS. VNEXT-001 through VNEXT-005 plus existing `tests.test_ollama_worker`: 153 tests PASS (1 existing symlink capability skip). `git diff --check`: PASS. Actual Qwen3:8B smoke call completed transport successfully in 6.221s but returned non-JSON explanatory text, so parsing failed closed; no filesystem/tool access or Candidate apply occurred. Ollama baseline during smoke: qwen3:8b 100% GPU, context 8192, approximately 6.1GB VRAM.
