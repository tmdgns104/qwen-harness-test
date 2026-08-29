# TP-OS-SHADOW-001D2 Evidence

Stage 0 completed before any model call and was checkpointed. Source size was
13,510 characters / 13,540 bytes; relevant test excerpt 3,107 / 3,235; the
original-shadow Context was 20,878 / 21,470 characters. Serialized request
sizes were: Minimal 2,086, Function+Test 5,804, Full Source 18,838, Original
Shadow 24,491 characters.

Stage 1 tiny probe completed in 0.681 s with Ollama metrics:
`total_duration=625,374,700 ns`, `load_duration=8,010,900 ns`,
`prompt_eval_count=28`, `prompt_eval_duration=29,652,000 ns`,
`eval_count=8`, `eval_duration=120,126,000 ns`; structured JSON was returned.

Stage 2 Function-only completed in 11.204 s. It generated a large 693-token
response (`eval_duration=11,070,958,000 ns`) and an invalid path Candidate.
Stage 3 Function+Relevant Tests completed in 1.394 s with 56 output tokens;
the response was structured but selected an unrelated path. Stage 4 Full Source
and Stage 5 Original Shadow completed only as timeout/error observations and
did not return response metrics.

The evidence does not support a single definitive root cause. Tiny and
Function+Test are fast, while Minimal incurred unusually long generation;
Full/Original did not complete within the bounded observation. The most
defensible classification is **INCONCLUSIVE**, with generation variability and
request/context interaction both plausible. Production timeout was not changed.

The Target repository was never written. Prior untracked zip state was not
altered. A follow-up should isolate generation length with a minimal exact
Candidate prompt and checkpoint each call, rather than increasing production
timeout or adding retries.
