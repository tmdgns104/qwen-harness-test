from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from collections.abc import Mapping

from tools.harness_core import (
    ToolRequest,
    ToolResult,
    ToolSpec,
    WorkerRequest,
    WorkerResponse,
    WorkerStep,
)


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:8b"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_CONTINUATION_TIMEOUT_SECONDS = 60.0


def call_ollama_worker(
    request: WorkerRequest,
    *,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> WorkerResponse:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": request.task_text}],
        "stream": False,
        "think": False,
    }
    body = json.dumps(payload).encode("utf-8")
    http_request = Request(
        f"{base_url.rstrip("/")}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(http_request, timeout=timeout_seconds) as response:
            decoded = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        return WorkerResponse(transport_ok=False, output_text="", error=str(exc))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return WorkerResponse(transport_ok=False, output_text="", error=f"invalid Ollama response: {exc}")

    try:
        content = decoded["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("message.content must be a string")
    except (KeyError, TypeError) as exc:
        return WorkerResponse(transport_ok=False, output_text="", error=f"invalid Ollama response schema: {exc}")

    return WorkerResponse(transport_ok=True, output_text=content, error=None)

class OllamaToolSession:
    """Native Ollama tool interaction translated through backend-neutral records."""

    def __init__(
        self,
        request: WorkerRequest,
        *,
        tools: tuple[ToolSpec, ...],
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        continuation_timeout_seconds: float = DEFAULT_CONTINUATION_TIMEOUT_SECONDS,
    ) -> None:
        self.request = request
        self.tools = tools
        self.base_url = base_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.continuation_timeout_seconds = continuation_timeout_seconds
        self._messages = [
            {"role": "user", "content": request.task_text}
        ]
        self._pending_tools: dict[str, str] = {}

    def _native_tools(self) -> list[dict[str, object]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in self.tools
        ]

    def _request_step(
        self,
        *,
        timeout_seconds: float | None = None,
    ) -> tuple[WorkerStep, dict[str, object] | None]:
        payload = {
            "model": self.model,
            "messages": self._messages,
            "stream": False,
            "think": False,
            "tools": self._native_tools(),
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = Request(
            f"{self.base_url.rstrip('/')}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(
                http_request,
                timeout=(
                    self.timeout_seconds if timeout_seconds is None else timeout_seconds
                ),
            ) as response:
                decoded = json.loads(response.read().decode("utf-8"))
        except URLError as exc:
            return (
                WorkerStep(False, "", (), str(exc)),
                None,
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return (
                WorkerStep(
                    False,
                    "",
                    (),
                    f"invalid Ollama response: {exc}",
                ),
                None,
            )

        try:
            message = decoded["message"]
            if not isinstance(message, dict):
                raise TypeError("message must be an object")

            content = message["content"]
            if not isinstance(content, str):
                raise TypeError("message.content must be a string")

            raw_tool_calls = message.get("tool_calls", [])
            if not isinstance(raw_tool_calls, list):
                raise TypeError("message.tool_calls must be a list")

            requests: list[ToolRequest] = []
            pending: dict[str, str] = {}

            for raw_call in raw_tool_calls:
                if not isinstance(raw_call, dict):
                    raise TypeError("tool call must be an object")

                call_id = raw_call.get("id")
                if not isinstance(call_id, str) or not call_id:
                    raise TypeError("tool call id must be a non-empty string")

                function = raw_call.get("function")
                if not isinstance(function, dict):
                    raise TypeError("tool call function must be an object")

                name = function.get("name")
                if not isinstance(name, str) or not name:
                    raise TypeError("tool call name must be a non-empty string")

                arguments = function.get("arguments")
                if not isinstance(arguments, Mapping):
                    raise TypeError("tool call arguments must be a mapping")

                requests.append(
                    ToolRequest(
                        call_id=call_id,
                        name=name,
                        arguments=arguments,
                    )
                )
                pending[call_id] = name

        except (KeyError, TypeError) as exc:
            return (
                WorkerStep(
                    False,
                    "",
                    (),
                    f"invalid Ollama tool response schema: {exc}",
                ),
                None,
            )

        self._pending_tools = pending

        return (
            WorkerStep(
                True,
                content,
                tuple(requests),
                None,
            ),
            message,
        )

    def start(self) -> WorkerStep:
        step, assistant_message = self._request_step()
        if step.transport_ok and assistant_message is not None:
            self._messages.append(assistant_message)
        return step

    def continue_with_tool_result(
        self,
        result: ToolResult,
    ) -> WorkerStep:
        tool_name = self._pending_tools.get(result.call_id)
        if tool_name is None:
            return WorkerStep(
                False,
                "",
                (),
                "tool result call_id does not match a pending ToolRequest",
            )

        if result.ok:
            content = result.output
        elif result.error is not None:
            content = result.error
        else:
            content = result.output

        self._messages.append(
            {
                "role": "tool",
                "tool_name": tool_name,
                "content": content,
            }
        )
        del self._pending_tools[result.call_id]

        step, assistant_message = self._request_step(
            timeout_seconds=self.continuation_timeout_seconds,
        )
        if step.transport_ok and assistant_message is not None:
            self._messages.append(assistant_message)
        return step
