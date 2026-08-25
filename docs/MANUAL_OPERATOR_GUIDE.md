# Codex 없이 Qwen Harness 계속 사용하는 방법

이 문서는 Codex CLI를 잠시 사용하지 않는 동안 Human이 직접 Repository 작업을 진행하는 절차를 설명합니다.

핵심은 **Codex만 빠지는 것이지 Harness 검증 절차를 없애는 것이 아닙니다.**

권장 역할은 다음과 같습니다.

```text
Human
  - CMD 명령 실행
  - Git commit / push
  - 필요하면 직접 파일 수정

ChatGPT
  - Requirements / Architecture / Task 설계
  - 기술 판단과 Review
  - 다음 단계 결정

Qwen Harness
  - 승인된 Task 범위의 Worker 실행
  - Scope / Verification / Final Gate

Qwen3:8B
  - Harness가 허용한 Tool 안에서 실제 작업 수행
```

Codex는 편리한 외부 Supervisor/Executor였지만 Qwen Harness의 필수 구성요소는 아닙니다.

---

## 1. 지금 프로젝트 상태

현재 authoritative Repository 상태는 다음과 같습니다.

- `QH-V2-PERF-007` = `COMPLETE - VERIFIED`
- implementation HEAD = `031dcae9beaef2db2730fbb81051fff7c3a40e79`
- lifecycle commit = `7ea2f389b7bd03858325dc38d7c72e0615653847`
- PERF-007 focused 14 tests: `551.646s -> 357.777s` (`35.15%` 개선)
- Git process starts: `284 -> 203` (`28.52%` 감소)
- final `tests.test_qh`: `1157.8s`
- final review phase: `1613.8s`
- practical runtime trigger `300s` 초과
- `QH-V2-OPS-004`는 시작하지 않음
- 다음 단계는 **Verification Strategy / Regression Tiering Architecture Review**
- `GLOBALIZATION = NOT AUTHORIZED`

즉 현재는 새 구현 Task를 바로 시작하는 상태가 아닙니다.

---

## 2. 작업을 시작하기 전에 항상 하는 것

Repository 폴더:

```bat
cd /d D:\qwen-harness-test
```

GitHub 최신 상태 가져오기:

```bat
git fetch origin
git pull --ff-only origin main
```

현재 상태 확인:

```bat
git status --short
git rev-parse HEAD
qh.cmd status
```

`git status --short`가 비어 있지 않으면 원인을 확인하기 전에는 다음 lifecycle 작업을 진행하지 않습니다.

---

## 3. Source of Truth 읽는 순서

새 작업을 시작하기 전에 최소한 다음을 확인합니다.

```text
PROJECT.md
REQUIREMENTS.md
DECISIONS.md
STATUS.md
BACKLOG.md
현재 tasks/<TASK-ID>.md
```

우선순위는 Chat 기록보다 Repository가 높습니다.

특히 다음을 확인합니다.

- Current Task
- Next Planned Task
- Task Status
- Allowed Changes
- Forbidden Changes
- Verification
- Stop Conditions

---

## 4. 지금 당장 하면 안 되는 것

현재 PERF-007 결과가 300초 practical trigger를 초과했으므로 다음은 바로 실행하지 않습니다.

```bat
qh.cmd start QH-V2-OPS-004
```

먼저 ChatGPT와 **Verification regression tiering Architecture**를 결정해야 합니다.

검토 대상 예시는 다음과 같습니다.

```text
Task close
  -> Task와 직접 관련된 focused authoritative regression
  -> 핵심 invariant suite
  -> exact HEAD / fresh Evidence

Milestone / Release / Main Gate
  -> repository-wide integration regression
  -> exact HEAD / fresh Evidence
```

다만 아직 Architecture로 Accepted된 것이 아니므로 임의 구현하지 않습니다.

---

## 5. 새 Task가 승인된 뒤 Human이 직접 실행하는 표준 절차

아래에서 `<TASK-ID>`와 `<IMPLEMENTATION-SHA>`는 실제 값으로 바꿉니다.

### A. 시작 전 확인

```bat
git status --short
qh.cmd status
```

working tree가 clean이어야 합니다.

### B. 승인된 Task 시작

```bat
qh.cmd start <TASK-ID>
```

변경된 `STATUS.md` 확인:

```bat
git diff -- STATUS.md
```

start lifecycle만 commit:

```bat
git add STATUS.md
git commit -m "start <TASK-ID>"
```

### C. Qwen Worker 실행

