# TP-OS-SHADOW-001R3

Operation-specific parser hardening was verified. The captured post-fix replay
produced one strict `REPLACE_TEXT` operation for `app/conversation.py`.

- Inference count: 1; latency: 10.989s
- Transport and strict parse: PASS
- Validator: PASS; exact occurrence: 1
- Isolated snapshot apply: PASS
- Independent Python semantic assertions: FAIL (`SEMANTIC_FAIL`; invalid
  balanced block 뒤의 valid object를 찾지 못함)
- Existing full regression: not run in this derived evidence
- Harness outcome: `VERIFICATION_FAILED`; Qwen first-pass: FAIL; Codex review:
  FAIL (Candidate 의미가 Acceptance Criteria를 충족하지 않음)
- Target mutation: 0; False COMPLETED: 0

R1 was 9.336s but selected `REPLACE_FILE`; R3 selected the required operation,
but the proposed implementation failed semantic verification. No Codex repair,
retry, or Candidate repair was performed.
Original full-file run timed out near 30s. Historical R2 timeout labeling is
explained by the parser bug and remains preserved.
