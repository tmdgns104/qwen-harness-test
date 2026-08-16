# QH-V2-SPEC-001 - Formalize Qwen Harness V2 Specification

## Status

APPROVED - READY FOR IMPLEMENTATION

## Goal

현재 ChatGPT/Human 설계와 기존 Qwen Harness V2 작업에만 존재하는 상위 프로젝트 목적, 운영 원칙, Architecture, 현재 상태를 Repository Formal Specification으로 고정한다.

이번 Task는 새로운 Architecture를 발명하는 작업이 아니다.

이미 합의된 Qwen Harness V2 방향을 Repository의 Source of Truth로 옮겨 이후 새로운 ChatGPT, Codex, OpenCode, Qwen 세션도 Repository만 읽고 현재 목적과 진행 상태를 복원할 수 있게 한다.

## Problem

현재 Qwen Harness Repository에는 개별 Task 명세와 fixture는 존재하지만 프로젝트 전체 목적과 Architecture를 설명하는 Formal Specification이 부족하다.

이 때문에 새 세션에서는 다음 정보가 Repository만으로 복원되지 않는다.

* Qwen Harness를 왜 만드는가
* Codex token exhaustion 시 어떤 방식으로 개발을 계속하는가
* OpenCode + Qwen의 역할은 무엇인가
* Codex의 역할은 무엇인가
* Qwen의 자기 보고 PASS를 왜 신뢰하지 않는가
* Git을 왜 Evidence와 external memory로 사용하는가
* ECC의 어떤 장점을 흡수하려 하는가
* LangGraph를 어느 단계에서 어떤 목적으로 도입하는가
* 현재 Milestone과 다음 구현 단계는 무엇인가

## Project Goal

Codex 사용 가능 여부와 관계없이 Repository 기반 개발을 지속할 수 있는 local-first development harness를 구축한다.

OpenCode + local Qwen을 저비용 실행 계층으로 사용하고, Git Evidence와 deterministic verification으로 local LLM의 신뢰성 한계를 보완한다.

Codex는 필수 구성요소가 아니라 어려운 작업에 사용할 수 있는 optional premium executor다.

Codex token이 소진되거나 사용할 수 없는 상태에서도 개발이 중단되지 않아야 한다.

Qwen이 직접 처리하기 어려운 작업은 작은 Qwen-safe Task로 분해한 뒤 계속 수행할 수 있어야 한다.

## Core Roles

### Human

* 목적 결정
* 범위 결정
* 중요한 Architecture Decision 승인
* Human Gate 최종 승인

### ChatGPT

* Problem 분석
* Requirements 설계
* Architecture 설계
* Task 분해
* 기술 판단
* Evidence Review
* Qwen-safe Task decomposition 지원

### Repository

프로젝트의 authoritative Source of Truth다.

Chat history, OpenCode session, Qwen 자기 보고, LangGraph runtime state는 Repository를 대체하지 않는다.

### OpenCode + Qwen

구현 Worker다.

주요 책임:

* 지정된 현재 Task 하나를 수행한다.
* Task의 Allowed Changes 범위 안에서 구현한다.
* Forbidden Changes를 수정하지 않는다.
* 요구사항을 추가하거나 확대 해석하지 않는다.
* 다음 Task를 선택하거나 시작하지 않는다.

다음 책임을 갖지 않는다.

* 최종 PASS/FAIL 판정
* Architecture 변경
* 프로젝트 상태의 자율 결정
* 전체 Repository 검증
* 자기 보고를 Evidence로 사용하는 것

### Git

단순 버전 관리 도구가 아니라 다음 역할을 수행한다.

* Task 실행 baseline
* 외부 상태 기억
* 실제 changed path 확인
* 실제 diff Evidence
* clean working tree Gate
* checkpoint
* rollback 기반
* Qwen 자기 보고와 독립적인 사실 확인 수단

### Deterministic Verifier

LLM의 주장 대신 실제 Evidence를 사용하여 기계적으로 판정 가능한 조건을 검증한다.

예:

* changed paths
* allowed/forbidden scope
* file existence
* exact content
* command exit code
* pytest
* ruff
* mypy
* deterministic output

Semantic Architecture Review와 분리한다.

### Codex

Optional premium executor다.

Codex가 없어도 Harness Core는 동작해야 한다.

복잡하거나 Qwen으로 안전하게 처리하기 어려운 구현에서 선택적으로 사용할 수 있다.

## Trust Boundary

