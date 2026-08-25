# Qwen Harness

로컬 Qwen LLM을 단순한 코드 생성기가 아니라, **Task Scope, 제한된 Tool 권한,
Git Evidence, Verification, Final Gate로 통제되는 검증 가능한 Coding Worker**로
사용하기 위한 local-first 개발 Harness입니다.

> 핵심 원칙: **LLM self-report != Evidence**

Qwen이 “수정했습니다”, “테스트를 통과했습니다”, `PASS`라고 말하는 것만으로는
작업이 완료되지 않습니다. 실제 Git changed paths, 승인된 Verification 명령의
exit code, scope 판정과 deterministic Final Gate가 완료 근거입니다.

## 현재 상태

운영 상태의 최종 권위는 항상 [STATUS.md](STATUS.md)입니다.

2026-08-25 기준 주요 상태:

| 영역 | 상태 | 의미 |
|---|---|---|
| Harness Core | ✅ 구현/검증됨 | Git baseline, ChangeScope, Verification, Evidence, Final Gate |
| Native Ollama Worker | ✅ 구현/검증됨 | 기본 `qwen3:8b`, native Ollama API |
| Repository Tools | ✅ 구현/검증됨 | `read_repo_text`, scoped `write_repo_text` |
| Single-Task Runner | ✅ 구현/검증됨 | 현재 ACTIVE Task 하나만 실행 |
| Bounded Retry | ✅ 구현/검증됨 | 유한 retry, 안전한 FAIL/BLOCKED 종료 |
| `qh task-new` | ✅ QH-V2-OPS-001 | Human-review Task 초안 생성 |
| `qh doctor` | ✅ QH-V2-OPS-002 | Python/Git/Repository/Ollama/model 진단 |
| 안전한 원격 handoff | ✅ QH-V2-OPS-GIT-001 | `qh handoff-check` + `git merge --ff-only` |
| 한국어 문서 정리 | ✅ QH-V2-DOC-KO-001 | GitHub 사용자-facing 문서 한국어 우선 |
| Candidate A 결정 | ✅ QH-V2-ARCH-018 | Deterministic Worker Brief Accepted |
| Candidate A production integration | ✅ QH-V2-WORKER-ROB-003 | production initial Worker input에 최소 통합 |
| Windows CMD launcher | ✅ QH-V2-OPS-003 | Repository-root `qh.cmd` thin launcher |
| close observability | ✅ QH-V2-PERF-006 | START/HEARTBEAT/COMPLETE timing 출력 |
| Git-heavy fixture 최적화 | ✅ QH-V2-PERF-007 | focused 14 tests 35.15% 개선 |
| Verification runtime | ⚠ Architecture Review 필요 | routine close 300초 목표 미달 |
| QH-V2-OPS-004 | ⏸ 보류 | Verification Strategy 결정 전 시작 금지 |

### 최신 성능 Evidence

`QH-V2-PERF-007`은 `COMPLETE - VERIFIED`입니다.

- implementation HEAD: `031dcae9beaef2db2730fbb81051fff7c3a40e79`
- lifecycle commit: `7ea2f389b7bd03858325dc38d7c72e0615653847`
- focused 14 tests: `551.646s -> 357.777s` (`35.15%` 개선)
- Git process starts: `284 -> 203` (`28.52%` 감소)
- final `tests.test_qh`: `1157.8s`
- final review phase: `1613.8s`
- Final Gate: `PASS`

fixture 최적화 자체는 성공했지만 routine authoritative close가 practical target인
`300s`를 크게 초과했습니다. 따라서 Repository 계약대로 다음 단계는
**Verification Strategy / Regression Tiering Architecture Review**이며
`QH-V2-OPS-004`를 아직 시작하지 않습니다.

현재 검토 후보는 다음과 같습니다.

```text
Task close
  -> Task에 직접 관련된 focused authoritative regression
  -> 핵심 invariant suite
  -> fresh exact HEAD Evidence

Milestone / Release / Main Gate
  -> repository-wide integration regression
  -> fresh exact HEAD Evidence
```

이 구조는 아직 Accepted Architecture가 아닙니다. Human + ChatGPT Architecture Review
전에는 임의 구현하지 않습니다.

`GLOBALIZATION = NOT AUTHORIZED`

## 이 프로젝트가 해결하려는 문제

작은 로컬 LLM은 코드를 작성할 수 있지만 다음을 스스로 안정적으로 보장하지
못합니다.

- 허용된 파일만 수정했는가?
- 테스트를 실제로 실행했는가?
- 실패한 검증을 숨기지 않았는가?
- 반복 실패에서 안전하게 멈췄는가?
- Repository 작업이 정말 완료되었는가?
- 다음 Task를 임의로 시작하지 않았는가?

Qwen Harness는 모델을 Final Authority로 두지 않습니다. 모델 바깥의 결정론적
Harness가 Tool 권한, 변경 범위, Verification, Git Evidence와 완료 판정을
소유합니다.

```text
Human-approved Task Contract
        ↓
Qwen Worker
        ↓
Harness-owned Tool Boundary
        ↓
Git / Verification Evidence
        ↓
Deterministic Final Gate
```

