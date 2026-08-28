# QH-V2-WORKER-TIMEOUT-001 - Separate Worker Continuation Timeout

## Status

COMPLETE - VERIFIED

## Problem

Real Qwen Harness experiments showed that the native Ollama tool-session continuation can approach the current fixed 30 second timeout.

Observed Evidence:

- QH-EXP-CODEX-REVIEW-002:
  - Outcome: BLOCKED
  - Failure Kind: TRANSIENT_WORKER
  - Error: Worker continuation failed: timed out
  - Attempts: 2
  - Write Side Effect Risk: NO
- Read-only exact-task probe using the same Worker Brief and tools:
  - 30 second setting:
    - start: 2.98s
    - continuation: 28.16s
    - continuation produced exactly one write_repo_text request
    - generated report payload: 2447 characters
  - 120 second setting:
    - start: 2.28s
    - continuation: 22.49s
    - continuation produced exactly one write_repo_text request
    - generated report payload: 1773 characters

Therefore the current single fixed 30 second timeout is too close to measured real continuation latency and can cause false TRANSIENT_WORKER failures.

## Goal

Separate the initial Worker request timeout from the tool-result continuation timeout.

Keep the initial request timeout at 30 seconds.

Set the default continuation timeout to 60 seconds.

Do not change model, think mode, retry count, tool authority, write scope, step budget, or Globalization state.

## Required Design

Preserve existing behavior for non-tool worker calls.

For OllamaToolSession:

- initial `start()` request uses 30 seconds by default.
- `continue_with_tool_result()` uses 60 seconds by default.
- the continuation timeout must be independently configurable for tests/callers.
- existing callers that only pass `timeout_seconds` must remain compatible.
- timeout handling must remain bounded and fail closed.
- no automatic unlimited timeout or infinite retry.

Preferred compatibility shape:

- keep `DEFAULT_TIMEOUT_SECONDS = 30.0`
- add `DEFAULT_CONTINUATION_TIMEOUT_SECONDS = 60.0`
- keep `timeout_seconds` as the initial request timeout
- add `continuation_timeout_seconds`

## Allowed Changes

- tools/ollama_worker.py
- tests/test_ollama_worker.py
- tasks/QH-V2-WORKER-TIMEOUT-001.md
- STATUS.md

## Forbidden Changes

- tools/task_runner.py
- tools/retry_runner.py
- tools/repo_tools.py
- tools/harness_core.py
- ops/**
- all other tests/**
- PROJECT.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- DECISIONS.md
- README.md
- BACKLOG.md
- experiments/**
- model selection
- think setting
- MAX_WORKER_STEPS
- MAX_RUNNER_ATTEMPTS
- tool schemas
- tool authority
- write scope rules
- network policy
- Globalization approval
- automatic successor selection/start/close

All unlisted paths are default-denied.

## Acceptance Criteria

1. Initial OllamaToolSession request still defaults to 30 seconds.
2. Tool-result continuation defaults to 60 seconds.
3. Initial and continuation timeout values are independently configurable.
4. Existing `timeout_seconds` callers remain compatible.
5. Existing native tool-call translation behavior remains unchanged.
6. Existing multi-ToolRequest preservation behavior remains unchanged.
7. Existing malformed-tool response handling remains unchanged.
8. No retry/model/think/tool/scope behavior changes.
9. Unit tests explicitly prove start uses 30 seconds and continuation uses 60 seconds.
10. Unit tests explicitly prove custom continuation timeout is honored.
11. All existing Ollama worker tests pass.
12. `git diff --check` passes.

## Verification

Run:

`python -m unittest tests.test_ollama_worker -v`

Then run:

`python -m compileall tools`

Then run:

`git diff --check`

Then run:

`git status --short`

After implementation commit, independently rerun the real QH-EXP-CODEX-REVIEW-002-style latency/protocol probe before authorizing another substantive Qwen review experiment.

## Evidence Requirements

- exact code diff
- unit-test output
- compile output
- git diff --check
- final changed paths
- independent real Ollama probe after implementation
- independent ChatGPT review
- later independent Codex review

## Stop Conditions

Stop if:

- fixing this requires changing retry count, step budget, model, think mode, tool authority, or write scope.
- timeout must be made unbounded.
- existing tool protocol tests regress.
- unexpected paths change.
- Architecture or Requirements must change beyond the timeout policy stated here.

## Next Task

NONE.

A new Qwen review experiment may be authorized only after this Task is implemented, verified, and independently probed.
