# Qwen Harness Research Log

> 이 문서는 Qwen Harness의 연구·실험 기록을 **가설 → 조건 → 측정 → 해석 → 결정** 순으로 정리합니다.

실험 결과는 production 적용과 구분합니다. Candidate가 좋은 수치를 보여도 별도 승인과 Task 없이는 Stable behavior가 아닙니다. 현재 장기 전략 역시 `GLOBALIZATION = NOT AUTHORIZED` 상태입니다.

---

## Research 001 — Local Qwen에게 완료 판정을 맡겨도 되는가

### Hypothesis

작은 로컬 coding model이 Task를 수행하고 스스로 PASS를 보고하면 단순한 Agent workflow로도 충분할 수 있다.

### Evidence

초기 Qwen regression과 개발 과정에서 다음 failure shape가 관찰되었습니다.

- prompt-only Allowed/Forbidden scope 위반 가능
- 기존 content 손상 가능
- syntactically valid하지만 semantic contract를 어기는 Candidate
- Worker self-report와 실제 Git/Test 상태 불일치 가능

### Interpretation

semantic implementation 능력과 deterministic safety/completion authority는 분리해야 합니다.

### Decision

[`ADR-001`](../DECISIONS.md): deterministic Harness Core 우선.

```text
LLM self-report != Evidence
```

이 결정은 이후 모든 연구의 baseline이 되었습니다.

---

## Research 002 — OpenCode를 통하지 않고 Native Ollama Tool Calling이 가능한가

### Question

Harness가 특정 Agent frontend에 종속되지 않고 local model과 직접 tool interaction을 할 수 있는가?

### Conditions / observations

Architecture Evidence는 다음을 기록합니다.

- qwen2.5-coder:7b는 OpenCode/Qwen Code 경로에서 executable tool call이 충분히 안정적이지 않았음
- Qwen3:8B는 native Ollama API에서 structured tool call을 생성함
- Python-controlled native Ollama tool-call/result continuation loop가 실제 Repository file을 대상으로 성공함

### Interpretation

Worker frontend가 아니라 deterministic Harness가 중심이 되고, Ollama는 backend Adapter로 둘 수 있습니다.

### Decision

[`ADR-002`](../DECISIONS.md): agent-independent architecture 채택.

Default Worker candidate:

```text
native Ollama + Qwen3:8B + think:false fast path
```

### Important limitation

correct tool call은 correct implementation을 보장하지 않습니다. Tool execution authority와 Final PASS는 Harness가 계속 소유합니다.

---

## Research 003 — Verification을 병렬화하면 빨라지는가

### Hypothesis

긴 Verification 시간을 줄이기 위해 independent suite를 concurrency로 실행하면 wall-clock이 크게 줄어들 수 있다.

### Experiment

QH-V2-PERF-001에서 parallel Verification을 측정했습니다.

### Result

wall-clock 개선은 약 **0.7%** 수준이었고 individual suites는 오히려 느려졌습니다.

### Interpretation

병목의 본질이 CPU test execution parallelism이 아니라 Git subprocess와 fixture/setup overhead일 가능성이 더 높았습니다.

### Decision

Verification concurrency는 채택하지 않았습니다. 이후 profiling으로 이동했습니다.

### Research value

"병렬화하면 빠르다"는 일반론보다 Repository 측정값을 우선한 사례입니다.

Sources: `QH-V2-PERF-001`, [`ADR-007`](../DECISIONS.md)

---

## Research 004 — `tests.test_qh`의 실제 병목은 무엇인가

### Question

Production `qh` logic 자체가 느린가, 아니면 test fixture가 느린가?

### Profiling Evidence

QH-V2-PERF-002에서 다음이 확인되었습니다.

- 당시 `tests.test_qh`: 약 80~90 s / 22 tests
- common setup이 test마다 real Git Repository를 반복 생성
- QhStatusCliTests common setup만 test당 8 Git commands
- 22 tests 기준 common setup에서만 최소 176 Git subprocess
- simple status test runtime의 약 61%가 common setup

### Interpretation

Production logic이 primary bottleneck이라는 Evidence는 부족했고, repeated Git fixture setup이 강하게 지목되었습니다.

### Decision

QH-V2-PERF-003에서 isolated seed Repository fixture reuse를 실험했습니다.

---

