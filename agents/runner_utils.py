"""Shared helper for running a single ADK agent turn and getting text back."""

import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types


def run_agent_sync(agent: Agent, prompt: str) -> str:
    """Run agent with a single user prompt and return the final response text."""
    runner = InMemoryRunner(agent=agent, app_name="study_guide_app")
    user_id = "cli_user"

    async def _run() -> str:
        session = await runner.session_service.create_session(
            app_name="study_guide_app", user_id=user_id
        )
        content = types.Content(role="user", parts=[types.Part(text=prompt)])
        final_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_text = "".join(p.text or "" for p in event.content.parts)
        return final_text

    return asyncio.run(_run())
