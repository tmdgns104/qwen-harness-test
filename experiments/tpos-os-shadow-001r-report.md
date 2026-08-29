# TP-OS-SHADOW-001R Evidence

One actual Qwen3:8B inference completed in 9.336 seconds. The Candidate used
the authorized path `app/conversation.py` and passed the existing Validator,
but selected `REPLACE_FILE` instead of the requested `REPLACE_TEXT`. The
isolated apply therefore succeeded under the existing REPLACE_FILE semantics;
this is not a valid partial-edit success and was classified `WRONG_OPERATION`.

No independent semantic test was promoted from this run because the requested
operation contract was not met. The full raw Candidate/metadata is in
`experiments/result.json`; the Target status was unchanged except for the
pre-existing untracked zip. No retry, repair, or Target write occurred.

Compared with the prior REPLACE_FILE timeout, this run demonstrates that the
new schema/parser path can return a bounded response, but it does not yet
demonstrate REPLACE_TEXT generation reliability or semantic correctness.
