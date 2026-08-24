# Qwen Harness 빠른 시작 가이드

이 문서는 Windows에서 Qwen Harness를 처음 설치하고, 환경을 확인하고, 작은 Task
하나를 안전하게 수행하는 현재 기준 절차입니다.

> `NORMAL` 또는 Qwen이 출력한 `PASS`는 Task 완료가 아닙니다.
> 완료 근거는 Git changed paths, Verification exit code, Diff Check와 Final Gate입니다.

## 현재 기준

최신 lifecycle과 Current Task는 항상 [STATUS.md](../STATUS.md)를 우선합니다.
이 문서는 `QH-V2-DOC-KO-001`에서 최신 사용자 흐름에 맞게 갱신했습니다.

현재 주요 운영 기능에는 다음이 포함됩니다.

- `qh task-new`
- `qh doctor`
- `qh start / run / close`
- `qh handoff-check`
- exact baseline 기반 atomic remote handoff

최근 안전한 handoff 경로는 `QH-V2-OPS-GIT-001`에서 추가되었습니다. 현재 선택된
가까운 순서는 다음과 같습니다.

```text
QH-V2-DOC-KO-001
  -> QH-V2-ARCH-018
  -> QH-V2-WORKER-ROB-003
  -> QH-V2-OPS-003
```

이 순서는 Worker의 자동 queue가 아닙니다. Worker는 현재 Task만 실행합니다.

`GLOBALIZATION = NOT AUTHORIZED`

## 시작 전에 필요한 것

- Windows
- Python 3.12 이상
- Git
- Ollama
- 기본 모델 `qwen3:8b`

실제로 검증된 한 환경은 Windows + RTX 5070 Laptop GPU 8 GB VRAM + RAM 32 GB +
Ollama + `qwen3:8b`입니다. 이것은 공식 최소 사양이 아닙니다.

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

현재 소스는 Python 3.12 이상 문법을 사용합니다.

## 3. Qwen 모델 준비

```powershell
ollama pull qwen3:8b
ollama list
```

`ollama list`에 `qwen3:8b`가 보이는지 확인합니다. Harness는 Ollama 설치나 model pull을
자동으로 대신하지 않습니다.

## 4. 가장 먼저 `qh doctor` 실행

```powershell
python tools\qh.py doctor
```

`doctor`는 읽기 전용으로 다음을 확인합니다.

- Python runtime
- Git 사용 가능 여부
- Repository root
- Source-of-Truth 파일
- STATUS lifecycle
- Current Task / ChangeScope / Verification Contract
- working tree
- Git remote
- Ollama endpoint
- 기본 모델 `qwen3:8b`

마지막 결과는 `OVERALL: PASS`, `OVERALL: WARN`, `OVERALL: FAIL` 중 하나입니다.

## 5. 현재 상태 확인

```powershell
python tools\qh.py status
python tools\qh.py preflight
```

`status`는 Current Task와 변경 경로/scope를 보여 줍니다. `preflight`는 Repository root,
Task file과 ChangeScope를 점검합니다. 두 명령의 exit code만 보고 Repository가 clean하거나
Task가 PASS라고 판단하지 않습니다.

## 6. Task 초안 만들기

```powershell
python tools\qh.py task-new QH-LOCAL-001
```

새 Task는 기본적으로:

```text
DRAFT - HUMAN REVIEW REQUIRED
```

상태입니다. `task-new`는 Task 파일 구조만 만들며 승인, start, commit, close, push를
자동으로 수행하지 않습니다.

## 7. Human이 Task 계약 완성

Task 계약에는 최소한 다음이 있어야 합니다.

- Goal
- Architecture Basis
- Allowed Changes
- Forbidden Changes
- Acceptance Criteria
- Verification
- Stop Conditions

실행 가능한 Task의 Status는 정확히:

```text
APPROVED - READY FOR CONTRACT BASELINE
```

이어야 합니다.

Worker write는 Allowed에 맞아야 하고 Forbidden이 우선합니다. Allowed에 없는 쓰기는
기본적으로 거부됩니다.

## 8. Task 계약을 baseline commit으로 보존

```powershell
git add tasks/QH-LOCAL-001.md
git diff --cached
git commit -m "define QH-LOCAL-001"
git status --short
```

마지막 `git status --short`가 비어 있어야 합니다.

## 9. Task 시작

```powershell
python tools\qh.py start QH-LOCAL-001
```

성공하면 `STATUS.md`에 Current Task와 Task Baseline이 기록됩니다. 이 lifecycle 변경은
구현 변경과 섞지 않고 별도 commit으로 보존합니다.

```powershell
git diff -- STATUS.md
git add STATUS.md
git commit -m "activate QH-LOCAL-001"
```

## 10. Worker 실행

```powershell
python tools\qh.py preflight
python tools\qh.py run QH-LOCAL-001
```

현재 Worker의 Repository tool은 다음 두 개입니다.

- `read_repo_text`
- `write_repo_text`

Qwen에게 일반 shell이나 Git 권한은 없습니다.

| Outcome | 의미 |
|---|---|
| `NORMAL` | Worker interaction 정상 종료. Task PASS 아님 |
| `FAIL` | 구조/권한/step budget 등 결정론적 실패 |
| `BLOCKED` | 안전한 retry가 불가능하거나 write 이후 위험 때문에 중단 |

`FAIL` 또는 `BLOCKED`면 무작정 반복 실행하지 말고 Git 상태와 Error Evidence를 먼저
확인합니다.

## 11. 실제 변경 검토

```powershell
git status --short
git diff
```

Qwen의 설명보다 실제 Repository 상태를 우선합니다. 예상 밖 경로가 있으면 commit하지
말고 원인을 조사합니다.

