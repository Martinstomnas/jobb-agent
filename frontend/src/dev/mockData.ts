import type { ResearchSource } from "../types";

export const mockOutput = `## Åpning

Start med perioden hos Kartverket der du tok ansvar for brukerstøtte på dagtid — dette er den mest direkte erfaringen og setter tonen for resten.

## Nøkkelpunkter å dekke

**Teknisk brukerstøtte og feilsøking**
- Bruk:Brukerstøtte-rollen hos Kartverket
- Vinkling:Vektlegg bredden — hardware, software, brukerfeil — og at du systematiserte det, ikke bare løste det

**Serviceinnstilling overfor ikke-tekniske brukere**
- Bruk:Kundeserviceerfaring fra Delta og Europris
- Vinkling:Koble eksplisitt til IT-kontekst — tålmodighet og pedagogikk er like viktig i support som teknisk kunnskap

**Strukturert og metodisk arbeid**
- Bruk:Bachelor i IT, praksis hos Kartverket
- Vinkling:Vis at du jobber systematisk, ikke bare reaktivt

## Gap å adressere

**Mangler ITIL/CompTIA A+**: Ikke be om unnskyldning. Anerkjenn gapet, vis at du kjenner rammeverket fra studiet, og ha en konkret plan for sertifisering.

## Avslutning

Nevn noe spesifikt fra Sopra Sterias profil — konsulentmodellen eller kundeporteføljens bredde. Ikke generisk "gleder meg til å bidra".

## Unngå

Ikke list teknologier uten kontekst. Unngå "løsningsorientert" og "strukturert". Ikke overskrid 350 ord.`;

export const mockMatchOutput = `Fremstill deg som en raskt lærende med bevist brukerstøtteerfaring som mangler formell sertifisering — ikke som en junior uten erfaring.`;

export const mockResearchSources: ResearchSource[] = [
  {
    query: "Sopra Steria Norge IT-konsulent kultur verdier",
    results: [
      { title: "Om oss – Sopra Steria", url: "https://www.soprasteria.no/om-oss" },
      { title: "Jobbe hos oss – Sopra Steria", url: "https://www.soprasteria.no/karriere" },
      { title: "Sopra Steria årsrapport 2023", url: "https://www.soprasteria.no/investorer/arsrapport" },
    ],
  },
  {
    query: "Sopra Steria IT support helpdesk stilling krav",
    results: [
      { title: "Ledige stillinger – Sopra Steria", url: "https://www.soprasteria.no/karriere/ledige-stillinger" },
      { title: "IT Support Technician – Finn.no", url: "https://www.finn.no/job/fulltime/ad.html?finnkode=123456" },
    ],
  },
  {
    query: "ITIL CompTIA A+ sertifisering krav IT-support Norge",
    results: [
      { title: "CompTIA A+ sertifisering – CompTIA", url: "https://www.comptia.org/certifications/a" },
      { title: "ITIL Foundation – Axelos", url: "https://www.axelos.com/certifications/itil-service-management" },
    ],
  },
];

export const mockInterviewPrep = `**Sp 1: "Du har bachelor i IT, men ingen formell IT-support-sertifisering. Hvordan kompenserer du?"**

Svar-strategi: Ikke defensiv. Anerkjenn gapet, vis bevissthet og konkret plan.

**Sp 2: "Gi et eksempel på en gang du løste et teknisk problem for en ikke-teknisk bruker."**

Svar-strategi: Bruk Kartverket. Vær konkret på hva problemet var, hva du gjorde, og hva utfallet ble.

### Spørsmål å stille intervjuer

- Hvordan ser en typisk uke ut for en IT-support tekniker her?
- Hvilke systemer og ticketverktøy bruker dere internt?
- Hva er de vanligste henvendelsene support-teamet håndterer?`;
