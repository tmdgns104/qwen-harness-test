# QH-V2-WORKER-ROB-003 - Deterministic Worker Brief Production Integration

## Status

COMPLETE - VERIFIED

## Problem

QH-V2-WORKER-ROB-002의 격리 실험에서 Candidate A - Deterministic Worker Brief는 Stable full Task input보다 높은 initial-step reliability와 낮은 latency를 기록했고 predefined promotion threshold를 충족했다. QH-V2-ARCH-018의 Human Architecture Gate는 Candidate A를 production Worker initial request input 방식으로 Accepted했다.

현재 production `tools/task_runner.py`는 original tracked Task 전체를 `WorkerRequest.task_text`로 전달한다. ADR-018을 실제 runtime에 반영하려면 original Task의 scope와 authority를 그대로 유지하면서 initial Worker input만 deterministic exact-section Brief로 바꾸는 최소 integration이 필요하다.

## Goal

Candidate A의 deterministic exact-section Worker Brief를 production Single-Task Runner의 initial Worker input에 최소 통합한다.

original tracked Task는 유일한 Source of Truth로 유지한다. Runner는 original Task에서 ChangeScope를 파싱하고 tool authorization을 계속 강제하며, WorkerRequest에만 exact projection Brief를 전달한다.

## Architecture Basis

- ADR-018은 Candidate A - Deterministic Worker Brief의 production promotion을 Accepted했다.
- original tracked Task가 유일한 Source of Truth다.
- Brief는 LLM 요약이 아니라 tracked Task의 exact section projection이다.
- required section 누락 또는 중복은 Worker session 생성 전에 fail closed한다.
- ADR-008의 backend-neutral Worker/tool interaction contract를 유지한다.
- ADR-009의 bounded Retry/safe-stop semantics를 유지한다.
- ADR-014의 한 WorkerStep당 0개 또는 1개의 ToolRequest SAFETY 경계를 유지한다.
- FR-004에 따라 Worker는 current Task만 수행하며 successor를 선택하거나 시작하지 않는다.
- deterministic Harness가 Scope, Verification, Final Gate, lifecycle과 Git authority를 계속 소유한다.
- `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.

## Dependencies

- QH-V2-WORKER-ROB-002 = `COMPLETE - VERIFIED`이며 tracked Evidence가 Candidate A만 promotion threshold를 충족했음을 기록한다.
- QH-V2-ARCH-018 = `COMPLETE - VERIFIED`; exact completion commit은 `adb5c9f0aacf863679cd978a924b82bf3ce1d867`이고 lifecycle commit `97251f4e24579c9a84ec16d39f05519a22462906`이 `origin/main`에 반영돼 있다.
- ADR-018 = `Accepted`.

## Production Design

### Deterministic Worker Brief

production projector는 original tracked Task text에서 다음만 exact-copy한다.

- Task identity/title
- `Goal`
- `Architecture Basis`
- `Dependencies`
- `Scope`
- `Allowed Changes`
- `Forbidden Changes`
- `Acceptance Criteria`
- `Stop Conditions`

Brief에는 다음 authority statement를 고정한다.

`The original tracked Task remains the Source of Truth. This Worker Brief grants no authority beyond the original Task. Verification and Final Gate remain Harness-owned.`

required title/section이 없거나 중복되면 `ValueError`로 fail closed한다. LLM paraphrasing, semantic summarization, requirement ranking, omission, inference를 사용하지 않는다.

### Runner Integration

1. Runner는 current ACTIVE Task file 전체를 기존처럼 읽는다.
2. Runner는 original Task 전체에서 ChangeScope를 기존처럼 파싱한다.
3. Runner는 original Task에서 deterministic Worker Brief를 생성한다.
4. Runner는 initial `WorkerRequest.task_text`에 Brief만 넣는다.
5. Tool validation/execution과 continuation loop는 기존 scope와 policy를 그대로 사용한다.

## Scope

- Candidate A projector를 production code로 구현한다.
- Single-Task Runner initial WorkerRequest가 full Task 대신 Brief를 사용하게 한다.
- exact projection, authority statement, fail-closed behavior와 Runner integration을 unit test로 검증한다.
- original Task 기반 scope/tool enforcement가 유지됨을 기존 Runner regression으로 검증한다.
- production code 밖의 Candidate B 실험 경로는 수정하지 않는다.

## Allowed Changes

- `tools/worker_brief.py`
- `tools/task_runner.py`
- `tests/test_worker_brief.py`
- `tests/test_task_runner.py`
- `STATUS.md`
- `tasks/QH-V2-WORKER-ROB-003.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `README.md`
- `docs/**`
- `experiments/**`
- `tools/ollama_worker.py`
- `tools/retry_runner.py`
- `tools/harness_core.py`
- `tools/repo_tools.py`
- `tools/qh.py`
- `ops/**`
- 현재 Task 이외의 `tasks/**`
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

모든 미기재 경로는 default-denied다.

## Acceptance Criteria

