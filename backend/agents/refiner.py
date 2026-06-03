"""
Agent: Refiner
Reviderer en eksisterende søknadsdisposisjon basert på kandidatens instruksjon.
"""

from utils.llm import llm

SYSTEM = """
Du er en redaktør som forbedrer søknadsdisposisjoner.
Du får en eksisterende disposisjon og en konkret instruksjon fra kandidaten.
Gjør kun den etterspurte endringen — behold alt annet uendret.
Svar på norsk.
"""


async def refiner(disposition: str, instruction: str) -> str:
    prompt = f"""
Her er den eksisterende søknadsdisposisjonen:

{disposition}

---

Kandidatens instruksjon:
{instruction}

Lever den reviderte disposisjonen i sin helhet.
"""
    return await llm(SYSTEM, prompt, max_tokens=1500)