Task가 Qwen Worker 사용을 허용한다면:

```bat
qh.cmd preflight
qh.cmd run <TASK-ID>
```

`NORMAL`은 완료가 아닙니다.

작업 결과 확인:

```bat
git status --short
git diff
```

Qwen이 작업을 못 했거나 일부 수정이 필요하면 Human이 직접 Allowed Changes 안에서 수정해도 됩니다.

### D. 개발 중 테스트

Task의 Verification 전체를 계속 반복하지 말고 변경한 기능의 focused test부터 실행합니다.

예:

```bat
python -m unittest tests.test_example
```

실제 명령은 반드시 현재 Task 계약을 기준으로 선택합니다.

### E. implementation commit

변경 경로 확인:

```bat
git status --short
git diff --check
```

Allowed Changes만 stage합니다.

```bat
git add path\to\allowed-file
```

stage 내용 확인:

```bat
git diff --cached
```

commit:

```bat
git commit -m "implement <TASK-ID>"
```

implementation SHA 확인:

```bat
git rev-parse HEAD
```

출력된 SHA를 복사합니다.

### F. authoritative close

```bat
qh.cmd close <IMPLEMENTATION-SHA>
```

반드시 다음을 확인합니다.

```text
Verification exit 0
Unexpected Changed Paths: no
Diff Check: exit 0
Final Gate: PASS
```

FAIL이면 성공으로 간주하지 않습니다.

### G. lifecycle completion commit

`qh close`가 성공하면 보통 `STATUS.md`와 현재 Task 파일이 lifecycle 상태로 변경됩니다.

```bat
git status --short
git diff
```

lifecycle 파일만 별도 commit:

```bat
git add STATUS.md tasks\<TASK-ID>.md
git commit -m "mark <TASK-ID> complete"
```

### H. GitHub push

```bat
git status --short
git push origin main
```

마지막 확인:

```bat
git status --short
git rev-parse HEAD
git rev-parse origin/main
```

두 SHA가 같고 working tree가 clean이면 handoff 준비가 된 상태입니다.

---

## 6. ChatGPT에 무엇을 보내면 되는가

Human이 직접 작업할 때는 모든 로그를 보낼 필요가 없습니다.

다음 상황에서 결과를 보내면 됩니다.

### 정상 진행

아래 정도만 보내면 충분합니다.

```text
Task ID
focused test 결과
implementation SHA
qh close Final Gate 결과
lifecycle SHA
working tree clean 여부
```

### 문제가 발생했을 때

다음을 그대로 복사해서 보냅니다.

```text
실행한 명령
전체 오류 메시지
현재 git status --short
현재 git rev-parse HEAD
```

ChatGPT가 원인을 분석한 뒤 **다음 명령 하나씩** 안내하는 방식으로 진행할 수 있습니다.

---

## 7. 절대 임의로 하지 않는 것

- 실패한 `qh close`를 PASS로 간주
- Forbidden path 수정
- 테스트 삭제 또는 skip으로 PASS 만들기
- assertion 약화
- stale/cached PASS 재사용
- `git reset --hard`, force push 같은 파괴적 복구를 문제 분석 없이 실행
- Architecture / Requirements를 구현 중 편의상 변경
- Worker에게 shell/Git 전체 권한 부여
- 다음 Task 자동 시작
- Globalization

문제가 생기면 현재 Task 범위 안에서 먼저 `Analyze -> Fix -> Test -> Verify`로 해결합니다.

---

## 8. Codex가 다시 사용 가능해졌을 때

Codex를 다시 켜도 Repository가 Source of Truth입니다.

Codex에 먼저 다음을 시키면 됩니다.

```text
Repository Source of Truth와 현재 Git 상태를 먼저 읽고, STATUS.md의 Current/Next 상태와 현재 Task 계약을 기준으로 이어서 진행해. 기존 대화 기억보다 Repository를 우선하고, 완료 주장은 Git/Test Evidence와 qh Final Gate로만 판단해.
```

그 후 Codex는 다시 implementation/test/debug executor 역할을 맡을 수 있습니다.

---

## 현재 다음 판단

PERF-007 결과로 routine authoritative close가 practical target인 300초를 크게 넘었습니다.

따라서 다음 구현보다 먼저 Human + ChatGPT가 다음을 결정해야 합니다.

**Verification Strategy / Regression Tiering Architecture Review**

결정 전에는 `QH-V2-OPS-004`를 시작하지 않습니다.
