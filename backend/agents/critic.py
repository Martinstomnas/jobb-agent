"""
Agent: Critic
Evaluerer Writer-utkastet mot krav og match-analyse.
Returnerer konkret kritikk som Writer bruker til å forbedre disposisjonen.
"""

from utils.llm import llm

SYSTEM = """
Du er en kritisk redaktør som evaluerer søknadsdisposisjoner.
Vær konkret og direkte. Identifiser svakheter — ikke ros.
Svar på norsk.
"""


async def critic(draft: str, krav: str, match: str) -> str:
    prompt = f"""
Her er et utkast til søknadsdisposisjon:

{draft}

---

Krav fra stillingen:
{krav}

Match-analyse (styrker og gap):
{match}

---

Evaluer utkastet på disse punktene:

1. Dekker alle nøkkelkrav konkrete CV-eksempler, eller er noen krav ikke adressert?
2. Er gap-håndteringen ærlig og konstruktiv, eller defensiv og vag?
3. Er det generiske råd som burde vært mer spesifikke for denne stillingen?

Lever 2-4 konkrete forbedringspunkter. Ingen ros. Bare det som kan gjøres bedre.
"""
    return await llm(SYSTEM, prompt, max_tokens=600)
