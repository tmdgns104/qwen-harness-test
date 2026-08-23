# Qwen Harness Project Timeline

> **Qwen Harness Engineering Journal**  
> A local AI coding agent built through evidence, failures, experiments, and deterministic verification.

이 문서는 Qwen Harness가 어떤 문제를 겪었고, 그 문제를 어떤 Task와 Evidence로 해결하면서 현재 구조에 도달했는지 시간순으로 정리한 기록입니다.

이 기록의 권위는 Chat 기록이 아니라 Repository Source of Truth에 있습니다. 주요 근거는 [`DECISIONS.md`](../DECISIONS.md), [`STATUS.md`](../STATUS.md), [`tasks/`](../tasks/), [`docs/verified_problem_resolutions.md`](verified_problem_resolutions.md), Worker 실험 Evidence, 그리고 Git commit history입니다.

## 상태 표기 읽는 법

| 상태 | 의미 |
|---|---|
| `COMPLETE - VERIFIED` | 승인된 Verification과 Final Gate를 통과한 성공 상태 |
| `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` | 실제로 시도·평가했지만 Acceptance Criteria를 만족하지 못해 성공으로 승격하지 않은 상태 |
| Candidate | 실험 결과일 뿐 production 적용을 의미하지 않음 |
| `GLOBALIZATION = NOT AUTHORIZED` | 다른 Repository에서 Stable Harness로 일반 사용하도록 승인된 상태가 아님 |

`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`는 PASS가 아닙니다. 실패·비승격 결과도 지우지 않고 다음 판단의 Evidence로 보존하는 것이 이 프로젝트의 원칙입니다.

---

## 2026-08-16 — 작은 Qwen 실험에서 시작

초기 Repository는 로컬 Qwen에게 작은 코딩 Task를 맡기고 실제 수정 결과를 확인하는 실험장으로 시작했습니다.

초기 Git history에는 Worker slimming, Evidence collector, Task contract parser, Qwen regression fixtures와 Formal Specification 작업이 순차적으로 남아 있습니다. 이 단계에서 중요한 발견은 "작은 Task는 성공할 수 있지만, 모델이 성공했다고 말하는 것만으로 완료를 판단할 수 없다"는 것이었습니다.

이 Evidence가 이후 [`ADR-001`](../DECISIONS.md)의 출발점이 되었습니다.

**대표 기록**

- `c5a3cae` — baseline before qwen worker tests
- `731ee10` — Qwen regression test 001
- `d89e18c` — Qwen regression test 002
- `b29b493` — Qwen Harness V2 project definition
- `bbcc4c6` — Qwen Harness V2 requirements

---

## 2026-08-17 ~ 08-19 — LLM보다 먼저 Deterministic Harness Core 구축

[`ADR-001`](../DECISIONS.md)은 mechanically checkable한 일을 LLM에게 반복해서 맡기지 않고 Python Harness가 소유하도록 결정했습니다.

그 결과 HC-001부터 HC-007까지가 작은 Task로 분해되었습니다.

| Core | 역할 | 결과 |
|---|---|---|
| HC-001 | Task Contract parsing | deterministic contract interpretation |
| HC-002 | Allowed / Forbidden path scope | deterministic scope decision |
| HC-003 | Git baseline / changed-path Evidence | 실제 변경 파일 추적 |
| HC-004 | Verification command parsing / execution | 승인된 검증 실행 |
| HC-005 | Exact / hash invariant | 내용 훼손 탐지 |
| HC-006 | Evidence assembly | 객관 Evidence 조립 |
| HC-007 | Deterministic Final Gate | LLM과 독립적인 최종 PASS/FAIL |

HC-007의 핵심 계약은 명확합니다. LLM 또는 Worker가 PASS라고 말해도 deterministic failure Evidence를 덮어쓸 수 없습니다.

**주요 완료 commit**

