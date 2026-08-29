import unittest
from tools.harness_core import (
    BoundedOutcome, Candidate, CandidateApplyResult, CandidateOperation,
    CandidateOperationType, CandidateValidationResult, VerificationCommandResult,
    verify_bounded_candidate,
)


class BoundedVerificationTests(unittest.TestCase):
    def setUp(self):
        self.c = Candidate((CandidateOperation(CandidateOperationType.CREATE_FILE, "src/a.py", "x"),))
        self.valid = CandidateValidationResult(True, ())
        self.applied = CandidateApplyResult(True, "C:/snapshot", ("src/a.py",), None)
        self.tests = (VerificationCommandResult("python -m unittest", 0, "ok", ""),)

    def test_completed_requires_all_evidence(self):
        r = verify_bounded_candidate(self.c, self.valid, self.applied, self.tests, ("src/a.py",), ("src/a.py",), True)
        self.assertEqual(r.outcome, BoundedOutcome.COMPLETED); self.assertTrue(r.verification_passed)

    def test_failures_map_without_false_success(self):
        bad = CandidateValidationResult(False, ("path outside allowed scope",))
        self.assertEqual(verify_bounded_candidate(self.c,bad,self.applied,self.tests,(),(),True).outcome, BoundedOutcome.CANDIDATE_INVALID)
        failed = (VerificationCommandResult("test", 1, "", "failure"),)
        self.assertEqual(verify_bounded_candidate(self.c,self.valid,self.applied,failed,("src/a.py",),("src/a.py",),True).outcome, BoundedOutcome.VERIFICATION_FAILED)
        self.assertEqual(verify_bounded_candidate(self.c,self.valid,self.applied,self.tests,("src/a.py",),("src/a.py","x.py"),True).outcome, BoundedOutcome.VERIFICATION_FAILED)

    def test_apply_safety_and_no_action(self):
        failed_apply=CandidateApplyResult(False,None,(),"conflict")
        self.assertEqual(verify_bounded_candidate(self.c,self.valid,failed_apply,self.tests,(),(),True).outcome, BoundedOutcome.SAFETY_FAIL)
        empty=Candidate(())
        self.assertEqual(verify_bounded_candidate(empty,self.valid,self.applied,self.tests,(),(),True).outcome, BoundedOutcome.VERIFICATION_FAILED)
        self.assertEqual(verify_bounded_candidate(empty,self.valid,self.applied,self.tests,(),(),True,allow_no_action=True).outcome, BoundedOutcome.NO_ACTION)


if __name__ == '__main__': unittest.main()