구현 중에는 필요한 focused test만 사용합니다. 문제 진단이 필요한 경우에만 선택적으로:

```powershell
python tools\qh.py verify
python tools\qh.py review
```

을 사용할 수 있습니다. 정상 final path에서는 `qh close`가 authoritative Verification을
다시 수행하므로 full Verification을 매 단계 반복하지 않습니다.

## 12. 구현 commit

실제 Task의 Allowed 구현 파일만 stage합니다.

```powershell
git add -- path\to\allowed-file
git diff --cached
git commit -m "implement QH-LOCAL-001"
git status --short
```

implementation commit에는 completion lifecycle 변경을 섞지 않습니다.

## 13. 정확한 implementation HEAD로 close

```powershell
$implementationHead = git rev-parse HEAD
python tools\qh.py close $implementationHead
```

CMD에서는 SHA를 직접 확인한 뒤 사용할 수 있습니다.

```cmd
git rev-parse HEAD
python tools\qh.py close <IMPLEMENTATION-COMMIT>
```

`qh close`는 다음을 수행합니다.

1. exact implementation commit이 current HEAD인지 확인
2. Task Verification 전체 실행
3. baseline 이후 changed paths 수집
4. Allowed/Forbidden scope 검사
5. `git diff --check`
6. deterministic Final Gate
7. 성공한 경우에만 lifecycle을 `COMPLETE - VERIFIED`로 변경

정상 핵심 출력:

```text
Unexpected Changed Paths: no
Diff Check: exit 0
Final Gate: PASS
Closed Task: QH-LOCAL-001
```

## 14. lifecycle completion commit

`qh close` 성공 뒤에는 보통 `STATUS.md`와 현재 Task 파일이 수정됩니다.

```powershell
git diff -- STATUS.md tasks/QH-LOCAL-001.md
git diff --check
git add STATUS.md tasks/QH-LOCAL-001.md
git commit -m "mark QH-LOCAL-001 complete"
git status --short
```

다음 Task는 Worker가 자동으로 시작하지 않습니다.

## 15. Push

현재 branch와 remote 상태를 확인한 뒤 정상 fast-forward push를 사용합니다.

```powershell
git branch --show-current
git remote -v
git push origin main
```

force push나 history rewrite가 필요한 상황은 routine flow로 처리하지 않습니다.

## 원격 작업 결과를 안전하게 가져오기

ChatGPT/GitHub 같은 원격 작업에서 만든 commit을 로컬로 가져올 때는
`QH-V2-OPS-GIT-001`에서 정의한 handoff 절차를 사용합니다.

### 정상 handoff 계약

```text
exact local HEAD baseline
  -> remote branch를 그 SHA에서 생성
  -> 정확히 하나의 atomic handoff commit
  -> git fetch
  -> qh handoff-check
  -> FAST_FORWARD_SAFE
  -> git merge --ff-only
```

실행 예:

```powershell
git fetch origin
python tools\qh.py handoff-check origin/work/QH-V2-EXAMPLE-handoff
git merge --ff-only origin/work/QH-V2-EXAMPLE-handoff
```

`qh handoff-check`는 read-only이며 fetch/merge/cherry-pick/reset/rebase/push/branch 삭제를
실행하지 않습니다.

분류:

| Classification | 의미 |
|---|---|
| `FAST_FORWARD_SAFE` | local HEAD가 handoff의 exact parent |
| `ALREADY_APPLIED_EXACT` | handoff commit이 현재 HEAD와 정확히 같음 |
| `ALREADY_CONTAINED` | handoff commit이 이미 current history에 포함됨 |
| `STOP_DIRTY` | worktree/index가 clean하지 않음 |
| `STOP_NON_ATOMIC_OR_DIVERGED` | 단일 direct-parent 계약 불일치 또는 divergence |

`FAST_FORWARD_SAFE`가 아니면 임의 `reset`, `rebase`, 반복 `cherry-pick --skip`으로
맞추지 않습니다. STOP 후 exact baseline에서 handoff를 다시 만들거나 Human-reviewed
integration을 선택합니다.

## 전체 흐름 요약

```text
Task contract
   ↓
Human approval
   ↓
contract commit
   ↓
qh start
   ↓
activation lifecycle commit
   ↓
implementation
   ↓
focused test / Git diff review
   ↓
implementation commit
   ↓
qh close exact-HEAD
   ↓
Final Gate PASS
   ↓
completion lifecycle commit
   ↓
safe push
```

## 자주 만나는 문제

| 증상 | 확인할 내용 |
|---|---|
| `doctor`가 Ollama FAIL | Ollama 실행 여부와 `ollama list` 확인 |
| `Repository is not clean` | `git status --short`, `git diff` 확인 |
| Task start 거부 | Current lifecycle, target Task Status, clean baseline 확인 |
| Worker 결과가 `NORMAL` | 대화 종료일 뿐. diff/commit/close 계속 수행 |
| `FAIL` / `BLOCKED` | 자동 반복 전에 Git diff와 Error Evidence 확인 |
| `Unexpected Changed Paths: yes` | scope 밖 변경 원인 조사. 완료 금지 |
| `Final Gate: FAIL` | 실패 Evidence 해결 전 완료로 간주 금지 |
| handoff가 `STOP_DIRTY` | local 변경을 먼저 검토하고 clean 상태 복구 |
| handoff가 diverged | 임의 history rewrite 대신 STOP 후 재-handoff/검토 |

## 더 읽기

- [README](../README.md)
- [PROJECT](../PROJECT.md)
- [REQUIREMENTS](../REQUIREMENTS.md)
- [How It Works](HOW_IT_WORKS.md)
- [Development Guide](DEVELOPMENT.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [STATUS](../STATUS.md)
- [BACKLOG](../BACKLOG.md)
