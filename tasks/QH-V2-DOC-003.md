# QH-V2-DOC-003 - Engineering Journal, Troubleshooting, and Research Record

## Status

COMPLETE - VERIFIED

## Problem

The Repository contains extensive implementation, Verification, failure, benchmark, and Architecture Evidence, but the project history is scattered across STATUS.md, DECISIONS.md, Task files, Git history, and Evidence artifacts. A new reader cannot easily understand how the Harness evolved, which failures changed the design, or which experiments were accepted or rejected.

The Human requested a readable GitHub record covering the project from its beginning through the current QH-V2-WORKER-ROB-002 result, including troubleshooting history, development journal, and research notes.

## Goal

Create a publish-safe, beginner-readable engineering journal that reconstructs the project history from Repository Source of Truth and clearly separates verified facts, measured Evidence, decisions, failed experiments, and future work.

## Architecture Basis

- Repository documents and Git remain Source of Truth.
- ADR-001 deterministic Harness authority remains unchanged.
- ADR-011 Evidence-driven evolution and `GLOBALIZATION = NOT AUTHORIZED` remain unchanged.
- ADR-013 keeps the revoked G1 manifest historical only.
- ADR-015 preserves unsuccessful Task outcomes as Evidence rather than rewriting them as success.
- ADR-016 preserves the Worker diagnosis sequence.
- ADR-017 governs exception-driven Human supervision and does not authorize unattended automation.
- QH-V2-WORKER-ROB-002 is COMPLETE - VERIFIED and its Candidate A recommendation is Evidence only, not production promotion.

No Architecture, Requirements, Trust Boundary, Worker runtime, Verification, lifecycle, or Git authority change is authorized by this documentation Task.

## Source Rules

The documentation must be grounded primarily in tracked Repository Evidence, including as applicable:

- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `STATUS.md`
- `BACKLOG.md`
- tracked Task files under `tasks/`
- tracked Evidence under `docs/`
- Git commit history
- current production and test code only when needed to explain verified behavior

Chat history may be used only to locate likely Repository Evidence. Claims not supported by Repository Source of Truth must be omitted or explicitly labeled as historical recollection rather than verified Repository Evidence.

## Scope

Create the following documentation set:

1. `docs/PROJECT_TIMELINE.md`
   - chronological project evolution;
   - major phases, Tasks, Architecture decisions, verified milestones, failures, and performance work;
   - concise commit/Evidence references where useful.

2. `docs/DEVELOPMENT_LOG.md`
   - development journal organized by problem -> implementation -> Verification -> result;
   - explain why major changes were made, not only what changed;
   - include important lifecycle and governance evolution.

3. `docs/TROUBLESHOOTING.md`
   - practical issue index using symptom -> cause -> investigation -> resolution/disposition -> Verification/prevention;
   - include verified historical examples such as lifecycle/parser failures, Worker timeout behavior, safety failures, regression/performance bottlenecks, and unsuccessful Candidate work where Repository Evidence exists.

4. `docs/RESEARCH_LOG.md`
   - hypothesis -> experiment -> conditions -> measured result -> interpretation -> decision/next step;
   - include local Qwen/Ollama Worker experiments, tool-calling Evidence, retry/safety studies, performance measurements, WORKER-DIAG-001, and WORKER-ROB-002 where supported.

5. `README.md`
   - add a compact `Project History & Research` navigation section linking the four documents;
   - do not rewrite the whole README or change technical claims outside the navigation need.

The documents should be attractive and readable on GitHub using clear headings, compact tables, callouts, and cross-links, while avoiding decorative complexity that obscures Evidence.

## Allowed Changes

