"""Deterministic core helpers for Qwen Harness V2."""

import os
import hashlib
import re
import subprocess
import shlex
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkerRequest:
    """Backend-independent request passed from the Harness to a Worker."""

    task_text: str


@dataclass(frozen=True)
class WorkerResponse:
    """Backend-independent Worker transport result; not a Harness PASS/FAIL."""

    transport_ok: bool
    output_text: str
    error: str | None = None


@dataclass(frozen=True)
class ToolSpec:
    """Backend-neutral description of a Harness-owned tool."""

    name: str
    description: str
    input_schema: Mapping[str, object]


@dataclass(frozen=True)
class ToolRequest:
    """Backend-neutral Worker request for a Harness-owned tool."""

    call_id: str
    name: str
    arguments: Mapping[str, object]


@dataclass(frozen=True)
class ToolResult:
    """Backend-neutral result of deterministic Harness tool execution."""

    call_id: str
    ok: bool
    output: str
    error: str | None


@dataclass(frozen=True)
class WorkerStep:
    """One backend-neutral Worker interaction step; not a Harness PASS/FAIL."""

    transport_ok: bool
    output_text: str
    tool_requests: tuple[ToolRequest, ...]
    error: str | None


@dataclass(frozen=True)
class ChangeScope:
    """Allowed and forbidden repository path patterns parsed from a Task."""

    allowed: tuple[str, ...]
    forbidden: tuple[str, ...]


def parse_change_scope(markdown: str) -> ChangeScope:
    """Parse Allowed Changes and Forbidden Changes from Task Markdown."""
    # Split markdown into sections based on ## headings
    lines = markdown.splitlines()
    
    allowed_items = []
    forbidden_items = []
    
    current_section = None
    
    for line in lines:
        if line.startswith("## "):
            section_name = line[3:].strip()
            if section_name == "Allowed Changes":
                current_section = "allowed"
            elif section_name == "Forbidden Changes":
                current_section = "forbidden"
            else:
                current_section = None
        elif current_section is not None and line.startswith("- "):
            # Extract the bullet value after "- "
            bullet_value = line[2:]
            
            # Step 1: Trim outer whitespace from the remaining bullet value
            bullet_value = bullet_value.strip()
            
            # Step 2: Check if it begins and ends with one matching backtick
            if len(bullet_value) >= 2 and bullet_value.startswith("`") and bullet_value.endswith("`"):
                # Remove exactly that outer backtick pair
                bullet_value = bullet_value[1:-1]
            
            # Add to the appropriate list
            if current_section == "allowed":
                allowed_items.append(bullet_value)
            elif current_section == "forbidden":
                forbidden_items.append(bullet_value)
    
    # Check for missing sections
    if not allowed_items:
        raise ValueError("Missing 'Allowed Changes' section")
    if not forbidden_items:
        raise ValueError("Missing 'Forbidden Changes' section")
    
    return ChangeScope(
        allowed=tuple(allowed_items),
        forbidden=tuple(forbidden_items)
    )


def path_matches(path: str, pattern: str) -> bool:
    """
    Determine if a repository-relative path matches a given pattern.
    
    Normalizes both inputs by replacing backslashes with forward slashes.
    Supports exact matching and trailing /** for recursive directory matching.
    Does not support other glob syntax (e.g., *.py).
    """
    # Normalize backslashes to forward slashes
    normalized_path = path.replace("\\", "/")
    normalized_pattern = pattern.replace("\\", "/")
    
    # Check for exact match first
    if normalized_path == normalized_pattern:
        return True
    
    # Check for recursive directory pattern ending in /**
    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern[:-3]  # Remove /**
        if normalized_path.startswith(prefix + "/"):
            return True
    
    return False


def is_path_allowed(path: str, scope: ChangeScope) -> bool:
    """
    Determine if a path is allowed based on the given scope.
    
    Order of precedence:
    1. If path matches any forbidden pattern, return False.
    2. Otherwise, if path matches any allowed pattern, return True.
    3. Otherwise, return False (default deny).
    """
    # Check forbidden patterns first
    for forbidden_pattern in scope.forbidden:
        if path_matches(path, forbidden_pattern):
            return False
    
    # Check allowed patterns
    for allowed_pattern in scope.allowed:
        if path_matches(path, allowed_pattern):
            return True
    
    # Default deny
    return False


