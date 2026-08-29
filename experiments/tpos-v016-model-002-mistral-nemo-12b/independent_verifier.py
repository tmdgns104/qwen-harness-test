from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_DIR.parents[1]
OLD_VERIFIER_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "tpos-v016-model-001-qwen25-coder-14b"
    / "independent_verifier.py"
)
EXPECTED_RAW = EXPERIMENT_DIR / "raw_result.json"
EXPECTED_OUTPUT = EXPERIMENT_DIR / "verification_result.json"
TARGET_COMMIT = "748b77391f2b545e75943f1fefeb9f18277c446f"


def _load_old_verifier():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    spec = importlib.util.spec_from_file_location("model001_verifier", OLD_VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load independent verifier: {OLD_VERIFIER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(repo_root: Path, original_repo: Path) -> dict[str, object]:
    verifier = _load_old_verifier()
    raw_bytes = EXPECTED_RAW.read_bytes()
    raw = json.loads(raw_bytes.decode("utf-8"))
    if raw.get("experiment") != "TPOS-V016-MODEL-002-MISTRAL-NEMO-12B":
        raise ValueError("unexpected experiment ID")

    commands = {
        "direct_positive_negative_probe": verifier._run(
            ["python", "-B", "-c", verifier.DIRECT_CASE_PROBE], cwd=repo_root
        ),
        "focused_generated_test": verifier._run(
            [
                "python", "-m", "unittest",
                "tests.test_structured_state_v016_ref_identity", "-v",
            ], cwd=repo_root
        ),
        "existing_v016": verifier._run(
            ["python", "-m", "unittest", "tests.test_conversation_import_v016", "-v"],
            cwd=repo_root,
        ),
        "existing_v016_discovery_diagnostic": verifier._run(
            [
                "python", "-m", "unittest", "discover", "-s", "tests",
                "-p", "test_conversation_import_v016.py", "-v",
            ], cwd=repo_root
        ),
        "full_regression": verifier._run(
            ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=repo_root,
        ),
        "compile_generated_test": verifier._run(
            ["python", "-m", "compileall", "tests/test_structured_state_v016_ref_identity.py"],
            cwd=repo_root,
        ),
        "git_diff_check": verifier._git(repo_root, "diff", "--check"),
        "git_status": verifier._git(repo_root, "status", "--short"),
        "changed_paths": verifier._git(repo_root, "diff", "--name-status", TARGET_COMMIT),
        "original_status": verifier._git(original_repo, "status", "--short", "--branch"),
    }
    review = verifier._generated_source_review(repo_root)
    expected_original_status = raw["pre"]["original_repo_status"]["stdout"]
    scope_ok = (
        commands["changed_paths"]["stdout"] == ""
        and commands["git_status"]["stdout"] == ""
        and commands["original_status"]["stdout"] == expected_original_status
    )
    verdict, reason = verifier._classify(raw, review, scope_ok)
    result = {
        "raw_result_sha256": verifier._sha256_bytes(raw_bytes),
        "generated_source_review": review,
        "commands": commands,
        "independent_checks": {
            "canonical_production_positive_case_pass": commands["direct_positive_negative_probe"]["exit_code"] == 0,
            "canonical_production_negative_case_pass": commands["direct_positive_negative_probe"]["exit_code"] == 0,
            "worker_positive_case_pass": bool(review["exists"]) and commands["focused_generated_test"]["exit_code"] == 0,
            "worker_negative_case_pass": bool(review["exists"]) and commands["focused_generated_test"]["exit_code"] == 0,
            "stable_requirement_identity_is_ref": True,
            "expected_conflict_path": "requirements.REQ-HUMAN-001",
            "fixture_contract_is_valid": commands["direct_positive_negative_probe"]["exit_code"] == 0,
            "production_files_unchanged": commands["changed_paths"]["stdout"] == "",
            "existing_tests_unchanged": commands["changed_paths"]["stdout"] == "",
            "allowed_scope_only": scope_ok,
            "test_weakening": False,
            "generated_test_missing": not bool(review["exists"]),
        },
        "offload_log": verifier._last_offload_lines(),
        "verdict": verdict,
        "verdict_reason": reason,
    }
    EXPECTED_OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    reread = json.loads(EXPECTED_OUTPUT.read_text(encoding="utf-8"))
    if reread["verdict"] != verdict:
        raise ValueError("verification artifact reread check failed")
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Independent MODEL-002 verifier")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--original-repo", required=True)
    args = parser.parse_args()
    result = verify(Path(args.repo_root).resolve(), Path(args.original_repo).resolve())
    print(result["verdict"].replace("—", "-"))
    print(result["verdict_reason"])
    for name, command in result["commands"].items():
        print(f"{name}: exit={command['exit_code']} elapsed={command['elapsed_seconds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
