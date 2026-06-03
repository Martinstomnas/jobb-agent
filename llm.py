"""
Delt LLM-klient. Bruker Anthropic Claude.
"""
import asyncio
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

async def llm(system: str, user: str, max_tokens: int = 1500) -> str:
    def _call():
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text
    return await asyncio.get_event_loop().run_in_executor(None, _call)