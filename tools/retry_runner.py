from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from tools.task_runner import (
    RunnerFailureKind,
    RunnerResult,
    run_single_task,
)


MAX_RUNNER_ATTEMPTS = 2


class RetryOutcomeKind(Enum):
    """Deterministic orchestration outcome; not Repository Task PASS."""

    NORMAL = "normal"
    FAIL = "fail"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class RetryOutcome:
    """Bounded Retry V1 orchestration result."""

    outcome_kind: RetryOutcomeKind
    attempts_consumed: int
    runner_result: RunnerResult
    error: str | None
    write_side_effect_risk: bool


def run_with_retry(
    repo_root: str | Path,
    task_id: str,
) -> RetryOutcome:
    attempts_consumed = 0
    write_side_effect_risk = False

    while attempts_consumed < MAX_RUNNER_ATTEMPTS:
        result = run_single_task(repo_root, task_id)
        attempts_consumed += 1
        write_side_effect_risk = (
            write_side_effect_risk or result.write_attempted
        )

        if result.interaction_ok:
            return RetryOutcome(
                outcome_kind=RetryOutcomeKind.NORMAL,
                attempts_consumed=attempts_consumed,
                runner_result=result,
                error=None,
                write_side_effect_risk=write_side_effect_risk,
            )

        if result.failure_kind in {
            RunnerFailureKind.SAFETY,
            RunnerFailureKind.STEP_BUDGET,
        }:
            return RetryOutcome(
                outcome_kind=RetryOutcomeKind.FAIL,
                attempts_consumed=attempts_consumed,
                runner_result=result,
                error=result.error,
                write_side_effect_risk=write_side_effect_risk,
            )

        if result.failure_kind is RunnerFailureKind.TRANSIENT_WORKER:
            if result.write_attempted:
                return RetryOutcome(
                    outcome_kind=RetryOutcomeKind.BLOCKED,
                    attempts_consumed=attempts_consumed,
                    runner_result=result,
                    error=result.error,
                    write_side_effect_risk=True,
                )

            if attempts_consumed < MAX_RUNNER_ATTEMPTS:
                continue

            return RetryOutcome(
                outcome_kind=RetryOutcomeKind.BLOCKED,
                attempts_consumed=attempts_consumed,
                runner_result=result,
                error=result.error,
                write_side_effect_risk=write_side_effect_risk,
            )

        # Unknown or absent failure metadata on an unsuccessful Runner result
        # is never guessed to be retryable.
        return RetryOutcome(
            outcome_kind=RetryOutcomeKind.FAIL,
            attempts_consumed=attempts_consumed,
            runner_result=result,
            error=result.error or "Runner failed without a recognized failure kind",
            write_side_effect_risk=write_side_effect_risk,
        )

    raise RuntimeError("unreachable retry orchestration state")
