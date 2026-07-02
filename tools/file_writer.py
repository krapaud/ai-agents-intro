"""Deterministic tool for saving Markdown content to disk."""

from pathlib import Path


def save_markdown_file(file_path: str, content: str) -> str:
    """Write Markdown content to file_path, creating parent dirs as needed.

    Returns a success message with the saved path, or an error message
    if the write fails.
    """
    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return f"Error: could not write file '{file_path}': {exc}"

    return f"Saved Markdown file to {path.resolve()}"


if __name__ == "__main__":
    result = save_markdown_file("output/_test.md", "# Test\n\nHello world.\n")
    print(result)
