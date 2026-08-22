from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

REMOTE = "origin"
REMOTE_BRANCH = "main"
LOCAL_BRANCH = "master"
CONFIG_DIR = Path.home() / ".qhops"
CONFIG_FILE = CONFIG_DIR / "config.json"

GATE_TASK_ID = "QH-V2-GATE-001"
GATE_MANIFEST_VERSION = 1
GATE_POLICY = "HUMAN ONE-TIME AUTONOMOUS QUEUE GATE"
GATE_EVIDENCE_PATH = "docs/AUTONOMOUS_QUEUE_GATE_EVIDENCE.md"
MANIFEST_REL_PATH = "ops/qhops/autonomous_queue_manifest.json"

APPROVED_STATUS = "APPROVED - READY FOR CONTRACT BASELINE"
COMPLETE_STATUS = "COMPLETE - VERIFIED"
ACTIVE_MARKER = " - ACTIVE"
COMPLETE_MARKER = " - COMPLETE - VERIFIED"

COVERED_QUEUE = (
    "QH-V2-HARD-006",
    "QH-V2-HARD-007",
    "QH-V2-OPS-001",
    "QH-V2-OPS-002",
    "QH-V2-OPS-003",
    "QH-V2-OPS-004",
    "QH-V2-OPS-005",
    "QH-V2-OPS-006",
    "QH-V2-M2-SPEC-001",
)

IMMUTABLE_CONTRACT_SECTIONS = (
    "Goal",
    "Architecture Basis",
    "Dependencies",
    "Scope",
    "Allowed Changes",
    "Forbidden Changes",
    "Acceptance Criteria",
    "Verification",
    "Evidence Requirements",
    "Stop Conditions",
    "Next Task",
)

AUTHORITY_SOURCE_PATHS = (
    "BACKLOG.md",
    "REQUIREMENTS.md",
    "DECISIONS.md",
)

DELEGATED_OPERATIONS = (
    "start exact next pre-approved covered Task",
    "create Task implementation commit",
    "invoke authoritative qh close at exact implementation HEAD",
    "create separate lifecycle commit after Final Gate PASS",
    "advance only to exact manifest successor after revalidation",
    "push HEAD:main to origin using fast-forward-only behavior",
)

FORBIDDEN_OPERATIONS = (
    "create Task during autonomous queue execution",
    "edit Task immutable contract authority",
    "insert remove or reorder covered queue",
    "edit Architecture or Requirements during covered execution",
    "expand Task scope or bypass Forbidden precedence",
    "force push rebase reset history rewrite or destructive recovery",
    "bypass Verification Evidence Diff Check or Final Gate",
    "expand Qwen Worker authority",
    "continue past HUMAN ARCHITECTURE GATE",
)


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

    qh_path = root / "tools" / "qh.py"
    if not qh_path.is_file():
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
    if explicit:
        return validate_repo(Path(explicit))

    cwd_root = git_root_from(Path.cwd())
    if cwd_root is not None and (cwd_root / "tools" / "qh.py").is_file():
        return cwd_root

    env_repo = os.environ.get("QH_REPO")
    if env_repo:
        return validate_repo(Path(env_repo))

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


def current_task_line(root: Path) -> str:
    status_file = root / "STATUS.md"
    if not status_file.is_file():
        raise Stop(f"STATUS.md not found: {root}")

    text = status_file.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.startswith("Current Task:")]
    if len(lines) != 1:
        raise Stop(f"expected exactly one Current Task line; found {len(lines)}")
    return lines[0]


def current_task_id(root: Path) -> str:
    line = current_task_line(root)
    match = re.match(r"Current Task:\s+(\S+)", line)
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


def print_verification_result(label: str, command: str, result: object, duration: float) -> None:
    print(f"Focused {label} command: {command}")
    print(f"Exit Code: {result.exit_code}")
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(
            result.stderr,
            file=sys.stderr,
            end="" if result.stderr.endswith("\n") else "\n",
        )
    print(f"Focused {label} Duration: {duration:.3f}s")


