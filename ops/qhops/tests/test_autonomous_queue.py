from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


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

FAKE_SHA = "a" * 40
OTHER_SHA = "b" * 40


def completed(*, returncode: int = 0, stdout: str = "", stderr: str = ""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def task_text(status: str = "APPROVED - READY FOR CONTRACT BASELINE") -> str:
    parts = ["# Example", "", "## Status", "", status, ""]
    for heading in IMMUTABLE_SECTIONS:
        parts.extend((f"## {heading}", "", f"content for {heading}", ""))
    return "\n".join(parts)


def base_manifest() -> dict:
    tasks = {
        task_id: {
            "path": f"tasks/{task_id}.md",
            "prestart_blob": FAKE_SHA,
            "immutable_sha256": "c" * 64,
        }
        for task_id in COVERED_QUEUE
    }
    payload = {
        "version": qh_ops.GATE_MANIFEST_VERSION,
        "policy": qh_ops.GATE_POLICY,
        "gate_change_set_commit": FAKE_SHA,
        "authority_source_blobs": {
            path: FAKE_SHA for path in qh_ops.AUTHORITY_SOURCE_PATHS
        },
        "human_gate_evidence": {
            "path": qh_ops.GATE_EVIDENCE_PATH,
            "blob": FAKE_SHA,
        },
        "covered_queue": list(COVERED_QUEUE),
        "tasks": tasks,
        "git": {
            "local_branch": qh_ops.LOCAL_BRANCH,
            "remote": qh_ops.REMOTE,
            "remote_identity": "github.com/tmdgns104/qwen-harness-test.git",
            "remote_branch": qh_ops.REMOTE_BRANCH,
            "push_refspec": "HEAD:main",
            "fast_forward_only": True,
        },
        "delegated_operations": list(qh_ops.DELEGATED_OPERATIONS),
        "forbidden_operations": list(qh_ops.FORBIDDEN_OPERATIONS),
        "validity": {
            "revoked": False,
            "valid_until": "first of revocation, manifest mismatch, policy invalidation, or covered queue completion at HUMAN ARCHITECTURE GATE",
            "terminal_gate": "HUMAN ARCHITECTURE GATE",
        },
        "audit": {
            "authoritative_resume": "Repository Git state plus exact manifest",
            "supplemental_local_audit": "%USERPROFILE%\\.qhops\\audit\\",
            "chat_or_session_memory_authority": False,
        },
    }
    return qh_ops._with_manifest_integrity(payload)


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

    def test_status_parser_ignores_literal_status_text_in_body(self) -> None:
        text = task_text().replace(
            "content for Goal",
            'prose may mention "## Status" without creating another heading',
        )
        self.assertEqual(
            qh_ops.task_status_from_text(text),
            qh_ops.APPROVED_STATUS,
        )

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

    def test_manifest_integrity_tamper_fails_closed(self) -> None:
        manifest = base_manifest()
        manifest["policy"] = "tampered"
        with self.assertRaises(qh_ops.Stop):
            qh_ops._validate_manifest_schema(manifest)

    def test_manifest_wrong_queue_fails_even_with_recomputed_integrity(self) -> None:
        manifest = base_manifest()
        manifest.pop("manifest_sha256")
        manifest["covered_queue"] = list(reversed(COVERED_QUEUE))
        manifest = qh_ops._with_manifest_integrity(manifest)
        with self.assertRaises(qh_ops.Stop):
            qh_ops._validate_manifest_schema(manifest)

    def test_manifest_revocation_fails_even_with_recomputed_integrity(self) -> None:
        manifest = base_manifest()
        manifest.pop("manifest_sha256")
        manifest["validity"]["revoked"] = True
        manifest = qh_ops._with_manifest_integrity(manifest)
        with self.assertRaises(qh_ops.Stop):
            qh_ops._validate_manifest_schema(manifest)

    def test_wrong_branch_fails_before_mutation(self) -> None:
        root = Path("repo")
        manifest = base_manifest()
        with (
            mock.patch.object(qh_ops, "require_clean"),
            mock.patch.object(qh_ops, "load_manifest", return_value=manifest),
            mock.patch.object(qh_ops, "_current_branch", return_value="feature"),
            mock.patch.object(qh_ops, "git") as git_call,
        ):
            with self.assertRaises(qh_ops.Stop):
                qh_ops.validate_gate_state(root)
        git_call.assert_not_called()

    def test_wrong_remote_identity_fails_before_queue_checks(self) -> None:
        root = Path("repo")
        manifest = base_manifest()
        with (
            mock.patch.object(qh_ops, "require_clean"),
            mock.patch.object(qh_ops, "load_manifest", return_value=manifest),
            mock.patch.object(qh_ops, "_current_branch", return_value=qh_ops.LOCAL_BRANCH),
            mock.patch.object(
                qh_ops,
                "_remote_url",
                return_value="https://github.com/other/repository.git",
            ),
            mock.patch.object(qh_ops, "_require_exact_backlog_queue") as queue_check,
        ):
            with self.assertRaises(qh_ops.Stop):
                qh_ops.validate_gate_state(root)
        queue_check.assert_not_called()

    def test_dirty_state_fails_before_manifest_read(self) -> None:
        root = Path("repo")
        with (
            mock.patch.object(
                qh_ops,
                "require_clean",
                side_effect=qh_ops.Stop("working tree is not clean"),
            ),
            mock.patch.object(qh_ops, "load_manifest") as load,
        ):
            with self.assertRaises(qh_ops.Stop):
                qh_ops.validate_gate_state(root)
        load.assert_not_called()

    def test_unapproved_pending_task_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = base_manifest()
            for task_id in COVERED_QUEUE:
                path = root / "tasks" / f"{task_id}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(task_text(), encoding="utf-8")
                manifest["tasks"][task_id]["immutable_sha256"] = qh_ops.immutable_contract_hash(
                    path.read_text(encoding="utf-8")
                )
            first = root / "tasks" / f"{COVERED_QUEUE[0]}.md"
            first.write_text(task_text("PLANNED"), encoding="utf-8")
            with self.assertRaises(qh_ops.Stop):
                qh_ops._queue_progress(root, manifest, allow_completed_gate=False)

    def test_completed_queue_expires_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = base_manifest()
            approved = task_text()
            for task_id in COVERED_QUEUE:
                path = root / "tasks" / f"{task_id}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(task_text("COMPLETE - VERIFIED"), encoding="utf-8")
                manifest["tasks"][task_id]["immutable_sha256"] = qh_ops.immutable_contract_hash(
                    path.read_text(encoding="utf-8")
                )
            with (
                mock.patch.object(qh_ops, "_git_blob_text", return_value=approved),
                self.assertRaises(qh_ops.Stop),
            ):
                qh_ops._queue_progress(root, manifest, allow_completed_gate=False)

    def test_completed_task_non_status_change_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = base_manifest()
            approved = task_text()
            for task_id in COVERED_QUEUE:
                path = root / "tasks" / f"{task_id}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(task_text(), encoding="utf-8")
                manifest["tasks"][task_id]["immutable_sha256"] = qh_ops.immutable_contract_hash(
                    approved
                )
            first = root / "tasks" / f"{COVERED_QUEUE[0]}.md"
            tampered = task_text("COMPLETE - VERIFIED").replace(
                "# Example",
                "# Example\n\nnon-status mutation",
            )
            first.write_text(tampered, encoding="utf-8")
            with (
                mock.patch.object(qh_ops, "_git_blob_text", return_value=approved),
                self.assertRaises(qh_ops.Stop),
            ):
                qh_ops._queue_progress(root, manifest, allow_completed_gate=True)

    def test_supervisor_start_never_promotes_planned_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "tasks" / f"{COVERED_QUEUE[0]}.md"
            task.parent.mkdir(parents=True)
            task.write_text(task_text("PLANNED"), encoding="utf-8")
            state = {"next_task": COVERED_QUEUE[0]}
            with (
                mock.patch.object(qh_ops, "validate_gate_state", return_value=state),
                mock.patch.object(qh_ops, "current_task_id", return_value=qh_ops.GATE_TASK_ID),
                mock.patch.object(
                    qh_ops,
                    "current_task_line",
                    return_value=f"Current Task: {qh_ops.GATE_TASK_ID} - COMPLETE - VERIFIED - commit abc",
                ),
                mock.patch.object(qh_ops, "qh") as qh_call,
                mock.patch.object(qh_ops, "approve_task_file") as approve,
            ):
                with self.assertRaises(qh_ops.Stop):
                    qh_ops.cmd_supervisor_start(root)
            qh_call.assert_not_called()
            approve.assert_not_called()

    def test_supervisor_commit_revalidates_before_and_after(self) -> None:
        root = Path("repo")
        current = COVERED_QUEUE[0]
        state = {"next_task": current}
        with (
            mock.patch.object(
                qh_ops,
                "validate_gate_state",
                side_effect=[state, state],
            ) as validate,
            mock.patch.object(qh_ops, "current_task_id", return_value=current),
            mock.patch.object(
                qh_ops,
                "current_task_line",
                return_value=f"Current Task: {current} - ACTIVE",
            ),
            mock.patch.object(qh_ops, "_commit_impl") as commit_impl,
        ):
            qh_ops.cmd_supervisor_commit_impl(root)
        self.assertEqual(validate.call_count, 2)
        commit_impl.assert_called_once_with(root)

    def test_supervisor_finish_closes_once_then_pushes_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = COVERED_QUEUE[0]
            task_path = root / "tasks" / f"{current}.md"
            task_path.parent.mkdir(parents=True)
            task_path.write_text(task_text(), encoding="utf-8")
            expected_paths = tuple(sorted(("STATUS.md", f"tasks/{current}.md")))

            def git_result(_root, *args, **_kwargs):
                if args[:2] == ("rev-parse", "HEAD"):
                    return completed(stdout="abc123\n")
                return completed()

            with (
                mock.patch.object(
                    qh_ops,
                    "validate_gate_state",
                    side_effect=[
                        {"next_task": current},
                        {"next_task": COVERED_QUEUE[1]},
                    ],
                ),
                mock.patch.object(qh_ops, "current_task_id", return_value=current),
                mock.patch.object(
                    qh_ops,
                    "current_task_line",
                    return_value=f"Current Task: {current} - ACTIVE",
                ),
                mock.patch.object(qh_ops, "current_task_path", return_value=task_path),
                mock.patch.object(qh_ops, "require_clean"),
                mock.patch.object(qh_ops, "git", side_effect=git_result),
                mock.patch.object(qh_ops, "qh") as qh_call,
                mock.patch.object(qh_ops, "changed_paths", return_value=expected_paths),
                mock.patch.object(qh_ops, "safe_push") as push,
            ):
                qh_ops.cmd_supervisor_finish(root)

            qh_call.assert_called_once_with(root, "close", "abc123")
            push.assert_called_once_with(root)

    def test_supervisor_finish_validation_failure_has_zero_mutation(self) -> None:
        root = Path("repo")
        with (
            mock.patch.object(
                qh_ops,
                "validate_gate_state",
                side_effect=qh_ops.Stop("manifest mismatch"),
            ),
            mock.patch.object(qh_ops, "qh") as qh_call,
            mock.patch.object(qh_ops, "git") as git_call,
            mock.patch.object(qh_ops, "safe_push") as push,
        ):
            with self.assertRaises(qh_ops.Stop):
                qh_ops.cmd_supervisor_finish(root)
        qh_call.assert_not_called()
        git_call.assert_not_called()
        push.assert_not_called()

    def test_usage_exposes_gate_and_supervisor_commands(self) -> None:
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
