# Qwen Harness Development Log

> 개발 과정에서 **무엇을 만들었는가**보다 **왜 그 구조가 필요해졌는가**를 중심으로 정리한 기록입니다.

이 문서는 [`PROJECT_TIMELINE.md`](PROJECT_TIMELINE.md)의 시간순 기록을 개발 의사결정 관점에서 다시 정리합니다. 상세 Architecture 권위는 [`DECISIONS.md`](../DECISIONS.md), 현재 lifecycle 권위는 [`STATUS.md`](../STATUS.md), 각 구현 범위와 Acceptance Criteria는 [`tasks/`](../tasks/)가 가집니다.

---

## 1. 시작점 — Local Qwen을 실제 Repository Worker로 쓸 수 있는가

### Problem

로컬 Qwen은 비용 부담 없이 코드를 생성할 수 있지만 다음 질문에 스스로 신뢰할 수 있는 답을 주지 못했습니다.

- 정말 승인된 파일만 수정했는가?
- 기존 코드를 훼손하지 않았는가?
- 테스트를 실제로 실행했는가?
- 실패했는데 PASS라고 말하지 않았는가?
- 반복 실패에서 멈출 수 있는가?

### Development direction

초기 Qwen regression을 통해 작은 Task 성공 가능성은 확인했지만, prompt-only safety와 Worker self-report를 최종 권위로 삼지 않기로 했습니다.

### Result

[`ADR-001`](../DECISIONS.md)이 Accepted 되었고, mechanically decidable한 영역은 Python Harness Core로 이동했습니다.

---

## 2. HC-001 ~ HC-007 — "판단 가능한 것은 코드로 판단"

### Problem

Worker가 작업을 수행해도 Repository가 실제로 올바른 상태인지 독립적으로 평가할 deterministic path가 없었습니다.

### Implementation

Core를 한 번에 크게 만들지 않고 책임별로 잘랐습니다.

| Task | 구현 책임 | 설계 의도 |
|---|---|---|
| HC-001 | Task contract parser | Task scope를 prompt 해석에만 맡기지 않음 |
| HC-002 | scope matcher | Allowed/Forbidden을 deterministic하게 판정 |
| HC-003 | Git baseline / changed paths | 실제 mutation Evidence 확보 |
| HC-004 | Verification parser / runner | 승인된 명령만 실행 |
| HC-005 | invariants | exact/hash 조건을 LLM 추론 없이 검사 |
| HC-006 | Evidence assembly | 결과를 objective record로 조립 |
| HC-007 | Final Gate | 최종 PASS/FAIL을 deterministic하게 결정 |

### Verification

각 Core Task는 RED test → 구현 → focused/full regression → Git diff 확인 방식으로 진행되었습니다.

HC-007은 `HarnessEvidence`를 mechanically decidable한 조건만으로 평가하며 Worker나 LLM의 PASS 선언을 권위로 사용하지 않습니다.

### Result

프로젝트의 가장 중요한 Trust Boundary가 생겼습니다.

```text
Semantic work: Qwen
Deterministic authority: Harness
```

---

## 3. 개발 중 운영 장애도 Source of Truth로 만들기

### Problem

Windows CMD quoting, accidental file creation, nested escaping, Qwen candidate pollution처럼 같은 종류의 문제가 반복되었습니다.

단순히 "이번에는 고쳤다"로 끝내면 다음 Task에서 같은 실패를 다시 조사해야 했습니다.

### Implementation

[`ADR-003`](../DECISIONS.md)과 [`verified_problem_resolutions.md`](verified_problem_resolutions.md)를 만들었습니다.

문제 기록은 다음 구조를 갖도록 했습니다.

```text
Problem
→ Symptoms / Trigger
→ Root Cause
→ Verified Resolution
→ Verification Evidence
→ Prevention
→ Automation Candidate
```

### Result