- `README.md`
- `docs/PROJECT_TIMELINE.md`
- `docs/DEVELOPMENT_LOG.md`
- `docs/TROUBLESHOOTING.md`
- `docs/RESEARCH_LOG.md`
- `STATUS.md`
- `tasks/QH-V2-DOC-003.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `tools/**`
- `tests/**`
- `experiments/**`
- `ops/**`
- any Task file other than `tasks/QH-V2-DOC-003.md`
- historical G1 manifest or its evidence
- Architecture, Requirements, Trust Boundary, Worker, Retry, Verification, Final Gate, lifecycle, Git authority, or Globalization changes
- promotion of Candidate A or any other experimental result into production behavior

## Acceptance Criteria

1. All four requested journal documents exist and are linked from README.
2. The record covers the project from early deterministic Harness work through QH-V2-WORKER-ROB-002.
3. Major claims are traceable to Repository Source of Truth rather than unsupported chat recollection.
4. Successful, unsuccessful, blocked, rejected, and diagnostic outcomes remain distinguishable.
5. `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` is never presented as PASS.
6. QH-V2-WORKER-ROB-002 accurately reports Stable 6/10 valid with 4/10 timeout, Candidate A 10/10 valid with 0/10 timeout, Candidate B 2/10 valid with 3/10 timeout, and zero executed Worker writes, matching tracked Evidence.
7. Candidate A is described only as recommended for a separate production Task, not as already integrated.
8. Troubleshooting entries include evidence-backed cause/disposition and do not invent fixes that were never implemented.
9. Research entries clearly distinguish hypothesis, measured Evidence, interpretation, and decision.
10. Historical G1 authorization remains revoked/historical.
11. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged and is not implied otherwise.
12. README changes are navigation-focused and do not alter project Architecture claims.
13. No production code, test, experiment, lifecycle implementation, or Architecture file changes occur.
14. Internal Markdown links added by this Task resolve to tracked files.
15. `git diff --check` passes.

## Verification

Run exactly:

`python -c "from pathlib import Path; required=['docs/PROJECT_TIMELINE.md','docs/DEVELOPMENT_LOG.md','docs/TROUBLESHOOTING.md','docs/RESEARCH_LOG.md']; missing=[p for p in required if not Path(p).is_file()]; assert not missing, missing; r=Path('README.md').read_text(encoding='utf-8'); assert 'Project History & Research' in r; assert all(Path(p).name in r for p in required)"`

Run exactly:

`python -c "from pathlib import Path; files=[Path('docs/PROJECT_TIMELINE.md'),Path('docs/DEVELOPMENT_LOG.md'),Path('docs/TROUBLESHOOTING.md'),Path('docs/RESEARCH_LOG.md')]; text='\n'.join(p.read_text(encoding='utf-8') for p in files); required=['QH-V2-WORKER-ROB-002','Candidate A','10/10','0/10','CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED','GLOBALIZATION = NOT AUTHORIZED','ADR-017']; missing=[x for x in required if x not in text]; assert not missing, missing"`

Run exactly:

`python -c "from pathlib import Path; import re; files=[Path('README.md'),Path('docs/PROJECT_TIMELINE.md'),Path('docs/DEVELOPMENT_LOG.md'),Path('docs/TROUBLESHOOTING.md'),Path('docs/RESEARCH_LOG.md')]; bad=[]; pat=re.compile(r'\[[^\]]+\]\(([^)]+)\)'); root=Path('.').resolve(); [bad.append((str(p),u)) for p in files for u in pat.findall(p.read_text(encoding='utf-8')) if not (u.startswith('http://') or u.startswith('https://') or u.startswith('#')) and not (p.parent/u.split('#',1)[0]).resolve().exists()]; assert not bad, bad"`

Run exactly:

`git diff --check`

Run exactly:

`git status --short`

## Evidence Requirements

Before successful close, record or demonstrate:

- the exact Repository sources used to reconstruct the timeline;
- the current WORKER-ROB-002 numbers copied from tracked Evidence;
- at least one clear unsuccessful/blocked historical example preserved without reinterpretation;
- README navigation links;
- internal-link check PASS;
- only Allowed Changes in the Task-range diff;
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS;
- separate lifecycle commit after Final Gate PASS.

## Stop Conditions

STOP for Human/ChatGPT review if documentation would require:

- changing Architecture or Requirements to make the narrative consistent;
- rewriting historical Evidence or status to improve presentation;
- treating an unsuccessful or diagnostic result as success;
- promoting Candidate A or another experiment into production;
- editing production code, tests, experiments, qh/qhops, or another Task;
- reactivating historical G1 authority;
- authorizing Globalization;
- inventing unsupported historical facts because Repository Evidence is missing.

## Next Task

No production successor is authorized by this documentation Task.

After completion, the previously recommended Candidate A production integration path remains a separate Human-governed proposal and is not started by QH-V2-DOC-003.
