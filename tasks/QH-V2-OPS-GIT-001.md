# QH-V2-OPS-GIT-001 - 안전한 원격 작업 인계와 Git 통합

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

이 Repository는 ChatGPT/GitHub에서 만든 작업을 원격 작업 브랜치에서 로컬 `main`으로 반복해서 가져온다. 현재의 임시 다중 커밋 `cherry-pick` 방식은 사람이 실수하기 쉽고, 적용 누락 여부를 즉시 알기 어렵다.

QH-V2-DOC-003 진행 중 실제로 다음 문제가 재현됐다.

- 원격 작업 브랜치에 여러 문서 커밋이 존재했다.
- 범위 cherry-pick 중 empty commit이 발생해 `git cherry-pick --skip`을 여러 번 사용해야 했다.
- 시퀀스가 끝난 뒤 `docs/PROJECT_TIMELINE.md`가 로컬에 누락되어 있었다.
- 누락된 정확한 커밋을 다시 찾아 별도로 cherry-pick해야 했다.
- 최종 Verification 전에 deterministic diff/file 검사로 누락을 발견했기 때문에 완료 Task 자체의 무결성은 지켜졌다.

이전 Git/CMD 사고 기록에서도 반복되는 수동 복구 절차는 shell ritual로 남기기보다 작은 deterministic workflow로 승격해야 한다는 Evidence가 있다.

이번 문제는 Repository를 손상시키지는 않았지만, 현재 인계 절차는 앞으로 여러 Task를 반복 수행하기에 충분히 신뢰할 수 있는 상태가 아니다.

## Goal

일상적인 다중 커밋 cherry-pick 모호성을 제거하고, 기준점이 맞는 경우 원격 커밋의 정확한 SHA를 보존하며, 수동 `--skip` 복구 대신 조건이 맞지 않으면 fail closed하는 최소 deterministic 원격→로컬 인계 절차를 설계하고 구현한다.

권장 정상 경로는 다음과 같다.

`정확한 local/main baseline -> 그 SHA에서 원격 작업 브랜치 생성 -> 단일 atomic handoff commit -> fetch -> read-only handoff check -> git merge --ff-only -> 동일 commit SHA 보존`

이 Task는 자동 destructive Git 복구를 추가하거나 Harness lifecycle 권한을 넓히지 않는다.

## Requirements

1. 일상 인계용 원격 작업은 명시적으로 기록된 baseline SHA에서 시작한 브랜치 위의 정확히 1개 atomic handoff commit으로 최종화한다.
2. 정상 경로에서는 multi-commit range cherry-pick을 사용하지 않는다.
3. 로컬 HEAD가 handoff commit의 정확한 parent와 같다면 `git merge --ff-only` 방식으로 통합해 원격 commit SHA를 그대로 보존한다.
4. 통합 전 deterministic read-only check는 최소한 다음을 보고한다.
   - 현재 로컬 HEAD
   - 원격 handoff ref/commit
   - handoff parent SHA
   - changed paths
   - exact fast-forward 통합이 안전한지 여부
5. read-only check는 최소 다음 상태를 구분한다.
   - `FAST_FORWARD_SAFE` - 로컬 HEAD가 정확히 handoff parent임
   - `ALREADY_APPLIED_EXACT` - 로컬 HEAD가 정확히 handoff commit임
   - `ALREADY_CONTAINED` - handoff commit이 이미 로컬 HEAD의 ancestor임
   - `STOP_DIRTY` - worktree/index가 clean하지 않음
   - `STOP_NON_ATOMIC_OR_DIVERGED` - baseline/parent/history 형태가 안전 계약과 맞지 않음