실패가 단순한 개발 낭비가 아니라 이후 Architecture와 automation 우선순위를 정하는 Evidence가 되었습니다.

---

## 4. Worker backend 독립 — OpenCode가 아니라 Harness가 중심

### Problem

초기 Worker 구조가 OpenCode 동작에 너무 의존하면 Harness 자체를 평가하기 어렵고 backend 변경도 어려워집니다.

### Evidence

Repository Architecture 기록은 다음을 구분했습니다.

- qwen2.5-coder:7b는 OpenCode/Qwen Code 경로에서 executable tool call이 안정적이지 않았음
- Qwen3:8B는 native Ollama API에서 structured tool call을 생성할 수 있었음
- Python-controlled tool-call/result continuation이 실제 Repository 파일 대상으로 성공함
- tool call 성공과 semantic correctness는 별개임

### Decision / Implementation

[`ADR-002`](../DECISIONS.md)로 agent-independent Worker Architecture를 채택했습니다.

기본 경로:

```text
Python Harness → Native Ollama → Qwen3:8B
```

QH-V2-WC-001은 WorkerRequest/WorkerResponse를 backend-independent boundary로 고정했고, QH-V2-OWA-001은 native Ollama transport만 담당하도록 제한했습니다.

### Result

Harness Core와 Worker backend가 분리되었습니다. Worker를 바꿔도 scope, Verification, Evidence, Final Gate 권위는 유지할 수 있는 구조가 되었습니다.

---

## 5. 반복 작업을 `qh`로 자동화

### Problem

개발 과정에서 `git status`, scope 확인, Verification 실행, review 준비가 계속 반복되었습니다. 사람이 매번 긴 CMD 명령을 조립하면서 quoting과 누락 문제가 늘어났습니다.

### Decision

[`ADR-005`](../DECISIONS.md)는 Worker integration보다 먼저 deterministic workflow automation을 넣었습니다.

### Implementation

QH-V2-AUTO-001에서 다음 CLI가 추가되었습니다.

- `qh status`
- `qh preflight`
- `qh verify`
- `qh review`

이후 lifecycle Task들을 통해 `qh start`, `qh close`, persisted baseline, task-range scope review가 추가·강화되었습니다.

### Verification / Result

중요한 원칙은 CLI가 새로운 safety engine을 만드는 것이 아니라 HC-001~HC-007을 재사용한다는 것입니다.

운영 편의가 올라가도 Task 승인, Architecture 판단, PASS authority는 자동화하지 않았습니다.

---

## 6. Repository Tool Boundary — Qwen에게 shell을 주지 않기

### Problem

실제 코딩 Worker가 Repository를 읽고 써야 하지만 일반 shell/Git 권한을 직접 주면 기존 deterministic scope 구조가 무력화될 수 있습니다.

### Implementation

QH-V2-READ-001과 QH-V2-EDIT-001에서 최소 Repository Tool을 만들었습니다.

```text
read_repo_text(path)
write_repo_text(path, content)
```

read/write 모두 Repository root, absolute path, traversal, directory target 등을 deterministic하게 검사합니다.

write의 Allowed/Forbidden scope는 Worker가 전달하지 않습니다. Runner/Harness가 현재 Task 계약에서 가져옵니다.

### Result

Qwen은 "이 파일을 쓰고 싶다"고 요청할 수는 있지만 실제 permission은 Harness가 판단하게 되었습니다.

---

## 7. Backend-Neutral Tool Interaction과 Single-Task Runner

### Problem

Ollama native `tool_calls`를 Runner가 직접 다루면 backend independence가 깨집니다. 또 Worker가 여러 Tool을 한 번에 요청하거나 malformed request를 만들 때 어떻게 처리할지도 명확해야 했습니다.

### Decision

[`ADR-008`](../DECISIONS.md)이 backend-neutral records를 정의했습니다.

- ToolSpec
- ToolRequest
- ToolResult
- WorkerStep

