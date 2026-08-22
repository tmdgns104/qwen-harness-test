# Qwen Harness Quick Start

이 문서는 Windows PowerShell에서 처음 Qwen Harness를 실행하는 사용자를 위한
따라 하기 안내서입니다. 명령만 복사하기보다 각 단계의 의미와 성공 조건을
함께 확인하세요.

> `NORMAL` 또는 Qwen이 출력한 `PASS`는 Task 완료가 아닙니다.
> 완료 근거는 Git 변경 범위, Verification 결과, Diff Check와 Final Gate입니다.

## Python을 어느 정도 알아야 하나요?

- 기본 사용에는 Python 코드를 직접 작성할 필요가 없습니다.
- Python 변수와 함수 문법을 본 정도면 출력과 오류를 따라가기 수월하지만,
  Harness 내부 구현을 이해하지 않아도 기본 흐름을 사용할 수 있습니다.
- Git commit은 이 문서의 명령을 순서대로 따라 하면 됩니다. 다만 commit 전에
  `git diff`와 stage된 파일을 직접 확인하세요.
- 처음에는 `python tools\qh.py task-new QH-LOCAL-001`로 학습용 Task 초안을 만든 뒤
  Human이 내용을 채우고 검토하여 승인하는 흐름을 권장합니다.

## 시작 전에 알아둘 점

- `task-new`는 Task 초안만 만들며 자동 승인, start, commit, close, push를 하지 않습니다.
- 생성된 초안의 상태는 `DRAFT - HUMAN REVIEW REQUIRED`이며 그대로는 시작할 수 없습니다.
- 공개 Repository의 현재 Task가 `COMPLETE - VERIFIED`라면 바로 실행할 ACTIVE
  Task가 없는 것이 정상입니다.
- 아래 `QH-LOCAL-001`은 사용자가 직접 만들 예시 ID입니다. 이미 같은 ID가
  있다면 다른 고유 ID를 사용하세요.
- 같은 ACTIVE Task에 `qh start`를 반복 실행하지 마세요. 이를 자동으로 막는
  lifecycle guard는 아직 Planned 상태입니다.
- 모든 명령은 Repository 최상위 폴더에서 실행합니다.

## 1. Repository 복제

```powershell
git clone https://github.com/tmdgns104/qwen-harness-test.git
cd qwen-harness-test
```

무엇을 하나요?

GitHub의 전체 Git 이력과 파일을 로컬 폴더로 내려받고 작업 위치를 이동합니다.

예상 결과:

- `qwen-harness-test` 폴더가 생깁니다.
- `git status --short`가 아무 경로도 출력하지 않습니다.

실패하면 확인할 것:

- Git이 설치되어 있는지 `git --version`으로 확인합니다.
- 이미 같은 이름의 폴더가 있다면 그 폴더가 이 Repository인지 먼저 확인합니다.
- 네트워크 또는 GitHub 인증 오류 메시지를 그대로 읽고, credential을 파일에
  저장하지 마세요.

## 2. Python, Git, Ollama 확인

```powershell
python --version
git --version
ollama --version
```

무엇을 하나요?

Harness와 로컬 모델을 실행할 필수 프로그램을 확인합니다. 현재 소스 문법상
Python 3.12 이상이 필요하며, 공개 준비 검증은 Python 3.13.5에서 수행했습니다.
Git과 Ollama의 최소 버전은 Repository에서 고정하지 않습니다.

예상 결과:

- 세 명령이 각각 설치된 버전을 출력합니다.
- 이 프로젝트의 Python 코드는 별도 third-party package 설치 없이 표준
  라이브러리만 사용합니다.

실패하면 확인할 것:

- `python` 명령이 없다면 Python 설치와 PATH 설정을 확인합니다.
- `ollama` 명령이 없다면 Ollama 설치를 먼저 완료합니다.
- Linux/macOS 전체 E2E는 현재 Repository에서 검증되었다고 문서화되어 있지
  않습니다. 처음에는 검증된 Windows 흐름을 권장합니다.

## 3. Qwen 모델 준비

```powershell
ollama pull qwen3:8b
ollama list
```

무엇을 하나요?

Harness의 기본 모델인 `qwen3:8b`를 Ollama 로컬 저장소에 준비하고 목록에서
확인합니다. Harness는 기본적으로 `http://127.0.0.1:11434`의 Ollama API를
사용합니다.

