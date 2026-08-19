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


if __name__ == "__main__":
    unittest.main()
