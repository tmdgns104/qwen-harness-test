from __future__ import annotations

import unittest
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
_TESTS_DIR = _REPO_ROOT / "tests"
_REQUIRED_MODULE_MARKERS = (
    "test_qh.",
    "test_harness_core.",
    "test_repo_tools.",
    "test_task_runner.",
    "test_markdown_append.",
)


def _test_ids(suite: unittest.TestSuite) -> tuple[str, ...]:
    ids: list[str] = []

    def visit(node: unittest.TestSuite | unittest.TestCase) -> None:
        if isinstance(node, unittest.TestSuite):
            for item in node:
                visit(item)
            return
        ids.append(node.id())

    visit(suite)
    return tuple(ids)


class TestDiscoveryIntegrityTests(unittest.TestCase):
    def test_repository_root_discovery_finds_real_suite(self) -> None:
        default_suite = unittest.TestLoader().discover(
            str(_REPO_ROOT),
            pattern="test*.py",
        )
        explicit_suite = unittest.TestLoader().discover(
            str(_TESTS_DIR),
            pattern="test*.py",
        )

        default_ids = _test_ids(default_suite)
        explicit_ids = _test_ids(explicit_suite)
        default_count = len(default_ids)
        explicit_count = len(explicit_ids)

        self.assertGreater(
            explicit_count,
            0,
            "explicit tests discovery unexpectedly found zero tests",
        )
        self.assertGreater(
            default_count,
            0,
            f"Repository-root discovery found {default_count} tests; "
            f"explicit tests discovery found {explicit_count}",
        )
        self.assertEqual(
            default_count,
            explicit_count,
            f"Repository-root discovery found {default_count} tests; "
            f"explicit tests discovery found {explicit_count}",
        )

        for marker in _REQUIRED_MODULE_MARKERS:
            with self.subTest(module=marker.rstrip(".")):
                self.assertTrue(
                    any(marker in test_id for test_id in default_ids),
                    f"Repository-root discovery is missing {marker.rstrip('.')}",
                )
