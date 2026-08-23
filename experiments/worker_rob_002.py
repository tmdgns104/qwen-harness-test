from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import time
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path

from tools.harness_core import (
    ChangeScope,
    ToolRequest,
    WorkerRequest,
    parse_change_scope,
    resolve_scoped_write_target,
)
from tools.ollama_worker import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT_SECONDS,
    OllamaToolSession,
)
from tools.task_runner import _runner_tools, _validate_tool_request


TASK_ID = "QH-V2-WORKER-ROB-002"
VARIANT_STABLE = "stable_full_task"
VARIANT_BRIEF = "candidate_worker_brief"
VARIANT_BRIEF_ONE_STEP = "candidate_worker_brief_one_step"
VARIANTS = (VARIANT_STABLE, VARIANT_BRIEF, VARIANT_BRIEF_ONE_STEP)

REQUIRED_BRIEF_SECTIONS = (
    "Goal",
    "Architecture Basis",
    "Dependencies",
    "Scope",
    "Allowed Changes",
    "Forbidden Changes",
    "Acceptance Criteria",
    "Stop Conditions",
)

BRIEF_AUTHORITY_STATEMENT = (
    "The original tracked Task remains the Source of Truth. "
    "This Worker Brief grants no authority beyond the original Task. "
    "Verification and Final Gate remain Harness-owned."
)

ONE_STEP_INSTRUCTION = (
    "Choose exactly one next Worker action for this turn. "
    "Do not attempt to solve the entire Task in one response. "
    "If a tool action is needed, issue no more than one ToolRequest."
)

EXPERIMENT_COMMAND = (
    "python -m experiments.worker_rob_002 --repo-root . "
    "--task-id QH-V2-WORKER-ROB-002 "
    "--results docs/WORKER_ROB_002_RESULTS.json "
    "--evidence docs/WORKER_ROB_002_EVIDENCE.md"
)


def _h1_title(markdown: str) -> str:
    titles = [line for line in markdown.splitlines() if line.startswith("# ")]
    if len(titles) != 1:
        raise ValueError(f"expected exactly one Task title; found {len(titles)}")
    return titles[0]


def _required_section_bodies(markdown: str) -> dict[str, str]:
    lines = markdown.splitlines(keepends=True)
    found: dict[str, list[str]] = {name: [] for name in REQUIRED_BRIEF_SECTIONS}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal current, buffer
        if current in found:
            found[current].append("".join(buffer))
        current = None
        buffer = []

    for line in lines:
        if line.startswith("## "):
            flush()
            current = line[3:].strip()
            continue
        if current is not None:
            buffer.append(line)
    flush()

    missing = [name for name, bodies in found.items() if not bodies]
    duplicated = [name for name, bodies in found.items() if len(bodies) != 1]
    if missing:
        raise ValueError(f"missing required Worker Brief sections: {missing}")
    if duplicated:
        raise ValueError(f"duplicated required Worker Brief sections: {duplicated}")

    return {name: found[name][0] for name in REQUIRED_BRIEF_SECTIONS}


def build_worker_brief(task_markdown: str) -> str:
    """Project exact tracked Task sections into a deterministic Worker Brief."""
    title = _h1_title(task_markdown)
    bodies = _required_section_bodies(task_markdown)
    pieces = [title, "", BRIEF_AUTHORITY_STATEMENT, ""]
    for section in REQUIRED_BRIEF_SECTIONS:
        pieces.append(f"## {section}")
        pieces.append(bodies[section].rstrip("\r\n"))
        pieces.append("")
    return "\n".join(pieces).rstrip() + "\n"


def build_variant_prompts(task_markdown: str) -> dict[str, str]:
    brief = build_worker_brief(task_markdown)
    return {
        VARIANT_STABLE: task_markdown,
        VARIANT_BRIEF: brief,
        VARIANT_BRIEF_ONE_STEP: brief.rstrip() + "\n\n" + ONE_STEP_INSTRUCTION + "\n",
    }


def interleaved_plan(runs_per_variant: int = 10) -> list[tuple[str, int]]:
    if runs_per_variant <= 0:
        raise ValueError("runs_per_variant must be positive")
    plan: list[tuple[str, int]] = []
    counters = {variant: 0 for variant in VARIANTS}
    for round_index in range(runs_per_variant):
        offset = round_index % len(VARIANTS)
        order = VARIANTS[offset:] + VARIANTS[:offset]
        for variant in order:
            counters[variant] += 1
            plan.append((variant, counters[variant]))
    return plan


