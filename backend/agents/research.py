"""
Agent: Research
Søker aktivt på nett etter informasjon om selskapet.
"""

from utils.llm import MODEL, api_errors, client

# Web-søk gjør flere runder server-side og tar lengre tid enn et vanlig kall,
# så vi gir dette kallet en romsligere timeout enn klient-standarden.
RESEARCH_TIMEOUT = 120.0


async def research(job_posting: str) -> tuple[str, list[dict]]:
    """
    Returnerer (tekst, søkelogg) der søkelogg er en liste av
    {"query": str, "results": [{"title": str, "url": str}]}.
    """
    async with api_errors():
        response = await client.with_options(timeout=RESEARCH_TIMEOUT).messages.create(
            model=MODEL,
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            system="""
Du er en researcher som hjelper jobbsøkere å forstå selskaper de søker hos.
Søk aktivt på nett for å finne fersk og relevant informasjon.
Fokuser på: kultur, tech-stack, verdier, kunder, nyheter, og hva ansatte sier.
Vær faktabasert. Skill tydelig mellom det du fant på nett og egne antakelser.
Svar på norsk.

Når du refererer til spesifikk informasjon du har funnet på nett, siter kilden inline med markdown-lenke: [kildenavn](url).
Eksempel: "Selskapet ble grunnlagt i 2010 [Selskapet.no](https://selskapet.no/om-oss) og har 200 ansatte [LinkedIn](https://linkedin.com/company/selskapet)."
Ikke legg alle kilder i en egen seksjon – integrer dem direkte i teksten der påstandene dukker opp.
Informasjon du ikke kan bekrefte fra søkeresultatene skal merkes med [USIKKER].
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

Lever en strukturert oppsummering med inline-kildehenvisninger (markdown-lenker) for alle påstander du kan bekrefte fra søkeresultatene:
## Selskapet
## Kultur og verdier
## Tech-stack og arbeidsmetoder
## Aktuelt (nyheter, vekst, prosjekter)
## Hva tidligere/nåværende ansatte sier
""",
                }
            ],
        )

    sources: list[dict] = []

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

    seen_urls: set[str] = set()
    for entry in sources:
        unique: list[dict] = []
        for r in entry["results"]:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique.append(r)
        entry["results"] = unique

    text = "\n".join(
        block.text for block in response.content if hasattr(block, "text")
    )
    if not text.strip():
        return "Ingen research-data tilgjengelig.", sources
    return text, sources
