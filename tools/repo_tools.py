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
    return path.read_text(encoding="utf-8")
