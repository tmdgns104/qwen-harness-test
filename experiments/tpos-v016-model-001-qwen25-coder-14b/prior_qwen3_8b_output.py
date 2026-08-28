import unittest
from app.structured_state_v016 import rebase_conflicts


class TestRebaseConflicts(unittest.TestCase):
    def test_positive_conflict(self):
        base = {
            "requirements": [
                {
                    "ref": "REQ-HUMAN-001",
                    "title": "Baseline requirement",
                    "detail": "Original detail",
                }
            ]
        }
        current = {
            "requirements": [
                {
                    "ref": "REQ-HUMAN-001",
                    "title": "Human-edited requirement",
                    "detail": "Official human edit",
                }
            ]
        }
        delta = {
            "requirements": [
                {
                    "ref": "REQ-HUMAN-001",
                    "title": "Incoming AI proposal",
                    "detail": "Proposed overwrite",
                }
            ]
        }
        result = rebase_conflicts(base, current, delta)
        self.assertEqual(result, ["requirements.REQ-HUMAN-001"])

    def test_negative_conflict(self):
        base = {
            "requirements": [
                {
                    "ref": "REQ-HUMAN-001",
                    "title": "Baseline requirement",
                    "detail": "Original detail",
                },
                {
                    "ref": "REQ-HUMAN-002",
                    "title": "Baseline requirement 2",
                    "detail": "Original detail 2",
                }
            ]
        }
        current = {
            "requirements": [
                {
                    "ref": "REQ-HUMAN-001",
                    "title": "Human-edited requirement",
                    "detail": "Official human edit",
                },
                {
                    "ref": "REQ-HUMAN-002",
                    "title": "Human-edited requirement 2",
                    "detail": "Official human edit 2",
                }
            ]
        }
        delta = {
            "requirements": [
                {
                    "ref": "REQ-HUMAN-001",
                    "title": "Incoming AI proposal",
                    "detail": "Proposed overwrite",
                }
            ]
        }
        result = rebase_conflicts(base, current, delta)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
