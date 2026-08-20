Current Task: QH-V2-HARD-001 - COMPLETE - VERIFIED - commit e4ba45c

Previous Task: QH-V2-E2E-001 - COMPLETE - VERIFIED - commit d9d095d

Next Planned Task: Verification Contract Fail-Closed Hardening - TASK NOT YET CREATED
Task Baseline: 17bac01fc0cc2d15f37e0ffef4d55d78bea7198b

Handoff:
- QH-V2-RUN-001A implementation commit 80cdfff adds frozen backend-neutral ToolSpec, ToolRequest, ToolResult, and WorkerStep records.
- Existing WorkerRequest and WorkerResponse contracts remain unchanged.
- QH-V2-RUN-001A Verification Evidence: focused RED confirmed missing records; focused GREEN PASS; WorkerStep PASS; full tests.test_harness_core 114 PASS; git diff --check PASS.
- ADR-008 accepted: backend-neutral ToolSpec / ToolRequest / ToolResult / WorkerStep semantics define the tool-enabled Worker boundary.
- QH-V2-WC-001 WorkerRequest and WorkerResponse remain unchanged; Ollama-native tool_calls stay inside the Adapter.
- Single-Task Runner owns the deterministic tool continuation loop; initial Worker tools are limited to read_repo_text and write_repo_text.
- Qwen cannot supply write scope; Runner injects the current Task Allowed/Forbidden scope into the Harness-owned edit tool.
- Initial Runner step policy: zero or one ToolRequest per Worker step; multiple, malformed, unknown, or unauthorized requests fail closed.
- Tool interaction requires a finite step budget; exact limit is deferred to the separately approved Runner implementation Task. Retry remains later.
- QH-V2-ARCH-002 Task contract baseline commit: 06bacaf
- HC-001 through HC-007 Deterministic Harness Core remains complete and authoritative.
- ADR-004 records staged Post-HC-007 Worker Integration Architecture.
- ADR-003 Worker Adapter deferral is released only for the approved Milestone 1 sequence.
- Default local Worker direction remains native Ollama API + Qwen3:8B with initial `think:false` fast path.
- Tool permission/execution authority remains owned by deterministic Harness code.
- Qwen receives no general filesystem or shell authority.
- HC-004 remains owner of approved verification command execution.
- Retry remains bounded and above the Worker Adapter.
- Milestone 1 remaining sequence now includes: Harness-owned Scoped Edit Tools -> Pre-Runner Safety/UX Review -> Single-Task Runner -> Bounded Retry/Safe Stop -> Minimal CLI -> E2E Regression.
- Post-Milestone 1 Hardening & UX Improvement review follows successful E2E Regression.
- Pre-Runner performance decision: remove redundant standalone Full Verification from the normal final workflow; explicit `qh.py close <HEAD>` remains authoritative because it runs review, full Verification, Scope Evidence, and Final Gate before close.
- Development loops should use focused tests; parallel Verification and stale-safe Evidence reuse remain follow-up candidates.
- QH-V2-PERF-001 measured parallel Verification at 137.55s versus a 138.45s sequential baseline (~0.7% improvement); concurrent suites slowed materially, so Verification concurrency is rejected for the current workload.
- Next performance candidate: profile tests.test_qh Git/subprocess/temporary-repository cost before considering further execution-level optimization.
- QH-V2-PERF-002 profiling found repeated Git/test-fixture process creation is the dominant tests.test_qh bottleneck: common setUp alone executes 8 Git commands per test, at least 176 Git subprocesses across 22 tests.
- A simple status test spent ~61% of runtime in common setUp; the slow close profile used 17 subprocesses, including 16 Git calls.
- Recommended next optimization: preserve per-test isolation while replacing repeated Repository construction with independent copies of a prebuilt seed test Repository.
- QH-V2-EDIT-002 resolved the remaining Pre-Runner scope-engine mismatch in implementation commit 5151777.
- write_repo_text now delegates authorization to Harness Core ChangeScope + is_path_allowed; recursive allow and forbidden-first semantics are shared with final review.
- Verification: tests.test_repo_tools 15 PASS, tests.test_harness_core 109 PASS.

