# Autonomous Shadow Batch

Target baseline: `3c05219d50a51f2bdad8e6671e702e8c5d575e50`.
The pre-existing untracked `team_project_os-main.zip` remained unchanged.

| Task | Target | Result | Latency | Classification |
|---|---|---:|---:|---|
| SHADOW-002 | `app/delivery_documents.py:_safe` | FAIL | 2.801s | MODEL_LOGIC_FAILURE (Candidate unchanged; `_safe(0)` failed) |
| SHADOW-003 | `app/live_state.py:_text` | FAIL | 3.760s | BENCHMARK_DEFECT / extraction boundary produced malformed source |
| SHADOW-004 | `app/conversation.py:_clip` | PASS | 3.004s | — |

All three calls used Qwen3:8B, `think=false`, strict REPLACE_TEXT, exact path,
isolated snapshot apply, and no retry. Transport, parser, validator, and apply
passed for all three; semantic verification passed only SHADOW-004. The
SHADOW-003 source excerpt extraction in this experimental runner accidentally
captured a later string fragment, so it is excluded from the model denominator
and recorded as benchmark defect rather than a Qwen failure.

Batch KPI: Qwen first-pass success **1/3**; parser **3/3**; validator **3/3**;
apply **3/3**; independent semantic **1/3**; Codex review **1/3**. Semantic
failures: one clear logic failure, one benchmark defect. Codex escalation:
SHADOW-002; SHADOW-003 requires fixture/runner correction before rerun.
False COMPLETED: 0. Original target mutation: 0.

The successful task is a small single-file, state-independent normalization
change. Current routing recommendation is to use Qwen for similarly bounded
single-file utility changes with explicit behavioral assertions; escalate
parser-heavy, multi-file, or ambiguous tasks to Codex. No official Architecture,
VNEXT task, timeout, authority, or globalization state was changed.