Qwen의 다음 출력은 최종 Evidence로 사용하지 않는다.

* PASS
* verification complete
* protected files unchanged
* tests passed
* only requested files changed

실제 완료 여부는 Git/Test Evidence로 판단한다.

Qwen의 최종 메시지는 worker report로만 취급한다.

## Execution Principle

Task 실행 전 가능하면 working tree는 clean이어야 한다.

기본 흐름:

1. Current Task 확인
2. Task Contract 읽기
3. Git baseline 확인
4. Worker 실행
5. Git Evidence 수집
6. Allowed / Forbidden scope 검증
7. Task Verification 실행
8. Evidence Review
9. PASS / RETRY / STOP 결정
10. Human Gate가 필요한 경우 사람에게 전달

## Failure Principle

실패가 발생했다고 Architecture를 임의 변경하지 않는다.

실패 종류를 구분한다.

* Worker tool error
* Task specification error
* scope violation
* deterministic verification failure
* Qwen capability limitation
* Architecture conflict

Architecture 변경이 필요하면 STOP하고 별도 Decision으로 다룬다.

같은 실패를 무제한 반복하지 않는다.

Qwen으로 처리하기 어려운 Task는 무조건 Codex로 넘기기 전에 더 작은 Qwen-safe Task로 분해할 수 있는지 검토한다.

## Codex Availability Principle

### Codex Available

Task 난이도와 비용을 고려해 Qwen 또는 Codex를 선택할 수 있다.

Routine / small task는 Qwen을 우선 사용할 수 있다.

### Codex Unavailable or Token Exhausted

개발을 중단하지 않는다.

* Qwen-safe Task → OpenCode + Qwen
* Qwen에 너무 큰 Task → Task decomposition
* Architecture Decision 필요 → STOP 후 Human + ChatGPT
* 안전하게 분해할 수 없는 고난도 작업 → BLOCKED 상태로 명확히 기록

Codex unavailable 자체는 프로젝트 중단 사유가 아니다.

## ECC Adoption Direction

Everything Claude Code의 전체 구조를 그대로 복제하지 않는다.

현재 목적에 필요한 장점만 단계적으로 흡수한다.

후속 검토 대상:

* Task Router
* Agent role separation
* Skill selection
* implicit skill routing
* context 최소화
* long-run boundary
* pre-execution gate
* Human Gate
* token-efficient execution

ECC 기능은 Qwen Harness Core가 안정된 이후 도입한다.

## LangGraph Direction

LangGraph는 현재 Qwen Worker 내부에 넣지 않는다.

LangGraph는 후속 단계에서 Control Plane / Orchestration Layer로 사용한다.

예상 책임:

* execution state
* node transition
* retry
* stop
* resume
* Human Gate
* executor routing
* evidence-based branching

LangGraph runtime state는 Repository Source of Truth를 대체하지 않는다.

LangGraph 도입 전 Qwen Harness의 deterministic Evidence/Verification Core를 먼저 완성한다.

## Architecture Layers

```text
Human + ChatGPT
       |
       v
Repository Source of Truth
       |
       v
Execution / Model Router
       |
       +-------------------+
       |                   |
       v                   v
OpenCode + Qwen          Codex
Local Executor     Optional Premium Executor
       |                   |
       +---------+---------+
                 |
                 v
            Git Evidence
                 |
                 v
      Deterministic Verification
                 |
          +------+------+
          |      |      |
         PASS   RETRY   STOP
```

후속 단계에서 위 구조의 Control Plane에 ECC-inspired routing과 LangGraph orchestration을 추가한다.

## Current Milestone

### Milestone 1

Codex가 없어도 OpenCode + Qwen + Git-based Harness만으로 작은 Repository Task를 안전하게 계속 수행할 수 있다.

Milestone 1에 ECC full adoption이나 LangGraph implementation은 필요하지 않다.

## Current Progress

완료된 기본 작업:

* QH-V2-001: Qwen task-worker 책임 축소
* QH-V2-REG-001: PASS
* QH-V2-REG-002: PASS
* TASK-004 fixture: PASS
* QH-V2-002 Evidence Collector specification 작성
* QH-V2-002A Change Contract Parser specification 작성

현재 Regression에서 Qwen의 자기 보고와 실제 tool trace가 일치하지 않을 수 있음을 관찰했다.

따라서 independent Evidence Layer가 필요하다는 설계 전제가 유지된다.

## Planned Sequence

