# Jobbsøker-agent

Multi-agent system som analyserer en stillingsannonse og CV, og produserer en strukturert søknadsdisposisjon med innebygd self-reflection, intervjuforberedelse og iterativ forbedring.

## Arkitektur

React-frontend kommuniserer med en FastAPI-backend via Server-Sent Events (SSE). Åtte spesialiserte Claude-agenter kjører i sekvens og delvis parallelt.

```
Input: Stillingsannonse + CV (tekst eller PDF)
    ↓
FastAPI-backend (/analyze)
    ├── Kravleser + Research   (parallelt)
    │     Kravleser:  trekker ut krav og implisitte signaler
    │     Research:   websøk etter selskapsinfo, kultur, tech-stack
    ├── Match          – kobler krav med kandidatens CV, anbefaler posisjonering
    ├── GapDetector    – stiller 0–3 oppfølgingsspørsmål der CV har hull
    ├── Writer + InterviewPrep  (parallelt)
    │     Writer:        lager søknadsdisposisjon (utkast)
    │     InterviewPrep: lager intervjuforberedelse
    ├── Critic         – evaluerer Writer-utkastet mot krav og match-analyse
    └── Writer revise  – forbedrer disposisjonen basert på kritikken

POST /refine  →  Refiner-agent reviderer disposisjonen på brukerens instruksjon
```

Resultater streames til frontend fortløpende via SSE.

## Agenter

| Agent         | Ansvar                                                                  |
|---------------|-------------------------------------------------------------------------|
| Kravleser     | Eksplisitte krav + implisitte signaler fra annonsen                     |
| Research      | Selskapsinfo, kultur, tech-stack og nyheter via websøk                  |
| Match         | Sterke matcher, gap og anbefalt posisjonering (brukes internt av Writer) |
| GapDetector   | Stiller inntil 3 oppfølgingsspørsmål der CV har hull                    |
| Writer        | Søknadsdisposisjon: åpning, nøkkelpunkter, gap, avslutning              |
| InterviewPrep | Sannsynlige spørsmål, svar-strategi og spørsmål å stille intervjuer     |
| Critic        | Evaluerer Writer-utkastet — identifiserer svakheter og mangler          |
| Refiner       | Reviderer disposisjonen basert på brukerens instruksjon (on-demand)     |

### Self-reflection-pattern

Writer og InterviewPrep kjøres parallelt. Deretter evaluerer Critic Writer-utkastet mot kravene og match-analysen. Writer reviderer basert på kritikken. Brukeren mottar kun den forbedrede versjonen.

## Output

Primær output er **søknadsdisposisjonen** — en konkret guide for hva kandidaten bør skrive, hvilke erfaringer å trekke frem og hvordan vinkle hvert punkt. Brukeren skriver sin egen søknad ut fra denne.

Over disposisjonen vises **Anbefalt vinkling** — én setning om hvordan kandidaten bør posisjonere seg.

Under disposisjonen er et **tekstfelt for iterativ forbedring**: brukeren kan skrive instrukser som "gjør åpningen kortere" eller "tonen er for formell", og Refiner-agenten oppdaterer disposisjonen. Flere runder støttes.

Sammenleggbare seksjoner:
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

## CV-input

CV kan limes inn som tekst eller lastes opp som PDF (tekst-basert PDF — ikke skannede bilder).

## Tech-stack

| Del      | Teknologi                              |
|----------|----------------------------------------|
| Backend  | Python, FastAPI, Anthropic Claude API  |
| Frontend | React 19, Vite                         |
| Streaming| Server-Sent Events (SSE)               |
| PDF      | PyMuPDF                                |
| LLM      | Claude Haiku 4.5                       |
