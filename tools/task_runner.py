from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from tools.harness_core import (
    ChangeScope,
    ToolRequest,
    ToolResult,
    ToolSpec,
    WorkerRequest,
    WorkerStep,
    parse_change_scope,
    resolve_scoped_write_target,
)
from tools.ollama_worker import OllamaToolSession
from tools.repo_tools import read_repo_text, write_repo_text


MAX_WORKER_STEPS = 8

_TASK_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_CURRENT_TASK_PREFIX = "Current Task:"


class RunnerFailureKind(Enum):
    """Structured deterministic Runner failure classification."""

    TRANSIENT_WORKER = "transient_worker"
    SAFETY = "safety"
    STEP_BUDGET = "step_budget"


@dataclass(frozen=True)
class RunnerResult:
    """Deterministic Runner interaction result; not Repository Task PASS."""

    interaction_ok: bool
    output_text: str
    steps_consumed: int
    error: str | None
    failure_kind: RunnerFailureKind | None = None
    write_attempted: bool = False


def _runner_tools() -> tuple[ToolSpec, ...]:
    return (
        ToolSpec(
            name="read_repo_text",
            description="Read a UTF-8 text file inside the Repository.",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["relative_path"],
                "properties": {
                    "relative_path": {"type": "string"},
                },
            },
        ),
        ToolSpec(
            name="write_repo_text",
            description="Write UTF-8 text to an authorized Repository file.",
            input_schema={
                "type": "object",
                "additionalProperties": False,
                "required": ["relative_path", "content"],
                "properties": {
                    "relative_path": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
        ),
    )


def _load_active_task(
    repo_root: Path,
    task_id: str,
) -> tuple[str, ChangeScope]:
    if _TASK_ID_RE.fullmatch(task_id) is None:
        raise ValueError("invalid Task ID")

    status_path = repo_root / "STATUS.md"
    status_markdown = status_path.read_text(encoding="utf-8")

    current_lines = [
        line
        for line in status_markdown.splitlines()
        if line.startswith(_CURRENT_TASK_PREFIX)
    ]
    if len(current_lines) != 1:
        raise ValueError(
            f"expected exactly one Current Task line; found {len(current_lines)}"
        )

    expected = f"Current Task: {task_id} - ACTIVE"
    if current_lines[0] != expected:
        raise ValueError(
            "selected Task does not match the ACTIVE Current Task"
        )

    task_path = repo_root / "tasks" / f"{task_id}.md"
    if not task_path.is_file():
        raise FileNotFoundError(
            f"Task file not found: tasks/{task_id}.md"
        )

    task_markdown = task_path.read_text(encoding="utf-8")
    scope = parse_change_scope(task_markdown)
    return task_markdown, scope


def _default_session_factory(
    request: WorkerRequest,
    *,
    tools: tuple[ToolSpec, ...],
):
    return OllamaToolSession(
        request,
        tools=tools,
    )


def _validate_relative_path(relative_path: str) -> str:
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("relative_path must be a non-empty string")

    requested = Path(relative_path)
    if requested.is_absolute():
        raise ValueError("absolute paths are not allowed")
    if ".." in requested.parts:
        raise ValueError("parent-directory path escape is not allowed")

    return requested.as_posix()


def _validate_tool_request(request: ToolRequest) -> tuple[str, Mapping[str, object]]:
    if not isinstance(request.call_id, str) or not request.call_id:
        raise ValueError("tool call_id must be a non-empty string")
    if not isinstance(request.name, str) or not request.name:
        raise ValueError("tool name must be a non-empty string")
    if not isinstance(request.arguments, Mapping):
        raise ValueError("tool arguments must be a mapping")

    if request.name == "read_repo_text":
        expected = {"relative_path"}
    elif request.name == "write_repo_text":
        expected = {"relative_path", "content"}
    else:
        raise ValueError(f"unsupported tool: {request.name}")

    actual = set(request.arguments.keys())
    if actual != expected:
        raise ValueError(
            f"{request.name} arguments must be exactly {sorted(expected)}"
        )

    relative_path = request.arguments.get("relative_path")
    normalized = _validate_relative_path(relative_path)

    if request.name == "write_repo_text":
        content = request.arguments.get("content")
        if not isinstance(content, str):
            raise ValueError("write_repo_text content must be a string")

    return normalized, request.arguments


def _execute_tool_request(
    repo_root: Path,
    task_id: str,
    scope: ChangeScope,
    request: ToolRequest,
) -> tuple[ToolResult, bool]:
    relative_path, arguments = _validate_tool_request(request)

    if request.name == "read_repo_text":
        try:
            output = read_repo_text(repo_root, relative_path)
        except (OSError, UnicodeError, ValueError) as exc:
            return (
                ToolResult(
                    call_id=request.call_id,
                    ok=False,
                    output="",
                    error=str(exc),
                ),
                False,
            )
        return (
            ToolResult(
                call_id=request.call_id,
                ok=True,
                output=output,
                error=None,
            ),
            False,
        )

    requested_target = resolve_scoped_write_target(
        repo_root,
        relative_path,
        scope,
    )
    lifecycle_targets = {
        os.path.normcase(str((repo_root / "STATUS.md").resolve())),
        os.path.normcase(str((repo_root / "tasks" / f"{task_id}.md").resolve())),
    }
    if os.path.normcase(str(requested_target)) in lifecycle_targets:
        raise ValueError("Worker write to lifecycle-control path is not allowed")

    content = arguments["content"]

    # Side-effect risk begins immediately before the Repository write boundary.
    write_attempted = True

    try:
        output = write_repo_text(
            repo_root,
            relative_path,
            content,
            allowed_changes=scope.allowed,
            forbidden_changes=scope.forbidden,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        return (
            ToolResult(
                call_id=request.call_id,
                ok=False,
                output="",
                error=str(exc),
            ),
            write_attempted,
        )

    return (
        ToolResult(
            call_id=request.call_id,
            ok=True,
            output=output,
            error=None,
        ),
        write_attempted,
    )


def run_single_task(
    repo_root: str | Path,
    task_id: str,
    *,
    session_factory: Callable = _default_session_factory,
) -> RunnerResult:
    root = Path(repo_root).resolve()

    try:
        task_markdown, scope = _load_active_task(
            root,
            task_id,
        )
    except (OSError, ValueError) as exc:
        return RunnerResult(
            interaction_ok=False,
            output_text="",
            steps_consumed=0,
            error=str(exc),
            failure_kind=RunnerFailureKind.SAFETY,
            write_attempted=False,
        )

    request = WorkerRequest(task_text=task_markdown)
    tools = _runner_tools()

    try:
        session = session_factory(
            request,
            tools=tools,
        )
        step: WorkerStep = session.start()
    except Exception as exc:
        return RunnerResult(
            interaction_ok=False,
            output_text="",
            steps_consumed=0,
            error=f"Worker session failed: {exc}",
            failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
            write_attempted=False,
        )

    steps_consumed = 1
    write_attempted = False

    while True:
        if not step.transport_ok:
            return RunnerResult(
                interaction_ok=False,
                output_text="",
                steps_consumed=steps_consumed,
                error=step.error or "Worker transport failed",
                failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
                write_attempted=write_attempted,
            )

        request_count = len(step.tool_requests)

        if request_count == 0:
            return RunnerResult(
                interaction_ok=True,
                output_text=step.output_text,
                steps_consumed=steps_consumed,
                error=None,
                failure_kind=None,
                write_attempted=write_attempted,
            )

        if request_count != 1:
            return RunnerResult(
                interaction_ok=False,
                output_text=step.output_text,
                steps_consumed=steps_consumed,
                error="Worker step must contain zero or one ToolRequest",
                failure_kind=RunnerFailureKind.SAFETY,
                write_attempted=write_attempted,
            )

        if steps_consumed >= MAX_WORKER_STEPS:
            return RunnerResult(
                interaction_ok=False,
                output_text=step.output_text,
                steps_consumed=steps_consumed,
                error="Worker step budget exhausted",
                failure_kind=RunnerFailureKind.STEP_BUDGET,
                write_attempted=write_attempted,
            )

        tool_request = step.tool_requests[0]

        try:
            tool_result, tool_write_attempted = _execute_tool_request(
                root,
                task_id,
                scope,
                tool_request,
            )
            write_attempted = write_attempted or tool_write_attempted
        except (TypeError, ValueError) as exc:
            return RunnerResult(
                interaction_ok=False,
                output_text=step.output_text,
                steps_consumed=steps_consumed,
                error=str(exc),
                failure_kind=RunnerFailureKind.SAFETY,
                write_attempted=write_attempted,
            )

        try:
            step = session.continue_with_tool_result(tool_result)
        except Exception as exc:
            return RunnerResult(
                interaction_ok=False,
                output_text="",
                steps_consumed=steps_consumed,
                error=f"Worker continuation failed: {exc}",
                failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
                write_attempted=write_attempted,
            )

        steps_consumed += 1
