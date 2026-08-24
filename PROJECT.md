# Qwen Harness V2

## 프로젝트 목적

Codex를 사용할 수 없거나 token/usage limit이 소진된 상황에서도 Repository 작업을
계속할 수 있도록 **local-first 개발 Harness**를 구축합니다.

Qwen Harness의 목적은 단순히 로컬 모델에게 코드를 생성시키는 것이 아닙니다.
Human이 승인한 작은 Task 안에서만 Worker가 움직이게 하고, 실제 완료 여부는
Git/Test 또는 다른 객관적 Evidence로 독립 검증하는 것입니다.

## 기본 실행 모델

- Harness Core는 특정 Agent frontend나 Worker backend에 종속되지 않습니다.
- 현재 기본 local Worker 후보는 native Ollama API + `Qwen3:8B`입니다.
- OpenCode는 선택 가능한 대안 Worker/backend이자 향후 benchmark 후보로 남깁니다.
- Codex는 선택 가능한 고성능 executor이며 Harness Core의 필수 의존성이 아닙니다.
- 어려운 작업은 Qwen이 안전하게 처리할 수 있는 더 작은 Task로 분해할 수 있습니다.
- Worker는 명시적으로 할당된 현재 Task만 실행하며 다음 Task를 자동 선택하거나 시작하지 않습니다.

## 신뢰성 원칙

- Qwen의 self-reported `PASS`는 authoritative하지 않습니다.
- 완료는 Git/Test 또는 다른 객관적 Evidence로 판정합니다.
- 프로젝트 상태의 기준은 chat history가 아니라 Repository 문서와 Git입니다.
- deterministic Harness가 만든 failure Evidence는 LLM 출력으로 뒤집을 수 없습니다.
- Tool permission, Verification, lifecycle, Git Evidence와 Final Gate 권한은 모델 바깥의 결정론적 경계가 소유합니다.

## Human과 Worker의 역할 경계

Human은 프로젝트 목적, 핵심 Scope, 중대한 Architecture/Requirements 변경과 예외
상황을 판단합니다. ChatGPT/Supervisor는 설계, Task 분해, review와 다음 단계 판단을
도울 수 있습니다. Worker는 승인된 현재 Task 구현에만 집중합니다.

이미 승인된 routine lifecycle을 외부 Supervisor가 이어가는 정책이 있더라도,
그 권한이 Qwen Worker에게 이전되는 것은 아닙니다. `FR-004`의 Worker successor
금지는 유지됩니다.

## Milestone 1

Codex나 paid model 없이도 local Worker가 작은 Repository Task를 안전하고 반복
가능하게 수행하고, deterministic Git/Test Evidence가 완료 여부를 독립 검증하며,
위험한 실패에서는 자동으로 멈출 수 있는 상태를 목표로 합니다.

현재 Milestone 1 핵심 경로에는 다음이 포함됩니다.

- backend-independent Worker contract
- native Ollama Adapter
- Harness-owned Repository read/write tools
- Single-Task Runner
- bounded retry / safe stop
- `qh` CLI
- authoritative `qh close`
- 실제 Qwen Repository E2E
- lifecycle / Evidence hardening
- 안전한 remote handoff (`qh handoff-check` + `git merge --ff-only`)

## 향후 방향

향후 단계에서 다음을 선택적으로 검토할 수 있습니다.

- 추가 local Worker backend와 model benchmark
- ECC에서 참고한 routing, skill selection, context-management 방식
- optional Codex escalation
- LangGraph orchestration
- 자연어 중심 사용자 UX

이 항목들은 단순히 목록에 있다는 이유만으로 구현 승인된 것이 아닙니다.
Architecture/Requirements/Trust Boundary를 넓히는 변경은 별도 Human Gate가 필요합니다.

현재 프로젝트 전체에 대해:

`GLOBALIZATION = NOT AUTHORIZED`