def qh(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(
        [sys.executable, str(root / "tools" / "qh.py"), *args],
        root,
        check=check,
    )


_H2_RE = re.compile(r"(?m)^## ([^\r\n]+)\r?$")


def _normalized_markdown(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _h2_sections(text: str) -> dict[str, list[str]]:
    normalized = _normalized_markdown(text)
    matches = list(_H2_RE.finditer(normalized))
    sections: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        name = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        chunk = normalized[match.start():end]
        sections.setdefault(name, []).append(chunk)
    return sections


def _single_h2_section(text: str, name: str) -> str:
    sections = _h2_sections(text).get(name, [])
    if len(sections) != 1:
        raise Stop(f"Task must contain exactly one ## {name} section")
    return sections[0]


def task_status_from_text(text: str) -> str:
    section = _single_h2_section(text, "Status")
    lines = section.splitlines()[1:]
    values = [line.strip() for line in lines if line.strip()]
    if len(values) != 1:
        raise Stop("Task Status section must contain exactly one non-empty status value")
    return values[0]


def task_status(path: Path) -> str:
    return task_status_from_text(path.read_text(encoding="utf-8"))


def replace_task_status(text: str, old: str, new: str) -> str:
    normalized = _normalized_markdown(text)
    matches = [m for m in _H2_RE.finditer(normalized) if m.group(1).strip() == "Status"]
    if len(matches) != 1:
        raise Stop("target task must contain exactly one ## Status section")

    match = matches[0]
    next_match = next((m for m in _H2_RE.finditer(normalized, match.end()) if m.start() > match.start()), None)
    end = next_match.start() if next_match else len(normalized)
    section = normalized[match.start():end]
    lines = section.splitlines()
    value_indexes = [i for i, line in enumerate(lines[1:], start=1) if line.strip()]
    if len(value_indexes) != 1:
        raise Stop("target task status value must be exactly one non-empty line")
    value_index = value_indexes[0]
    if lines[value_index].strip() != old:
        raise Stop(f"target task status is not {old}: {lines[value_index].strip()}")
    prefix = lines[value_index][: len(lines[value_index]) - len(lines[value_index].lstrip())]
    lines[value_index] = prefix + new
    replacement = "\n".join(lines)
    if section.endswith("\n"):
        replacement += "\n"
    return normalized[:match.start()] + replacement + normalized[end:]


def immutable_contract_hash(text: str) -> str:
    sections = _h2_sections(text)
    canonical: list[str] = []
    for name in IMMUTABLE_CONTRACT_SECTIONS:
        chunks = sections.get(name, [])
        if len(chunks) != 1:
            raise Stop(f"Task must contain exactly one immutable ## {name} section")
        chunk = chunks[0]
        canonical.append(chunk.rstrip("\n") + "\n")
    payload = "".join(canonical).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def manifest_path(root: Path) -> Path:
    return root / Path(MANIFEST_REL_PATH)


def _canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _manifest_integrity(payload_without_integrity: dict) -> str:
    return hashlib.sha256(_canonical_json_bytes(payload_without_integrity)).hexdigest()


def _with_manifest_integrity(payload: dict) -> dict:
    result = dict(payload)
    result["manifest_sha256"] = _manifest_integrity(result)
    return result


def _validate_manifest_integrity(data: dict) -> None:
    recorded = data.get("manifest_sha256")
    if not isinstance(recorded, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded):
        raise Stop("manifest integrity field is missing or malformed")
    payload = dict(data)
    payload.pop("manifest_sha256", None)
    actual = _manifest_integrity(payload)
    if actual != recorded:
        raise Stop("manifest integrity mismatch")


def _git_value(root: Path, *args: str) -> str:
    return git(root, *args).stdout.strip()


def _git_blob_at(root: Path, commit: str, path: str) -> str:
    value = _git_value(root, "rev-parse", f"{commit}:{path}")
    if not re.fullmatch(r"[0-9a-f]{40,64}", value):
        raise Stop(f"could not resolve Git blob identity for {path}")
    return value


def _worktree_blob(root: Path, path: str) -> str:
    target = root / path
    if not target.is_file():
        raise Stop(f"required Gate file missing: {path}")
    value = _git_value(root, "hash-object", f"--path={path}", path)
    if not re.fullmatch(r"[0-9a-f]{40,64}", value):
        raise Stop(f"could not hash working-tree file: {path}")
    return value


def _git_blob_text(root: Path, blob_sha: str) -> str:
    result = git(root, "cat-file", "blob", blob_sha)
    return result.stdout


def _current_branch(root: Path) -> str:
    return _git_value(root, "rev-parse", "--abbrev-ref", "HEAD")


def _remote_url(root: Path) -> str:
    return _git_value(root, "remote", "get-url", REMOTE)


def _normalize_remote_identity(url: str) -> str:
    value = url.strip()
    if not value:
        raise Stop("origin remote URL is empty")

    if "://" in value:
        parts = urlsplit(value)
        if parts.username is not None or parts.password is not None:
            raise Stop("credential-bearing remote URL cannot be stored in Gate manifest")
        if not parts.hostname or not parts.path:
            raise Stop("origin remote URL is malformed")
        host = parts.hostname.lower()
        port = f":{parts.port}" if parts.port else ""
        return f"{host}{port}{parts.path.rstrip('/')}"

    match = re.fullmatch(r"(?:[^@/:]+@)?([^:]+):(.+)", value)
    if match:
        host = match.group(1).lower()
        path = "/" + match.group(2).lstrip("/")
        return f"{host}{path.rstrip('/')}"

    normalized = value.replace("\\", "/").rstrip("/")
    if not normalized:
        raise Stop("origin remote identity is malformed")
    return normalized


def _queue_from_backlog(text: str) -> tuple[str, ...]:
    found: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) < 2:
            continue
        candidate = columns[1]
        if candidate in COVERED_QUEUE:
            found.append(candidate)
    return tuple(found)


def _require_exact_backlog_queue(root: Path) -> None:
    backlog = (root / "BACKLOG.md").read_text(encoding="utf-8")
    found = _queue_from_backlog(backlog)
    if found != COVERED_QUEUE:
        raise Stop(f"BACKLOG covered queue mismatch: {found}")


def _task_manifest_entry(root: Path, commit: str, task_id: str) -> dict:
    rel = f"tasks/{task_id}.md"
    path = root / rel
    text = path.read_text(encoding="utf-8")
    status = task_status_from_text(text)
    if status != APPROVED_STATUS:
        raise Stop(f"{task_id} is not pre-approved: {status}")
    return {
        "path": rel,
        "prestart_blob": _git_blob_at(root, commit, rel),
        "immutable_sha256": immutable_contract_hash(text),
    }


def _manifest_base_payload(root: Path, gate_commit: str) -> dict:
    branch = _current_branch(root)
    if branch != LOCAL_BRANCH:
        raise Stop(f"Gate seal requires branch {LOCAL_BRANCH}; found {branch}")

    remote_identity = _normalize_remote_identity(_remote_url(root))
    _require_exact_backlog_queue(root)

    source_blobs = {
        path: _git_blob_at(root, gate_commit, path)
        for path in AUTHORITY_SOURCE_PATHS
    }

    evidence = root / GATE_EVIDENCE_PATH
    if not evidence.is_file():
        raise Stop(f"Human Gate evidence file missing: {GATE_EVIDENCE_PATH}")

    tasks = {
        task_id: _task_manifest_entry(root, gate_commit, task_id)
        for task_id in COVERED_QUEUE
    }

    return {
        "version": GATE_MANIFEST_VERSION,
        "policy": GATE_POLICY,
        "gate_change_set_commit": gate_commit,
        "authority_source_blobs": source_blobs,
        "human_gate_evidence": {
            "path": GATE_EVIDENCE_PATH,
            "blob": _git_blob_at(root, gate_commit, GATE_EVIDENCE_PATH),
        },
        "covered_queue": list(COVERED_QUEUE),
        "tasks": tasks,
        "git": {
            "local_branch": LOCAL_BRANCH,
            "remote": REMOTE,
            "remote_identity": remote_identity,
            "remote_branch": REMOTE_BRANCH,
            "push_refspec": f"HEAD:{REMOTE_BRANCH}",
            "fast_forward_only": True,
        },
        "delegated_operations": list(DELEGATED_OPERATIONS),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "validity": {
            "revoked": False,
            "valid_until": "first of revocation, manifest mismatch, policy invalidation, or covered queue completion at HUMAN ARCHITECTURE GATE",
            "terminal_gate": "HUMAN ARCHITECTURE GATE",
        },
        "audit": {
            "authoritative_resume": "Repository Git state plus exact manifest",
            "supplemental_local_audit": "%USERPROFILE%\\.qhops\\audit\\",
            "chat_or_session_memory_authority": False,
        },
    }


def _validate_manifest_schema(data: dict) -> None:
    if not isinstance(data, dict):
        raise Stop("manifest root must be a JSON object")
    _validate_manifest_integrity(data)

    if data.get("version") != GATE_MANIFEST_VERSION:
        raise Stop("manifest version mismatch")
    if data.get("policy") != GATE_POLICY:
        raise Stop("manifest policy mismatch")
    if tuple(data.get("covered_queue", ())) != COVERED_QUEUE:
        raise Stop("manifest covered queue mismatch")
    if tuple(data.get("delegated_operations", ())) != DELEGATED_OPERATIONS:
        raise Stop("manifest delegated operations mismatch")
    if tuple(data.get("forbidden_operations", ())) != FORBIDDEN_OPERATIONS:
        raise Stop("manifest forbidden operations mismatch")

    validity = data.get("validity")
    if not isinstance(validity, dict):
        raise Stop("manifest validity block missing")
    if validity.get("revoked") is not False:
        raise Stop("Gate approval is revoked")
    if validity.get("terminal_gate") != "HUMAN ARCHITECTURE GATE":
        raise Stop("manifest terminal Gate mismatch")

    git_policy = data.get("git")
    expected_git = {
        "local_branch": LOCAL_BRANCH,
        "remote": REMOTE,
        "remote_branch": REMOTE_BRANCH,
        "push_refspec": f"HEAD:{REMOTE_BRANCH}",
        "fast_forward_only": True,
    }
    if not isinstance(git_policy, dict):
        raise Stop("manifest git policy missing")
    for key, expected in expected_git.items():
        if git_policy.get(key) != expected:
            raise Stop(f"manifest git policy mismatch: {key}")
    if not isinstance(git_policy.get("remote_identity"), str) or not git_policy["remote_identity"]:
        raise Stop("manifest remote identity missing")

    gate_commit = data.get("gate_change_set_commit")
    if not isinstance(gate_commit, str) or not re.fullmatch(r"[0-9a-f]{40,64}", gate_commit):
        raise Stop("manifest gate_change_set_commit malformed")

    sources = data.get("authority_source_blobs")
    if not isinstance(sources, dict) or set(sources) != set(AUTHORITY_SOURCE_PATHS):
        raise Stop("manifest authority source set mismatch")
    for path in AUTHORITY_SOURCE_PATHS:
        if not re.fullmatch(r"[0-9a-f]{40,64}", str(sources.get(path, ""))):
            raise Stop(f"manifest authority blob malformed: {path}")

    evidence = data.get("human_gate_evidence")
    if not isinstance(evidence, dict) or evidence.get("path") != GATE_EVIDENCE_PATH:
        raise Stop("manifest Human Gate evidence mismatch")
    if not re.fullmatch(r"[0-9a-f]{40,64}", str(evidence.get("blob", ""))):
        raise Stop("manifest Human Gate evidence blob malformed")

    tasks = data.get("tasks")
    if not isinstance(tasks, dict) or tuple(tasks.keys()) != COVERED_QUEUE:
        raise Stop("manifest task entry order/set mismatch")
    for task_id in COVERED_QUEUE:
        entry = tasks.get(task_id)
        expected_path = f"tasks/{task_id}.md"
        if not isinstance(entry, dict) or entry.get("path") != expected_path:
            raise Stop(f"manifest task path mismatch: {task_id}")
        if not re.fullmatch(r"[0-9a-f]{40,64}", str(entry.get("prestart_blob", ""))):
            raise Stop(f"manifest task blob malformed: {task_id}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("immutable_sha256", ""))):
            raise Stop(f"manifest immutable hash malformed: {task_id}")


def load_manifest(root: Path) -> dict:
    path = manifest_path(root)
    if not path.is_file():
        raise Stop(f"Gate manifest not found: {MANIFEST_REL_PATH}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Stop(f"invalid Gate manifest: {exc}") from exc
    _validate_manifest_schema(data)
    return data


def _queue_progress(root: Path, data: dict, *, allow_completed_gate: bool) -> dict:
    statuses: list[str] = []
    for task_id in COVERED_QUEUE:
        rel = data["tasks"][task_id]["path"]
        text = (root / rel).read_text(encoding="utf-8")
        immutable = immutable_contract_hash(text)
        if immutable != data["tasks"][task_id]["immutable_sha256"]:
            raise Stop(f"immutable Task contract mismatch: {task_id}")

        status = task_status_from_text(text)
        statuses.append(status)
        if status == APPROVED_STATUS:
            current_blob = _worktree_blob(root, rel)
            if current_blob != data["tasks"][task_id]["prestart_blob"]:
                raise Stop(f"pre-start whole-file identity mismatch: {task_id}")
        elif status == COMPLETE_STATUS:
            prestart_text = _git_blob_text(root, data["tasks"][task_id]["prestart_blob"])
            expected_complete = replace_task_status(
                prestart_text,
                APPROVED_STATUS,
                COMPLETE_STATUS,
            )
            if _normalized_markdown(text) != _normalized_markdown(expected_complete):
                raise Stop(f"completed Task changed outside Status lifecycle value: {task_id}")
        else:
            raise Stop(f"covered Task has invalid manifest lifecycle status: {task_id}: {status}")

    seen_pending = False
    completed_count = 0
    for task_id, status in zip(COVERED_QUEUE, statuses):
        if status == COMPLETE_STATUS:
            if seen_pending:
                raise Stop(f"covered queue completion is not a prefix: {task_id}")
            completed_count += 1
        else:
            seen_pending = True

    if completed_count == len(COVERED_QUEUE):
        if not allow_completed_gate:
            raise Stop("Gate validity ended at HUMAN ARCHITECTURE GATE")
        next_task = None
    else:
        next_task = COVERED_QUEUE[completed_count]

    line = current_task_line(root)
    current_id = current_task_id(root)

    if completed_count == 0 and current_id == GATE_TASK_ID:
        if ACTIVE_MARKER not in line and COMPLETE_MARKER not in line:
            raise Stop("GATE-001 lifecycle is neither ACTIVE nor COMPLETE - VERIFIED")
    elif next_task is not None and current_id == next_task:
        if ACTIVE_MARKER not in line:
            raise Stop(f"next covered Task is current but not ACTIVE: {next_task}")
    elif completed_count > 0 and current_id == COVERED_QUEUE[completed_count - 1]:
        if COMPLETE_MARKER not in line:
            raise Stop("last covered Task lifecycle is not COMPLETE - VERIFIED")
    elif next_task is None and current_id == COVERED_QUEUE[-1]:
        if COMPLETE_MARKER not in line:
            raise Stop("terminal covered Task lifecycle is not COMPLETE - VERIFIED")
    else:
        raise Stop(
            f"STATUS lifecycle does not match manifest queue progress: current={current_id}, "
            f"completed={completed_count}, next={next_task}"
        )

    return {
        "completed_count": completed_count,
        "next_task": next_task,
        "current_task": current_id,
        "current_line": line,
    }


def validate_gate_state(
    root: Path,
    *,
    require_clean_state: bool = True,
    allow_completed_gate: bool = False,
) -> dict:
    if require_clean_state:
        require_clean(root)

    data = load_manifest(root)

    branch = _current_branch(root)
    if branch != data["git"]["local_branch"]:
        raise Stop(f"wrong branch for Gate: {branch}")

    remote_identity = _normalize_remote_identity(_remote_url(root))
    if remote_identity != data["git"]["remote_identity"]:
        raise Stop("origin remote identity mismatch")

    gate_commit = data["gate_change_set_commit"]
    exists = git(root, "cat-file", "-e", f"{gate_commit}^{{commit}}", check=False)
    if exists.returncode != 0:
        raise Stop("Gate Change Set commit is unavailable")
    ancestor = git(root, "merge-base", "--is-ancestor", gate_commit, "HEAD", check=False)
    if ancestor.returncode != 0:
        raise Stop("current HEAD is not descended from Gate Change Set commit")

    _require_exact_backlog_queue(root)

    for path, expected_blob in data["authority_source_blobs"].items():
        if _worktree_blob(root, path) != expected_blob:
            raise Stop(f"authority source changed after Gate seal: {path}")

    evidence = data["human_gate_evidence"]
    if _worktree_blob(root, evidence["path"]) != evidence["blob"]:
        raise Stop("Human Gate evidence changed after seal")

    progress = _queue_progress(root, data, allow_completed_gate=allow_completed_gate)
    return {
        "manifest": data,
        **progress,
    }


def cmd_gate_seal(root: Path) -> None:
    require_clean(root)
    if current_task_id(root) != GATE_TASK_ID or ACTIVE_MARKER not in current_task_line(root):
        raise Stop("gate-seal is only valid while QH-V2-GATE-001 is ACTIVE")

    path = manifest_path(root)
    if path.exists():
        raise Stop(f"refusing to overwrite existing manifest: {MANIFEST_REL_PATH}")

    gate_commit = _git_value(root, "rev-parse", "HEAD")
    payload = _manifest_base_payload(root, gate_commit)
    manifest = _with_manifest_integrity(payload)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Gate Change Set Commit: {gate_commit}")
    print(f"Manifest SHA-256: {manifest['manifest_sha256']}")
    print(f"Sealed manifest: {MANIFEST_REL_PATH}")
    print("No Task was started and nothing was pushed.")


def cmd_gate_check(root: Path) -> None:
    state = validate_gate_state(root)
    next_task = state["next_task"]
    print("Gate Check: PASS")
    print(f"Completed Covered Tasks: {state['completed_count']}/{len(COVERED_QUEUE)}")
    print(f"Next Covered Task: {next_task or 'HUMAN ARCHITECTURE GATE'}")


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
    value = task_status_from_text(text)
    if value == APPROVED_STATUS:
        return False
    if value != "PLANNED":
        raise Stop(f"target task is not PLANNED/APPROVED: {value}")

    updated = replace_task_status(text, "PLANNED", APPROVED_STATUS)
    path.write_text(updated, encoding="utf-8", newline="\n")
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

    started = time.perf_counter()
    command, result = first_verification(root)
    duration = time.perf_counter() - started
    print_verification_result("RED", command, result, duration)

    if result.exit_code == 0:
        raise Stop("focused RED unexpectedly passed; stop and review")

    print("RED confirmed. Do not push yet.")


def cmd_green(root: Path, sha: str) -> None:
    require_clean(root)
    git(root, "fetch", REMOTE)
    git(root, "cherry-pick", sha)
    require_clean(root)

    started = time.perf_counter()
    command, result = first_verification(root)
    duration = time.perf_counter() - started
    print_verification_result("GREEN", command, result, duration)

    if result.exit_code != 0:
        raise Stop("focused GREEN failed; stop before final close")

    require_clean(root)
    git(root, "diff", "--check")
    print("Focused GREEN verified locally. Do not push yet.")


def cmd_verify(root: Path) -> None:
    print("== Task Verification ==")
    qh(root, "verify")
    print("== diff check ==")
    git(root, "diff", "--check")
    print("Verification commands passed.")


def _commit_impl(root: Path) -> None:
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

    started = time.perf_counter()
    command, result = first_verification(root)
    duration = time.perf_counter() - started
    print_verification_result("GREEN", command, result, duration)
    if result.exit_code != 0:
        raise Stop("focused GREEN failed; implementation not committed")

    after = changed_paths(root)
    if any(path in lifecycle for path in after):
        raise Stop(f"Focused Verification changed lifecycle files: {after}")

    bad = [path for path in after if not is_path_allowed(path, scope)]
    if bad:
        raise Stop(f"post-Verification paths outside Task scope: {bad}")

    if not after:
        raise Stop("no changes remain after focused Verification")

    git(root, "diff", "--check")
    for path in after:
        git(root, "add", "--", path)

    git(root, "commit", "-m", f"implement {task_id}")
    require_clean(root)
    print(f"Implementation committed locally: {task_id}")
    print("Authoritative full Verification and push are deferred to finish.")


def cmd_commit_impl(root: Path) -> None:
    _commit_impl(root)


def _finish_current_task(root: Path, *, push: bool) -> tuple[str, str]:
    finish_started = time.perf_counter()
    require_clean(root)

    task_id = current_task_id(root)
    task_path = current_task_path(root)
    task_rel = task_path.relative_to(root).as_posix()
    head = git(root, "rev-parse", "HEAD").stdout.strip()

    print(f"== authoritative close {task_id} @ {head} ==")
    close_started = time.perf_counter()
    qh(root, "close", head)
    close_duration = time.perf_counter() - close_started
    print(f"Authoritative Close Duration: {close_duration:.3f}s")
    print("Authoritative Full Verification Count: 1")

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
    if push:
        safe_push(root)
    finish_duration = time.perf_counter() - finish_started
    print(f"Finish Total Duration: {finish_duration:.3f}s")
    return task_id, head


def cmd_finish(root: Path) -> None:
    task_id, _ = _finish_current_task(root, push=True)
    print(f"COMPLETE - VERIFIED and pushed: {task_id}")


def cmd_supervisor_start(root: Path) -> None:
    state = validate_gate_state(root, require_clean_state=True)
    next_task = state["next_task"]
    if next_task is None:
        raise Stop("HUMAN ARCHITECTURE GATE reached; no successor may be started")

    if current_task_id(root) == GATE_TASK_ID and ACTIVE_MARKER in current_task_line(root):
        raise Stop("QH-V2-GATE-001 must be COMPLETE - VERIFIED before Supervisor start")

    target = root / "tasks" / f"{next_task}.md"
    if task_status(target) != APPROVED_STATUS:
        raise Stop(f"next manifest Task is not pre-approved: {next_task}")

    print(f"== manifest-guarded supervisor start: {next_task} ==")
    qh(root, "start", next_task)
    paths = changed_paths(root)
    if paths != ("STATUS.md",):
        raise Stop(f"qh start changed unexpected paths: {paths}")

    git(root, "add", "STATUS.md")
    git(root, "commit", "-m", f"start {next_task} via sealed queue")
    require_clean(root)
    post = validate_gate_state(root, require_clean_state=True)
    if post["current_task"] != next_task:
        raise Stop("post-start manifest lifecycle mismatch")
    print(f"Supervisor ACTIVE locally: {next_task}")
    print("No push occurred; final push is deferred to supervisor-finish.")


def cmd_supervisor_commit_impl(root: Path) -> None:
    state = validate_gate_state(root, require_clean_state=False)
    current = current_task_id(root)
    if current not in COVERED_QUEUE or ACTIVE_MARKER not in current_task_line(root):
        raise Stop("supervisor-commit-impl requires one covered ACTIVE Task")
    if state["next_task"] != current:
        raise Stop("current ACTIVE Task is not the exact next manifest Task")

    _commit_impl(root)
    validate_gate_state(root, require_clean_state=True)
    print("Manifest revalidation after implementation commit: PASS")


def cmd_supervisor_finish(root: Path) -> None:
    state = validate_gate_state(root, require_clean_state=True)
    current = current_task_id(root)
    if current not in COVERED_QUEUE or ACTIVE_MARKER not in current_task_line(root):
        raise Stop("supervisor-finish requires one covered ACTIVE Task")
    if state["next_task"] != current:
        raise Stop("current ACTIVE Task is not the exact next manifest Task")

    task_id, _ = _finish_current_task(root, push=False)
    post = validate_gate_state(
        root,
        require_clean_state=True,
        allow_completed_gate=True,
    )
    safe_push(root)

    if post["next_task"] is None:
        print(f"COMPLETE - VERIFIED and pushed: {task_id}")
        print("STOP: HUMAN ARCHITECTURE GATE reached; no automatic successor")
        return

    print(f"COMPLETE - VERIFIED and pushed: {task_id}")
    print(f"Next manifest Task eligible after revalidation: {post['next_task']}")


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
        "Human/operator commands:\n"
        "  qhops status\n"
        "  qhops config\n"
        "  qhops activate <TASK-ID>\n"
        "  qhops red <RED-COMMIT-SHA>\n"
        "  qhops green <IMPLEMENTATION-COMMIT-SHA>\n"
        "  qhops verify\n"
        "  qhops commit-impl\n"
        "  qhops finish\n"
        "\n"
        "Sealed autonomous-queue commands:\n"
        "  qhops gate-seal\n"
        "  qhops gate-check\n"
        "  qhops supervisor-start\n"
        "  qhops supervisor-commit-impl\n"
        "  qhops supervisor-finish\n"
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
        elif command == "gate-seal" and not rest:
            cmd_gate_seal(root)
        elif command == "gate-check" and not rest:
            cmd_gate_check(root)
        elif command == "supervisor-start" and not rest:
            cmd_supervisor_start(root)
        elif command == "supervisor-commit-impl" and not rest:
            cmd_supervisor_commit_impl(root)
        elif command == "supervisor-finish" and not rest:
            cmd_supervisor_finish(root)
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
