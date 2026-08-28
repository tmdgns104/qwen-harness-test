# TPOS-V016-REG-002 - Explicit Ref-Identity Rebase Conflict Regression

The original tracked Task remains the Source of Truth. This Worker Brief grants no authority beyond the original Task. Verification and Final Gate remain Harness-owned.

## Goal

Add one new deterministic `unittest` module that directly proves
`rebase_conflicts`:

1. returns the exact conflict path for a human edit and incoming delta targeting
   the same stable requirement identity; and
2. does not report a false conflict when the human edit targets a different
   stable requirement identity.

This is a test-only successor Pilot. Production behavior must not change.

## Architecture Basis

- The approved V0.16 single-process FastAPI + SQLite architecture is unchanged.
- `rebase_conflicts` remains the production implementation under test.
- Codex is Supervisor and Final Verifier.
- Qwen is a bounded test author, not a semantic Reviewer or Final Verifier.
- Harness `NORMAL` is interaction status only, never Task PASS.
- No Architecture, authentication, security, migration, production, tool
  authority, write scope, model, think, retry, timeout, or step-budget change is
  authorized.
- GLOBALIZATION remains NOT AUTHORIZED.

## Dependencies

- Verified dirty-tree baseline: 64/64 Python tests PASS.
- Baseline tracked diff patch-id:
  `c5127f54e22bca84e37c0d4f2282300f08dae128`.
- Preserved snapshot commit:
  `fbb0665404c9a7218f26de556d7a917954f7c49a`.
- Previous unsuccessful Pilot Evidence commit:
  `d203ab5b6b09ee6185b2995e68130d391e59356a`.

Authoritative source semantics inspected by the Supervisor:

- `app/structured_state_v016.py` imports `CATEGORY_SPECS` from
  `app.conversation_import`.
- `app/conversation_import.py` defines the requirements entry exactly as
  `"requirements": ("ref", "REQ", ("title", "detail"))`.
- Therefore the stable identity field for the `requirements` category is
  exactly `ref`, not `id`.
- `rebase_conflicts` obtains `id_field` from `CATEGORY_SPECS`, indexes base and
  current items by that field, and emits `f"{category}.{incoming[id_field]}"`.

## Scope

Required Worker protocol:

1. The first Worker step requests exactly one `read_repo_text` for
   `app/structured_state_v016.py`.
2. Analyze only the `rebase_conflicts` behavior described by this contract.
3. A later Worker step requests exactly one `write_repo_text` for
   `tests/test_structured_state_v016_ref_identity.py` containing the complete
   test module.
4. Never emit more than one ToolRequest in one Worker step.
5. Do not request shell, Git, network, another file, or an external path.

Identity contract — no inference is required:

- For `requirements`, use the dictionary key `ref` as the stable identity.
- Every requirement fixture in `base`, `current`, and `delta` must use `ref`.
- Do not use `id` as a requirement identity key.
- Confusing `id` with `ref` is an Acceptance failure even if a test happens to
  pass.

Exact positive fixture shape:

```python
base = {
    "requirements": [
        {
            "ref": "REQ-HUMAN-001",
            "title": "Baseline requirement",
            "detail": "Original detail",
        }
    ]
}
current = {
    "requirements": [
        {
            "ref": "REQ-HUMAN-001",
            "title": "Human-edited requirement",
            "detail": "Official human edit",
        }
    ]
}
delta = {
    "requirements": [
        {
            "ref": "REQ-HUMAN-001",
            "title": "Incoming AI proposal",
            "detail": "Proposed overwrite",
        }
    ]
}
```

The positive test must call `rebase_conflicts(base, current, delta)` and assert
exactly:

```python
["requirements.REQ-HUMAN-001"]
```

Exact negative behavior:

- `base` contains `REQ-HUMAN-001` and `REQ-HUMAN-002` using `ref`.
- `current` leaves `REQ-HUMAN-001` unchanged and human-edits only
  `REQ-HUMAN-002`.
- `delta` targets only `REQ-HUMAN-001`.
- The exact result must be `[]`.

The module must use Python `unittest`, small in-memory dictionaries, and no
filesystem, database, subprocess, network, timing, or random behavior.

## Allowed Changes

- tests/test_structured_state_v016_ref_identity.py

## Forbidden Changes

- app/**
- local_bridge/**
- tools/**
- all existing tests/**
- STATUS.md
- tasks/**
- README.md
- requirements.txt
- project_os.db
- any external path
- Architecture or Requirements changes
- authentication, security, permission, migration, production, tool-authority,
  model, think, retry, timeout, or step-budget changes
- Globalization approval

All unlisted paths are default-denied.

## Acceptance Criteria

1. The Worker creates only
   `tests/test_structured_state_v016_ref_identity.py`.
2. The first Worker request is the required source read.
3. No Worker step contains multiple ToolRequests.
4. The test imports `rebase_conflicts` from
   `app.structured_state_v016` and exercises that real function.
5. Every requirement fixture uses `ref`; no requirement fixture uses `id`.
6. The positive fixture has the exact minimum shape and exact values specified
   in this contract.
7. The positive assertion is exactly
   `["requirements.REQ-HUMAN-001"]`.
8. The negative fixture changes only the different identity
   `REQ-HUMAN-002` in `current`, targets `REQ-HUMAN-001` in `delta`, and asserts
   exactly `[]`.
9. Focused Verification passes.
10. Existing V0.16 tests and the full Python regression remain passing.
11. Diff and scope review show no production or existing-test mutation.
12. Codex independently reviews the test source, assertions, diff, scope, and
    actual exit codes before any PASS classification.

## Stop Conditions

Stop without repair, retry, or scope expansion if:

- Qwen requests an unauthorized path or tool;
- Harness returns FAIL, BLOCKED, or SAFETY;
- any unexpected path changes;
- any requirement fixture uses `id` instead of `ref`;
- focused or regression Verification fails;
- production implementation or an existing test must change;
- Architecture, Requirements, authentication, security, permissions, migration,
  authority, model, think, retry, timeout, step budget, or Globalization must
  change;
- the test is weak, tautological, nondeterministic, or does not exercise the
  real `rebase_conflicts` function.
