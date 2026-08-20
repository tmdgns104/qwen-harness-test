# QH-V2-DOC-002 - Beginner Onboarding and Hardware Guide

## Status

COMPLETE - VERIFIED

## Goal

Make the public GitHub landing page answer two beginner questions before the
detailed Architecture:

1. Can this project run on my PC?
2. How does someone with only basic Python familiarity perform the first setup?

Document one actually tested hardware environment without presenting it as a
minimum requirement or a general compatibility guarantee. Preserve the existing
Architecture, trust model, lifecycle, and production behavior.

## Architecture Basis

- ADR-001 keeps objective Evidence, not LLM self-report, as completion authority.
- ADR-002 keeps native Ollama plus Qwen3:8B as the default local Worker path.
- ADR-007 keeps `qh close` as the authoritative final Verification operation.
- ADR-010 keeps capability expansion and HARD-003 separate from this documentation Task.
- QH-V2-E2E-001 and Repository history provide COMPLETE - VERIFIED real Worker E2E Evidence.
- The maintainer has supplied the tested-machine facts for this Task: Windows,
  NVIDIA RTX 5070 Laptop GPU, 8 GB VRAM, 32 GB system RAM, Ollama, `qwen3:8b`,
  successful real Repository Worker E2E, and observed mixed CPU/GPU use during execution.
- A current read-only probe independently identified the RTX 5070 Laptop GPU with
  8151 MiB VRAM and confirmed that local Ollama has `qwen3:8b`; the 32 GB RAM and
  mixed-use observations remain maintainer-provided tested-run Evidence.

These facts describe one tested environment. They do not establish minimum VRAM,
support for every NVIDIA GPU, CPU-only support, Linux/macOS E2E support, an offload
ratio, or a performance guarantee.

## Dependencies

- QH-V2-DOC-001 is COMPLETE - VERIFIED.
- QH-V2-HARD-002 is COMPLETE - VERIFIED.
- The separately reviewed Hardening/Operations Backlog is preserved in commit `c38df9f`.
- The Human explicitly selected this documentation-only Task before HARD-003.
  This does not reorder or start the Hardening queue.

## Scope

- Reorder the README opening into a beginner-first path while retaining the existing
  detailed Architecture and trust-model content below it.
- Add beginner navigation links to Quick Start, How It Works, and Development Guide.
- Add a Tested Hardware section that separates the one verified machine from
  unverified environments and environment-dependent performance.
- Add a copy/paste 5-minute setup path with one-sentence meaning and expected result
  for each requested command.
- Explain what setup success proves and what `status`/`preflight` do not prove.
- Explain Task, Allowed Changes, Forbidden Changes, Verification, Final Gate, and
  Git commit in beginner language.
- Add `Python을 어느 정도 알아야 하나요?` near the start of QUICKSTART while
  preserving its complete 1-through-12 lifecycle and safety guidance.
- Record implementation and Verification Evidence in this Task and STATUS.
- After successful close, restore HARD-003 as the nominated PLANNED candidate without
  approving or starting it.

## Allowed Changes

- `README.md`
- `docs/QUICKSTART.md`
- `STATUS.md`
- `tasks/QH-V2-DOC-002.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `DECISIONS.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `BACKLOG.md`
- `docs/HOW_IT_WORKS.md`
- `docs/DEVELOPMENT.md`

All existing Task contracts and every path not listed under Allowed Changes remain
default-denied by ChangeScope.

## Acceptance Criteria

1. README begins with project meaning and the Evidence principle, followed in order
   by beginner navigation, Tested Hardware, 5-minute setup, installation-success
   checks, first-Task concepts, and then the retained detailed explanation.
2. The Tested Hardware section records Windows, RTX 5070 Laptop GPU, 8 GB VRAM,
   32 GB system RAM, Ollama, `qwen3:8b`, successful real Repository Worker E2E,
   and observed mixed CPU/GPU use.
3. Hardware wording explicitly says the tested machine is not a minimum specification.
4. Other GPU/VRAM setups, CPU-only execution, and Linux/macOS E2E are labelled
   unverified; CPU/system-RAM use and performance are possibilities that vary by environment.
5. README contains every requested setup command in copy/paste form and gives each
   command a one-sentence purpose plus normal expected result.
6. README explains that model download may exceed five minutes and that
   `status`/`preflight` do not contact Ollama or prove Worker E2E success.
7. README defines Task, Allowed Changes, Forbidden Changes, Verification, Final Gate,
   and Git commit in beginner language without weakening their actual authority.
8. README links beginners to QUICKSTART, HOW_IT_WORKS, and DEVELOPMENT using
   existing Repository-relative paths.
9. QUICKSTART adds `Python을 어느 정도 알아야 하나요?`, recommends creating and
   following its embedded QH-LOCAL-001 example, and preserves the existing lifecycle.
10. Every README internal link resolves and the documented qh commands match `tools/qh.py`.
11. No minimum VRAM number, universal GPU/OS/CPU-only support, performance promise,
    Architecture change, production-code change, or test change is introduced.
12. Task-range changed paths contain only Allowed Changes and `git diff --check` passes.
13. After close, STATUS nominates QH-V2-HARD-003 as PLANNED/Human-approval-required,
    but no next Task is started.

## Verification

Run exactly:

