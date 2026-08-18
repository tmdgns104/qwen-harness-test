# Verified Problem Resolutions

## Purpose

Record operational failures only after the cause and resolution have been verified by Git, Test, file inspection, or other objective Evidence. Reuse the verified resolution when the same failure shape appears again.

## Record Format

Each incident must contain these fields exactly once:

1. Problem
2. Symptoms / Trigger
3. Root Cause
4. Verified Resolution
5. Verification Evidence
6. Prevention
7. Automation Candidate
8. Automation Status

## Incidents

### Incident 001 - Windows CMD multiline and redirection failure

**Problem**
Long multiline Python or Markdown content was pasted directly into Windows CMD.

**Symptoms / Trigger**
The first python -c line ended with an unterminated string, later Markdown lines were executed as CMD commands, and characters such as greater-than were interpreted as redirection.

**Root Cause**
Windows CMD parsed line breaks and shell metacharacters before Python could receive the intended complete payload.

**Verified Resolution**
Stop the broken command, inspect git status, inspect any unexpected untracked file before deletion, restore a clean Repository state, and avoid direct multiline payloads in CMD.

**Verification Evidence**
git status --short exposed the accidental tuple[str file. File inspection showed it was an empty artifact. After deletion, git status --short returned clean.

**Prevention**
Do not paste raw multiline Python, Markdown, or code-generation payloads directly into Windows CMD. Prefer a Repository Python utility for repeated procedures. For one-off work, use short readable Python commands and verify Repository state after failure.

**Automation Candidate**
A reusable Python utility that accepts Task and content files directly instead of embedding long payloads in CMD.

**Automation Status**
Candidate. Implementation requires a separate approved Task and must not bypass the HC-001 through HC-007 sequence.


### Incident 002 - Unexpected untracked artifact recovery

**Problem**
A failed CMD or editing operation created an unexpected untracked file outside the current Task scope.

**Symptoms / Trigger**
git status --short showed an unexpected ?? path such as tuple[str or tore -- toolsharness_core.py.

**Root Cause**
CMD redirection or accidental command output created a Repository file that was not part of the approved Task.

**Verified Resolution**
Do not delete immediately. Use git status and inspect the exact path, size, and content first. Delete it only after confirming that it is an accidental artifact, then verify the working tree again.

**Verification Evidence**
The unexpected files were inspected and identified as either an empty redirection artifact or saved git diff output. After deletion, git status --short showed only approved changes or returned clean.

**Prevention**
Treat every unexpected changed or untracked path as Evidence requiring inspection before cleanup. Never hide or delete unknown changes merely to obtain a clean status.

**Automation Candidate**
A Repository-state inspection utility that lists unexpected paths, metadata, and a safe preview before any cleanup action.

**Automation Status**
Candidate. Implement only through a separate approved Python utility Task.

### Incident 003 - Qwen candidate isolation before Repository application

**Problem**
Qwen-generated implementation output can be syntactically valid while still changing unrelated code, adding unnecessary helpers, omitting existing content, or failing the Task contract.

**Symptoms / Trigger**
Generated candidates included Markdown fences, incomplete files, excessive reasoning comments, unnecessary helper functions, missing module docstrings, or semantically incorrect Git logic.

**Root Cause**
LLM output quality is nondeterministic. Successful generation or self-reported completion does not prove Task correctness or scope compliance.

**Verified Resolution**
Write Qwen output to an isolated candidate file first. Before Repository application, verify syntax, compare existing top-level definitions with AST, inspect newly added definitions, run focused candidate-only tests, run the full regression suite, and inspect the exact diff. Apply the candidate to the Repository only after all required checks pass.

**Verification Evidence**
HC-003B candidate validation reached 11 focused tests PASS and 46 full tests PASS before Repository application. HC-003C candidates exposed implementation failures without modifying the Repository, while the final isolated candidate passed 9 focused tests and all 46 Repository tests before application.

**Prevention**
Never copy raw Worker output directly into an approved source file. Candidate isolation and objective verification must precede Repository modification. Worker self-reported PASS is not Evidence.

**Automation Candidate**
A reusable candidate-generation and candidate-validation Python utility that performs syntax, AST preservation, focused tests, full tests, and diff/scope checks.

**Automation Status**
Candidate. Current prototype behavior was exercised outside the Repository; permanent implementation requires a separate approved Task after Architecture boundaries permit it.

### Incident 004 - Global trailing-whitespace cleanup polluted verified code diff

**Problem**
A whitespace cleanup intended only for newly generated HC-003B code also changed whitespace in previously verified existing code.

**Symptoms / Trigger**
git diff --check initially reported trailing whitespace only in the new HC-003B block. A global regex cleanup then expanded the diff from a small append-only change to 106 changed lines, including unrelated existing functions.

**Root Cause**
The cleanup command operated on the entire source file instead of only the newly added block. Existing trailing whitespace that was outside the current Task was therefore modified as collateral change.

**Verified Resolution**
Restore the source file from Git, extract only the approved new block from the validated candidate, trim trailing whitespace inside that block only, and append that minimal block back to the original file.

**Verification Evidence**
After the global cleanup, git diff --stat showed 106 changed lines. After git restore and block-only reapplication, the diff returned to the intended HC-003B-only change of 45 insertions and 1 deletion, git diff --check passed, and all 46 tests passed.

**Prevention**
Do not run whole-file formatting or whitespace cleanup during a narrowly scoped Task unless that formatting change is explicitly approved. Apply cleanup only to newly generated or explicitly allowed regions and inspect the resulting diff before tests or commit.

**Automation Candidate**
A safe block-application Python utility that preserves the original file byte content outside an explicitly selected insertion or replacement region.

**Automation Status**
Candidate. Implement through a separate approved Python utility Task if block-level candidate application continues to recur.

### Incident 005 - Nested CMD/Python NUL delimiter escaping failure

**Problem**
A generated HC-003C candidate attempted to split NUL-delimited Git path output, but the generated source contained a literal backslash-zero sequence instead of a real NUL delimiter.

**Symptoms / Trigger**
HC-003C focused tests returned paths such as tracked.txt followed by an embedded NUL marker instead of separate tuple entries. Source inspection with findstr confirmed that the split expression contained an escaped backslash-zero literal.

**Root Cause**
The code passed through multiple interpretation layers: Windows CMD, python -c, a Python source-generating string, and the generated candidate source. Backslash escaping changed meaning across those layers.

**Verified Resolution**
Avoid representing the delimiter through nested escape sequences. Replace the generated split delimiter with bytes([0]), which constructs the NUL byte explicitly without depending on backslash escaping.

**Verification Evidence**
Before the fix, 4 of 9 HC-003C focused tests failed because multiple paths remained joined by NUL bytes. After replacing the delimiter with bytes([0]), all 9 focused tests passed and the full 46-test suite passed with no skips.

**Prevention**
When generated code must express control bytes through multiple command or string layers, prefer explicit byte construction such as bytes([0]) over nested escape literals. Repeated source generation should move out of CMD one-liners into a Python utility.

**Automation Candidate**
A Python candidate-generation utility that writes Python source directly and validates generated source before execution, eliminating nested CMD string escaping.

**Automation Status**
Candidate. This failure repeated the broader CMD escaping problem, so it is strong Evidence for promotion to a Repository Python utility through a separate approved Task.

### Incident 006 - Oversized or malformed Qwen candidate handled by bounded repair

**Problem**
Qwen sometimes produced candidates that were syntactically malformed, incomplete, excessively large, or outside the requested minimal implementation shape.

**Symptoms / Trigger**
Observed outputs included Markdown fences despite raw-source instructions, a partial file instead of the complete module, unnecessary helper functions, hundreds of lines of reasoning comments, missing module docstrings, and implementations that violated the Task contract.

**Root Cause**
Local LLM generation is probabilistic and tool-call or source-generation success does not guarantee semantic correctness, minimality, or preservation of existing verified code.

**Verified Resolution**
Keep the generated candidate isolated. Validate syntax, compare existing top-level definitions with AST, inspect new definitions, compare file size and exact diff, and run focused tests. When a candidate fails, use the concrete failure Evidence for one bounded repair instead of repeatedly expanding the prompt or applying speculative edits. If repeated attempts still fail, stop as FAIL or BLOCKED.

**Verification Evidence**
HC-003B qwen3.5:9b first produced a 515-line candidate with an unnecessary helper and extensive reasoning comments. A bounded repair produced a 240-line candidate preserving all existing definitions; 11 focused tests and the full 46-test suite passed before application. HC-003C Qwen candidates were also rejected by code inspection and focused tests before the final deterministic candidate was applied.

**Prevention**
Treat candidate size, syntax, AST preservation, added-definition count, diff, focused tests, and full regression results as mandatory Evidence before Repository application. Do not trust Worker self-reported PASS and do not use unlimited prompt retries.

**Automation Candidate**
A native local Worker utility that performs candidate generation, syntax and AST validation, bounded repair, test execution, diff inspection, and explicit PASS, FAIL, or BLOCKED Evidence.

**Automation Status**
Candidate. The repeated manual workflow now has sufficient recurrence Evidence to justify a separate Python utility Task when current Architecture and HC sequencing permit implementation.

### Incident 007 - Opaque Base64/zlib payload corruption

**Problem**
A long compressed Base64 payload was used to create a Markdown document through a Windows CMD python -c command, but the encoded payload was corrupted before successful decompression.

**Symptoms / Trigger**
Python raised zlib.error with invalid code lengths set before write_text executed, so the intended runbook file was not created.

**Root Cause**
The long opaque encoded payload was difficult for a human to inspect and verify and introduced another fragile transport layer on top of CMD and python -c.

**Verified Resolution**
Stop using large opaque Base64/zlib blobs for repeated document creation. Confirm Repository state and file existence after failure, then build the document incrementally using short readable Python commands whose content can be inspected directly.

**Verification Evidence**
After the zlib error, git status --short showed no Repository modification and an explicit existence check returned RUNBOOK_NOT_CREATED. The runbook was then created successfully with a short readable Python command and incidents were appended incrementally.

**Prevention**
Do not use long compressed or encoded payloads merely to avoid CMD quoting problems. If content or automation is large enough to require opaque encoding, promote the operation to a readable Python utility or file-based workflow instead.

**Automation Candidate**
A Repository Python utility that reads structured incident data or source files directly and writes Markdown without transporting large encoded payloads through CMD.

**Automation Status**
Candidate. This incident strengthens the requirement to replace recurring long CMD content-generation procedures with approved Python utilities.
