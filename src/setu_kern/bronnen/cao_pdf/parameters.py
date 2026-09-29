"""Gegevens die niet in de cao staan: over de organisatie, de looptijd van de uitvraag en de contactpersoon.

Uit een TOML-bestand (``Parameters.lees("organisatie.toml")``) of rechtstreeks in Python::

    naam_regeling = "Koppert 2026"
    geldig_van = 2026-01-01
    opdrachtgever_naam = "Koppert Nederland B.V."
    opdrachtgever_kvk = "12345678"
    opdrachtgever_kvk_type = "KvK"        # KvK, OIN of RSIN (hoofdletters maken niet uit)
    sector = "Tuinbouw"
    contactpersonen = ["J. Jansen"]
"""

import datetime as dt
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

from ..wijzerbelonen.formulier import Formulier
from ..wijzerbelonen.formulier.s01_algemeen import TypeIdentificatienummer
from ..wijzerbelonen.formulier.s16_ondertekenen import Contactpersoon
from .invullen.rapport import Ingevuld

_ALGEMEEN = ("naam_regeling", "geldig_van", "geldig_tot", "opdrachtgever_naam", "opdrachtgever_kvk", "opdrachtgever_kvk_type", "sector")


@dataclass
class Parameters:
    naam_regeling: str | None = None
    geldig_van: dt.date | None = None
    geldig_tot: dt.date | None = None
    opdrachtgever_naam: str | None = None
    opdrachtgever_kvk: str | None = None
    opdrachtgever_kvk_type: TypeIdentificatienummer | str | None = None
    sector: str | None = None
    contactpersonen: list[str] = field(default_factory=list)

    @classmethod
    def lees(cls, pad: str | Path) -> "Parameters":
        data = tomllib.loads(Path(pad).read_text(encoding="utf-8"))
        onbekend = set(data) - {f.name for f in fields(cls)}
        if onbekend:
            raise ValueError(f"onbekende parameters in {pad}: {', '.join(sorted(onbekend))}")
        return cls(**data)

    def toepassen(self, formulier: Formulier) -> list[Ingevuld]:
        """Zet de parameters in het formulier; geeft terug wat er is ingevuld (voor het rapport)."""
        ingevuld = []
        for naam in _ALGEMEEN:
            waarde = getattr(self, naam)
            if waarde is None:
                continue
            if naam == "opdrachtgever_kvk_type":
                waarde = _type_identificatie(waarde)
            setattr(formulier.algemeen, naam, waarde)
            ingevuld.append(Ingevuld(f"algemeen.{naam}", str(waarde), None))
        if self.contactpersonen:
            formulier.ondertekenen.contactpersonen = [Contactpersoon(naam=n) for n in self.contactpersonen]
            ingevuld += [Ingevuld(f"ondertekenen.contactpersonen[{i}].naam", n, None) for i, n in enumerate(self.contactpersonen)]
        return ingevuld


def _type_identificatie(waarde: TypeIdentificatienummer | str) -> TypeIdentificatienummer:
    """``"kvk"``, ``"KvK"`` of ``TypeIdentificatienummer.KVK`` → het lid (hoofdletters maken niet uit)."""
    for lid in TypeIdentificatienummer:
        if str(waarde).lower() == lid.value.lower():
            return lid
    raise ValueError(f"onbekend type identificatienummer {waarde!r}: kies uit {', '.join(l.value for l in TypeIdentificatienummer)}")
