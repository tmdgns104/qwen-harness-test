from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from harness_core import GitBaseline, VerificationContract, _require_git_top_level, _run_git, assemble_evidence, evaluate_final_gate, get_changed_paths, parse_change_scope, parse_verification_commands, run_verification_commands


CURRENT_TASK_RE = re.compile(r"Current Task:\s+(\S+)", re.MULTILINE)


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


def command_start(repo_root: Path, target_task_id: str) -> int:
    _require_git_top_level(str(repo_root))
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", target_task_id) is None:
        raise ValueError("Invalid Task ID")

    target_path = repo_root / "tasks" / f"{target_task_id}.md"
    if not target_path.is_file():
        raise FileNotFoundError(f"Task file not found: {target_path.relative_to(repo_root)}")

    status_path = repo_root / "STATUS.md"
    markdown = status_path.read_text(encoding="utf-8")
    current_line = _require_single_lifecycle_line(markdown, "Current Task")
    previous_line = _require_single_lifecycle_line(markdown, "Previous Task")
    next_planned_line = _require_single_lifecycle_line(markdown, "Next Planned Task")

    current_match = CURRENT_TASK_RE.match(current_line)
    if current_match is None:
        raise ValueError("Current Task line is malformed")

    baseline_head = _run_git(str(repo_root), ("rev-parse", "HEAD")).stdout.strip()
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
    print(f"Previous Task: {current_match.group(1)}")
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

    if command_review(repo_root) != 0:
        return 1

    commit_type = _run_git(str(repo_root), ("cat-file", "-t", commit)).stdout.strip()
    if commit_type != "commit":
        raise ValueError(f"Not a Git commit: {commit}")

    head = _run_git(str(repo_root), ("rev-parse", "HEAD")).stdout.strip()
    resolved_commit = _run_git(str(repo_root), ("rev-parse", commit)).stdout.strip()
    if resolved_commit != head:
        raise ValueError(f"Completion commit must match current HEAD: {head}")

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
        baseline_head = _run_git(str(repo_root), ("rev-parse", "HEAD")).stdout.strip()
    else:
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
    changed_paths = get_changed_paths(str(repo_root), baseline)
    verification_contract = parse_verification_commands(task_markdown)
    verification_results = run_verification_commands(verification_contract, str(repo_root))
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Qwen Harness workflow utility")
    parser.add_argument("command", choices=("status", "preflight", "verify", "review", "start", "close"))
    parser.add_argument("task_id", nargs="?")
    args = parser.parse_args()
    repo_root = Path.cwd().resolve()
    try:
        if args.command == "start":
            if args.task_id is None:
                raise ValueError("start requires a Task ID")
            return command_start(repo_root, args.task_id)
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
