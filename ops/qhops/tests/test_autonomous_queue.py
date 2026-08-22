from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


QH_OPS_PATH = Path(__file__).resolve().parents[1] / "qh_ops.py"
spec = importlib.util.spec_from_file_location("qh_ops_gate001", QH_OPS_PATH)
assert spec and spec.loader
qh_ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qh_ops)


COVERED_QUEUE = (
    "QH-V2-HARD-006",
    "QH-V2-HARD-007",
    "QH-V2-OPS-001",
    "QH-V2-OPS-002",
    "QH-V2-OPS-003",
    "QH-V2-OPS-004",
    "QH-V2-OPS-005",
    "QH-V2-OPS-006",
    "QH-V2-M2-SPEC-001",
)

IMMUTABLE_SECTIONS = (
    "Goal",
    "Architecture Basis",
    "Dependencies",
    "Scope",
    "Allowed Changes",
    "Forbidden Changes",
    "Acceptance Criteria",
    "Verification",
    "Evidence Requirements",
    "Stop Conditions",
    "Next Task",
)


def task_text(status: str = "APPROVED - READY FOR CONTRACT BASELINE") -> str:
    parts = ["# Example", "", "## Status", "", status, ""]
    for heading in IMMUTABLE_SECTIONS:
        parts.extend((f"## {heading}", "", f"content for {heading}", ""))
    return "\n".join(parts)


class Gate001ContractTests(unittest.TestCase):
    def test_covered_queue_is_exact_and_finite(self) -> None:
        self.assertEqual(qh_ops.COVERED_QUEUE, COVERED_QUEUE)

    def test_immutable_sections_are_exact(self) -> None:
        self.assertEqual(qh_ops.IMMUTABLE_CONTRACT_SECTIONS, IMMUTABLE_SECTIONS)

    def test_status_only_transition_preserves_immutable_hash(self) -> None:
        approved = task_text()
        complete = task_text("COMPLETE - VERIFIED")
        self.assertEqual(
            qh_ops.immutable_contract_hash(approved),
            qh_ops.immutable_contract_hash(complete),
        )

    def test_immutable_change_changes_hash(self) -> None:
        original = task_text()
        changed = original.replace("content for Scope", "changed scope")
        self.assertNotEqual(
            qh_ops.immutable_contract_hash(original),
            qh_ops.immutable_contract_hash(changed),
        )

    def test_missing_required_section_fails_closed(self) -> None:
        broken = task_text().replace("## Goal\n\ncontent for Goal\n\n", "")
        with self.assertRaises(qh_ops.Stop):
            qh_ops.immutable_contract_hash(broken)

    def test_duplicate_required_section_fails_closed(self) -> None:
        broken = task_text() + "\n## Goal\n\nduplicate\n"
        with self.assertRaises(qh_ops.Stop):
            qh_ops.immutable_contract_hash(broken)

    def test_gate_commands_exist(self) -> None:
        for name in (
            "cmd_gate_seal",
            "cmd_gate_check",
            "cmd_supervisor_start",
            "cmd_supervisor_commit_impl",
            "cmd_supervisor_finish",
        ):
            self.assertTrue(callable(getattr(qh_ops, name, None)), name)

    def test_manifest_path_is_repo_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                qh_ops.manifest_path(root),
                root / "ops" / "qhops" / "autonomous_queue_manifest.json",
            )

    def test_usage_exposes_gate_and_supervisor_commands(self) -> None:
        import contextlib
        import io

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            qh_ops.usage()
        text = output.getvalue()
        for command in (
            "gate-seal",
            "gate-check",
            "supervisor-start",
            "supervisor-commit-impl",
            "supervisor-finish",
        ):
            self.assertIn(command, text)


if __name__ == "__main__":
    unittest.main()
