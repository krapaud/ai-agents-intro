"""Practice Designer Agent: creates a small exercise based on the explanation."""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from agents.runner_utils import run_agent_sync

MODEL_NAME = os.environ.get("MODEL_NAME", "ollama_chat/llama3.2:1b")

practice_designer_agent = Agent(
    name="practice_designer_agent",
    model=LiteLlm(model=MODEL_NAME),
    instruction=(
        "You are a practice designer agent for a beginner-friendly programming study guide. "
        "You will be given a topic and an explanation that was already written by another agent. "
        "Do not rewrite or repeat the explanation. "
        "Respond in Markdown with exactly one heading, written EXACTLY as shown below "
        "(no extra words on the heading line):\n"
        "## Practice Exercise\n\n"
        "Under that single heading, write a small, concrete exercise a beginner could finish "
        "in 10-20 minutes, including expected input/output if relevant, and 1-2 short hints. "
        "Use plain text or bullet points under the heading, not additional headings. "
        "Do not add any other headings or commentary."
    ),
)


def run_practice_designer_agent(topic: str, explanation: str) -> str:
    """Return Markdown with a single Practice Exercise section."""
    prompt = (
        f"Topic: {topic}\n\n"
        f"Explanation already written:\n{explanation}\n\n"
        "Create the practice exercise now."
    )
    return run_agent_sync(practice_designer_agent, prompt)


if __name__ == "__main__":
    from agents.explainer_agent import run_explainer_agent

    topic = "Python decorators"
    explanation = run_explainer_agent(topic)
    print(run_practice_designer_agent(topic, explanation))