## 한눈에 보는 구조

```mermaid
flowchart TD
    Human["Human: 목적·핵심 범위·예외 판단"]
    ChatGPT["ChatGPT: 설계·기술 판단·Review"]
    Task["Task Contract\nGoal / Allowed / Forbidden / Verification"]
    Run["qh run TASK-ID"]
    Retry["Bounded Retry"]
    Runner["Single-Task Runner"]
    Adapter["OllamaToolSession"]
    Qwen["Qwen3:8B\nthink:false"]
    Tools["Harness-owned Tools\nread_repo_text / write_repo_text"]
    Repo[("Git Repository")]
    Commit["Implementation commit"]
    Close["qh close IMPLEMENTATION-HEAD"]
    Gate["Scope + Verification + Diff Check + Final Gate"]
    Done["COMPLETE - VERIFIED"]

    Human --> ChatGPT --> Task --> Run --> Retry --> Runner --> Adapter --> Qwen
    Qwen --> Adapter --> Runner --> Tools --> Repo
    Repo --> Human --> Commit --> Close --> Gate --> Done
```

Codex CLI는 이 구조에서 편리한 외부 implementation/test/debug executor로 사용할 수
있지만 **필수 구성요소는 아닙니다.** Codex를 사용하지 않을 때는 Human이 CMD/Git
실행자 역할을 맡고 ChatGPT가 설계·Review를 계속 담당할 수 있습니다.

자세한 수동 운영 방법은 [Codex 없이 계속하기](docs/MANUAL_OPERATOR_GUIDE.md)를
참고하세요.

`qh run`이 `NORMAL`로 끝났다는 사실은 Repository Task PASS가 아닙니다.
최종 완료 판정은 `qh close <IMPLEMENTATION-HEAD>`가 수행하는 객관적 Evidence와
Final Gate를 통해 이루어집니다.

## 실제로 검증된 환경

아래는 최소 사양이 아니라 실제 Worker E2E가 성공한 한 가지 환경입니다.

| 항목 | 검증 환경 |
|---|---|
| 운영체제 | Windows |
| GPU | NVIDIA RTX 5070 Laptop GPU |
| VRAM | 8 GB |
| System RAM | 32 GB |
| 모델 런타임 | Ollama |
| 기본 모델 | `qwen3:8b` |
| 결과 | 실제 Repository Worker E2E 성공 |

다른 GPU, CPU-only, Linux/macOS 환경은 동일 수준의 E2E Evidence가 아직 없을 수
있습니다. 8 GB VRAM을 공식 최소 사양으로 해석하면 안 됩니다.

## 설치

### 1. Repository 복제

```powershell
git clone https://github.com/tmdgns104/qwen-harness-test.git
cd qwen-harness-test
```

### 2. 필수 프로그램 확인

```powershell
python --version
git --version
ollama --version
```

현재 소스는 Python 3.12 이상 문법을 사용합니다. Git/Ollama 최소 버전은
별도로 고정하지 않습니다.

### 3. 기본 모델 준비

```powershell
ollama pull qwen3:8b
ollama list
```

### 4. 환경 진단

```powershell
qh.cmd doctor
```

또는 기존 direct Python 경로:

```powershell
python tools\qh.py doctor
```

### 5. 현재 상태 확인

```powershell
qh.cmd status
qh.cmd preflight
```

처음부터 실제 Task lifecycle을 따라 해보고 싶다면
[Quick Start](docs/QUICKSTART.md)를 참고하세요.

## qh CLI

| 명령 | 목적 | 중요한 의미 |
|---|---|---|
| `qh.cmd doctor` | 환경 진단 | 읽기 전용. PASS/WARN/FAIL 구분 |
| `qh.cmd task-new <TASK-ID>` | Task 초안 생성 | 자동 승인/start/commit/close 하지 않음 |
| `qh.cmd status` | 현재 Task와 변경 경로 확인 | PASS 판정 명령이 아님 |
| `qh.cmd preflight` | Repository/Task/scope 기본 점검 | 실행 전 진단 |
| `qh.cmd verify` | 현재 Task Verification 실행 | 진단용, full Final Gate 아님 |
| `qh.cmd review [BASELINE]` | scope + Verification + Final Gate 진단 | 정상 final path에서는 선택적 |
| `qh.cmd start <TASK-ID>` | 승인된 Task를 ACTIVE로 전환 | clean baseline 필요 |
| `qh.cmd run <TASK-ID>` | Qwen Worker 실행 | `NORMAL`은 Task PASS가 아님 |
| `qh.cmd close <COMMIT>` | authoritative close | Task Verification + scope + Final Gate |
| `qh.cmd handoff-check <REMOTE-REF>` | 원격 handoff 안전성 검사 | read-only, Git mutation 없음 |

`qh.cmd`는 기존 Python CLI에 전체 argument를 그대로 전달하고 child exit code를
그대로 반환하는 thin launcher입니다. lifecycle, Git 또는 PASS authority를 추가하지
않습니다.

