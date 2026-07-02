"""AI Study Guide Generator - sequential multi-agent workflow entry point."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agents.explainer_agent import run_explainer_agent
from agents.practice_designer_agent import run_practice_designer_agent
from agents.reviewer_agent import run_reviewer_agent
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections

OUTPUT_PATH = "output/study_guide.md"


def check_config() -> None:
    """Fail fast with a readable message if required config is missing."""
    if not os.environ.get("MODEL_NAME"):
        raise RuntimeError(
            "MODEL_NAME is not set. Copy .env.example to .env and set MODEL_NAME "
            "(e.g. ollama_chat/llama3.2:1b)."
        )
    if not os.environ.get("OLLAMA_API_BASE"):
        raise RuntimeError(
            "OLLAMA_API_BASE is not set. Copy .env.example to .env and set "
            "OLLAMA_API_BASE (e.g. http://localhost:11434)."
        )


def get_topic() -> str:
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:]).strip()
    else:
        topic = input("Enter a programming topic: ").strip()

    if not topic:
        raise ValueError("Topic cannot be empty.")
    return topic


def assemble_final_markdown(topic: str, explanation: str, practice: str, review: str) -> str:
    return (
        f"# {topic}\n\n"
        "## Topic\n"
        f"{topic}\n\n"
        f"{explanation.strip()}\n\n"
        f"{practice.strip()}\n\n"
        f"{review.strip()}\n\n"
        "## Final Summary\n"
        f"This study guide covered **{topic}**: a simple explanation, key concepts, "
        "a worked example, a practice exercise, common mistakes, and reviewer feedback. "
        "Revisit the practice exercise to check your understanding.\n"
    )


def main() -> None:
    check_config()
    topic = get_topic()

    print(f"[1/5] Running Explainer Agent for '{topic}'...")
    try:
        explanation = run_explainer_agent(topic)
    except Exception as exc:
        raise RuntimeError(
            f"Explainer Agent failed. Is Ollama running and is the model pulled? ({exc})"
        ) from exc
    if not explanation.strip():
        raise RuntimeError("Explainer Agent returned an empty response.")

    print("[2/5] Running Practice Designer Agent...")
    practice = run_practice_designer_agent(topic, explanation)
    if not practice.strip():
        raise RuntimeError("Practice Designer Agent returned an empty response.")

    draft = f"# {topic}\n\n{explanation.strip()}\n\n{practice.strip()}\n"

    print("[3/5] Running Reviewer Agent...")
    review = run_reviewer_agent(draft)
    if not review.strip():
        raise RuntimeError("Reviewer Agent returned an empty response.")

    print("[4/5] Assembling final Markdown and validating sections...")
    final_markdown = assemble_final_markdown(topic, explanation, practice, review)

    validation_result = validate_required_sections(final_markdown)
    if not validation_result["is_valid"]:
        print(
            "Warning: generated guide is missing sections: "
            f"{validation_result['missing_sections']}"
        )

    print("[5/5] Saving Markdown file...")
    try:
        result = save_markdown_file(OUTPUT_PATH, final_markdown)
    except Exception as exc:
        raise RuntimeError(f"Failed to save study guide: {exc}") from exc

    print(result)
    print(f"Validation: {validation_result}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
