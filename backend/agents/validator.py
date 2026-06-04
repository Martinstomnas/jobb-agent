"""
Agent: Validator
Sjekker at Writer-output er faktaforankret.
Verifiserer at påstander i disposisjonen kan spores tilbake til CV og research.
"""

from utils.llm import llm

SYSTEM = """
Du er en faktasjekker. Din eneste oppgave er å verifisere at påstander i et dokument
kan spores tilbake til kildematerialet.
Se ikke etter kvalitet eller stil — bare uforankrede påstander.
Svar på norsk.
"""


async def validator(draft: str, cv: str, krav: str, research: str) -> str:
    prompt = f"""
Her er en søknadsdisposisjon:

{draft}

---

Kildemateriale:

CV:
{cv}

Krav fra stillingen:
{krav}

Research om arbeidsgiver:
{research}

---

Gå gjennom disposisjonen og identifiser påstander som IKKE kan verifiseres i kildematerialet.

Se spesielt etter:
- Ferdigheter, titler eller erfaringer som ikke finnes i CV-en
- Spesifikke prosjekter eller prestasjoner som ikke er nevnt i CV
- Påstander om kandidaten som går utover det CV-en faktisk dokumenterer

Lever kun funn som korte kulepunkter. Hvis alt er forankret, svar kun: "Ingen avvik funnet."
Maks 5 punkter.
"""
    return await llm(SYSTEM, prompt, max_tokens=500)