1. Formal Specification 확정
2. QH-V2-002A - Change Contract Parser
3. QH-V2-002 - Git Evidence Collector
4. Deterministic Verifier
5. Harness Runner
6. Milestone 1 Regression Suite
7. ECC-inspired Router / Agent / Skill / Context control
8. Qwen-safe Task decomposition
9. Optional Codex escalation
10. LangGraph Control Plane
11. 실제 Repository에서 단계적 검증

## Required Repository Documents

이번 Task에서 다음 Formal Specification을 작성한다.

* `PROJECT.md`
* `REQUIREMENTS.md`
* `ARCHITECTURE.md`
* `DECISIONS.md`
* `AGENTS.md`
* `STATUS.md`

각 문서는 중복을 최소화하고 책임을 분리한다.

### PROJECT.md

* Problem
* Goal
* Scope
* Non-Goals
* Milestone

### REQUIREMENTS.md

* 기능 요구사항
* 비기능 요구사항
* Verification 요구사항
* Codex unavailable 요구사항

### ARCHITECTURE.md

* Human / ChatGPT / Repository / Worker / Git / Verifier 역할
* Trust Boundary
* 실행 흐름
* ECC / LangGraph의 후속 위치

### DECISIONS.md

현재까지 합의된 중요한 결정을 ADR 형태로 기록한다.

최소 다음 결정을 포함한다.

* Repository is Source of Truth
* Qwen is Worker, not final verifier
* Qwen self-reported PASS is non-authoritative
* Git-based independent Evidence
* Codex is optional
* local Qwen fallback must continue during Codex exhaustion
* deterministic verification before semantic review
* ECC adoption is incremental
* LangGraph adoption is deferred until Harness Core is stable

### AGENTS.md

* 한 번에 Current Task 하나만 수행
* Task 시작 전 Formal Specification 확인
* Allowed / Forbidden 준수
* Architecture 임의 변경 금지
* 다음 Task 자동 시작 금지
* Evidence 없이 완료 주장 금지

### STATUS.md

현재 실제 상태와 다음 Gate를 사람이 읽을 수 있게 기록한다.

기존 완료 Regression을 보존하고 현재 구현 대기 상태를 명확히 한다.

## Allowed Changes

* `PROJECT.md`
* `REQUIREMENTS.md`
* `ARCHITECTURE.md`
* `DECISIONS.md`
* `AGENTS.md`
* `STATUS.md`

## Forbidden Changes

* `src/**`
* `tools/**`
* `tests/**`
* 기존 `tasks/**`
* OpenCode agent configuration
* fixture files
* 다른 Repository

## Acceptance Criteria

* 여섯 Formal Specification 문서만 생성 또는 수정한다.
* 기존 Qwen Harness V2 설계를 임의로 변경하지 않는다.
* Codex unavailable 상태에서도 OpenCode + Qwen으로 개발을 지속한다는 목적이 명시된다.
* Codex가 optional executor임이 명시된다.
* Qwen 자기 보고가 최종 Evidence가 아님이 명시된다.
* Git의 Evidence / baseline / rollback 역할이 명시된다.
* deterministic verification과 semantic review가 구분된다.
* ECC 도입 방향이 후속 단계로 기록된다.
* LangGraph가 Harness Core 이후 Control Plane으로 도입된다는 방향이 기록된다.
* Milestone 1이 명시된다.
* 현재 완료된 Regression 상태가 STATUS.md에 반영된다.
* QH-V2-002A가 다음 구현 Gate임이 명확하다.
* 애플리케이션 코드를 구현하지 않는다.
* third-party dependency를 추가하지 않는다.

## Verification

구현 후 다음을 확인한다.

* `git diff --name-only` 결과가 Allowed Changes 범위 안에만 있다.
* 여섯 Formal Specification 파일이 존재한다.
* 각 문서에서 요구된 핵심 설계가 확인된다.
* 기존 Task 파일이 수정되지 않았다.
* `src/**`, `tools/**`, `tests/**`가 수정되지 않았다.
* dependency 파일이 수정되지 않았다.

## Stop Condition

Formal Specification 작성과 Verification Evidence 확보 후 즉시 중단한다.

QH-V2-002A를 구현하지 않는다.

QH-V2-002를 구현하지 않는다.

ECC 기능을 구현하지 않는다.

LangGraph를 설치하거나 구현하지 않는다.

다음 Task를 자동으로 시작하지 않는다.
