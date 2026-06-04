# Jobbsøker-agent

Multi-agent system som analyserer en stillingsannonse og CV, og produserer en strukturert søknadsdisposisjon. Pipelinen er dynamisk — en orchestrator-agent vurderer kandidatens match og bestemmer hvilke steg som er nødvendige.

## Arkitektur

React-frontend kommuniserer med en FastAPI-backend via Server-Sent Events (SSE). Spesialiserte Claude-agenter kjører i sekvens og delvis parallelt. Orchestratoren gjør pipelinen adaptiv basert på matchkvalitet.

```
Input: Stillingsannonse + CV (tekst eller PDF)
    ↓
FastAPI /analyze
    ├── Kravleser + Research      (parallelt)
    │     Kravleser:  trekker ut krav og implisitte signaler
    │     Research:   websøk etter selskapsinfo, kultur, tech-stack
    ├── Match          – kobler krav med kandidatens CV
    ├── Orchestrator   – vurderer fit og bestemmer pipeline-strategi:
    │     · "weak"   → advar bruker, vent på bekreftelse før videre
    │     · "strong" → hopp over GapDetector
    ├── GapDetector    – stiller 0–3 oppfølgingsspørsmål (hoppes over ved sterk match)
    ├── Writer + InterviewPrep    (parallelt)
    │     Writer:        lager søknadsdisposisjon
    │     InterviewPrep: lager intervjuforberedelse
    └── Validator      – faktasjekker Writer-output mot CV og research
```

Resultater streames til frontend fortløpende via SSE.

## Agenter

| Agent         | Ansvar                                                                   |
|---------------|--------------------------------------------------------------------------|
| Kravleser     | Eksplisitte krav + implisitte signaler fra annonsen                      |
| Research      | Selskapsinfo, kultur, tech-stack og nyheter via websøk                   |
| Match         | Sterke matcher, gap og anbefalt posisjonering (brukes internt av Writer) |
| Orchestrator  | Vurderer fit-nivå og bestemmer dynamisk pipeline-strategi                |
| GapDetector   | Stiller inntil 3 oppfølgingsspørsmål der CV har hull                     |
| Writer        | Søknadsdisposisjon: åpning, nøkkelpunkter, gap, avslutning               |
| InterviewPrep | Sannsynlige spørsmål, svar-strategi og spørsmål å stille intervjuer      |
| Validator     | Faktasjekker Writer-output — flaggerer påstander uforankret i CV         |

## Agentiske mønstre

**Dynamisk pipeline (Orchestrator)**
Etter Match vurderer Orchestratoren kandidatens fit og justerer pipelinen:
- Svak match → pauser og ber brukeren bekrefte før analysen fortsetter
- Sterk match → hopper over GapDetector

**Faktaforankring (Validator)**
Writer og InterviewPrep kjøres parallelt. Deretter faktasjekker Validator Writer-utkastet mot CV og research — flagger påstander som ikke kan spores til kildematerialet. Brukeren ser funnene under disposisjonen.

**Human-in-the-loop (GapDetector + FitWarning)**
GapDetector stiller målrettede oppfølgingsspørsmål der CV har hull. Ved svak match vises en advarsel med valget om å fortsette eller avbryte.

## Output

Over disposisjonen vises **Anbefalt vinkling** — én setning om hvordan kandidaten bør posisjonere seg.

Under disposisjonen er to sammenleggbare seksjoner:
- **Intervjuforberedelse** — spørsmål og svar-strategi
- **Søkelogg** — websøk Research-agenten utførte

## Oppsett

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # legg inn ANTHROPIC_API_KEY
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Frontend kjører på `http://localhost:5173`, backend på `http://localhost:8000`.

## Testing

26 tester som dekker parsing, input-validering og pipeline-orkestrering.
LLM-kall mockes, så hele suiten kjører på under ett sekund uten API-kost.

```bash
cd backend
pytest
```

- **Unit:** GapDetector-parsing, Orchestrator-fallback, input-validatorer
- **Endepunkt:** PDF-opplasting (filtype, størrelse, korrupt fil)
- **Integrasjon:** hele `/analyze`-flyten — event-sekvens, adaptiv pipeline,
  guardrails, og de blokkerende human-in-the-loop-grenene (svar via `/answer`)

AI-*kvalitet* (relevans, faktuell forankring) hører hjemme i en egen
eval-suite — bevisst utenfor denne deterministiske testpakken.

## CV-input

CV kan limes inn som tekst eller lastes opp som PDF (tekst-basert PDF — ikke skannede bilder).

## Tech-stack

| Del      | Teknologi                                     |
|----------|-----------------------------------------------|
| Backend  | Python, FastAPI, Anthropic Claude API         |
| Frontend | React 19, TypeScript, Vite                    |
| Streaming| Server-Sent Events (SSE)                      |
| PDF      | PyMuPDF                                       |
| LLM      | Claude Haiku 4.5                              |
