# Qwen Harness VNext Architecture

## Scope and invariants

VNext adds `bounded_stateless` beside the existing `native_agent` mode. Native Ollama tool sessions remain available and unchanged. Local Workers never receive filesystem, Git, shell, or direct write authority. `GLOBALIZATION = NOT AUTHORIZED`.

## Flow

Codex Supervisor → Task Contract → deterministic Harness → Context Pack Builder → bounded stateless Worker → Structured Candidate → Candidate Validator → temporary snapshot apply → focused/regression verification → diff/scope/evidence → Codex Final Gate.

The original Team Project OS remains an external, read-only source. A pilot uses a fresh isolated snapshot; only a Codex-approved final gate may promote a candidate to a real branch.

## Bounded stateless contract

`WorkerRequest` contains `task`, `context_pack`, and `output_contract`. `WorkerResponse` contains `transport_ok`, `candidate`, `error`, and metadata. Each request is self-contained; the Worker cannot ask for more context or invoke tools.

The candidate representation is a structured list of file operations (`create_file`, `replace_file`, or `patch`) plus optional `test_candidate`. Unified diff is not accepted as authority by itself; the validator parses operations into an explicit schema before any apply. The candidate is only a proposal.

## Smart Worker, Bounded Authority

`bounded_stateless` does not mean a deliberately weak code generator. The Worker may use the maximum practical software-engineering capability available on the target hardware (RTX 5070 Laptop, 8GB VRAM, 32GB RAM): interpret requirements, understand supplied code and Architecture, compare implementation strategies, plan multi-file changes, generate code/tests, review its own Candidate, and reason from prior failure Evidence. Its boundary is authority, not intelligence.

The Worker may not explore a Repository, read files outside the Context Pack, access a filesystem, run Git/shell/tests, modify files, or apply its own Candidate. Harness exclusively owns Repository access, context selection, schema/scope/path validation, temporary apply, test execution, diff verification, retry state, failure Evidence, and final Verdict. `stateless` means the Worker owns no durable Repository or Task state; Harness may retain and supply bounded Task state.

Retries are stateful at the Harness layer: `Task + Context Pack → Candidate A → apply/test → Failure Evidence`, then `Task + Context Pack + Failure Evidence → Candidate B`. Failure Evidence is bounded, explicit input and never grants additional authority.

Qwen3:8B remains the practical baseline. Larger models require benchmark evidence of meaningful accuracy improvement plus acceptable latency and memory on the target hardware.

## Context pack

The pack includes Task ID, goal, acceptance criteria, allowed/forbidden paths, bounded file excerpts, relevant tests, approved Architecture/Decision excerpts, and the output contract. Selection is deterministic from the Task manifest. A byte/token budget is mandatory; overflow fails closed with a recorded reason rather than truncating arbitrary content.

## Validation and apply

Before apply, deterministic validation checks schema, path normalization/traversal, allowed and forbidden scope, lifecycle-control files, file count and byte limits, and rejects delete/unexpected operations. Valid candidates apply only to a temporary snapshot. Focused tests, regression tests, Git diff, scope, and evidence are authoritative; Worker claims are not.

## Outcomes

The bounded runner distinguishes `COMPLETED`, `NO_ACTION`, `CANDIDATE_INVALID`, `VERIFICATION_FAILED`, `SAFETY_FAIL`, `TRANSPORT_FAIL`, `PERFORMANCE_FAIL`, and `BLOCKED`. Existing native mode outcomes and behavior remain backward compatible.

## Evidence/training boundary

Evidence stores contract identity, context metadata (not unrestricted repository data), candidate, validator result, test results, diff summary, verdict, and Codex correction reference. Sensitive or unnecessary repository content is excluded by construction.
