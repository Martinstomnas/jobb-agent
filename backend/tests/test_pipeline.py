"""
Integrasjonstest av /analyze-pipelinen. Alle agenter mockes, så vi verifiserer
selve orkestreringen og SSE-event-sekvensen uten å bruke API-kreditter.
"""

import asyncio
import json
from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient

import main
from main import app


def _patch_agents(monkeypatch, *, plan):
    """Mocker alle agentene main kaller, med en gitt orchestrator-plan."""
    monkeypatch.setattr(main, "kravleser", AsyncMock(return_value="KRAV"))
    monkeypatch.setattr(
        main, "research", AsyncMock(return_value=("RESEARCH", [{"query": "q", "results": []}]))
    )
    monkeypatch.setattr(
        main, "match", AsyncMock(return_value="## Anbefalt vinkling\nVinkle slik.\n")
    )
    monkeypatch.setattr(main, "orchestrator", AsyncMock(return_value=plan))
    monkeypatch.setattr(main, "gap_detector", AsyncMock(return_value=[]))
    monkeypatch.setattr(main, "writer", AsyncMock(return_value="UTKAST"))
    monkeypatch.setattr(main, "interview_prep", AsyncMock(return_value="INTERVJU"))
    monkeypatch.setattr(main, "validator", AsyncMock(return_value="Ingen avvik funnet."))


def _events(response_text: str) -> list[dict]:
    out = []
    for line in response_text.splitlines():
        if line.startswith("data:"):
            raw = line[5:].strip()
            if raw:
                out.append(json.loads(raw))
    return out


def test_happy_path_medium_match(monkeypatch):
    plan = {
        "fit_level": "medium",
        "fit_summary": "Grei match.",
        "skip_gap_detector": False,
    }
    _patch_agents(monkeypatch, plan=plan)

    with TestClient(app) as client:
        res = client.post("/analyze", json={"job_posting": "annonse", "cv": "cv"})
        assert res.status_code == 200
        events = _events(res.text)

    agents_seen = {(e["agent"], e["status"]) for e in events}
    # Kjernesekvensen er til stede.
    assert ("Kravleser", "done") in agents_seen
    assert ("Research", "done") in agents_seen
    assert ("Match", "done") in agents_seen
    assert ("Orchestrator", "done") in agents_seen
    assert ("Writer", "done") in agents_seen
    assert ("InterviewPrep", "done") in agents_seen
    assert ("Validator", "done") in agents_seen
    assert events[-1]["agent"] == "FERDIG"

    # Writer-output skal være direkte fra Writer, ikke revidert.
    writer_done = next(e for e in events if e["agent"] == "Writer" and e["status"] == "done")
    assert writer_done["content"] == "UTKAST"

    # Match skal trekke ut "Anbefalt vinkling".
    match_done = next(e for e in events if e["agent"] == "Match" and e["status"] == "done")
    assert "Vinkle slik." in match_done["content"]


def test_match_vinkling_robust_mot_omformulert_overskrift(monkeypatch):
    plan = {"fit_level": "medium", "fit_summary": "", "skip_gap_detector": False}
    _patch_agents(monkeypatch, plan=plan)
    monkeypatch.setattr(
        main,
        "match",
        AsyncMock(
            return_value="## Sterke kort\n- Noe bra.\n\n## Anbefalt posisjonering:\nVinkle annerledes.\n"
        ),
    )

    with TestClient(app) as client:
        res = client.post("/analyze", json={"job_posting": "annonse", "cv": "cv"})
        events = _events(res.text)

    match_done = next(e for e in events if e["agent"] == "Match" and e["status"] == "done")
    assert "Vinkle annerledes." in match_done["content"]


def test_validator_utloser_regenerering_ved_funn(monkeypatch):
    plan = {"fit_level": "medium", "fit_summary": "", "skip_gap_detector": False}
    _patch_agents(monkeypatch, plan=plan)
    monkeypatch.setattr(
        main,
        "validator",
        AsyncMock(side_effect=["- Påstand ikke funnet i CV.", "Ingen avvik funnet."]),
    )
    monkeypatch.setattr(main, "writer", AsyncMock(side_effect=["UTKAST_V1", "UTKAST_V2"]))

    with TestClient(app) as client:
        res = client.post("/analyze", json={"job_posting": "annonse", "cv": "cv"})
        events = _events(res.text)

    statuses = [(e["agent"], e["status"]) for e in events]
    assert ("Validator", "issues") in statuses
    assert ("Writer", "running") in statuses[statuses.index(("Validator", "issues")):], \
        "Writer skal restartes etter validator-funn"
    assert main.writer.await_count == 2
    assert main.validator.await_count == 2
    writer_done_events = [e for e in events if e["agent"] == "Writer" and e["status"] == "done"]
    assert writer_done_events[-1]["content"] == "UTKAST_V2"
    validator_done = next(e for e in events if e["agent"] == "Validator" and e["status"] == "done")
    assert "Ingen avvik" in validator_done["content"]


