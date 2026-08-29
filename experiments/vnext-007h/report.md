# VNEXT-007H Evidence

## Findings

Experiment 001–003 used an explicit output instruction (return only JSON,
no explanation/markdown) and richer task/context presentation. The official
VNEXT-006/007 adapter serialized the request object but did not state that
the response must be only the Candidate JSON. The 89-character value was the
ContextPack `used_chars`; the approximately 220-character value was the
serialized `request.context_pack`, not the complete model prompt. Thus those
numbers did not prove that all task/acceptance/source/test/output-contract
content was delivered as natural-language guidance.

## A/B/C direct probe (5 distinct synthetic tasks)

| Condition | Transport | Strict JSON | Mean seconds |
|---|---:|---:|---:|
| A current official-like request | 5/5 | 0/5 | 2.740 |
| B explicit strict output prompt | 5/5 | 4/5 | 1.180 |
| C B + Ollama JSON Schema `format` | 5/5 | 5/5 | 1.110 |

Ollama 0.33.1 accepted the `format` JSON Schema on `/api/chat`. The schema
is exactly the existing Candidate contract: `operations`, exact operation
fields `operation_type`, `path`, `content`, and only CREATE_FILE/REPLACE_FILE.

## Official adapter hardening rerun

The adapter now adds the explicit strict-output instruction and the same JSON
Schema as `format`. The parser and validator were not changed. Five fresh
bounded requests produced transport 5/5, strict parse 5/5, and validator
5/5. Mean inference elapsed was 1.350 seconds and median 1.320 seconds.

No markdown extraction, repair, unknown-field tolerance, unsupported-operation
conversion, tool execution, retry, timeout, or authority change was added.

## Interpretation and gate

The evidence identifies prompt/output-contract strength as the first-order
cause, with Ollama structured output providing the most reliable additional
constraint. It does not establish a Qwen reasoning improvement or full task
correctness. The prior VNEXT-007 0/10 strict parse result remains unchanged;
the 5-task rerun is protocol-focused evidence, not a replacement of that
benchmark. A full independent correctness benchmark should precede VNEXT-008,
which remains not started and is not recommended yet solely from this rerun.

The change is limited to the bounded adapter and experiment evidence. Native
Agent, strict parsing, validation, timeout/retry, authority, and GLOBALIZATION
boundaries are unchanged.

