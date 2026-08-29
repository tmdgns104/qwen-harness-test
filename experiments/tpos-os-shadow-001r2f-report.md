# TP-OS-SHADOW-001R2F — Forensic result

## Findings

The R2 run did not hit an HTTP timeout. `call_bounded_stateless_worker()` was
invoked with `timeout_seconds=30`, and its `urlopen(..., timeout=30)` completed
with HTTP/JSON transport success. The response was then rejected by the
strict parser with `ValueError: invalid Candidate operation schema`.

The parser currently checks `set(raw) == {operation_type, path, content}`
before branching on `REPLACE_TEXT`. A valid REPLACE_TEXT response instead has
`{operation_type, path, old_text, new_text, expected_occurrences}`, so every
REPLACE_TEXT response is deterministically rejected. This explains the R2
"no Candidate" result and its misleading upper-level timeout label.

## Timeout chain

| Component | Configured/used |
|---|---:|
| bounded adapter default | 30.0 s |
| R2 call argument | 60.0 s in the R2 runner |
| HTTP `urlopen` in R2 runner | 60.0 s |
| forensic minimal probe | 30.0 s |
| outer subprocess | none |

The forensic calls completed in 1.236 s (minimal) and 14.450 s (R2 replay).
Both returned `transport_ok=true`, `parse_ok=false`; no socket/read timeout,
HTTP error, or missing response occurred. Raw response body was decoded by the
adapter (the parser error proves `message.content` was present), but raw body
is not retained by the current adapter.

## Schema and probes

The inspected schema contains three branches (CREATE_FILE, REPLACE_FILE,
REPLACE_TEXT), 848 compact JSON characters before dynamic filtering; the
REPLACE_TEXT branch requires `path`, `old_text`, `new_text`, and
`expected_occurrences=1`. The dynamic operation filter was not the failure:
the model response reached parsing and was rejected by the unconditional
legacy key check.

Minimal REPLACE_TEXT probe: 1.236 s, transport success, no Candidate, parser
failure `invalid Candidate operation schema`.

R2 replay: 14.450 s, transport success, no Candidate, same parser failure.

## Classification and action boundary

Primary root cause: `ADAPTER_PARSER_BUG` (not an Ollama server timeout,
context-generation timeout, or production timeout mismatch). The previous R2
`TRANSPORT_TIMEOUT` label should be treated as historical misclassification;
it is preserved, not rewritten. Correcting the parser and retaining raw
transport diagnostics requires a separate hardening change and is not applied
in this forensic task.

No target repository was modified. No retry, repair, schema relaxation,
operation conversion, or timeout change was performed.
