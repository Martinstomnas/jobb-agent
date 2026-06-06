# Jobbsøker-agent

Multi-agent system som analyserer en stillingsannonse og CV, og produserer en strukturert søknadsdisposisjon. Pipelinen er dynamisk — Match-agenten vurderer kandidatens fit og bestemmer hvilke steg som er nødvendige.

<img width="1350" height="693" alt="jobb-agent" src="https://github.com/user-attachments/assets/9d14a157-dd03-4082-a333-f1875fb36f8b" />

## Arkitektur

React-frontend kommuniserer med en FastAPI-backend via Server-Sent Events (SSE). Spesialiserte Claude-agenter kjører i sekvens og delvis parallelt. Match-agenten gjør pipelinen adaptiv basert på matchkvalitet.

```
Input: Stillingsannonse + CV (tekst eller PDF)
    ↓
FastAPI /analyze
    ├── JobPostingAnalyzer + Research      (parallelt)
    │     JobPostingAnalyzer:  trekker ut krav og implisitte signaler
    │     Research:   websøk etter selskapsinfo, kultur, tech-stack
    ├── Match          – kobler krav med kandidatens CV og vurderer fit:
    │     · "weak"   → advar bruker, vent på bekreftelse før videre
    ├── GapDetector    – stiller 0–3 oppfølgingsspørsmål (hoppes over ved sterk match)
    ├── Writer + InterviewPrep    (parallelt)
    │     Writer:        lager søknadsdisposisjon
    │     InterviewPrep: lager intervjuforberedelse
    └── Validator      – faktasjekker Writer-output; funn utløser regenerering (maks 1 gang)
```

Resultater streames til frontend fortløpende via SSE.

## Agenter

| Agent              | Ansvar                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| JobPostingAnalyzer | Eksplisitte krav + implisitte signaler fra annonsen                                                     |
| Research           | Selskapsinfo, kultur, tech-stack og nyheter via websøk                                                  |
| Match              | Sterke matcher, gap og anbefalt posisjonering — vurderer fit-nivå og kan pause pipelinen ved svak match |
| GapDetector        | Stiller inntil 3 oppfølgingsspørsmål der CV har hull                                                    |
| Writer             | Søknadsdisposisjon: åpning, nøkkelpunkter, gap, avslutning, unngå-liste                                 |
| InterviewPrep      | Sannsynlige spørsmål, svar-strategi og spørsmål å stille intervjuer                                     |
| Validator          | Faktasjekker Writer-output — funn sendes tilbake til Writer for revisjon                                |

## Agentiske mønstre

**Dynamisk pipeline (Match)**
Match-agenten produserer analyse og fit-vurdering i ett LLM-kall og justerer pipelinen deretter:

- Svak match → pauser og ber brukeren bekrefte før analysen fortsetter

**Faktaforankring (Validator)**
Writer og InterviewPrep kjøres parallelt. Deretter faktasjekker Validator Writer-utkastet mot CV, research og svar fra GapDetector. Hvis påstander ikke kan spores til kildematerialet, regenererer Writer utkastet stille i bakgrunnen — brukeren ser aldri mellomversjonen. Validator kjøres én gang til på det reviderte utkastet, og disposisjonen vises først når løkken er ferdig. Maks én regenereringssyklus.

**Human-in-the-loop (GapDetector + FitWarning)**
GapDetector stiller målrettede oppfølgingsspørsmål der CV har hull. Ved svak match vises en advarsel med valget om å fortsette eller avbryte.

## Output

Output er delt i to faner:

**Resultat**

- **Anbefalt vinkling**
- **Søknadsdisposisjon**
- **Intervjuforberedelse**

**Analyse** — for kvalitetssikring og etterprøvbarhet

- **Faktasjekk** — tydelig grønt/oransje statusbanner; funn vises som punkter. Fanen får et !-merke hvis det er avvik å sjekke.
- **Kravanalyse** — eksplisitte krav, implisitte signaler og nøkkelord fra JobPostingAnalyzer
- **Match-analyse** — sterke kort, gap og anbefalt vinkling fra Match
- **Selskapsresearch** — Alle brukte URL-er listet

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

**Backend** — 51 tester. LLM-kall mockes, suiten kjører på under ett sekund uten API-kost.

```bash
cd backend
pytest
```

- **Unit:** GapDetector-parsing, Orchestrator-fallback, input-validatorer
- **Agent:** alle agenter (JobPostingAnalyzer, Writer, InterviewPrep, Validator, Research) — prompt-innhold, parametere og returverdier
- **Endepunkt:** PDF-opplasting (filtype, størrelse, korrupt fil)
- **Integrasjon:** hele `/analyze`-flyten — event-sekvens, adaptiv pipeline,
  guardrails, og de blokkerende human-in-the-loop-grenene (svar via `/answer`)

**Frontend** — 18 tester med Vitest + React Testing Library.

```bash
cd frontend
npm test
```

- **InputForm:** innsending blokkert på tomme felt, tilleggsinfo kombineres i CV, deaktivert under kjøring
- **FitWarning:** viser oppsummering, poster "avbryt"/"fortsett" til riktig endepunkt
- **FollowUpQuestion:** send-knapp deaktivert på tom input, poster svar og hopp-over
- **AgentPipeline:** agentnavn, fremgangsteller, CSS-klasser og statusikonet per status

## CV-input

CV kan limes inn som tekst eller lastes opp som PDF (tekst-basert PDF — ikke skannede bilder).

## Tech-stack

| Del       | Teknologi                             |
| --------- | ------------------------------------- |
| Backend   | Python, FastAPI, Anthropic Claude API |
| Frontend  | React 19, TypeScript, Vite            |
| Streaming | Server-Sent Events (SSE)              |
| PDF       | PyMuPDF                               |
| LLM       | Claude Haiku 4.5                      |
