"""
Tester Orchestrator: at en gyldig plan slippes gjennom og slås sammen med
defaults, og at ekte fallback brukes når modellen ikke returnerer en plan.
"""

from unittest.mock import AsyncMock

from agents import orchestrator as orch


async def test_gyldig_plan_returneres(monkeypatch):
    plan = {
        "fit_level": "strong",
        "fit_summary": "Sterk match.",
        "skip_gap_detector": True,
    }
    monkeypatch.setattr(orch, "llm_tool", AsyncMock(return_value=plan))
    result = await orch.orchestrator("krav", "match")
    assert result == plan


async def test_delvis_plan_fylles_med_defaults(monkeypatch):
    # Modellen utelater noen nøkler — defaults skal fylle inn resten.
    monkeypatch.setattr(
        orch, "llm_tool", AsyncMock(return_value={"fit_level": "weak"})
    )
    result = await orch.orchestrator("krav", "match")
    assert result["fit_level"] == "weak"
    assert result["skip_gap_detector"] is False
    assert result["fit_summary"] == ""


async def test_skip_gap_detector_overstyres_ved_ikke_sterk_match(monkeypatch):
    monkeypatch.setattr(
        orch,
        "llm_tool",
        AsyncMock(return_value={"fit_level": "medium", "fit_summary": "", "skip_gap_detector": True}),
    )
    result = await orch.orchestrator("krav", "match")
    assert result["skip_gap_detector"] is False


async def test_ingen_tool_use_gir_standardplan(monkeypatch):
    monkeypatch.setattr(orch, "llm_tool", AsyncMock(return_value=None))
    result = await orch.orchestrator("krav", "match")
    assert result == orch.DEFAULT_PLAN
    # Skal være en kopi, ikke samme objekt som modulkonstanten.
    assert result is not orch.DEFAULT_PLAN
