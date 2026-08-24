# Qwen Harness V2 Requirements

이 문서는 Qwen Harness V2의 기능 요구사항과 검증 경계를 정의합니다. 기술 token,
Task/FR ID, 상태값과 권한 경계는 의미 보존을 위해 원문 literal을 유지합니다.

## 기능 요구사항

### FR-001 - Codex-independent continuation

Codex를 사용할 수 없거나 token/usage limit이 소진되어도 Harness를 통해 Repository
작업을 계속할 수 있어야 합니다.

### FR-002 - Local Worker execution path

Harness는 Codex나 paid model이 없어도 사용할 수 있는 local implementation Worker
경로를 제공해야 합니다.

현재 기본 local Worker 후보는 native Ollama API + `Qwen3:8B`입니다.
OpenCode는 선택 가능한 대안 Worker/backend으로 남을 수 있습니다.

### FR-003 - Small Task execution

Qwen 구현 작업은 하나의 명확한 Goal과 제한된 change scope를 가진 작은 Task로
할당할 수 있어야 합니다.

### FR-004 - One Task at a time

Worker는 **명시적으로 할당된 현재 Task만 실행해야 하며, 다른 Task를 자동으로
선택하거나 시작해서는 안 됩니다.**

원문 요구사항:

> A Worker must execute only the explicitly assigned current Task and must not automatically select or start another Task.

이 Worker 제한은 Accepted governance policy 아래에서 외부 Human/ChatGPT/Supervisor
workflow가 이미 승인된 routine lifecycle을 이어가거나, 정확히 이미 승인된 successor를
시작하는 것까지 금지하지는 않습니다. 단, 외부 continuation이 Worker에게 successor
선택, lifecycle, Git, Verification 또는 Final PASS 권한을 이전해서는 안 되며,
Human-review exception 조건에서는 반드시 중단해야 합니다.

### FR-005 - Change scope contract

Task는 Allowed Changes와 Forbidden Changes를 선언할 수 있어야 하며, 실제 Repository
변경이 해당 Task 계약과 일치하는지 독립적으로 확인할 수 있어야 합니다.

### FR-006 - Independent completion evidence

Qwen의 self-reported `PASS`, verification 주장 또는 file-change 주장을 authoritative
완료 Evidence로 취급해서는 안 됩니다.

완료는 Git, tests, command exit code, exact file content 또는 다른 객관적 Evidence로
판정해야 합니다.

### FR-007 - Git baseline

Worker 실행 전에 clean Git baseline을 식별할 수 있어야 하며, Task 변경과 기존 변경을
구분할 수 있어야 합니다.

### FR-008 - Failure stop behavior

Task가 실패하거나, scope를 위반하거나, Architecture와 충돌하거나, 승인되지 않은
결정이 필요해지면 workflow는 조용히 Architecture/Requirements를 바꾸지 말고
중단해야 합니다.

### FR-009 - Optional Codex

Codex는 Harness Core의 필수 의존성이 아니라 선택 가능한 고성능 executor여야 합니다.

### FR-010 - Qwen-safe decomposition

Task가 Qwen에게 너무 어렵거나 크면 escalation을 고려하기 전에 더 작은 Qwen-safe
Task로 분해할 수 있어야 합니다.

### FR-011 - Worker/backend independence

Task contract, scope check, Git Evidence, Verification과 completion gate는 OpenCode-specific
behavior 또는 단일 Worker frontend/backend에 종속되어서는 안 됩니다.

### FR-012 - Harness-owned tool boundary

Tool permission과 실행 경계는 deterministic Harness code가 강제해야 합니다.
LLM의 요청만으로 Repository operation이 허가되어서는 안 됩니다.

### FR-013 - Bounded retry and safe stop

Worker retry는 유한해야 합니다.

반복 실패는 무한 loop 또는 제한 없는 prompt 복잡도 증가로 이어져서는 안 되며,
최종적으로 `FAIL` 또는 `BLOCKED`로 종료되어야 합니다.

### FR-014 - Manifest-bound optional external Codex CLI Supervisor

선택 가능한 external Codex CLI Supervisor는 Human-approved immutable Approval Manifest가
포함하는 **정확한 ordered queue**만 실행할 수 있습니다.

이 위임 권한은 Qwen Worker 바깥에 있습니다. `FR-004`는 그대로 유지되며 Worker는
명시적으로 할당된 현재 Task만 실행하고 successor를 선택하거나 시작하지 않습니다.

각 delegated mutation 전에 deterministic `qhops` guard logic은 다음을 검증해야 합니다.

- manifest
- current branch / remote
- authority-source blobs
- queue order
- covered Task identity
- Immutable Contract Sections
- lifecycle eligibility
- revocation state

어떤 mismatch도 fail closed해야 합니다.

유효한 하나의 manifest 범위에서 Supervisor는 다음만 수행할 수 있습니다.

- 정확한 next already-approved covered Task 시작
- implementation commit 생성
- exact implementation HEAD에 authoritative `qh close` 실행
- 별도 lifecycle commit 생성
- 재검증 후 manifest의 정확한 successor로만 진행
- `origin`에 `HEAD:main`만 fast-forward push

다음은 금지됩니다.

- force push
- rebase / history rewrite
- Task creation
- covered-contract 또는 queue mutation
- covered 실행 중 Architecture/Requirements mutation
- scope expansion
- Final Gate bypass
- Qwen/Worker authority expansion

승인은 revocation, manifest mismatch, policy invalidation 또는 covered queue가 Human
Architecture Gate에 도달해 완료되는 시점에 만료됩니다.

## Verification Requirements

- 실제 changed paths를 Worker self-report와 독립적으로 확인할 수 있어야 합니다.
- Forbidden-path modification을 탐지할 수 있어야 합니다.
- Task가 exact output을 정의하는 경우 required exact file content를 독립적으로 비교할 수 있어야 합니다.
- Evidence로 사용하는 test/command 결과에는 실제 exit result가 포함되어야 합니다.
- LLM이 `PASS`라고 말했다는 이유만으로 완료를 승인해서는 안 됩니다.
- 실패한 Task가 자동으로 다음 Task로 진행해서는 안 됩니다.

## Non-Functional Requirements

- 프로젝트 Source of Truth는 chat history나 LLM session memory가 아니라 Repository 문서와 Git입니다.
- orchestration complexity를 추가하기 전에 Harness Core는 이해 가능하고 최소한의 구조를 유지해야 합니다.
- local execution은 paid model 없이도 사용할 수 있어야 합니다.
- Qwen Worker 책임은 좁게 유지해야 합니다.
- Architecture 변경에는 명시적인 Human approval이 필요합니다. ChatGPT는 기술 분석과 recommendation을 제공할 수 있지만 Worker가 Architecture 변경을 추론하거나 승인해서는 안 됩니다.

## Milestone 1 Boundary

Milestone 1에서 필요한 것은 다음입니다.

- local Worker가 Codex나 paid model 없이 작은 Repository Task를 실행할 수 있음
- Git/Test 또는 다른 객관적 Evidence로 결과를 독립 검증할 수 있음
- 실패 시 다음 Task로 자동 진행하지 않고 안전하게 멈출 수 있음

Milestone 1에서 필수로 요구하지 않는 항목은 다음입니다.

- full ECC adoption
- automatic Agent/Skill routing
- automatic Codex escalation
- LangGraph orchestration

## 현재 권한 경계

현재 Task/Architecture에 의해 별도 승인되지 않은 Globalization이나 Trust Boundary 확대는
허용되지 않습니다.

`GLOBALIZATION = NOT AUTHORIZED`