1. production Worker Brief는 Task title과 ADR-018의 8개 required section을 original tracked Task에서 exact-copy한다.
2. original tracked Task가 유일한 Source of Truth이고 Brief가 추가 authority를 부여하지 않는다는 고정 statement가 포함된다.
3. production projector는 LLM 또는 semantic summarization을 사용하지 않는다.
4. required Task title 또는 section이 없거나 중복되면 fail closed한다.
5. Single-Task Runner는 original Task에서 ChangeScope를 파싱하고 initial WorkerRequest에만 Brief를 전달한다.
6. Candidate B one-step instruction은 production Worker input에 포함되지 않는다.
7. `qwen3:8b`, `think:false`, timeout `30.0`, `MAX_WORKER_STEPS`, `MAX_RUNNER_ATTEMPTS`, tool schema/authority가 변경되지 않는다.
8. 기존 zero-or-one ToolRequest, lifecycle-path write denial과 original Task scope enforcement가 유지된다.
9. FR-004, Verification, Final Gate, lifecycle, Git authority가 변경되지 않는다.
10. production code는 `experiments.worker_rob_002`를 import하지 않는다.
11. focused projector/Runner tests와 Retry/Adapter regression이 PASS한다.
12. 실제 changed paths는 Allowed Changes에 한정된다.
13. `git diff --check`가 PASS한다.
14. `GLOBALIZATION = NOT AUTHORIZED`가 유지된다.

## Verification

Run exactly:

`python -m unittest tests.test_worker_brief tests.test_task_runner`

Run exactly:

`python -m unittest tests.test_retry_runner tests.test_ollama_worker`

Run exactly:

`python -c "from pathlib import Path; from tools.ollama_worker import DEFAULT_MODEL,DEFAULT_TIMEOUT_SECONDS; from tools.task_runner import MAX_WORKER_STEPS; from tools.retry_runner import MAX_RUNNER_ATTEMPTS; b=Path('tools/worker_brief.py').read_text(encoding='utf-8'); r=Path('tools/task_runner.py').read_text(encoding='utf-8'); o=Path('tools/ollama_worker.py').read_text(encoding='utf-8'); required=['original tracked Task remains the Source of Truth','Goal','Architecture Basis','Dependencies','Scope','Allowed Changes','Forbidden Changes','Acceptance Criteria','Stop Conditions']; missing=[x for x in required if x not in b]; assert not missing,missing; assert 'build_worker_brief(task_markdown)' in r; assert 'experiments.worker_rob_002' not in r+b; assert DEFAULT_MODEL == 'qwen3:8b'; assert DEFAULT_TIMEOUT_SECONDS == 30.0; assert chr(34)+'think'+chr(34)+': False' in o; assert MAX_WORKER_STEPS == 8; assert MAX_RUNNER_ATTEMPTS == 2"`

Run exactly:

`git diff --check`

Run exactly:

`git status --short`

## Verification Budget

- RED/GREEN 개발 중에는 `tests.test_worker_brief`와 필요한 `tests.test_task_runner`만 focused 실행한다.
- 구현 완료 후 위 Verification을 한 번 실행한다.
- 최종 authoritative Verification과 scope/Final Gate는 `qh close <exact implementation HEAD>`에서 실행한다.
- live Ollama benchmark는 이 deterministic integration Task의 close 명령으로 재실행하지 않는다.

## Evidence Requirements

- exact Task contract baseline SHA
- focused RED가 production projector/integration 부재를 검출한 Evidence
- focused GREEN 및 Runner regression exit 0
- Retry/Adapter regression exit 0
- original Task와 generated Brief의 exact-section 비교 Evidence
- Candidate B one-step instruction 부재 Evidence
- model/think/timeout/step/Retry/tool authority 불변 Evidence
- Allowed Changes만 발생
- exact implementation HEAD 기반 authoritative `qh close` Final Gate PASS
- Final Gate 이후 별도 lifecycle commit
- safe fast-forward `HEAD:main` push

## Stop Conditions

다음이면 STOP하고 Human/ChatGPT review를 요청한다.

- exact projection만으로 original Task authority를 유지할 수 없음
- Candidate B one-step instruction이 필요함
- model, think, timeout, Worker step budget, Retry policy 또는 tool schema/authority 변경이 필요함
- WorkerRequest/WorkerStep public contract 변경이 필요함
- multi-tool split/repair 또는 새로운 continuation policy가 필요함
- FR-004 Worker successor 금지 변경이 필요함
- Verification/Final Gate/lifecycle/Git authority 변경이 필요함
- Requirements, Architecture 또는 Trust Boundary 변경이 필요함
- Globalization이 필요함
- production integration이 반복적으로 deterministic Verification을 통과하지 못함

## Next Task

QH-V2-WORKER-ROB-003이 `COMPLETE - VERIFIED`에 도달한 뒤 다음 후보는:

`QH-V2-OPS-003`

이 Task는 successor를 자동 시작하지 않는다.
