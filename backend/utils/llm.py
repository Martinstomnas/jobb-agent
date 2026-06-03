"""
Delt LLM-klient. Bruker Anthropic Claude (async).
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5-20251001"


@asynccontextmanager
async def api_errors():
    """Mapper Anthropic-feil til brukervennlige RuntimeErrors."""
    try:
        yield
    except anthropic.RateLimitError:
        raise RuntimeError("Rate limit nådd — prøv igjen om litt")
    except anthropic.APIConnectionError:
        raise RuntimeError("Kunne ikke koble til Anthropic API")
    except anthropic.AuthenticationError:
        raise RuntimeError("Ugyldig API-nøkkel")
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"API-feil ({e.status_code})")


async def llm(system: str, user: str, max_tokens: int = 1500) -> str:
    async with api_errors():
        response = await client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    return response.content[0].text


async def llm_tool(
    system: str, user: str, tool: dict, max_tokens: int = 500
) -> dict | None:
    """
    Kaller modellen med tvunget tool-bruk og returnerer tool-inputen som dict.
    Returnerer None hvis modellen ikke produserte et tool_use-kall.
    Erstatter skjør JSON-parsing: skjemaet i `tool` validerer strukturen.
    """
    async with api_errors():
        response = await client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool["name"]},
            messages=[{"role": "user", "content": user}],
        )
    for block in response.content:
        if getattr(block, "type", None) == "tool_use":
            return block.input
    return None
