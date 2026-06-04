import agents.kravleser as module


async def test_job_posting_i_prompt(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["prompt"] = prompt
        return "krav-output"

    monkeypatch.setattr(module, "llm", fake_llm)
    result = await module.kravleser("Vi søker en Python-utvikler med 5 års erfaring")
    assert "Vi søker en Python-utvikler" in captured["prompt"]
    assert result == "krav-output"


async def test_bruker_temperatur_null(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["kwargs"] = kwargs
        return "output"

    monkeypatch.setattr(module, "llm", fake_llm)
    await module.kravleser("annonse")
    assert captured["kwargs"].get("temperature") == 0


async def test_tom_annonse_sendes_videre(monkeypatch):
    captured = {}

    async def fake_llm(system, prompt, **kwargs):
        captured["prompt"] = prompt
        return ""

    monkeypatch.setattr(module, "llm", fake_llm)
    result = await module.kravleser("")
    assert result == ""
