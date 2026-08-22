# Qwen Harness Quick Start

이 문서는 Windows에서 처음 Qwen Harness를 설치하고, 환경을 진단하고,
작은 Task 하나를 실제로 실행하는 현재 기준 절차입니다.

> `NORMAL` 또는 Qwen이 출력한 `PASS`는 Task 완료가 아닙니다.
> 완료 근거는 Git changed paths, Verification exit code, Diff Check와 Final Gate입니다.

## 현재 기준

2026-08-23 기준 공개 `main`은 `QH-V2-OPS-002 - COMPLETE - VERIFIED` 상태입니다.
`qh task-new`와 `qh doctor`가 구현되어 있고, 다음 Task는 자동으로 선택되지 않습니다.
최신 상태는 항상 Repository의 `STATUS.md`를 우선하세요.

## 시작 전에 필요한 것

- Windows
- Python 3.12 이상
- Git
- Ollama
- 기본 모델 `qwen3:8b`

이 프로젝트의 Python 실행 코드는 현재 별도 third-party Python package 설치 없이
표준 라이브러리만 사용합니다.

실제로 검증된 한 환경은 Windows + RTX 5070 Laptop GPU 8 GB VRAM + RAM 32 GB +
Ollama + `qwen3:8b`입니다. 이것은 최소 사양이 아닙니다.

## 1. Repository 복제

```powershell
git clone https://github.com/tmdgns104/qwen-harness-test.git
cd qwen-harness-test
```

확인:

```powershell
git branch --show-current
git status --short
```

새 clone이라면 보통 branch는 `main`이고 `git status --short`는 아무것도 출력하지 않습니다.

## 2. Python, Git, Ollama 확인

```powershell
python --version
git --version
ollama --version
```

현재 소스는 Python 3.12 이상 문법을 사용하며 주요 검증은 Python 3.13.5에서 수행되었습니다.
Git과 Ollama의 최소 버전은 Repository가 별도로 고정하지 않습니다.

## 3. Qwen 모델 준비

```powershell
ollama pull qwen3:8b
ollama list
```

`ollama list`에 `qwen3:8b`가 보이는지 확인합니다.
Harness는 Ollama를 자동 설치하거나 모델을 대신 pull하지 않습니다.

## 4. 가장 먼저 `qh doctor` 실행

```powershell
python tools\qh.py doctor
```

`doctor`는 읽기 전용으로 다음을 확인합니다.

- Python runtime
- Git 사용 가능 여부
- 현재 위치가 Repository root인지
- `PROJECT.md`, `REQUIREMENTS.md`, `DECISIONS.md`, `STATUS.md`
- STATUS lifecycle 형태
- Current Task 파일
- ChangeScope
- Verification Contract
- working tree
- Git remote
- Ollama `/api/tags`
- 기본 모델 `qwen3:8b`

마지막 결과:

```text
OVERALL: PASS ...
```

또는:

```text
OVERALL: WARN ...
OVERALL: FAIL ...
```

입니다.

Dirty worktree나 optional Git remote 부재는 WARN일 수 있습니다. 필수 Repository 계약이나
Ollama/model readiness 실패는 FAIL입니다. 에러 메시지는 credential-bearing backend 오류를
그대로 노출하지 않도록 제한되어 있습니다.

## 5. 현재 상태 확인

```powershell
python tools\qh.py status
python tools\qh.py preflight
```

현재 `status`는 Current Task, Task file, 현재 HEAD 기준 worktree 변경 경로와
Allowed/Forbidden scope를 보여 줍니다.

`preflight`는 Repository root, Current Task file, ChangeScope를 확인하고 Git State를 표시합니다.

주의:

- `status`와 `preflight`는 dirty 상태를 출력으로 보고할 수 있으므로 exit code만 보지 마세요.
- `qh doctor`가 PASS라고 해서 실제 Worker E2E나 Task 완료가 증명된 것은 아닙니다.

## 6. Task 초안 만들기

