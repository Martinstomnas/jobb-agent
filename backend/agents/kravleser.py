"""
Agent 1: Kravleser
Leser stillingsannonsen og trekker ut eksplisitte krav og implisitte signaler.
"""

from utils.llm import llm

SYSTEM = """
Du er en ekspert på å analysere stillingsannonser.
Din jobb er å lese mellom linjene og finne:
1. Eksplisitte krav – det som faktisk står skrevet
2. Implisitte signaler – kulturen, forventningene og prioriteringene som ikke sies rett ut

Vær konkret og kortfattet. Ikke gjengi annonsen – analyser den.
Svar på norsk.
"""


async def kravleser(job_posting: str) -> str:
    prompt = f"""
Analyser denne stillingsannonsen:

---
{job_posting}
---

Svar strukturert:

## Eksplisitte krav
- (list harde krav: teknologier, erfaring, utdanning)

## Implisitte signaler
- (list kulturelle forventninger, prioriteringer, hva de egentlig ser etter)

## Nøkkelord å speile i søknaden
- (3-5 ord/fraser fra annonsen som bør gjentas i søknaden)
"""
    return await llm(SYSTEM, prompt)
