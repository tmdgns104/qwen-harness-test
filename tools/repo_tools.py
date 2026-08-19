from pathlib import Path


def read_repo_text(repo_root: str | Path, relative_path: str) -> str:
    path = Path(repo_root) / relative_path
    return path.read_text(encoding="utf-8")
