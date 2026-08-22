from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from harness_core import GitBaseline, VerificationContract, _require_git_top_level, _run_git, assemble_evidence, capture_git_baseline, evaluate_final_gate, get_changed_paths, parse_change_scope, parse_verification_commands, run_verification_commands


TASK_ID_PATTERN = r"[A-Za-z0-9][A-Za-z0-9._-]*"
CURRENT_TASK_RE = re.compile(r"Current Task:\s+(\S+)", re.MULTILINE)
COMPLETED_CURRENT_TASK_RE = re.compile(
    rf"Current Task: (?P<task_id>{TASK_ID_PATTERN})"
    r" - COMPLETE - VERIFIED - commit \S+"
)
APPROVED_TASK_STATUS = "APPROVED - READY FOR CONTRACT BASELINE"
TASK_DRAFT_STATUS = "DRAFT - HUMAN REVIEW REQUIRED"


def _load_current_task(repo_root: Path) -> tuple[str, Path, str]:
    status_path = repo_root / "STATUS.md"
    markdown = status_path.read_text(encoding="utf-8")
    match = CURRENT_TASK_RE.match(markdown)
    if match is None:
        raise ValueError("Current Task not found in STATUS.md")
    task_id = match.group(1)
    task_path = repo_root / "tasks" / f"{task_id}.md"
    if not task_path.is_file():
        raise FileNotFoundError(f"Task file not found: {task_path.relative_to(repo_root)}")
    return task_id, task_path, task_path.read_text(encoding="utf-8")


