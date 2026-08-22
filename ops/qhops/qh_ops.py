from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REMOTE = "origin"
REMOTE_BRANCH = "main"
CONFIG_DIR = Path.home() / ".qhops"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Stop(RuntimeError):
    pass


def run(
    cmd: list[str],
    cwd: Path,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(
            result.stderr,
            file=sys.stderr,
            end="" if result.stderr.endswith("\n") else "\n",
        )
    if check and result.returncode != 0:
        raise Stop(f"command failed ({result.returncode}): {' '.join(cmd)}")
    return result


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(["git", *args], root, check=check)


def git_root_from(path: Path) -> Path | None:
    try:
        candidate = path.expanduser().resolve()
    except OSError:
        return None

    if not candidate.exists():
        return None

    cwd = candidate if candidate.is_dir() else candidate.parent
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    return Path(result.stdout.strip()).resolve()


def validate_repo(path: Path) -> Path:
    root = git_root_from(path)
    if root is None:
        raise Stop(f"not inside a Git repository: {path}")

    qh = root / "tools" / "qh.py"
    if not qh.is_file():
        raise Stop(f"not a Qwen Harness repository (missing tools/qh.py): {root}")

    return root


def load_config() -> dict:
    if not CONFIG_FILE.is_file():
        return {}

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Stop(f"invalid qhops config: {CONFIG_FILE}: {exc}") from exc

    if not isinstance(data, dict):
        raise Stop(f"invalid qhops config object: {CONFIG_FILE}")
    return data


def save_default_repo(root: Path) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "default_repo": str(root),
    }
    CONFIG_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_repo(explicit: str | None = None) -> Path:
    # 1) Explicit CLI override.
    if explicit:
        return validate_repo(Path(explicit))

    # 2) Current working directory, if it is already inside a Qwen Harness repo.
    cwd_root = git_root_from(Path.cwd())
    if cwd_root is not None and (cwd_root / "tools" / "qh.py").is_file():
        return cwd_root

    # 3) Environment override.
    env_repo = os.environ.get("QH_REPO")
    if env_repo:
        return validate_repo(Path(env_repo))

    # 4) User-level configured default repo.
    config = load_config()
    configured = config.get("default_repo")
    if configured:
        return validate_repo(Path(configured))

    raise Stop(
        "no Qwen Harness repository is configured.\n"
        "Run once: qhops init <repository-path>"
    )


def status_porcelain(root: Path) -> str:
    return git(root, "status", "--porcelain").stdout


def require_clean(root: Path) -> None:
    status = status_porcelain(root)
    if status.strip():
        raise Stop("working tree is not clean:\n" + status)


def current_task_id(root: Path) -> str:
    status_file = root / "STATUS.md"
    if not status_file.is_file():
        raise Stop(f"STATUS.md not found: {root}")

    text = status_file.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.startswith("Current Task:")]
    if len(lines) != 1:
        raise Stop(f"expected exactly one Current Task line; found {len(lines)}")

    match = re.match(r"Current Task:\s+(\S+)", lines[0])
    if not match:
        raise Stop("could not parse Current Task")
    return match.group(1)


def current_task_path(root: Path) -> Path:
    task_id = current_task_id(root)
    path = root / "tasks" / f"{task_id}.md"
    if not path.is_file():
        raise Stop(f"task file not found: {path}")
    return path


def changed_paths(root: Path) -> tuple[str, ...]:
    tracked = git(root, "diff", "--name-only", "-z", "HEAD", "--").stdout
    staged = git(root, "diff", "--cached", "--name-only", "-z", "--").stdout
    untracked = git(
        root,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
    ).stdout

    items: set[str] = set()
    for output in (tracked, staged, untracked):
        for item in output.split("\0"):
            if item:
                items.add(item.replace("\\", "/"))
    return tuple(sorted(items))


def import_harness(root: Path):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from tools.harness_core import (
        VerificationContract,
        is_path_allowed,
        parse_change_scope,
        parse_verification_commands,
        run_verification_commands,
    )

    return (
        VerificationContract,
        is_path_allowed,
        parse_change_scope,
        parse_verification_commands,
        run_verification_commands,
    )


def safe_push(root: Path) -> None:
    print("== fetch remote ==")
    git(root, "fetch", REMOTE, REMOTE_BRANCH)

    ancestor = git(
        root,
        "merge-base",
        "--is-ancestor",
        f"{REMOTE}/{REMOTE_BRANCH}",
        "HEAD",
        check=False,
    )
    if ancestor.returncode != 0:
        raise Stop(
            f"{REMOTE}/{REMOTE_BRANCH} is not an ancestor of HEAD; "
            "refusing non-fast-forward push"
        )

    print("== fast-forward push ==")
    git(root, "push", REMOTE, f"HEAD:{REMOTE_BRANCH}")


