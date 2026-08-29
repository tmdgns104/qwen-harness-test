import json
import unittest
from unittest.mock import patch

from tools.harness_core import BoundedWorkerRequest, CandidateOperationType
from tools.ollama_worker import call_bounded_stateless_worker, _bounded_prompt


class FakeResponse:
    def __init__(self, payload): self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.payload


class BoundedOllamaWorkerTests(unittest.TestCase):
    request = BoundedWorkerRequest("T", {"task_id": "T", "items": []}, {"type": "candidate"})
    def test_prompt_is_stable_and_payload_has_no_tools(self):
        self.assertEqual(_bounded_prompt(self.request), _bounded_prompt(self.request))
        with patch("tools.ollama_worker.urlopen", return_value=FakeResponse({"message": {"content": '{"operations":[]}'}})) as open_mock:
            result = call_bounded_stateless_worker(self.request)
        payload = json.loads(open_mock.call_args.args[0].data.decode())
        self.assertNotIn("tools", payload); self.assertTrue(result.transport_ok); self.assertEqual(result.candidate.operations, ())

    def test_parses_create_replace_and_preserves_transport(self):
        content = '{"operations":[{"operation_type":"CREATE_FILE","path":"a.py","content":"x"},{"operation_type":"REPLACE_FILE","path":"b.py","content":"y"}]}'
        with patch("tools.ollama_worker.urlopen", return_value=FakeResponse({"message": {"content": content}})):
            result = call_bounded_stateless_worker(self.request)
        self.assertTrue(result.metadata["parse_ok"]); self.assertEqual([x.operation_type for x in result.candidate.operations], [CandidateOperationType.CREATE_FILE, CandidateOperationType.REPLACE_FILE])

    def test_malformed_and_unsupported_fail_closed(self):
        for content in ("not json", '{"operations":[{"operation_type":"DELETE","path":"a","content":"x"}]}', '{"operations":[{"operation_type":"CREATE_FILE","path":"a"}]}'):
            with patch("tools.ollama_worker.urlopen", return_value=FakeResponse({"message": {"content": content}})):
                result = call_bounded_stateless_worker(self.request)
            self.assertTrue(result.transport_ok); self.assertIsNone(result.candidate); self.assertFalse(result.metadata["parse_ok"])

    def test_transport_failure_is_distinct(self):
        with patch("tools.ollama_worker.urlopen", side_effect=TimeoutError("timeout")):
            result = call_bounded_stateless_worker(self.request)
        self.assertFalse(result.transport_ok); self.assertIsNone(result.candidate)


if __name__ == "__main__": unittest.main()