- `746a0d3` — HC-001-R1 Task parser
- `b04f127` — HC-002 path scope matcher
- `9657827` / `5eeea43` / `7ab7c19` — HC-003 계열 Git Evidence
- `5da53fb` / `eb2fd68` — HC-004 Verification parser / execution
- `dc02ba2` — HC-005 invariant checks
- `3f869c3` — HC-006 Evidence assembly
- `d6cd50b` — HC-007 deterministic Final Gate

이 단계에서 Qwen Harness의 핵심 방향이 "좋은 모델 만들기"에서 **"작은 모델을 신뢰 가능한 바깥 구조로 통제하기"**로 굳어졌습니다.

---

## 2026-08-18 — OpenCode 종속을 벗어나 Native Ollama Worker 채택

[`ADR-002`](../DECISIONS.md)은 Harness Core가 OpenCode나 특정 Agent frontend에 종속되지 않도록 했습니다.

Repository Evidence에서 `qwen3:8b`가 native Ollama API를 통해 structured tool call을 만들 수 있었고, Python이 tool-call/result continuation을 제어할 수 있음을 확인했습니다.

기본 Worker 방향은 다음과 같이 정리되었습니다.

```text
Deterministic Python Harness
        ↓
native Ollama API
        ↓
Qwen3:8B
```

OpenCode는 선택 가능한 backend/benchmark 후보로 남고, Codex 역시 Harness Core 작동에 필수 요소가 아닌 별도 고성능 executor 역할로 분리되었습니다.

---

## 2026-08-19 — Core 이후 Worker Integration Architecture 확정

HC-007 완료 후 [`ADR-004`](../DECISIONS.md)가 Milestone 1 Worker 통합 순서를 확정했습니다.

```text
Worker Contract
  → Native Ollama Adapter
  → Repository Read Tool
  → Scoped Edit Tool
  → Single-Task Runner
  → Bounded Retry / Safe Stop
  → Minimal CLI
  → Real Worker E2E
```

동시에 반복되던 Git/status/verification 수작업이 개발 속도와 오류 가능성에 영향을 주면서 [`ADR-005`](../DECISIONS.md)에 의해 `qh status`, `preflight`, `verify`, `review` 자동화가 Worker Adapter보다 먼저 삽입되었습니다.

**대표 Task**

- QH-V2-WC-001 — backend-independent Worker contract
- QH-V2-AUTO-001 — deterministic workflow commands
- QH-V2-OWA-001 — Native Ollama Worker Adapter
- QH-V2-READ-001 — Repository text read
- QH-V2-EDIT-001 — scoped Repository text write

Native Ollama Adapter는 transport-only 경계로 구현됐으며 Qwen에게 filesystem, shell, Git, Verification 또는 Final Gate 권한을 주지 않았습니다.

---

## 2026-08-20 — Tool Contract, Runner, Retry, CLI, 실제 E2E 완성

[`ADR-008`](../DECISIONS.md)은 Ollama 고유 `tool_calls` 구조를 Runner가 직접 알지 않도록 backend-neutral Tool interaction contract를 만들었습니다.

초기 Worker tool surface는 오직 다음 두 개였습니다.

- `read_repo_text`
- `write_repo_text`

한 WorkerStep에서 0개 또는 1개의 ToolRequest만 허용하고, 여러 ToolRequest는 실행하지 않은 채 fail closed하도록 했습니다.

이후 QH-V2-RUN-001에서 Single-Task Runner가 완성됐고, [`ADR-009`](../DECISIONS.md)에 따라 Retry는 Runner 바깥의 별도 deterministic policy로 구현되었습니다.

Retry V1은 최대 **2 total Runner attempts**이며, Repository write attempt 이후에는 whole-Runner automatic retry를 허용하지 않습니다. deterministic safety failure는 retry 대상이 아닙니다.

**대표 완료 기록**

