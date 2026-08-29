# VNEXT-003 — Structured Candidate Validator

## Task Status

ACTIVE

Implemented deterministic `CandidateValidationResult` and `validate_candidate()` in `tools/harness_core.py`. The validator accepts only frozen VNEXT-001 `CREATE_FILE`/`REPLACE_FILE` operations, checks malformed types, relative path/traversal/absolute paths, allowed and forbidden scope, protected lifecycle paths, duplicate paths, operation count, and content limits. It never applies or executes a Candidate and performs no semantic LLM judgment.

Focused validator tests: 4/4 PASS. VNEXT-001/002 contract plus `tests.test_harness_core`: 127/127 PASS. `git diff --check`: PASS. No Native Agent, authority, timeout, retry, or Team Project OS behavior changed.
