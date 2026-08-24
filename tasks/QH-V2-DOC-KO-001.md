# QH-V2-DOC-KO-001 - GitHub 문서 한국어 통일 및 최신화

## Status

COMPLETE - VERIFIED

## Problem

현재 Repository의 사용자-facing 문서는 한국어 중심으로 작성된 파일과 영어 중심으로 작성된 파일이 섞여 있다. 특히 `README.md`의 현재 상태는 실제 `STATUS.md`보다 오래되어 `QH-V2-OPS-002`까지만 완료된 것으로 표시되고 있으며, `PROJECT.md`, `REQUIREMENTS.md`, `BACKLOG.md`, `DECISIONS.md`의 일부 핵심 설명도 영어 중심이라 한국어 사용자가 현재 구조와 진행 상황을 빠르게 이해하기 어렵다.

반대로 과거 Task 계약, 실험 Evidence, raw JSON과 같은 역사적 기록을 문서 미관을 위해 대규모 재작성하면 Git 추적성과 당시 Evidence의 의미를 훼손할 위험이 있다.

따라서 현재 사용자-facing 문서와 Formal Source of Truth의 읽기 경험은 한국어 중심으로 정리하되, 역사적 Evidence와 exact technical literal은 보존하는 별도 문서 Task가 필요하다.

## Goal

GitHub에서 처음 Repository를 보는 한국어 사용자가 현재 Qwen Harness의 목적, 설치/사용법, 현재 상태, 안전 원칙, 개발 흐름과 다음 계획을 자연스럽게 이해할 수 있도록 현재/사용자-facing Markdown 문서를 한국어 중심으로 통일하고 최신 상태로 맞춘다.

이 Task는 문서 표현과 현재 상태 설명만 다루며 production 코드 동작, Harness Architecture, Requirements 의미, Worker/Tool authority를 변경하지 않는다.

## Architecture Basis

- Repository 문서와 Git이 Source of Truth라는 ADR-001/ADR-008 계열 원칙을 유지한다.
- ADR-017의 Exception-Driven Human Supervision과 QH-V2-OPS-GIT-001의 안전한 handoff 정책을 현재 사용자 문서에 정확히 반영한다.
- QH-V2-OPS-GIT-001에서 선택된 순서 `QH-V2-DOC-KO-001 -> QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003`을 현재 계획으로 표시한다.
- `GLOBALIZATION = NOT AUTHORIZED`를 유지한다.
- 문서 최신화는 기존 Architecture/Requirements를 재설계하는 권한이 아니다.

## Documentation Policy

1. 사람이 읽는 새 GitHub Markdown 서술은 한국어를 기본 언어로 한다.
2. 다음 exact technical literal은 번역하지 않거나 원문을 병기한다.
   - Task ID / ADR ID / FR ID
   - CLI command와 code
   - file/path/API/model name
   - Git SHA
   - `ACTIVE`, `COMPLETE - VERIFIED`, `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`, `PASS`, `FAIL`, `BLOCKED`, `SAFETY` 같은 상태 토큰
   - `GLOBALIZATION = NOT AUTHORIZED`
3. `PROJECT.md`, `REQUIREMENTS.md`, `DECISIONS.md`, `BACKLOG.md`의 의미를 번역 과정에서 변경하지 않는다.
4. 완료된 과거 Task 계약, 실험 Evidence, raw JSON/result는 언어 통일을 이유로 대규모 재작성하지 않는다.
5. 역사적 기록의 영어 원문을 유지해야 추적성이 더 높은 경우에는 원문을 보존하고 한국어 안내/요약을 추가할 수 있다.
6. 현재 상태 설명은 `STATUS.md`와 완료 Git Evidence를 기준으로 갱신한다.

## Scope

