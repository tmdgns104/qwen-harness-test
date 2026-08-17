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