- `80cdfff` — backend-neutral Tool records
- `5472162` — native Ollama tool interaction adapter
- `4cb1ff5` — deterministic Single-Task Runner
- `7caff32` — bounded retry / safe stop orchestration
- `ffd5dcb` — minimal Worker CLI
- `d9d095d` — real Worker E2E edit

QH-V2-E2E-001은 실제 local Ollama + Qwen Worker를 이용한 작은 Repository Task 흐름을 완료했고 Milestone 1의 핵심 실행 경로를 검증했습니다.

---

## 2026-08-20 ~ 08-22 — "기능 추가"보다 Hardening과 Verification 신뢰성 우선

E2E 성공 뒤 [`ADR-010`](../DECISIONS.md)은 다음 capability expansion보다 Verification/lifecycle hardening을 우선했습니다.

특히 실제 QH-V2-CLI-001 과정에서 intended multi-command Verification이 잘못 해석되어도 Final Gate PASS가 가능했던 Evidence 때문에 Verification fail-closed hardening이 최우선이 되었습니다.

이어 다음 문제가 순차적으로 다뤄졌습니다.

- Verification contract fail-closed
- duplicate `qh start` lifecycle guard
- Evidence refresh / lifecycle consistency
- Windows path / resolved alias scope safety
- root unittest discovery가 0 tests가 되는 문제
- Git-heavy Verification performance

QH-V2-HARD-007은 Repository root에서 test discovery가 실제 suite를 놓치는 문제를 해결하고 zero-test guard를 추가했습니다.

---

## 2026-08-20 ~ 08-22 — 성능 최적화도 Evidence로 판단

Verification이 안전해도 지나치게 느리면 실제 운영성이 떨어집니다. 이 프로젝트는 성능 개선도 추측이 아니라 측정 후 결정했습니다.

QH-V2-PERF-001은 Verification concurrency를 실험했지만 wall-clock 개선이 약 **0.7%** 수준이고 개별 suite는 오히려 느려져 채택하지 않았습니다.

QH-V2-PERF-002는 병목을 profiling했고, QH-V2-PERF-003은 반복 temporary Git Repository 생성이 큰 비용임을 확인해 isolated seed Repository fixture를 도입했습니다.

HARD-007 뒤에도 Windows host에서 다음 비용이 측정되었습니다.

| Regression | 측정값 |
|---|---:|
| selected 259 tests | 560.059 s |
| `tests.test_qh` 48 tests | 470.073 s |
| `tests.test_harness_core` 119 tests | 207.330 s |

이 Evidence로 [`ADR-013`](../DECISIONS.md)은 남은 G1 queue를 폐기하고 QH-V2-PERF-005를 삽입했습니다. G1 manifest는 삭제하거나 새 queue로 재해석하지 않고 **historical Evidence only**로 보존되었습니다.

---

## 2026-08-22 — 제한된 G1 Queue 실험과 명시적 폐기

[`ADR-012`](../DECISIONS.md)은 정확히 seal된 한 개 queue에 대해서만 반복 Human relay를 줄이는 narrow autonomous queue gate를 승인했습니다.

QH-V2-HARD-006과 HARD-007은 이 sealed G1 아래 완료되었습니다. 그러나 HARD-007 뒤 새로운 performance Evidence가 생기자 Human은 queue를 그대로 밀어붙이지 않고 [`ADR-013`](../DECISIONS.md)으로 남은 G1 권한을 폐기했습니다.

이 기록은 중요한 설계 원칙을 보여 줍니다.

> 자동화 권한도 Evidence가 바뀌면 중단될 수 있어야 하며, 과거 승인 manifest를 새 계획에 맞게 편집해서는 안 된다.

현재 G1은 historical/revoked 상태입니다.

---

## 2026-08-22 ~ 08-23 — 운영 도구: `task-new`, `doctor`

