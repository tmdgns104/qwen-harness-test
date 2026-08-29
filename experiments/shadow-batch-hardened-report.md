# Shadow Batch Hardening 002

AST-based function extraction was used (`ast.get_source_segment`), preventing
the prior boundary corruption. Five real Qwen3:8B first-pass calls were made,
plus the SHADOW-003 rerun, all in isolated snapshots. Target baseline was
`3c05219d50a51f2bdad8e6671e702e8c5d575e50`; the pre-existing zip remained
unchanged.

| Task | Type | Latency | Pipeline | Semantic result |
|---|---|---:|---|---|
| SHADOW-003R `_text` | boundary/scalar | 13.95s | transport/parse/validator/apply PASS | FAIL: unchanged zero handling |
| SHADOW-005 `_safe` | normalization | 2.76s | transport/parse/validator/apply PASS | FAIL: Candidate polluted with assertions (syntax error) |
| SHADOW-006 `_clip` | scalar/trim | 1.74s | transport/parse/validator/apply PASS | FAIL: unchanged zero handling |
| SHADOW-007 `merge_project_brief` | validation | 4.94s | transport/parse/validator/apply PASS | FAIL: Candidate polluted with assertions (syntax error) |
| SHADOW-008 `sanitize_live_state` | data handling | 30.03s | transport timeout | not reached |

Capability denominator: 4 valid model samples (all semantic failures), excluding
the SHADOW-008 performance failure; no benchmark defect was observed after AST
extraction. Qwen first-pass semantic success: **0/4 valid samples**. Parser,
validator, and apply succeeded for 4/4 valid calls. Codex escalation candidates:
all four semantic failures. The fifth is `PERFORMANCE_FAIL`.

Target regression command `python -m unittest tests.test_conversation tests.test_documents -q`
failed before collection because the repository has no importable `tests` package
(`ModuleNotFoundError`); this is recorded as `TEST_INFRA_DEFECT`, not PASS.

Safety: False COMPLETED 0, unauthorized apply 0, original target mutation 0.
No production Harness, architecture, timeout, retry, authority, or globalization
state was changed.