예상 결과:

- pull이 정상 종료됩니다.
- `ollama list` 출력에 `qwen3:8b`가 보입니다.

실패하면 확인할 것:

- Ollama 애플리케이션 또는 서비스가 실행 중인지 확인합니다.
- 모델 이름이 정확히 `qwen3:8b`인지 확인합니다.
- 저장 공간과 네트워크 상태를 확인합니다.
- Harness가 Ollama를 설치하거나 모델을 대신 다운로드하지는 않습니다.

## 4. 현재 상태 확인

```powershell
git status --short
python tools\qh.py status
python tools\qh.py preflight
```

무엇을 하나요?

첫 명령은 실제 Git working tree를, 나머지 두 명령은 현재 Task와 scope를
보여 줍니다.

예상 결과:

- 새 clone이라면 `git status --short`가 비어 있습니다.
- `qh.py status`는 Current Task와 변경 경로를 출력합니다.
- `qh.py preflight`는 Repository root, Task 파일과 scope를 검사합니다.

실패하거나 dirty라고 나오면 확인할 것:

- `status`와 `preflight`는 exit code 0이어도 dirty 상태를 보고할 수 있습니다.
  반드시 출력 내용을 확인하세요.
- 알지 못하는 변경이 있으면 새 Task를 시작하지 말고 `git diff`로 원인을
  확인하세요.
- Current Task가 `ACTIVE`라면 새 Task를 시작하지 마세요.

## Task 초안 만들기와 Human 승인 경계

새 Task를 처음부터 빈 파일로 작성하는 대신 다음 명령으로 필수 섹션이 들어간
초안을 만들 수 있습니다.

```powershell
python tools\qh.py task-new QH-LOCAL-001
```

생성되는 `tasks/QH-LOCAL-001.md`는 정확히 `DRAFT - HUMAN REVIEW REQUIRED`
상태입니다. `task-new`는 구조만 만들 뿐 Goal, Architecture Basis, Allowed/Forbidden
Changes, Acceptance Criteria, Verification을 대신 결정하거나 승인하지 않습니다.
또한 STATUS를 수정하거나 `start`, commit, close, push를 실행하지 않습니다.

Human은 생성된 초안의 placeholder를 실제 Task 계약 내용으로 교체하고 범위와
Verification을 직접 검토해야 합니다. 검토가 끝난 뒤에만 Status를
`APPROVED - READY FOR CONTRACT BASELINE`으로 명시적으로 바꾸고 Task 계약을
baseline commit으로 보존합니다. untouched DRAFT를 `qh start`에 넘기면 거부되는
것이 정상입니다. 즉 `task-new`와 `start`는 서로 다른 단계이며 Human 승인 없이
자동으로 연결되지 않습니다.

## 5. 작은 Task 계약 만들기

아래 예시는 Repository root의 `example.txt`에 한 줄을 쓰는 학습용 Task입니다.
먼저 Human이 내용과 범위를 읽고 승인해야 합니다.

`tasks/QH-LOCAL-001.md` 파일을 만들거나 위 `task-new`로 만든 초안을 검토한 뒤
다음 계약 내용으로 완성합니다.

```markdown
# QH-LOCAL-001 - Write a Harness greeting

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Create `example.txt` containing exactly `hello from Qwen Harness` followed by
one newline.

## Scope

Use the current Worker path to make one small, observable Repository edit.

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

## Stop Conditions

STOP if any forbidden path or Architecture change is required.
```

무엇을 하나요?

Task 계약이 Goal, 허용/금지 경로, 완료 조건과 실행할 Verification을 미리
고정합니다. `qh start`는 이 계약을 생성하거나 Human 대신 승인하지 않습니다.

예상 결과:

- 새 Task 파일 하나만 untracked 상태로 보입니다.
- Verification marker 하나마다 독립 명령 하나만 연결되어 있습니다.

실패하면 확인할 것:

- 섹션 이름을 `## Allowed Changes`, `## Forbidden Changes`,
  `## Verification`으로 정확히 썼는지 확인합니다.
- scope는 정확한 경로 또는 trailing `/**`만 지원합니다. `*.py` 같은 일반
  glob은 지원하지 않습니다.
- 목록에 없는 경로는 default deny이므로 “all other files” 같은 가상 pattern을
  쓸 필요가 없습니다.
