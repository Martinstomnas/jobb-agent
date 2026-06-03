"""
Agent: Orchestrator
Leser krav og match-analyse og bestemmer hvordan pipelinen skal kjøres.
Returnerer en JSON-plan med beslutninger om neste steg.
"""

import json
import logging
import re
from utils.llm import llm

logger = logging.getLogger(__name__)

SYSTEM = """
Du er en pipeline-orchestrator for et jobbsøkersystem.
Du skal vurdere hvor godt en kandidat matcher en stilling og bestemme hvordan analysen skal fortsette.
Svar alltid med kun gyldig JSON — ingen forklaring utenfor JSON-blokken.
"""


async def orchestrator(krav: str, match: str) -> dict:
    prompt = f"""
Vurder kandidatens match mot stillingen basert på disse inputene:

## Krav fra stillingen
{krav}

## Match-analyse (styrker, gap, posisjonering)
{match}

---

Returner en JSON-plan med disse feltene:

{{
  "fit_level": "strong" | "medium" | "weak",
  "fit_summary": "én setning om matchkvaliteten",
  "skip_gap_detector": true | false,
  "critic_rounds": 1 | 2
}}

Regler:
- fit_level "weak": kandidaten mangler flere sentrale krav — brukeren bør advares
- fit_level "strong": sterk match — hopp over GapDetector (skip_gap_detector: true)
- critic_rounds 2: kun ved "weak" eller tydelige gap som krever ekstra revisjon
- skip_gap_detector true: kun ved "strong" match
"""
    result = await llm(SYSTEM, prompt, max_tokens=200)

    json_match = re.search(r'\{.*\}', result, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Orchestrator fikk ugyldig JSON — bruker standardplan. Svar: %r", result[:200])
    return {"fit_level": "medium", "fit_summary": "", "skip_gap_detector": False, "critic_rounds": 1}
