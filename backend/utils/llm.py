"""
Delt LLM-klient. Bruker Anthropic Claude (async).
"""
import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import anthropic

logger = logging.getLogger(__name__)

load_dotenv()

# Per-kall timeout og automatiske retries. SDK-en retry-er transiente feil
# (429, 5xx, connection) med eksponentiell backoff og respekterer Retry-After —
# derfor konfigurerer vi den her i stedet for å håndrulle en backoff-løkke.
REQUEST_TIMEOUT = 60.0  # sekunder per kall — hindrer hengende forespørsler
MAX_RETRIES = 3

client = anthropic.AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    timeout=REQUEST_TIMEOUT,
    max_retries=MAX_RETRIES,
)

MODEL = "claude-haiku-4-5-20251001"


@asynccontextmanager
async def api_errors():
    """Mapper Anthropic-feil til brukervennlige RuntimeErrors."""
    try:
        yield
    except anthropic.RateLimitError:
        raise RuntimeError("Rate limit nådd — prøv igjen om litt")
    except anthropic.APITimeoutError:
        raise RuntimeError("Forespørselen tok for lang tid — prøv igjen")
    except anthropic.APIConnectionError:
        raise RuntimeError("Kunne ikke koble til Anthropic API")
    except anthropic.AuthenticationError:
        raise RuntimeError("Ugyldig API-nøkkel")
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"API-feil ({e.status_code})")


async def llm(
    system: str, user: str, max_tokens: int = 1500, temperature: float = 1.0
) -> str:
    async with api_errors():
        response = await client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    if response.stop_reason == "max_tokens":
        logger.warning(
            "Svar avkuttet av max_tokens (%d) — vurder å heve grensen.", max_tokens
        )
    return response.content[0].text


async def llm_tool(
    system: str,
    user: str,
    tool: dict,
    max_tokens: int = 500,
    temperature: float = 0.0,
) -> dict | None:
    """
    Kaller modellen med tvunget tool-bruk og returnerer tool-inputen som dict.
    Returnerer None hvis modellen ikke produserte et tool_use-kall.
    Erstatter skjør JSON-parsing: skjemaet i `tool` validerer strukturen.
    Standard temperatur er 0 — strukturert beslutningsoutput skal være stabil.
    """
    async with api_errors():
        response = await client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool["name"]},
            messages=[{"role": "user", "content": user}],
        )
    for block in response.content:
        if getattr(block, "type", None) == "tool_use":
            return block.input
    return None
