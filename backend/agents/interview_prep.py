"""
Agent 6: InterviewPrep
Genererer intervjuforberedelse basert på krav, research og match-analyse.
Kjøres parallelt med Writer.
"""

from utils.llm import llm

SYSTEM = """
Du er en erfaren karriererådgiver som hjelper kandidater å forberede seg til jobbintervju.
Vær konkret og direkte. Ingen generiske råd. Basér alt på den faktiske stillingen og kandidatens profil.
Svar på norsk.
"""


async def interview_prep(
    krav: str,
    research: str,
    match: str,
    extra_context: str = "",
) -> str:
    extra_section = (
        f"\nTilleggsinformasjon fra kandidaten:\n{extra_context}\n"
        if extra_context
        else ""
    )
    prompt = f"""
Lag en konkret intervjuforberedelse basert på:

Krav fra stillingen:
{krav}

Research om selskapet:
{research}

Match-analyse (styrker og gap):
{match}
{extra_section}

Lever to seksjoner:

Velg 4-5 spørsmål som denne kandidaten sannsynligvis vil få, basert på kravene og gapene i match-analysen.
For hvert spørsmål:
**Sp: [Spørsmålet]**
Svar: [Én konkret tilnærming til svar – hva skal kandidaten fremheve, hvilken erfaring passer, hvordan håndtere gap ærlig]

## Spørsmål å stille arbeidsgiveren

3 konkrete spørsmål kandidaten bør stille i intervjuet, basert på research om selskapet.
Spørsmålene skal vise at kandidaten har satt seg inn i selskapet og tenker strategisk.
Format: én setning per spørsmål, ingen forklaring.
"""
    return await llm(SYSTEM, prompt, max_tokens=2000)
