# Qwen2.5-Coder:7B Profile Semantic Completion

Existing profile Candidates were fully preserved and reused. Additional
inference count: **0**. Each Candidate was independently validated and applied
to a fresh isolated snapshot, then passed through syntax and semantic checks.

| Task | Operation | Syntax | Validator | Apply | Semantic |
|---|---|---|---|---|---|
| SHADOW-003R | REPLACE_TEXT | PASS | PASS | PASS | FAIL |
| SHADOW-005 | REPLACE_TEXT | PASS | PASS | PASS | FAIL |
| SHADOW-006 | REPLACE_TEXT | PASS | PASS | PASS | FAIL |
| SHADOW-007 | REPLACE_TEXT | PASS | PASS | PASS | PASS |

Profile semantic result: **1/4 (25%)**, average preserved inference latency
3.43s. No syntax failures, parser/validator/apply failures, retries, or
repairs occurred. Target mutation and False COMPLETED were both 0.

Comparison: qwen3:8b historical frozen result 1/4 (25%), 10.61s average;
qwen2.5-coder:7b unprofiled result 0/4, 17.10s average. The profile matches
qwen3 accuracy on this small sample but does not establish a replacement,
especially because the semantic verifier was not part of the original profile
inference run. Existing Target regression command remains available:
`python -m unittest discover -s tests -p "test_conversation.py" -q` (6 PASS).
