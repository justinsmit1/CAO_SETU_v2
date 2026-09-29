"""Basisklassen en veld-helper voor het formuliermodel.

Elk veld draagt metadata die terugverwijst naar het webformulier (zie docs/formulier/):
- ``slug``: de sleutel waaronder de webform het antwoord opslaat. ``[i]``/``[j]``/``[k]`` zijn
  rij-indexen van herhaalbare blokken, ``<p>`` is een slug-prefix (bijv. bij een Bedragregel).
- ``vraagtype``: radio, keuzelijst, tekst, getal, ... (zie ``Vraagtype``). Alleen expliciet
  opgegeven waar het type niet uit de Python-annotatie volgt; ``inspectie.vragen()`` vult de rest aan.
- ``eenheid``: prefix/postfix bij getallen (``€``, ``%``, ``uur``).
- ``opties``: de toegestane opties als een vraag maar een deel van een keuzelijst toont
  (bij een Bedragregel: de toegestane soorten). Wordt bij het vullen gecontroleerd.
- ``zonder_per``: Bedragregel zonder "per"-vragen; een ingevuld "per" wordt geweigerd.
- ``toon_als``: de zichtbaarheidsvoorwaarde (showIf). Als ``Voorwaarde`` (zie ``voorwaarden.py``) wordt
  gecontroleerd dat het veld alleen ingevuld is als de voorwaarde klopt; als gewone tekst is het alleen uitleg.
"""

from collections.abc import Iterable
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .voorwaarden import Voorwaarde, schendingen

_GEEN_WAARDE = object()


class Keuze(StrEnum):
    """Keuzelijst met een leesbaar label per optie.

    Leden worden gedefinieerd als ``NAAM = "waarde", "label"``; de waarde is wat de webform opslaat.
    """

    label: str

    def __new__(cls, waarde: str, label: str | None = None) -> Self:
        obj = str.__new__(cls, waarde)
        obj._value_ = waarde
        obj.label = label or waarde
        return obj


class Vraagtype(StrEnum):
    TEKST = "tekst"
    GETAL = "getal"
    DATUM = "datum"
    TIJD = "tijd"
    RADIO = "radio"
    KEUZELIJST = "keuzelijst"  # radio die in de tool als dropdown wordt getoond
    CHECKBOX = "checkbox"
    BEDRAGREGEL = "bedragregel"
    BLOK = "blok"  # submodel of herhaalbaar blok


class FormulierModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    def __setattr__(self, naam: str, waarde: Any) -> None:
        # Pydantic laat bij een mislukte model-validatie de nieuwe waarde staan; zet de oude terug,
        # zodat een geweigerde toewijzing het formulier niet in een ongeldige toestand achterlaat.
        oud = self.__dict__.get(naam, _GEEN_WAARDE)
        try:
            super().__setattr__(naam, waarde)
        except ValidationError:
            if oud is not _GEEN_WAARDE:
                self.__dict__[naam] = oud
            raise

    @model_validator(mode="after")
    def _controleer_opties(self) -> Self:
        for naam, info in type(self).model_fields.items():
            extra = info.json_schema_extra or {}
            waarde = getattr(self, naam)
            if waarde is None:
                continue
            toegestaan = extra.get("opties")
            # Bij een Bedragregel gaat de beperking over de gekozen soort.
            gekozen = getattr(waarde, "soort", waarde)
            if toegestaan and gekozen is not None and gekozen not in toegestaan:
                raise ValueError(
                    f"{type(self).__name__}.{naam}: optie '{gekozen}' is niet toegestaan bij deze vraag "
                    f"(toegestaan: {', '.join(toegestaan)})"
                )
            if extra.get("zonder_per") and waarde.per() is not None:
                raise ValueError(f"{type(self).__name__}.{naam}: deze vraag heeft geen 'per' in het formulier")
        return self

    @model_validator(mode="after")
    def _controleer_voorwaarden(self) -> Self:
        fouten = schendingen(self)
        if fouten:
            raise ValueError("; ".join(fouten))
        return self


def veld(
    slug: str,
    vraag: str,
    *,
    vraagtype: Vraagtype | str | None = None,
    eenheid: str | None = None,
    opties: Iterable[str] | None = None,
    zonder_per: bool = False,
    toon_als: Voorwaarde | str | None = None,
    optioneel: bool = False,
    lijst: bool = False,
    mapping: bool = False,
    **kwargs: Any,
) -> Any:
    """Formuliervraag als Pydantic-veld; standaard leeg (None, lege lijst of lege dict).

    ``lijst=True`` voor herhaalbare blokken, ``mapping=True`` voor antwoorden per sleutel
    (bijv. per grondslagcode of per toeslagsoort).
    """
    extra: dict[str, Any] = {"slug": slug}
    if vraagtype:
        extra["vraagtype"] = Vraagtype(vraagtype).value
    if eenheid:
        extra["eenheid"] = eenheid
    if opties is not None:
        extra["opties"] = [str(o) for o in opties]
    if zonder_per:
        extra["zonder_per"] = True
    if toon_als:
        extra["toon_als"] = toon_als
    if optioneel:
        extra["optioneel"] = True
    if lijst:
        kwargs["default_factory"] = list
    elif mapping:
        kwargs["default_factory"] = dict
    else:
        kwargs.setdefault("default", None)
    return Field(description=vraag, json_schema_extra=extra, **kwargs)
