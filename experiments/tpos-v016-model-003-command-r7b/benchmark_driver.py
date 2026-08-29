from __future__ import annotations
import importlib.util, sys
from pathlib import Path
EXPERIMENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_DIR.parents[1]
OLD = PROJECT_ROOT / 'experiments/tpos-v016-model-001-qwen25-coder-14b/benchmark_driver.py'
MODEL = 'command-r7b:7b-12-2024-q4_K_M'
def main() -> int:
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--repo-root', required=True); p.add_argument('--original-repo', required=True)
    a = p.parse_args(); sys.path.insert(0, str(PROJECT_ROOT))
    spec = importlib.util.spec_from_file_location('frozen_driver', OLD); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    mod.EXPERIMENT_ID = 'TPOS-V016-MODEL-003-COMMAND-R7B'; mod.MODEL = MODEL; mod.EXPECTED_OUTPUT = EXPERIMENT_DIR/'raw_result.json'
    result = mod.run(Path(a.repo_root).resolve(), Path(a.original_repo).resolve(), mod.EXPECTED_OUTPUT)
    print(result['harness']); print(f"total_wall_clock_seconds={result['total_wall_clock_seconds']}"); return 0
if __name__ == '__main__': raise SystemExit(main())