QH-V2-OPS-001은 Human review용 Task scaffold를 만들었고, QH-V2-OPS-002는 Python/Git/Repository/Ollama/model 상태를 읽기 전용으로 진단하는 `qh doctor`를 구현했습니다.

운영 자동화는 Task 승인이나 Architecture 결정을 대신하지 않도록 제한되었습니다.

---

## 2026-08-23 — 첫 Cross-Repository Trial이 새로운 문제를 발견

[`ADR-014`](../DECISIONS.md)은 `ai_data_analyst`에서의 첫 cross-Repository trial Evidence를 근거로 두 문제를 분리했습니다.

1. documented `python tools\qh.py run ...` 경로에서 `ModuleNotFoundError: No module named 'tools'`가 날 수 있는 runtime portability defect
2. real `qwen3:8b`가 한 WorkerStep에서 여러 ToolRequest를 반환하는 Worker interaction robustness 문제

첫 번째는 QH-V2-HARD-008에서 import/runtime portability를 수정했습니다.

두 번째 문제는 safety rule 자체를 완화하지 않았습니다. multi-tool step은 계속 `SAFETY`로 fail closed하고 그 step의 Tool을 하나도 실행하지 않는 상태를 유지한 채 Worker 쪽 interaction 품질만 개선하는 QH-V2-WORKER-ROB-001로 분리했습니다.

`GLOBALIZATION = NOT AUTHORIZED`는 그대로 유지되었습니다.

---

## 2026-08-23 — WORKER-ROB-001: 실패를 성공으로 포장하지 않기

QH-V2-WORKER-ROB-001은 Worker에게 one-tool protocol을 더 명확히 주면 실제 Task 성공률이 개선되는지 Stable-versus-Candidate 방식으로 측정했습니다.

결과는 다음과 같았습니다.

- Stable: **0/10 exact task success**
- Candidate: **0/10 exact task success**
- Candidate promotion: **REJECTED**

따라서 이 Task는 `COMPLETE - VERIFIED`가 아니라:

