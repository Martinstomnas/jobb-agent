import agents.writer as module


async def test_alle_inputs_i_prompt(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["prompt"] = prompt
        return "disposisjon"

    monkeypatch.setattr(module, "llm", fake_llm)
    result = await module.writer("KRAV", "RESEARCH", "MATCH")
    assert "KRAV" in captured["prompt"]
    assert "RESEARCH" in captured["prompt"]
    assert "MATCH" in captured["prompt"]
    assert result == "disposisjon"


async def test_extra_context_inkluderes_i_prompt(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["prompt"] = prompt
        return "output"

    monkeypatch.setattr(module, "llm", fake_llm)
    await module.writer("krav", "research", "match", extra_context="Jobbet i Equinor")
    assert "Equinor" in captured["prompt"]
    assert "Tilleggsinformasjon" in captured["prompt"]


async def test_tom_extra_context_gir_ingen_tilleggsseksjon(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["prompt"] = prompt
        return "output"

    monkeypatch.setattr(module, "llm", fake_llm)
    await module.writer("krav", "research", "match")
    assert "Tilleggsinformasjon" not in captured["prompt"]


async def test_max_tokens_er_1500(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["kwargs"] = kwargs
        return "output"

    monkeypatch.setattr(module, "llm", fake_llm)
    await module.writer("krav", "research", "match")
    assert captured["kwargs"].get("max_tokens") == 1500
