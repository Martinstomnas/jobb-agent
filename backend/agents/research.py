"""
Agent 2: Research
Søker aktivt på nett etter informasjon om selskapet.
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


async def research(job_posting: str) -> tuple[str, list[dict]]:
    """
    Returnerer (tekst, søkelogg) der søkelogg er en liste av
    {"query": str, "results": [{"title": str, "url": str}]}.
    """
    import asyncio

    def _call():
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            system="""
Du er en researcher som hjelper jobbsøkere å forstå selskaper de søker hos.
Søk aktivt på nett for å finne fersk og relevant informasjon.
Fokuser på: kultur, tech-stack, verdier, kunder, nyheter, og hva ansatte sier.
Vær faktabasert. Skill tydelig mellom det du fant på nett og egne antakelser.
Svar på norsk.
""",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Analyser denne stillingsannonsen og finn ut mest mulig om selskapet.
Søk etter: selskapsnavn + kultur, tech-stack, ansatte, nyheter det siste året.

Annonse:
---
{job_posting}
---

Lever en strukturert oppsummering:
## Selskapet
## Kultur og verdier
## Tech-stack og arbeidsmetoder
## Aktuelt (nyheter, vekst, prosjekter)
## Hva tidligere/nåværende ansatte sier [USIKKER hvis ikke funnet]
""",
                }
            ],
        )

        sources: list[dict] = []
        current_query = ""

        for block in response.content:
            block_type = getattr(block, "type", None)

            if block_type == "server_tool_use":
                tool_input = getattr(block, "input", {}) or {}
                current_query = (
                    tool_input.get("query", "")
                    if isinstance(tool_input, dict)
                    else getattr(tool_input, "query", "")
                )
                sources.append({"query": current_query, "results": []})

            elif block_type == "web_search_tool_result":
                for result in getattr(block, "content", []) or []:
                    title = result.get("title", "") if isinstance(result, dict) else getattr(result, "title", "")
                    url = result.get("url", "") if isinstance(result, dict) else getattr(result, "url", "")
                    if sources:
                        sources[-1]["results"].append({"title": title, "url": url})

        text = "\n".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        return text, sources

    return await asyncio.get_event_loop().run_in_executor(None, _call)