# QH-V2-DOC-001 - GitHub Documentation and Publish Preparation

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Prepare Qwen Harness for its first public GitHub publication with accurate,
beginner-friendly documentation grounded in the current Repository implementation,
tests, accepted decisions, Task history, and Git Evidence.

Clearly separate implemented and verified behavior from planned or future work.
Do not change the approved Architecture or add application functionality.

## Scope

- create the GitHub landing-page README;
- create beginner Quick Start, architecture explanation, and development workflow documents;
- add publish-safe ignore rules for local environments, caches, logs, archives, and secrets;
- inspect the current Repository and Git history for high-confidence credential material without exposing values;
- verify documentation links, CLI syntax, implementation claims, Mermaid fences, and Task change scope;
- record documentation and publication-preparation Evidence in the current Task and `STATUS.md`;
- prepare the completed local history for the separately authorized GitHub remote and push steps.

`ARCHITECTURE.md` and `AGENTS.md` do not currently exist in the Repository.
This Task must not invent them. Accepted Architecture is documented from
`DECISIONS.md`, supported by `PROJECT.md`, `REQUIREMENTS.md`, implementation,
tests, completed Tasks, and Git history.

## Allowed Changes

- `README.md`
- `docs/QUICKSTART.md`
- `docs/HOW_IT_WORKS.md`
- `docs/DEVELOPMENT.md`
- `.gitignore`
- `STATUS.md`
- `tasks/QH-V2-DOC-001.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `AGENTS.md`
- `tools/**`
- `tests/**`
- `src/**`
- other Task files
- Repository fixture files
- Worker, Runner, Retry, Repository-tool, Verification, Evidence, or Final-Gate behavior
- Git history rewriting or force push
- unrelated files

## Acceptance Criteria

1. `README.md` explains the purpose, motivation, trust model, architecture,
   implemented features, planned work, requirements, Quick Start, CLI, Task flow,
   current status, and Source-of-Truth links for a beginner.
2. `docs/QUICKSTART.md` gives a command-by-command first-run workflow with meaning,
   expected result, and troubleshooting guidance.
3. `docs/HOW_IT_WORKS.md` accurately explains Qwen, Ollama, Harness, Worker,
   Runner, tool calls, scope, Git Evidence, Verification, Final Gate, and Retry.
4. `docs/DEVELOPMENT.md` documents the Repository's approved
   Problem -> Requirements -> Architecture -> Task -> Implementation -> Verification workflow.
5. Every documented `qh` command matches the actual parser and behavior in
   `tools/qh.py`.
6. Implemented claims are supported by current code/tests/completed Task or Git
   Evidence; planned/future behavior is visibly separated.
7. README-relative links resolve to existing Repository paths; missing
   `ARCHITECTURE.md` and `AGENTS.md` are not linked as if they exist.
8. Mermaid blocks have balanced fences and use straightforward GitHub-supported syntax.
9. `.gitignore` covers local Python environments, caches, environment files,
   coverage, logs, and zip archives without ignoring required tracked files.
10. A high-confidence secret scan of the current tree and reachable Git history
    reports no credential value suitable for public misuse, or the Task stops
    with filenames/types only.
11. Existing deterministic Harness/Worker/Runner regression tests selected by
    this Task remain PASS.
12. `git diff --check` passes and all changed paths remain inside Allowed Changes.
13. No Architecture, Requirements, Decisions, application behavior, or forbidden
    file changes occur.

## Verification

Run exactly:

`python -c "import re; from pathlib import Path; required=tuple(Path(p) for p in ('README.md','docs/QUICKSTART.md','docs/HOW_IT_WORKS.md','docs/DEVELOPMENT.md','.gitignore')); assert all(p.is_file() for p in required); text=Path('README.md').read_text(encoding='utf-8'); links=[value.split('#',1)[0] for value in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text) if not value.startswith(('http://','https://','#'))]; assert all((Path('README.md').parent / value).exists() for value in links if value), links"`

Then run:

`python -c "import ast; from pathlib import Path; docs='\n'.join(Path(p).read_text(encoding='utf-8') for p in ('README.md','docs/QUICKSTART.md')); tree=ast.parse(Path('tools/qh.py').read_text(encoding='utf-8')); commands=('status','preflight','verify','review','start','close','run'); literals={node.value for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str)}; assert set(commands) <= literals; assert all(('qh.py '+name) in docs for name in commands)"`

Then run:

`python -c "from pathlib import Path; paths=('README.md','docs/QUICKSTART.md','docs/HOW_IT_WORKS.md','docs/DEVELOPMENT.md'); texts=tuple(Path(p).read_text(encoding='utf-8') for p in paths); assert all(text.count('```') % 2 == 0 for text in texts); assert sum(text.count('```mermaid') for text in texts) >= 2"`

Then run:

`python -m unittest tests.test_qh tests.test_harness_core tests.test_qh_worker_run tests.test_retry_runner tests.test_task_runner tests.test_ollama_worker tests.test_repo_tools`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Conditions

STOP if completion requires:

- changing Architecture, Requirements, or Decisions;
- creating an `ARCHITECTURE.md` or `AGENTS.md` from assumptions;
- modifying application code or tests;
- documenting planned behavior as implemented;
- exposing a secret value in output or documentation;
- modifying a tracked file that must instead remain publishable;
- changing an existing Git remote URL without Human direction;
- force push, history rewrite, or destructive Git recovery;
- starting another Task.

## Implementation Result

- Added a beginner-facing GitHub landing page in `README.md` with the project
  purpose, trust model, execution/completion architecture, implemented versus
  Planned behavior, requirements, CLI reference, Task lifecycle, current status,
  and links to existing Source-of-Truth documents.
- Added `docs/QUICKSTART.md` with a command-by-command Windows PowerShell
  walkthrough, expected results, troubleshooting, explicit commit boundaries,
  and the ADR-007 single authoritative final Verification path.
- Added `docs/HOW_IT_WORKS.md` explaining the Model, Ollama, Harness, Adapter,
  Worker, Runner, Tool Call, scope, Git Evidence, Verification, Final Gate, and
  bounded Retry roles without giving Qwen shell, Git, or PASS authority.
- Added `docs/DEVELOPMENT.md` documenting the approved
  Problem -> Requirements -> Architecture -> Task -> Implementation ->
  Verification workflow and Architecture-change stop procedure.
- Added `.gitignore` rules for Python caches, local environments, environment
  files, coverage, logs, archives, temporary files, and operating-system metadata.
- Did not create the absent `ARCHITECTURE.md` or `AGENTS.md` files. The
  documentation identifies `DECISIONS.md` Accepted ADRs as the current
  Architecture authority.
- No production code, tests, Requirements, Decisions, Architecture, or unrelated
  Task files were changed.

## Verification Evidence

- Task Verification document/link, CLI-source, and Markdown/Mermaid structural
  commands: all exit 0.
- README and detailed-document relative links: 24 checked, all resolve.
- Mermaid blocks: 7 checked for balanced fences and supported top-level static
  structure; no obvious syntax error found. No renderer-based visual claim is made.
- Selected lifecycle, Verification, Worker, Runner, Retry, Ollama, and
  Repository-tool regression suite: 217 PASS in 311.400 seconds.
- High-confidence credential scan: no private key, token, credential assignment,
  embedded URL credential, authorization credential, JWT, or service-account
  marker found in the current publish tree or 236 reachable pre-publication commits.
- Local `.pytest_cache/` is untracked and ignored. Its contents could not be
  enumerated because of an existing ACL denial; it is not part of the publish set.
- One existing Git author email may be personal public metadata. No value was
  printed, it is not a credential, and history rewriting is Forbidden for this Task.
- `.gitignore` representative-rule checks PASS; `.env.example` remains
  includable; no tracked file conflicts with the ignore rules.
- `ollama pull` and `ollama list` are supported by the installed Ollama CLI;
  the Repository still pins no Ollama version.
- `git diff --check`: PASS.
- Task-range changed paths: exactly the seven Allowed Changes; no unexpected path.
- The known three QH-V2-MD-001 RED fixture failures are outside this Task and are
  not represented as a green full-discovery result.

## Conclusion

All pre-commit QH-V2-DOC-001 acceptance checks pass. The documentation
implementation commit may proceed; `qh close` remains the authoritative final
Verification and lifecycle gate.
