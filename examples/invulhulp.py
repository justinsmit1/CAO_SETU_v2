"""Invulhulp: welke vragen er per sectie zijn en hoe je ze invult in ``maak_upload.py``.

Draaien vanuit de projectmap:

    .venv\\Scripts\\python.exe examples\\invulhulp.py            # schrijft INVULHULP.md in de hoofdmap
    .venv\\Scripts\\python.exe examples\\invulhulp.py 9          # toont alleen sectie 09 Verlof op het scherm

Per vraag zie je de Nederlandse vraagtekst, de regel die je in ``maak_upload.py`` schrijft en de keuzes zoals je ze
typt (bijvoorbeeld ``JaNee.JA``).
"""

import datetime as dt
import sys
import typing
from enum import Enum
from pathlib import Path
from types import NoneType, UnionType

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from pydantic import BaseModel  # noqa: E402

from cao_setu_v2.formulier import Formulier  # noqa: E402
from cao_setu_v2.formulier.bouwstenen import Bedragregel  # noqa: E402

UITVOER = PROJECT / "INVULHULP.md"

# De naam waaronder een sectie in maak_upload.py bereikbaar is, bijv. f.algemeen
SECTIES = list(Formulier.model_fields)


def _kern(annotatie: object) -> tuple[object, str]:
    """``X | None`` → X; ``list[X]`` → (X, "lijst"); ``dict[K, X]`` → (X, "per K")."""
    soort = ""
    while True:
        oorsprong, args = typing.get_origin(annotatie), typing.get_args(annotatie)
        if oorsprong is list:
            annotatie, soort = args[0], "lijst"
        elif oorsprong is dict:
            annotatie, soort = args[1], f"per {args[0].__name__}"
        elif oorsprong in (typing.Union, UnionType) and NoneType in args:
            annotatie = next(a for a in args if a is not NoneType)
        else:
            return annotatie, soort


def _voorbeeld(t: object, eenheid: str | None) -> str:
    if isinstance(t, type):
        if issubclass(t, Enum):
            return f"{t.__name__}.{next(iter(t)).name}"
        if t is bool:
            return "True"
        if t is dt.date:
            return "dt.date(2026, 1, 1)"
        if t is dt.time:
            return "dt.time(22, 0)"
        if t in (int, float):
            return {"€": "1250", "%": "8", "uur": "40"}.get(eenheid or "", "10")
    return '"tekst"'


_UITGESCHREVEN: set[str] = set()  # rij-soorten die al een keer volledig zijn uitgeschreven


def _rij(t: type[BaseModel], diepte: int) -> list[str]:
    """De vragen van een rij-soort; een soort die al eerder voorkwam, verwijst terug."""
    if t.__name__ in _UITGESCHREVEN:
        return [f"{'  ' * diepte}- dezelfde vragen als bij `{t.__name__}` hierboven"]
    _UITGESCHREVEN.add(t.__name__)
    return _regels(t, t.__name__, diepte)


def _regels(model: type[BaseModel], pad: str, diepte: int) -> list[str]:
    uit = []
    for naam, info in model.model_fields.items():
        extra = info.json_schema_extra if isinstance(info.json_schema_extra, dict) else {}
        t, soort = _kern(info.annotation)
        vraag = (info.description or "").replace("|", "/").replace("\n", " ")
        if len(vraag) > 110:
            vraag = vraag[:107] + "…"
        binnen_rij = not pad.startswith("f.")  # binnen Rij(...) schrijf je naam=waarde
        veldpad = naam if binnen_rij else f"{pad}.{naam}"
        is_ = "=" if binnen_rij else " = "
        toon = extra.get("toon_als")
        voorwaarde = f" *(alleen als: {toon})*" if isinstance(toon, str) else (f" *(alleen als: {toon})*" if toon else "")
        inspring = "  " * diepte

        if isinstance(t, type) and issubclass(t, BaseModel):
            if t is Bedragregel:
                opties = extra.get("opties")
                toegestaan = f" Toegestaan: {', '.join(opties)}." if opties else ""
                uit.append(f"{inspring}- **{vraag}**{voorwaarde}  \n{inspring}  `{veldpad}{is_}Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan).{toegestaan}")
                continue
            if soort == "lijst":
                uit.append(f"{inspring}- **{vraag}**{voorwaarde}  \n{inspring}  `{veldpad}{is_}[{t.__name__}(...), {t.__name__}(...)]`: herhaalbaar; per rij:")
                uit += _rij(t, diepte + 1)
            elif soort:
                uit.append(f"{inspring}- **{vraag}**{voorwaarde}  \n{inspring}  `{veldpad}{is_}{{sleutel: {t.__name__}(...)}}` ({soort}); per sleutel:")
                uit += _rij(t, diepte + 1)
            elif extra:  # submodel met eigen vraag (bijv. een vaste rij)
                uit.append(f"{inspring}- **{vraag}**{voorwaarde}  \n{inspring}  `{veldpad}{is_}{t.__name__}(...)` met:")
                uit += _rij(t, diepte + 1)
            else:  # subsectie zonder eigen vraag
                uit += _regels(t, veldpad, diepte)
            continue

        if soort.startswith("per"):
            uit.append(f"{inspring}- **{vraag}**{voorwaarde}  \n{inspring}  `{veldpad}{is_}{{sleutel: True}}` ({soort})")
            continue
        regel = f"{inspring}- **{vraag}**{voorwaarde}  \n{inspring}  `{veldpad}{is_}{_voorbeeld(t, extra.get('eenheid'))}`"
        if extra.get("eenheid"):
            regel += f" ({extra['eenheid']})"
        if isinstance(t, type) and issubclass(t, Enum):
            keuzes = " · ".join(f"`{t.__name__}.{e.name}` = {getattr(e, 'label', e.value)}" for e in t)
            regel += f"  \n{inspring}  Keuzes: {keuzes}"
        uit.append(regel)
    return uit


