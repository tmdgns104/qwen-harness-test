"""Deterministic core helpers for Qwen Harness V2."""

import os
import re
import subprocess
from dataclasses import dataclass


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