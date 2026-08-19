from pathlib import Path


def read_repo_text(repo_root: str | Path, relative_path: str) -> str:
    requested = Path(relative_path)
    if requested.is_absolute():
        raise ValueError("absolute paths are not allowed")
    root = Path(repo_root).resolve()
    path = (root / requested).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes repository root") from exc
    if path.is_dir():
        raise ValueError("directories are not readable as text files")
    return path.read_text(encoding="utf-8")


def write_repo_text(
    repo_root: str | Path,
    relative_path: str,
    content: str,
    *,
    allowed_changes: tuple[str, ...],
    forbidden_changes: tuple[str, ...],
) -> str:
    requested = Path(relative_path)
    if requested.is_absolute():
        raise ValueError("absolute paths are not allowed")
    normalized = requested.as_posix()
    if normalized in forbidden_changes:
        raise ValueError("path is forbidden")
    if normalized not in allowed_changes:
        raise ValueError("path is not allowed")
    path = Path(repo_root) / requested
    path.write_text(content, encoding="utf-8")
    return requested.as_posix()
