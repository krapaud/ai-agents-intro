"""Reviewer Agent: inspects a draft study guide and produces review comments."""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from agents.runner_utils import run_agent_sync

MODEL_NAME = os.environ.get("MODEL_NAME", "ollama_chat/llama3.2:1b")

reviewer_agent = Agent(
    name="reviewer_agent",
    model=LiteLlm(model=MODEL_NAME),
    instruction=(
        "You are a reviewer agent for a beginner-friendly programming study guide. "
        "You will be given a draft study guide in Markdown. Review it for clarity, "
        "completeness, and usefulness. Do not rewrite the guide. "
        "Respond in Markdown with exactly two headings:\n"
        "## Common Mistakes\n"
        "## Review Comments\n\n"
        "Under 'Common Mistakes', list 2-4 common mistakes beginners make with this topic. "
        "Under 'Review Comments', give specific, actionable feedback: missing information, "
        "ambiguous parts, suggestions for improvement, and end with a short approval or "
        "revision recommendation. Be specific, not generic. "
        "Do not add any other headings or commentary."
    ),
)


def run_reviewer_agent(draft: str) -> str:
    """Return Markdown with Common Mistakes and Review Comments sections."""
    prompt = f"Draft study guide:\n\n{draft}\n\nReview it now."
    return run_agent_sync(reviewer_agent, prompt)


if __name__ == "__main__":
    sample_draft = (
        "# Python decorators\n\n"
        "## Simple Explanation\nDecorators wrap functions.\n\n"
        "## Key Concepts\n- functions are objects\n\n"
        "## Example\n```python\n@dec\ndef f(): pass\n```\n"
    )
    print(run_reviewer_agent(sample_draft))
