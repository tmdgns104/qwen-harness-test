from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from harness_core import GitBaseline, _require_git_top_level, _run_git, get_changed_paths, parse_change_scope


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Qwen Harness workflow utility")
    parser.add_argument("command", choices=("status",))
    args = parser.parse_args()
    repo_root = Path.cwd().resolve()
    try:
        if args.command == "status":
            return command_status(repo_root)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
