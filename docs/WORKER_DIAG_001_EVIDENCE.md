# QH-V2-WORKER-DIAG-001 Evidence

## Worker Timing / Timeout Evidence

### Stable runtime values observed

- Ollama base URL: `http://127.0.0.1:11434`
- Default model: `qwen3:8b`
- Worker timeout: `30.0` seconds
- Worker think mode: `False`
- Worker step budget: `8`
- Retry attempt budget: `2`
- qh doctor Ollama timeout: `5.0` seconds

No production behavior was changed while collecting this Evidence.

### Case 1 - short prompt, no tools

Prompt: `Reply with OK only.`
Model: `qwen3:8b`
Think: `False`
Timeout: `30.0` seconds
Runs: 5
Repository write attempted: no

| Run | Elapsed seconds | Result |
|---:|---:|---|
| 1 | 12.128 | transport success |
| 2 | 0.297 | transport success |
| 3 | 0.303 | transport success |
| 4 | 0.301 | transport success |
| 5 | 0.327 | transport success |

Observation: first-call warm-up/cold-start cost is plausible, but all five calls completed within the Stable timeout.

### Case 2 - short prompt, current Worker tool schema

Prompt: `Reply with OK only.`
Tools: current `read_repo_text` and `write_repo_text` schema
Model: `qwen3:8b`
Think: `False`
Timeout: `30.0` seconds
Runs: 5
Repository write attempted: no; only the first Worker step was requested and no ToolRequest was executed.

| Run | Elapsed seconds | ToolRequests | Result |
|---:|---:|---:|---|
| 1 | 0.669 | 0 | transport success |
| 2 | 0.472 | 0 | transport success |
| 3 | 0.300 | 0 | transport success |
| 4 | 0.338 | 0 | transport success |
| 5 | 0.307 | 0 | transport success |

Observation: current tool-schema exposure alone did not reproduce the timeout on a short prompt.

### Case 3 - representative full Task prompt, no tools

Prompt source: tracked `tasks/QH-V2-WORKER-DIAG-001.md` whole-file contents
Model: `qwen3:8b`
Think: `False`
Timeout: `30.0` seconds
Runs: 5
Repository write attempted: no

| Run | Elapsed seconds | Result |
|---:|---:|---|
| 1 | 30.061 | `TimeoutError: timed out` |
| 2 | 30.021 | `TimeoutError: timed out` |
| 3 | 30.006 | `TimeoutError: timed out` |
| 4 | 30.013 | `TimeoutError: timed out` |
| 5 | 30.018 | `TimeoutError: timed out` |

Observation: 0/5 calls completed. The current `call_ollama_worker` path does not normalize this observed socket `TimeoutError` into `WorkerResponse(transport_ok=False)`; the exception escaped the adapter call during this diagnostic procedure. This is separate from Repository Task PASS/FAIL and does not itself prove a correct repair.

### Control - same full Task input, constrained output

Procedure: the same full Task text was wrapped with `Do not execute or solve ... reply with exactly OK.`
Runs: 3
Repository write attempted: no

| Run | Elapsed seconds | Result |
|---:|---:|---|
| 1 | 1.766 | transport success, output `OK` |
| 2 | 0.351 | transport success, output `OK` |
| 3 | 0.320 | transport success, output `OK` |

Interpretation: input length by itself is not sufficient to explain the 30-second failures. The evidence points more strongly toward the task-solving/generation path than raw prompt ingestion alone.

### Case 4 - representative full Task prompt, current Worker tool schema

Prompt source: tracked `tasks/QH-V2-WORKER-DIAG-001.md` whole-file contents
Tools: current `read_repo_text` and `write_repo_text` schema
Model: `qwen3:8b`
Think: `False`
Timeout: `30.0` seconds
Runs: 5
Repository write attempted: no; only `OllamaToolSession.start()` was called and returned ToolRequests were not executed.

| Run | Elapsed seconds | ToolRequests | Result |
|---:|---:|---:|---|
| 1 | 2.980 | 1 | transport success |
| 2 | 1.712 | 1 | transport success |
| 3 | 30.023 | n/a | `TimeoutError: timed out` |
| 4 | 30.022 | n/a | `TimeoutError: timed out` |
| 5 | 30.003 | n/a | `TimeoutError: timed out` |

Additional 3-run request inspection:

- run 1: 30.042 seconds, `TimeoutError`
- run 2: 1.753 seconds, one `read_repo_text` request for `docs/WORKER_DIAG_001_EVIDENCE.md`
- run 3: 1.692 seconds, one `read_repo_text` request for `docs/WORKER_DIAG_001_EVIDENCE.md`

