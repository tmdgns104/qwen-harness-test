# Local Worker Research Closeout — 2026-09-04

## Status

`LOCAL_IMPLEMENTATION_WORKER_RESEARCH = CLOSED`

`LOCAL_CASCADE = NOT PROMOTED`

`HYBRID_NOT_GENERALIZED`

`VNEXT-008 = NOT STARTED`

`GLOBALIZATION = NOT AUTHORIZED`

## Final recommendation

The current recommended coding path is:

```text
Task
→ Codex Direct
→ isolated snapshot / bounded execution
→ tests
→ independent semantic verifier
→ scope / diff validation
→ Final Gate
```

The Harness remains valuable as a verification and authority boundary. The current local LLM stack is not promoted as a general implementation Worker or as a default Codex pre-processing layer.

## Local implementation Worker result

Real-project frozen semantic evaluation showed stable capability limits rather than useful run-to-run variance.

- `qwen3:8b`: 25% on the frozen real-project task set
- `qwen2.5-coder:7b`: 25%
- `qwen2.5-coder:14b-instruct-q3_K_S`: no uplift over the 25% baseline
- `qwen3.5:9b`: no semantic uplift
- `command-r7b`: no uplift
- Mistral Nemo: protocol/apply path not sufficient for promotion
- `gpt-oss:20b`: structured/hardware gate unsuccessful
- `qwen3-coder:30b`: memory-pressure hardware feasibility failure on the current laptop

Reproducibility testing showed deterministic output at the tested settings: the same Model×Task pair repeatedly produced the same Candidate hash and the same verifier result. The dominant limitation was semantic capability, not stochastic instability.

## Retry and cascade result

Same-model bounded revision did not repair the observed semantic failure and repeated the same logic error. A local model cascade increased latency without improving verified correctness, so automatic local retry/cascade is not promoted.

## Role-reduced Local Triage experiment

An initial four-task Codex-First Hybrid experiment suggested a possible benefit:

- verified correctness unchanged
- total Codex token reduction: 8.64%
- uncached input reduction: 31.89%

This result was treated only as a candidate because the task sample was small.

## Historical Replay generalization test

A later frozen Historical Bug Replay evaluation used four real historical bugs whose parent commit failed an independent verifier and whose historical fix passed it. The benchmark used the same frozen manifest and verifier for three strategies:

- A — Codex Direct
- B — Local Triage → Codex
- C — Code/Test RAG + Local Triage → Codex

All strategies achieved the same verified correctness: `3/4`.

### Efficiency

| Metric | A — Codex Direct | B — Local Triage | C — RAG + Local Triage |
|---|---:|---:|---:|
| Tokens / Verified Task | 432,382.67 | 536,372.00 | 541,732.33 |
| Uncached input / Verified Task | 34,975.33 | 49,188.67 | 42,052.00 |
| Codex elapsed | 508.611s | 631.000s | 648.876s |
| End-to-end elapsed | 508.611s | 678.248s | 707.229s |
| Tool calls | 34 | 46 | 49 |

A→B therefore increased Tokens/Verified Task by 24.05%, uncached input by 40.64%, Codex time by 24.06%, and end-to-end time by 33.35% while correctness stayed unchanged.

B→C preserved correctness but did not provide a meaningful incremental improvement. C increased Tokens/Verified Task by 1.00% and end-to-end time by 4.27%, although uncached input fell by 14.51% relative to B.

Final disposition: `HYBRID_NOT_GENERALIZED`.

## RAG finding

The retrieval layer itself was not the main failure:

- Code RAG relevance: `4/4 HIGHLY_RELEVANT`
- the writable source ranked first for all four tasks
- Test RAG: `4/4 IRRELEVANT`
- Obsidian: two `NEUTRAL`, two `WITHHELD_FOR_LEAKAGE_SAFETY`

The weak point was the Local Triage interpretation layer. In the RAG strategy its requirement/localization assessment was wrong on all four tasks, and misleading assistance was common. Therefore the rejected architecture is specifically:

```text
RAG → Local LLM Triage → Codex
```

This does not prove that deterministic retrieval directly into Codex can never help; it only means that no such architecture is promoted by the current evidence.

## Harness findings that remain successful

The research produced durable engineering value independent of local-model promotion:

- Bounded Authority
- task-scoped operation constraints
- structured output handling
- parser / validator separation
- exact `REPLACE_TEXT` semantics
- isolated apply
- scope and diff validation
- deterministic tests
- independent semantic verification
- false-COMPLETED prevention
- original target invariance
- fail-closed benchmark and lifecycle handling

In the final Historical Replay evaluation, Codex made one false-PASS claim that the hidden verifier correctly rejected. This reinforces the value of the Harness as a verification boundary.

## Infrastructure hardening learned during the final evaluation

The first Historical Replay attempt was blocked by `JSONL_READER_DEADLOCK` in the experiment runner. The fix introduced concurrent binary stdout/stderr draining, explicit UTF-8 stdin EOF handling, a first-JSONL watchdog, Windows process-tree termination, cwd/workspace alignment, and fail-closed launch validation. The rerun completed all 12 valid slots without deadlock recurrence.

## Current hardware conclusion

On the tested Windows laptop with RTX 5070 Laptop GPU 8GB VRAM and 32GB RAM, larger local models quickly move into RAM/VRAM pressure without demonstrated semantic uplift. A hardware upgrade could make larger models runnable, but current evidence does not justify assuming that this alone would make a local coding Worker competitive.

## Future local-LLM direction

Local LLM work should shift away from autonomous repository implementation and toward lower-risk, high-volume utility roles such as:

- personal knowledge RAG
- structured extraction
- log/test failure classification
- development journal generation
- semantic file search
- grounded document summarization
- data-analysis explanation

The Personal Engineering Brain project is the primary RAG/knowledge track and remains separate from Qwen Harness.

## Evidence provenance note

The final Historical Replay / RAG-Hybrid raw evidence was produced on the local branch `experiment/rag-hybrid-assist-001` with the following reported local commits:

- evaluation evidence: `37f4d99d1ff6988c96a560d0bb9490fb436a3768`
- lifecycle: `bbb0f6715a206fffcb200f3845ee17c38c90e1a8`

Those commits are not currently present on remote GitHub `main`; this closeout document records the verified research disposition without reconstructing or fabricating the missing raw evidence tree. The local experiment branch should be pushed separately from the user's PC if full raw-evidence publication is desired.
