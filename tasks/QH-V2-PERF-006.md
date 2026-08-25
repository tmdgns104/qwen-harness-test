# QH-V2-PERF-006 - Authoritative Close Runtime and Observability Optimization

## Status

COMPLETE - VERIFIED

## Problem

QH-V2-OPS-003의 authoritative `qh close`는 exact implementation HEAD에서 10분 이상 장시간 실행되었고, child Verification output이 `subprocess.run(..., capture_output=True)`에 의해 command 종료까지 보이지 않아 실행 중간에 현재 단계와 진행 상태를 확인하기 어려웠다.

QH-V2-OPS-003의 tracked Follow-up Observation도 다음을 기록한다.

- authoritative `qh close`가 long-running이었다.
- child output이 buffered되어 incremental visible progress가 없었다.
- buffering, Verification coverage, Final Gate, qh authority 변경은 별도 performance/operations Task에서만 검토해야 한다.

기존 performance Evidence도 이미 관련 병목을 확인했다.

- QH-V2-PERF-004는 normal workflow의 duplicate full Verification을 제거하고 `qh close` 1회를 authoritative final path로 유지했다.
- QH-V2-PERF-005는 selected regression을 560.059s에서 422.114s로 24.63% 개선했지만, remaining dominant cost가 production qh review/close Git subprocess behavior라고 기록했다.
- Verification concurrency는 QH-V2-PERF-001에서 효과가 미미하고 개별 suite를 느리게 해 rejected 상태다.

현재 문제는 Final Gate를 약화하는 것이 아니라, authoritative close가 오래 걸릴 때 Harness가 진행 상황을 충분히 노출하지 못하고, close/review 경로의 남은 orchestration/Git overhead도 아직 Evidence 기반으로 정리되지 않았다는 점이다.

## Goal

authoritative `qh close`의 Verification/Final Gate 의미와 강도를 그대로 유지하면서 다음 두 가지를 달성한다.

1. 장시간 Verification command가 실행 중일 때 Harness가 실시간으로 current command, elapsed time, completion/exit status를 표시하여 외부 Supervisor가 반복 polling 없이 실행 상태를 이해할 수 있게 한다.
2. `qh review` / `qh close` 경로의 orchestration 및 Git subprocess overhead를 측정하고, 동일 Evidence 강도를 유지하면서 제거 가능한 deterministic redundancy만 최소한으로 최적화한다.

이 Task는 테스트를 줄이거나 PASS를 재사용해서 시간을 단축하는 Task가 아니다.

## Human Selection

2026-08-25 Human은 QH-V2-OPS-003 완료 후 QH-V2-OPS-004보다 이 performance/observability 개선을 먼저 수행하는 방향을 승인했다.

따라서 queue intent는 다음과 같다.

`QH-V2-OPS-003 -> QH-V2-PERF-006 -> QH-V2-OPS-004`

이 Task의 완료가 unattended autonomous queue authority를 부여하지 않는다.

## Architecture Basis

- Repository 문서와 Git/Test Evidence가 Source of Truth다.
- `qh close <exact implementation HEAD>`는 계속 authoritative final Verification / scope / Final Gate 경로다.
- QH-V2-PERF-001의 Verification concurrency rejection을 유지한다.
- QH-V2-PERF-004의 duplicate full Verification 제거 정책을 유지한다.
- QH-V2-PERF-005의 test-isolation 및 Evidence-strength 보존 원칙을 유지한다.
- ADR-017의 Exception-Driven Human Supervision은 approval cadence만 다루며 qh/Worker authority 확대가 아니다.
- FR-004의 Worker successor selection 금지를 유지한다.
- `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.

## Dependencies

- QH-V2-PERF-001 through QH-V2-PERF-005는 completed historical performance Evidence로 유지한다.
- QH-V2-OPS-003 = `COMPLETE - VERIFIED`.
- QH-V2-OPS-003 implementation commit = `905d575969936216b5648e07f8622c0f23208d58`.
- QH-V2-OPS-003 lifecycle commit = `8338e9a1b09e48a8be648bf03889ab6c02f5445e`.
- QH-V2-OPS-004는 이 Task가 완료되기 전 시작하지 않는다.

## Scope

### Stage A - Close / Verification Observability

- Verification command 실행 직전에 command index/total과 command identity를 즉시 출력한다.
- progress 출력은 명시적으로 flush되어 long-running command 시작 상태가 즉시 보이게 한다.
- long-running command가 아직 실행 중임을 알 수 있도록 bounded periodic heartbeat를 제공한다.
- heartbeat는 elapsed wall-clock time을 포함하며 Verification command 자체를 재실행하거나 병렬 실행하지 않는다.
- command 종료 시 exit code와 elapsed duration을 출력한다.
- `qh close`의 major phase도 최소한 review start/end, post-Verification integrity check, Final Gate/lifecycle transition을 구분할 수 있게 한다.
- child stdout/stderr와 `VerificationCommandResult` Evidence 의미는 보존한다.

### Stage B - Runtime Profiling and Safe Deduplication

- current `qh review` / `qh close` 경로의 phase timing과 Git subprocess 호출 수를 deterministic test/profiling Evidence로 측정한다.
- duplicated repository-root validation, HEAD/type resolution, clean-state or changed-path probes 등 동일 실행 내에서 의미가 중복되는 Git calls가 있는지 확인한다.
- fail-closed semantics와 final Evidence freshness를 유지하면서 명백히 중복인 call만 제거할 수 있다.
- stale PASS cache, persisted receipt, Verification skip, test skip, cross-run cache는 사용할 수 없다.
- 안전한 runtime reduction이 입증되지 않으면 관측 결과를 기록하고 불필요한 복잡성은 추가하지 않는다. Observability 개선 자체는 독립적으로 유효하다.

## Allowed Changes

- `tools/harness_core.py`
- `tools/qh.py`
- `tests/test_harness_core.py`
- `tests/test_qh.py`
- `tests/test_qh_progress.py`
- `docs/DEVELOPMENT.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-PERF-006.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `README.md`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `tools/worker_brief.py`
- `ops/qhops/**`
- `experiments/**`
- 현재 Task 이외의 `tasks/**`
- Verification command 삭제 또는 축소
- test 삭제, new skip, assertion weakening
- cached/persisted PASS 또는 stale Verification Evidence 재사용
- Verification concurrency 또는 parallel suite 실행
- `qh close` authoritative authority 변경
- Final Gate / ChangeScope / lifecycle semantics 변경
- command failure를 숨기거나 success로 재해석
- background process를 남기고 `qh close`가 먼저 성공 반환하는 동작
- model / `think` / timeout / Worker step budget / Retry policy 변경
- tool schema / tool authority 변경
- Worker successor selection 권한 확대
- Git push/branch authority 확대
- Globalization 승인

