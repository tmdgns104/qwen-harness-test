from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = REPO_ROOT / "qh.cmd"
CMD_EXE = shutil.which("cmd.exe") or shutil.which("cmd")


class WindowsWorkflowStaticContractTests(unittest.TestCase):
    def test_launcher_is_a_three_line_transparent_wrapper(self):
        lines = self._launcher_lines()

        self.assertEqual(
            lines,
            [
                "@echo off",
                'python "%~dp0tools\\qh.py" %*',
                "exit /b %ERRORLEVEL%",
            ],
        )

    def test_launcher_quotes_its_own_path_and_forwards_arguments_once(self):
        launcher = LAUNCHER_PATH.read_text(encoding="utf-8")

        self.assertIn('"%~dp0tools\\qh.py"', launcher)
        self.assertEqual(launcher.count("%*"), 1)
        self.assertEqual(launcher.lower().count("python "), 1)

    def test_launcher_contains_no_independent_authority_or_environment_mutation(self):
        launcher = LAUNCHER_PATH.read_text(encoding="utf-8").lower()

        for forbidden in (
            "git ",
            "setx ",
            "reg ",
            "pushd ",
            "popd ",
            "cd /d",
            "start ",
            "call ",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, launcher)

    @staticmethod
    def _launcher_lines() -> list[str]:
        return [
            line.rstrip()
            for line in LAUNCHER_PATH.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]


@unittest.skipUnless(
    os.name == "nt" and CMD_EXE is not None,
    "requires Windows cmd.exe execution",
)
class WindowsWorkflowExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="qh launcher repository path with spaces ",
        )
        self.addCleanup(self.temp.cleanup)
        self.repo_root = Path(self.temp.name)
        tools_dir = self.repo_root / "tools"
        tools_dir.mkdir()
        shutil.copyfile(LAUNCHER_PATH, self.repo_root / "qh.cmd")
        (tools_dir / "qh.py").write_text(
            "import json\n"
            "import sys\n"
            "arguments = sys.argv[1:]\n"
            "print(json.dumps(arguments))\n"
            "if not arguments:\n"
            "    raise SystemExit(11)\n"
            "if arguments[0] == 'unknown-command':\n"
            "    raise SystemExit(2)\n"
            "if arguments[0] == 'child-failure':\n"
            "    raise SystemExit(23)\n"
            "raise SystemExit(0)\n",
            encoding="utf-8",
        )

    def test_argument_and_exit_code_matrix(self):
        cases = (
            ((), 11),
            (("status",), 0),
            (("start", "TASK-001"), 0),
            (("review", "abc123"), 0),
            (("close", "def456"), 0),
            (("unknown-command",), 2),
            (("child-failure",), 23),
            (("task-new", "TASK WITH SPACES"), 0),
        )

        for arguments, expected_exit in cases:
            with self.subTest(arguments=arguments):
                completed = self._run_launcher(*arguments)
                self.assertEqual(completed.returncode, expected_exit)
                self.assertEqual(json.loads(completed.stdout), list(arguments))
                self.assertEqual(completed.stderr, "")

    def test_launcher_resolves_python_child_from_its_space_containing_path(self):
        self.assertIn(" ", str(self.repo_root))

        completed = self._run_launcher("status")

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout), ["status"])

    def _run_launcher(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [CMD_EXE, "/d", "/c", "qh.cmd", *arguments],
            cwd=self.repo_root,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