`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

로 종료되었습니다.

이 상태를 정식 lifecycle에 넣기 위해 [`ADR-015`](../DECISIONS.md)와 QH-V2-LIFECYCLE-001이 만들어졌습니다. 실패한 Candidate는 production으로 들어가지 않았고 Evidence만 남았습니다.

자세한 수치는 [`WORKER_ROB_001_EVIDENCE.md`](WORKER_ROB_001_EVIDENCE.md)에 있습니다.

---

## 2026-08-23 — Worker timeout 원인을 먼저 진단

QH-V2-WORKER-DIAG-001은 timeout 값을 바로 늘리거나 모델을 바꾸지 않고 현상을 분해했습니다.

실험 결과:

| 조건 | 결과 |
|---|---|
| short prompt, no tools | 5/5 transport success |
| short prompt + current tool schema | 5/5 transport success |
| representative full Task, no tools | 0/5 before 30 s timeout |
| same full Task input, output constrained to `OK` | 3/3 quick completion |
| full Task + tool schema | 일부 빠른 one-tool action, 반복 timeout도 발생 |

따라서 **입력 길이만으로 timeout을 설명할 수 없고**, tool schema 자체도 독립 원인으로 확인되지 않았습니다. full Task를 실제로 해결하려는 semantic generation path가 중요한 변수로 보였습니다.

또한 socket `TimeoutError`가 현재 Adapter에서 `WorkerResponse(transport_ok=False)`로 normalize되지 않고 escape하는 별도 transport 후보 문제도 발견되었습니다.

이 진단은 수정을 하지 않았습니다. 다음 실험으로 deterministic Worker Brief를 제안했을 뿐입니다.

자세한 Evidence: [`WORKER_DIAG_001_EVIDENCE.md`](WORKER_DIAG_001_EVIDENCE.md)

---

## 2026-08-23 — ADR-017: 반복 승인 대신 Exception-Driven Human Supervision

[`ADR-017`](../DECISIONS.md)은 이미 승인된 Task 내부의 routine lifecycle까지 매번 Human에게 재승인받는 비용을 줄였습니다.

정상적으로 이미 승인된 범위 안에서 deterministic checks가 통과하는 작업은 계속 진행할 수 있지만, 다음 종류는 여전히 Human review 대상입니다.

- FAIL / BLOCKED / SAFETY / unresolved timeout
- unexpected Repository mutation 또는 scope violation
- Git divergence / destructive recovery ambiguity
- 새 Task 또는 queue 변경
- Candidate production promotion
- Architecture / Requirements / Trust Boundary 변경
- model / think / timeout / retry / step-budget 같은 policy 변경

이 변경은 **approval cadence**만 바꿨습니다. Qwen Worker가 다음 Task를 선택하거나 시작할 권한은 여전히 없습니다.

---

## 2026-08-23 — WORKER-ROB-002: Deterministic Worker Brief 실험

QH-V2-WORKER-ROB-002는 full Task를 그대로 넘기는 Stable과 두 Candidate를 10회씩 interleaved 측정했습니다.

Candidate A는 원본 Task의 지정 section을 LLM 요약 없이 deterministic하게 projection한 Worker Brief입니다. Candidate B는 같은 Brief에 one-step instruction을 더했습니다.

| Variant | transport success | timeout | valid bounded first step | median completed | Worker writes |
|---|---:|---:|---:|---:|---:|
| Stable — Full Task | 60% | 4/10 | 6/10 | 10.529492 s | 0 |
| Candidate A — Deterministic Worker Brief | 100% | 0/10 | 10/10 | 2.013165 s | 0 |
| Candidate B — Brief + One-Step | 70% | 3/10 | 2/10 | 20.778239 s | 0 |

모든 run은 initial Worker step만 관찰했고 반환된 ToolRequest를 **실행하지 않았습니다**.

Evidence 결론은:

**RECOMMEND SEPARATE PRODUCTION TASK: Candidate A - Deterministic Worker Brief**

입니다.

중요하게도 이것은 Candidate A가 이미 production에 들어갔다는 뜻이 아닙니다. QH-V2-WORKER-ROB-002는 실험 Task이며 Candidate production promotion은 별도 Human-governed Task가 필요합니다.

자세한 수치: [`WORKER_ROB_002_EVIDENCE.md`](WORKER_ROB_002_EVIDENCE.md), [`WORKER_ROB_002_RESULTS.json`](WORKER_ROB_002_RESULTS.json)

---

## 현재까지의 핵심 변화

Qwen Harness는 다음 방향으로 발전했습니다.

```text
Qwen에게 잘 시키기
        ↓
Qwen 결과를 의심하고 검증하기
        ↓
결정론적 부분을 Python Harness로 분리하기
        ↓
Tool / Git / Verification / Final Gate 권한을 Harness가 소유하기
        ↓
실패와 성능 문제도 Evidence로 기록하기
        ↓
Stable vs Candidate 실험으로 개선안을 평가하기
```

현재의 가장 중요한 원칙은 여전히 같습니다.

> **LLM self-report != Evidence**

그리고 장기 전략이 존재하더라도 현재 Repository의 권한 상태는 명확합니다.

`GLOBALIZATION = NOT AUTHORIZED`

---

## 관련 문서

- [Development Log](DEVELOPMENT_LOG.md) — 무엇을 왜 만들었는지 개발 과정 중심
- [Troubleshooting](TROUBLESHOOTING.md) — 실제 문제와 검증된 대응
- [Research Log](RESEARCH_LOG.md) — 가설, 실험 조건, 측정값, 판단
- [Verified Problem Resolutions](verified_problem_resolutions.md) — 초기 운영 장애의 원본 Evidence 기록
- [Architecture Decisions](../DECISIONS.md) — Accepted ADR
- [Current Status](../STATUS.md) — 현재 lifecycle Source of Truth