그리고 한 WorkerStep에서 **0 또는 1 ToolRequest**만 허용했습니다.

### Implementation

QH-V2-RUN-001A/B/C에서 record → Ollama adapter → deterministic Runner loop 순으로 구현했습니다.

Runner는 한 번에 현재 ACTIVE Task 하나만 실행하고 lifecycle-control write를 보호합니다.

### Verification / Result

multi-tool, malformed, unknown, unauthorized 요청은 silent repair하지 않고 Tool 실행 전에 fail closed합니다.

Worker interaction success는 여전히 Repository PASS가 아닙니다.

---

## 8. Retry를 Worker 안이 아니라 Harness policy로 분리

### Problem

네트워크나 Worker session 실패는 재시도할 가치가 있지만, scope violation 같은 deterministic failure를 재시도하면 안 됩니다.

특히 write가 이미 시도된 뒤 whole-Runner retry를 하면 duplicate/partial side effect 위험이 생깁니다.

### Decision

[`ADR-009`](../DECISIONS.md)은 Retry를 Runner 바깥의 deterministic layer로 분리했습니다.

### Implementation

QH-V2-RETRY-001의 핵심 규칙:

- total Runner attempts 최대 2회
- transient Worker/session failure만 retry 후보
- Repository write attempt가 없을 때만 automatic retry 가능
- deterministic safety failure는 즉시 FAIL
- retry exhausted 또는 write side-effect risk가 있으면 BLOCKED
- error text parsing이 아니라 structured failure metadata 사용

### Result

"다시 해보면 될 것 같다"는 LLM 판단이 retry policy를 바꾸지 못합니다.

---

## 9. 실제 Worker E2E 후 Capability Expansion을 멈추고 Hardening

### Problem

QH-V2-E2E-001은 실제 local Qwen Worker로 작은 Repository edit flow를 성공시켰습니다. 하지만 E2E 성공은 전체 Harness가 충분히 안전하다는 뜻은 아니었습니다.

### Evidence

실제 QH-V2-CLI-001 과정에서 intended multi-command Verification contract가 완전하게 해석되지 않았는데도 Final Gate PASS가 가능한 사례가 발견되었습니다.

### Decision

[`ADR-010`](../DECISIONS.md)은 다음 milestone보다 Verification/lifecycle hardening을 먼저 하도록 했습니다.

### Implementation

HARD 계열 Task들은 다음을 강화했습니다.

- Verification parser fail-closed
- duplicate start guard
- Evidence refresh ordering
- Windows path identity / resolved alias
- test discovery integrity
- runtime import portability

### Result

새 기능보다 "잘못된 PASS를 막는 것"이 우선순위가 되었습니다.

---

## 10. Verification 성능 — 빠르게가 아니라 안전하게 빠르게

### Problem

authoritative Verification이 몇 분씩 걸리면 운영성이 나빠집니다. 하지만 테스트를 줄이거나 stale Evidence를 재사용해서 빠르게 만드는 것은 허용할 수 없습니다.

### Experiment / Implementation

QH-V2-PERF-001은 concurrency를 먼저 측정했습니다. 개선은 약 0.7%에 그쳤고 suite 개별 성능은 나빠져 채택하지 않았습니다.

QH-V2-PERF-002 profiling 결과 반복 Git fixture 생성이 주요 병목으로 드러났습니다.

QH-V2-PERF-003은 seed Repository reuse를 통해 isolation을 유지하면서 setup cost를 낮췄습니다.

HARD-007 후에도:

- 259 tests: 560.059 s
- `tests.test_qh`: 470.073 s
- `tests.test_harness_core`: 207.330 s

가 측정되어 QH-V2-PERF-005가 추가되었습니다.

### Result

성능 최적화도 Architecture를 임의로 바꾸지 않고 별도 Task + benchmark Evidence로 진행하는 패턴이 정착했습니다.

---

