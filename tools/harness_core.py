"""Deterministic core helpers for Qwen Harness V2."""

import re
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