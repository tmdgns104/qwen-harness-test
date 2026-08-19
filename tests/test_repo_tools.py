import tempfile
import unittest
from pathlib import Path

from tools.repo_tools import read_repo_text


class RepositoryReadToolsTests(unittest.TestCase):
    def test_read_repo_text_returns_exact_utf8_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            expected = "첫 줄\nsecond line\n"
            (repo / "notes.txt").write_text(expected, encoding="utf-8")

            actual = read_repo_text(repo, "notes.txt")

            self.assertEqual(actual, expected)

    def test_read_repo_text_rejects_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            outside = root / "outside.txt"
            outside.write_text("OUTSIDE\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_repo_text(repo, str(outside))

    def test_read_repo_text_rejects_path_traversal_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            outside = root / "outside.txt"
            outside.write_text("OUTSIDE\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_repo_text(repo, "../outside.txt")

    def test_read_repo_text_rejects_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)

            with self.assertRaises(FileNotFoundError):
                read_repo_text(repo, "missing.txt")


if __name__ == "__main__":
    unittest.main()
