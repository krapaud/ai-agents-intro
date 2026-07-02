"""Explainer Agent: produces a short explanation, key concepts, and an example."""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from agents.runner_utils import run_agent_sync

MODEL_NAME = os.environ.get("MODEL_NAME", "ollama_chat/llama3.2:1b")

explainer_agent = Agent(
    name="explainer_agent",
    model=LiteLlm(model=MODEL_NAME),
    instruction=(
        "You are an explainer agent for a beginner-friendly programming study guide. "
        "Given a topic, respond in Markdown with exactly these three headings, in order:\n"
        "## Simple Explanation\n"
        "## Key Concepts\n"
        "## Example\n\n"
        "Under 'Simple Explanation', write 2-4 short sentences a beginner can understand. "
        "Under 'Key Concepts', write a bulleted list of 3-6 short items. "
        "Under 'Example', include one small, concrete, correct code example in a fenced code block, "
        "with one sentence explaining what it does. "
        "Do not add any other headings or commentary."
    ),
)


def run_explainer_agent(topic: str) -> str:
    """Return Markdown with Simple Explanation, Key Concepts, and Example sections."""
    prompt = f"Topic: {topic}"
    return run_agent_sync(explainer_agent, prompt)


if __name__ == "__main__":
    print(run_explainer_agent("Python decorators"))
