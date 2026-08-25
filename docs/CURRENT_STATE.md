# Qwen Harness Current State

이 문서는 GitHub에서 프로젝트의 **현재 상태를 빠르게 확인하기 위한 최신 스냅샷**입니다.

현재 lifecycle의 최종 권위는 항상 [`STATUS.md`](../STATUS.md)이며, Architecture 결정은 [`DECISIONS.md`](../DECISIONS.md), Task 계약과 Evidence는 [`tasks/`](../tasks/)가 우선합니다. 이 문서는 그 정보를 사람이 빠르게 읽을 수 있도록 요약합니다.

## 기준 시점

- 기준일: 2026-08-25
- GitHub `main` 기준 문서 동기화 전 HEAD: `328453591a16e1fb10cac77979427df439168eed`
- 마지막 완료 Task: `QH-V2-PERF-007`
- PERF-007 implementation HEAD: `031dcae9beaef2db2730fbb81051fff7c3a40e79`
- PERF-007 lifecycle commit: `7ea2f389b7bd03858325dc38d7c72e0615653847`
- Current Task 상태: `QH-V2-PERF-007 - COMPLETE - VERIFIED`
- Next Planned Task: `NOT SET - HUMAN SELECTION REQUIRED`
- `GLOBALIZATION = NOT AUTHORIZED`

## 현재까지 구현된 핵심 기능

| 영역 | 현재 상태 |
|---|---|
| Deterministic Harness Core | 구현/검증 완료 |
| ChangeScope / Git Evidence / Verification / Final Gate | 구현/검증 완료 |
| Native Ollama + `qwen3:8b` Worker | 구현/검증 완료 |
| Repository read / scoped write tools | 구현/검증 완료 |
| Single-Task Runner | 구현/검증 완료 |
| Bounded Retry / Safe Stop | 구현/검증 완료 |
| `qh task-new` | 구현/검증 완료 |
| `qh doctor` | 구현/검증 완료 |
| safe remote handoff (`qh handoff-check`) | 구현/검증 완료 |
| Deterministic Worker Brief (Candidate A) | Architecture 승인 및 production integration 완료 |
| Windows `qh.cmd` launcher | 구현/검증 완료 |
| long-running Verification progress/heartbeat | 구현/검증 완료 |
| Git-heavy test fixture optimization | PERF-007에서 추가 개선 완료 |

## 최근 주요 완료 흐름

```text
QH-V2-WORKER-ROB-002
  -> QH-V2-OPS-GIT-001
  -> QH-V2-DOC-KO-001
  -> QH-V2-ARCH-018
  -> QH-V2-WORKER-ROB-003
  -> QH-V2-OPS-003
  -> QH-V2-PERF-006
  -> QH-V2-PERF-007
  -> CURRENT: Architecture Review Required
```

### Candidate A production integration

`QH-V2-ARCH-018`에서 Candidate A - Deterministic Worker Brief를 Accepted했고, `QH-V2-WORKER-ROB-003`에서 production initial Worker input에 최소 통합했습니다.

유지된 경계:

- original tracked Task가 Source of Truth
- Brief는 정해진 section의 deterministic exact projection
- Candidate B one-step instruction은 채택하지 않음
- `qwen3:8b`, `think:false`, timeout `30.0` 유지
- Worker step budget / Retry / tool schema와 authority 유지
- FR-004 successor-selection 금지 유지
- Verification / Final Gate / lifecycle / Git authority 유지

## 현재 가장 큰 미해결 문제: authoritative close runtime

`QH-V2-PERF-006`은 장시간 `qh close`가 무엇을 실행 중인지 보이지 않던 문제를 해결했습니다.

현재 Verification은 다음을 즉시 표시합니다.

```text
Verification [n/total] START
Verification [n/total] HEARTBEAT elapsed=...
Verification [n/total] COMPLETE exit=... duration=...
```

따라서 process가 살아 있는지 확인하려고 외부 Supervisor가 계속 짧게 polling할 필요는 줄었습니다.

하지만 **실제 실행시간 자체는 아직 실사용 목표를 만족하지 않습니다.**

### PERF-007 Evidence

| 측정 | Before | After | 변화 |
|---|---:|---:|---:|
| focused 14 Git-heavy tests | 551.646 s | 357.777 s | -35.15% |
| Git process starts | 284 | 203 | -28.52% |
| final `tests.test_qh` | PERF-006 1232.5 s | PERF-007 1157.8 s | -6.06% |
| final full Verification | - | 1600.9 s | 300 s 초과 |
| final review phase | PERF-006 1457.5 s | PERF-007 1613.8 s | 300 s 초과 |

