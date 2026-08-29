# TP-OS-SHADOW-001 Evidence

## Scope

Harness repository: `D:\qwen-harness-test`

Target repository: `D:\team_project_os\team_project_os-main`

Target baseline: `3c05219d50a51f2bdad8e6671e702e8c5d575e50`

The target had one pre-existing untracked artifact, `team_project_os-main.zip`.
Its status was identical before and after the run.

## Worker result

One actual Qwen3:8B inference was attempted using the frozen bounded adapter,
exact authorized path `app/conversation.py`, target state EXISTS/REPLACE_FILE,
and source plus existing test context. The Ollama call timed out at the
production adapter timeout of 30.052 seconds. No Candidate was produced, so
Validator, Snapshot Apply, and semantic verification were not reached.

- Candidate: none
- Validator: not reached
- Snapshot Apply: not reached
- Independent semantic verification: not reached
- Existing Team Project OS regression: not run
- First-pass success: false
- Classification: `PERFORMANCE` / transport timeout
- Retry: none
- Original target mutation: none (pre-existing zip status unchanged)
- False COMPLETED: none

The run is not a Qwen semantic correctness result. The full source/test
Context and raw failure metadata are preserved in
`tpos-os-shadow-001-result.json`. No target repository write or branch/merge
was attempted.

