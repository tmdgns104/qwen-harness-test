import unittest
from dataclasses import FrozenInstanceError

from tools.harness_core import (
    BoundedWorkerRequest, BoundedWorkerResponse, Candidate, CandidateOperation,
    CandidateOperationType, BoundedOutcome,
)


class BoundedStatelessContractTests(unittest.TestCase):
    def test_request_response_and_candidate_are_structured(self):
        candidate = Candidate(operations=(
            CandidateOperation(CandidateOperationType.CREATE_FILE, "tests/a.py", "pass\n"),
            CandidateOperation(CandidateOperationType.REPLACE_FILE, "src/a.py", "new\n"),
        ))
        request = BoundedWorkerRequest("T-1", {"files": []}, {"type": "candidate"})
        response = BoundedWorkerResponse(True, candidate, None, {"attempt": 1})
        self.assertEqual(request.task, "T-1")
        self.assertEqual(len(response.candidate.operations), 2)
        self.assertEqual(response.metadata["attempt"], 1)

    def test_immutable_and_passive(self):
        op = CandidateOperation(CandidateOperationType.CREATE_FILE, "a.py", "x")
        self.assertEqual(Candidate.__dataclass_fields__.keys(), {"operations"})
        with self.assertRaises(FrozenInstanceError):
            op.path = "b.py"
        self.assertFalse(any(name in dir(op) for name in ("apply", "execute", "write", "save")))

    def test_operation_and_outcome_values_are_closed(self):
        self.assertEqual(set(CandidateOperationType), {CandidateOperationType.CREATE_FILE, CandidateOperationType.REPLACE_FILE, CandidateOperationType.REPLACE_TEXT})
        self.assertEqual({x.value for x in BoundedOutcome}, {"COMPLETED", "NO_ACTION", "CANDIDATE_INVALID", "VERIFICATION_FAILED", "SAFETY_FAIL", "TRANSPORT_FAIL", "PERFORMANCE_FAIL", "BLOCKED"})

    def test_native_contract_remains_distinct(self):
        from tools.harness_core import WorkerRequest, WorkerResponse
        self.assertEqual(WorkerRequest("task").task_text, "task")
        self.assertEqual(WorkerResponse(True, "ok").output_text, "ok")


if __name__ == "__main__":
    unittest.main()
