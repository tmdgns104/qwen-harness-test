import json
import unittest
from unittest.mock import patch

from tools.harness_core import WorkerRequest


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


class OllamaWorkerTests(unittest.TestCase):
    def test_success_sends_native_chat_payload_and_returns_worker_response(self):
        from tools.ollama_worker import call_ollama_worker

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            captured["timeout"] = timeout
            return FakeResponse({"message": {"content": "worker-output"}})

        with patch("tools.ollama_worker.urlopen", side_effect=fake_urlopen):
            result = call_ollama_worker(
                WorkerRequest(task_text="do small task"),
                base_url="http://127.0.0.1:11434",
                model="qwen3:8b",
                timeout_seconds=30.0,
            )

        self.assertEqual(captured["url"], "http://127.0.0.1:11434/api/chat")
        self.assertEqual(captured["payload"]["model"], "qwen3:8b")
        self.assertEqual(captured["payload"]["messages"], [{"role": "user", "content": "do small task"}])
        self.assertIs(captured["payload"]["stream"], False)
        self.assertIs(captured["payload"]["think"], False)
        self.assertNotIn("tools", captured["payload"])
        self.assertEqual(captured["timeout"], 30.0)
        self.assertTrue(result.transport_ok)
        self.assertEqual(result.output_text, "worker-output")
        self.assertIsNone(result.error)


if __name__ == "__main__":
    unittest.main()
