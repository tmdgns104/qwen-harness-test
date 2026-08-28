from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from tools import retry_runner, task_runner
from tools.harness_core import ToolRequest, ToolResult, WorkerRequest, WorkerStep
from tools.ollama_worker import (
    DEFAULT_BASE_URL,
    DEFAULT_CONTINUATION_TIMEOUT_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    OllamaToolSession,
)
from tools.worker_brief import REQUIRED_BRIEF_SECTIONS, build_worker_brief


EXPERIMENT_ID = "TPOS-V016-MODEL-001-QWEN25-CODER-14B"
TARGET_TASK_ID = "TPOS-V016-REG-002"
TARGET_COMMIT = "748b77391f2b545e75943f1fefeb9f18277c446f"
MODEL = "qwen2.5-coder:14b-instruct-q3_K_S"
EXPECTED_CONTEXT = 16384
EXPECTED_TASK_SHA256 = (
    "b4ea3b067e897da23b7ef6f2f61f75daf677ecae081bc30d751e7b255c56c7a0"
)
EXPECTED_BRIEF_SHA256 = (
    "cd5f861fce3288d68edde4850d61c73677e7e5b9c5ca7252c1b9f8c0eb545081"
)
EXPECTED_OUTPUT = Path(__file__).resolve().parent / "raw_result.json"
CANONICAL_DIR = Path(__file__).resolve().parent / "canonical"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _run_command(arguments: list[str], *, cwd: Path | None = None) -> dict[str, object]:
    started = time.perf_counter()
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "arguments": arguments,
        "exit_code": completed.returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _git(repo_root: Path, *arguments: str) -> dict[str, object]:
    return _run_command(["git", *arguments], cwd=repo_root)


def _ollama_json(path: str, payload: dict[str, object] | None = None) -> object:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        f"{DEFAULT_BASE_URL.rstrip('/')}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="GET" if body is None else "POST",
    )
    with urlopen(request, timeout=10.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _model_metadata() -> dict[str, object]:
    tags = _ollama_json("/api/tags")
    show = _ollama_json("/api/show", {"model": MODEL})
    if not isinstance(tags, dict) or not isinstance(show, dict):
        raise ValueError("unexpected Ollama metadata response")
    models = tags.get("models")
    if not isinstance(models, list):
        raise ValueError("Ollama tags response has no models list")
    matches = [entry for entry in models if entry.get("name") == MODEL]
    if len(matches) != 1:
        raise ValueError(f"expected one exact model tag, found {len(matches)}")
    return {"tag": matches[0], "show": show}


def _bounded_arguments(request: ToolRequest) -> dict[str, object]:
    if not isinstance(request.arguments, Mapping):
        return {"invalid_arguments_type": type(request.arguments).__name__}
    result: dict[str, object] = {}
    for name in sorted(request.arguments):
        value = request.arguments[name]
        if name == "content" and isinstance(value, str):
            result["content_length"] = len(value)
            result["content_sha256"] = _sha256_text(value)
        else:
            result[name] = value
    return result


def _step_record(
    phase: str,
    elapsed_seconds: float,
    step: WorkerStep | None,
    error: BaseException | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "phase": phase,
        "elapsed_seconds": round(elapsed_seconds, 6),
    }
    if error is not None:
        record["exception"] = f"{type(error).__name__}: {error}"
        return record
    if step is None:
        raise ValueError("step or error is required")
    record.update(
        {
            "transport_ok": step.transport_ok,
            "output_length": len(step.output_text),
            "output_sha256": _sha256_text(step.output_text),
            "error": step.error,
            "tool_request_count": len(step.tool_requests),
            "tool_requests": [
                {
                    "call_id": request.call_id,
                    "name": request.name,
                    "arguments": _bounded_arguments(request),
                }
                for request in step.tool_requests
            ],
        }
    )
    return record


def _tool_result_record(result: ToolResult) -> dict[str, object]:
    return {
        "call_id": result.call_id,
        "ok": result.ok,
        "output_length": len(result.output),
        "output_sha256": _sha256_text(result.output),
        "error": result.error,
    }


class MeasuredSession:
    def __init__(
        self,
        request: WorkerRequest,
        *,
        tools,
        expected_brief: str,
        trace: list[dict[str, object]],
    ) -> None:
        if request.task_text != expected_brief:
            raise ValueError("runtime Worker Brief differs from canonical input")
        self._trace = trace
        self._session = OllamaToolSession(
            request,
            tools=tools,
            model=MODEL,
        )

    def start(self) -> WorkerStep:
        started = time.perf_counter()
        try:
            step = self._session.start()
        except Exception as exc:
            self._trace.append(
                _step_record("initial", time.perf_counter() - started, None, exc)
            )
            raise
        self._trace.append(
            _step_record("initial", time.perf_counter() - started, step)
        )
        return step

    def continue_with_tool_result(self, result: ToolResult) -> WorkerStep:
        started = time.perf_counter()
        try:
            step = self._session.continue_with_tool_result(result)
        except Exception as exc:
            record = _step_record(
                "continuation",
                time.perf_counter() - started,
                None,
                exc,
            )
            record["tool_result"] = _tool_result_record(result)
            self._trace.append(record)
            raise
        record = _step_record(
            "continuation",
            time.perf_counter() - started,
            step,
        )
        record["tool_result"] = _tool_result_record(result)
        self._trace.append(record)
        return step


def _read_canonical_inputs() -> tuple[str, str]:
    task = (CANONICAL_DIR / "TPOS-V016-REG-002.md").read_text(encoding="utf-8")
    brief = (CANONICAL_DIR / "worker_brief.md").read_text(encoding="utf-8")
    if _sha256_text(task) != EXPECTED_TASK_SHA256:
        raise ValueError("canonical Task hash mismatch")
    if _sha256_text(brief) != EXPECTED_BRIEF_SHA256:
        raise ValueError("canonical Worker Brief hash mismatch")
    if build_worker_brief(task) != brief:
        raise ValueError("canonical Worker Brief is not the exact Task projection")
    return task, brief


def _validate_runtime_policy() -> dict[str, object]:
    tools = task_runner._runner_tools()
    tool_schemas = [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        }
        for tool in tools
    ]
    policy = {
        "model": MODEL,
        "expected_context": EXPECTED_CONTEXT,
        "think": False,
        "initial_timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        "continuation_timeout_seconds": DEFAULT_CONTINUATION_TIMEOUT_SECONDS,
        "max_worker_steps": task_runner.MAX_WORKER_STEPS,
        "max_runner_attempts": retry_runner.MAX_RUNNER_ATTEMPTS,
        "tools": tool_schemas,
    }
    expected = (30.0, 60.0, 8, 2)
    actual = (
        DEFAULT_TIMEOUT_SECONDS,
        DEFAULT_CONTINUATION_TIMEOUT_SECONDS,
        task_runner.MAX_WORKER_STEPS,
        retry_runner.MAX_RUNNER_ATTEMPTS,
    )
    if actual != expected:
        raise ValueError(f"runtime policy differs from benchmark contract: {actual}")
    if [tool.name for tool in tools] != ["read_repo_text", "write_repo_text"]:
        raise ValueError("tool set differs from benchmark contract")
    return policy


