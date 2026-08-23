# Qwen Harness Troubleshooting

> 실제 Repository에서 확인된 문제만 기록합니다.  
> 추측성 해결책보다 **증상 → 원인 → 조사 → 검증된 해결/처분 → 재발 방지** 순서를 우선합니다.

초기 운영 장애의 원본 기록은 [`verified_problem_resolutions.md`](verified_problem_resolutions.md), Worker 진단과 Candidate 실험은 [`WORKER_DIAG_001_EVIDENCE.md`](WORKER_DIAG_001_EVIDENCE.md), [`WORKER_ROB_001_EVIDENCE.md`](WORKER_ROB_001_EVIDENCE.md), [`WORKER_ROB_002_EVIDENCE.md`](WORKER_ROB_002_EVIDENCE.md)에 있습니다.

---

## 빠른 문제 찾기

| 증상 | 먼저 볼 항목 |
|---|---|
| Windows CMD에 긴 내용을 붙여넣은 뒤 이상한 명령/파일이 생김 | [1. CMD multiline / redirection](#1-windows-cmd-multiline--redirection-실패) |
| `git status`에 예상 못 한 `??` 파일이 생김 | [2. Unexpected artifact](#2-예상하지-못한-untracked-artifact) |
| Qwen 결과가 PASS라고 하지만 diff가 이상함 | [3. Qwen candidate isolation](#3-qwen-candidate는-바로-repository에-적용하지-않기) |
| 작은 수정인데 diff가 수십/수백 줄로 늘어남 | [4. Whole-file cleanup pollution](#4-전체-파일-cleanup이-scope를-오염시킴) |
| NUL path parsing이 이상함 | [5. Nested escaping](#5-nested-cmdpython-escape로-nul-delimiter가-깨짐) |
| Qwen이 지나치게 큰/불완전한 코드를 만듦 | [6. Bounded repair](#6-oversized--malformed-qwen-candidate) |
| Base64/zlib 문서 생성이 깨짐 | [7. Opaque payload](#7-opaque-base64zlib-payload-손상) |
| Verification이 실행됐는데 계약 일부가 빠진 것 같음 | [8. Verification fail-closed](#8-verification-contract가-완전하게-해석되지-않음) |
| `unittest`가 성공한 것 같은데 0 tests | [9. Zero-test discovery](#9-repository-root-unittest-discovery가-0-tests) |
| 다른 Repository에서 `No module named 'tools'` | [10. Runtime portability](#10-cross-repository-run에서-no-module-named-tools) |
| Worker가 한 step에 여러 ToolRequest를 반환 | [11. Multi-tool SAFETY](#11-worker가-한-step에서-여러-toolrequest를-반환) |
| 짧은 prompt는 되는데 full Task는 30초 timeout | [12. Full Task timeout](#12-짧은-prompt는-되지만-full-task는-30초-timeout) |
| Worker Candidate가 실험 실패했는데 Task를 어떻게 닫아야 하는지 애매함 | [13. Unsuccessful lifecycle](#13-실험은-끝났지만-candidate가-실패한-경우) |
| range cherry-pick 뒤 일부 파일이 빠지거나 `--skip`을 반복함 | [14. 원격 handoff 누락](#14-multi-commit-range-cherry-pick에서-인계-누락) |

---

## 1. Windows CMD multiline / redirection 실패

### 증상

긴 Python 또는 Markdown을 Windows CMD에 직접 붙여넣은 뒤:

- Python string이 중간에서 끊김
- 이후 Markdown 줄이 CMD 명령으로 실행됨
- `>` 같은 문자가 redirection으로 해석됨
- 예상하지 못한 파일이 생성됨

### 원인

CMD가 Python보다 먼저 줄바꿈과 shell metacharacter를 해석했습니다.

### 검증된 대응

1. 실패한 명령을 중단합니다.
2. `git status --short`로 Repository mutation을 확인합니다.
3. 예상하지 못한 파일이 있으면 지우기 전에 크기와 내용을 먼저 확인합니다.
4. accidental artifact임이 확인된 뒤에만 삭제합니다.
5. 반복되는 content-generation 절차는 CMD one-liner가 아니라 Repository Python utility 또는 file-based workflow로 옮깁니다.

### Evidence

초기 incident에서 `tuple[str`라는 accidental file이 `git status --short`로 발견되었고, inspection으로 empty artifact임을 확인한 후 삭제했습니다. 이후 working tree가 clean으로 복구되었습니다.

### 예방

긴 Markdown/Python payload를 CMD에 직접 운반하지 않습니다.

Source: [`verified_problem_resolutions.md` Incident 001](verified_problem_resolutions.md)

---

## 2. 예상하지 못한 untracked artifact

### 증상

`git status --short`에서 현재 Task scope에 없는 `?? path`가 나타납니다.

### 원인

failed CMD redirection 또는 accidental command output이 Repository file을 만들 수 있습니다.

### 잘못된 대응

clean 상태를 만들기 위해 원인을 확인하지 않고 바로 삭제하는 것.

### 검증된 대응

파일의 path, size, content를 먼저 확인합니다. accidental artifact라는 Evidence가 확보된 뒤 삭제하고 다시 `git status --short`를 확인합니다.

### 예방

Unexpected path는 "치워야 할 쓰레기"가 아니라 먼저 조사해야 하는 Evidence로 취급합니다.

Source: [`verified_problem_resolutions.md` Incident 002](verified_problem_resolutions.md)

---

## 3. Qwen candidate는 바로 Repository에 적용하지 않기

### 증상

Qwen이 syntactically valid한 코드를 만들었지만:

- 기존 함수가 사라짐
- 불필요한 helper 추가
- Markdown fence 포함
- module docstring 누락
- Task와 다른 Git logic 추가
- self-report는 PASS

### 원인

LLM generation은 nondeterministic하고 생성 성공은 semantic correctness나 scope compliance를 증명하지 않습니다.

### 검증된 대응

Candidate를 실제 source file과 분리한 뒤 다음을 확인합니다.

```text
syntax
→ existing top-level definition preservation
→ newly added definitions
→ focused candidate tests
→ full regression
→ exact diff / scope
```

모든 Evidence가 만족된 뒤에만 Repository에 적용합니다.

### Evidence

HC-003B candidate는 11 focused tests와 46 full tests PASS 뒤 적용되었습니다. HC-003C에서는 잘못된 Candidate를 Repository를 수정하지 않은 채 test로 탈락시켰고, 최종 Candidate는 9 focused + 46 full tests PASS 후 적용했습니다.

### 예방

**Worker self-reported PASS is not Evidence.**

Source: [`verified_problem_resolutions.md` Incident 003](verified_problem_resolutions.md)

---

## 4. 전체 파일 cleanup이 scope를 오염시킴

### 증상

새 block의 trailing whitespace만 정리하려 했는데 diff가 갑자기 100줄 이상으로 늘어납니다.

### 원인

cleanup regex가 newly added block이 아니라 기존 source 전체에 적용되었습니다.

### 검증된 대응

원본 파일을 Git에서 복구하고 validated Candidate에서 승인된 새 block만 다시 가져옵니다. 그 block 내부의 whitespace만 정리한 후 minimal diff를 확인합니다.

### Evidence

HC-003B에서 global cleanup 후 diff가 **106 changed lines**로 증가했습니다. 원본 복구 후 block-only reapplication으로 **45 insertions / 1 deletion**의 의도한 범위로 돌아왔고 `git diff --check`와 46 tests가 PASS했습니다.

### 예방

좁은 Task에서 whole-file formatter/cleanup을 임의로 실행하지 않습니다.

Source: [`verified_problem_resolutions.md` Incident 004](verified_problem_resolutions.md)

---

## 5. Nested CMD/Python escape로 NUL delimiter가 깨짐

### 증상

Git의 NUL-delimited path output을 split했는데 여러 path가 하나의 값으로 붙어 있습니다.

### 원인

Windows CMD → `python -c` → source-generating Python string → generated source를 거치면서 `\0`의 의미가 바뀌었습니다.

### 검증된 대응

중첩 escape literal 대신 명시적인 byte construction을 사용했습니다.

```python
bytes([0])
```

### Evidence

수정 전 HC-003C focused tests 9개 중 4개가 실패했습니다. `bytes([0])`으로 변경 후 9/9 focused와 46/46 full tests가 PASS했습니다.

### 예방

여러 interpretation layer를 통과하는 control byte는 nested backslash escape보다 explicit construction을 사용합니다.

Source: [`verified_problem_resolutions.md` Incident 005](verified_problem_resolutions.md)

---

## 6. Oversized / malformed Qwen candidate

### 증상

Qwen Candidate가:

- 너무 큼
- reasoning comment가 수백 줄
- incomplete file
- unnecessary helper
- Markdown fence
- Task contract 위반

형태로 나옵니다.

### 원인

Local LLM generation 품질은 probabilistic합니다. prompt를 계속 길게 만든다고 안정적으로 해결되지 않습니다.

### 검증된 대응

Candidate를 격리하고 syntax/AST/diff/tests로 실패 이유를 구체화합니다. 그 Evidence로 **bounded repair 한 번**을 수행합니다. 반복해도 실패하면 FAIL/BLOCKED로 멈춥니다.

### Evidence

HC-003B에서 qwen3.5:9b 첫 Candidate는 **515 lines**였고 불필요한 helper와 많은 reasoning comments를 포함했습니다. bounded repair 후 **240 lines** Candidate가 기존 definitions를 보존했고 11 focused + 46 full tests PASS했습니다.

### 예방

무제한 prompt retry를 하지 않습니다. Candidate size와 preservation도 검증 대상입니다.

Source: [`verified_problem_resolutions.md` Incident 006](verified_problem_resolutions.md)

---

## 7. Opaque Base64/zlib payload 손상

### 증상

긴 문서를 Base64/zlib으로 압축해 CMD `python -c`로 전달했는데 `zlib.error`가 발생합니다.

### 원인

사람이 검사하기 어려운 opaque payload가 CMD/Python transport layer 위에 하나 더 추가되어 corruption을 찾기 어려워졌습니다.

### 검증된 대응

실패 후 `git status`와 file existence를 먼저 확인했습니다. write가 발생하지 않은 것을 확인한 다음, 짧고 읽을 수 있는 Python command로 문서를 생성하고 incrementally append했습니다.

### Evidence

zlib error 직후 intended runbook file은 생성되지 않았고 Repository mutation도 없었습니다.

### 예방

quoting 회피만을 위해 긴 encoded blob을 만들지 않습니다. 길어지면 file-based utility로 승격합니다.

Source: [`verified_problem_resolutions.md` Incident 007](verified_problem_resolutions.md)

---

## 8. Verification contract가 완전하게 해석되지 않음

### 증상

의도한 Verification은 여러 command인데 parser가 일부만 contract로 인식해도 final workflow가 진행될 수 있는 위험이 있습니다.

### 원인

Milestone 1 E2E 이후 실제 QH-V2-CLI-001 과정에서 Verification completeness를 fail-closed로 보장하지 못하는 gap이 확인되었습니다.

### 처분

[`ADR-010`](../DECISIONS.md)은 이 문제를 다음 capability expansion 전에 처리해야 하는 최우선 hardening으로 지정했습니다.

QH-V2-HARD-002에서 Verification fail-closed hardening을 구현했습니다.

### 예방

Verification parser가 승인된 contract shape를 만족하지 못하면 일부 command만 실행하고 계속하는 대신 fail closed해야 합니다.

### 확인 포인트

- 현재 Task의 `## Verification` 형식
- parser가 추출한 command 개수
- `qh close`의 authoritative Verification output
- Final Gate가 실행한 exact contract

Source: [`ADR-010`](../DECISIONS.md), `QH-V2-HARD-002`

---

## 9. Repository-root unittest discovery가 0 tests

### 증상

Repository root에서 default `unittest` discovery가 실제 suite를 실행하지 않고 zero tests를 찾습니다.

### 위험

명령 exit/output을 대충 보면 regression이 실행된 것처럼 오해할 수 있습니다.

### 원인

Repository-root default discovery와 실제 `tests` layout 사이의 discovery integrity gap이 있었습니다.

### 검증된 대응

QH-V2-HARD-007에서 root discovery가 실제 suite를 실행하도록 하고 representative tests가 undiscoverable해지면 실패하는 deterministic meta-regression을 추가했습니다.

### 예방

"test command가 실행됐다"가 아니라 **실제 test count와 representative discovery**를 Evidence로 봅니다.

Source: [`tasks/QH-V2-HARD-007.md`](../tasks/QH-V2-HARD-007.md)

---

## 10. Cross-Repository run에서 `No module named 'tools'`

### 증상

다른 Repository에 Harness를 복사해 documented command를 실행할 때:

```text
python tools\qh.py run TASK-ID
```

`ModuleNotFoundError: No module named 'tools'`가 발생할 수 있습니다.

### 원인

entry-path/import-chain이 operator-set `PYTHONPATH`에 사실상 의존하는 runtime portability defect였습니다.

### 조사

`qh doctor`와 `qh preflight`는 delayed Worker/run import chain을 직접 exercise하지 않아 readiness를 잘못 판단할 수 있었습니다.

### 검증된 대응

QH-V2-HARD-008에서 documented direct entry path가 operator `PYTHONPATH` 없이 동작하도록 runtime import portability를 수정하고, `qh doctor`가 delayed Worker import chain의 structural readiness를 확인하도록 regression을 추가했습니다.

### 중요한 경계

이 수정은 formal Globalization 승인이 아닙니다.

`GLOBALIZATION = NOT AUTHORIZED`

Source: [`tasks/QH-V2-HARD-008.md`](../tasks/QH-V2-HARD-008.md), [`ADR-014`](../DECISIONS.md)

---

## 11. Worker가 한 step에서 여러 ToolRequest를 반환

### 증상

real `qwen3:8b`가 한 WorkerStep에서 둘 이상의 ToolRequest를 반환합니다.

### 현재 safety behavior

Runner는 이 step을 `SAFETY`로 fail closed하고 invalid step의 Tool을 **하나도 실행하지 않습니다**.

### 하지 않은 것

- multi-tool request를 자동 분할하지 않음
- 하나만 골라 실행하지 않음
- silent repair하지 않음
- retry로 의미를 바꾸지 않음

### WORKER-ROB-001 실험

one-tool protocol을 더 강하게 prompt하면 개선되는지 Candidate를 측정했습니다.

결과:

- Stable 0/10 exact task success
- Candidate 0/10 exact task success
- Candidate promotion REJECTED

따라서 safety boundary는 유지하고 Candidate는 production에 적용하지 않았습니다.

Task 상태:

`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

Source: [`WORKER_ROB_001_EVIDENCE.md`](WORKER_ROB_001_EVIDENCE.md), [`ADR-014`](../DECISIONS.md), [`ADR-015`](../DECISIONS.md)

---

## 12. 짧은 prompt는 되지만 full Task는 30초 timeout

### 증상

native Ollama Worker에서 짧은 request는 빠르게 완료되지만 representative full Task는 현재 30.0 s timeout에 반복 도달합니다.

### QH-V2-WORKER-DIAG-001 측정

| 조건 | 결과 |
|---|---|
| short, no tools | 5/5 success |
| short + tools | 5/5 success |
| full Task, no tools | 0/5; 모두 약 30 s timeout |
| same full input constrained to `OK` | 3/3 quick |
| full Task + tools | 일부 빠른 relevant ToolRequest + 반복 timeout |

### 해석

Evidence가 지지하지 않는 결론:

- "입력이 길어서 무조건 timeout"
- "tool schema 때문에 timeout"
- "timeout을 늘리면 해결"

같은 긴 input에서도 exact `OK` 요청은 빠르게 완료되었기 때문에 input length만으로는 설명할 수 없습니다.

### 추가로 발견된 문제

observed socket `TimeoutError`가 Adapter의 기존 handling에서 normalize되지 않고 escape했습니다. 이것은 timeout 원인과 별도의 transport-normalization 후보입니다.

### 다음 Evidence-driven 조치

진단 결과는 deterministic Worker Brief 실험을 제안했습니다. QH-V2-WORKER-ROB-002에서 Candidate A가 10/10 valid bounded first step, 0/10 timeout을 기록했습니다.

하지만 Candidate A는 아직 production integration되지 않았습니다.

Source: [`WORKER_DIAG_001_EVIDENCE.md`](WORKER_DIAG_001_EVIDENCE.md), [`WORKER_ROB_002_EVIDENCE.md`](WORKER_ROB_002_EVIDENCE.md)

---

## 13. 실험은 끝났지만 Candidate가 실패한 경우

### 문제

실험 Task를 실제로 수행했고 충분한 Evidence도 있지만 Candidate가 Acceptance Criteria를 충족하지 못했습니다.

기존 lifecycle에서 `COMPLETE - VERIFIED`로 표시하면 거짓 성공이 되고, ACTIVE로 계속 두면 다음 작업을 막습니다.

### 검증된 해결

[`ADR-015`](../DECISIONS.md)은 별도 terminal state를 정의했습니다.

```text
CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED
```

QH-V2-LIFECYCLE-001이 이를 durable lifecycle operation으로 구현했습니다.

### 의미

이 상태는:

- Task를 실제로 시도/평가했음
- objective Evidence가 있음
- production promotion은 하지 않았음
- PASS가 아님
- later work가 성공 Evidence로 인용하면 안 됨

을 의미합니다.

### 첫 사례

QH-V2-WORKER-ROB-001.

Source: [`ADR-015`](../DECISIONS.md), [`tasks/QH-V2-LIFECYCLE-001.md`](../tasks/QH-V2-LIFECYCLE-001.md)

---

## 14. Multi-commit range cherry-pick에서 인계 누락

### 증상

QH-V2-DOC-003에서 원격 작업 브랜치의 여러 commit을 범위 `cherry-pick`으로
가져오는 도중 empty commit이 발생했고 `git cherry-pick --skip`을 반복한 뒤,
최종적으로 `docs/PROJECT_TIMELINE.md`가 로컬에 없는 상태가 발견됐습니다.

### 원인

원격 작업 결과가 여러 commit으로 나뉜 상태에서 로컬에 이미 일부와 동일한
변경이 섞이면서 cherry-pick sequence가 사람이 추적하기 어려운 상태가 됐습니다.
`--skip` 자체가 파일 누락을 자동으로 검증하지 않기 때문에 sequence 종료만 보고
완료로 판단하면 위험합니다.

### 당시 처분

Repository corruption은 발생하지 않았습니다. 최종 Verification 전에 expected
path와 실제 diff를 deterministic하게 비교해 누락을 찾았고, 누락된 exact commit만
별도로 확인해 적용한 뒤 다시 Verification했습니다.

### 이후 표준 해결

QH-V2-OPS-GIT-001은 일상 handoff를 다음 구조로 바꿉니다.

```text
exact local baseline
  -> 그 SHA에서 remote branch 생성
  -> one atomic handoff commit
  -> git fetch
  -> qh handoff-check <remote-ref>
  -> FAST_FORWARD_SAFE
  -> git merge --ff-only <remote-ref>
```

`qh handoff-check`는 read-only이며 현재 Local HEAD와 handoff commit의 direct-parent
관계, commit parent shape, changed paths, dirty 상태를 검사합니다.

### STOP해야 하는 경우

- `STOP_DIRTY`
- `STOP_NON_ATOMIC_OR_DIVERGED`
- merge commit handoff
- baseline에서 두 commit 이상 진행된 handoff
- history divergence

이 경우 자동 reset/rebase/merge/cherry-pick 복구를 하지 않습니다. exact baseline에서
새 handoff를 만들거나 별도 Human-reviewed integration으로 처리합니다.

### 예방

정상 원격 인계에서 multi-commit range `cherry-pick`과 반복 `--skip`을 사용하지
않습니다. 적용 전에 changed paths와 classification을 먼저 확인합니다.

Source: `QH-V2-OPS-GIT-001`, `ADR-017A`

---

## 문제 발생 시 기본 순서

Qwen Harness 자체를 개발하거나 사용하는 동안 예상하지 못한 문제가 생기면 아래 순서가 기본입니다.

```text
STOP speculative changes
→ git status / exact changed paths 확인
→ 현재 Task Allowed/Forbidden scope 확인
→ 기존 verified incident / ADR / Evidence 검색
→ 원인 Evidence 수집
→ 최소 수정 또는 truthful FAIL/BLOCKED/UNSUCCESSFUL disposition
→ focused test
→ authoritative qh close 또는 해당 Task의 approved terminal path
```

문제를 숨기기 위해 clean working tree를 만들지 않습니다. 먼저 원인을 확인하고 Evidence를 남깁니다.

---

## 관련 문서

- [Project Timeline](PROJECT_TIMELINE.md)
- [Development Log](DEVELOPMENT_LOG.md)
- [Research Log](RESEARCH_LOG.md)
- [Verified Problem Resolutions](verified_problem_resolutions.md)
- [Architecture Decisions](../DECISIONS.md)
