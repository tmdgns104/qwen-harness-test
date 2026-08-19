import tempfile
import unittest
from pathlib import Path

from tools.repo_tools import read_repo_text, write_repo_text


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

    def test_read_repo_text_rejects_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "folder").mkdir()

            with self.assertRaises(ValueError):
                read_repo_text(repo, "folder")

    def test_read_repo_text_rejects_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "invalid.txt").write_bytes(b"\xff\xfe\xfa")

            with self.assertRaises(UnicodeDecodeError):
                read_repo_text(repo, "invalid.txt")

    def test_write_repo_text_creates_allowed_file_with_exact_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            content = "hello\nworld\n"

            result = write_repo_text(
                repo,
                "allowed.txt",
                content,
                allowed_changes=("allowed.txt",),
                forbidden_changes=(),
            )

            self.assertEqual((repo / "allowed.txt").read_text(encoding="utf-8"), content)
            self.assertEqual(result, "allowed.txt")

    def test_write_repo_text_replaces_allowed_file_with_exact_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "allowed.txt"
            target.write_text("OLD\n", encoding="utf-8")
            content = "NEW\nCONTENT\n"

            result = write_repo_text(
                repo,
                "allowed.txt",
                content,
                allowed_changes=("allowed.txt",),
                forbidden_changes=(),
            )

            self.assertEqual(target.read_text(encoding="utf-8"), content)
            self.assertEqual(result, "allowed.txt")

    def test_write_repo_text_rejects_path_outside_allowed_changes_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "blocked.txt"
            target.write_text("ORIGINAL\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                write_repo_text(
                    repo,
                    "blocked.txt",
                    "CHANGED\n",
                    allowed_changes=("allowed.txt",),
                    forbidden_changes=(),
                )

            self.assertEqual(target.read_text(encoding="utf-8"), "ORIGINAL\n")

    def test_write_repo_text_forbidden_changes_override_allowed_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "blocked.txt"
            target.write_text("ORIGINAL\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                write_repo_text(
                    repo,
                    "blocked.txt",
                    "CHANGED\n",
                    allowed_changes=("blocked.txt",),
                    forbidden_changes=("blocked.txt",),
                )

            self.assertEqual(target.read_text(encoding="utf-8"), "ORIGINAL\n")

    def test_write_repo_text_rejects_absolute_path_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            outside = root / "outside.txt"
            outside.write_text("ORIGINAL\n", encoding="utf-8")
            absolute = str(outside)

            with self.assertRaises(ValueError):
                write_repo_text(
                    repo,
                    absolute,
                    "CHANGED\n",
                    allowed_changes=(Path(absolute).as_posix(),),
                    forbidden_changes=(),
                )

            self.assertEqual(outside.read_text(encoding="utf-8"), "ORIGINAL\n")

    def test_write_repo_text_rejects_path_traversal_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            outside = root / "outside.txt"
            outside.write_text("ORIGINAL\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                write_repo_text(
                    repo,
                    "../outside.txt",
                    "CHANGED\n",
                    allowed_changes=("../outside.txt",),
                    forbidden_changes=(),
                )

            self.assertEqual(outside.read_text(encoding="utf-8"), "ORIGINAL\n")

    def test_write_repo_text_rejects_directory_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "folder"
            target.mkdir()

            with self.assertRaises(ValueError):
                write_repo_text(
                    repo,
                    "folder",
                    "CHANGED\n",
                    allowed_changes=("folder",),
                    forbidden_changes=(),
                )

            self.assertTrue(target.is_dir())


if __name__ == "__main__":
    unittest.main()
