"""
Agent: Match
Sammenligner krav med kandidatens profil og finner styrker, gap og beste eksempler.
"""

from utils.llm import llm

SYSTEM = """
Du er en karriererådgiver som hjelper kandidater å posisjonere seg best mulig.
Du er ærlig om gap, men fokuserer på å finne de sterkeste koblingene mellom
kandidatens erfaring og det stillingen krever.

Vær konkret – pek på spesifikke prosjekter og erfaringer, ikke generelle påstander.
Svar på norsk.
"""


async def match(krav: str, research: str, cv: str) -> str:
    prompt = f"""
Du har fått disse tre inputene:

## Krav fra stillingen
{krav}

## Research (selskap)
{research}

## CV
{cv}

Gjør en ærlig match-analyse:

## Sterke kort
- (konkrete erfaringer som treffer kravene direkte – pek på spesifikke prosjekter)

## Gap å håndtere
- (hva mangler, og hvordan kan kandidaten adressere det i søknaden)

## Anbefalt vinkling
- (én setning om hvordan kandidaten bør posisjonere seg)
"""
    return await llm(SYSTEM, prompt, max_tokens=2000)
