from __future__ import annotations


REQUIRED_BRIEF_SECTIONS = (
    "Goal",
    "Architecture Basis",
    "Dependencies",
    "Scope",
    "Allowed Changes",
    "Forbidden Changes",
    "Acceptance Criteria",
    "Stop Conditions",
)

BRIEF_AUTHORITY_STATEMENT = (
    "The original tracked Task remains the Source of Truth. "
    "This Worker Brief grants no authority beyond the original Task. "
    "Verification and Final Gate remain Harness-owned."
)


def _task_title(task_markdown: str) -> str:
    titles = [
        line
        for line in task_markdown.splitlines()
        if line.startswith("# ")
    ]
    if len(titles) != 1:
        raise ValueError(
            f"expected exactly one Task title; found {len(titles)}"
        )
    return titles[0]


def _required_section_bodies(task_markdown: str) -> dict[str, str]:
    lines = task_markdown.splitlines(keepends=True)
    found: dict[str, list[str]] = {
        section: [] for section in REQUIRED_BRIEF_SECTIONS
    }
    current_section: str | None = None
    current_body: list[str] = []

    def save_current_section() -> None:
        nonlocal current_section, current_body
        if current_section in found:
            found[current_section].append("".join(current_body))
        current_section = None
        current_body = []

    for line in lines:
        if line.startswith("## "):
            save_current_section()
            current_section = line[3:].strip()
            continue
        if current_section is not None:
            current_body.append(line)
    save_current_section()

    missing = [section for section, bodies in found.items() if not bodies]
    duplicated = [
        section for section, bodies in found.items() if len(bodies) != 1
    ]
    if missing:
        raise ValueError(f"missing required Worker Brief sections: {missing}")
    if duplicated:
        raise ValueError(
            f"duplicated required Worker Brief sections: {duplicated}"
        )

    return {
        section: found[section][0]
        for section in REQUIRED_BRIEF_SECTIONS
    }


def build_worker_brief(task_markdown: str) -> str:
    """Project exact tracked Task sections into the initial Worker input.

    The tracked Task remains authoritative. Missing or duplicated required
    structure raises ValueError so the Runner can fail closed before creating a
    Worker session.
    """
    title = _task_title(task_markdown)
    section_bodies = _required_section_bodies(task_markdown)
    brief_parts = [title, "", BRIEF_AUTHORITY_STATEMENT, ""]

    for section in REQUIRED_BRIEF_SECTIONS:
        brief_parts.append(f"## {section}")
        brief_parts.append(section_bodies[section].rstrip("\r\n"))
        brief_parts.append("")

    return "\n".join(brief_parts).rstrip() + "\n"
