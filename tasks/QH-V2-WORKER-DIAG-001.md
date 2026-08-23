# QH-V2-WORKER-DIAG-001 - Worker Runtime and Global-Use Configuration Diagnosis

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

Recent real Worker execution produced two distinct concerns that must be separated before any implementation change:

1. During QH-V2-LIFECYCLE-001, short native Ollama requests remained responsive while the full Task prompt repeatedly reached the current 30-second Worker timeout.
2. The Repository is intended for later global/cross-Repository use, but runtime code currently contains fixed defaults and policy constants such as the Ollama endpoint, default model, timeout, thinking mode, Worker step budget, and Retry attempt budget. Some of these may be valid Architecture defaults, while others may become portability/configuration blockers.

Changing these values before diagnosing their role would mix Evidence collection with implementation and could accidentally weaken safety policy.

## Goal

Produce objective Evidence that answers both questions:

- What actually causes or correlates with the long/full-Task-prompt Worker timeout behavior?
- Which hard-coded values in tracked runtime/operations code are environment-specific configuration, tunable policy, safety-critical constants, or harmless protocol/schema constants for future global use?

This Task is diagnosis and classification only. It does not change Worker, Runner, Retry, model, configuration, lifecycle, tool authority, Verification, Final Gate, or global-use behavior.

## Architecture Basis

- ADR-002 keeps the Worker backend independent and currently uses native Ollama + Qwen3:8B as the default local path.
- ADR-009 owns bounded Retry and safe-stop semantics.
- ADR-011 keeps Globalization NOT AUTHORIZED and requires Evidence-first improvement.
- ADR-015 preserves truthful unsuccessful Task closure.
- ADR-016 explicitly selects Worker diagnosis before Operations resume and makes any repair Task conditional on diagnostic Evidence and Human review.
- Existing deterministic safety boundaries remain authoritative while diagnosis is performed.

## Diagnostic Scope

### A. Worker Runtime Timing / Timeout Diagnosis

Collect bounded repeated observations for at least these cases using the current Stable implementation and current local Ollama environment:

1. short prompt, no tools;
2. short prompt, current Worker tool schema;
3. representative full Task prompt, no tools;
4. representative full Task prompt, current Worker tool schema.

For each case record at minimum:

- exact prompt source or reproducible description;
- tool exposure state;
- model;
- think setting;
- timeout value;
- run count;
- elapsed time per run;
- success / timeout / transport failure classification;
- whether any Repository write was attempted;
- relevant Ollama response timing/token metadata if available without changing production code.

The experiment must be bounded. Do not repeatedly increase timeout, prompt complexity, model size, retry count, or reasoning mode until something passes.

### B. Global-Use Hard-Coding Inventory

Inspect tracked runtime and operations code, including at least `tools/**` and `ops/qhops/**`, for literals or assumptions that could affect use on another Repository, machine, model, Ollama installation, branch, remote, or operating environment.

Classify each relevant finding into exactly one of these categories:

1. **Environment configuration** - machine/service/repository dependent and likely should be externally configurable.
2. **Tunable runtime policy** - legitimate default but may need explicit configuration or override after Evidence.
3. **Safety-critical policy constant** - intentionally fixed by Accepted Architecture unless a later ADR changes it.
4. **Protocol/schema constant** - stable identifier/contract value that should normally remain fixed.
5. **Test/documentation fixture only** - not a production portability blocker.

The inventory must specifically review, but is not limited to:

- Ollama base URL / port;
- default model;
- timeout;
- think mode;
- Worker step budget;
- Runner Retry attempt budget;
- Repository paths and absolute-path assumptions;
- usernames or machine-specific directories;
- remote/branch names;
- current Repository name assumptions;
- Windows-only command assumptions;
- tool names and lifecycle/status strings where relevant.

For every finding record:

- file and symbol/location;
- current literal/default;
- classification;
- global-use impact;
- whether change is recommended;
- suggested future configuration source or Architecture treatment;
- whether changing it would require a new ADR or only a normal implementation Task.

## Scope

- Run read-only diagnostic experiments against the current Stable Worker path.
- Inspect tracked code for global-use hard-coding and portability assumptions.
- Create one Evidence report at `docs/WORKER_DIAG_001_EVIDENCE.md`.
- Record a conclusion that distinguishes diagnosis from proposed implementation.
- Recommend one of these dispositions for Human review:
  - no Worker/config implementation change justified;
  - QH-V2-WORKER-ROB-002 justified;
  - a separate configuration/portability Task is justified;
  - both are justified as separate Tasks;
  - Architecture review required before any change.

