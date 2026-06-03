# Jobbsøker-agent

Multi-agent system som analyserer en stillingsannonse og CV, og produserer en strukturert søknadsdisposisjon, intervjuforberedelse og match-analyse.

## Arkitektur

React-frontend kommuniserer med en FastAPI-backend via Server-Sent Events (SSE). Syv spesialiserte Claude-agenter kjører i sekvens og delvis parallelt.

```
Input: Stillingsannonse + CV (tekst eller PDF)
    ↓
FastAPI-backend (/analyze)
    ├── Agent 1: Kravleser      – trekker ut krav og implisitte signaler
    ├── Agent 2: Research       – websøk etter selskapsinfo, kultur, tech-stack
    │   (parallelt med Kravleser)
    ├── Agent 3: Match          – kobler krav med kandidatens CV
    ├── Agent 4: GapDetector    – identifiserer gap, stiller 0–3 oppfølgingsspørsmål
    ├── Agent 5: Writer         – lager søknadsdisposisjon (ikke ferdig tekst)
    ├── Agent 6: InterviewPrep  – lager intervjuforberedelse
    │   (parallelt med Writer)
    └── Agent 7: Kontroll       – validerer disposisjonen mot CV-data
```

Resultater streames til frontend fortløpende via SSE.

## Agenter

| Agent        | Ansvar                                                                 |
|--------------|------------------------------------------------------------------------|
| Kravleser    | Eksplisitte krav + implisitte signaler fra annonsen                    |
| Research     | Selskapsinfo, kultur, tech-stack og nyheter via websøk                 |
| Match        | Sterke matcher, gap og anbefalt posisjonering                          |
| GapDetector  | Stiller inntil 3 oppfølgingsspørsmål der CV har hull                   |
| Writer       | Strukturert søknadsdisposisjon: åpning, nøkkelpunkter, gap, avslutning |
| InterviewPrep| Sannsynlige spørsmål, svar-strategi og spørsmål å stille intervjuer    |
| Kontroll     | Validerer disposisjonen: [OK] / [Utdyp] / [Sjekk] per punkt           |

## Output

Primær output er **søknadsdisposisjonen** fra Writer — en konkret guide for hva kandidaten bør skrive, hvilke erfaringer å trekke frem og hvordan vinkle hvert punkt. Brukeren skriver sin egen søknad ut fra denne.

Under disposisjonen er fire sammenleggbare seksjoner:
- **Validering** — Kontroll-agentens gjennomgang av hvert punkt
- **Match-analyse** — styrker, gap og posisjonering
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

CV kan limes inn som tekst eller lastes opp som PDF (tekst-basert PDF — ikke skannede bilder). Et eget felt for ekstra informasjon (lenker, prosjekter, motivasjon) kombineres automatisk med CV-en.

## Tech-stack

| Del      | Teknologi                              |
|----------|----------------------------------------|
| Backend  | Python, FastAPI, Anthropic Claude API  |
| Frontend | React 19, Vite                         |
| Streaming| Server-Sent Events (SSE)               |
| PDF      | PyMuPDF                                |
| LLM      | Claude Haiku 4.5                       |
