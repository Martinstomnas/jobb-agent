// Dummy SSE-events for lokal utvikling — simulerer en full pipeline-kjøring.
// Hvert event har et valgfritt _delay (ms) som styrer hvor fort det dukker opp.

export interface DummyEvent {
  agent: string;
  status: string;
  content: string;
  _delay?: number;
  // ekstra felt som backend sender på spesifikke events
  sources?: { query: string; results: { title: string; url: string }[] }[];
  full_match?: string;
  fit_level?: string;
  skip_gap_detector?: boolean;
}

const KRAVLESER_OUTPUT = `**Eksplisitte krav:**
- 3+ års erfaring med Python og FastAPI
- Erfaring med PostgreSQL og databasedesign
- Kjennskap til Docker og CI/CD-pipelines
- God skriftlig kommunikasjon på norsk og engelsk

**Implisitte signaler:**
- Autonomi og eierskap til hele features
- Produktorientert tankegang, ikke bare teknisk utførelse
- Komfortabel med ambiguitet i en voksende startup
- Interesse for klima og bærekraft som bransjefokus`;

const RESEARCH_OUTPUT = `NordTech AS er et Oslo-basert klimatech-selskap grunnlagt i 2019. Selskapet utvikler SaaS-løsninger for energioptimalisering i næringsbygg og hadde i 2023 en omsetningsvekst på 80 %. Teamet er på ca. 35 ansatte med et erklært mål om å doble staben innen 2025.

**Teknologistakk** (basert på GitHub og stillingsannonser): Python-backend, React-frontend, PostgreSQL, Kubernetes på GCP. Aktiv open source-profil.

**Kultur:** Flat struktur, remote-friendly, sterkt fokus på bærekraft som kjerneverdi. Glassdoor-snitt 4,3/5 basert på 12 anmeldelser — positivt om faglig frihet, noe kritikk av prosessmodenhet.`;

const MATCH_FULL = `## Styrker
- **Python/FastAPI:** Kandidaten har 4 år med Python og brukte FastAPI i Equinor-prosjektet (2022–2023) — direkte treff på primærkravet.
- **PostgreSQL:** Databasearbeid dokumentert i to av tre siste roller. Schema-design for høy-last system hos Computas.
- **Startup-erfaring:** Jobbet i to tidligfase-selskaper, vant til autonomi og hurtig iterasjon.

## Gap
- **Docker/CI-CD:** Nevnt i CV, men kun som bruker — ingen selvstendig oppsett dokumentert.
- **Klimadomene:** Ingen direkte bransjekjennskap, men ingeniørbakgrunn er overførbar.

## Anbefalt vinkling
Posisjonér deg som en produktnær Python-utvikler med bevist evne til å levere i ambisiøse team — ikke som klimaekspert.`;

const WRITER_OUTPUT = `## Åpning
Start med Equinor-prosjektet (2022–2023): du bygde en FastAPI-tjeneste som håndterte tung last i produksjon. Dette treffer NordTechs primærkrav direkte og viser at du har skalert Python i virkeligheten — ikke bare hobbyprosjekter.

## Nøkkelpunkter å dekke

**Python og FastAPI**
- Bruk: Equinor-integrasjon, 2022–2023
- Vinkling: Beskriv omfang og produksjonsansvar, ikke bare teknologien

**PostgreSQL og databasedesign**
- Bruk: Computas-prosjektet, schema-design for høy-last
- Vinkling: Fremhev at du tok designbeslutninger, ikke bare skrev queries

**Startup-mentalitet**
- Bruk: To tidligfase-arbeidsgivere i CV
- Vinkling: Velg ett konkret eksempel på at du leverte en feature fra ide til produksjon uten håndholding

## Gap å adressere
**Docker/CI-CD:** Ikke prøv å overdrive. Si noe á la: *"Har brukt Docker i alle prosjekter og er komfortabel i etablerte pipelines — men har ikke satt opp CI fra scratch."*

## Avslutning
Koble avslutningen til NordTechs klimafokus — ikke som ekspertise, men som personlig motivasjon. Gjør det konkret: hvorfor energioptimalisering, ikke bare "bærekraft er viktig".

## Unngå
- Generiske påstander om "pasjon for teknologi"
- Å antyde klimaekspertise du ikke har
- Kopier av stillingsbeskrivelsen som egne ferdigheter`;

