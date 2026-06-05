"""
Agent: Match
Sammenligner krav med kandidatens profil og finner styrker, gap og beste eksempler.
Returnerer også en strukturert fit-vurdering for pipeline-beslutninger.
"""

import logging
from utils.llm import llm_with_tool

logger = logging.getLogger(__name__)

SYSTEM = """
Du er en karriererådgiver som hjelper kandidater å posisjonere seg best mulig.
Du er ærlig om gap, men fokuserer på å finne de sterkeste koblingene mellom
kandidatens erfaring og det stillingen krever.

Vær konkret – pek på spesifikke prosjekter og erfaringer, ikke generelle påstander.
Svar på norsk.
"""

FIT_TOOL = {
    "name": "set_fit",
    "description": "Registrer fit-vurderingen etter at analysen er skrevet.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fit_level": {
                "type": "string",
                "enum": ["strong", "medium", "weak"],
                "description": (
                    "'weak' = mangler flere sentrale krav (brukeren bør advares). "
                    "'strong' = sterk match, GapDetector kan hoppes over."
                ),
            },
            "fit_summary": {
                "type": "string",
                "description": "Én setning om matchkvaliteten — vises til brukeren ved svak match.",
            },
            "skip_gap_detector": {
                "type": "boolean",
                "description": "True kun ved 'strong' match.",
            },
        },
        "required": ["fit_level", "fit_summary", "skip_gap_detector"],
    },
}

DEFAULT_FIT = {
    "fit_level": "medium",
    "fit_summary": "",
    "skip_gap_detector": False,
}


async def match(krav: str, research: str, cv: str) -> tuple[str, dict]:
    """
    Returnerer (analyse_tekst, fit_vurdering).
    fit_vurdering inneholder fit_level, fit_summary og skip_gap_detector.
    """
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
Én setning — ikke punktliste, ikke tabell. Eksempel: "Posisjoner deg som en X med erfaring fra Y."

Kall set_fit etter at analysen er skrevet.
"""
    text, fit = await llm_with_tool(SYSTEM, prompt, FIT_TOOL, max_tokens=2000)

    if fit is None:
        logger.warning("Match returnerte ingen fit-vurdering — bruker standard.")
        fit = dict(DEFAULT_FIT)

    # Håndhev invariant
    if fit.get("skip_gap_detector") and fit.get("fit_level") != "strong":
        logger.warning(
            "Match satte skip_gap_detector=True med fit_level=%r — overstyrt til False.",
            fit.get("fit_level"),
        )
        fit["skip_gap_detector"] = False

    return text, {**DEFAULT_FIT, **fit}
