# TP-OS-SHADOW-001R2

## Result

The task-scoped operation constraint was implemented and tested. The real
Team Project OS shadow invocation performed one Qwen3:8B inference, but the
diagnostic response did not yield a Candidate within the observation window.
No retry or repair was performed.

* Target baseline: `3c05219d50a51f2bdad8e6671e702e8c5d575e50`
* Target status before/after: pre-existing `?? team_project_os-main.zip`; unchanged
* Inference count: 1
* Inference elapsed: 14.049s; wall-clock: 14.117s
* Candidate: none; operation/path/content metrics: unavailable
* Validator/apply/semantic/regression: not reached
* Harness outcome: `FAILED`
* First-pass success: no
* Classification: `TRANSPORT_TIMEOUT`/no structured Candidate (the adapter returned no candidate)
* Original target mutation: 0
* False COMPLETED: 0
* Codex review: FAIL for task completion (no Candidate to review)

## Contract and regression evidence

`BoundedWorkerRequest.allowed_operation_types` now permits a task to restrict
generation to an explicit operation tuple. The Ollama JSON schema is filtered
to that tuple, and `validate_candidate()` independently rejects an operation
outside it. For TP-OS-SHADOW-001R2 the only allowed operation is
`REPLACE_TEXT`; `CREATE_FILE` and `REPLACE_FILE` are not exposed by the
task-scoped schema and are rejected by validation.

Focused contract, apply, validator, and adapter tests: **27 passed, 1 skipped**.
`git diff --check`: pass. Native Agent semantics were not changed.

## Comparison

R1 produced a `REPLACE_FILE` Candidate in 9.336s and failed with
`WRONG_OPERATION`. R2 did not produce a Candidate in the observed run, so it
did not reach operation validation or isolated apply. This is not evidence of
semantic success; a subsequent bounded observation may be needed, but this
task run itself remains a preserved failure.