## Research 005 — Seed Repository reuse로 isolation을 유지하며 test를 줄일 수 있는가

### Hypothesis

매 test마다 Git baseline을 처음부터 만드는 대신 검증된 seed Repository를 copy하면 isolation을 유지하면서 setup 시간을 줄일 수 있다.

### Conditions

- 각 test는 독립 working copy 사용
- existing behavioral assertions 유지
- production semantics 변경 없음

### Result

QH-V2-PERF-003은 seed Repository fixture optimization을 `COMPLETE - VERIFIED`로 마쳤습니다.

### Interpretation

성능 개선은 safety check를 삭제하는 방식이 아니라 test infrastructure의 반복 비용을 줄이는 방식으로 가능했습니다.

### Follow-up

HARD-007 뒤에도 larger regression은 여전히 Git-heavy했습니다. 이것이 PERF-005로 이어졌습니다.

---

## Research 006 — HARD-007 이후 Verification cost는 충분히 낮아졌는가

### Measurement

2026-08-22 Windows host Evidence:

| Regression | Measured time |
|---|---:|
| selected 259 tests | 560.059 s |
| `tests.test_qh` 48 tests | 470.073 s |
| `tests.test_harness_core` 119 tests | 207.330 s |

### Interpretation

중복 full Verification 제거와 seed fixture 개선 이후에도 Git baseline/evidence, qh review/close path가 material bottleneck으로 남았습니다.

### Decision

[`ADR-013`](../DECISIONS.md)은 remaining G1 autonomous queue를 폐기하고 QH-V2-PERF-005를 먼저 수행하도록 했습니다.

### Governance lesson

이미 seal된 자동 실행 queue보다 새로운 objective performance Evidence가 우선했습니다.

G1은 이후 historical Evidence only입니다.

---

## Research 007 — Multi-tool Worker failure를 prompt만 강화하면 해결할 수 있는가

### Background

첫 cross-Repository trial에서 real `qwen3:8b`가 두 번 한 WorkerStep에 여러 ToolRequest를 반환했습니다.

Runner는 existing policy에 따라 해당 step을 `SAFETY`로 종료하고 Tool을 실행하지 않았습니다.

### Hypothesis

Worker prompt/context에 one-tool protocol을 더 강하게 명시하면 exact Task compliance가 materially improve할 수 있다.

### Experiment

QH-V2-WORKER-ROB-001.

Stable과 bounded single-tool protocol Candidate를 같은 representative scenario에서 비교했습니다.

### Result

| Variant | Exact task success |
|---|---:|
| Stable | 0/10 |
| final Candidate | 0/10 |

Candidate는 final measurement에서 10회 모두 NORMAL_TASK_MISS로 남았습니다.

### Safety Result

Candidate work는 existing Runner-owned multi-tool SAFETY boundary를 약화하지 않았습니다.

### Interpretation

문제가 단순히 "one-tool 규칙 설명이 약해서"라고 보기 어려웠습니다. ToolResult delivery와 semantic reuse가 일부 가능해도 exact downstream argument/task fidelity가 안정적이지 않았습니다.

### Decision

**Candidate promotion: REJECTED.**

Task status:

