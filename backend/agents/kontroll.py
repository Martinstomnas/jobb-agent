"""
Agent 7: Kontroll
Validerer disposisjonen mot CV-dataene.
Merker hvert punkt som godt støttet, trenger utdyping, eller bør verifiseres.
"""

from utils.llm import llm

SYSTEM = """
Du er en kritisk karriereveileder. Din jobb er å sjekke at søknadsdisposisjonen er forankret i kandidatens faktiske CV.

Du skiller mellom:
- [OK]: direkte dokumentert i CV – trygt å bruke
- [Utdyp]: rimelig slutning fra kjent erfaring, men kandidaten bør legge til egne detaljer
- [Sjekk]: ikke klart dokumentert – kandidaten må verifisere eller fjerne

Regler:
- Ikke skriv om disposisjonen. Annotter den.
- Vær presis og kortfattet i vurderingene.
- Ikke bruk tabeller.
- Ikke bruk emojier.
- Svar på norsk.
"""


async def kontroll(writer_output: str, research: str) -> str:
    prompt = f"""
Her er søknadsdisposisjonen som skal valideres:

{writer_output}

---

Her er de faktiske dataene vi har om kandidaten (CV og research):

{research}

---

Gjør en validering av disposisjonen:

## Vurdering av disposisjonen

Gå gjennom hvert nøkkelpunkt og marker det med [OK], [Utdyp] eller [Sjekk]. Forklar kort hvorfor.

## Oppsummering
Et kort avsnitt om hva kandidaten står sterkt på i denne søknaden, og hva de bør tenke nøye gjennom eller utdype selv før de skriver.
"""
    return await llm(SYSTEM, prompt, max_tokens=1500)