- QH-V2-PERF-003 implemented isolated seed Repository fixtures in commit 7a8a5f6 with no production-code changes.
- tests.test_qh improved from 90.110s to 46.899s for 22 tests, approximately 48% faster.
- Isolation probe PASS; tests.test_qh 22 PASS, tests.test_harness_core 109 PASS, tests.test_repo_tools 13 PASS.
- ECC routing, LangGraph orchestration, multi-agent expansion, and automatic Codex escalation remain outside Milestone 1.
- QH-V2-ARCH-002 Architecture review completed and committed: 13b9077.
- Working tree was clean after Architecture commit.
- QH-V2-WC-001 Worker Contract Task baseline commit: 241bcbc.
- QH-V2-WC-001 Worker Contract implementation completed and verified: 2ee6119.
- Native Ollama Worker Adapter remains NOT STARTED.
- Human requested prioritizing repetitive workflow automation before the Native Ollama Worker Adapter.
- Architecture/task sequencing must be adjusted before automation implementation begins.

- QH-V2-ARCH-003 Task baseline commit: 1dc953e.
- ADR-005 workflow automation priority decision completed and committed: 1233379.
- QH-V2-AUTO-001 Task baseline commit: d1e215c.
- QH-V2-AUTO-001 implementation completed through final implementation commit: f8d6280.
- Automation V1 commands implemented: status, preflight, verify, review.
- QH-V2-AUTO-001 focused Verification: 7 tests PASS.
- Harness Core regression: 109 tests PASS.
- Final qh review: Final Gate PASS; unexpected changed paths none.
- Working tree clean after final Verification.
- QH-V2-OWA-001 Task baseline commit: e334135.
- Native Ollama Worker Adapter is now the active Task.
- Repository read/edit tools, Runner, and retry remain NOT STARTED.
- Native Ollama Worker Adapter implementation completed and verified: 66405cd.
- Focused Adapter tests: 6 PASS.
- Harness Core regression: 109 PASS.
- Real local Ollama qwen3:8b smoke: transport_ok=True, non-empty output, error=None.
- Final qh review: Final Gate PASS; unexpected changed paths none.
- Task-range changed files stayed within Allowed Changes.

- QH-V2-AUTO-002 Task baseline commit: 82d15af.
- Deterministic Task Lifecycle Assistance is now the active Task.
- Harness-owned Repository Read Tools remains NOT STARTED.
- This is the final manually prepared Task-start transition before lifecycle assistance is implemented.

Improvement Checkpoints:
- QH-V2-AUTO-002 Task lifecycle automation is implemented; the earlier lifecycle candidate is resolved.
- QH-V2-AUTO-004 Task-range scope review is implemented; the earlier range-review candidate is resolved.
- Pre-Runner Safety/UX Review is required before Single-Task Runner and will classify baseline automation, scope-evaluation unification, and the remaining known candidates.
- Post-Milestone 1 Hardening & UX Improvement follows E2E Regression and will revisit CMD simplification, qh doctor, qh status UX, Task scaffolding, Worker smoke standardization, and any new repeated Evidence.
- Continue to defer automatic commit, automatic Task completion, automatic Architecture modification, automatic next-Task start, and RED/GREEN semantic judgment automation. Human approval remains authoritative.
- QH-V2-PRR-001 review result: Single-Task Runner is BLOCKED until Task baseline lifecycle/review integration and Repository Edit Tool scope-engine unification are completed and verified.
- CMD simplification, qh doctor, qh status UX, and Task scaffolding are safe to defer until after E2E.
- Worker smoke-test standardization remains deferred pending repeated Runner/E2E Evidence.
- Improvement candidates require separate approved Tasks before implementation.

Post-Milestone 1 Hardening Review:
- Milestone 1 real Worker E2E is COMPLETE - VERIFIED.
- QH-V2-HARD-001 selects Verification Contract Fail-Closed Hardening as the next implementation stage.
- Duplicate qh start / Lifecycle Guard is the second REQUIRED-BEFORE-NEXT-MILESTONE fix.
- Task scaffold generation, qh doctor, Windows CMD simplification, and Worker smoke/E2E standardization are NEXT-HARDENING.
- qh status UX and STATUS historical cleanup are SAFE-TO-DEFER.
- No capability expansion should begin until the two required hardening fixes are complete and verified.