All unlisted Repository paths remain default-denied.

## Acceptance Criteria

1. `qh verify`, `qh review`, `qh close`에서 Verification command 시작이 command 종료 전에 즉시 사용자에게 보인다.
2. long-running command는 bounded heartbeat를 출력하여 살아 있는 process임을 확인할 수 있다.
3. heartbeat는 elapsed time을 표시하고 command execution 순서/횟수/exit semantics를 변경하지 않는다.
4. command completion progress는 exact exit code와 elapsed duration을 표시한다.
5. progress/timing output은 명시적으로 flush되어 stdout buffering 때문에 parent progress까지 늦게 보이지 않는다.
6. Verification commands는 기존 contract 순서대로 정확히 한 번씩 순차 실행된다.
7. child stdout/stderr는 기존 `VerificationCommandResult` Evidence로 보존된다.
8. progress reporter 자체 오류가 Verification PASS를 위조하거나 child failure를 성공으로 바꾸지 않는다.
9. heartbeat용 monitoring이 있다면 Verification command를 병렬 실행하지 않으며 process ownership/termination semantics를 바꾸지 않는다.
10. `qh close`는 exact implementation HEAD와 clean-state/fresh Evidence를 계속 요구한다.
11. `qh close`의 scope review, `git diff --check`, Final Gate와 lifecycle mutation ordering은 변경되지 않는다.
12. Stage B는 before/after Git subprocess count 또는 phase timing Evidence를 기록한다.
13. retained runtime optimization은 동일 fixture/host 조건에서 measurable improvement 또는 deterministic call-count reduction을 보여야 한다.
14. measurable benefit이 없는 복잡한 optimization은 retained하지 않는다.
15. QH-V2-PERF-001에서 rejected된 Verification concurrency를 재도입하지 않는다.
16. `BACKLOG.md`는 Human-selected order `QH-V2-OPS-003 -> QH-V2-PERF-006 -> QH-V2-OPS-004`를 반영한다.
17. production Worker/Runner/Retry/model/tool behavior는 변경되지 않는다.
18. `GLOBALIZATION = NOT AUTHORIZED`가 유지된다.
19. Allowed Changes만 발생한다.
20. `git diff --check`가 PASS한다.

## Verification

Run exactly:

`python -m unittest tests.test_qh_progress`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -c "from pathlib import Path; b=Path('BACKLOG.md').read_text(encoding='utf-8'); required=['QH-V2-OPS-003','QH-V2-PERF-006','QH-V2-OPS-004']; missing=[x for x in required if x not in b]; assert not missing,missing; assert b.index('QH-V2-OPS-003') < b.index('QH-V2-PERF-006') < b.index('QH-V2-OPS-004')"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Verification Budget

