from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path


if __file__ == "<stdin>":
    ROOT = Path.cwd().resolve()
else:
    ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ollama_worker import DEFAULT_MODEL
from tools.retry_runner import RetryOutcomeKind, run_with_retry
from tools.task_runner import RunnerFailureKind


TASK_ID = "QH-WORKER-PROTOCOL-PROBE"
DEFAULT_RUNS = 10


def _task_markdown() -> str:
    return f"""# {TASK_ID} - Sequential Tool Protocol Probe

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Use the Repository tools to read `source.txt`. Then create `target.txt` with exactly
`COPIED:` followed immediately by the exact text returned from `source.txt`.
Do not guess the source text. Finish with a short completion message only after the
write ToolResult has been returned.

## Allowed Changes

- `target.txt`

## Forbidden Changes

- `STATUS.md`
- `tasks/**`
"""


def _prepare_repo(root: Path, run_number: int) -> str:
    source = f"PROBE-CONTENT-{run_number:02d}"
    (root / "tasks").mkdir()
    (root / "STATUS.md").write_text(
        f"Current Task: {TASK_ID} - ACTIVE\n",
        encoding="utf-8",
        newline="\n",
    )
    (root / "tasks" / f"{TASK_ID}.md").write_text(
        _task_markdown(),
        encoding="utf-8",
        newline="\n",
    )
    (root / "source.txt").write_text(
        source,
        encoding="utf-8",
        newline="\n",
    )
    return source


def _classify(outcome, root: Path, expected: str) -> tuple[str, bool]:
    result = outcome.runner_result
    target = root / "target.txt"
    target_ok = target.is_file() and target.read_text(encoding="utf-8") == expected

    if outcome.outcome_kind is RetryOutcomeKind.NORMAL:
        return ("NORMAL" if target_ok else "NORMAL_TASK_MISS"), target_ok

    if outcome.outcome_kind is RetryOutcomeKind.BLOCKED:
        if result.failure_kind is RunnerFailureKind.TRANSIENT_WORKER:
            return "TRANSIENT_WORKER/BLOCKED", target_ok
        return "BLOCKED_OTHER", target_ok

    if result.failure_kind is RunnerFailureKind.SAFETY:
        if result.error and "zero or one ToolRequest" in result.error:
            return "SAFETY_MULTI_TOOL", target_ok
        return "SAFETY_OTHER", target_ok

    if result.failure_kind is RunnerFailureKind.STEP_BUDGET:
        return "STEP_BUDGET", target_ok

    if result.failure_kind is RunnerFailureKind.TRANSIENT_WORKER:
        return "TRANSIENT_WORKER", target_ok

    return "OTHER_FAIL", target_ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, choices=("Stable", "Candidate"))
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    args = parser.parse_args()

    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")

    counts: Counter[str] = Counter()
    records: list[dict[str, object]] = []

    print(
        "PROBE_CONFIG "
        f"label={args.label} runs={args.runs} model={DEFAULT_MODEL} "
        "think=false scenario=read->ToolResult->write->ToolResult->text"
    )

    for run_number in range(1, args.runs + 1):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = _prepare_repo(root, run_number)
            expected = f"COPIED:{source}"
            outcome = run_with_retry(root, TASK_ID)
            category, target_ok = _classify(outcome, root, expected)
            counts[category] += 1

            result = outcome.runner_result
            record = {
                "run": run_number,
                "category": category,
                "outcome": outcome.outcome_kind.name,
                "attempts": outcome.attempts_consumed,
                "failure_kind": (
                    result.failure_kind.name if result.failure_kind is not None else None
                ),
                "steps": result.steps_consumed,
                "write_side_effect_risk": outcome.write_side_effect_risk,
                "target_ok": target_ok,
                "error": result.error,
            }
            records.append(record)
            print("RUN " + json.dumps(record, ensure_ascii=False, sort_keys=True))

    summary = {
        "label": args.label,
        "runs": args.runs,
        "model": DEFAULT_MODEL,
        "think": False,
        "counts": dict(sorted(counts.items())),
        "normal_target_ok": sum(1 for item in records if item["category"] == "NORMAL"),
    }
    print("SUMMARY " + json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
