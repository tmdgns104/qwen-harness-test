"""Small text helpers used only by the Qwen Harness testbed."""


import re


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace runs to one space and trim outer whitespace."""
    if not text:
        return ''
    processed = re.sub(r'\s+', ' ', text)
    return processed.strip()


def truncate_with_ellipsis(text: str, max_length: int) -> str:
    """Truncate text to max_length, using ... when truncation is needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def slugify_heading(text: str) -> str:
    """Normalize a heading for use in a simple section identifier."""
    return normalize_whitespace(text).replace(' ', '-').lower()
