"""Deterministic core helpers for Qwen Harness V2."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChangeScope:
    """Allowed and forbidden repository path patterns parsed from a Task."""

    allowed: tuple[str, ...]
    forbidden: tuple[str, ...]


def parse_change_scope(markdown: str) -> ChangeScope:
    """Parse Allowed Changes and Forbidden Changes from Task Markdown."""
    raise NotImplementedError("HC-001")