- 실제 프로젝트 작업에서는 예시를 그대로 쓰지 말고 승인된 목표와 경로로
  계약을 작성하세요.

## 6. Task 계약을 baseline으로 커밋

```powershell
git add tasks/QH-LOCAL-001.md
git diff --cached
git commit -m "define QH-LOCAL-001"
git status --short
```

무엇을 하나요?

`qh start`가 기록할 baseline보다 먼저 Task 계약을 Git Evidence로 보존합니다.

예상 결과:

- staged diff에는 Task 계약만 있습니다.
- commit이 생성되고 마지막 status 출력이 비어 있습니다.

실패하면 확인할 것:

- Git 사용자 이름/이메일 설정이 필요한지 오류 메시지를 확인합니다.
- 다른 파일이 stage되었다면 commit 전에 범위를 바로잡습니다.
- working tree가 clean이 아니면 다음 단계로 넘어가지 않습니다.

## 7. Task 시작과 start 전환 커밋

```powershell
python tools\qh.py start QH-LOCAL-001
python tools\qh.py status
git diff -- STATUS.md
git add STATUS.md
git commit -m "start QH-LOCAL-001"
git status --short
```

무엇을 하나요?

`start`는 이미 존재하는 Task를 Current Task로 지정하고 현재 HEAD를
`Task Baseline`으로 `STATUS.md`에 기록합니다. Task 파일을 만들거나 commit하지
않으며, 현재 구현은 clean tree를 강제하지 않습니다.

예상 결과:

- Current Task가 `QH-LOCAL-001 - ACTIVE`로 보입니다.
- 변경된 `STATUS.md`만 별도 commit됩니다.
- 마지막 status 출력이 비어 있습니다.

실패하면 확인할 것:

- `tasks/QH-LOCAL-001.md`가 존재하는지 확인합니다.
- 다른 ACTIVE Task가 있으면 중단합니다.
- 같은 ACTIVE Task에 `start`를 다시 실행하지 않습니다.

## 8. Preflight와 Worker 실행

Ollama가 실행 중인지 확인한 뒤 다음을 실행합니다.

```powershell
python tools\qh.py preflight
python tools\qh.py run QH-LOCAL-001
```

무엇을 하나요?

`run`은 최대 2번의 Runner attempt와 attempt당 최대 8 Worker step 안에서
Qwen과 Tool Call을 주고받습니다. Worker에게 제공되는 Repository 도구는
`read_repo_text`와 scope 검사를 거치는 `write_repo_text`입니다.

예상 결과:

- `NORMAL`: Worker 상호작용이 정상 종료되었습니다. Task PASS 의미는 아닙니다.
- `FAIL`: 안전 규칙, 유효성 검사 또는 step budget 등 결정론적 실패입니다.
- `BLOCKED`: 안전한 retry를 소진했거나 쓰기 시도 뒤 transient 문제가
  발생했습니다.

실패하면 확인할 것:

- Ollama API와 `qwen3:8b` 모델이 준비되었는지 확인합니다.
- `FAIL` 또는 `BLOCKED`면 반복 실행부터 하지 말고 출력, `git status --short`,
  `git diff`를 확인합니다.
- Worker가 쓴 뒤에는 자동 retry가 제한됩니다. 이미 생긴 변경을 먼저
  검토하세요.

## 9. 변경 검토와 선택적 진단

```powershell
git status --short
git diff
```

무엇을 하나요?

working tree에 생긴 실제 변경을 먼저 Human이 검토합니다. 정상 final path에서는
구현을 commit한 뒤 `qh close`가 full Verification, scope, Evidence, Diff Check와
Final Gate를 한 번 실행합니다.

예상 결과:

- 현재 working-tree 변경은 `example.txt`뿐입니다.
- 내용은 Task가 요구한 정확한 한 줄입니다.

실패하면 확인할 것:

- Qwen의 설명이 아니라 실제 파일과 exit code를 확인합니다.
- 예상 밖 working-tree path가 있으면 commit하거나 close하지 않습니다.

문제 진단이 필요하면 다음 명령을 선택적으로 사용할 수 있습니다.

```powershell
python tools\qh.py verify
python tools\qh.py review
```

- `verify`는 현재 Task의 Verification command만 실행합니다.
- `review`는 persisted Task Baseline 기준 changed paths, scope, Verification,
  Evidence, Final Gate와 별도 Diff Check를 평가합니다.
