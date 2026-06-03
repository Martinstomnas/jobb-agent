"""
Agent: Critic
Evaluerer Writer-utkastet mot krav, match-analyse og CV.
Returnerer konkret kritikk som Writer bruker til å forbedre disposisjonen.
"""

from utils.llm import llm

SYSTEM = """
Du er en kritisk redaktør som evaluerer søknadsdisposisjoner.
Vær konkret og direkte. Identifiser svakheter — ikke ros.
Svar på norsk.
"""


async def critic(draft: str, krav: str, match: str, cv: str) -> str:
    prompt = f"""
Her er et utkast til søknadsdisposisjon:

{draft}

---

Krav fra stillingen:
{krav}

Match-analyse (styrker og gap):
{match}

Kandidatens CV:
{cv}

---

Evaluer utkastet på disse punktene:

1. Dekker alle nøkkelkrav konkrete CV-eksempler, eller er noen krav ikke adressert?
2. Er gap-håndteringen ærlig og konstruktiv, eller defensiv og vag?
3. Er det generiske råd som burde vært mer spesifikke for denne stillingen?
4. Er det påstander om kandidatens erfaring eller ferdigheter som ikke er forankret i CV-en — 
dvs. noe som kan overdrive, pynte på eller gå utover det CV-en faktisk dokumenterer?

Lever 2-4 konkrete forbedringspunkter. Ingen ros. Bare det som kan gjøres bedre.
"""
    return await llm(SYSTEM, prompt, max_tokens=700)
