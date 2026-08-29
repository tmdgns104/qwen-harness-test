import unittest
from tools.harness_core import (
    Candidate, CandidateOperation, CandidateOperationType, ChangeScope,
    validate_candidate,
)


class CandidateValidatorTests(unittest.TestCase):
    scope = ChangeScope(("src/a.py", "tests/a.py"), ("STATUS.md", "tests/hidden.py"))
    def candidate(self, *ops): return Candidate(tuple(ops))
    def op(self, typ=CandidateOperationType.CREATE_FILE, path="src/a.py", content="x"): return CandidateOperation(typ, path, content)

    def test_valid_operations_and_test_scope(self):
        result = validate_candidate(self.candidate(self.op(), self.op(path="tests/a.py")), self.scope)
        self.assertTrue(result.valid); self.assertEqual(result.errors, ())

    def test_rejects_forbidden_protected_and_traversal_paths(self):
        for path in ("tests/hidden.py", "STATUS.md", "../src/a.py", "C:/x.py", ""):
            self.assertFalse(validate_candidate(self.candidate(self.op(path=path)), self.scope).valid)

    def test_rejects_duplicates_and_limits(self):
        self.assertFalse(validate_candidate(self.candidate(self.op(), self.op()), self.scope).valid)
        self.assertFalse(validate_candidate(self.candidate(self.op(content="1234")), self.scope, max_content_chars=3).valid)
        self.assertFalse(validate_candidate(self.candidate(self.op(), self.op(path="tests/a.py"), self.op(path="src/a.py", content="z")), self.scope, max_operations=2).valid)

    def test_rejects_malformed_or_unsupported_operations(self):
        self.assertFalse(validate_candidate(None, self.scope).valid)
        self.assertFalse(validate_candidate(self.candidate(self.op(typ="CREATE_FILE")), self.scope).valid)


if __name__ == "__main__": unittest.main()
