"""
Tester for Research-agenten. Mocker Anthropic-klienten slik at ingen ekte
API-kall gjøres, og verifiserer at tekst og søkelogg parses korrekt.
"""

from unittest.mock import AsyncMock, MagicMock

import agents.research as module


class _Block:
    """Enkel block-stub der hasattr() oppfører seg korrekt."""

    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)


def _mock_client(content_blocks):
    mock_response = MagicMock()
    mock_response.content = content_blocks

    mock_messages = MagicMock()
    mock_messages.create = AsyncMock(return_value=mock_response)

    mock_with_options = MagicMock()
    mock_with_options.messages = mock_messages

    mock_client = MagicMock()
    mock_client.with_options.return_value = mock_with_options
    return mock_client


async def test_tekst_ekstraheres_fra_text_blokker(monkeypatch):
    blocks = [_Block(type="text", text="Selskapet er bra.")]
    monkeypatch.setattr(module, "client", _mock_client(blocks))

    text, sources = await module.research("stillingsannonse")
    assert "Selskapet er bra." in text
    assert sources == []


async def test_soek_og_resultater_parses(monkeypatch):
    blocks = [
        _Block(type="server_tool_use", input={"query": "Acme AS kultur"}),
        _Block(type="web_search_tool_result", content=[
            {"title": "Acme AS – om oss", "url": "https://acme.no/om-oss"}
        ]),
        _Block(type="text", text="Acme er et norsk selskap."),
    ]
    monkeypatch.setattr(module, "client", _mock_client(blocks))

    text, sources = await module.research("Vi søker i Acme AS")
    assert "Acme er et norsk selskap." in text
    assert len(sources) == 1
    assert sources[0]["query"] == "Acme AS kultur"
    assert sources[0]["results"][0]["url"] == "https://acme.no/om-oss"
    assert sources[0]["results"][0]["title"] == "Acme AS – om oss"


async def test_flere_soek_gir_separate_oppforinger(monkeypatch):
    blocks = [
        _Block(type="server_tool_use", input={"query": "Acme tech stack"}),
        _Block(type="web_search_tool_result", content=[
            {"title": "Tech", "url": "https://acme.no/tech"}
        ]),
        _Block(type="server_tool_use", input={"query": "Acme nyheter 2025"}),
        _Block(type="web_search_tool_result", content=[
            {"title": "Nyheter", "url": "https://acme.no/nyheter"}
        ]),
        _Block(type="text", text="Sammendrag."),
    ]
    monkeypatch.setattr(module, "client", _mock_client(blocks))

    _, sources = await module.research("annonse")
    assert len(sources) == 2
    assert sources[0]["query"] == "Acme tech stack"
    assert sources[1]["query"] == "Acme nyheter 2025"


async def test_blokker_uten_text_ignoreres_i_output(monkeypatch):
    blocks = [
        _Block(type="server_tool_use", input={"query": "q"}),
        _Block(type="text", text="Faktasetning."),
    ]
    monkeypatch.setattr(module, "client", _mock_client(blocks))

    text, _ = await module.research("annonse")
    assert text == "Faktasetning."
