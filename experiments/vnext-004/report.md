# VNEXT-004 — Temporary Candidate Apply

## Task Status

ACTIVE

Implemented `CandidateApplyResult` and `apply_candidate_to_snapshot()`. A validated Candidate is copied into a fresh temporary directory, then CREATE_FILE/REPLACE_FILE operations are applied with containment and symlink checks. CREATE conflicts, missing replacements, invalid validation, unsafe paths, and any mid-operation error fail closed; failed snapshots are removed, so partial success is never returned. The original repository is never written.

Focused apply tests: 3/3 PASS, symlink test skipped because the host does not permit symlink creation. VNEXT-001/002/003 plus `tests.test_harness_core`: 131/131 PASS. `git diff --check`: PASS. No Native Agent, authority, timeout, retry, verification orchestration, or Team Project OS behavior changed.
