from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from tools.harness_core import WorkerRequest, WorkerResponse


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:8b"
DEFAULT_TIMEOUT_SECONDS = 30.0


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

    content = decoded["message"]["content"]
    return WorkerResponse(transport_ok=True, output_text=content, error=None)
