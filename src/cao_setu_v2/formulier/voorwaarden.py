"""Zichtbaarheidsvoorwaarden (showIf) als controleerbare objecten.

Een veld met ``toon_als=Als("cao_of_regeling", CaoOfRegeling.CAO)`` mag alleen een waarde hebben als
de voorwaarde klopt, net zoals de webform de vraag anders niet toont.

Paden in een voorwaarde verwijzen naar Python-velden:
- ``"veld"`` of ``"sub.veld"``: in hetzelfde model (het model waar de vraag in staat);
- ``"../veld"``: in het bovenliggende model (bijv. vanuit een rij naar de salaristabel);
- ``"/sectie.veld"``: vanaf het hele ``Formulier`` (bijv. ``"/pensioen.van_toepassing"``).

Een voorwaarde is ook een ``str`` (de leesbare tekst), zodat hij gewoon in de veld-metadata en het
JSON-schema kan staan.
"""

from typing import Any

from pydantic import BaseModel

ONBEKEND = object()
"""Waarde van een pad dat vanuit het huidige model (nog) niet te bereiken is."""


def is_leeg(waarde: Any) -> bool:
    """Niet ingevuld: None, "", False (checkbox uit), lege lijst/dict of een model met alleen lege velden."""
    if waarde is None or waarde is False or waarde == "":
        return True
    if isinstance(waarde, list):
        return all(is_leeg(w) for w in waarde)
    if isinstance(waarde, dict):
        return all(is_leeg(w) for w in waarde.values())
    if isinstance(waarde, BaseModel):
        return all(is_leeg(getattr(waarde, n)) for n in type(waarde).model_fields)
    return False


class Context:
    """De keten van modellen van het gevalideerde (top)model tot het model waar de vraag in staat."""

    def __init__(self, keten: list[BaseModel]):
        self.keten = keten

    def lees(self, pad: str) -> Any:
        if pad.startswith("/"):
            obj: Any = self.keten[0]
            if not getattr(type(obj), "is_wortel", False):
                return ONBEKEND
            pad = pad[1:]
        else:
            omhoog = 0
            while pad.startswith("../"):
                omhoog, pad = omhoog + 1, pad[3:]
            if omhoog >= len(self.keten):
                return ONBEKEND
            obj = self.keten[-1 - omhoog]
        for deel in pad.split("."):
            obj = getattr(obj, deel) if obj is not None else None
        return obj


class Voorwaarde(str):
    """Basis; ``geldt()`` geeft True/False, of None als het niet te bepalen is."""

    def geldt(self, ctx: Context) -> bool | None:
        raise NotImplementedError


class Als(Voorwaarde):
    """``Als("veld", A, B)``: veld heeft waarde A of B. ``Als("veld")``: veld is ingevuld (bijv. checkbox aan)."""

    veld: str
    waarden: tuple[str, ...]

    def __new__(cls, veld: str, *waarden: Any) -> "Als":
        teksten = tuple(str(w) for w in waarden)
        tekst = f"{veld} = {' of '.join(teksten)}" if teksten else f"{veld} is ingevuld"
        obj = super().__new__(cls, tekst)
        obj.veld, obj.waarden = veld, teksten
        return obj

    def __getnewargs__(self) -> tuple:
        return (self.veld, *self.waarden)

    def geldt(self, ctx: Context) -> bool | None:
        waarde = ctx.lees(self.veld)
        if waarde is ONBEKEND:
            return None
        if not self.waarden:
            return not is_leeg(waarde)
        return waarde is not None and str(waarde) in self.waarden


class Niet(Voorwaarde):
    deel: Voorwaarde

    def __new__(cls, deel: Voorwaarde) -> "Niet":
        obj = super().__new__(cls, f"niet ({deel})")
        obj.deel = deel
        return obj

    def __getnewargs__(self) -> tuple:
        return (self.deel,)

    def geldt(self, ctx: Context) -> bool | None:
        uitkomst = self.deel.geldt(ctx)
        return None if uitkomst is None else not uitkomst


class _Samengesteld(Voorwaarde):
    delen: tuple[Voorwaarde, ...]
    _woord = ""

    def __new__(cls, *delen: Voorwaarde):
        obj = super().__new__(cls, f" {cls._woord} ".join(f"({d})" for d in delen))
        obj.delen = delen
        return obj

    def __getnewargs__(self) -> tuple:
        return self.delen


class En(_Samengesteld):
    _woord = "en"

    def geldt(self, ctx: Context) -> bool | None:
        uitkomsten = [d.geldt(ctx) for d in self.delen]
        if False in uitkomsten:
            return False
        return None if None in uitkomsten else True


class Of(_Samengesteld):
    _woord = "of"

    def geldt(self, ctx: Context) -> bool | None:
        uitkomsten = [d.geldt(ctx) for d in self.delen]
        if True in uitkomsten:
            return True
        return None if None in uitkomsten else False


def _kinderen(waarde: Any) -> list[BaseModel]:
    if isinstance(waarde, BaseModel):
        return [waarde]
    if isinstance(waarde, list):
        return [w for w in waarde if isinstance(w, BaseModel)]
    if isinstance(waarde, dict):
        return [w for w in waarde.values() if isinstance(w, BaseModel)]
    return []


def schendingen(model: BaseModel, keten: list[BaseModel] | None = None) -> list[str]:
    """Alle velden (ook in submodellen) die ingevuld zijn terwijl hun voorwaarde niet klopt."""
    keten = [*(keten or []), model]
    ctx = Context(keten)
    fouten = []
    for naam, info in type(model).model_fields.items():
        waarde = getattr(model, naam)
        voorwaarde = (info.json_schema_extra or {}).get("toon_als")
        if isinstance(voorwaarde, Voorwaarde) and not is_leeg(waarde) and voorwaarde.geldt(ctx) is False:
            fouten.append(f"{type(model).__name__}.{naam} mag alleen ingevuld worden als {voorwaarde}")
        for kind in _kinderen(waarde):
            fouten += schendingen(kind, keten)
    return fouten
