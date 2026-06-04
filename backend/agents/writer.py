"""
Agent: Writer
Produserer en søknadsdisposisjon – ikke en ferdig tekst.
"""

from utils.llm import llm

SYSTEM = """
Du er en erfaren norsk karriereveileder.

Du skriver IKKE en ferdig søknadstekst. Du lager en disposisjon – en konkret veiledning som hjelper kandidaten å skrive sin egen autentiske søknad.

Regler:
- Bruk kun erfaringer og fakta som faktisk finnes i CV og match-analysen. Dikt ikke opp noe.
- Navngi spesifikke prosjekter, roller og arbeidsgivere fra CV der det er mulig.
- Skriv råd og pekere – ikke ferdige setninger kandidaten skal copy-paste.
- Vær konkret og direkte. Ingen fyller, ingen klisjeer.
- Svar på norsk.
"""


async def writer(
    krav: str,
    research: str,
    match: str,
    extra_context: str = "",
) -> str:
    extra_section = (
        f"\nTilleggsinformasjon kandidaten har oppgitt:\n{extra_context}\n"
        if extra_context
        else ""
    )
    prompt = f"""
Lag en søknadsdisposisjon for kandidaten basert på analysen under.

Krav fra stillingsannonsen:
{krav}

Research om arbeidsgiver:
{research}

Match-analyse (styrker, gap, anbefalt posisjonering):
{match}
{extra_section}

---

Lever disposisjonen i dette formatet:

## Åpning
Hvilken konkret erfaring eller prestasjon å åpne med, og hvorfor denne treffer stillingen best. Vær spesifikk – navngi prosjekt, rolle eller situasjon fra CV.

## Nøkkelpunkter å dekke
For hvert av de viktigste kravene: hvilken CV-erfaring som treffer, og kort råd om vinkling.
Bruk formatet:
**[Krav]**
- Bruk: [Spesifikk erfaring fra CV]
- Vinkling: [Råd om hvordan presentere det]

Ta med 2–4 punkter.

## Gap å adressere
For hvert gap fra match-analysen: et konkret forslag til ærlig, ikke-defensiv formulering. Ikke skriv setningen for dem – beskriv tilnærmingen.

## Avslutning
Hva avslutningen bør inneholde konkret i denne konteksten. Unngå generiske råd.

## Unngå
2–3 konkrete ting som ville svekket søknaden i denne spesifikke konteksten.
"""
    return await llm(SYSTEM, prompt, max_tokens=1500)
