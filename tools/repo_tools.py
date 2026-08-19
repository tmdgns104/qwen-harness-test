from pathlib import Path


def read_repo_text(repo_root: str | Path, relative_path: str) -> str:
    requested = Path(relative_path)
    if requested.is_absolute():
        raise ValueError("absolute paths are not allowed")
    path = Path(repo_root) / requested
    return path.read_text(encoding="utf-8")
