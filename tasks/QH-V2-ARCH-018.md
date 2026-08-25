# QH-V2-ARCH-018 - Deterministic Worker Brief Production Promotion Decision

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

QH-V2-WORKER-DIAG-001은 현재 local Worker가 짧은 요청에는 응답하지만 full Repository Task를 직접 해결하도록 요청하면 기존 30초 timeout 안에서 불안정해지는 문제를 확인했다.

이후 QH-V2-WORKER-ROB-002는 production runtime을 변경하지 않은 격리 실험으로 Stable full Task와 두 Candidate를 비교했다. 그 결과 Candidate A - Deterministic Worker Brief는 10/10 valid bounded first step, 0/10 timeout, 100% transport success, median completed latency 약 2.013초를 기록했다. Stable은 6/10 valid bounded first step, 4/10 timeout, 60% transport success, median 약 10.529초였다. Candidate B는 2/10 valid bounded first step과 3/10 timeout으로 Candidate A보다 나빴다.

WORKER-ROB-002는 Candidate A를 별도 production Task로 promotion하라고 권고했지만, 실험 자체에는 production Architecture 변경 권한이 없었다. 따라서 실제 integration 전에 Candidate A의 production 경계와 불변 조건을 Architecture Decision으로 명확히 고정해야 한다.

## Goal

QH-V2-WORKER-DIAG-001과 QH-V2-WORKER-ROB-002의 객관적 Evidence를 검토하여 Candidate A - Deterministic Worker Brief를 production Worker input 경로에 채택할지 Human Architecture Gate에서 결정하고, 승인된 경우 그 경계와 불변 조건을 ADR-018로 기록한다.

이 Task는 Architecture 결정과 다음 implementation Task의 경계만 정의한다. production Worker/Runner 코드는 이 Task에서 수정하지 않는다.

## Architecture Basis

- Repository 문서와 Git이 Source of Truth다.
- Qwen self-report는 completion Evidence가 아니다.
- deterministic Harness가 Scope, Tool authority, Verification, Final Gate를 소유한다.
- FR-004에 따라 Worker는 명시적으로 할당된 current Task만 수행하며 successor를 선택하거나 시작하지 않는다.
- ADR-008의 backend-neutral Worker/tool interaction contract는 유지한다.
- ADR-009의 bounded Retry/safe-stop semantics는 유지한다.
- ADR-014의 one WorkerStep에서 0개 또는 1개의 ToolRequest만 허용하는 deterministic SAFETY 경계는 유지한다.
- ADR-017의 Exception-Driven Human Supervision은 Worker authority 확대가 아니다.
- QH-V2-OPS-GIT-001의 safe remote handoff 경로를 유지한다.
- `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.

## Evidence Basis

Architecture review는 다음 tracked Evidence만 근거로 한다.

- `tasks/QH-V2-WORKER-DIAG-001.md`
- `docs/WORKER_DIAG_001_EVIDENCE.md`
- `tasks/QH-V2-WORKER-ROB-002.md`
- `docs/WORKER_ROB_002_EVIDENCE.md`
- `docs/WORKER_ROB_002_RESULTS.json`

QH-V2-WORKER-ROB-002에서 확인된 핵심 수치:

| Variant | Transport Success | Timeout | Valid bounded first step | Median completed latency |
|---|---:|---:|---:|---:|
| Stable - Full Task | 60% | 40% | 6/10 | 10.529s |
| Candidate A - Deterministic Worker Brief | 100% | 0% | 10/10 | 2.013s |
| Candidate B - Brief + One-Step Instruction | 70% | 30% | 2/10 | 20.778s |

세 variant 모두 multi-tool SAFETY shape 0, scope-incompatible request 0, benchmark 실행 write 0이었다.

## Candidate A Definition

Candidate A는 원본 tracked Task를 대체하는 요약문이 아니다.

Deterministic Worker Brief는 원본 Task text에서 다음 section을 exact projection으로 복사한다.

- Task identity/title
- `Goal`
- `Architecture Basis`
- `Dependencies`
- `Scope`
- `Allowed Changes`
- `Forbidden Changes`
- `Acceptance Criteria`
- `Stop Conditions`

고정 문구로 다음을 명시한다.

- original tracked Task remains the Source of Truth;
- Worker Brief grants no authority beyond the original Task;
- Verification and Final Gate remain Harness-owned.

Required section이 없거나 중복되면 fail closed해야 한다. LLM paraphrasing, semantic summarization, requirement ranking/omission/inference는 허용하지 않는다.

## Human Architecture Gate

이 Task의 contract 승인 자체는 Candidate A production promotion 승인이 아니다.

ADR-018을 `Accepted`로 기록하기 전에 Human에게 다음 선택지를 제시한다.

1. **ACCEPT Candidate A** - Deterministic Worker Brief를 production Worker input 경로에 채택하고 QH-V2-WORKER-ROB-003에서 최소 integration을 구현한다.
2. **REJECT / DEFER** - Stable full Task input을 유지하고 별도 diagnosis/design으로 돌아간다.
3. **MORE EVIDENCE REQUIRED** - production promotion 전 추가 격리 실험을 요구한다.

ChatGPT의 기술 추천은 Evidence가 현재 상태로 유지된다면 **1. ACCEPT Candidate A**다. 이유는 Candidate A만 predefined promotion threshold를 충족했고 Stable 대비 reliability와 latency가 모두 크게 개선됐으며 Candidate B의 추가 one-step instruction은 오히려 성능을 악화시켰기 때문이다.

Human의 명시적 선택 전에는 ADR-018을 Accepted로 확정하지 않는다.

## Human Architecture Gate Result

2026-08-25 Human은 **1. ACCEPT Candidate A**를 명시적으로 선택하고 Candidate A - Deterministic Worker Brief의 production promotion Architecture를 승인했다.

이 승인은 다음 불변 조건을 유지한다.

- original tracked Task가 유일한 Source of Truth다.
- Candidate B one-step instruction은 채택하지 않는다.
- `qwen3:8b`, `think:false`, timeout `30.0`초를 유지한다.
- Worker step budget, Retry policy, tool schema와 tool authority를 유지한다.
- FR-004 Worker successor 금지와 Verification, Final Gate, lifecycle, Git authority를 유지한다.
- `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.
- QH-V2-ARCH-018이 `COMPLETE - VERIFIED`에 도달하기 전에는 QH-V2-WORKER-ROB-003을 시작하지 않는다.

