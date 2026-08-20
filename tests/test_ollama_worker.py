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


class RawResponse:
    def __init__(self, payload):
        self.payload = payload

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


    def test_network_failure_returns_transport_failure(self):
        from urllib.error import URLError
        from tools.ollama_worker import call_ollama_worker

        with patch("tools.ollama_worker.urlopen", side_effect=URLError("connection refused")):
            result = call_ollama_worker(WorkerRequest(task_text="do small task"))

        self.assertFalse(result.transport_ok)
        self.assertEqual(result.output_text, "")
        self.assertIsNotNone(result.error)
        self.assertIn("connection refused", result.error)


    def test_http_failure_returns_transport_failure(self):
        from urllib.error import HTTPError
        from tools.ollama_worker import call_ollama_worker

        error = HTTPError("http://127.0.0.1:11434/api/chat", 500, "Internal Server Error", {}, None)
        with patch("tools.ollama_worker.urlopen", side_effect=error):
            result = call_ollama_worker(WorkerRequest(task_text="do small task"))

        self.assertFalse(result.transport_ok)
        self.assertEqual(result.output_text, "")
        self.assertIsNotNone(result.error)
        self.assertIn("500", result.error)

    def test_invalid_json_returns_transport_failure(self):
        from tools.ollama_worker import call_ollama_worker

        with patch("tools.ollama_worker.urlopen", return_value=RawResponse(b"not-json")):
            result = call_ollama_worker(WorkerRequest(task_text="do small task"))

        self.assertFalse(result.transport_ok)
        self.assertEqual(result.output_text, "")
        self.assertIsNotNone(result.error)

    def test_missing_message_content_returns_transport_failure(self):
        from tools.ollama_worker import call_ollama_worker

        with patch("tools.ollama_worker.urlopen", return_value=FakeResponse({"message": {}})):
            result = call_ollama_worker(WorkerRequest(task_text="do small task"))

        self.assertFalse(result.transport_ok)
        self.assertEqual(result.output_text, "")
        self.assertIsNotNone(result.error)

    def test_non_string_message_content_returns_transport_failure(self):
        from tools.ollama_worker import call_ollama_worker

        with patch("tools.ollama_worker.urlopen", return_value=FakeResponse({"message": {"content": 123}})):
            result = call_ollama_worker(WorkerRequest(task_text="do small task"))

        self.assertFalse(result.transport_ok)
        self.assertEqual(result.output_text, "")
        self.assertIsNotNone(result.error)


    def test_tool_session_initial_request_translates_tools_and_tool_call(self):
        from tools.harness_core import ToolRequest, ToolSpec, WorkerStep
        from tools.ollama_worker import OllamaToolSession

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            captured["timeout"] = timeout
            return FakeResponse(
                {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "function": {
                                    "index": 0,
                                    "name": "read_repo_text",
                                    "arguments": {"relative_path": "PROJECT.md"},
                                },
                            }
                        ],
                    }
                }
            )

        tool = ToolSpec(
            "read_repo_text",
            "Read text",
            {
                "type": "object",
                "required": ["relative_path"],
                "properties": {
                    "relative_path": {"type": "string"},
                },
            },
        )

        with patch("tools.ollama_worker.urlopen", side_effect=fake_urlopen):
            session = OllamaToolSession(
                WorkerRequest("inspect project"),
                tools=(tool,),
                base_url="http://127.0.0.1:11434",
                model="qwen3:8b",
                timeout_seconds=30.0,
            )
            step = session.start()

        self.assertEqual(captured["url"], "http://127.0.0.1:11434/api/chat")
        self.assertEqual(captured["payload"]["model"], "qwen3:8b")
        self.assertEqual(
            captured["payload"]["messages"],
            [{"role": "user", "content": "inspect project"}],
        )
        self.assertIs(captured["payload"]["stream"], False)
        self.assertIs(captured["payload"]["think"], False)
        self.assertEqual(
            captured["payload"]["tools"],
            [
                {
                    "type": "function",
                    "function": {
                        "name": "read_repo_text",
                        "description": "Read text",
                        "parameters": tool.input_schema,
                    },
                }
            ],
        )
        self.assertEqual(captured["timeout"], 30.0)
        self.assertEqual(
            step,
            WorkerStep(
                True,
                "",
                (
                    ToolRequest(
                        "call-1",
                        "read_repo_text",
                        {"relative_path": "PROJECT.md"},
                    ),
                ),
                None,
            ),
        )

    def test_tool_session_preserves_multiple_native_tool_call_order(self):
        from tools.harness_core import ToolRequest, ToolSpec
        from tools.ollama_worker import OllamaToolSession

        response = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call-1",
                        "function": {
                            "index": 0,
                            "name": "read_repo_text",
                            "arguments": {"relative_path": "a.txt"},
                        },
                    },
                    {
                        "id": "call-2",
                        "function": {
                            "index": 1,
                            "name": "write_repo_text",
                            "arguments": {
                                "relative_path": "b.txt",
                                "content": "B",
                            },
                        },
                    },
                ],
            }
        }

        tools = (
            ToolSpec("read_repo_text", "Read", {"type": "object"}),
            ToolSpec("write_repo_text", "Write", {"type": "object"}),
        )

        with patch("tools.ollama_worker.urlopen", return_value=FakeResponse(response)):
            step = OllamaToolSession(
                WorkerRequest("task"),
                tools=tools,
            ).start()

        self.assertEqual(
            step.tool_requests,
            (
                ToolRequest(
                    "call-1",
                    "read_repo_text",
                    {"relative_path": "a.txt"},
                ),
                ToolRequest(
                    "call-2",
                    "write_repo_text",
                    {"relative_path": "b.txt", "content": "B"},
                ),
            ),
        )

    def test_tool_session_continues_with_matching_tool_result(self):
        from tools.harness_core import ToolResult, ToolSpec, WorkerStep
        from tools.ollama_worker import OllamaToolSession

        payloads = []

        first_message = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call-1",
                    "function": {
                        "index": 0,
                        "name": "read_repo_text",
                        "arguments": {"relative_path": "PROJECT.md"},
                    },
                }
            ],
        }

        responses = [
            FakeResponse({"message": first_message}),
            FakeResponse(
                {
                    "message": {
                        "role": "assistant",
                        "content": "RESULT:PROBE-CONTENT",
                    }
                }
            ),
        ]

        def fake_urlopen(request, timeout):
            payloads.append(json.loads(request.data.decode("utf-8")))
            return responses[len(payloads) - 1]

        tool = ToolSpec(
            "read_repo_text",
            "Read text",
            {"type": "object"},
        )

        with patch("tools.ollama_worker.urlopen", side_effect=fake_urlopen):
            session = OllamaToolSession(
                WorkerRequest("inspect project"),
                tools=(tool,),
            )
            first = session.start()
            second = session.continue_with_tool_result(
                ToolResult("call-1", True, "PROBE-CONTENT", None)
            )

        self.assertEqual(first.tool_requests[0].call_id, "call-1")
        self.assertEqual(
            payloads[1]["messages"],
            [
                {"role": "user", "content": "inspect project"},
                first_message,
                {
                    "role": "tool",
                    "tool_name": "read_repo_text",
                    "content": "PROBE-CONTENT",
                },
            ],
        )
        self.assertIn("tools", payloads[1])
        self.assertEqual(
            second,
            WorkerStep(True, "RESULT:PROBE-CONTENT", (), None),
        )

    def test_tool_session_rejects_malformed_native_tool_call_without_id(self):
        from tools.harness_core import ToolSpec
        from tools.ollama_worker import OllamaToolSession

        malformed = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "function": {
                            "index": 0,
                            "name": "read_repo_text",
                            "arguments": {"relative_path": "PROJECT.md"},
                        }
                    }
                ],
            }
        }

        with patch(
            "tools.ollama_worker.urlopen",
            return_value=FakeResponse(malformed),
        ):
            step = OllamaToolSession(
                WorkerRequest("task"),
                tools=(ToolSpec("read_repo_text", "Read", {"type": "object"}),),
            ).start()

        self.assertFalse(step.transport_ok)
        self.assertEqual(step.tool_requests, ())
        self.assertIsNotNone(step.error)

    def test_tool_session_rejects_non_mapping_tool_arguments(self):
        from tools.harness_core import ToolSpec
        from tools.ollama_worker import OllamaToolSession

        malformed = {
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call-1",
                        "function": {
                            "index": 0,
                            "name": "read_repo_text",
                            "arguments": "PROJECT.md",
                        },
                    }
                ],
            }
        }

        with patch(
            "tools.ollama_worker.urlopen",
            return_value=FakeResponse(malformed),
        ):
            step = OllamaToolSession(
                WorkerRequest("task"),
                tools=(ToolSpec("read_repo_text", "Read", {"type": "object"}),),
            ).start()

        self.assertFalse(step.transport_ok)
        self.assertEqual(step.tool_requests, ())
        self.assertIsNotNone(step.error)

    def test_tool_session_rejects_mismatched_tool_result_without_second_request(self):
        from tools.harness_core import ToolResult, ToolSpec
        from tools.ollama_worker import OllamaToolSession

        calls = []

        def fake_urlopen(request, timeout):
            calls.append(request)
            return FakeResponse(
                {
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "function": {
                                    "index": 0,
                                    "name": "read_repo_text",
                                    "arguments": {"relative_path": "PROJECT.md"},
                                },
                            }
                        ],
                    }
                }
            )

        with patch("tools.ollama_worker.urlopen", side_effect=fake_urlopen):
            session = OllamaToolSession(
                WorkerRequest("task"),
                tools=(ToolSpec("read_repo_text", "Read", {"type": "object"}),),
            )
            session.start()
            step = session.continue_with_tool_result(
                ToolResult("wrong-call", True, "CONTENT", None)
            )

        self.assertEqual(len(calls), 1)
        self.assertFalse(step.transport_ok)
        self.assertEqual(step.tool_requests, ())
        self.assertIsNotNone(step.error)


    def test_tool_session_rejects_missing_message_content(self):
        from tools.harness_core import ToolSpec
        from tools.ollama_worker import OllamaToolSession

        malformed = {
            "message": {
                "role": "assistant",
                "tool_calls": [],
            }
        }

        with patch(
            "tools.ollama_worker.urlopen",
            return_value=FakeResponse(malformed),
        ):
            step = OllamaToolSession(
                WorkerRequest("task"),
                tools=(ToolSpec("read_repo_text", "Read", {"type": "object"}),),
            ).start()

        self.assertFalse(step.transport_ok)
        self.assertEqual(step.tool_requests, ())
        self.assertIsNotNone(step.error)


if __name__ == "__main__":
    unittest.main()
