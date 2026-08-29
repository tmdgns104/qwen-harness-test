import tempfile
import unittest
from pathlib import Path

from tools.harness_core import (
    Candidate, CandidateOperation, CandidateOperationType, ChangeScope,
    validate_candidate, apply_candidate_to_snapshot,
)


class CandidateApplyTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(); self.repo = Path(self.td.name) / "repo"; self.repo.mkdir()
        (self.repo / "src").mkdir(); (self.repo / "src/existing.py").write_text("old\n")
        self.scope = ChangeScope(("src/**",), ("STATUS.md",))
    def tearDown(self): self.td.cleanup()
    def c(self,*ops): return Candidate(tuple(ops))
    def op(self,t,p,c): return CandidateOperation(t,p,c)
    def valid(self,c): return validate_candidate(c,self.scope)
    def test_create_replace_and_original_unchanged(self):
        original=(self.repo/'src/existing.py').read_bytes()
        c=self.c(self.op(CandidateOperationType.CREATE_FILE,'src/new.py','new'),self.op(CandidateOperationType.REPLACE_FILE,'src/existing.py','changed'))
        r=apply_candidate_to_snapshot(self.repo,c,self.valid(c)); self.assertTrue(r.success); self.assertEqual(len(r.applied_operations),2)
        self.assertEqual((Path(r.snapshot_path)/'src/new.py').read_text(),'new'); self.assertEqual((Path(r.snapshot_path)/'src/existing.py').read_text(),'changed'); self.assertEqual((self.repo/'src/existing.py').read_bytes(),original)
    def test_conflicts_and_invalid_validation_fail_closed(self):
        c=self.c(self.op(CandidateOperationType.CREATE_FILE,'src/existing.py','x')); r=apply_candidate_to_snapshot(self.repo,c,self.valid(c)); self.assertFalse(r.success); self.assertIsNone(r.snapshot_path)
        bad=self.c(self.op(CandidateOperationType.CREATE_FILE,'../escape','x')); r=apply_candidate_to_snapshot(self.repo,bad,self.valid(bad)); self.assertFalse(r.success)
    def test_missing_replace_and_atomic_failure(self):
        c=self.c(self.op(CandidateOperationType.CREATE_FILE,'src/new.py','ok'),self.op(CandidateOperationType.REPLACE_FILE,'src/missing.py','boom'))
        r=apply_candidate_to_snapshot(self.repo,c,self.valid(c)); self.assertFalse(r.success); self.assertIsNone(r.snapshot_path); self.assertFalse((self.repo/'src/new.py').exists())
    def test_source_symlink_rejected(self):
        link=self.repo/'src/link.py'
        try: link.symlink_to(self.repo/'src/existing.py')
        except (OSError, NotImplementedError): self.skipTest('symlink unavailable')
        c=self.c(self.op(CandidateOperationType.CREATE_FILE,'src/new.py','x')); r=apply_candidate_to_snapshot(self.repo,c,self.valid(c)); self.assertFalse(r.success)


if __name__ == '__main__': unittest.main()