def _preconditions(repo_root: Path, original_repo: Path, task: str, brief: str) -> dict[str, object]:
    head = _git(repo_root, "rev-parse", "HEAD")
    status = _git(repo_root, "status", "--short")
    original_status = _git(original_repo, "status", "--short", "--branch")
    target_task_path = repo_root / "tasks" / f"{TARGET_TASK_ID}.md"
    output_path = repo_root / "tests" / "test_structured_state_v016_ref_identity.py"
    target_task = target_task_path.read_text(encoding="utf-8")
    if head["exit_code"] != 0 or str(head["stdout"]).strip() != TARGET_COMMIT:
        raise ValueError("isolated target is not at the canonical Task commit")
    if status["exit_code"] != 0 or status["stdout"] != "":
        raise ValueError("isolated target is not clean")
    if target_task != task or build_worker_brief(target_task) != brief:
        raise ValueError("isolated target Task/Brief differs from canonical input")
    if output_path.exists():
        raise ValueError("benchmark output test already exists")
    return {
        "target_head": head,
        "target_status": status,
        "target_output_absent": True,
        "original_repo_status": original_status,
    }


def _run_benchmark(repo_root: Path, expected_brief: str) -> tuple[object, list[dict[str, object]], float]:
    attempts: list[dict[str, object]] = []

    def measured_run_single_task(root: str | Path, task_id: str):
        attempt_number = len(attempts) + 1
        trace: list[dict[str, object]] = []

        def session_factory(request: WorkerRequest, *, tools):
            return MeasuredSession(
                request,
                tools=tools,
                expected_brief=expected_brief,
                trace=trace,
            )

        result = task_runner.run_single_task(
            root,
            task_id,
            session_factory=session_factory,
        )
        attempts.append(
            {
                "attempt": attempt_number,
                "trace": trace,
                "runner_result": {
                    "interaction_ok": result.interaction_ok,
                    "output_text": result.output_text,
                    "steps_consumed": result.steps_consumed,
                    "error": result.error,
                    "failure_kind": (
                        result.failure_kind.name
                        if result.failure_kind is not None
                        else "NONE"
                    ),
                    "write_attempted": result.write_attempted,
                },
            }
        )
        return result

    original = retry_runner.run_single_task
    started = time.perf_counter()
    try:
        retry_runner.run_single_task = measured_run_single_task
        outcome = retry_runner.run_with_retry(repo_root, TARGET_TASK_ID)
    finally:
        retry_runner.run_single_task = original
    return outcome, attempts, time.perf_counter() - started


