# VNEXT-007G Evidence

## Phase 1 audit

The six visible-pass/independent-fail rows were identified: A `a-multi`, and
B `b-empty`, `b-state`, `b-parser`, `b-multi`, and `b-scope`. The preserved
VNEXT-007S result contains only task id, key, paths, booleans, outcome, and
timing. It does not contain Candidate content, visible test assertions,
independent verifier assertions, or expected/actual failure values. Therefore
none of the six can be validly classified as MODEL_GENERALIZATION_FAILURE;
their audit result is **INCONCLUSIVE**, not a Qwen failure.

The prior 44.4% Set B number remains historical Evidence but cannot be
recomputed into a specification-valid semantic baseline from the preserved
artifact. No prior Evidence was rewritten.

## Phase 2/3 status

No official adapter, parser, validator, apply, retry, or authority change was
made. A direct local Ollama probe with `think=true` returned transport success
and strict JSON for an empty Candidate, confirming the runtime accepts the
option. This is not evidence of semantic improvement. A/B/C full semantic
comparison was not claimed because the audit prerequisite (complete failure
evidence) is missing; running it without that prerequisite would confound
model generalization with an unverifiable benchmark.

Qwen3:8B remains the practical baseline, but VNEXT-008 is not recommended.
The next valid experiment must preserve Candidate content, visible and hidden
assertions, expected/actual failures, and per-task classification before any
reasoning-mode comparison.