`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

Source: [`WORKER_ROB_001_EVIDENCE.md`](WORKER_ROB_001_EVIDENCE.md)

---

## Research 008 — Full Task timeout은 input length 때문인가

### Background

QH-V2-LIFECYCLE-001 개발 중 short Ollama request는 responsive했지만 full Task request는 30 s timeout에 반복 도달했습니다.

### Hypotheses to separate

1. input이 길기 때문인가?
2. tool schema exposure 때문인가?
3. model이 full semantic Task를 해결하려는 generation workload 때문인가?
4. 단순히 timeout budget이 너무 짧은가?

### Experiment — QH-V2-WORKER-DIAG-001

Default conditions:

- model: `qwen3:8b`
- timeout: `30.0` s
- native Ollama
- existing `think:false` policy

### Measurements

#### A. Short prompt, no tools

**5/5 completed.**

첫 call warm-up/cold-start cost는 있었지만 모두 timeout 안에 완료되었습니다.

#### B. Short prompt + current tool schema

**5/5 completed.**

Tool schema exposure만으로 timeout을 재현하지 못했습니다.

#### C. Representative full Task, no tools

**0/5 completed.**

각 run은 약 30 s에서 `TimeoutError: timed out`.

#### D. Same full Task input, answer constrained to exact `OK`

**3/3 completed quickly.**

같은 긴 input이 빠르게 처리될 수 있었습니다.

#### E. Full Task + current tools

일부 run은 relevant one-tool next action을 빠르게 만들었지만 반복 timeout도 발생했습니다.

Returned ToolRequest는 diagnosis에서 실행하지 않았습니다.

### Interpretation

- input length alone: **not sufficient explanation**
- tool schema alone: **not sufficient explanation**
- timeout increase alone: **not established as correct fix**
- semantic task-solving path: strong candidate variable

### Separate finding

socket `TimeoutError`가 current adapter handling을 빠져나와 exception으로 escape했습니다. 이것은 root semantic latency 문제와 별개인 small transport-normalization candidate입니다.

### Decision

production policy를 바꾸지 않고 다음 비교 실험을 제안했습니다.

1. full Task Stable
2. deterministic Worker Brief
3. deterministic Worker Brief + one-step instruction

Source: [`WORKER_DIAG_001_EVIDENCE.md`](WORKER_DIAG_001_EVIDENCE.md)

---

## Research 009 — Deterministic Worker Brief가 full Task보다 나은가

### Problem

Local Worker에게 full Task를 그대로 주면 semantic workload가 커지지만 LLM에게 자유 요약을 맡기면 Allowed/Forbidden scope, Acceptance Criteria, Stop Conditions가 누락될 수 있습니다.

### Hypothesis

원본 Task를 Source of Truth로 유지하면서 필요한 section만 exact-copy하는 deterministic projection은 semantic 부담을 줄이면서 authority를 보존할 수 있다.

### Experiment — QH-V2-WORKER-ROB-002

세 variant를 각각 10회, rotating interleaved order로 실행했습니다.

- **Stable** — full Task
- **Candidate A** — deterministic Worker Brief
- **Candidate B** — same Brief + explicit one-step instruction

공통 조건:

- `qwen3:8b`
- `think:false`
- timeout `30.0`
- current tool schema
- initial Worker step only
- ToolRequest inspected, **not executed**

### Measurements

| Metric | Stable | Candidate A | Candidate B |
|---|---:|---:|---:|
| transport success | 60% | 100% | 70% |
| timeout | 4/10 | 0/10 | 3/10 |
| valid bounded first step | 6/10 | 10/10 | 2/10 |
| zero-tool terminal | 0% | 0% | 50% |
| multi-tool | 0 | 0 | 0 |
| invalid tool | 0 | 0 | 0 |
| scope-incompatible | 0 | 0 | 0 |
| median completed latency | 10.529492 s | 2.013165 s | 20.778239 s |
| max latency | 30.038475 s | 4.816314 s | 30.023746 s |
| Worker writes executed | 0 | 0 | 0 |

### Interpretation

Candidate A는 Stable 대비:

- valid first step: 6/10 → **10/10**
- timeout: 4/10 → **0/10**
- completed median latency: 10.53 s → **2.01 s**

로 개선되었습니다.

Candidate B의 extra one-step wording은 오히려 interaction quality를 악화시켰습니다.

이 결과는 "instruction을 더 많이 넣을수록 좋다"는 가정을 지지하지 않습니다.

### Decision

**RECOMMEND SEPARATE PRODUCTION TASK: Candidate A - Deterministic Worker Brief**

### What this does NOT mean

- Candidate A production integration 완료 아님
- Repository Task PASS 측정 아님
- Worker authority expansion 아님
- timeout policy 변경 아님
- model/think/retry/step budget 변경 아님
- Globalization 승인 아님

valid bounded first step는 interaction-quality metric입니다. Verification PASS나 Final Gate PASS와 동일하지 않습니다.

Source: [`WORKER_ROB_002_EVIDENCE.md`](WORKER_ROB_002_EVIDENCE.md), [`WORKER_ROB_002_RESULTS.json`](WORKER_ROB_002_RESULTS.json)

---

## Research 010 — Worker hardcode는 모두 "설정값"인가

### Question

향후 cross-Repository/global use를 생각할 때 code에 박힌 literal을 모두 configuration으로 빼면 되는가?

### QH-V2-WORKER-DIAG-001 classification

Evidence는 hardcode를 같은 종류로 보지 않았습니다.

#### Environment/configuration candidate

- Ollama base URL `http://127.0.0.1:11434`
- default model `qwen3:8b`
- duplicated Worker/doctor endpoint/model resolution
- general qhops remote / target branch candidate