PERF-007의 fixture 최적화 자체는 성공했고 Final Gate도 PASS했습니다. 그러나 focused 14 tests만으로도 300초를 초과했으며, 현재 Windows 환경에서는 개별 Git subprocess가 대략 1.6~1.9초 수준으로 관찰되었습니다.

따라서 현재 계약의 practical-runtime disposition은:

`ARCHITECTURE REVIEW REQUIRED`

입니다.

## 다음 단계

`QH-V2-OPS-004`를 바로 시작하지 않습니다.

먼저 Human + ChatGPT가 **Verification Strategy / Regression Tiering Architecture Review**를 수행해야 합니다.

현재 검토 중인 방향은 다음과 같습니다.

```text
Task close
  -> 현재 Task와 직접 관련된 focused authoritative regression
  -> 공통 핵심 invariant suite
  -> fresh exact implementation HEAD
  -> Scope / Diff Check / Final Gate

Milestone / Release / Main Gate
  -> repository-wide integration regression
  -> fresh exact HEAD
  -> 별도 강한 gate
```

아직 Accepted Architecture가 아니므로 다음은 금지합니다.

- test 삭제
- new skip
- assertion weakening
- cached/stale PASS reuse
- Final Gate 축소
- Verification concurrency 재도입
- Worker authority 확대
- OPS-004 자동 시작

핵심 목표는 **검증 강도를 낮추지 않으면서 routine Task close를 실제 개발에 사용할 수 있는 시간으로 만드는 것**입니다.

## Codex CLI 일시 중단 상태

Codex CLI weekly usage 한도로 인해 현재는 Codex를 필수 실행자로 사용하지 않습니다.

현재 권장 운영 구조:

```text
Human
  -> CMD / Git 실행

ChatGPT
  -> Requirements / Architecture / Task 설계
  -> 기술 판단 / Review
  -> 다음 명령 결정

Qwen Harness + Qwen3:8B
  -> 승인된 Task 안에서 Worker 실행
  -> Scope / Verification / Final Gate
```

Codex는 Harness Architecture의 필수 구성요소가 아니므로 사용 가능량이 회복되면 다시 선택적 external executor로 사용할 수 있습니다.

수동 운영 절차는 [`MANUAL_OPERATOR_GUIDE.md`](MANUAL_OPERATOR_GUIDE.md)를 사용합니다.

## 문서 신선도 / 읽는 순서

| 문서 | 역할 | 현재성 |
|---|---|---|
| [`STATUS.md`](../STATUS.md) | 현재 lifecycle / baseline | **최우선 / 최신** |
| [`DECISIONS.md`](../DECISIONS.md) | Accepted Architecture | **권위 문서** |
| [`tasks/QH-V2-PERF-007.md`](../tasks/QH-V2-PERF-007.md) | 최신 성능 Task Evidence | **최신** |
| [`README.md`](../README.md) | GitHub 사용자-facing 개요 | **최신 상태 반영** |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | 개발 규칙 / PERF-006~007 Evidence | **최신 상태 반영** |
| [`MANUAL_OPERATOR_GUIDE.md`](MANUAL_OPERATOR_GUIDE.md) | Codex 없이 수동 운영 | **최신 상태 반영** |
| [`BACKLOG.md`](../BACKLOG.md) | queue / historical override 기록 | 여러 시점의 override가 누적되어 있으므로 **STATUS와 최신 Task Evidence를 함께 읽음** |
| [`PROJECT_TIMELINE.md`](PROJECT_TIMELINE.md) | 역사 기록 | 과거 단계 중심, 현재 판정용 아님 |
| [`DEVELOPMENT_LOG.md`](DEVELOPMENT_LOG.md) | 개발 역사 | 과거 단계 중심, 현재 판정용 아님 |
| [`RESEARCH_LOG.md`](RESEARCH_LOG.md) | 실험/연구 역사 | 과거 단계 중심, 현재 판정용 아님 |

`BACKLOG.md`와 역사 로그 안에는 당시에는 맞았지만 이후 override된 `Current Nomination`, Candidate 상태, queue 문구가 남아 있을 수 있습니다. 이를 현재 상태로 단독 해석하지 않습니다. 현재 운영 판단은 `STATUS.md` 상단 + 최신 Task + Accepted ADR + 이 문서의 최신 스냅샷을 함께 사용합니다.

## 다음 세션 시작 체크

Human이 직접 CMD에서 작업할 때는 먼저 다음을 확인합니다.

```bat
cd /d D:\qwen-harness-test
git fetch origin
git pull --ff-only origin main
git status --short
git rev-parse HEAD
qh.cmd status
```

working tree가 clean하지 않거나 local/main이 예상과 다르면 다음 lifecycle 작업을 시작하지 않습니다.

현재는 Architecture Review가 먼저이므로 `qh.cmd start QH-V2-OPS-004`를 실행하지 않습니다.
