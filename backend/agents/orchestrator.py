"""
Agent: Orchestrator
Leser krav og match-analyse og bestemmer hvordan pipelinen skal kjøres.
Returnerer en plan med beslutninger om neste steg via structured output (tool use).
"""

import logging
from utils.llm import llm_tool

logger = logging.getLogger(__name__)

SYSTEM = """
Du er en pipeline-orchestrator for et jobbsøkersystem.
Du skal vurdere hvor godt en kandidat matcher en stilling og bestemme hvordan analysen skal fortsette.
Bruk verktøyet set_plan for å registrere planen.
"""

DEFAULT_PLAN = {
    "fit_level": "medium",
    "fit_summary": "",
    "skip_gap_detector": False,
}

PLAN_TOOL = {
    "name": "set_plan",
    "description": "Registrer pipeline-planen for videre kjøring.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fit_level": {
                "type": "string",
                "enum": ["strong", "medium", "weak"],
                "description": (
                    "Hvor godt kandidaten matcher. 'weak' = mangler flere sentrale "
                    "krav (brukeren bør advares). 'strong' = sterk match."
                ),
            },
            "fit_summary": {
                "type": "string",
                "description": "Én setning om matchkvaliteten.",
            },
            "skip_gap_detector": {
                "type": "boolean",
                "description": "Hopp over GapDetector — sett true kun ved 'strong' match.",
            },
        },
        "required": ["fit_level", "fit_summary", "skip_gap_detector"],
    },
}


async def orchestrator(krav: str, match: str) -> dict:
    prompt = f"""
Vurder kandidatens match mot stillingen basert på disse inputene:

## Krav fra stillingen
{krav}

## Match-analyse (styrker, gap, posisjonering)
{match}

Registrer planen med set_plan.
"""
    plan = await llm_tool(SYSTEM, prompt, PLAN_TOOL, max_tokens=300)

    if plan is None:
        logger.warning("Orchestrator returnerte ingen plan — bruker standardplan.")
        return dict(DEFAULT_PLAN)

    # Slå sammen med defaults så alle nøkler garantert finnes nedstrøms.
    merged = {**DEFAULT_PLAN, **plan}

    # Håndhev invariant: GapDetector kan kun hoppes over ved sterk match.
    if merged["skip_gap_detector"] and merged["fit_level"] != "strong":
        logger.warning(
            "Orchestrator satte skip_gap_detector=True med fit_level=%r — overstyrt til False.",
            merged["fit_level"],
        )
        merged["skip_gap_detector"] = False

    return merged
