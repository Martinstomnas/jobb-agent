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


async def validator(
    draft: str, cv: str, krav: str, research: str, extra_context: str = ""
) -> str:
    extra_section = (
        f"\nBekreftet tilleggsinformasjon fra kandidaten:\n{extra_context}\n\n"
        "VIKTIG: Punktene over er direkte bekreftet av kandidaten og skal aldri flagges som avvik. "
        "Behandle dem som like gyldige som CV-en.\n"
        if extra_context
        else ""
    )
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
{extra_section}
---

Gå gjennom disposisjonen og identifiser påstander som IKKE kan verifiseres i kildematerialet ovenfor.

Se spesielt etter:
- Ferdigheter, titler eller erfaringer som ikke finnes i CV-en eller bekreftet tilleggsinformasjon
- Spesifikke prosjekter eller prestasjoner som ikke er nevnt i CV eller bekreftet tilleggsinformasjon
- Påstander om kandidaten som går utover det kildematerialet faktisk dokumenterer

Lever kun funn som korte kulepunkter. Hvis alt er forankret, svar kun: "Ingen avvik funnet."
Maks 5 punkter.
"""
    return await llm(SYSTEM, prompt, max_tokens=500, temperature=0)
