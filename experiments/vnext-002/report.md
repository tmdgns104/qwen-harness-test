# VNEXT-002 — Deterministic Context Pack Builder

## Task Status

ACTIVE

Implemented and verified the immutable Context Pack contract and Harness-owned builder. `ContextItem` preserves kind/source/content/metadata provenance; `ContextPack` preserves task ID, goal, acceptance, allowed/forbidden scope, selected items, output contract, metadata, and character budget usage. `build_context_pack()` consumes only explicitly supplied items, sorts deterministically by kind/source/content, rejects missing required fields and budget overflow, and never truncates or enumerates a Repository.

Focused Context Pack tests: 4/4 PASS. VNEXT-001 contract tests: 4/4 PASS. `tests.test_harness_core`: 119/119 PASS. `git diff --check`: PASS. No Native Agent, tool authority, candidate validation/application, inference, timeout, retry, or Team Project OS behavior changed.