const INTERVIEW_OUTPUT = `## Sannsynlige spørsmål

**Teknisk**
1. *"Kan du beskrive en API du har designet fra scratch?"* — Bruk Equinor-prosjektet. Fokus på valgene du tok (autentisering, rate limiting, schema), ikke bare at det fungerte.
2. *"Hvordan håndterer du databasemigrasjoner i produksjon?"* — Vær ærlig om hva du har brukt (Alembic/Flyway) og hva du ville gjort annerledes.

**Kultur og fit**
3. *"Hva betyr autonomi i jobb for deg?"* — Gi et konkret eksempel, ikke en definisjon.
4. *"Hva tiltrekker deg til klimadomenet?"* — Vær spesifikk om NordTech, ikke generell om bærekraft.

## Spørsmål å stille intervjuer
- Hva er den viktigste tekniske utfordringen dere ser de neste 6 månedene?
- Hvordan ser onboarding ut for en ny backend-utvikler?
- Hva skiller junior fra senior i teamet deres?`;

const VALIDATOR_OUTPUT = `- **Docker/CI-CD:** Disposisjonen foreslår å nevne erfaring med å *sette opp* CI-pipelines, men CV-en dokumenterer kun brukererfaring — ikke selvstendig konfigurasjon. Unngå å fremheve dette som en styrke.
- Øvrige påstander er forankret i CV og research.`;

const RESEARCH_SOURCES = [
  {
    query: "NordTech AS Oslo klimatech",
    results: [
      { title: "NordTech AS – offisiell nettside", url: "https://nordtech.no" },
      { title: "NordTech henter 50 MNOK i Serie A – Shifter", url: "https://shifter.no/nordtech-serie-a" },
    ],
  },
  {
    query: "NordTech AS ansatte kultur tech stack",
    results: [
      { title: "NordTech – LinkedIn", url: "https://linkedin.com/company/nordtech-as" },
      { title: "NordTech anmeldelser – Glassdoor", url: "https://glassdoor.com/nordtech" },
    ],
  },
  {
    query: "NordTech AS GitHub open source",
    results: [
      { title: "nordtech-as – GitHub", url: "https://github.com/nordtech-as" },
    ],
  },
];

export const DUMMY_EVENTS: DummyEvent[] = [
  { agent: "Kravleser",    status: "running", content: "",              _delay: 0   },
  { agent: "Research",     status: "running", content: "",              _delay: 0   },
  { agent: "Kravleser",    status: "done",    content: KRAVLESER_OUTPUT, _delay: 900 },
  { agent: "Research",     status: "done",    content: RESEARCH_OUTPUT,  _delay: 400,
    sources: RESEARCH_SOURCES },
  { agent: "Match",        status: "running", content: "",              _delay: 0   },
  { agent: "Match",        status: "done",
    content: "Posisjonér deg som en produktnær Python-utvikler med bevist evne til å levere i ambisiøse team — ikke som klimaekspert.",
    full_match: MATCH_FULL,                                              _delay: 1100 },
  { agent: "Orchestrator", status: "running", content: "",              _delay: 0   },
  { agent: "Orchestrator", status: "done",
    content: "Sterk match — kandidaten dekker alle primærkrav og har relevant startup-erfaring.",
    fit_level: "strong", skip_gap_detector: true,                       _delay: 700  },
  { agent: "Writer",       status: "running", content: "",              _delay: 0   },
  { agent: "InterviewPrep",status: "running", content: "",              _delay: 0   },
  { agent: "InterviewPrep",status: "done",    content: INTERVIEW_OUTPUT, _delay: 1400 },
  { agent: "Writer",       status: "done",    content: WRITER_OUTPUT,    _delay: 600  },
  { agent: "Validator",    status: "running", content: "",              _delay: 0   },
  { agent: "Validator",    status: "done",    content: VALIDATOR_OUTPUT, _delay: 900  },
  { agent: "FERDIG",       status: "done",    content: "",              _delay: 0   },
];