1. `README.md`의 오래된 현재 상태를 최신 Repository 상태로 교정한다.
2. README의 설치, 사용 흐름, `qh` CLI, 안전 원칙, 현재 계획을 한국어 사용자 기준으로 정리한다.
3. `PROJECT.md`와 `REQUIREMENTS.md`의 사람이 읽는 설명을 기존 의미를 보존하면서 한국어 중심으로 정리한다.
4. `DECISIONS.md`와 `BACKLOG.md`는 현재 사용자가 방향을 이해하는 데 필요한 제목/설명/최신 정책을 한국어 중심으로 정리하되, 과거 Decision의 의미와 역사적 Evidence를 변경하지 않는다.
5. 다음 현재 사용자-facing 문서를 한국어 기준으로 점검하고 필요한 부분만 수정한다.
   - `docs/QUICKSTART.md`
   - `docs/HOW_IT_WORKS.md`
   - `docs/DEVELOPMENT.md`
   - `docs/TROUBLESHOOTING.md`
6. 다음 프로젝트 기록 문서는 기존 역사 내용을 보존하면서 navigation, 최신 단계 또는 혼합 언어 표현만 필요한 범위에서 정리한다.
   - `docs/PROJECT_TIMELINE.md`
   - `docs/DEVELOPMENT_LOG.md`
   - `docs/RESEARCH_LOG.md`
7. README와 사용자-facing 문서에서 QH-V2-OPS-GIT-001의 `qh handoff-check` + `git merge --ff-only` 운영 경로를 확인 가능하게 한다.
8. 현재 계획에 `QH-V2-DOC-KO-001 -> QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003` 순서를 반영한다.
9. Markdown 내부 링크와 상대 경로가 문서 수정으로 깨지지 않게 한다.

## Allowed Changes