## 11. G1 — 자율 실행도 정확한 범위에서만

### Problem

Task가 이미 승인되어 있는데 매 lifecycle 단계마다 Human relay가 반복되는 비용이 있었습니다.

### Decision

[`ADR-012`](../DECISIONS.md)은 exact sealed queue 한 개에 대해서만 narrow autonomous queue gate G1을 허용했습니다.

### Evidence-driven change

HARD-006과 HARD-007 완료 후 새로운 performance Evidence가 나왔고 Human은 PERF-005를 먼저 하기로 결정했습니다.

[`ADR-013`](../DECISIONS.md)은 남은 G1 권한을 폐기하고 sealed manifest를 historical Evidence로 보존했습니다.

### Result

자동화 계획이 이미 있어도 새로운 Evidence가 나오면 queue를 멈추고 다시 판단한다는 governance pattern이 검증되었습니다.

---

## 12. Cross-Repository Trial — 실제 다른 프로젝트에서만 보이는 문제

### Problem

Repository 내부 E2E로는 발견하지 못한 운영 문제가 다른 Repository trial에서 나타났습니다.

[`ADR-014`](../DECISIONS.md)이 기록한 두 문제:

1. direct `python tools\qh.py run ...` import portability
2. real Qwen multi-ToolRequest WorkerStep

### Implementation

QH-V2-HARD-008은 import path 문제를 먼저 수정하고 `qh doctor`가 delayed Worker import chain까지 확인하도록 강화했습니다.

Worker multi-tool 문제는 safety rule을 바꾸지 않고 QH-V2-WORKER-ROB-001이라는 별도 Level B Candidate 실험으로 분리했습니다.

### Result

cross-Repository trial은 Globalization 승인 Evidence가 아니라 **새 hardening 요구를 발견한 Evidence**로 사용되었습니다.

`GLOBALIZATION = NOT AUTHORIZED`

---

## 13. WORKER-ROB-001 — 실패 Candidate도 정식 결과로 남기기

### Hypothesis

Worker에게 one-tool protocol을 더 명확히 주면 exact task success가 개선될 수 있다.

### Measured result

- Stable: 0/10 exact task success
- final Candidate: 0/10 exact task success
- promotion rejected

자세한 Evidence: [`WORKER_ROB_001_EVIDENCE.md`](WORKER_ROB_001_EVIDENCE.md)

### Development consequence

기존 lifecycle은 성공 상태 `COMPLETE - VERIFIED`만 durable terminal로 다룰 수 있어 실패한 실험을 truthful하게 닫기 어려웠습니다.

[`ADR-015`](../DECISIONS.md)은:

`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

상태를 도입했고, QH-V2-LIFECYCLE-001이 durable support를 구현했습니다.

### Result

"실험을 제대로 했지만 Candidate가 실패했다"와 "Task 구현 성공"을 명확히 분리할 수 있게 되었습니다.

---

## 14. WORKER-DIAG-001 — timeout 값을 바꾸기 전에 원인 분해

### Problem

full Task prompt가 30초 timeout에 반복적으로 도달했습니다. 단순히 timeout을 늘리거나 model을 변경하는 것은 Evidence 없는 policy change였습니다.

### Investigation

QH-V2-WORKER-DIAG-001은 production 동작을 바꾸지 않고 조건을 분리했습니다.

- short/no tools: 5/5
- short/current tools: 5/5
- full Task/no tools: 0/5
- same full input but exact `OK`: 3/3 quick
- full Task/tools: 일부 bounded ToolRequest 성공 + 반복 timeout

### Interpretation

input length만으로 설명되지 않고 tool schema도 독립 충분 원인이 아니었습니다. full semantic task-solving workload가 중요한 변수로 보였습니다.

또 socket `TimeoutError` normalization gap, Ollama/model/qhops configuration hardcode 후보도 별도 문제로 분리했습니다.

### Result

수정 대신 다음 실험 설계가 나왔습니다: deterministic Worker Brief.

Evidence: [`WORKER_DIAG_001_EVIDENCE.md`](WORKER_DIAG_001_EVIDENCE.md)

---

## 15. ADR-017 — Human이 모든 기계적 단계를 중계하지 않도록 변경

### Problem

이미 승인된 Task 안에서 focused test, Verification, close, lifecycle commit 같은 routine step까지 매번 다시 승인받는 것은 Harness가 deterministic해진 만큼 불필요한 relay가 되었습니다.

### Decision

[`ADR-017`](../DECISIONS.md)은 Exception-Driven Human Supervision을 채택했습니다.

정상이고 이미 승인된 범위의 routine work는 계속할 수 있지만 다음은 STOP/Human review입니다.

- FAIL/BLOCKED/SAFETY/unresolved timeout
- unexpected mutation/scope violation
- Git divergence/ambiguity
- new Task/queue decision
- Candidate production promotion
- Architecture/Requirements/Trust Boundary change
- model/think/timeout/retry/step-budget policy change

### Result

Human의 역할이 "모든 명령 승인"에서 "예외와 방향 판단"으로 이동했습니다.

단, Qwen Worker의 FR-004는 그대로이며 Worker는 successor를 선택하거나 시작하지 않습니다.

---

## 16. WORKER-ROB-002 — Task를 줄이지 말고 deterministic하게 투영

### Problem

full Task semantic workload가 local Worker의 latency/timeout과 관련 있어 보였지만, LLM 요약은 scope나 Acceptance Criteria를 누락할 수 있습니다.

### Experiment design

원본 Task를 Source of Truth로 그대로 두고 지정 section만 exact-copy하는 deterministic Worker Brief를 만들었습니다.

세 조건을 10회씩 interleaved 비교했습니다.

| Variant | Valid bounded first step | Timeout | Median completed | Writes executed |
|---|---:|---:|---:|---:|
| Stable — Full Task | 6/10 | 4/10 | 10.529492 s | 0 |
| Candidate A — Deterministic Worker Brief | 10/10 | 0/10 | 2.013165 s | 0 |
| Candidate B — Brief + One-Step | 2/10 | 3/10 | 20.778239 s | 0 |

ToolRequest는 관찰만 했고 실행하지 않았습니다.

### Result

Candidate A는 별도 production Task를 만들 가치가 있는 Candidate로 추천되었습니다.

하지만 **추천과 production integration은 다릅니다.** 현재 Evidence는 Candidate A를 production에 적용하지 않았습니다.

Evidence: [`WORKER_ROB_002_EVIDENCE.md`](WORKER_ROB_002_EVIDENCE.md)

---

## 개발 과정에서 정착된 규칙

현재 구조가 복잡해 보이는 이유는 기능을 많이 넣어서가 아니라, 반복 실패를 하나씩 deterministic boundary로 옮겼기 때문입니다.

핵심 개발 패턴은 다음과 같습니다.

```text
Problem
→ Task Contract
→ 최소 구현
→ Focused Test
→ Git / Scope Evidence
→ Authoritative qh close
→ Final Gate
→ 성공 또는 truthful unsuccessful closure
```

그리고 개선 후보는:

```text
Evidence
→ Candidate
→ Stable vs Candidate evaluation
→ Promotion decision
```

순서를 따릅니다.

성능, Worker prompt, lifecycle, retry, global-use 모두 같은 방식으로 다룹니다.

---

## 다음에 이 문서를 읽을 때

- 전체 시간 흐름: [Project Timeline](PROJECT_TIMELINE.md)
- 문제 해결법: [Troubleshooting](TROUBLESHOOTING.md)
- 실험/가설/수치: [Research Log](RESEARCH_LOG.md)
- Architecture 권위: [DECISIONS.md](../DECISIONS.md)
- 현재 상태: [STATUS.md](../STATUS.md)