def _run_git(
    repo_root: str,
    args: tuple[str, ...],
    *,
    text: bool = True,
) -> subprocess.CompletedProcess:
    """
    Execute a Git command within the specified repository root.
    
    Args:
        repo_root: The path to the repository root (or worktree).
        args: Tuple of arguments for the git command (e.g., ("rev-parse", "--show-toplevel")).
        text: If True, decode stdout/stderr as UTF-8; if False, return raw bytes.
    
    Returns:
        A CompletedProcess instance with the result of the Git command.
    
    Raises:
        RuntimeError: If process creation fails (OSError/FileNotFoundError) or if Git returns a non-zero exit code.
    """
    # Construct the command list using subprocess defaults (no shell)
    cmd = ["git", "-C", repo_root] + list(args)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=text,
            check=False  # We will handle non-zero exit codes manually
        )
    except OSError as e:
        # Catch process creation failures (e.g., git not found, permission denied)
        raise RuntimeError(f"Failed to execute Git command: {e}") from e
    
    if result.returncode != 0:
        # Raise an error for non-zero exit codes
        raise RuntimeError(f"Git command failed with exit code {result.returncode}: {result.stderr}")
    
    return result


def _require_git_top_level(repo_root: str) -> str:
    """
    Validate and resolve the top-level path of a Git repository.
    
    Args:
        repo_root: A path that is either the actual repository root or a subdirectory within it.
    
    Returns:
        The normalized, resolved path to the Git repository's top-level directory.
    
    Raises:
        RuntimeError: If the provided path is not inside a valid Git repository (Git command fails).
        ValueError: If the provided path is a subdirectory within a valid worktree but not the root.
    """
    # Use _run_git to get the actual top-level path reported by Git
    result = _run_git(repo_root, ("rev-parse", "--show-toplevel"))
    
    git_top_level = result.stdout.strip()
    
    # Normalize both paths for comparison (handle Windows / vs \ differences)
    normalized_repo_root = os.path.normpath(repo_root)
    normalized_git_top_level = os.path.normpath(git_top_level)
    
    # Resolve to absolute paths to handle relative paths and symlinks correctly
    resolved_repo_root = os.path.realpath(normalized_repo_root)
    resolved_git_top_level = os.path.realpath(normalized_git_top_level)
    
    # Check if the provided path is exactly the repository root (or equivalent)
    if resolved_repo_root == resolved_git_top_level:
        return git_top_level
    
    # If not equal, check containment logic
    # The supplied canonical path must NOT be contained within the Git top-level
    # If it is contained, it is a subdirectory and must raise ValueError
    if resolved_repo_root.startswith(resolved_git_top_level + os.sep) or resolved_repo_root == resolved_git_top_level:
        # This case handles the scenario where repo_root is a subdirectory of the actual top level.
        # Since we already checked equality above, if we are here and they differ,
        # and repo_root starts with git_top_level (plus separator), it's a subdir.
        raise ValueError(f"Provided path '{repo_root}' is a subdirectory of the repository root '{resolved_git_top_level}', not the root itself.")
    
    # If we reach here, the provided path is outside the repository entirely
    raise RuntimeError(f"Path '{repo_root}' is not inside a valid Git repository (expected top-level: {resolved_git_top_level})")


@dataclass(frozen=True)
class GitBaseline:
    """Captured Git baseline state at a specific HEAD commit."""

    head: str


def capture_git_baseline(repo_root: str) -> GitBaseline:
    """
    Capture the current clean Git baseline for the repository root.

    Args:
        repo_root: The path to the Git repository top-level directory.

    Returns:
        A frozen GitBaseline instance containing the current HEAD commit SHA.

    Raises:
        RuntimeError: If the path is not a valid Git repository or Git commands fail.
        ValueError: If the repository is dirty (tracked changes) or untracked files exist.
    """
    # First, validate that repo_root is the actual top-level of the repository
    _require_git_top_level(repo_root)

    # Run git status --porcelain to check for any cleanliness issues
    result = _run_git(
        repo_root,
        ("status", "--porcelain")
    )

    status_output = result.stdout

    # Porcelain output is empty if and only if the repository is clean
    if status_output.strip():
        # There are tracked unstaged changes, staged changes, or untracked non-ignored files
        raise ValueError(f"Repository is not clean. Git status:\n{status_output}")

    # Capture the current HEAD commit
    head_result = _run_git(repo_root, ("rev-parse", "HEAD"))
    head_sha = head_result.stdout.strip()

    return GitBaseline(head=head_sha)