- 이 예시에서 review의 Task-range changed paths는 `STATUS.md`와
  `example.txt`입니다. Task 계약 commit 뒤의 start 전환 commit도 포함됩니다.
- `review`의 선택 인자는 Task ID가 아니라 baseline commit입니다. 보통은
  저장된 baseline을 쓰기 위해 인자 없이 실행합니다.
- 두 명령은 진단용입니다. 이후 `qh close`가 authoritative full Verification을
  다시 실행하므로 정상 경로의 필수 단계로 반복하지 않습니다.
- 진단 Verification이 실패하면 테스트를 지우거나 약화하지 말고 현재 Task
  범위 안에서 원인을 해결합니다.

## 10. 구현 커밋

```powershell
git add example.txt
git diff --cached
git commit -m "implement QH-LOCAL-001"
git status --short
```

무엇을 하나요?

검증된 구현 변경만 Git에 보존합니다. lifecycle 파일은 이 commit에 섞지
않습니다.

예상 결과:

- staged diff에는 `example.txt`만 있습니다.
- commit 후 working tree가 clean입니다.

실패하면 확인할 것:

- stage된 경로가 Task Allowed Changes 안에만 있는지 확인합니다.
- clean하지 않으면 `qh close`를 실행하지 않습니다.

## 11. 정확한 구현 HEAD로 close

```powershell
$implementationHead = git rev-parse HEAD
python tools\qh.py close $implementationHead
```

무엇을 하나요?

review를 다시 수행한 뒤 인자로 받은 commit이 실제 현재 HEAD인지 확인하고,
두 검사가 모두 성공할 때만 Task와 STATUS lifecycle을
`COMPLETE - VERIFIED`로 바꿉니다.

예상 결과:

- Task Verification 명령이 모두 실행됩니다.
- `Unexpected Changed Paths: no`와 `Diff Check: exit 0`가 보입니다.
- `Final Gate: PASS`가 보입니다.
- `STATUS.md`와 현재 Task 파일만 수정됩니다.

실패하면 확인할 것:

- 임의의 과거 SHA가 아니라 `git rev-parse HEAD`의 값을 사용했는지 확인합니다.
- working tree가 clean이었는지 확인합니다.
- Final Gate가 PASS가 아니면 COMPLETE라고 판단하지 않습니다.

## 12. lifecycle 커밋과 최종 확인

```powershell
git diff -- STATUS.md tasks/QH-LOCAL-001.md
git diff --check
git add STATUS.md tasks/QH-LOCAL-001.md
git diff --cached
git commit -m "mark QH-LOCAL-001 complete"
git status --short
python tools\qh.py status
```

무엇을 하나요?

`close`가 만든 완료 기록을 구현과 분리된 Git commit으로 보존합니다.

예상 결과:

- lifecycle diff에 Current Task의 `COMPLETE - VERIFIED` 상태가 기록됩니다.
- 마지막 `git status --short`가 비어 있습니다.
- 다음 Task가 자동으로 시작되지 않습니다.

실패하면 확인할 것:

- 두 lifecycle 파일 외의 변경이 있으면 commit 전에 원인을 확인합니다.
- `close` 자체는 자동 commit 기능이 없습니다.

## 자주 만나는 문제

| 증상 | 확인할 내용 |
|---|---|
| `Task file not found` | `tasks/<TASK-ID>.md` 파일명과 ID가 정확히 같은지 확인 |
| preflight가 dirty를 표시 | exit code만 보지 말고 `git status --short`와 출력 경로 확인 |
| Ollama 연결 실패 | Ollama 실행 여부, `127.0.0.1:11434`, `ollama list` 확인 |
| Worker 결과가 `NORMAL` | 정상 대화 종료일 뿐이므로 Git diff와 review 계속 수행 |
| `Unexpected Changed Paths` | Task scope 밖 변경을 commit하지 말고 원인 조사 |
| Verification parser 오류 | marker, inline command/fence, 한 marker당 한 명령 규칙 확인 |
| `Final Gate: FAIL` | 실패 Evidence를 해결하기 전 close/완료 선언 금지 |

다음으로 [How It Works](HOW_IT_WORKS.md)에서 내부 역할을 읽거나
[Development Guide](DEVELOPMENT.md)에서 Repository 개발 규칙을 확인하세요.