def _require_single_lifecycle_line(markdown: str, label: str) -> str:
    prefix = f"{label}:"
    matches = [line for line in markdown.splitlines() if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {label} line in STATUS.md; found {len(matches)}")
    return matches[0]


def _require_completed_current_task(current_line: str) -> re.Match[str]:
    match = COMPLETED_CURRENT_TASK_RE.fullmatch(current_line)
    if match is None:
        raise ValueError(
            "Current Task must be exactly COMPLETE - VERIFIED before start"
        )
    return match


def _require_approved_target_status(markdown: str) -> None:
    lines = markdown.splitlines()
    status_headings = [
        index for index, line in enumerate(lines) if line == "## Status"
    ]
    if len(status_headings) != 1:
        raise ValueError(
            "Expected exactly one target Task Status heading; "
            f"found {len(status_headings)}"
        )

    status_heading = status_headings[0]
    next_heading = next(
        (
            index
            for index in range(status_heading + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        len(lines),
    )
    status_values = [
        line
        for line in lines[status_heading + 1 : next_heading]
        if line.strip()
    ]
    if len(status_values) != 1:
        raise ValueError(
            "Expected exactly one target Task Status value; "
            f"found {len(status_values)}"
        )
    if status_values[0] != APPROVED_TASK_STATUS:
        raise ValueError(
            f"Target Task Status must be exactly {APPROVED_TASK_STATUS}"
        )


def _task_draft_markdown(task_id: str) -> str:
    placeholder = "HUMAN REVIEW REQUIRED. Replace this placeholder before approval."
    return (
        f"# {task_id} - Human-Review Task Draft\n\n"
        "## Status\n\n"
        f"{TASK_DRAFT_STATUS}\n\n"
        "This file is only a scaffold. Human review and explicit approval are required before start.\n\n"
        "## Problem\n\n"
        f"{placeholder}\n\n"
        "## Goal\n\n"
        f"{placeholder}\n\n"
        "## Architecture Basis\n\n"
        f"{placeholder}\n\n"
        "## Dependencies\n\n"
        f"{placeholder}\n\n"
        "## Scope\n\n"
        f"{placeholder}\n\n"
        "## Allowed Changes\n\n"
        f"{placeholder}\n\n"
        "## Forbidden Changes\n\n"
        f"{placeholder}\n\n"
        "## Acceptance Criteria\n\n"
        f"{placeholder}\n\n"
        "## Verification\n\n"
        "HUMAN REVIEW REQUIRED. Add explicitly marked commands before approval.\n\n"
        "## Evidence Requirements\n\n"
        f"{placeholder}\n\n"
        "## Stop Conditions\n\n"
        f"{placeholder}\n\n"
        "## Next Task\n\n"
        f"{placeholder}\n"
    )


def command_task_new(repo_root: Path, task_id: str) -> int:
    if re.fullmatch(TASK_ID_PATTERN, task_id) is None:
        raise ValueError("Invalid Task ID")

    tasks_dir = repo_root / "tasks"
    if not tasks_dir.is_dir():
        raise FileNotFoundError("Task directory not found: tasks")

    task_path = tasks_dir / f"{task_id}.md"
    try:
        with task_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(_task_draft_markdown(task_id))
    except FileExistsError as exc:
        raise ValueError(f"Task file already exists: tasks/{task_id}.md") from exc

    print(f"Created Task Draft: tasks/{task_id}.md")
    print(f"Status: {TASK_DRAFT_STATUS}")
    return 0


def command_doctor(repo_root: Path) -> int:
    print(f"PYTHON_RUNTIME: PASS Python {sys.version.split()[0]}")
    return 0


def command_start(repo_root: Path, target_task_id: str) -> int:
    _require_git_top_level(str(repo_root))
    if re.fullmatch(TASK_ID_PATTERN, target_task_id) is None:
        raise ValueError("Invalid Task ID")

    target_path = repo_root / "tasks" / f"{target_task_id}.md"
    if not target_path.is_file():
        raise FileNotFoundError(f"Task file not found: {target_path.relative_to(repo_root)}")

    status_path = repo_root / "STATUS.md"
    markdown = status_path.read_text(encoding="utf-8")
    current_line = _require_single_lifecycle_line(markdown, "Current Task")
    previous_line = _require_single_lifecycle_line(markdown, "Previous Task")
    next_planned_line = _require_single_lifecycle_line(markdown, "Next Planned Task")

    current_match = _require_completed_current_task(current_line)
    target_markdown = target_path.read_text(encoding="utf-8")
    _require_approved_target_status(target_markdown)

    baseline_head = capture_git_baseline(str(repo_root)).head
    previous_value = current_line.removeprefix("Current Task: ")
    lines = markdown.splitlines()
    current_index = lines.index(current_line)
    previous_index = lines.index(previous_line)
    next_planned_index = lines.index(next_planned_line)
    baseline_indexes = [index for index, line in enumerate(lines) if line.startswith("Task Baseline:")]
    if len(baseline_indexes) > 1:
        raise ValueError(f"Expected at most one Task Baseline line in STATUS.md; found {len(baseline_indexes)}")
    lines[current_index] = f"Current Task: {target_task_id} - ACTIVE"
    lines[previous_index] = f"Previous Task: {previous_value}"
    lines[next_planned_index] = "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED"
    if baseline_indexes:
        lines[baseline_indexes[0]] = f"Task Baseline: {baseline_head}"
    else:
        lines.insert(next_planned_index + 1, f"Task Baseline: {baseline_head}")
    updated = "\n".join(lines) + ("\n" if markdown.endswith("\n") else "")
    status_path.write_text(updated, encoding="utf-8")

    print(f"Started Task: {target_task_id}")
    print(f"Previous Task: {current_match.group('task_id')}")
    return 0


def _completed_task_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    headings = [index for index, line in enumerate(lines) if line == "## Status"]
    if len(headings) != 1:
        raise ValueError(f"Expected exactly one Task Status heading; found {len(headings)}")
    status_index = headings[0] + 1
    while status_index < len(lines) and not lines[status_index].strip():
        status_index += 1
    if status_index >= len(lines):
        raise ValueError("Task Status value not found")
    lines[status_index] = "COMPLETE - VERIFIED"
    return "\n".join(lines) + ("\n" if markdown.endswith("\n") else "")


def command_close(repo_root: Path, commit: str) -> int:
    _require_git_top_level(str(repo_root))

    resolved_commit = _run_git(str(repo_root), ("rev-parse", commit)).stdout.strip()
    commit_type = _run_git(
        str(repo_root),
        ("cat-file", "-t", resolved_commit),
    ).stdout.strip()
    if commit_type != "commit":
        raise ValueError(f"Not a Git commit: {commit}")

    entry_baseline = capture_git_baseline(str(repo_root))
    if resolved_commit != entry_baseline.head:
        raise ValueError(
            f"Completion commit must match current HEAD: {entry_baseline.head}"
        )

    if command_review(repo_root) != 0:
        return 1

    post_verification_baseline = capture_git_baseline(str(repo_root))
    if post_verification_baseline.head != resolved_commit:
        raise ValueError(
            "Repository HEAD changed during Verification: "
            f"{post_verification_baseline.head}"
        )

    task_id, task_path, task_markdown = _load_current_task(repo_root)
    status_path = repo_root / "STATUS.md"
    markdown = status_path.read_text(encoding="utf-8")
    current_line = _require_single_lifecycle_line(markdown, "Current Task")
    _require_single_lifecycle_line(markdown, "Previous Task")
    _require_single_lifecycle_line(markdown, "Next Planned Task")

    if not current_line.startswith(f"Current Task: {task_id} - ACTIVE"):
        raise ValueError("Current Task is not ACTIVE")

    updated_task = _completed_task_markdown(task_markdown)
    lines = markdown.splitlines()
    current_index = lines.index(current_line)
    lines[current_index] = f"Current Task: {task_id} - COMPLETE - VERIFIED - commit {commit}"
    updated_status = "\n".join(lines) + ("\n" if markdown.endswith("\n") else "")

    status_path.write_text(updated_status, encoding="utf-8")
    task_path.write_text(updated_task, encoding="utf-8")
    print(f"Closed Task: {task_id}")
    print(f"Completion Commit: {commit}")
    return 0


def command_status(repo_root: Path) -> int:
    _require_git_top_level(str(repo_root))
    task_id, task_path, task_markdown = _load_current_task(repo_root)
    scope = parse_change_scope(task_markdown)
    head = _run_git(str(repo_root), ("rev-parse", "HEAD")).stdout.strip()
    changed_paths = get_changed_paths(str(repo_root), GitBaseline(head=head))
    print(f"Current Task: {task_id}")
    print(f"Task File: {task_path.relative_to(repo_root).as_posix()}")
    print(f"Git State: {"clean" if not changed_paths else "dirty"}")
    print("Changed Paths:")
    if changed_paths:
        for path in changed_paths:
            print(f"- {path}")
    else:
        print("- none")
    print("Allowed Changes:")
    for pattern in scope.allowed:
        print(f"- {pattern}")
    print("Forbidden Changes:")
    for pattern in scope.forbidden:
        print(f"- {pattern}")
    return 0


def command_preflight(repo_root: Path) -> int:
    _require_git_top_level(str(repo_root))
    task_id, task_path, task_markdown = _load_current_task(repo_root)
    parse_change_scope(task_markdown)
    git_status = _run_git(str(repo_root), ("status", "--porcelain")).stdout
    print(f"Current Task: {task_id}")
    print(f"Task File: {task_path.relative_to(repo_root).as_posix()}")
    print(f"Git State: {"clean" if not git_status.strip() else "dirty"}")
    print("Task Scope: valid")
    return 0


def command_verify(repo_root: Path) -> int:
    _require_git_top_level(str(repo_root))
    task_id, task_path, task_markdown = _load_current_task(repo_root)
    contract = parse_verification_commands(task_markdown)
    results = run_verification_commands(contract, str(repo_root))
    print(f"Current Task: {task_id}")
    print(f"Task File: {task_path.relative_to(repo_root).as_posix()}")
    for result in results:
        print(f"Command: {result.command}")
        print(f"Exit Code: {result.exit_code}")
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return 0 if all(result.exit_code == 0 for result in results) else 1


def command_review(repo_root: Path, baseline_commit: str | None = None) -> int:
    _require_git_top_level(str(repo_root))
    task_id, task_path, task_markdown = _load_current_task(repo_root)
    scope = parse_change_scope(task_markdown)
    if baseline_commit is None:
        status_markdown = (repo_root / "STATUS.md").read_text(encoding="utf-8")
        baseline_line = _require_single_lifecycle_line(status_markdown, "Task Baseline")
        baseline_commit = baseline_line.removeprefix("Task Baseline:").strip()
        if not baseline_commit:
            raise ValueError("Task Baseline is empty")
    baseline_head = _run_git(
        str(repo_root),
        ("rev-parse", "--verify", baseline_commit),
    ).stdout.strip()
    baseline_type = _run_git(
        str(repo_root),
        ("cat-file", "-t", baseline_head),
    ).stdout.strip()
    if baseline_type != "commit":
        raise ValueError("review baseline must resolve to a commit")
    baseline = GitBaseline(head=baseline_head)
    verification_contract = parse_verification_commands(task_markdown)
    verification_results = run_verification_commands(verification_contract, str(repo_root))
    changed_paths = get_changed_paths(str(repo_root), baseline)
    evidence = assemble_evidence(scope, baseline, changed_paths, verification_results)
    diff_result = run_verification_commands(VerificationContract(commands=("git diff --check",)), str(repo_root))[0]
    print(f"Current Task: {task_id}")
    print(f"Task File: {task_path.relative_to(repo_root).as_posix()}")
    print("Changed Paths:")
    if evidence.path_scope_results:
        for item in evidence.path_scope_results:
            state = "allowed" if item.allowed else "forbidden"
            print(f"- {item.path}: {state}")
    else:
        print("- none")
    print("Verification:")
    for result in verification_results:
        print(f"- {result.command}: exit {result.exit_code}")
    print(f"Diff Check: exit {diff_result.exit_code}")
    unexpected = any(not item.allowed for item in evidence.path_scope_results)
    final_gate = evaluate_final_gate(evidence)
    print(f"Unexpected Changed Paths: {"yes" if unexpected else "no"}")
    print(f"Final Gate: {"PASS" if final_gate.passed else "FAIL"}")
    if final_gate.failures:
        print(f"Final Gate Failures: {", ".join(final_gate.failures)}")
    passed = final_gate.passed and diff_result.exit_code == 0
    return 0 if passed else 1


def command_run(
    repo_root: Path,
    task_id: str,
    *,
    retry_callable=None,
) -> int:
    """Run the current Task through bounded Retry orchestration.

    This reports Worker interaction state only.
    It does not perform Verification, Final Gate, Task completion, or commit.
    """
    from tools.retry_runner import RetryOutcomeKind, run_with_retry

    if retry_callable is None:
        retry_callable = run_with_retry

    outcome = retry_callable(repo_root, task_id)
    runner_result = outcome.runner_result

    failure_kind = (
        runner_result.failure_kind.name
        if runner_result.failure_kind is not None
        else "NONE"
    )

    print(f"Task: {task_id}")
    print(f"Outcome: {outcome.outcome_kind.name}")
    print(f"Attempts: {outcome.attempts_consumed}")
    print(f"Failure Kind: {failure_kind}")
    print(
        "Write Side Effect Risk: "
        + ("YES" if outcome.write_side_effect_risk else "NO")
    )

    if runner_result.output_text:
        print(f"Worker Output: {runner_result.output_text}")

    if outcome.error:
        print(f"Error: {outcome.error}")

    return 0 if outcome.outcome_kind is RetryOutcomeKind.NORMAL else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Qwen Harness workflow utility")
    parser.add_argument("command", choices=("status", "preflight", "verify", "review", "start", "close", "run", "task-new", "doctor"))
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()
    repo_root = Path.cwd().resolve()
    try:
        if args.command == "doctor":
            if args.task_id is not None:
                raise ValueError("doctor does not accept a Task ID")
            return command_doctor(repo_root)
        if args.command == "task-new":
            if args.task_id is None:
                raise ValueError("task-new requires a Task ID")
            return command_task_new(repo_root, args.task_id)
        if args.command == "start":
            if args.task_id is None:
                raise ValueError("start requires a Task ID")
            return command_start(repo_root, args.task_id)
        if args.command == "run":
            if args.task_id is None:
                raise ValueError("run requires a Task ID")
            return command_run(repo_root, args.task_id)
        if args.command == "close":
            if args.task_id is None:
                raise ValueError("close requires a commit")
            return command_close(repo_root, args.task_id)
        if args.command == "review":
            return command_review(repo_root, args.task_id)
        if args.task_id is not None:
            raise ValueError(f"{args.command} does not accept a Task ID")
        if args.command == "status":
            return command_status(repo_root)
        if args.command == "preflight":
            return command_preflight(repo_root)
        if args.command == "verify":
            return command_verify(repo_root)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())