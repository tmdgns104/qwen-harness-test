from pathlib import Path

path = Path("tools/qh.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one replacement target, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    '''COMPLETED_CURRENT_TASK_RE = re.compile(
    rf"Current Task: (?P<task_id>{TASK_ID_PATTERN})"
    r" - COMPLETE - VERIFIED - commit \\S+"
)
APPROVED_TASK_STATUS = "APPROVED - READY FOR CONTRACT BASELINE"
''',
    '''COMPLETED_CURRENT_TASK_RE = re.compile(
    rf"Current Task: (?P<task_id>{TASK_ID_PATTERN})"
    r" - COMPLETE - VERIFIED - commit \\S+"
)
UNSUCCESSFUL_TASK_STATUS = "CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED"
UNSUCCESSFUL_CURRENT_TASK_RE = re.compile(
    rf"Current Task: (?P<task_id>{TASK_ID_PATTERN})"
    rf" - {re.escape(UNSUCCESSFUL_TASK_STATUS)} - evidence (?P<evidence>\\S+)"
)
APPROVED_TASK_STATUS = "APPROVED - READY FOR CONTRACT BASELINE"
''',
)

replace_once(
    '''def _require_completed_current_task(current_line: str) -> re.Match[str]:
    match = COMPLETED_CURRENT_TASK_RE.fullmatch(current_line)
    if match is None:
        raise ValueError(
            "Current Task must be exactly COMPLETE - VERIFIED before start"
        )
    return match


''',
    '''def _resolve_tracked_evidence(repo_root: Path, evidence_arg: str) -> str:
    if not evidence_arg or evidence_arg.strip() != evidence_arg:
        raise ValueError("Evidence path must be a non-empty Repository-relative path")

    evidence_path = Path(evidence_arg)
    if evidence_path.is_absolute():
        raise ValueError("Evidence path must be Repository-relative")

    resolved_repo = repo_root.resolve()
    resolved_evidence = (repo_root / evidence_path).resolve()
    try:
        relative = resolved_evidence.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError("Evidence path must remain inside Repository") from exc

    if not resolved_evidence.is_file():
        raise ValueError("Evidence path must exist as a regular file")

    relative_text = relative.as_posix()
    _run_git(
        str(repo_root),
        ("cat-file", "-e", f"HEAD:{relative_text}"),
    )
    return relative_text


def _require_startable_current_task(
    repo_root: Path,
    current_line: str,
) -> re.Match[str]:
    completed = COMPLETED_CURRENT_TASK_RE.fullmatch(current_line)
    if completed is not None:
        return completed

    unsuccessful = UNSUCCESSFUL_CURRENT_TASK_RE.fullmatch(current_line)
    if unsuccessful is not None:
        _resolve_tracked_evidence(repo_root, unsuccessful.group("evidence"))
        return unsuccessful

    raise ValueError(
        "Current Task must be exactly COMPLETE - VERIFIED or "
        "CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED before start"
    )


''',
)

replace_once(
    '    current_match = _require_completed_current_task(current_line)\n',
    '    current_match = _require_startable_current_task(repo_root, current_line)\n',
)

replace_once(
    '''def _completed_task_markdown(markdown: str) -> str:
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
    return "\\n".join(lines) + ("\\n" if markdown.endswith("\\n") else "")


''',
    '''def _task_markdown_with_status(markdown: str, status: str) -> str:
    lines = markdown.splitlines()
    headings = [index for index, line in enumerate(lines) if line == "## Status"]
    if len(headings) != 1:
        raise ValueError(f"Expected exactly one Task Status heading; found {len(headings)}")
    status_index = headings[0] + 1
    while status_index < len(lines) and not lines[status_index].strip():
        status_index += 1
    if status_index >= len(lines):
        raise ValueError("Task Status value not found")
    lines[status_index] = status
    return "\\n".join(lines) + ("\\n" if markdown.endswith("\\n") else "")


def _completed_task_markdown(markdown: str) -> str:
    return _task_markdown_with_status(markdown, "COMPLETE - VERIFIED")


def command_close_unsuccessful(repo_root: Path, evidence_arg: str) -> int:
    _require_git_top_level(str(repo_root))
    capture_git_baseline(str(repo_root))

    task_id, task_path, task_markdown = _load_current_task(repo_root)
    status_path = repo_root / "STATUS.md"
    markdown = status_path.read_text(encoding="utf-8")
    current_line = _require_single_lifecycle_line(markdown, "Current Task")
    _require_single_lifecycle_line(markdown, "Previous Task")
    _require_single_lifecycle_line(markdown, "Next Planned Task")

    expected_active = f"Current Task: {task_id} - ACTIVE"
    if current_line != expected_active:
        raise ValueError("Current Task is not exactly ACTIVE")

    evidence_path = _resolve_tracked_evidence(repo_root, evidence_arg)
    updated_task = _task_markdown_with_status(
        task_markdown,
        UNSUCCESSFUL_TASK_STATUS,
    )

    lines = markdown.splitlines()
    current_index = lines.index(current_line)
    lines[current_index] = (
        f"Current Task: {task_id} - {UNSUCCESSFUL_TASK_STATUS} "
        f"- evidence {evidence_path}"
    )
    updated_status = "\\n".join(lines) + ("\\n" if markdown.endswith("\\n") else "")

    status_path.write_text(updated_status, encoding="utf-8")
    task_path.write_text(updated_task, encoding="utf-8")
    print(f"Closed Task Unsuccessfully: {task_id}")
    print(f"Evidence: {evidence_path}")
    return 0


''',
)

replace_once(
    'parser.add_argument("command", choices=("status", "preflight", "verify", "review", "start", "close", "run", "task-new", "doctor"))',
    'parser.add_argument("command", choices=("status", "preflight", "verify", "review", "start", "close", "close-unsuccessful", "run", "task-new", "doctor"))',
)

replace_once(
    '''        if args.command == "close":
            if args.task_id is None:
                raise ValueError("close requires a commit")
            return command_close(repo_root, args.task_id)
''',
    '''        if args.command == "close":
            if args.task_id is None:
                raise ValueError("close requires a commit")
            return command_close(repo_root, args.task_id)
        if args.command == "close-unsuccessful":
            if args.task_id is None:
                raise ValueError("close-unsuccessful requires an Evidence path")
            return command_close_unsuccessful(repo_root, args.task_id)
''',
)

path.write_text(text, encoding="utf-8", newline="\n")
print("updated tools/qh.py")
