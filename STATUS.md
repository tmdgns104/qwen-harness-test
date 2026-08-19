Current Task: QH-V2-ARCH-002 - ACTIVE - ADR-004 / STATUS UPDATE

Previous Task: HC-007 - COMPLETE - VERIFIED - commit d6cd50b

Next Planned Task: Worker contract / backend-independent boundary, only after QH-V2-ARCH-002 completion and clean verification.

Handoff:
- QH-V2-ARCH-002 Task contract baseline commit: 06bacaf
- HC-001 through HC-007 Deterministic Harness Core remains complete and authoritative.
- ADR-004 records staged Post-HC-007 Worker Integration Architecture.
- ADR-003 Worker Adapter deferral is released only for the approved Milestone 1 sequence.
- Default local Worker direction remains native Ollama API + Qwen3:8B with initial `think:false` fast path.
- Tool permission/execution authority remains owned by deterministic Harness code.
- Qwen receives no general filesystem or shell authority.
- HC-004 remains owner of approved verification command execution.
- Retry remains bounded and above the Worker Adapter.
- Milestone 1 sequence: Worker Contract -> Native Ollama Adapter -> Harness-owned Repository Read Tools -> Harness-owned Scoped Edit Tools -> Single-Task Runner -> Bounded Retry/Safe Stop -> Minimal CLI -> E2E Regression.
- ECC routing, LangGraph orchestration, multi-agent expansion, and automatic Codex escalation remain outside Milestone 1.
- No Worker implementation begins until QH-V2-ARCH-002 is independently reviewed, committed, and the working tree is clean.
