## ADR-015 - Evidence-Backed Unsuccessful Task Closure and Lifecycle Bootstrap

### Status

Accepted

### Context

QH-V2-WORKER-ROB-001 reached a Human Architecture review after objective Stable-versus-Candidate Evidence showed no promotable Worker protocol improvement.

The representative real `qwen3:8b`, `think:false` probe measured 0/10 exact task success for Stable and 0/10 for the final Candidate. Focused diagnostics showed that ToolResult delivery and semantic reuse can succeed while exact downstream tool-argument fidelity remains unreliable. The Candidate was therefore rejected and its failed implementation history was preserved as Evidence only.

The current lifecycle has a gap: normal progression assumes an ACTIVE Task eventually becomes `COMPLETE - VERIFIED`. That is truthful for successful implementation, but it cannot represent a Task that was executed and evaluated correctly yet intentionally not promoted because its Acceptance Criteria were not met. Leaving such a Task ACTIVE forever blocks the queue, while marking it COMPLETE - VERIFIED would falsely claim success.

The Human explicitly approved an Architecture change to add an Evidence-backed unsuccessful terminal state and a one-time bootstrap transition so the lifecycle implementation Task can be started without falsifying QH-V2-WORKER-ROB-001.

### Decision

1. Add a distinct non-success terminal lifecycle state:

   `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

2. This state means all of the following:
   - the Task was actually attempted or evaluated;
   - objective Evidence explains why promotion or successful completion did not occur;
   - the Task is no longer ACTIVE;
   - the state is not equivalent to PASS, COMPLETE, or COMPLETE - VERIFIED;
   - no failed Candidate becomes production state merely because the Task is closed;
   - later work must not cite this state as successful implementation Evidence.

3. `COMPLETE - VERIFIED` remains the only successful completion state. Existing successful `qh close` Final Gate semantics remain authoritative and unchanged.

4. Durable support for unsuccessful closure must be implemented through the separately approved `QH-V2-LIFECYCLE-001` Task. Exact command names and code structure are deferred to that Task, but the implementation must remain Human-invoked, deterministic, Evidence-backed, and fail closed.

5. A future unsuccessful-close operation must require at minimum:
   - exactly one ACTIVE current Task;
   - explicit Human invocation;
   - a declared Evidence artifact or deterministic Evidence condition supporting the non-success result;
   - no claim of Final Gate PASS or successful implementation;
   - lifecycle mutation limited to the explicitly authorized lifecycle files;
   - clean, reviewable Git state before and after the lifecycle transition;
   - no automatic successor start.

6. After an unsuccessful Task is closed, the next Task is not automatically selected or started. Successor eligibility requires an explicit Human decision under the ordinary lifecycle unless a later Accepted ADR grants a narrower deterministic exception.

7. QH-V2-WORKER-ROB-001 is the first and only one-time bootstrap case authorized by this ADR. Its accepted disposition is:

   `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

   with Candidate promotion rejected and the failed implementation branch retained as Evidence only.

8. Because durable unsuccessful-close support does not yet exist, one Human-authorized bootstrap transition may update the Repository Source of Truth to close QH-V2-WORKER-ROB-001 unsuccessfully and activate `QH-V2-LIFECYCLE-001`. This bootstrap is not reusable precedent for arbitrary manual lifecycle mutation after LIFECYCLE-001 is implemented.

9. The bootstrap change set must be narrow and explicit. It may update only the Architecture/queue/lifecycle records and the new lifecycle Task contract needed to represent the approved transition. It must not modify Worker, Runner, Retry, Repository-tool, Verification, Evidence, Final Gate, model-routing, or tool-authority implementation.

10. QH-V2-OPS-003 remains deferred. The next implementation priority is `QH-V2-LIFECYCLE-001`. Worker/backend/model/thinking-policy comparison and the longer-term question of whether exact data binding belongs in deterministic Harness code require later separately approved Investigation/Architecture work.

### Safety Boundaries

- Qwen Worker authority does not expand.
- Multi-tool Runner SAFETY behavior remains unchanged.
- Retry policy and the eight-step Worker budget remain unchanged.
- Default model and routing policy remain unchanged.
- `qh close` successful Final Gate authority remains unchanged.
- No automatic repair, normalization, silent Candidate promotion, successor start, commit, push, or Architecture mutation is authorized.
- `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
- `M3 = FUTURE / NOT AUTHORIZED` remains unchanged.

### Consequences

- Failed experiments can terminate truthfully without being mislabeled as successful completion.
- Evidence becomes part of the lifecycle outcome rather than an informal side note.
- QH-V2-WORKER-ROB-001 can leave ACTIVE state without promoting its failed Candidate.
- QH-V2-LIFECYCLE-001 becomes the next Human-approved implementation Task before further Worker investigation or OPS-003.
- Future lifecycle code must support this state deterministically so another manual bootstrap is not needed.
