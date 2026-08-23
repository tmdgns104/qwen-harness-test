# QH-V2-OPS-GIT-001 - Safe Remote Work Handoff and Git Integration

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

The Repository repeatedly transfers ChatGPT/GitHub work from a remote work branch into the local `main` branch. The current ad-hoc multi-commit `cherry-pick` workflow is error-prone.

A concrete recurrence occurred during QH-V2-DOC-003:

- a remote work branch contained several documentation commits;
- a range cherry-pick encountered empty commits and required repeated `git cherry-pick --skip`;
- after the sequence completed, `docs/PROJECT_TIMELINE.md` was missing locally;
- the missing exact commit had to be identified and cherry-picked separately;
- deterministic diff/file checks caught the omission before final Verification.

Earlier Git/CMD incidents also showed that repeated manual recovery procedures should become a deterministic workflow candidate rather than remain shell ritual.

The failure did not corrupt the completed Task because the missing path was detected before `qh close`, but the handoff process itself is not yet reliable enough for repeated use.

## Goal

Define and implement the minimum deterministic remote-to-local handoff workflow that prevents routine multi-commit cherry-pick ambiguity, preserves exact commit identity when the baseline permits it, and fails closed instead of requiring manual skip/recovery sequences.

The preferred normal path is:

`exact local/main baseline -> remote work branch created from that exact SHA -> one atomic handoff commit -> fetch -> deterministic read-only handoff check -> git merge --ff-only -> exact commit preserved`

This Task must not introduce automatic destructive Git recovery or broaden Harness lifecycle authority.

## Requirements

1. Remote work intended for routine handoff must be finalized as exactly one atomic handoff commit on a branch created from an explicitly recorded baseline SHA.
2. The routine happy path must not require a multi-commit range cherry-pick.
3. When local HEAD still equals the handoff commit parent, integration must use fast-forward-only semantics so the exact remote commit SHA is preserved.
4. Before integration, a deterministic read-only check must report at minimum:
   - current local HEAD;
   - remote handoff ref/commit;
   - handoff parent SHA;
   - changed paths;
   - whether the state is safe for exact fast-forward integration.
5. The read-only check must distinguish at least:
   - `FAST_FORWARD_SAFE` - local HEAD is the exact handoff parent;
   - `ALREADY_APPLIED_EXACT` - local HEAD is the exact handoff commit;
   - `ALREADY_CONTAINED` - the exact handoff commit is already an ancestor of local HEAD;
   - `STOP_DIRTY` - worktree/index is not clean;
   - `STOP_NON_ATOMIC_OR_DIVERGED` - baseline/parent/history shape does not match the safe contract.
6. The deterministic check must not fetch, merge, cherry-pick, reset, rebase, force-update, delete branches, push, or otherwise mutate Git state.
7. If the safe contract is not satisfied, the normal workflow must STOP. It must not recommend repeated `cherry-pick --skip` as automatic recovery.
8. A divergent/non-atomic handoff requires a new exact handoff prepared from the current approved baseline or separate Human-reviewed integration.
9. Existing `qh close`, Verification, lifecycle, Git Evidence, Worker authority, and Human Gates remain unchanged.
10. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.

## Architecture Basis

- ADR-001 keeps deterministic mechanically checkable workflow in Harness code.
- ADR-003 requires verified recurring operational failures to be recorded and repeated error-prone manual recovery to be promoted to a small deterministic utility through a separate approved Task.
- ADR-005/ADR-006 permit deterministic workflow/UX improvements while keeping lifecycle and completion authority unchanged.
- ADR-007 keeps `qh close` authoritative for final Task Verification and lifecycle completion.
- ADR-017 permits routine already-approved continuation but requires STOP on Git divergence, ambiguity, conflict, destructive recovery, or unexpected state.

This is an Operations hardening Task. It does not change the Worker Architecture or Trust Boundary.

## Scope

1. Record the Human-selected operational priority in Repository Source of Truth.
2. Add an Accepted decision documenting the atomic handoff + fast-forward-only policy and the QH-V2-DOC-003 recurrence Evidence.
3. Update BACKLOG so the planned order becomes:

   `QH-V2-OPS-GIT-001 -> QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003`

   without cancelling the existing Operations/M2 queue.
4. Add a read-only `qh handoff-check <remote-ref>` workflow using existing deterministic Git helpers where practical.
5. Add focused tests covering the required classifications and zero-mutation behavior.
6. Update the relevant development/troubleshooting documentation with the verified safe handoff procedure.
7. Demonstrate the resulting flow with a temporary/local Git fixture; do not use production remote mutation as the test mechanism.

## Allowed Changes

- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-GIT-001.md`
- `tools/qh.py`
- `tools/harness_core.py` only if a small reusable read-only Git helper is required
- `tests/test_qh.py`
- `tests/test_harness_core.py` only if `tools/harness_core.py` changes
- `docs/DEVELOPMENT.md`
- `docs/TROUBLESHOOTING.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- Worker Adapter/Runner/Retry behavior
- model, `think`, timeout, Retry budget, Worker-step budget, or Tool authority changes
- automatic fetch/merge/cherry-pick/reset/rebase/push/force operations inside Harness
- automatic conflict resolution
- automatic branch deletion
- weakening `qh close`, Verification, Final Gate, lifecycle, or scope authority
- historical G1 manifest modification/reactivation
- Candidate A or Candidate B production integration
- Globalization

## Acceptance Criteria

1. The QH-V2-DOC-003 multi-commit cherry-pick recurrence is recorded as objective motivation without claiming Repository corruption.
2. An Accepted decision defines the exact normal handoff contract: exact baseline, one atomic handoff commit, read-only deterministic check, then manual `git merge --ff-only` only when safe.
3. BACKLOG records `OPS-GIT-001 -> ARCH-018 -> WORKER-ROB-003 -> OPS-003` and preserves the remaining existing queue.
4. `qh handoff-check <remote-ref>` is read-only and reports current HEAD, handoff commit, handoff parent, changed paths, and one deterministic classification.
5. `FAST_FORWARD_SAFE` is returned only when the Repository is clean and current HEAD is the exact parent of the single handoff commit.
6. Exact already-applied/contained states are distinguished from safe-to-apply state.
7. Dirty, divergent, merge-commit, or otherwise non-atomic shapes fail closed.
8. Focused regression proves the command performs zero Repository mutation in every classification.
9. No automatic Git write operation is added.
10. Existing qh lifecycle/Verification regressions remain PASS.
11. Documentation tells operators not to use multi-commit range cherry-pick as the routine handoff path.
12. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
13. Only Allowed Changes occur.
14. `git diff --check` passes.

## Verification

Run exactly:

`python -m unittest tests.test_qh.HandoffCheckTests`

Run exactly:

`python -m unittest tests.test_qh`

Run exactly:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8'); b=Path('BACKLOG.md').read_text(encoding='utf-8'); text=d+'\n'+b; required=['QH-V2-OPS-GIT-001','QH-V2-ARCH-018','QH-V2-WORKER-ROB-003','QH-V2-OPS-003','FAST_FORWARD_SAFE','GLOBALIZATION = NOT AUTHORIZED']; missing=[x for x in required if x not in text]; assert not missing, missing"`

Run exactly:

`python -c "from pathlib import Path; t=Path('docs/TROUBLESHOOTING.md').read_text(encoding='utf-8')+'\n'+Path('docs/DEVELOPMENT.md').read_text(encoding='utf-8'); required=['merge --ff-only','atomic handoff','cherry-pick']; missing=[x for x in required if x not in t]; assert not missing, missing"`

Run exactly:

`git diff --check`

Run exactly:

`git status --short`

## Evidence Requirements

Before successful close, preserve Evidence for:

- the QH-V2-DOC-003 handoff recurrence and missing-path detection;
- exact Task baseline SHA;
- focused RED reproducing at least dirty/diverged/non-atomic unsafe states before implementation where applicable;
- focused GREEN for all required classifications;
- zero mutation for every read-only classification;
- `tests.test_qh` regression PASS;
- exact changed paths and scope classification;
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS;
- separate lifecycle commit after Final Gate PASS.

## Stop Conditions

STOP for Human/ChatGPT review if implementation would require:

- automatic cherry-pick, merge, reset, rebase, push, force, conflict resolution, or destructive Git recovery;
- changing branch/remote authority globally;
- changing lifecycle or Final Gate authority;
- accepting a divergent/non-atomic remote state by heuristic instead of fail-closed classification;
- Architecture, Requirements, Trust Boundary, Worker, model, Retry, Tool authority, or Globalization changes;
- expanding scope beyond the exact remote/local handoff problem.

## Next Task

If QH-V2-OPS-GIT-001 reaches COMPLETE - VERIFIED, the exact next direction is the already Human-selected Candidate A promotion path:

`QH-V2-ARCH-018 - Deterministic Worker Brief Production Promotion Decision`

After ARCH-018, the planned sequence is:

`QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003 -> QH-V2-OPS-004 -> QH-V2-OPS-005 -> QH-V2-OPS-006 -> QH-V2-M2-SPEC-001 -> HUMAN ARCHITECTURE GATE`.
