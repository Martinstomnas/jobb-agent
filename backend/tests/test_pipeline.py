"""
Integrasjonstest av /analyze-pipelinen. Alle agenter mockes, så vi verifiserer
selve orkestreringen og SSE-event-sekvensen uten å bruke API-kreditter.
"""

import json
from unittest.mock import AsyncMock

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
    monkeypatch.setattr(main, "critic", AsyncMock(return_value="KRITIKK"))
    monkeypatch.setattr(main, "writer_revise", AsyncMock(return_value="REVIDERT"))


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
        "critic_rounds": 1,
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
    assert ("Critic", "done") in agents_seen
    assert events[-1]["agent"] == "FERDIG"

    # Writer-output skal være den reviderte versjonen, ikke utkastet.
    writer_done = next(e for e in events if e["agent"] == "Writer" and e["status"] == "done")
    assert writer_done["content"] == "REVIDERT"

    # Match skal trekke ut "Anbefalt vinkling".
    match_done = next(e for e in events if e["agent"] == "Match" and e["status"] == "done")
    assert "Vinkle slik." in match_done["content"]


def test_strong_match_hopper_over_gap_detector(monkeypatch):
    plan = {
        "fit_level": "strong",
        "fit_summary": "Sterk match.",
        "skip_gap_detector": True,
        "critic_rounds": 1,
    }
    _patch_agents(monkeypatch, plan=plan)

    with TestClient(app) as client:
        res = client.post("/analyze", json={"job_posting": "annonse", "cv": "cv"})
        events = _events(res.text)

    # GapDetector skal ikke ha kjørt i det hele tatt.
    assert main.gap_detector.await_count == 0
    assert not any(e["agent"] == "GapDetector" for e in events)
    assert events[-1]["agent"] == "FERDIG"


def test_critic_rounds_clamp(monkeypatch):
    # Orchestrator returnerer ugyldig høyt tall — guardrailen skal begrense til 2.
    # Bruker "medium" så pipelinen ikke blokkerer på bekreftelse.
    plan = {
        "fit_level": "medium",
        "fit_summary": "Grei.",
        "skip_gap_detector": False,
        "critic_rounds": 99,
    }
    _patch_agents(monkeypatch, plan=plan)

    with TestClient(app) as client:
        res = client.post("/analyze", json={"job_posting": "annonse", "cv": "cv"})
        events = _events(res.text)

    # critic skal ha kjørt maks 2 ganger til tross for critic_rounds=99.
    assert main.critic.await_count == 2
    assert events[-1]["agent"] == "FERDIG"
