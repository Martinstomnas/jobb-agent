"""
Delt LLM-klient. Bruker Anthropic Claude (async).
"""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


async def llm(system: str, user: str, max_tokens: int = 1500) -> str:
    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text
    except anthropic.RateLimitError:
        raise RuntimeError("Rate limit nådd — prøv igjen om litt")
    except anthropic.APIConnectionError:
        raise RuntimeError("Kunne ikke koble til Anthropic API")
    except anthropic.AuthenticationError:
        raise RuntimeError("Ugyldig API-nøkkel")
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"API-feil ({e.status_code})")