## Accepted Production Boundary

ADR-018은 다음을 고정한다.

1. production Worker initial request는 full Task text 대신 deterministic Worker Brief를 사용할 수 있다.
2. original tracked Task가 유일한 Source of Truth다.
3. Brief는 exact section projection이며 LLM summary가 아니다.
4. missing/duplicated required section은 fail closed다.
5. Candidate B의 fixed one-step instruction은 채택하지 않는다.
6. model은 `qwen3:8b` 그대로 유지한다.
7. `think:false` 그대로 유지한다.
8. timeout `30.0` seconds 그대로 유지한다.
9. Worker step budget과 Retry policy를 변경하지 않는다.
10. tool schema와 tool authority를 변경하지 않는다.
11. multi-tool split/repair를 추가하지 않는다.
12. Verification, Final Gate, lifecycle, Git authority를 변경하지 않는다.
13. Worker successor selection을 허용하지 않는다.
14. production integration은 별도 QH-V2-WORKER-ROB-003에서 구현·테스트한다.
15. `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.

## Scope

- Evidence를 바탕으로 Candidate A production promotion Architecture를 검토한다.
- Human Architecture Gate 결과를 ADR-018에 기록한다.
- Accepted인 경우 QH-V2-WORKER-ROB-003의 implementation boundary와 non-goals를 명확히 한다.
- BACKLOG의 현재 순서를 해당 결정과 일치시킨다.
- production code는 수정하지 않는다.

## Allowed Changes

- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-ARCH-018.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `README.md`
- `tools/**`
- `tests/**`
- `src/**`
- `ops/**`
- `experiments/**`
- `docs/**`
- 현재 Task 이외의 `tasks/**`
- production Worker prompt/runtime integration
- Candidate B one-step instruction production adoption
- model 변경 또는 model routing
- `think` 정책 변경
- timeout 변경
- Worker step budget 변경
- Retry attempt/classification 변경
- tool schema/tool authority 변경
- multi-tool split/repair/continuation behavior 변경
- Verification/Final Gate/lifecycle/Git authority 변경
- Worker successor selection 권한 확대
- Globalization 승인

## Acceptance Criteria

1. Human Architecture Gate의 명시적 선택이 기록된다.
2. Candidate A가 Accepted인 경우 `DECISIONS.md`에 `ADR-018`이 Accepted로 기록된다.
3. ADR-018은 Candidate A를 deterministic exact-section projection으로 정의하고 original Task가 Source of Truth임을 명시한다.
4. Candidate B one-step instruction은 production 경로에서 채택하지 않음을 명시한다.
5. model `qwen3:8b`, `think:false`, timeout `30.0`, current Worker step budget, Retry policy, tool schema/authority가 변경되지 않음을 명시한다.
6. FR-004의 Worker successor 금지와 deterministic Verification/Final Gate authority가 유지된다.
7. production integration은 별도 `QH-V2-WORKER-ROB-003` Task로 분리된다.
8. `BACKLOG.md`의 현재 순서는 `QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003`과 충돌하지 않는다.
9. `GLOBALIZATION = NOT AUTHORIZED`가 유지된다.
10. production code/test/Evidence artifact 변경이 없다.
11. Allowed Changes만 발생한다.
12. `git diff --check`가 PASS한다.

## Verification

Human이 ACCEPT Candidate A를 선택했으므로 다음 Accepted 전용 Verification을 사용한다.

Run exactly:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8'); required=['ADR-018','Accepted','Candidate A','Deterministic Worker Brief','original tracked Task','Source of Truth','QH-V2-WORKER-ROB-003','qwen3:8b','think:false','30.0','GLOBALIZATION = NOT AUTHORIZED']; missing=[x for x in required if x not in d]; assert not missing,missing"`

Run exactly:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8'); b=Path('BACKLOG.md').read_text(encoding='utf-8'); required=['Candidate B','QH-V2-ARCH-018','QH-V2-WORKER-ROB-003','QH-V2-OPS-003','FR-004']; text=d+'\n'+b; missing=[x for x in required if x not in text]; assert not missing,missing"`

Run exactly:

`git diff --check`

Run exactly:

`git status --short`

Human이 REJECT / DEFER 또는 MORE EVIDENCE REQUIRED를 선택하면 Accepted 전용 Verification을 그대로 사용하지 말고, Human 선택에 맞는 exact check-only Verification으로 이 Task 계약을 먼저 수정·재승인한 뒤 진행한다.

## Verification Budget

이 Task는 Architecture 문서 전용이므로 Python production regression을 실행하지 않는다.

- 설계 검토 중에는 tracked Evidence와 문서 diff만 확인한다.
- 최종 `qh close <exact implementation HEAD>`가 승인된 Verification과 scope/Final Gate를 authoritative하게 한 번 실행한다.
- production code/test 변경이 발견되면 STOP한다.

## Evidence Requirements

- exact contract baseline SHA
- QH-V2-WORKER-ROB-002 핵심 metric 재확인
- Human Architecture Gate의 명시적 선택
- ADR-018의 exact disposition
- Accepted인 경우 Candidate A boundary와 Candidate B rejection/defer 이유
- changed paths가 Allowed에 한정됨
- `git diff --check` PASS
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS
- Final Gate 이후 별도 lifecycle commit

## Stop Conditions

다음이면 STOP하고 Human/ChatGPT review를 요청한다.

- Human Architecture Gate 선택이 없음
- Evidence와 Candidate A recommendation이 충돌함
- Candidate A production integration을 이 Architecture Task에서 직접 구현해야 하는 상황
- model/think/timeout/Retry/step budget/tool authority 변경이 필요함
- Candidate B one-step policy를 함께 채택해야 한다는 새로운 Evidence가 나타남
- Worker successor selection 또는 autonomous queue authority 확대가 필요함
- Verification/Final Gate/lifecycle/Git authority 변경이 필요함
- Requirements 변경이 필요함
- Globalization 또는 Trust Boundary 확대가 필요함

## Next Task

Human이 Candidate A를 ACCEPT하고 QH-V2-ARCH-018이 `COMPLETE - VERIFIED`에 도달한 경우 다음 구현 Task는:

`QH-V2-WORKER-ROB-003 - Deterministic Worker Brief Production Integration`

이 successor는 별도 Task contract, scope, tests와 authoritative Final Gate를 가져야 한다.
