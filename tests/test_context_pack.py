import unittest
from dataclasses import FrozenInstanceError

from tools.harness_core import (
    ContextItem, ContextItemKind, ContextPackBuildError, build_context_pack,
)


class ContextPackTests(unittest.TestCase):
    def inputs(self):
        return dict(task_id="T-1", goal="goal", acceptance_criteria=("pass",), allowed_changes=("a.py",), forbidden_changes=("b.py",), items=(
            ContextItem(ContextItemKind.TEST_FILE, "tests/t.py", "test"),
            ContextItem(ContextItemKind.SOURCE_FILE, "a.py", "source"),
            ContextItem(ContextItemKind.ARCHITECTURE, "ARCH", "design"),
        ), output_contract={"type": "candidate"})

    def test_build_preserves_fields_and_provenance(self):
        pack = build_context_pack(**self.inputs(), budget_chars=100)
        self.assertEqual(pack.task_id, "T-1")
        self.assertEqual([x.source for x in pack.items], ["ARCH", "a.py", "tests/t.py"])
        self.assertEqual(pack.used_chars, 16)

    def test_order_is_independent_of_input_order(self):
        a = self.inputs(); b = self.inputs(); b["items"] = tuple(reversed(b["items"]))
        self.assertEqual(build_context_pack(**a, budget_chars=100), build_context_pack(**b, budget_chars=100))

    def test_budget_overflow_and_missing_required_fail_closed(self):
        with self.assertRaises(ContextPackBuildError): build_context_pack(**self.inputs(), budget_chars=3)
        bad = self.inputs(); bad["goal"] = ""
        with self.assertRaises(ContextPackBuildError): build_context_pack(**bad, budget_chars=100)

    def test_frozen_and_no_repository_operations(self):
        pack = build_context_pack(**self.inputs(), budget_chars=100)
        with self.assertRaises(FrozenInstanceError): pack.task_id = "x"
        self.assertFalse(any(x in dir(pack) for x in ("apply", "execute", "write", "save")))


if __name__ == "__main__": unittest.main()