- `README.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-DOC-KO-001.md`
- `docs/QUICKSTART.md`
- `docs/HOW_IT_WORKS.md`
- `docs/DEVELOPMENT.md`
- `docs/TROUBLESHOOTING.md`
- `docs/PROJECT_TIMELINE.md`
- `docs/DEVELOPMENT_LOG.md`
- `docs/RESEARCH_LOG.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `src/**`
- `ops/**`
- `experiments/**`
- 현재 Task 이외의 `tasks/**`
- `docs/*_EVIDENCE.md`
- `docs/*_RESULTS.json`
- historical G1 manifest 또는 raw Evidence 수정
- Worker Adapter/Runner/Retry 동작 변경
- model, `think`, timeout, Retry budget, Worker-step budget, Tool authority 변경
- `qh close`, Verification, Final Gate, lifecycle 또는 Git authority 변경
- Candidate A/B production integration
- Architecture/Requirements의 의미 변경
- Globalization 승인 또는 `GLOBALIZATION = NOT AUTHORIZED` 제거

## Acceptance Criteria

1. `README.md`가 더 이상 `QH-V2-OPS-002`를 현재 최신 완료 상태로 설명하지 않는다.
2. README가 최소한 `QH-V2-OPS-GIT-001`, `qh handoff-check`, `git merge --ff-only`와 현재 다음 단계 `QH-V2-DOC-KO-001 -> QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003`를 설명한다.
3. README, PROJECT, REQUIREMENTS와 주요 사용자-facing docs의 일반 설명은 한국어를 기본으로 한다.
4. `FR-004`, Worker successor 금지, deterministic Verification/Final Gate authority, `GLOBALIZATION = NOT AUTHORIZED`의 의미가 번역 과정에서 유지된다.
5. 과거 Task/Evidence/raw JSON은 언어 통일 목적으로 수정하지 않는다.
6. `DECISIONS.md`와 `BACKLOG.md`의 최신 정책/순서가 현재 Repository state와 충돌하지 않는다.
7. `docs/QUICKSTART.md`, `docs/HOW_IT_WORKS.md`, `docs/DEVELOPMENT.md`, `docs/TROUBLESHOOTING.md`의 주요 사용자 안내가 현재 CLI 및 handoff 흐름과 모순되지 않는다.
8. 프로젝트 timeline/log/research 문서의 역사적 사실과 commit/Task ID를 임의로 바꾸지 않는다.
9. 상대 Markdown 링크가 수정으로 인해 깨지지 않는다.
10. production code/test 동작 변경이 없다.
11. Allowed Changes만 발생한다.
12. `git diff --check`가 PASS한다.

## Verification

Run exactly:

`python -c "from pathlib import Path; r=Path('README.md').read_text(encoding='utf-8'); required=['QH-V2-OPS-GIT-001','qh handoff-check','git merge --ff-only','QH-V2-DOC-KO-001','QH-V2-ARCH-018','QH-V2-WORKER-ROB-003','QH-V2-OPS-003']; missing=[x for x in required if x not in r]; assert not missing, missing; assert 'QH-V2-OPS-002 (`qh doctor`)까지 COMPLETE - VERIFIED' not in r"`

Run exactly:

`python -c "from pathlib import Path; import re; files=['README.md','PROJECT.md','REQUIREMENTS.md','docs/QUICKSTART.md','docs/HOW_IT_WORKS.md','docs/DEVELOPMENT.md','docs/TROUBLESHOOTING.md']; bad=[p for p in files if not re.search(r'[가-힣]',Path(p).read_text(encoding='utf-8'))]; assert not bad,bad; text=Path('REQUIREMENTS.md').read_text(encoding='utf-8')+'\n'+Path('DECISIONS.md').read_text(encoding='utf-8')+'\n'+Path('BACKLOG.md').read_text(encoding='utf-8'); required=['FR-004','GLOBALIZATION = NOT AUTHORIZED','QH-V2-ARCH-018','QH-V2-WORKER-ROB-003']; missing=[x for x in required if x not in text]; assert not missing,missing"`

Run exactly:

`python -c "from pathlib import Path; import re; files=['README.md','PROJECT.md','REQUIREMENTS.md','docs/QUICKSTART.md','docs/HOW_IT_WORKS.md','docs/DEVELOPMENT.md','docs/TROUBLESHOOTING.md','docs/PROJECT_TIMELINE.md','docs/DEVELOPMENT_LOG.md','docs/RESEARCH_LOG.md']; missing=[]; pat=re.compile(r'\[[^\]]+\]\(([^)]+)\)'); [missing.append((f,x)) for f in files for x in pat.findall(Path(f).read_text(encoding='utf-8')) if not x.startswith(('http://','https://','#','mailto:')) and not (Path(f).parent/x.split('#',1)[0]).resolve().exists()]; assert not missing,missing"`

Run exactly:

`git diff --check`

Run exactly:

`git status --short`

## Verification Budget

이 Task는 문서 전용이므로 production Python 전체 regression을 중간 단계에서 반복 실행하지 않는다.

- 구현 중: 문서 내용/링크와 `git diff --check` 같은 focused check만 사용한다.
- 오류가 발견되면 해당 문서 검사만 다시 실행한다.
- 최종 완료: `qh close <exact implementation HEAD>`가 위 Verification 계약과 scope/Final Gate를 authoritative하게 한 번 실행한다.
- production 코드가 변경된 흔적이 발견되면 STOP하며 문서 Task에서 테스트를 추가로 돌려 이를 정당화하지 않는다.

## Evidence Requirements

성공적으로 close하기 전에 다음을 확인한다.

- exact Task contract baseline SHA
- README의 이전 stale 상태와 수정 후 현재 상태 차이
- 변경된 Markdown 파일 목록
- historical Evidence/raw result 파일 무변경
- relative-link check PASS
- `git diff --check` PASS
- exact implementation HEAD를 사용한 authoritative `qh close` Final Gate PASS
- Final Gate 이후 별도 lifecycle commit

## Stop Conditions

다음이 필요하면 Human/ChatGPT review를 위해 STOP한다.

- Architecture 또는 Requirements 의미 변경
- Worker/Runner/Retry/model/tool/lifecycle/Verification/Final Gate/Git authority 변경
- historical Evidence를 재작성해야만 문서 통일이 가능한 상황
- current state와 Git Evidence 사이의 충돌
- README에 표시할 다음 순서가 Source of Truth와 충돌하거나 모호한 경우
- Globalization 승인 또는 Trust Boundary 확대
- 문서 Task를 넘어 production 코드 수정이 필요한 경우

## Next Task

QH-V2-DOC-KO-001이 `COMPLETE - VERIFIED`에 도달하면 다음 Human-selected Architecture Task는:

`QH-V2-ARCH-018 - Deterministic Worker Brief Production Promotion Decision`

QH-V2-ARCH-018은 한국어 Task 계약으로 다시 준비하며, 과거 영어 draft branch를 그대로 authoritative contract로 사용하지 않는다.