#### Policy-controlled value

- Worker timeout `30.0`
- `think:false`

#### Safety-critical policy

- Worker step budget
- Retry attempt budget
- authority/tool boundaries

### Interpretation

"hardcoded = bad"가 아닙니다. machine-specific configuration과 safety policy를 구분해야 합니다.

특히 step/retry limits를 자유 user setting으로 바꾸면 safety contract가 약해질 수 있습니다.

### Decision

별도의 configuration/portability Task 후보는 정당화되지만, Worker diagnosis Task에서는 아무 runtime behavior도 변경하지 않았습니다.

`GLOBALIZATION = NOT AUTHORIZED`

---

## Research 011 — Human relay를 줄여도 deterministic safety를 유지할 수 있는가

### Background

G1은 exact sealed queue 방식으로 narrow automation을 시험했지만 new Evidence가 생겼을 때 remaining authority가 revoke되었습니다.

이후 반복 Human prompt 자체가 이미-approved routine work의 병목으로 남았습니다.

### Decision experiment

[`ADR-017`](../DECISIONS.md)은 approval cadence를 Exception-Driven Human Supervision으로 변경했습니다.

Routine, already-authorized work는 deterministic checks가 정상일 때 계속할 수 있습니다.

### Mandatory Human exceptions

- FAIL / BLOCKED / SAFETY
- repeated unresolved timeout
- unexpected mutation / scope violation
- Git divergence / ambiguity
- new Task / reprioritization
- Candidate production promotion
- Architecture / Requirements / Trust Boundary change
- model / reasoning / timeout / retry / step-budget policy change

### Interpretation

Human을 제거한 것이 아니라 Human review를 **mechanical relay에서 exception/direction judgment로 이동**시킨 것입니다.

### Constraint

FR-004는 그대로입니다. Qwen Worker는 다음 Task를 고르거나 시작하지 않습니다.

---

## 현재 연구 결론 요약

| 질문 | 현재 Evidence 기반 결론 |
|---|---|
| Local Qwen self-PASS를 믿어도 되는가 | 아니오. deterministic Evidence/Final Gate 필요 |
| Native Ollama tool calling이 가능한가 | 가능. 그러나 semantic correctness는 별도 |
| Verification concurrency가 큰 성능 향상을 주는가 | 현재 Evidence에서는 아니오 (~0.7%) |
| Git fixture reuse가 유효한가 | 예. isolation을 유지하는 방향으로 채택됨 |
| one-tool prompt 강화만으로 Worker exact success가 좋아지는가 | ROB-001에서는 아니오, 0/10 vs 0/10 |
| full Task timeout이 input length만의 문제인가 | 아니오 |
| tool schema만으로 timeout이 발생하는가 | 아니오 |
| deterministic Worker Brief가 유망한가 | ROB-002 Candidate A에서 강한 개선 Evidence 있음 |
| Candidate A가 production인가 | 아니오. separate production Task 필요 |
| Globalization이 승인됐는가 | 아니오 — `GLOBALIZATION = NOT AUTHORIZED` |

---

## 연구 원칙

Qwen Harness의 연구는 다음 순서를 지향합니다.

```text
Observation
→ Hypothesis
→ Controlled Task / Experiment
→ Objective Evidence
→ Interpretation
→ Accept / Reject / Diagnose Further
→ Separate Production Task if justified
```

실패 실험도 삭제하지 않습니다. WORKER-ROB-001처럼 실패 자체가 다음 진단과 lifecycle Architecture를 만든 중요한 Evidence가 될 수 있기 때문입니다.

---

## 관련 문서

- [Project Timeline](PROJECT_TIMELINE.md)
- [Development Log](DEVELOPMENT_LOG.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [WORKER-DIAG-001 Evidence](WORKER_DIAG_001_EVIDENCE.md)
- [WORKER-ROB-001 Evidence](WORKER_ROB_001_EVIDENCE.md)
- [WORKER-ROB-002 Evidence](WORKER_ROB_002_EVIDENCE.md)
- [Architecture Decisions](../DECISIONS.md)
