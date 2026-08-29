# Qwen2.5-Coder:7B Profile Evaluation

Environment contained `qwen3:8b` and `qwen2.5-coder:7b`; no model was
installed. Harness HEAD before evidence was `3e93284`; Target baseline was
`3c05219d50a51f2bdad8e6671e702e8c5d575e50`; Target mutation remained 0.

Profile change was limited to one common coder-oriented instruction: analyze
only supplied source and return exactly one strict REPLACE_TEXT JSON operation.
Core Candidate, parser, validator, apply, timeout, retry, and authority were
unchanged. This profile is not task-specific.

The four frozen tasks all reached transport, strict parse, validator, and
isolated apply (4/4). Latencies were 3.08s, 2.78s, 2.88s, and 4.97s (average
3.43s). The first task also served as the smoke path. Semantic verifiers were
not rerun in this profile script; therefore semantic PASS is **not claimed**.
The prior identical-task model comparison recorded qwen2.5-coder:7b at 0/4
semantic PASS and 17.10s average, while qwen3:8b was 1/4 and 10.61s.

Safety: no unauthorized apply, no target mutation, no repair/retry, and no
False COMPLETED. Current evidence does not justify replacing qwen3:8b as the
best local model. qwen2.5-coder remains an experimental candidate only.
