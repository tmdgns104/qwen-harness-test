from __future__ import annotations

import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class GitRepositoryCopy:
    def __init__(self, seed_path: Path) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self._tempdir.name) / "repo"
        shutil.copytree(seed_path, self.path)

    def cleanup(self) -> None:
        self._tempdir.cleanup()


class GitSeedRepository:
    def __init__(
        self,
        files: Mapping[str, str],
        *,
        user_email: str = "fixture@example.test",
        user_name: str = "Git Fixture Test",
    ) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self._tempdir.name) / "seed"
        self.path.mkdir()

        run_git(self.path, "init", "-q")
        run_git(self.path, "config", "user.email", user_email)
        run_git(self.path, "config", "user.name", user_name)

        for relative_path, content in files.items():
            target = self.path / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        run_git(self.path, "add", "--", ".")
        run_git(self.path, "commit", "-q", "--allow-empty", "-m", "baseline")

    def new_copy(self) -> GitRepositoryCopy:
        return GitRepositoryCopy(self.path)

    def cleanup(self) -> None:
        self._tempdir.cleanup()