def get_changed_paths(repo_root: str, baseline: GitBaseline) -> tuple[str, ...]:
    """Return deterministic repository-relative paths changed since baseline."""
    _require_git_top_level(repo_root)

    tracked = _run_git(
        repo_root,
        ("diff", "--no-renames", "--name-only", "-z", baseline.head, "--"),
        text=False,
    )
    untracked = _run_git(
        repo_root,
        ("ls-files", "--others", "--exclude-standard", "-z"),
        text=False,
    )

    changed: set[str] = set()
    for output in (tracked.stdout, untracked.stdout):
        for raw_path in output.split(bytes([0])):
            if raw_path:
                changed.add(os.fsdecode(raw_path).replace("\\", "/"))

    return tuple(sorted(changed))

@dataclass(frozen=True)
class VerificationContract:
    """Explicit verification commands parsed from Task Markdown."""
    commands: tuple[str, ...]


def parse_verification_commands(markdown: str) -> VerificationContract:
    """Parse only explicitly marked commands from the Verification section."""
    lines = markdown.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line == "## Verification":
            start = index + 1
            break
    if start is None:
        raise ValueError("Missing Verification section")

    section = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        section.append(line)

    markers = {"Run exactly:", "Run:", "Then run:"}
    commands = []
    index = 0
    while index < len(section):
        line = section[index]
        if line not in markers:
            token = line.strip()
            if token.startswith("```") or (
                token.startswith("`") and token.endswith("`")
            ):
                raise ValueError("Unmarked verification command")
            index += 1
            continue

        index += 1
        while index < len(section) and not section[index].strip():
            index += 1
        if index >= len(section):
            raise ValueError("Verification marker has no command")

        token = section[index].strip()
        if token.startswith("```"):
            index += 1
            block = []
            while index < len(section) and not section[index].strip().startswith("```"):
                if section[index].strip():
                    block.append(section[index].strip())
                index += 1
            if index >= len(section) or len(block) != 1:
                raise ValueError("Verification fence must contain exactly one command")
            command = block[0]
            index += 1
        elif token.startswith("`") and token.endswith("`"):
            command = token[1:-1].strip()
            index += 1
        else:
            raise ValueError("Unsupported verification command format")

        if not command:
            raise ValueError("Verification command is empty")
        commands.append(command)

    if not commands:
        raise ValueError("No explicitly marked verification commands")
    return VerificationContract(commands=tuple(commands))

@dataclass(frozen=True)
class VerificationCommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


def run_verification_commands(contract: VerificationContract, cwd: str) -> tuple[VerificationCommandResult, ...]:
    if not contract.commands:
        raise ValueError("VerificationContract must contain at least one command")
    prepared = []
    for command in contract.commands:
        if not command.strip():
            raise ValueError("Empty command is invalid")
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            raise ValueError("Malformed quoting in command")
        if any(token in ("&&", "||", "|", ";") for token in tokens):
            raise ValueError("Unsupported shell control operator in command")
        prepared.append((command, tokens))
    results = []
    for command, tokens in prepared:
        try:
            result = subprocess.run(
                tokens,
                cwd=cwd,
                shell=False,
                capture_output=True,
                text=True,
                check=False
            )
            results.append(VerificationCommandResult(command, result.returncode, result.stdout, result.stderr))
        except OSError as e:
            raise RuntimeError(f"Failed to start process: {e}") from e
    return tuple(results)


@dataclass(frozen=True)
class ExactContentResult:
    path: str
    expected_content: str
    exists: bool
    matches: bool


@dataclass(frozen=True)
class Sha256Result:
    path: str
    expected_sha256: str
    actual_sha256: str | None
    exists: bool
    matches: bool


