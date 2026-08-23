from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import qh as qh_module


class FakeJsonResponse:
    def __init__(self, payload: object) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


def _fake_success_opener(request, timeout):
    return FakeJsonResponse({"models": [{"name": "qwen3:8b"}]})


def _prepare_doctor_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "tasks").mkdir()
    for name in ("PROJECT.md", "REQUIREMENTS.md", "DECISIONS.md"):
        (repo / name).write_text(f"# {name}\n", encoding="utf-8", newline="\n")
    (repo / "STATUS.md").write_text(
        "Current Task: QH-V2-PORTABILITY-FIXTURE - ACTIVE\n\n"
        "Previous Task: QH-V2-DEMO-000 - COMPLETE - VERIFIED - commit deadbeef\n\n"
        "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n"
        "Task Baseline: deadbeef\n",
        encoding="utf-8",
        newline="\n",
    )
    (repo / "tasks" / "QH-V2-PORTABILITY-FIXTURE.md").write_text(
        """# QH-V2-PORTABILITY-FIXTURE - Doctor Fixture

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Exercise delayed run import readiness.

## Allowed Changes

- `STATUS.md`
- `tasks/QH-V2-PORTABILITY-FIXTURE.md`

## Forbidden Changes

- `tools/**`

## Verification

Run exactly:

`python -c "print('ok')"`
""",
        encoding="utf-8",
        newline="\n",
    )


class RuntimePortabilityTests(unittest.TestCase):
    def test_documented_run_entry_reaches_runner_without_pythonpath(self) -> None:
        task_id = "QH-V2-PORTABILITY-FIXTURE"

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            shutil.copytree(
                ROOT / "tools",
                repo / "tools",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            (repo / "tasks").mkdir()

            (repo / "STATUS.md").write_text(
                f"Current Task: {task_id} - ACTIVE\n",
                encoding="utf-8",
                newline="\n",
            )
            (repo / "tasks" / f"{task_id}.md").write_text(
                f"""# {task_id} - Runtime Portability Fixture

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Reach the delayed Runner import chain and fail safely before Worker startup.
""",
                encoding="utf-8",
                newline="\n",
            )

            env = os.environ.copy()
            env.pop("PYTHONPATH", None)

            result = subprocess.run(
                [sys.executable, "tools/qh.py", "run", task_id],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            combined = result.stdout + result.stderr

            self.assertEqual(result.returncode, 1, combined)
            self.assertNotIn("ModuleNotFoundError", combined)
            self.assertNotIn("Traceback", combined)
            self.assertIn(f"Task: {task_id}", result.stdout)
            self.assertIn("Outcome: FAIL", result.stdout)
            self.assertIn("Failure Kind: SAFETY", result.stdout)
            self.assertIn("Write Side Effect Risk: NO", result.stdout)

    def test_doctor_fails_required_check_when_run_import_chain_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _prepare_doctor_repo(repo)
            output = io.StringIO()

            with (
                patch.object(
                    qh_module,
                    "_load_run_dependencies",
                    side_effect=ModuleNotFoundError("No module named 'tools.retry_runner'"),
                ),
                redirect_stdout(output),
            ):
                result = qh_module.command_doctor(
                    repo,
                    ollama_opener=_fake_success_opener,
                )

            rendered = output.getvalue()
            self.assertNotEqual(result, 0, rendered)
            self.assertRegex(rendered, r"RUN_IMPORT_CHAIN:\s+FAIL\b")
            self.assertRegex(rendered, r"OVERALL:\s+FAIL\b")


if __name__ == "__main__":
    unittest.main()
