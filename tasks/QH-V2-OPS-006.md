# QH-V2-OPS-006 - STATUS / Handoff Historical Cleanup

## Status

PLANNED

## Problem

The concise lifecycle fields at the top of STATUS are authoritative, but the accumulated
Handoff body also contains old ACTIVE and NOT STARTED statements from earlier milestones.
Those records are useful Evidence yet can be misread as current state.

## Goal

Separate concise current STATUS state from a lossless, provenance-labelled historical
Handoff archive without deleting Evidence, rewriting Git history, or changing past
Task completion meaning.

## Architecture Basis

- Repository Source-of-Truth policy and `docs/DEVELOPMENT.md` require current state
  and historical Evidence to remain inspectable.
- ADR-006 identifies STATUS historical cleanup as an operations candidate.
- ADR-010 classifies STATUS/Handoff historical cleanup as SAFE-TO-DEFER.
- `docs/DEVELOPMENT.md` defines the top lifecycle block as current authority.
- Git history remains the immutable record of prior lifecycle transitions.

## Dependencies

- QH-V2-OPS-005 must be COMPLETE - VERIFIED.
- Status UX is completed first so the cleanup can archive one stable final pre-M2 snapshot.
- Human approval is required before activation.

## Scope

- Create `docs/STATUS_HISTORY.md` as the single archive artifact.
- Preserve the complete pre-cleanup Handoff bytes verbatim and label the source
  commit and Task baseline.
- Keep exactly one Current Task, Previous Task, Next Planned Task, and Task Baseline
  field at the top of STATUS.
- Replace the accumulated body with a concise current handoff, current known issues,
  and a resolvable archive link.
- Update README/DEVELOPMENT navigation and explain current-versus-history authority.
- Preserve the post-start lifecycle values throughout implementation; only qh close
  performs the later approved lifecycle transition.

## Allowed Changes

- `STATUS.md`
- `docs/STATUS_HISTORY.md`
- `README.md`
- `docs/DEVELOPMENT.md`
- `tasks/QH-V2-OPS-006.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. STATUS contains exactly one Current Task, Previous Task, Next Planned Task, and
   Task Baseline field.
2. After the approved `qh start` transition, the four lifecycle values remain
   unchanged during implementation until the normal authoritative qh close transition.
3. Every byte of the pre-cleanup Handoff body appears verbatim in
   `docs/STATUS_HISTORY.md`.
4. The archive identifies the source Git commit and Task baseline used for preservation.
5. STATUS contains a concise current handoff, current known issues, and a working
   relative link to the archive.
6. README and DEVELOPMENT links resolve and explain that STATUS top fields are current
   while the archive is historical context.
7. Past COMPLETE/VERIFIED facts, hashes, commands, and Evidence meaning are not altered.
8. No production code or test changes occur and no Git history is rewritten.

## Verification

Run exactly:

`python -c "from pathlib import Path; import subprocess; s=Path('STATUS.md').read_text(encoding='utf-8'); lines=s.splitlines(); labels=('Current Task:','Previous Task:','Next Planned Task:','Task Baseline:'); assert all(sum(x.startswith(label) for x in lines)==1 for label in labels); baseline=next(x.split(':',1)[1].strip() for x in lines if x.startswith('Task Baseline:')); old=subprocess.run(['git','cat-file','blob',f'{baseline}:STATUS.md'],check=True,capture_output=True).stdout; body=old.split(b'Handoff:',1)[1]; history=Path('docs/STATUS_HISTORY.md').read_bytes(); assert body in history and f'Source commit: {baseline}'.encode() in history and f'Task baseline: {baseline}'.encode() in history"`

Then run:

`python -c "from pathlib import Path; assert Path('docs/STATUS_HISTORY.md').is_file(); assert '(docs/STATUS_HISTORY.md)' in Path('STATUS.md').read_text(encoding='utf-8'); assert '(docs/STATUS_HISTORY.md)' in Path('README.md').read_text(encoding='utf-8'); assert '(STATUS_HISTORY.md)' in Path('docs/DEVELOPMENT.md').read_text(encoding='utf-8')"`

Then run:

`python tools/qh.py status`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Record the pre-cleanup STATUS blob SHA and the exact source commit/baseline.
- A deterministic byte comparison and SHA-256 record prove the full old Handoff body
  occurs verbatim in the archive; heading counts alone are insufficient.
- A human-readable diff proves current lifecycle values and historical facts retain meaning.
- Link checks cover STATUS, README, DEVELOPMENT, and the archive.
- Baseline-to-implementation changed paths contain only Allowed Changes and no
  production or test files.
- Exact implementation HEAD is used by `qh close`; all Verification exits are 0,
  unexpected paths are absent, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- deleting, paraphrasing, or losing historical Evidence;
- changing a past completion hash/status or rewriting Git history;
- moving Architecture authority away from Accepted ADRs;
- production-code, test, BACKLOG, Requirements, or Decisions changes;
- automatic successor activation.

## Next Task

Queue successor candidate: QH-V2-M2-SPEC-001.

Human approval is required. Do not auto-start it.
