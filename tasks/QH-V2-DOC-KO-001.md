# QH-V2-DOC-KO-001 - GitHub 문서 한국어 통일 및 최신화

## Status

PLANNED - HUMAN APPROVED DIRECTION

## Problem

현재 Repository의 사용자-facing 문서는 한국어 중심이지만 일부 Source of Truth, 운영 문서, 과거에 생성된 문서에는 영어 서술이 섞여 있고 README의 현재 상태도 최신 완료 Task와 후속 계획을 충분히 반영하지 못한다.

Human은 2026-08-24부터 GitHub에 올리는 사람이 읽는 문서를 한국어로 작성하고, 현재 공개/운영 문서도 최신 상태로 정리하도록 요청했다.

다만 완료된 historical Task 계약, raw Evidence, JSON 결과, command/status/API/file name처럼 exact literal이 필요한 자료는 의미와 검증 가능성을 보존해야 한다.

## Goal

GitHub에서 사람이 읽는 현재/사용자-facing 문서를 한국어로 통일하고 최신 Repository 상태와 계획을 반영한다. 동시에 historical Evidence와 exact machine-readable literal의 의미를 변경하지 않는다.

## 기본 정책

- 새로 작성하는 GitHub Markdown 문서의 설명 문장은 한국어를 기본으로 한다.
- Task ID, ADR ID, 파일명, CLI command, code, status token, API name, model name, Git SHA 등 정확한 식별자는 원문 표기를 유지할 수 있다.
- raw 실험 결과와 JSON은 번역 때문에 값을 바꾸지 않는다.
- 완료된 historical Task 계약과 Evidence는 과거 사실을 재작성하지 않는다. 필요한 경우 한국어 요약/인덱스에서 설명한다.
- 현재 상태를 설명하는 README/운영 문서는 `STATUS.md`, 최신 Task, Git Evidence에 맞춰 갱신한다.

## 예정 Scope

정확한 Allowed/Forbidden Changes와 Verification은 QH-V2-OPS-GIT-001 완료 후 계약 baseline을 확정할 때 최종 검토한다.

우선 검토 대상:

- `README.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- 현재 운영/사용 가이드 `docs/*.md`
- 앞으로 생성되는 Task 계약과 설계/연구 문서

보존 우선 대상:

- 완료된 historical Task 계약의 의미
- raw Evidence/JSON
- exact command/status/API/file/model/SHA literal
- Git history

## Next Task

QH-V2-OPS-GIT-001 완료 후 이 Task의 exact contract를 확정하고 실행한다. 완료 후 Human이 이미 선택한 `QH-V2-ARCH-018` 경로로 진행한다.
