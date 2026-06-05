"""
Tester Match: analyse-tekst og fit-vurdering returneres korrekt,
fallback brukes når modellen ikke returnerer tool_use, og
skip_gap_detector-invarianten håndheves.
"""

from unittest.mock import AsyncMock

import agents.match as module


async def test_returnerer_tekst_og_fit(monkeypatch):
    fit = {"fit_level": "strong", "fit_summary": "Sterk.", "skip_gap_detector": True}
    monkeypatch.setattr(module, "llm_with_tool", AsyncMock(return_value=("ANALYSE", fit)))
    text, result = await module.match("krav", "research", "cv")
    assert text == "ANALYSE"
    assert result["fit_level"] == "strong"
    assert result["skip_gap_detector"] is True


async def test_fallback_ved_ingen_tool_use(monkeypatch):
    monkeypatch.setattr(module, "llm_with_tool", AsyncMock(return_value=("ANALYSE", None)))
    text, result = await module.match("krav", "research", "cv")
    assert text == "ANALYSE"
    assert result == module.DEFAULT_FIT
    assert result is not module.DEFAULT_FIT


async def test_delvis_fit_fylles_med_defaults(monkeypatch):
    monkeypatch.setattr(
        module, "llm_with_tool", AsyncMock(return_value=("ANALYSE", {"fit_level": "weak"}))
    )
    _, result = await module.match("krav", "research", "cv")
    assert result["fit_level"] == "weak"
    assert result["skip_gap_detector"] is False
    assert result["fit_summary"] == ""


async def test_skip_gap_detector_overstyres_ved_ikke_sterk_match(monkeypatch):
    fit = {"fit_level": "medium", "fit_summary": "", "skip_gap_detector": True}
    monkeypatch.setattr(module, "llm_with_tool", AsyncMock(return_value=("ANALYSE", fit)))
    _, result = await module.match("krav", "research", "cv")
    assert result["skip_gap_detector"] is False


async def test_alle_inputs_i_prompt(monkeypatch):
    captured = {}

    async def fake(system, prompt, tool, **kwargs):
        captured["prompt"] = prompt
        return ("output", None)

    monkeypatch.setattr(module, "llm_with_tool", fake)
    await module.match("KRAV", "RESEARCH", "CV")
    assert "KRAV" in captured["prompt"]
    assert "RESEARCH" in captured["prompt"]
    assert "CV" in captured["prompt"]
