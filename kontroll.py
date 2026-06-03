"""
Agent 5: Kontroll
Siste stopp. Sjekker at søknaden ikke dikter opp erfaring,
og merker påstander som ikke er forankret i research-dataene.
"""

from utils.llm import llm

SYSTEM = """
Du er en kritisk kvalitetskontrollør. Din jobb er å beskytte kandidaten mot
å sende inn en søknad som overdriver eller dikter opp erfaring.

Du er ikke negativ – du er presis. Du skiller mellom:
- Fakta: direkte støttet av CV
- Rimelig slutning: logisk utledet fra kjent erfaring
- Usikker påstand: ikke direkte støttet – bør verifiseres eller modereres
- Rød flagg: tydelig overdrivelse eller noe som ikke stemmer

Svar på norsk.
"""


async def kontroll(writer_output: str, research: str) -> str:
    prompt = f"""
Her er søknadsteksten som skal kvalitetssikres:

{writer_output}

---

Her er de faktiske dataene vi har om kandidaten fra CV:

{research}

---

Gjør en kvalitetsjekk:

## ✅ Verifiserte påstander
(påstander direkte støttet av data)

## ⚠️ Usikre påstander
(påstander som ikke er direkte støttet – foreslå moderering)

## 🚩 Røde flagg
(noe som bør fjernes eller endres før innsending)

## Revidert søknadstekst
Lever den endelige, verifiserte versjonen av søknadsteksten med usikre
påstander moderert. Behold pitchen og intervjuforberedelsen uendret.
"""
    return await llm(SYSTEM, prompt, max_tokens=2500)