def _bounded_value(value: object) -> object:
    if isinstance(value, str):
        if len(value) <= 200:
            return value
        return {
            "length": len(value),
            "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        }
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return {"type": type(value).__name__, "repr": repr(value)[:200]}


def bounded_arguments(request: ToolRequest) -> dict[str, object]:
    if not isinstance(request.arguments, Mapping):
        return {"arguments": _bounded_value(request.arguments)}
    result: dict[str, object] = {}
    for key in sorted(request.arguments):
        value = request.arguments[key]
        if key == "content" and isinstance(value, str):
            result["content_length"] = len(value)
            result["content_sha256"] = hashlib.sha256(
                value.encode("utf-8")
            ).hexdigest()
        else:
            result[key] = _bounded_value(value)
    return result


def _read_path_is_repo_relative(repo_root: Path, relative_path: str) -> bool:
    root = repo_root.resolve()
    try:
        target = (root / relative_path).resolve()
        target.relative_to(root)
    except (OSError, ValueError):
        return False
    return True


def review_tool_request(
    repo_root: Path,
    task_id: str,
    scope: ChangeScope,
    request: ToolRequest,
) -> dict[str, object]:
    review: dict[str, object] = {
        "name": request.name,
        "arguments": bounded_arguments(request),
        "schema_valid": False,
        "path_compatible": False,
        "validation_error": None,
    }
    try:
        relative_path, _ = _validate_tool_request(request)
        review["schema_valid"] = True
        if request.name == "read_repo_text":
            if not _read_path_is_repo_relative(repo_root, relative_path):
                raise ValueError("read path does not remain inside Repository")
        elif request.name == "write_repo_text":
            target = resolve_scoped_write_target(repo_root, relative_path, scope)
            lifecycle_targets = {
                os.path.normcase(str((repo_root / "STATUS.md").resolve())),
                os.path.normcase(
                    str((repo_root / "tasks" / f"{task_id}.md").resolve())
                ),
            }
            if os.path.normcase(str(target)) in lifecycle_targets:
                raise ValueError("Worker write to lifecycle-control path is not allowed")
        review["path_compatible"] = True
    except (OSError, TypeError, ValueError) as exc:
        review["validation_error"] = f"{type(exc).__name__}: {exc}"
    return review


def _is_timeout_error(exc: BaseException | str | None) -> bool:
    if isinstance(exc, TimeoutError):
        return True
    return "timed out" in str(exc or "").lower()


def _default_session_factory(request: WorkerRequest, *, tools):
    return OllamaToolSession(
        request,
        tools=tools,
        base_url=DEFAULT_BASE_URL,
        model=DEFAULT_MODEL,
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    )


def measure_initial_step(
    repo_root: Path,
    task_id: str,
    task_markdown: str,
    variant: str,
    run_index: int,
    prompt: str,
    *,
    session_factory: Callable = _default_session_factory,
) -> dict[str, object]:
    scope = parse_change_scope(task_markdown)
    tools = _runner_tools()
    started = time.perf_counter()
    try:
        session = session_factory(WorkerRequest(prompt), tools=tools)
        step = session.start()
    except Exception as exc:  # benchmark records escaped adapter failures as Evidence
        elapsed = time.perf_counter() - started
        return {
            "variant": variant,
            "run_index": run_index,
            "elapsed_seconds": round(elapsed, 6),
            "transport_success": False,
            "failure_classification": (
                "timeout_exception" if _is_timeout_error(exc) else "exception"
            ),
            "error": f"{type(exc).__name__}: {exc}",
            "timeout_occurrence": _is_timeout_error(exc),
            "tool_request_count": 0,
            "tool_request_names": [],
            "tool_requests": [],
            "output_length": 0,
            "multi_tool_safety_shape": False,
            "invalid_unknown_tool_request": False,
            "scope_incompatible_requested_path": False,
            "valid_bounded_first_step": False,
            "zero_tool_terminal_response": False,
            "write_executed": False,
        }

    elapsed = time.perf_counter() - started
    reviews = [
        review_tool_request(repo_root, task_id, scope, request)
        for request in step.tool_requests
    ]
    invalid = any(not bool(review["schema_valid"]) for review in reviews)
    incompatible = any(not bool(review["path_compatible"]) for review in reviews)
    count = len(step.tool_requests)
    transport_success = bool(step.transport_ok)
    valid_bounded = transport_success and count == 1 and not invalid and not incompatible

    return {
        "variant": variant,
        "run_index": run_index,
        "elapsed_seconds": round(elapsed, 6),
        "transport_success": transport_success,
        "failure_classification": "ok" if transport_success else "transport_failure",
        "error": step.error,
        "timeout_occurrence": _is_timeout_error(step.error),
        "tool_request_count": count,
        "tool_request_names": [request.name for request in step.tool_requests],
        "tool_requests": reviews,
        "output_length": len(step.output_text),
        "multi_tool_safety_shape": count > 1,
        "invalid_unknown_tool_request": invalid,
        "scope_incompatible_requested_path": incompatible,
        "valid_bounded_first_step": valid_bounded,
        "zero_tool_terminal_response": transport_success and count == 0,
        "write_executed": False,
    }


def summarize_variant(runs: list[dict[str, object]]) -> dict[str, object]:
    if not runs:
        raise ValueError("variant has no runs")
    n = len(runs)

    def count_true(key: str) -> int:
        return sum(1 for run in runs if bool(run[key]))

    completed_elapsed = [
        float(run["elapsed_seconds"])
        for run in runs
        if bool(run["transport_success"])
    ]
    return {
        "runs": n,
        "transport_success_rate": count_true("transport_success") / n,
        "timeout_rate": count_true("timeout_occurrence") / n,
        "valid_one_tool_request_rate": count_true("valid_bounded_first_step") / n,
        "valid_bounded_first_step_count": count_true("valid_bounded_first_step"),
        "zero_tool_terminal_response_rate": count_true("zero_tool_terminal_response") / n,
        "multi_tool_safety_shape_rate": count_true("multi_tool_safety_shape") / n,
        "invalid_unknown_tool_request_rate": count_true("invalid_unknown_tool_request") / n,
        "scope_incompatible_requested_path_rate": count_true(
            "scope_incompatible_requested_path"
        )
        / n,
        "timeout_count": count_true("timeout_occurrence"),
        "multi_tool_count": count_true("multi_tool_safety_shape"),
        "invalid_unknown_tool_count": count_true("invalid_unknown_tool_request"),
        "scope_incompatible_count": count_true("scope_incompatible_requested_path"),
        "median_elapsed_completed_seconds": (
            round(statistics.median(completed_elapsed), 6)
            if completed_elapsed
            else None
        ),
        "max_elapsed_seconds": round(
            max(float(run["elapsed_seconds"]) for run in runs), 6
        ),
        "executed_repository_writes": count_true("write_executed"),
    }


def summarize_all(runs: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {
        variant: summarize_variant([run for run in runs if run["variant"] == variant])
        for variant in VARIANTS
    }


def _candidate_meets_threshold(
    candidate: dict[str, object],
    stable: dict[str, object],
) -> bool:
    fixed = (
        candidate["multi_tool_count"] == 0
        and candidate["scope_incompatible_count"] == 0
        and candidate["executed_repository_writes"] == 0
        and candidate["valid_bounded_first_step_count"] >= 9
        and candidate["timeout_count"] <= 1
        and candidate["invalid_unknown_tool_count"] == 0
    )
    safety_not_worse = (
        candidate["multi_tool_count"] <= stable["multi_tool_count"]
        and candidate["scope_incompatible_count"] <= stable["scope_incompatible_count"]
        and candidate["invalid_unknown_tool_count"] <= stable["invalid_unknown_tool_count"]
    )
    candidate_median = candidate["median_elapsed_completed_seconds"]
    stable_median = stable["median_elapsed_completed_seconds"]
    materially_better = (
        candidate["valid_bounded_first_step_count"] >= stable["valid_bounded_first_step_count"] + 2
        or candidate["timeout_count"] <= stable["timeout_count"] - 2
        or (
            candidate_median is not None
            and stable_median is not None
            and candidate_median <= stable_median * 0.75
        )
    )
    return bool(fixed and safety_not_worse and materially_better)


def promotion_recommendation(summary: dict[str, dict[str, object]]) -> str:
    stable = summary[VARIANT_STABLE]
    a_ok = _candidate_meets_threshold(summary[VARIANT_BRIEF], stable)
    b_ok = _candidate_meets_threshold(summary[VARIANT_BRIEF_ONE_STEP], stable)
    if a_ok:
        return "RECOMMEND SEPARATE PRODUCTION TASK: Candidate A - Deterministic Worker Brief"
    if b_ok:
        return (
            "RECOMMEND SEPARATE PRODUCTION TASK: "
            "Candidate B - Deterministic Worker Brief + One-Step Instruction"
        )
    return "NO PROMOTION RECOMMENDATION"


def _rate(value: object) -> str:
    return f"{float(value) * 100:.1f}%"


def render_evidence(data: dict[str, object]) -> str:
    summary = data["summary"]
    assert isinstance(summary, dict)
    labels = {
        VARIANT_STABLE: "Stable - Full Task",
        VARIANT_BRIEF: "Candidate A - Deterministic Worker Brief",
        VARIANT_BRIEF_ONE_STEP: (
            "Candidate B - Deterministic Worker Brief + One-Step Instruction"
        ),
    }
    lines = [
        "# QH-V2-WORKER-ROB-002 Evidence",
        "",
        "## Procedure",
        "",
        f"Exact experiment command: `{EXPERIMENT_COMMAND}`",
        "",
        "The three variants were run in rotating interleaved order for 10 measured runs each. Only `OllamaToolSession.start()` was requested. Returned ToolRequests were inspected but never executed.",
        "",
        "Stable runtime settings:",
        "",
        f"- model: `{data['runtime']['model']}`",
        f"- think: `{data['runtime']['think']}`",
        f"- timeout: `{data['runtime']['timeout_seconds']}` seconds",
        "- tools: current production `read_repo_text` and `write_repo_text` schema",
        "",
        "Exact one-step instruction:",
        "",
        f"`{data['one_step_instruction']}`",
        "",
        "The Worker Brief is a deterministic exact-section projection. The original tracked Task remains the Source of Truth and Verification / Final Gate authority remains Harness-owned.",
        "",
        "## Summary",
        "",
        "| Variant | transport-success rate | timeout rate | valid bounded first step | zero-tool terminal | multi-tool | invalid tool | scope-incompatible | median completed s | max s | Worker writes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS:
        metrics = summary[variant]
        lines.append(
            "| "
            + labels[variant]
            + " | "
            + " | ".join(
                [
                    _rate(metrics["transport_success_rate"]),
                    _rate(metrics["timeout_rate"]),
                    f"{metrics['valid_bounded_first_step_count']}/{metrics['runs']}",
                    _rate(metrics["zero_tool_terminal_response_rate"]),
                    _rate(metrics["multi_tool_safety_shape_rate"]),
                    _rate(metrics["invalid_unknown_tool_request_rate"]),
                    _rate(metrics["scope_incompatible_requested_path_rate"]),
                    str(metrics["median_elapsed_completed_seconds"]),
                    str(metrics["max_elapsed_seconds"]),
                    str(metrics["executed_repository_writes"]),
                ]
            )
            + " |"
        )
    recommendation = promotion_recommendation(summary)
    lines.extend(
        [
            "",
            "## Safety / Interpretation",
            "",
            "- No returned ToolRequest was executed by this benchmark; `write_executed` is false for every run.",
            "- Read-path validity and write ChangeScope/lifecycle-path validity were reviewed against existing Harness contracts without invoking the production tool executor.",
            "- A valid bounded first step is an interaction-quality metric only. It is not Repository PASS, Verification PASS, or Final Gate PASS.",
            "- QH-V2-WORKER-ROB-001 remains CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED and is not reinterpreted as success.",
            "",
            "## Promotion Recommendation",
            "",
            recommendation,
            "",
            "The recommendation is only for a separate future production Task. This experiment performs no production promotion.",
            "",
            "`GLOBALIZATION = NOT AUTHORIZED` remains unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def run_experiment(
    repo_root: Path,
    task_id: str,
    results_path: Path,
    evidence_path: Path,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    task_path = repo_root / "tasks" / f"{task_id}.md"
    task_markdown = task_path.read_text(encoding="utf-8")
    prompts = build_variant_prompts(task_markdown)
    runs: list[dict[str, object]] = []

    for variant, run_index in interleaved_plan(10):
        record = measure_initial_step(
            repo_root,
            task_id,
            task_markdown,
            variant,
            run_index,
            prompts[variant],
        )
        runs.append(record)
        print(
            f"{variant} run={run_index} elapsed={record['elapsed_seconds']} "
            f"transport={record['transport_success']} timeout={record['timeout_occurrence']} "
            f"tools={record['tool_request_count']} valid={record['valid_bounded_first_step']}"
        )

    data: dict[str, object] = {
        "task_id": task_id,
        "task_sha256": hashlib.sha256(task_markdown.encode("utf-8")).hexdigest(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "base_url": DEFAULT_BASE_URL,
            "model": DEFAULT_MODEL,
            "think": False,
            "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
            "tools": [tool.name for tool in _runner_tools()],
        },
        "one_step_instruction": ONE_STEP_INSTRUCTION,
        "required_brief_sections": list(REQUIRED_BRIEF_SECTIONS),
        "interleaving": "rotating round-robin stable/A/B",
        "runs": runs,
        "summary": summarize_all(runs),
    }

    results_path = (repo_root / results_path).resolve()
    evidence_path = (repo_root / evidence_path).resolve()
    results_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    evidence_path.write_text(render_evidence(data), encoding="utf-8")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="QH-V2-WORKER-ROB-002 experiment")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID)
    parser.add_argument("--results", default="docs/WORKER_ROB_002_RESULTS.json")
    parser.add_argument("--evidence", default="docs/WORKER_ROB_002_EVIDENCE.md")
    args = parser.parse_args()
    run_experiment(
        Path(args.repo_root),
        args.task_id,
        Path(args.results),
        Path(args.evidence),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