- 개발 중에는 `tests.test_qh_progress`와 변경 지점의 focused RED/GREEN tests만 사용한다.
- implementation commit 전에 full `tests.test_harness_core` 또는 full `tests.test_qh`를 별도로 반복 실행하지 않는다.
- implementation이 focused Evidence로 안정화되면 commit을 만들고, authoritative `qh close <exact implementation HEAD>`가 위 Verification contract 전체를 최종적으로 **한 번** 실행한다.
- `qh close` PASS 후에는 같은 full regression을 단순 확인 목적으로 다시 실행하지 않는다.
- deterministic FAIL이 발생하면 원인을 수정하고 focused test로 확인한 뒤 새 exact implementation HEAD에서 `qh close`를 다시 수행한다. 실패한 Final Gate를 우회하거나 이전 PASS를 재사용하지 않는다.
- 이 Task의 successful final `qh close` 자체가 새 progress/timing behavior의 real operational Evidence가 되어야 한다.

## Evidence Requirements

- exact contract baseline SHA
- OPS-003 tracked Follow-up Observation 재확인
- PERF-004 / PERF-005 historical performance basis
- focused RED Evidence: 기존 path에서 incremental progress/heartbeat가 없음을 테스트로 재현
- GREEN Evidence: start, heartbeat, completion, elapsed timing이 command 완료 전후에 올바르게 발생함
- command order/count가 변경되지 않았다는 Evidence
- child stdout/stderr/exit code 보존 Evidence
- heartbeat가 Verification concurrency가 아니라 reporting-only임을 입증하는 test
- Stage B before/after Git subprocess count 또는 phase timing table
- retained optimization의 measurable result 또는 `NO MATERIAL RUNTIME DEDUP RETAINED` 기록
- final `qh close` 실제 progress/timing output
- changed paths가 Allowed에 한정됨
- `git diff --check` PASS
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS
- Final Gate 이후 별도 lifecycle commit
- safe fast-forward push 후 final working tree clean

## Implementation Evidence

- Exact contract baseline: `6342a80ad1c7cecd4a20a5f6eeaec59aa1da73c5`.
- OPS-003의 tracked Follow-up Observation과 PERF-004/PERF-005 historical basis를
  구현 전에 재확인했다.
- Focused RED `python -m unittest tests.test_qh_progress`는 start visibility,
  heartbeat, completion timing, close phase 부재를 4개 assertion failure로 재현했다.
- Focused GREEN은 6 tests PASS이며 command start-before-completion, elapsed heartbeat,
  exact exit/stdout/stderr 보존, reporting-only monitoring, 순차 1회 실행을 입증한다.
- 기존 변경 지점 focused regression은 Harness execution 12 tests PASS와 qh
  verify/review/close 5 tests PASS다.
- Stage B deterministic profile은 RED/GREEN 모두 `qh close` `_run_git` 15 calls를
  기록했다. freshness boundary를 합치는 최적화는 유지하지 않았다:
  `NO MATERIAL RUNTIME DEDUP RETAINED`.
- Verification concurrency, coverage 축소, cached PASS, skip 또는 authority 변경은 없다.
- authoritative close 전체 Verification과 Final Gate Evidence는 exact implementation
  HEAD에서 lifecycle 변경 전에 한 번만 실행한다.
- Authoritative close는 exact implementation HEAD
  `d4befcb41dabf230ded83938c83546db1b716700`에서 한 번 실행되어 Final Gate PASS했다.
  실제 command completion timing은 progress tests `41.6s`, Harness Core `166.6s`,
  qh regression `1232.5s`, Backlog order `0.1s`, contract diff check `1.6s`, status
  check `1.6s`였고 모두 exit `0`이었다.
- 실제 close phase timing은 review `1457.5s`, post-Verification integrity `5.2s`,
  lifecycle transition `0.0s`였다. review 동안 30초 heartbeat가 반복 노출되었고
  post-Verification HEAD는 exact implementation HEAD와 일치했다.

## Stop Conditions

STOP하고 Human/ChatGPT review를 요청한다 if completion requires:

- Verification command 수/coverage 감소
- test 삭제/skip/assertion weakening
- stale/cached PASS reuse
- Verification concurrency 또는 command parallelization
- command output/progress 때문에 child exit semantics 변경
- `qh close`가 child process 종료 전에 성공 반환
- Final Gate/ChangeScope/lifecycle authority 변경
- Architecture 또는 Requirements 변경
- Worker/Runner/Retry/model/tool authority 변경
- automatic successor start 또는 unattended queue authority
- Git divergence/destructive recovery
- Globalization 또는 Trust Boundary 확대

Long-running verification 자체는 failure가 아니다. Progress output이 정상적으로 계속되고 process가 살아 있다면 arbitrary timeout 증가나 Verification 우회를 하지 않는다.

## Next Task

QH-V2-PERF-006이 `COMPLETE - VERIFIED`에 도달하면 successor candidate는:

`QH-V2-OPS-004`

QH-V2-OPS-004가 Repository에서 exact approved successor이고 ADR-017 normal-continuation 조건을 모두 충족하는 경우에만 external Supervisor가 다음 lifecycle을 진행할 수 있다. Qwen Worker 자체는 successor를 선택하거나 시작하지 않는다.