## Allowed Changes

- `docs/WORKER_DIAG_001_EVIDENCE.md`
- `STATUS.md`
- `tasks/QH-V2-WORKER-DIAG-001.md`

## Forbidden Changes

- all production code
- all tests
- all Worker/model/backend/prompt implementation files
- all Runner/Retry/Repository-tool implementation files
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- all other Task files
- `ops/qhops/**`
- configuration implementation
- model/routing/timeout/think/step/retry behavior changes
- lifecycle, Verification, Final Gate, Git, tool authority, or automatic-successor behavior changes

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. `docs/WORKER_DIAG_001_EVIDENCE.md` contains reproducible bounded Worker timing/timeout Evidence for the four required prompt/tool cases.
2. The Evidence clearly separates transport timeout behavior from Repository Task PASS/FAIL.
3. The Evidence records whether any write attempt occurred; diagnostic experiments must not intentionally mutate Repository content.
4. The Evidence contains a tracked-code hard-coding inventory with the five required classifications.
5. Ollama URL, model, timeout, think mode, Worker step budget, Retry attempt budget, Repository path assumptions, branch/remote assumptions, and Windows assumptions are each explicitly reviewed.
6. Machine/user/repository-specific absolute paths are either identified or explicitly reported absent from tracked runtime/operations code based on search Evidence.
7. Safety-critical constants are not automatically converted into configuration merely because they are literals.
8. The conclusion identifies which findings are genuine global-use blockers versus acceptable defaults/contracts.
9. Any proposed Worker repair, configuration extraction, policy tuning, or Architecture change is deferred to a separate Human-reviewed Task/ADR as applicable.
10. No production code, test, Worker/Runner/Retry behavior, or Architecture authority changes occur in this Task.
11. QH-V2-WORKER-ROB-001 remains `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` and is not reinterpreted as successful Evidence.
12. No successor is automatically created or started after completion.

## Verification

Run exactly:

`python -c "from pathlib import Path; p=Path('docs/WORKER_DIAG_001_EVIDENCE.md'); assert p.is_file(); s=p.read_text(encoding='utf-8'); required=['Worker Timing / Timeout Evidence','Global-Use Hard-Coding Inventory','Environment configuration','Tunable runtime policy','Safety-critical policy constant','Protocol/schema constant','Test/documentation fixture only','Ollama','timeout','think','Worker step budget','Retry attempt budget','Repository path','branch','remote','Windows','Conclusion / Human Review Disposition']; missing=[x for x in required if x not in s]; assert not missing, missing"`

Then run:

`python -c "from pathlib import Path; s=Path('STATUS.md').read_text(encoding='utf-8'); assert 'Current Task: QH-V2-WORKER-DIAG-001 - ACTIVE' in s; d=Path('docs/WORKER_DIAG_001_EVIDENCE.md').read_text(encoding='utf-8'); assert 'production behavior changed' not in d.lower()"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Preserve the exact commands or sufficiently reproducible procedures used for each diagnostic run.
- Record run counts and observed elapsed times rather than only a narrative summary.
- Record the current Stable values observed in source for model/base URL/timeout/think/step/retry without changing them.
- Include search Evidence for machine-specific absolute paths, Repository-name assumptions, branch/remote literals, and Windows-specific assumptions.
- Distinguish tests/docs fixtures from production/operations blockers.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Human review determines whether a later implementation Task is justified.
- Exact implementation HEAD is used by normal `qh close`; Final Gate PASS is required for this diagnostic documentation Task.
- Lifecycle close commit is separate and final working tree is clean.

## Stop Conditions

STOP if diagnosis requires:

- changing Worker timeout, model, think mode, prompt, tool schema, step budget, or Retry budget;
- changing production configuration behavior;
- adding shell/Git/network/filesystem authority;
- weakening or bypassing deterministic SAFETY, Verification, Evidence, or Final Gate behavior;
- treating longer timeout alone as proof of a correct fix;
- converting a safety-critical constant into user configuration without Architecture review;
- changing queue order, PROJECT, REQUIREMENTS, DECISIONS, or BACKLOG;
- automatically creating or starting QH-V2-WORKER-ROB-002 or any configuration Task.

## Next Task

Human review required after Evidence is COMPLETE - VERIFIED.

Possible follow-up Tasks are conditional on the Evidence and are not authorized by this contract. QH-V2-OPS-003 remains deferred until the Worker diagnostic path reaches a Human-reviewed disposition under ADR-016.
