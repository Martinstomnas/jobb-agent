"""
Tester parsing-logikken i GapDetector — den deterministiske delen som filtrerer
og begrenser LLM-output. LLM-kallet selv mockes, så ingen nettverk.
"""

from unittest.mock import AsyncMock

from agents import gap_detector as gd


async def _run_with_llm_output(monkeypatch, text: str):
    monkeypatch.setattr(gd, "llm", AsyncMock(return_value=text))
    return await gd.gap_detector("research", "cv")


async def test_ingen_gir_tom_liste(monkeypatch):
    assert await _run_with_llm_output(monkeypatch, "INGEN") == []


async def test_ingen_er_case_insensitiv(monkeypatch):
    assert await _run_with_llm_output(monkeypatch, "ingen reelle gap") == []


async def test_ett_spoersmaal_per_linje(monkeypatch):
    out = await _run_with_llm_output(monkeypatch, "Spørsmål 1?\nSpørsmål 2?")
    assert out == ["Spørsmål 1?", "Spørsmål 2?"]


async def test_maks_tre_spoersmaal(monkeypatch):
    out = await _run_with_llm_output(monkeypatch, "A?\nB?\nC?\nD?\nE?")
    assert out == ["A?", "B?", "C?"]


async def test_markdown_og_overskrifter_filtreres_bort(monkeypatch):
    out = await _run_with_llm_output(
        monkeypatch, "Ekte spørsmål?\n**fet linje**\n# overskrift"
    )
    assert out == ["Ekte spørsmål?"]


async def test_for_lange_linjer_filtreres_bort(monkeypatch):
    long_line = "x" * 201
    out = await _run_with_llm_output(monkeypatch, f"Kort?\n{long_line}")
    assert out == ["Kort?"]


async def test_blanke_linjer_ignoreres(monkeypatch):
    out = await _run_with_llm_output(monkeypatch, "\n\nSpørsmål?\n\n")
    assert out == ["Spørsmål?"]