def test_strong_match_hopper_over_gap_detector(monkeypatch):
    plan = {
        "fit_level": "strong",
        "fit_summary": "Sterk match.",
        "skip_gap_detector": True,
    }
    _patch_agents(monkeypatch, plan=plan)

    with TestClient(app) as client:
        res = client.post("/analyze", json={"job_posting": "annonse", "cv": "cv"})
        events = _events(res.text)

    # GapDetector skal ikke ha kjørt i det hele tatt.
    assert main.gap_detector.await_count == 0
    assert not any(e["agent"] == "GapDetector" for e in events)
    assert events[-1]["agent"] == "FERDIG"


# --- Human-in-the-loop: blokkerende grener ---------------------------------
#
# Disse grenene venter på et brukersvar via /answer mens SSE-strømmen står åpen.
# httpx' ASGITransport buffrer responsen, så vi kan ikke lese strømmen event for
# event mens pipelinen blokkerer. I stedet kjører vi to samtidige tasks:
#   - consume(): poster /analyze og samler alle eventene
#   - drive():   oppdager sesjonen i _answer_queues og poster svar via /answer
# Svaret går altså gjennom det ekte endepunktet, og pipelinen låses opp slik at
# consume() til slutt fullfører.


def _parse_events(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        if line.startswith("data:"):
            raw = line[5:].strip()
            if raw:
                out.append(json.loads(raw))
    return out


async def _stream_with_answers(payload: dict, answers: list[str]) -> list[dict]:
    events: list[dict] = []

    async def consume():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post("/analyze", json=payload)
            events.extend(_parse_events(res.text))

    async def drive():
        pending = list(answers)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            while pending:
                await asyncio.sleep(0.01)
                for sid in list(main._answer_queues.keys()):
                    if pending:
                        await client.post(
                            f"/answer/{sid}", json={"answer": pending.pop(0)}
                        )
                        break

    await asyncio.gather(consume(), drive())
    return events


async def test_gap_svar_flyter_videre_til_writer(monkeypatch):
    plan = {
        "fit_level": "medium",
        "fit_summary": "",
        "skip_gap_detector": False,
    }
    _patch_agents(monkeypatch, plan=plan)
    monkeypatch.setattr(
        main, "gap_detector", AsyncMock(return_value=["Erfaring med energi?"])
    )

    events = await asyncio.wait_for(
        _stream_with_answers(
            {"job_posting": "a", "cv": "c"}, answers=["Ja, tre år i Equinor"]
        ),
        timeout=10,
    )

    # Svaret kvitteres i strømmen ...
    answered = [
        e for e in events
        if e["agent"] == "GapDetector" and e["status"] == "answered"
    ]
    assert any("Equinor" in e["content"] for e in answered)
    # ... og sendes videre som extra_context til Writer.
    assert "Equinor" in main.writer.await_args.kwargs["extra_context"]
    assert events[-1]["agent"] == "FERDIG"


async def test_weak_match_fortsett_kjorer_videre(monkeypatch):
    plan = {
        "fit_level": "weak",
        "fit_summary": "Svak match.",
        "skip_gap_detector": False,
    }
    _patch_agents(monkeypatch, plan=plan)

    events = await asyncio.wait_for(
        _stream_with_answers({"job_posting": "a", "cv": "c"}, answers=["fortsett"]),
        timeout=10,
    )

    assert any(
        e["agent"] == "Orchestrator" and e["status"] == "warning" for e in events
    )
    # "fortsett" -> pipelinen kjører videre til Writer.
    assert main.writer.await_count == 1
    assert events[-1]["agent"] == "FERDIG"


async def test_weak_match_avbryt_stopper_pipelinen(monkeypatch):
    plan = {
        "fit_level": "weak",
        "fit_summary": "Svak match.",
        "skip_gap_detector": False,
    }
    _patch_agents(monkeypatch, plan=plan)

    events = await asyncio.wait_for(
        _stream_with_answers({"job_posting": "a", "cv": "c"}, answers=["avbryt"]),
        timeout=10,
    )

    assert any(
        e["agent"] == "Orchestrator" and e["status"] == "warning" for e in events
    )
    # "avbryt" -> Writer skal aldri kjøre.
    assert main.writer.await_count == 0
    assert events[-1]["agent"] == "FERDIG"