def _outcome_record(outcome: object) -> dict[str, object]:
    runner_result = outcome.runner_result
    return {
        "outcome": outcome.outcome_kind.name,
        "attempts": outcome.attempts_consumed,
        "failure_kind": (
            runner_result.failure_kind.name
            if runner_result.failure_kind is not None
            else "NONE"
        ),
        "write_side_effect_risk": outcome.write_side_effect_risk,
        "error": outcome.error,
        "worker_output": runner_result.output_text,
    }


def _post_state(repo_root: Path, original_repo: Path, original_status: str) -> dict[str, object]:
    output_path = repo_root / "tests" / "test_structured_state_v016_ref_identity.py"
    post_original = _git(original_repo, "status", "--short", "--branch")
    generated = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    return {
        "target_head": _git(repo_root, "rev-parse", "HEAD"),
        "target_status": _git(repo_root, "status", "--short"),
        "changed_paths": _git(repo_root, "diff", "--name-status", TARGET_COMMIT),
        "diff": _git(repo_root, "diff", TARGET_COMMIT, "--"),
        "generated_test_exists": generated is not None,
        "generated_test": generated,
        "generated_test_sha256": _sha256_text(generated) if generated is not None else None,
        "original_repo_status": post_original,
        "original_repo_unchanged": post_original["stdout"] == original_status,
    }


def _runtime_observations() -> dict[str, object]:
    return {
        "ollama_version": _run_command(["ollama", "--version"]),
        "ollama_ps": _run_command(["ollama", "ps"]),
        "nvidia_smi_gpu": _run_command(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,memory.used,memory.free,utilization.gpu,power.draw",
                "--format=csv,noheader",
            ]
        ),
        "nvidia_smi_processes": _run_command(
            [
                "nvidia-smi",
                "--query-compute-apps=pid,process_name,used_memory",
                "--format=csv,noheader",
            ]
        ),
    }


def run(repo_root: Path, original_repo: Path, output: Path) -> dict[str, object]:
    if output.resolve() != EXPECTED_OUTPUT:
        raise ValueError(f"output must be exactly {EXPECTED_OUTPUT}")
    task, brief = _read_canonical_inputs()
    policy = _validate_runtime_policy()
    model = _model_metadata()
    pre = _preconditions(repo_root, original_repo, task, brief)
    observations_before = _runtime_observations()

    started_at = datetime.now(timezone.utc).isoformat()
    outcome, attempts, elapsed = _run_benchmark(repo_root, brief)
    finished_at = datetime.now(timezone.utc).isoformat()

    data: dict[str, object] = {
        "experiment": EXPERIMENT_ID,
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "total_wall_clock_seconds": round(elapsed, 6),
        "canonical": {
            "target_commit": TARGET_COMMIT,
            "task_sha256": _sha256_text(task),
            "brief_sha256": _sha256_text(brief),
            "required_brief_sections": list(REQUIRED_BRIEF_SECTIONS),
            "brief_exactly_rebuilt": build_worker_brief(task) == brief,
        },
        "policy": policy,
        "model_metadata": model,
        "pre": pre,
        "attempt_records": attempts,
        "harness": _outcome_record(outcome),
        "post": _post_state(
            repo_root,
            original_repo,
            str(pre["original_repo_status"]["stdout"]),
        ),
        "runtime_before": observations_before,
        "runtime_after": _runtime_observations(),
    }
    output.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=EXPERIMENT_ID)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--original-repo", required=True)
    parser.add_argument("--output", default=str(EXPECTED_OUTPUT))
    arguments = parser.parse_args()
    result = run(
        Path(arguments.repo_root).resolve(),
        Path(arguments.original_repo).resolve(),
        Path(arguments.output).resolve(),
    )
    print(json.dumps(result["harness"], ensure_ascii=False))
    print(f"total_wall_clock_seconds={result['total_wall_clock_seconds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
