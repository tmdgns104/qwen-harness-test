# VNEXT-007P Candidate Path Alignment

## Raw analysis

The preserved VNEXT-007R rows stored only operation counts, not operation
paths, so exact path-level reconstruction from that artifact alone is limited.
The new 1:1 rerun records every returned path. In both conditions, the common
pattern was `src/module.py` plus (for most tasks) `tests/visible.py`; the latter
was not an authorized change. Multi-file rows correctly used
`src/module.py` and `src/caller.py`.

This is not basename shortening or prefix mismatch. The primary observed
categories are `WRONG_TARGET_SELECTION` / `ALLOWED_SCOPE_MISMATCH`: the model
selected a visible test path because the Context included a test item while
the task allowed only source paths. The fixture and provenance source strings
were otherwise identical (`src/module.py`, `src/caller.py`). This exposes a
benchmark/context contract ambiguity, not a justification for fuzzy repair.

## A/B

| Condition | Transport | Strict parse | Validator PASS | Mean inference |
|---|---:|---:|---:|---:|
| A current hardened adapter | 12/12 | 12/12 | 2/12 | 1.180 s |
| B exact-path contract hardening | 12/12 | 12/12 | 3/12 | 1.151 s |

Path alignment is therefore 16.7% to 25.0% in this run, below the 90%
reference gate. The improvement is insufficient and the benchmark itself must
separate worker-visible test context from Candidate-allowed paths in a future
fixture. No parser or validator relaxation was made; no path was repaired or
auto-mapped.

No snapshot apply or semantic E2E verification was reached in this task. No
scope-violating candidate was applied, no original repository mutation
occurred, and no false `COMPLETED` was produced. VNEXT-008 remains blocked.

## Hardening decision

The exact-path instruction was retained in the bounded prompt. Ollama JSON
Schema and strict parsing remain unchanged. Because the observed failure is
primarily scope/context ambiguity and B did not approach the alignment gate,
no further adapter or architecture change is promoted here.

