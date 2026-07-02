"""Deterministic tool for validating study guide Markdown structure."""

REQUIRED_SECTIONS = [
    "Topic",
    "Simple Explanation",
    "Key Concepts",
    "Example",
    "Practice Exercise",
    "Common Mistakes",
    "Review Comments",
    "Final Summary",
]


def validate_required_sections(markdown: str) -> dict:
    """Check that markdown contains a heading for each required section.

    Returns a dict with 'is_valid' (bool) and 'missing_sections' (list[str]).
    Matching is done against Markdown headings (lines starting with '#').
    """
    heading_lines = []
    in_code_block = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("#"):
            heading_lines.append(stripped.lstrip("#").strip().lower())

    missing = [
        section
        for section in REQUIRED_SECTIONS
        if not any(heading.startswith(section.lower()) for heading in heading_lines)
    ]

    return {
        "is_valid": len(missing) == 0,
        "missing_sections": missing,
    }


if __name__ == "__main__":
    sample = "# Topic\n\n## Simple Explanation\ntext\n"
    print(validate_required_sections(sample))