def first_verification(root: Path) -> tuple[str, object]:
    (
        VerificationContract,
        _,
        _,
        parse_verification_commands,
        run_verification_commands,
    ) = import_harness(root)

    markdown = current_task_path(root).read_text(encoding="utf-8")
    contract = parse_verification_commands(markdown)
    if not contract.commands:
        raise Stop("current Task has no Verification commands")

    command = contract.commands[0]
    result = run_verification_commands(
        VerificationContract(commands=(command,)),
        str(root),
    )[0]
    return command, result


def qh(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(
        [sys.executable, str(root / "tools" / "qh.py"), *args],
        root,
        check=check,
    )


def cmd_init(repo_arg: str) -> None:
    root = validate_repo(Path(repo_arg))
    save_default_repo(root)
    print(f"Default repository configured: {root}")
    print(f"Config: {CONFIG_FILE}")


def cmd_config() -> None:
    config = load_config()
    configured = config.get("default_repo")
    print(f"Config file: {CONFIG_FILE}")
    print(f"Default repository: {configured or '(not configured)'}")
    env_repo = os.environ.get("QH_REPO")
    print(f"QH_REPO override: {env_repo or '(not set)'}")


def cmd_status(root: Path) -> None:
    print(f"Repository: {root}")
    print(f"Current Task: {current_task_id(root)}")
    print(f"HEAD: {git(root, 'rev-parse', 'HEAD').stdout.strip()}")
    print("Git status:")
    status = status_porcelain(root)
    print(status if status.strip() else "(clean)")


def approve_task_file(root: Path, task_id: str) -> bool:
    path = root / "tasks" / f"{task_id}.md"
    if not path.is_file():
        raise Stop(f"task file not found: {path}")

    text = path.read_text(encoding="utf-8")
    marker = "## Status"
    if text.count(marker) != 1:
        raise Stop("target task must contain exactly one ## Status section")

    lines = text.splitlines()
    idx = lines.index(marker) + 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        raise Stop("target task status value missing")

    value = lines[idx]
    if value == "APPROVED - READY FOR CONTRACT BASELINE":
        return False
    if value != "PLANNED":
        raise Stop(f"target task is not PLANNED/APPROVED: {value}")

    lines[idx] = "APPROVED - READY FOR CONTRACT BASELINE"
    newline = "\n" if text.endswith("\n") else ""
    path.write_text("\n".join(lines) + newline, encoding="utf-8")
    return True


def cmd_activate(root: Path, task_id: str) -> None:
    require_clean(root)

    print(f"== Human-invoked activation: {task_id} ==")
    changed = approve_task_file(root, task_id)
    if changed:
        git(root, "add", f"tasks/{task_id}.md")
        git(root, "commit", "-m", f"approve {task_id} contract baseline")

    require_clean(root)
    qh(root, "start", task_id)

    paths = changed_paths(root)
    if paths != ("STATUS.md",):
        raise Stop(f"qh start changed unexpected paths: {paths}")

    git(root, "add", "STATUS.md")
    git(root, "commit", "-m", f"start {task_id}")
    require_clean(root)
    safe_push(root)
    print(f"ACTIVE and pushed: {task_id}")


def cmd_red(root: Path, sha: str) -> None:
    require_clean(root)
    git(root, "fetch", REMOTE)
    git(root, "cherry-pick", sha)
    require_clean(root)

    command, result = first_verification(root)
    print(f"Focused RED command: {command}")
    print(f"Exit Code: {result.exit_code}")
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(
            result.stderr,
            file=sys.stderr,
            end="" if result.stderr.endswith("\n") else "\n",
        )

    if result.exit_code == 0:
        raise Stop("focused RED unexpectedly passed; stop and review")

    print("RED confirmed. Do not push yet.")


def cmd_green(root: Path, sha: str) -> None:
    require_clean(root)
    git(root, "fetch", REMOTE)
    git(root, "cherry-pick", sha)
    require_clean(root)

    print("== full Task Verification ==")
    qh(root, "verify")
    require_clean(root)

    git(root, "diff", "--check")
    safe_push(root)
    print("GREEN verified and implementation history pushed.")


def cmd_verify(root: Path) -> None:
    print("== Task Verification ==")
    qh(root, "verify")
    print("== diff check ==")
    git(root, "diff", "--check")
    print("Verification commands passed.")


def cmd_commit_impl(root: Path) -> None:
    task_id = current_task_id(root)
    task_path = current_task_path(root)
    lifecycle = {"STATUS.md", task_path.relative_to(root).as_posix()}

    before = changed_paths(root)
    if not before:
        raise Stop("no implementation changes to commit")
    if any(path in lifecycle for path in before):
        raise Stop(f"lifecycle files must not be in implementation changes: {before}")

    (_, is_path_allowed, parse_change_scope, _, _) = import_harness(root)
    markdown = task_path.read_text(encoding="utf-8")
    scope = parse_change_scope(markdown)
    bad = [path for path in before if not is_path_allowed(path, scope)]
    if bad:
        raise Stop(f"changed paths outside Task scope: {bad}")

    cmd_verify(root)

    after = changed_paths(root)
    if any(path in lifecycle for path in after):
        raise Stop(f"Verification changed lifecycle files: {after}")

    bad = [path for path in after if not is_path_allowed(path, scope)]
    if bad:
        raise Stop(f"post-Verification paths outside Task scope: {bad}")

    if not after:
        raise Stop("no changes remain after Verification")

    for path in after:
        git(root, "add", "--", path)

    git(root, "commit", "-m", f"implement {task_id}")
    require_clean(root)
    safe_push(root)
    print(f"Implementation committed and pushed: {task_id}")


def cmd_finish(root: Path) -> None:
    require_clean(root)

    task_id = current_task_id(root)
    task_path = current_task_path(root)
    task_rel = task_path.relative_to(root).as_posix()
    head = git(root, "rev-parse", "HEAD").stdout.strip()

    print(f"== authoritative close {task_id} @ {head} ==")
    qh(root, "close", head)

    paths = changed_paths(root)
    expected = tuple(sorted(("STATUS.md", task_rel)))
    if paths != expected:
        raise Stop(
            f"qh close changed unexpected paths: {paths}; "
            f"expected exactly {expected}"
        )

    git(root, "add", "STATUS.md", task_rel)
    git(root, "commit", "-m", f"mark {task_id} complete")
    require_clean(root)
    safe_push(root)
    print(f"COMPLETE - VERIFIED and pushed: {task_id}")


def extract_repo_override(argv: list[str]) -> tuple[str | None, list[str]]:
    args = list(argv)
    explicit_repo = None

    if len(args) >= 2 and args[0] == "--repo":
        explicit_repo = args[1]
        args = args[2:]

    return explicit_repo, args


def usage() -> None:
    print(
        "qhops - portable Qwen Harness operations helper\n"
        "\n"
        "First-time setup:\n"
        "  qhops init <repository-path>\n"
        "\n"
        "Commands:\n"
        "  qhops status\n"
        "  qhops config\n"
        "  qhops activate <TASK-ID>\n"
        "  qhops red <RED-COMMIT-SHA>\n"
        "  qhops green <IMPLEMENTATION-COMMIT-SHA>\n"
        "  qhops verify\n"
        "  qhops commit-impl\n"
        "  qhops finish\n"
        "\n"
        "Repository selection priority:\n"
        "  1. --repo <path>\n"
        "  2. current directory, when inside a Qwen Harness repo\n"
        "  3. QH_REPO environment variable\n"
        "  4. qhops init saved default\n"
        "\n"
        "Examples:\n"
        "  qhops init D:\\qwen-harness-test\n"
        "  qhops status\n"
        "  qhops --repo D:\\another-harness status\n"
    )


def main() -> int:
    try:
        explicit_repo, args = extract_repo_override(sys.argv[1:])

        if not args:
            usage()
            return 2

        command = args[0]
        rest = args[1:]

        if command == "init" and len(rest) == 1:
            cmd_init(rest[0])
            return 0

        if command == "config" and not rest:
            cmd_config()
            return 0

        root = resolve_repo(explicit_repo)

        if command == "status" and not rest:
            cmd_status(root)
        elif command == "activate" and len(rest) == 1:
            cmd_activate(root, rest[0])
        elif command == "red" and len(rest) == 1:
            cmd_red(root, rest[0])
        elif command == "green" and len(rest) == 1:
            cmd_green(root, rest[0])
        elif command == "verify" and not rest:
            cmd_verify(root)
        elif command == "commit-impl" and not rest:
            cmd_commit_impl(root)
        elif command == "finish" and not rest:
            cmd_finish(root)
        else:
            usage()
            return 2

        return 0
    except Stop as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("STOP: interrupted by user", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"STOP: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