`python -c "import re; from pathlib import Path; text=Path('README.md').read_text(encoding='utf-8'); links=[v.split('#',1)[0] for v in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text) if not v.startswith(('http://','https://','#'))]; assert links and all((Path('README.md').parent/v).exists() for v in links if v),links"`

Then run:

`python -c "from pathlib import Path; s=Path('README.md').read_text(encoding='utf-8'); headings=('## 처음이라면 여기부터','## Tested Hardware / 실제로 검증된 실행 환경','## 처음 사용하는 사람을 위한 5분 시작','## 설치 성공 확인','## 첫 Task를 이해하기','## 왜 만들었나요?','## 전체 흐름'); positions=tuple(s.index(x) for x in headings); assert positions==tuple(sorted(positions)); required=('RTX 5070 Laptop GPU','VRAM 8 GB','System RAM 32 GB','qwen3:8b','CPU/GPU 혼합 사용','최소 사양이 아닙니다','미검증','환경에 따라'); assert all(x in s for x in required)"`

Then run:

`python -c "from pathlib import Path; s=Path('README.md').read_text(encoding='utf-8'); commands=('git clone https://github.com/tmdgns104/qwen-harness-test.git','cd qwen-harness-test','python --version','git --version','ollama --version','ollama pull qwen3:8b','ollama list',r'python tools\qh.py status',r'python tools\qh.py preflight'); assert all(x in s for x in commands); assert all(x in s for x in ('Task','Allowed Changes','Forbidden Changes','Verification','Final Gate','Git commit'))"`

Then run:

`python -c "import ast; from pathlib import Path; readme=Path('README.md').read_text(encoding='utf-8'); quick=Path('docs/QUICKSTART.md').read_text(encoding='utf-8'); tree=ast.parse(Path('tools/qh.py').read_text(encoding='utf-8')); literals={n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}; assert {'status','preflight'}<=literals; assert '## Python을 어느 정도 알아야 하나요?' in quick and 'QH-LOCAL-001' in quick; assert all(x in readme for x in ('docs/QUICKSTART.md','docs/HOW_IT_WORKS.md','docs/DEVELOPMENT.md'))"`

Then run:

`python -c "from pathlib import Path; s=Path('README.md').read_text(encoding='utf-8'); forbidden=('최소 VRAM 8GB','최소 VRAM은 8GB','모든 NVIDIA GPU 지원','모든 NVIDIA GPU를 지원','Linux/macOS 완전 지원','CPU-only 완전 지원'); assert not any(x in s for x in forbidden),[x for x in forbidden if x in s]"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- README section-order, internal-link, hardware-language, command, and glossary checks exit 0.
- QUICKSTART onboarding assertions exit 0 without changing its lifecycle procedure.
- The hardware table distinguishes tested, unverified, possible, and environment-dependent claims.
- Git diff shows no Architecture, production, test, or other Task change.
- Baseline-to-implementation changed paths contain only the four Allowed paths.
- Exact implementation HEAD is used by `qh close`; all Verification commands exit 0,
  Unexpected Changed Paths is no, Diff Check is 0, and Final Gate is PASS.
- Lifecycle changes are committed separately, HARD-003 is only nominated, and final
  working tree is clean.

## Stop Conditions

STOP if completion requires:

- inventing a minimum VRAM/RAM/GPU/CPU specification or performance guarantee;
- claiming every NVIDIA GPU, CPU-only, Linux, or macOS is fully supported;
- changing Architecture, Requirements, Decisions, BACKLOG, production code, or tests;
- weakening Task scope, lifecycle, Verification, Evidence, or Final Gate guidance;
- editing another Task contract or starting another Task;
- force push, history rewrite, or changing the configured remote URL.

## Next Task

After successful lifecycle completion, nominate QH-V2-HARD-003 as PLANNED and
Human-approval-required. Do not approve or start it.

## Implementation Result

- Reordered the README opening into the approved beginner-first sequence while
  retaining the existing Why, Architecture, component, CLI, trust-model, and
  development content below it.
- Added navigation for first-time users, Architecture learners, and Repository
  developers.
- Documented the single tested Windows environment and separated it from
  unverified hardware/OS configurations and environment-dependent performance.
- Added the requested copy/paste setup commands, normal outcomes, setup-success
  checklist, limitations of `status`/`preflight`, and beginner Task terminology.
- Added the QUICKSTART Python-familiarity section and clarified that its
  QH-LOCAL-001 contract is created by the reader rather than supplied as a
  pre-existing tracked Task file.

## Verification Evidence

- `python tools\qh.py verify` executed all seven marked Verification commands;
  every command exited 0.
- README internal Repository links resolve, and the required beginner sections
  occur before the retained detailed explanation in the approved order.
- The requested setup commands and all six beginner terms are present; the
  documented `status` and `preflight` commands match the actual qh parser.
- Hardware wording includes the tested facts and explicitly rejects minimum-spec,
  universal GPU/OS/CPU-only support, and performance-guarantee interpretations.
- `git diff --check` exited 0. Git emitted only the expected Windows line-ending
  conversion notices for modified Markdown files.
- Baseline-to-current Task paths are the four Allowed paths only: `README.md`,
  `docs/QUICKSTART.md`, `STATUS.md`, and `tasks/QH-V2-DOC-002.md`.

## Conclusion

The documentation implementation is ready for its implementation commit and the
authoritative `qh close` Final Gate. QH-V2-HARD-003 remains a PLANNED candidate
requiring Human approval and has not been started.
