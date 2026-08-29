# VNEXT-007A Evidence

The VNEXT-007E artifact recorded only apply booleans, so it could not identify
the ten apply failures. This rerun recorded operation type, path, target state,
and exact errors against fresh fixtures. Fixture integrity was PASS: both
`src/module.py` and `src/caller.py` existed in the snapshot and matched the
Context provenance.

| Condition | Transport | Parse | Validator | Apply | Apply reliability |
|---|---:|---:|---:|---:|---:|
| A current contract | 12/12 | 12/12 | 11/12 | 3/12 | 27.3% |
| B explicit target state | 12/12 | 12/12 | 12/12 | 12/12 | 100% |

The exact dominant A failure was `CREATE_EXISTING_TARGET`: the Candidate
selected `CREATE_FILE` for existing `src/caller.py`. The error was the
fail-closed `FileExistsError` (`src/caller.py`). The remaining A apply passes
used valid `REPLACE_FILE` operations. No fixture defect, path-resolution
failure, parent failure, or missing-target failure was observed.

B explicitly stated `EXISTS => allowed_operation REPLACE_FILE` for each target;
the model then selected valid replacement operations for all twelve tasks.
No CREATE/REPLACE correction was performed by Harness. Parser, Validator, and
Apply semantics remain unchanged. No invalid Candidate was applied and no
original repository was mutated.

Mean/median inference latency was A 1.631/1.220 s and B 1.212/1.085 s. This
is operation-selection evidence, not semantic correctness evidence. No visible
or independent tests were run after apply in this task; Final COMPLETED is
therefore unverified. VNEXT-008 remains not recommended until semantic E2E
verification follows this hardening.