6. deterministic check는 fetch, merge, cherry-pick, reset, rebase, force-update, branch 삭제, push 등 Git mutation을 수행하지 않는다.
7. 안전 계약이 만족되지 않으면 정상 workflow는 STOP한다. repeated `cherry-pick --skip`을 자동 복구 절차로 권장하지 않는다.
8. divergent/non-atomic handoff는 현재 승인된 baseline에서 새 exact handoff를 다시 만들거나 별도 Human-reviewed integration으로 처리한다.
9. 기존 `qh close`, Verification, lifecycle, Git Evidence, Worker authority, Human Gate는 변경하지 않는다.
10. `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.

## Architecture Basis

- ADR-001: 기계적으로 판정 가능한 workflow는 deterministic Harness 코드가 담당한다.
- ADR-003: 반복적으로 검증된 운영 실패와 수동 복구는 별도 승인 Task를 통해 작은 deterministic utility 후보로 승격할 수 있다.
- ADR-005/ADR-006: lifecycle과 completion authority를 유지한 채 workflow/UX 개선을 허용한다.
- ADR-007: 최종 Task Verification과 lifecycle completion의 권위는 `qh close`에 유지된다.
- ADR-017: 이미 승인된 일상 진행은 계속할 수 있지만 Git divergence, ambiguity, conflict, destructive recovery, unexpected state에서는 STOP해야 한다.

이 Task는 Operations hardening이며 Worker Architecture나 Trust Boundary를 변경하지 않는다.

## Scope

1. Human이 선택한 Git handoff 우선순위를 Repository Source of Truth에 기록한다.
2. atomic handoff + fast-forward-only 정책과 QH-V2-DOC-003 재현 Evidence를 Accepted decision으로 기록한다.
3. BACKLOG 순서를 다음과 같이 조정한다.

   `QH-V2-OPS-GIT-001 -> QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003`

   기존 Operations/M2 queue는 취소하지 않는다.
4. 기존 deterministic Git helper를 재사용할 수 있으면 재사용하여 read-only `qh handoff-check <remote-ref>` workflow를 추가한다.
5. 필수 classification과 zero-mutation 동작을 검증하는 focused tests를 추가한다.
6. 검증된 안전 인계 절차를 관련 개발/트러블슈팅 문서에 한국어로 반영한다.
7. 실제 production remote mutation을 테스트 수단으로 사용하지 않고 temporary/local Git fixture로 동작을 입증한다.

## Allowed Changes

- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-GIT-001.md`
- `tools/qh.py`
- 작은 재사용 read-only Git helper가 필요한 경우에만 `tools/harness_core.py`
- `tests/test_qh.py`
- `tools/harness_core.py`가 변경될 경우에만 `tests/test_harness_core.py`
- `docs/DEVELOPMENT.md`
- `docs/TROUBLESHOOTING.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- Worker Adapter/Runner/Retry 동작
- model, `think`, timeout, Retry budget, Worker-step budget, Tool authority 변경
- Harness 내부의 자동 fetch/merge/cherry-pick/reset/rebase/push/force 동작
- 자동 conflict resolution
- 자동 branch 삭제
- `qh close`, Verification, Final Gate, lifecycle, scope authority 약화
- historical G1 manifest 수정/재활성화
- Candidate A/B production integration
- Globalization

## Acceptance Criteria

1. QH-V2-DOC-003의 multi-commit cherry-pick 재현을 Repository corruption으로 과장하지 않고 객관적 동기로 기록한다.
2. Accepted decision이 exact baseline, one atomic handoff commit, read-only deterministic check, safe일 때만 수동 `git merge --ff-only`를 사용하는 정상 handoff contract를 정의한다.
3. BACKLOG에 `OPS-GIT-001 -> ARCH-018 -> WORKER-ROB-003 -> OPS-003` 순서가 기록되고 기존 후속 queue가 보존된다.
4. `qh handoff-check <remote-ref>`는 read-only이며 현재 HEAD, handoff commit, handoff parent, changed paths, deterministic classification 하나를 출력한다.
5. `FAST_FORWARD_SAFE`는 Repository가 clean이고 현재 HEAD가 정확히 handoff commit의 parent일 때만 반환된다.
6. exact already-applied/contained 상태를 safe-to-apply 상태와 구분한다.
7. dirty, divergent, merge-commit 또는 그 밖의 non-atomic 형태는 fail closed한다.
8. focused regression으로 모든 classification에서 Repository mutation이 0임을 증명한다.
9. 자동 Git write operation을 추가하지 않는다.
10. 기존 qh lifecycle/Verification regression이 PASS한다.
11. 운영 문서가 multi-commit range cherry-pick을 일상 handoff 경로로 사용하지 말라고 명시한다.
12. `GLOBALIZATION = NOT AUTHORIZED`가 유지된다.
13. Allowed Changes만 발생한다.
14. `git diff --check`가 PASS한다.
15. 사람이 읽는 새 GitHub 문서 서술은 한국어로 작성하고, command/status/API/file name 등 정확한 기술 literal만 원문 표기를 유지한다.

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

성공적으로 close하기 전에 다음 Evidence를 보존한다.

- QH-V2-DOC-003 handoff 재현과 missing-path 탐지 기록
- exact Task baseline SHA
- 구현 전 가능한 범위에서 dirty/diverged/non-atomic unsafe state를 재현하는 focused RED
- 모든 필수 classification의 focused GREEN
- 모든 read-only classification의 zero mutation
- `tests.test_qh` regression PASS
- exact changed paths와 scope classification
- exact implementation HEAD를 사용한 authoritative `qh close` Final Gate PASS
- Final Gate 이후 별도 lifecycle commit

## Stop Conditions

다음이 필요하면 Human/ChatGPT review를 위해 STOP한다.

- 자동 cherry-pick, merge, reset, rebase, push, force, conflict resolution 또는 destructive Git recovery
- branch/remote authority의 전역 변경
- lifecycle 또는 Final Gate authority 변경
- divergent/non-atomic remote state를 heuristic으로 수용
- Architecture, Requirements, Trust Boundary, Worker, model, Retry, Tool authority, Globalization 변경
- 정확한 remote/local handoff 문제를 넘어서는 범위 확장

## Next Task

QH-V2-OPS-GIT-001이 `COMPLETE - VERIFIED`에 도달하면, 다음 방향은 Human이 이미 선택한 Candidate A 승격 경로다.

`QH-V2-ARCH-018 - Deterministic Worker Brief Production Promotion Decision`

단, Human이 2026-08-24에 요청한 GitHub 문서 한국어 통일/최신화 작업은 별도 문서 Task로 분리해 OPS-GIT-001 이후 Source of Truth에 추가한다. 이 문서 Task는 기존 historical Evidence의 의미를 바꾸지 않고, 현재/사용자-facing 문서를 한국어로 최신화하는 것을 목표로 한다.

그 이후 계획은 다음 순서를 유지한다.

`QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003 -> QH-V2-OPS-004 -> QH-V2-OPS-005 -> QH-V2-OPS-006 -> QH-V2-M2-SPEC-001 -> HUMAN ARCHITECTURE GATE`.