def _resolve_invariant_target(repo_root: str, path: str) -> Path:
    relative = Path(path)
    if relative.is_absolute() or relative.drive:
        raise ValueError("Invariant path must be Repository-relative")
    try:
        root = Path(repo_root).resolve()
        target = (root / relative).resolve()
    except OSError as exc:
        raise RuntimeError(f"Failed to resolve invariant path: {exc}") from exc
    if not target.is_relative_to(root):
        raise ValueError("Invariant path escapes Repository root")
    return target


def check_exact_content(repo_root: str, path: str, expected_content: str) -> ExactContentResult:
    target = _resolve_invariant_target(repo_root, path)
    if not target.exists():
        return ExactContentResult(path, expected_content, False, False)
    if not target.is_file():
        raise ValueError("Invariant target must be a regular file")
    try:
        actual = target.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Failed to read invariant target: {exc}") from exc
    return ExactContentResult(path, expected_content, True, actual == expected_content.encode("utf-8"))


def check_sha256(repo_root: str, path: str, expected_sha256: str) -> Sha256Result:
    if re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256) is None:
        raise ValueError("Expected SHA-256 must contain exactly 64 hexadecimal characters")
    target = _resolve_invariant_target(repo_root, path)
    if not target.exists():
        return Sha256Result(path, expected_sha256, None, False, False)
    if not target.is_file():
        raise ValueError("Invariant target must be a regular file")
    try:
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeError(f"Failed to read or hash invariant target: {exc}") from exc
    return Sha256Result(path, expected_sha256, actual, True, actual.lower() == expected_sha256.lower())


@dataclass(frozen=True)
class PathScopeEvidence:
    path: str
    allowed: bool


@dataclass(frozen=True)
class HarnessEvidence:
    scope: ChangeScope
    baseline: GitBaseline
    changed_paths: tuple[str, ...]
    path_scope_results: tuple[PathScopeEvidence, ...]
    verification_results: tuple[VerificationCommandResult, ...]
    exact_content_results: tuple[ExactContentResult, ...]
    sha256_results: tuple[Sha256Result, ...]


def assemble_evidence(
    scope: ChangeScope,
    baseline: GitBaseline,
    changed_paths: tuple[str, ...],
    verification_results: tuple[VerificationCommandResult, ...] = (),
    exact_content_results: tuple[ExactContentResult, ...] = (),
    sha256_results: tuple[Sha256Result, ...] = (),
) -> HarnessEvidence:
    path_scope_results = tuple(
        PathScopeEvidence(path, is_path_allowed(path, scope))
        for path in changed_paths
    )
    return HarnessEvidence(
        scope=scope,
        baseline=baseline,
        changed_paths=changed_paths,
        path_scope_results=path_scope_results,
        verification_results=verification_results,
        exact_content_results=exact_content_results,
        sha256_results=sha256_results,
    )


@dataclass(frozen=True)
class FinalGateResult:
    passed: bool
    failures: tuple[str, ...]


def evaluate_final_gate(evidence: HarnessEvidence) -> FinalGateResult:
    recomputed_scope_results = tuple(
        PathScopeEvidence(path, is_path_allowed(path, evidence.scope))
        for path in evidence.changed_paths
    )

    failures = []

    evidence_inconsistent = recomputed_scope_results != evidence.path_scope_results
    evidence_inconsistent = evidence_inconsistent or any(
        result.matches and not result.exists
        for result in evidence.exact_content_results
    )
    evidence_inconsistent = evidence_inconsistent or any(
        result.matches
        and (
            not result.exists
            or result.actual_sha256 is None
            or result.actual_sha256.lower() != result.expected_sha256.lower()
        )
        for result in evidence.sha256_results
    )
    if evidence_inconsistent:
        failures.append("evidence_consistency")

    if any(not result.allowed for result in recomputed_scope_results):
        failures.append("scope")
    if any(result.exit_code != 0 for result in evidence.verification_results):
        failures.append("verification")
    if any(not result.matches for result in evidence.exact_content_results):
        failures.append("exact_content")
    if any(not result.matches for result in evidence.sha256_results):
        failures.append("sha256")

    return FinalGateResult(passed=not failures, failures=tuple(failures))
