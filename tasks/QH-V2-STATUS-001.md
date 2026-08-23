# QH-V2-STATUS-001 - STATUS Handoff Consistency Cleanup

## Status

COMPLETE - VERIFIED

## Problem

`STATUS.md` correctly records `QH-V2-LIFECYCLE-001` as `COMPLETE - VERIFIED` at the lifecycle header, but one older Handoff bullet still says that QH-V2-LIFECYCLE-001 is ACTIVE through the one-time ADR-015 bootstrap transition.

That stale historical sentence conflicts with the current Source of Truth and can mislead future Human, ChatGPT, Work, or Codex sessions.

## Goal

Remove the stale ACTIVE wording and replace it with a concise historical handoff statement that accurately records QH-V2-LIFECYCLE-001 completion and the now-historical one-time ADR-015 bootstrap.

## Architecture Basis

- No Architecture change is required.
- ADR-015 remains unchanged.
- `QH-V2-LIFECYCLE-001` remains `COMPLETE - VERIFIED` with implementation commit `6f6ec879301cf59f85283f65394a4d34bf127c87`.
- Lifecycle commit `32d81ee61e0c1b65c4a488898bd7abbaaedf5488` is the current authoritative Repository state before this cleanup Task starts.
- This Task is documentation/state consistency cleanup only.

## Scope

- Update only the stale QH-V2-LIFECYCLE-001 Handoff bullet in `STATUS.md`.
- Preserve the lifecycle header, Previous Task, Next Planned Task, Task Baseline, and unrelated Handoff/history content except for normal lifecycle mutations performed by `qh start` / `qh close` for this Task.
- Record that durable unsuccessful-close support is implemented and that the one-time ADR-015 bootstrap is historical Evidence only.

## Allowed Changes

- `STATUS.md`
- `tasks/QH-V2-STATUS-001.md`

## Forbidden Changes

- all production code
- all tests
- `DECISIONS.md`
- `REQUIREMENTS.md`
- `PROJECT.md`
- `BACKLOG.md`
- all other Task files
- Worker, Runner, Retry, qhops, model, tool, Verification, Final Gate, and lifecycle implementation behavior

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. The stale Handoff sentence stating that `QH-V2-LIFECYCLE-001 is ACTIVE through the one-time Human-authorized ADR-015 bootstrap transition` is removed.
2. The replacement Handoff text states that QH-V2-LIFECYCLE-001 is `COMPLETE - VERIFIED` and references implementation commit `6f6ec879301cf59f85283f65394a4d34bf127c87` and lifecycle commit `32d81ee61e0c1b65c4a488898bd7abbaaedf5488`.
3. The replacement states that durable unsuccessful-close support is implemented and the one-time ADR-015 bootstrap is historical Evidence only and must not be reused.
4. No unrelated Handoff/history lines are edited.
5. No Architecture, production code, tests, lifecycle authority, or next-Task selection behavior changes.
6. Changed paths remain within Allowed Changes.

## Verification

Run exactly:

`python -c "from pathlib import Path; s=Path('STATUS.md').read_text(encoding='utf-8'); assert 'QH-V2-LIFECYCLE-001 is ACTIVE through the one-time Human-authorized ADR-015 bootstrap transition.' not in s; assert 'QH-V2-LIFECYCLE-001 is COMPLETE - VERIFIED; implementation commit 6f6ec879301cf59f85283f65394a4d34bf127c87 and lifecycle commit 32d81ee61e0c1b65c4a488898bd7abbaaedf5488 are authoritative.' in s; assert 'the one-time ADR-015 bootstrap is historical Evidence only and must not be reused.' in s"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Show the exact STATUS diff for the stale Handoff bullet.
- Verification commands exit 0.
- Final review shows no unexpected changed paths.
- Normal `qh close <implementation HEAD>` Final Gate PASS is required before completion.
- Lifecycle close commit remains separate from the implementation commit.

## Stop Conditions

STOP if cleanup requires changing Architecture, ADR-015, production code, tests, qh/qhops behavior, lifecycle semantics, automatic successor selection, or any path outside Allowed Changes.

## Next Task

Human selection required after this Task is COMPLETE - VERIFIED. Do not auto-start a successor.