Interpretation: tool calling can produce a relevant bounded next action quickly, but identical full-Task conditions remain unstable. This supports later controlled comparison of original full Task versus a deterministic Worker Brief and a Worker Brief constrained to one step/one ToolRequest. It does not authorize that implementation in this Task.

### Timing conclusion

- Short prompts are stable after possible first-call warm-up.
- Tool schema is not independently sufficient to reproduce the timeout.
- Full Task execution with no tools timed out 5/5.
- The same full input with output constrained to exactly `OK` completed quickly 3/3.
- Full Task plus tools produced a useful one-tool next action on some runs but still timed out repeatedly.
- Increasing the timeout alone is not established as the correct fix.
- A future Worker robustness experiment should compare deterministic Task projection / Worker Brief and one-step ToolRequest behavior against the current full-Task Stable path using success rate, latency, and safety Evidence.

## Global-Use Hard-Coding Inventory

The tracked-code searches covered at least `tools/**` and `ops/qhops/**`, including Ollama literals, model and timeout defaults, Worker/Retry budgets, absolute paths, usernames, Repository names, branch/remote names, Windows assumptions, and existing configuration mechanisms.

### Environment configuration

| File / symbol | Current literal/default | Global-use impact | Change recommended | Suggested future treatment | ADR needed? |
|---|---|---|---|---|---|
| `tools/ollama_worker.py` `DEFAULT_BASE_URL` | `http://127.0.0.1:11434` | Another Ollama host/port requires code-level override by callers; default is duplicated in doctor | yes, retain this as a default but provide one explicit external configuration source shared by Worker/doctor where appropriate | environment/config value with deterministic precedence and validated fallback | normally implementation Task if authority is unchanged |
| `tools/ollama_worker.py` `DEFAULT_MODEL` | `qwen3:8b` | Other installed/default local models require caller override; doctor duplicates the same model name separately | yes, as a configurable default, without authorizing automatic model routing | environment/config value with Stable default | normal implementation Task if no routing policy change |
| `tools/qh.py` `DOCTOR_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | doctor can report failure even when Worker is intentionally configured elsewhere in a future global installation | yes; avoid independent drift from Worker service configuration | reuse a common resolved endpoint, while retaining doctor-specific behavior | normal implementation Task if semantics remain diagnostic only |
| `tools/qh.py` `DOCTOR_OLLAMA_MODEL` | `qwen3:8b` | doctor can disagree with a future configured Worker model | yes; resolve the same configured Stable model rather than copy the literal | common configuration resolution | normal implementation Task if no routing expansion |
| `ops/qhops/qh_ops.py` `REMOTE` | `origin` | general `safe_push()` fetch/push requires a remote named `origin` | yes for future global use | Repository-specific qhops configuration or explicit command/config resolution | likely normal implementation Task if push authority remains Human-controlled and bounded |
| `ops/qhops/qh_ops.py` `REMOTE_BRANCH` | `main` | general `safe_push()` assumes target branch `main`; another Repository may use another branch | yes for future global use | Repository-specific configured push target with safe fast-forward validation | may require Architecture review if changing an existing sealed authority boundary; ordinary operations path can be separately scoped |

### Tunable runtime policy

| File / symbol | Current literal/default | Global-use impact | Change recommended | Suggested future treatment | ADR needed? |
|---|---|---|---|---|---|
| `tools/ollama_worker.py` `DEFAULT_TIMEOUT_SECONDS` | `30.0` | real full-Task execution repeatedly hits this boundary; different hardware/model workloads may differ | investigate/configure only after benchmark Evidence | explicit bounded runtime policy, not unbounded user freedom | likely policy review; ADR if retry/stop semantics or authority change |
| `tools/ollama_worker.py` payload `think` | `False` | fixed fast-path behavior may not suit every model/task, but it is an Accepted Worker strategy rather than mere machine configuration | do not change automatically | policy-controlled value evaluated by Stable-vs-Candidate Evidence | yes or Human policy review if changing accepted model/reasoning behavior |
| `tools/qh.py` `DOCTOR_OLLAMA_TIMEOUT_SECONDS` | `5.0` | diagnostic reachability budget can differ from Worker execution timeout | no immediate blocker; keep separate purpose | doctor-specific bounded diagnostic policy | normally no ADR for a narrow diagnostic-only adjustment |

### Safety-critical policy constant

| File / symbol | Current literal/default | Why it is safety-critical | Change recommended | ADR needed? |
|---|---|---|---|---|
| `tools/task_runner.py` `MAX_WORKER_STEPS` | `8` | finite bound prevents indefinite Worker/tool looping and is tied to accepted Runner/Retry policy | no automatic configuration extraction | yes before changing policy semantics |
| `tools/retry_runner.py` `MAX_RUNNER_ATTEMPTS` | `2` | bounds whole-Runner retry and write-side-effect risk under ADR-009 | no automatic configuration extraction | yes before changing retry policy |
| `ops/qhops/qh_ops.py` `LOCAL_BRANCH` | `master` | observed use is in sealed G1 gate-manifest validation, not general Repository discovery; changing it would reinterpret historical authorization | do not generalize as a normal runtime setting inside the old sealed gate | yes if redesigning that Gate authority |

### Protocol/schema constant

Relevant fixed strings such as Worker tool names (`read_repo_text`, `write_repo_text`), lifecycle status strings, Task headings, and exact manifest fields are contract identifiers rather than environment portability defects. They should remain fixed unless the corresponding contract is deliberately versioned or superseded.

### Test/documentation fixture only

- `ops/qhops/README.md`: `D:\qwen-harness-test` and `D:\another-harness` are usage examples.
- `ops/qhops/qh_ops.py` usage text contains the same example paths; these do not control Repository resolution.
- `ops/qhops/tests/test_autonomous_queue.py`: repository remote identity is a test fixture.
- `ops/qhops/autonomous_queue_manifest.json`: `github.com/tmdgns104/qwen-harness-test.git`, `master`, `origin`, `main`, and `HEAD:main` belong to the sealed historical G1 manifest. They are Evidence/authorization identity, not a template to rewrite for global use.

### Repository path, branch, remote, and Windows review

Repository path:

- `qhops` resolves a Repository by explicit `--repo`, current Git top-level, `QH_REPO`, or `%USERPROFILE%/.qhops/config.json` `default_repo`.
- Harness Core uses `git rev-parse --show-toplevel`, resolved `repo_root`, and Repository-relative paths.
- No tracked production runtime code search hit for a user-specific `C:\Users\...` path.
- `D:\qwen-harness-test` occurrences found in runtime-adjacent code are command usage examples, not Repository selection authority.

branch / remote:

- general qhops `safe_push()` uses fixed `origin` and `main`; this is a genuine global-use portability blocker candidate.
- fixed `master` was observed specifically in the sealed autonomous G1 gate path and must not be rewritten casually.
- the sealed historical manifest's exact remote identity must remain historical Evidence.

Windows:

- `os.name == "nt"` in Harness Core is used to select Windows path-comparison behavior; this is a platform compatibility branch, not a portability defect by itself.
- qhops is explicitly documented as a Windows helper, but Repository discovery itself is path-dynamic.
- Windows command examples are documentation/usage fixtures.

Existing configuration mechanism:

- `%USERPROFILE%/.qhops/config.json` currently stores only `default_repo`.
- `QH_REPO` currently overrides only Repository selection.
- No existing environment/config resolution was found for Ollama URL, model, Worker timeout, think mode, remote, or remote branch.

## Conclusion / Human Review Disposition

Recommended disposition: **both are justified as separate Tasks**.

1. **QH-V2-WORKER-ROB-002 is justified as an Evidence-driven experiment Task**, not as an immediate production change. It should compare:
   - current full Task Stable input;
   - a deterministic Harness-produced Worker Brief that preserves Goal, scope, safety boundaries, Acceptance Criteria, and required context without making the brief a new Source of Truth;
   - Worker Brief plus explicit one-step/one-ToolRequest instruction.

   The comparison should measure task success, latency, timeout rate, tool correctness, and safety violations. Long timeout increases alone should not count as a fix.

2. **A separate global-use configuration/portability Task is justified** for true environment-dependent values and duplicated defaults, especially Ollama endpoint/model resolution and general qhops remote/target-branch configuration. It must explicitly preserve sealed historical G1 evidence and must not convert safety-critical step/retry constants into free user settings.

3. **A separate small transport-normalization fix candidate is also justified** because observed socket `TimeoutError` escaped the adapter's current `URLError` handling. That fix should normalize transport failure without changing timeout duration, Retry classification authority, or Repository PASS semantics.

No Worker/model/backend/prompt implementation, Runner/Retry behavior, configuration behavior, lifecycle behavior, Verification, Final Gate, Git authority, or Globalization authorization changed in QH-V2-WORKER-DIAG-001.

QH-V2-WORKER-ROB-001 remains `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` and is not reinterpreted as successful Evidence.
