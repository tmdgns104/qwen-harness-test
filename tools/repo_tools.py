from pathlib import Path

from tools.harness_core import ChangeScope, resolve_scoped_write_target


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
    scope = ChangeScope(
        allowed=allowed_changes,
        forbidden=forbidden_changes,
    )
    path = resolve_scoped_write_target(repo_root, relative_path, scope)
    if path.is_dir():
        raise ValueError("directories are not writable as text files")
    path.write_text(content, encoding="utf-8")
    return requested.as_posix()
