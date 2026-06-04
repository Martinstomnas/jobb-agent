"""
FastAPI backend – tar imot input fra React-frontend
og streamer agentoppdateringer via SSE.
"""

import asyncio
import json
import logging
import re
import time
import uuid
from contextlib import asynccontextmanager
import fitz  # pymupdf
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from agents.kravleser import kravleser
from agents.research import research
from agents.match import match
from agents.gap_detector import gap_detector
from agents.writer import writer
from agents.validator import validator
from agents.orchestrator import orchestrator
from agents.interview_prep import interview_prep

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

# session_id -> asyncio.Queue som Writer venter på svar fra
_answer_queues: dict[str, asyncio.Queue] = {}
_session_created: dict[str, float] = {}
_SESSION_TTL = 600  # sekunder før en hengende sesjon ryddes opp


async def _cleanup_stale_sessions() -> None:
    while True:
        await asyncio.sleep(60)
        cutoff = time.time() - _SESSION_TTL
        stale = [sid for sid, t in list(_session_created.items()) if t < cutoff]
        for sid in stale:
            _answer_queues.pop(sid, None)
            _session_created.pop(sid, None)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_cleanup_stale_sessions())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def event(agent: str, status: str, content: str = "", **extra):
    """Lager en SSE-melding."""
    payload = {"agent": agent, "status": status, "content": content}
    payload.update(extra)
    return {"data": json.dumps(payload)}


_MAX_PDF_BYTES = 5_000_000  # 5 MB


@app.post("/extract-pdf")
@limiter.limit("20/minute")
async def extract_pdf(request: Request, file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Kun PDF-filer støttes")
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF er for stor (maks 5 MB)")
    chunks: list[bytes] = []
    size = 0
    async for chunk in file:
        size += len(chunk)
        if size > _MAX_PDF_BYTES:
            raise HTTPException(status_code=413, detail="PDF er for stor (maks 5 MB)")
        chunks.append(chunk)
    data = b"".join(chunks)
    if not data:
        raise HTTPException(status_code=400, detail="Tom fil")
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=422, detail="Kunne ikke lese PDF-filen")
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
@limiter.limit("5/minute")
async def analyze(request: Request, input: JobInput):
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
            _sections = re.findall(r"##[^\n]*\n(.*?)(?=\n##|\Z)", match_result, re.DOTALL)
            vinkling = _sections[-1].strip() if _sections else ""
            yield event("Match", "done", vinkling, full_match=match_result)

            # Orchestrator: bestem pipeline-strategi
            active.add("Orchestrator")
            yield event("Orchestrator", "running")
            plan = await orchestrator(krav_result, match_result)
            active.discard("Orchestrator")
            yield event(
                "Orchestrator",
                "done",
                plan.get("fit_summary", ""),
                fit_level=plan.get("fit_level"),
                skip_gap_detector=plan.get("skip_gap_detector"),
            )

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
                yield event("GapDetector", "running")
                questions = await gap_detector(research_text, input.cv, krav_result)
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
                if not questions:
                    yield event("GapDetector", "done", "Ingen gap å avklare")
                active.discard("GapDetector")
                extra_context = "\n".join(collected_answers)

            # Writer + InterviewPrep parallelt
            active.update({"Writer", "InterviewPrep"})
            yield event("Writer", "running")
            yield event("InterviewPrep", "running")

            writer_result, interview_result = await asyncio.gather(
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
            yield event("Writer", "done", writer_result)

            # Validator: faktasjekk Writer-output — regenerer writer ved funn (maks 1 gang)
            draft = writer_result
            for _attempt in range(2):
                active.add("Validator")
                yield event("Validator", "running")
                validation = await validator(draft, input.cv, krav_result, research_text)
                active.discard("Validator")

                has_issues = "ingen avvik" not in validation.lower()
                if not has_issues or _attempt == 1:
                    yield event("Validator", "done", validation)
                    break

                yield event("Validator", "issues", validation)
                active.add("Writer")
                yield event("Writer", "running")
                draft = await writer(
                    krav_result,
                    research_text,
                    match_result,
                    extra_context=extra_context,
                    validation_issues=validation,
                )
                active.discard("Writer")
                yield event("Writer", "done", draft)

            yield event("FERDIG", "done")

        except Exception:
            logger.exception("Uventet feil i stream-orkestrering (session=%s)", session_id)
            for agent in list(active):
                yield event(agent, "error", "En uventet feil oppstod. Prøv igjen.")
            yield event("FERDIG", "done")
        finally:
            _answer_queues.pop(session_id, None)
            _session_created.pop(session_id, None)

    return EventSourceResponse(stream())