```powershell
python tools\qh.py task-new QH-LOCAL-001
```

새 파일:

```text
tasks/QH-LOCAL-001.md
```

상태:

```text
DRAFT - HUMAN REVIEW REQUIRED
```

`task-new`는 필수 섹션이 있는 초안만 만듭니다.
다음 작업은 하지 않습니다.

- Task 승인
- STATUS 변경
- `qh start`
- Git commit
- `qh close`
- push

## 7. Human이 Task 계약 완성

아래 예시는 Repository root의 `example.txt`에 한 줄을 쓰는 학습용 Task입니다.
`tasks/QH-LOCAL-001.md`의 placeholder를 다음처럼 교체합니다.

```markdown
# QH-LOCAL-001 - Write a Harness greeting

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

A tiny Repository edit is needed to learn the guarded Worker flow.

## Goal

Create `example.txt` containing exactly `hello from Qwen Harness` followed by one newline.

## Architecture Basis

Use the existing single-Task Worker, scoped Repository write, and deterministic Final Gate.

## Dependencies

Current Repository lifecycle must be COMPLETE - VERIFIED and the working tree must be clean.

## Scope

Use the current Worker path to make one small observable Repository edit.

## Allowed Changes

- `example.txt`
- `STATUS.md`
- `tasks/QH-LOCAL-001.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `docs/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `.git/**`

## Acceptance Criteria

1. `example.txt` exists.
2. Its UTF-8 content is exactly the required line plus one newline.
3. No unexpected path changes.

## Verification

Run exactly:

`python -c "from pathlib import Path; assert Path('example.txt').read_text(encoding='utf-8') == 'hello from Qwen Harness\n'"`

Then run:

`git diff --check`

## Evidence Requirements

- The implementation commit contains only the intended implementation change.
- Final Gate reports no unexpected changed paths.

## Stop Conditions

STOP if any forbidden path or Architecture change is required.

## Next Task

No automatic successor.
```

중요:

- `## Status` 값이 정확히 `APPROVED - READY FOR CONTRACT BASELINE`이어야 `qh start`가 허용됩니다.
- `Allowed Changes`에 없는 쓰기는 default deny입니다.
- Forbidden이 Allowed보다 우선합니다.
- scope pattern은 exact path 또는 trailing `/**` recursive path를 사용합니다.
- 일반 `*.py` glob은 지원하지 않습니다.
- Verification marker 하나에는 정확히 한 command만 연결합니다.

## 8. Task 계약을 baseline commit으로 보존

```powershell
git add tasks/QH-LOCAL-001.md
git diff --cached
git commit -m "define QH-LOCAL-001"
git status --short
```

마지막 `git status --short`가 비어 있어야 합니다.

현재 `qh start`는 `capture_git_baseline()`을 사용하므로 dirty working tree에서는 시작하지 않습니다.

## 9. Task 시작

```powershell
python tools\qh.py start QH-LOCAL-001
```

현재 `qh start`는 다음을 fail closed로 검사합니다.

- 현재 `Current Task`가 정확히 `COMPLETE - VERIFIED`인지
- target Task가 정확히 `APPROVED - READY FOR CONTRACT BASELINE`인지
- Repository가 clean인지
- target Task file이 실제 존재하는지

성공하면 `STATUS.md`에:

```text
Current Task: QH-LOCAL-001 - ACTIVE
Task Baseline: <현재 HEAD>
```

형태의 lifecycle 전환이 기록됩니다.

그 변경을 별도 commit으로 보존합니다.

```powershell
git diff -- STATUS.md
git add STATUS.md
git commit -m "start QH-LOCAL-001"
git status --short
```

같은 ACTIVE Task에 `qh start`를 다시 실행하면 현재 lifecycle guard가 거부하는 것이 정상입니다.

## 10. Worker 실행

Ollama가 실행 중인지 확인한 뒤:

```powershell
python tools\qh.py preflight
python tools\qh.py run QH-LOCAL-001
```

현재 Worker 경로:

```text
Task
 ↓
Bounded Retry (최대 2 attempts)
 ↓
Single-Task Runner (attempt당 최대 8 steps)
 ↓
OllamaToolSession
 ↓
Ollama + qwen3:8b
 ↓
Harness-owned read/write tools
```

Worker에게 제공되는 Repository tool은:

- `read_repo_text`
- `write_repo_text`

두 개입니다.

`write_repo_text`는 Task ChangeScope를 통과해야 합니다.
Qwen에게 일반 shell 또는 Git 권한은 없습니다.

실행 결과:

| Outcome | 의미 |
|---|---|
| `NORMAL` | Worker interaction 정상 종료. Task PASS 아님 |
| `FAIL` | 구조/권한/step budget 등 결정론적 실패 |
| `BLOCKED` | 안전한 retry가 불가능하거나 write 이후 위험 때문에 중단 |

`FAIL` 또는 `BLOCKED`면 무작정 다시 실행하지 말고 먼저 Git 상태와 diff를 확인합니다.

## 11. 실제 변경 검토

```powershell
git status --short
git diff
```

Qwen의 설명보다 실제 Repository 상태를 우선합니다.

학습용 예제라면 `example.txt`만 구현 변경으로 보여야 합니다.
예상 밖 경로가 있으면 commit하지 말고 원인을 조사합니다.

문제 진단이 필요할 때만 선택적으로:

```powershell
python tools\qh.py verify
python tools\qh.py review
```

을 실행할 수 있습니다.

- `verify`: 현재 Task의 Verification만 실행
- `review`: persisted baseline 기준 changed paths, scope, Verification, Diff Check, Final Gate 진단

정상 final path에서는 이 두 명령을 매번 선행 실행할 필요가 없습니다.
`qh close`가 authoritative full Verification을 다시 실행하기 때문입니다.

## 12. 구현 commit

```powershell
git add example.txt
git diff --cached
git commit -m "implement QH-LOCAL-001"
git status --short
```

구현 commit에는 구현 파일만 넣고 lifecycle completion 파일은 섞지 않습니다.
마지막 working tree는 clean이어야 합니다.

## 13. 정확한 implementation HEAD로 close

PowerShell:

```powershell
$implementationHead = git rev-parse HEAD
python tools\qh.py close $implementationHead
```

CMD에서는:

```cmd
for /f %i in ('git rev-parse HEAD') do python tools\qh.py close %i
```

또는 SHA를 직접 복사해서:

```cmd
python tools\qh.py close <IMPLEMENTATION-COMMIT>
```

실행할 수 있습니다.

`qh close`는 단순 상태 변경이 아닙니다.

1. exact implementation commit이 현재 HEAD인지 확인
2. Task Verification 전체 실행
3. baseline 이후 changed paths 수집
4. Allowed/Forbidden scope 검사
5. `git diff --check`
6. deterministic Final Gate
7. 성공한 경우에만 Task/STATUS를 `COMPLETE - VERIFIED`로 변경

정상 핵심 출력:

```text
Unexpected Changed Paths: no
Diff Check: exit 0
Final Gate: PASS
Closed Task: QH-LOCAL-001
```

### close가 오래 걸려도 이상하지 않을 수 있습니다

Task Verification에 실제 Git fixture나 integration test가 많이 포함되면 수분이 걸릴 수 있습니다.
현재 `qh close`는 child Verification이 실행되는 동안 한동안 출력이 없을 수 있습니다.

중간 RED/GREEN 또는 구현 단계에서는 focused test를 사용하고, 전체 Verification은 정상적으로
close에서 한 번 실행하는 것이 현재 운영 원칙입니다.

## 14. lifecycle completion commit

`close` 성공 뒤에는 보통 `STATUS.md`와 현재 Task 파일이 수정됩니다.

```powershell
git diff -- STATUS.md tasks/QH-LOCAL-001.md
git diff --check
git add STATUS.md tasks/QH-LOCAL-001.md
git diff --cached
git commit -m "mark QH-LOCAL-001 complete"
git status --short
```

마지막 `git status --short`가 비어 있어야 합니다.
다음 Task는 자동으로 시작되지 않습니다.

## 15. Push

새 clone이 `main`을 추적한다면:

```powershell
git push origin main
```

오래된 local clone이 `master`이고 GitHub 기본 branch가 `main`이라면 먼저 확인합니다.

```powershell
git branch --show-current
git remote -v
```

해당 local branch를 그대로 GitHub main에 push해야 하는 상황에서는:

```powershell
git push origin master:main
```

처럼 명시적인 refspec이 필요할 수 있습니다.
브랜치 이름 변경은 별도 운영 판단으로 처리하고, 진행 중 Task가 있을 때 임의 변경하지 마세요.

## 전체 흐름 요약

```text
task-new
   ↓
Human 계약 작성 / 승인
   ↓
Task contract commit
   ↓
clean working tree
   ↓
qh start
   ↓
start lifecycle commit
   ↓
qh run
   ↓
Human diff review
   ↓
implementation commit
   ↓
qh close exact-HEAD
   ↓
Final Gate PASS
   ↓
lifecycle completion commit
   ↓
optional push
```

## 자주 만나는 문제

| 증상 | 확인할 내용 |
|---|---|
| `doctor`가 `OLLAMA_ENDPOINT: FAIL` | Ollama 실행 여부와 `127.0.0.1:11434` 확인 |
| `doctor`가 `OLLAMA_MODEL: FAIL` | `ollama list`, `ollama pull qwen3:8b` 확인 |
| `Repository is not clean` | `git status --short`, `git diff`로 변경 원인 확인 |
| `Current Task must be exactly COMPLETE - VERIFIED before start` | 다른 ACTIVE/비정상 lifecycle이 있는지 STATUS 확인 |
| `Target Task Status must be exactly APPROVED...` | Task 초안이 Human 승인 상태로 바뀌었는지 확인 |
| `Task file not found` | `tasks/<TASK-ID>.md` 파일명 확인 |
| Worker 결과가 `NORMAL` | 대화 정상 종료일 뿐. 구현 diff/commit/close 계속 수행 |
| `FAIL` / `BLOCKED` | 자동 반복 전에 Git diff와 Error Evidence 확인 |
| `Unexpected Changed Paths: yes` | scope 밖 경로 변경 원인 조사. 완료 선언 금지 |
| `Final Gate: FAIL` | 실패 Evidence 해결 전 close 성공으로 간주 금지 |
| `git push origin main`이 `src refspec main` 오류 | local branch가 `master`인지 `git branch --show-current` 확인 |
| cherry-pick이 empty | 동일 patch가 이미 local history에 들어갔는지 `git log` 확인. 무조건 반복 적용하지 않음 |

## 무엇을 아직 자동화하지 않나요?

현재 기본 사용자 흐름은 다음을 자동으로 하지 않습니다.

- Architecture 변경
- Human approval
- 다음 Task 자동 선택/시작
- implementation commit
- lifecycle commit
- 일반 Git push
- unrestricted shell 실행
- Qwen self-report를 Final PASS로 인정

## 다음 개발 계획

현재 계획된 운영 마무리 순서:

```text
QH-V2-OPS-003  Windows Workflow Simplification
QH-V2-OPS-004  Worker Smoke / E2E Standardization
QH-V2-OPS-005  qh status UX
QH-V2-OPS-006  STATUS / Handoff Historical Cleanup
QH-V2-M2-SPEC-001  Milestone 2 Specification & Architecture Review
HUMAN ARCHITECTURE GATE
```

Milestone 2 후보 기능은 아직 구현 승인 상태가 아닙니다.

## 더 읽기

- [README](../README.md)
- [How It Works](HOW_IT_WORKS.md)
- [Development Guide](DEVELOPMENT.md)
- [STATUS](../STATUS.md)
- [BACKLOG](../BACKLOG.md)