def sectie_tekst(nummer: int) -> str:
    naam = SECTIES[nummer - 1]
    model = typing.get_type_hints(Formulier)[naam]
    titel = f"{nummer:02d} · {naam.replace('_', ' ').capitalize()}"
    return f"## {titel}\n\nIn `maak_upload.py`: `f.{naam}` (zie `vul_{naam}`).\n\n" + "\n".join(_regels(model, f"f.{naam}", 0))


KOP = """# Invulhulp: alle vragen per sectie

Dit bestand is gemaakt met `examples\\invulhulp.py`. Maak het na een wijziging in het formulier opnieuw.

Zo lees je het:
- Per vraag staat de regel die je in `maak_upload.py` schrijft. Pas alleen de waarde na het `=` aan.
- **Keuzes** schrijf je precies zoals hier staat, bijv. `JaNee.JA`.
- *(alleen als: …)* betekent dat je deze vraag alleen mag invullen als die andere vraag zo beantwoord is. Anders
  geeft het script een melding.
- **Herhaalbaar** (bijv. meerdere salaristabellen) schrijf je als een lijst: `[Rij(...), Rij(...)]`. Binnen een rij
  zet je de antwoorden tussen de haakjes: `Salaristabel(naam="Tabel 2026", geldig_vanaf=dt.date(2026, 1, 1))`.
- **Per sleutel** (bijv. per grondslag) schrijf je als `{sleutel: waarde}`, bijv. `{Grondslag.BRUTO_LOON: GrondslagInstelling(salaris=True)}`.
- **Datums:** `dt.date(2026, 1, 31)`. **Bedragen en percentages:** gewone getallen, met een punt als decimaalteken
  (`8.5`).

## Bedragen (Bedragregel)

Veel vragen vragen om een bedrag, een percentage of een aantal uren. Dat schrijf je zo:

```python
Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=50, per=Interval.MAAND))
Bedragregel(soort=BedragSoort.PERCENTAGE, percentage=Percentage(percentage=8, basis=Loonbasis.JAARLOON,
                                                               per=Interval.JAAR, grondslag=Grondslag.BRUTO_LOON))
Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=2, per=Interval.WEEK))
Bedragregel(soort=BedragSoort.NVT)            # alleen waar "N.v.t." een keuze is
```

- `Interval` ("per"): UUR, DAG, WEEK, MAAND, KWARTAAL, JAAR, DAGDEEL, DIENST, EENMALIG, GEWERKTE_DAG, ITEM, KILOMETER,
  NACHT, OP_DECLARATIEBASIS, RIT, ROUTE, THUISWERKDAG, VERHUIZING, WEKELIJKSE_REISDAG.
- `Loonbasis` ("van"): UURLOON, DAGLOON, VIERWEKENLOON, MAANDLOON, JAARLOON.
- `Grondslag` (optioneel): BASISLOON, BRUTO_LOON, SV_LOON, VAKANTIEBIJSLAG, PENSIOEN, DERTIENDE_MAAND,
  GEBRUIKELIJK_LOON.
"""


def main() -> None:
    if len(sys.argv) > 1:
        print(sectie_tekst(int(sys.argv[1])))
        return
    tekst = KOP + "\n" + "\n\n".join(sectie_tekst(n) for n in range(1, len(SECTIES) + 1)) + "\n"
    UITVOER.write_text(tekst, encoding="utf-8")
    print(f"Geschreven: {UITVOER}")


if __name__ == "__main__":
    main()
