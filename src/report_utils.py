"""Small report helpers used only by the Qwen Harness testbed."""


from text_utils import slugify_heading


def build_section_anchor(title: str, prefix: str) -> str:
    """Build a prefixed section anchor from a heading."""
    return f"{prefix}-{title}"
