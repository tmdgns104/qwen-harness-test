from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_DIR.parents[1]
OLD_DRIVER_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "tpos-v016-model-001-qwen25-coder-14b"
    / "benchmark_driver.py"
)
MODEL = "mistral-nemo:12b-instruct-2407-q3_K_S"
EXPECTED_OUTPUT = EXPERIMENT_DIR / "raw_result.json"


def _load_old_driver():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    spec = importlib.util.spec_from_file_location("model001_driver", OLD_DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load benchmark driver: {OLD_DRIVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="TPOS-V016-MODEL-002-MISTRAL-NEMO-12B")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--original-repo", required=True)
    parser.add_argument("--output", default=str(EXPECTED_OUTPUT))
    args = parser.parse_args()

    driver = _load_old_driver()
    # Reuse the frozen MODEL-001 implementation and canonical input. These are
    # process-local selections; no production source or prior evidence changes.
    driver.EXPERIMENT_ID = "TPOS-V016-MODEL-002-MISTRAL-NEMO-12B"
    driver.MODEL = MODEL
    driver.EXPECTED_OUTPUT = EXPECTED_OUTPUT
    result = driver.run(
        Path(args.repo_root).resolve(),
        Path(args.original_repo).resolve(),
        Path(args.output).resolve(),
    )
    print(result["harness"])
    print(f"total_wall_clock_seconds={result['total_wall_clock_seconds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
