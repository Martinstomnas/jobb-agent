import agents.validator as module


async def test_alle_inputs_i_prompt(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["prompt"] = prompt
        return "Ingen avvik funnet."

    monkeypatch.setattr(module, "llm", fake_llm)
    result = await module.validator("UTKAST", "CV", "KRAV", "RESEARCH")
    assert "UTKAST" in captured["prompt"]
    assert "CV" in captured["prompt"]
    assert "KRAV" in captured["prompt"]
    assert "RESEARCH" in captured["prompt"]
    assert result == "Ingen avvik funnet."


async def test_max_tokens_er_500(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["kwargs"] = kwargs
        return "output"

    monkeypatch.setattr(module, "llm", fake_llm)
    await module.validator("draft", "cv", "krav", "research")
    assert captured["kwargs"].get("max_tokens") == 500


async def test_avvik_returneres_direkte(monkeypatch):
    async def fake_llm(system, prompt, **kwargs):
        return "- Kandidaten nevner Azure, men det finnes ikke i CV-en"

    monkeypatch.setattr(module, "llm", fake_llm)
    result = await module.validator("draft", "cv", "krav", "research")
    assert "Azure" in result
