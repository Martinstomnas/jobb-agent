"""
FastAPI backend – tar imot input fra React-frontend
og streamer agentoppdateringer via SSE.
"""

import asyncio
import json
import re
import time
import uuid
import fitz  # pymupdf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from sse_starlette.sse import EventSourceResponse

from agents.kravleser import kravleser
from agents.research import research
from agents.match import match
from agents.gap_detector import gap_detector
from agents.writer import writer, writer_revise
from agents.critic import critic
from agents.orchestrator import orchestrator
from agents.interview_prep import interview_prep

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# session_id -> asyncio.Queue som Writer venter på svar fra
_answer_queues: dict[str, asyncio.Queue] = {}
_session_created: dict[str, float] = {}
_SESSION_TTL = 600  # sekunder før en hengende sesjon ryddes opp


class JobInput(BaseModel):
    job_posting: str
    cv: str

    @field_validator("job_posting")
    @classmethod
    def validate_job_posting(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Stillingsannonse kan ikke være tom")
        if len(v) > 10_000:
            raise ValueError("Stillingsannonse er for lang (maks 10 000 tegn)")
        return v

    @field_validator("cv")
    @classmethod
    def validate_cv(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("CV kan ikke være tom")
        if len(v) > 15_000:
            raise ValueError("CV er for lang (maks 15 000 tegn)")
        return v


class AnswerInput(BaseModel):
    answer: str



@app.on_event("startup")
async def startup():
    async def _cleanup_stale_sessions():
        while True:
            await asyncio.sleep(60)
            cutoff = time.time() - _SESSION_TTL
            stale = [sid for sid, t in list(_session_created.items()) if t < cutoff]
            for sid in stale:
                _answer_queues.pop(sid, None)
                _session_created.pop(sid, None)

    asyncio.create_task(_cleanup_stale_sessions())


def event(agent: str, status: str, content: str = "", **extra):
    """Lager en SSE-melding."""
    payload = {"agent": agent, "status": status, "content": content}
    payload.update(extra)
    return {"data": json.dumps(payload)}


@app.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Kun PDF-filer støttes")
    data = await file.read()
    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for page in doc:
        raw = page.get_text("text", sort=True)
        cleaned = re.sub(r"\n{3,}", "\n\n", raw).strip()
        if cleaned:
            pages.append(cleaned)
    text = "\n\n".join(pages)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Kunne ikke lese tekst fra PDF")
    return {"text": text}


@app.post("/answer/{session_id}")
async def submit_answer(session_id: str, body: AnswerInput):
    queue = _answer_queues.get(session_id)
    if queue is None:
        raise HTTPException(status_code=404, detail="Ukjent sesjon")
    await queue.put(body.answer)
    return {"ok": True}


@app.post("/analyze")
async def analyze(input: JobInput):
    session_id = str(uuid.uuid4())
    answer_queue: asyncio.Queue = asyncio.Queue()
    _answer_queues[session_id] = answer_queue
    _session_created[session_id] = time.time()

    async def stream():
        active: set[str] = set()

        try:
            # Kravleser + Research parallelt
            active.update({"Kravleser", "Research"})
            yield event("Kravleser", "running")
            yield event("Research", "running")

            krav_result, (research_text, research_sources) = await asyncio.gather(
                kravleser(input.job_posting),
                research(input.job_posting),
            )

            active.difference_update({"Kravleser", "Research"})
            yield event("Kravleser", "done", krav_result)
            yield event("Research", "done", research_text, sources=research_sources)

            # Match
            active.add("Match")
            yield event("Match", "running")
            match_result = await match(krav_result, research_text, input.cv)
            active.discard("Match")
            _vm = re.search(
                r"## Anbefalt vinkling\s*\n(.*?)(?=\n##|\Z)", match_result, re.DOTALL
            )
            vinkling = _vm.group(1).strip() if _vm else ""
            yield event("Match", "done", vinkling)

            # Orchestrator: bestem pipeline-strategi
            active.add("Orchestrator")
            yield event("Orchestrator", "running")
            plan = await orchestrator(krav_result, match_result)
            active.discard("Orchestrator")
            yield event("Orchestrator", "done", plan.get("fit_summary", ""))

            # Advar brukeren ved svak match og vent på bekreftelse
            if plan.get("fit_level") == "weak":
                yield event("Orchestrator", "warning", plan.get("fit_summary", ""), session_id=session_id)
                try:
                    confirmation = await asyncio.wait_for(answer_queue.get(), timeout=300)
                    if confirmation.strip().lower() == "avbryt":
                        yield event("FERDIG", "done")
                        return
                except asyncio.TimeoutError:
                    pass

            # Gap-detektor: hopp over ved sterk match
            extra_context = ""
            if not plan.get("skip_gap_detector"):
                active.add("GapDetector")
                questions = await gap_detector(research_text, input.cv)
                collected_answers = []
                for question in questions:
                    yield event("GapDetector", "question", question, session_id=session_id)
                    try:
                        answer = await asyncio.wait_for(answer_queue.get(), timeout=300)
                        yield event("GapDetector", "answered", answer)
                        if answer.strip():
                            collected_answers.append(answer)
                    except asyncio.TimeoutError:
                        yield event("GapDetector", "answered", "")
                active.discard("GapDetector")
                extra_context = "\n".join(collected_answers)

            # Writer + InterviewPrep parallelt
            active.update({"Writer", "InterviewPrep"})
            yield event("Writer", "running")
            yield event("InterviewPrep", "running")

            writer_draft, interview_result = await asyncio.gather(
                writer(
                    krav_result,
                    research_text,
                    match_result,
                    extra_context=extra_context,
                ),
                interview_prep(
                    krav_result,
                    research_text,
                    match_result,
                    extra_context=extra_context,
                ),
            )

            active.difference_update({"Writer", "InterviewPrep"})
            yield event("InterviewPrep", "done", interview_result)

            # Critic: antall runder bestemt av orchestrator
            critic_rounds = plan.get("critic_rounds", 1)
            writer_result = writer_draft
            for _ in range(critic_rounds):
                active.add("Critic")
                yield event("Critic", "running")
                critique = await critic(writer_result, krav_result, match_result, input.cv)
                writer_result = await writer_revise(writer_result, critique)
                active.discard("Critic")
                yield event("Critic", "done")

            yield event("Writer", "done", writer_result)
            yield event("FERDIG", "done")

        except Exception as e:
            err_msg = str(e) or "Ukjent feil"
            for agent in list(active):
                yield event(agent, "error", err_msg)
            yield event("FERDIG", "done")
        finally:
            _answer_queues.pop(session_id, None)
            _session_created.pop(session_id, None)

    return EventSourceResponse(stream())


