"""De berichten aan het LLM: een vaste systeemprompt en per blok de vragen plus de gevonden cao-fragmenten."""

from ...wijzerbelonen.formulier.inspectie import Vraag
from ..zoeken import Fragment
from .blokken import Blok

SYSTEEM = """\
Je vult een vragenlijst over arbeidsvoorwaarden in op basis van fragmenten uit een Nederlandse cao.

Regels:
1. Gebruik ALLEEN de gegeven fragmenten. Verzin niets en vul niets in op basis van algemene kennis.
2. Elke ingevulde waarde heeft een onderbouwing: het pad van het veld, document, pagina, artikel en een LETTERLIJK
   citaat uit een fragment. Eén onderbouwing mag een heel blok velden dekken (bijv. pad "bedrag").
3. Staat iets niet in de fragmenten, laat het veld dan null en zet het pad in "niet_gevonden". "Niet gevonden" is
   iets anders dan "nee": kies "nee" alleen als de cao dat uitdrukkelijk zegt, met citaat.
4. Gebruik bij keuzes precies een van de toegestane waarden. Getallen zonder eenheid of procentteken (8 voor 8%),
   met een punt als decimaalteken. Datums als JJJJ-MM-DD.
5. Vul een vraag met "Alleen invullen als: ..." alleen in als die voorwaarde klopt; laat hem anders null.
6. Een bedragregel: kies eerst "soort" en vul dan alleen het bijbehorende deel in (vast_bedrag, percentage of tijd).
7. Herhaalbare blokken (lijsten): maak alleen rijen die echt in de cao staan, elk met een eigen onderbouwing.
"""


def blok_bericht(blok: Blok, vragen: list[Vraag], fragmenten: list[Fragment]) -> str:
    regels = [f"Blok: {blok.naam}"]
    if blok.toelichting:
        regels.append(blok.toelichting)
    regels += ["", "Vragen (pad: vraag):"]
    for v in vragen:
        regel = f"- {v.pad}: {v.vraag}"
        if v.eenheid:
            regel += f" [{v.eenheid}]"
        if v.opties:
            regel += " | keuzes: " + "; ".join(f"'{w}' = {label}" for w, label in v.opties)
        if v.toon_als:
            regel += f" | alleen als: {v.toon_als}"
        regels.append(regel)
    regels += ["", "Fragmenten uit de cao:"]
    if not fragmenten:
        regels.append("(geen fragmenten gevonden)")
    for i, f in enumerate(fragmenten, 1):
        kop = f"[F{i}] {f.document}, pagina {f.pagina}" + (f", {f.sectie}" if f.sectie else "")
        regels += [kop, f.tekst, ""]
    return "\n".join(regels)


def herstel_bericht(fouten: list[str]) -> str:
    return (
        "Je antwoord voldoet niet aan de vragenlijst:\n"
        + "\n".join(f"- {f}" for f in fouten)
        + "\n\nGeef een verbeterd antwoord volgens hetzelfde schema. Laat velden die je niet zeker weet null."
    )
