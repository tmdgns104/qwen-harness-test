"""Small text helpers used only by the Qwen Harness testbed."""


import re

def normalize_whitespace(text: str) -> str:
    """Collapse whitespace runs to one space and trim outer whitespace."""
    if not text:
        return ''
    processed = re.sub(r'\s+', ' ', text)
    return processed.strip()