## 표준 Task lifecycle

```text
1. Problem / Goal 정의
2. Requirements / Architecture 확인
3. Task 계약 작성 및 Human 승인
4. Task contract commit
5. clean working tree 확인
6. qh start TASK-ID
7. start lifecycle commit
8. 구현 또는 qh run
9. focused test / diff 검토
10. implementation commit
11. qh close IMPLEMENTATION_HEAD
12. Final Gate PASS 확인
13. lifecycle completion commit
14. safe push
```

개발 중 전체 regression을 습관적으로 반복하지 않습니다. 변경한 기능의 focused
검사를 우선하며 최종 Verification 정책은 현재 Task 계약과 Accepted Architecture를
따릅니다.

## 안전한 원격 작업 handoff

ChatGPT/GitHub 등 원격 작업에서 만든 변경을 로컬로 가져오는 정상 경로는
**exact baseline + atomic handoff + read-only check + fast-forward merge**입니다.

```powershell
git fetch origin
qh.cmd handoff-check origin/work/<handoff-branch>
git merge --ff-only origin/work/<handoff-branch>
```

주요 classification:

- `FAST_FORWARD_SAFE`: local HEAD가 handoff commit의 정확한 parent
- `ALREADY_APPLIED_EXACT`: exact handoff commit이 현재 HEAD
- `ALREADY_CONTAINED`: handoff commit이 이미 현재 history에 포함
- `STOP_DIRTY`: worktree/index가 clean하지 않음
- `STOP_NON_ATOMIC_OR_DIVERGED`: direct-parent 계약 불일치 또는 divergence

`FAST_FORWARD_SAFE`가 아니면 임의 `reset`, `rebase`, force push로 맞추지 않습니다.

## Safety / Trust Model

- Qwen에게 최종 PASS 권한이 없습니다.
- Qwen에게 일반 shell 또는 Git 권한을 주지 않습니다.
- Worker write는 Task Allowed/Forbidden ChangeScope를 통과해야 합니다.
- Forbidden이 Allowed보다 우선하고 기본값은 deny입니다.
- Repository root 탈출과 절대 경로는 거부합니다.
- 한 Worker step의 다중/잘못된/알 수 없는 ToolRequest는 fail closed됩니다.
- Retry는 유한하며 write 이후 위험한 재시도는 `BLOCKED`로 멈춥니다.
- `qh close`의 deterministic FAIL은 LLM이 뒤집을 수 없습니다.
- Worker는 다음 Task를 자동 선택하거나 시작하지 않습니다. 이는 `FR-004`의 핵심 경계입니다.
- Architecture, Requirements, Trust Boundary, Globalization 변경은 Human Gate 대상입니다.

## 문서 안내

| 문서 | 용도 |
|---|---|
| [PROJECT.md](PROJECT.md) | 프로젝트 목적과 큰 경계 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | 기능/검증 요구사항 |
| [DECISIONS.md](DECISIONS.md) | Accepted ADR와 주요 결정 |
| [STATUS.md](STATUS.md) | 현재 lifecycle과 baseline |
| [BACKLOG.md](BACKLOG.md) | 후보 Task와 Human-selected 순서 |
| [Quick Start](docs/QUICKSTART.md) | 처음 실행하는 방법 |
| [Codex 없이 계속하기](docs/MANUAL_OPERATOR_GUIDE.md) | Human이 직접 CMD/Git를 실행하는 절차 |
| [How It Works](docs/HOW_IT_WORKS.md) | 내부 구조와 신뢰 모델 |
| [Development Guide](docs/DEVELOPMENT.md) | Harness 개발 규칙과 성능 Evidence |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | 실패 사례와 복구 원칙 |
| [Project Timeline](docs/PROJECT_TIMELINE.md) | 프로젝트 진행 역사 |
| [Development Log](docs/DEVELOPMENT_LOG.md) | 개발 기록 |
| [Research Log](docs/RESEARCH_LOG.md) | Worker/실험 연구 기록 |

## 앞으로의 방향

현재 바로 다음 구현 Task는 정해져 있지 않습니다.

PERF-007의 300초 practical runtime trigger가 초과되었으므로 다음 단계는
**Human + ChatGPT Verification Strategy / Regression Tiering Architecture Review**입니다.

핵심 질문은 다음과 같습니다.

- routine Task close에서 어느 regression을 authoritative하게 요구할 것인가?
- repository-wide integration regression은 어떤 gate에서 수행할 것인가?
- 두 계층 모두 fresh exact HEAD Evidence를 어떻게 유지할 것인가?
- test 삭제/skip/cached PASS 없이 실사용 가능한 runtime을 만들 수 있는가?

이 결정이 Repository의 Accepted Architecture와 새 Task 계약으로 반영되기 전에는
`QH-V2-OPS-004`를 시작하지 않습니다.

LangGraph, Subtask Queue, expanded shell authority, model routing, multi-agent,
larger autonomous tasks는 현재 자동으로 허가된 기능이 아닙니다.

`GLOBALIZATION = NOT AUTHORIZED`
