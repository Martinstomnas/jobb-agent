"""
Agent: Gap Detector
Identifiserer domener i Research som kandidaten ikke har nevnt i CV,
og genererer målrettet oppfølgingsspørsmål.
"""

from utils.llm import llm

SYSTEM = """
Du svarer med ett spørsmål per linje (maks 3 linjer) eller ordet INGEN.
Ingen nummerering, ingen markdown, ingen forklaring. Bare spørsmålene eller INGEN.
Still kun spørsmål om gap som er vesentlige for stillingen.
"""


async def gap_detector(research: str, cv: str, krav: str = "") -> list[str]:
    """
    Returnerer 0–3 oppfølgingsspørsmål basert på domenegap mellom krav/research og CV.
    """
    krav_section = f"\nKrav fra stillingen:\n{krav}\n" if krav else ""
    prompt = f"""
Research om selskapet:
{research}
{krav_section}
Kandidatens CV:
{cv}

Finn krav eller domener som er vesentlige for stillingen, men som kandidaten IKKE har nevnt i CV-en.
For hvert vesentlig gap (maks 3): skriv ett spørsmål, ett per linje.
Bare spørsmål som faktisk vil berike søknaden.
Eksempel: "Jeg fant at de jobber mye med energisektoren – har du noen erfaring derfra?"
INGEN hvis ingen reelle gap.

Svar nå:"""
    # Gap-deteksjon er en analytisk vurdering -> lav temperatur for stabilitet.
    result = await llm(SYSTEM, prompt, max_tokens=250, temperature=0)
    lines = result.strip().splitlines()
    questions = []
    for line in lines:
        line = line.strip()
        if not line or line.upper().startswith("INGEN"):
            continue
        if len(line) > 200 or "**" in line or "#" in line:
            continue
        questions.append(line)
        if len(questions) == 3:
            break
    return questions
