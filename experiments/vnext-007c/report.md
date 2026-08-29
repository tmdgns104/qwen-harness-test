# VNEXT-007C Evidence

Twelve exact-authorized synthetic tasks were compared. Read-only
`tests/visible.py` remained visible in Context but was explicitly separated
from write authority in B/C.

| Condition | Transport | Parse | Validator | Read-only path | Mean / median |
|---|---:|---:|---:|---:|---:|
| A current adapter | 12/12 | 12/12 | 6/12 | 2 | 1.045 / 0.960 s |
| B authority serialization | 12/12 | 12/12 | 12/12 | 0 | 0.809 / 0.830 s |
| C B + dynamic path enum | 12/12 | 12/12 | 12/12 | 0 | 0.600 / 0.603 s |

B explicitly serialized `AUTHORIZED WRITE TARGETS` versus `READ-ONLY
CONTEXT`. C additionally passed an Ollama JSON Schema path enum containing
only `src/module.py`. Parser and Validator semantics were unchanged; no path
repair or authority expansion was used.

Apply and semantic verification were not implemented in this experiment, so
those stages and Final COMPLETED remain unverified. No invalid candidate was
applied, no original mutation occurred, and false COMPLETED was zero.

The result supports hardening when the Harness has a finite authorized path
set, but does not authorize VNEXT-008. Wildcard/new-file scopes require a
separate design and must not be silently converted to enums.
