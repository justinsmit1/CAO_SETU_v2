"""01 · Algemeen → SETU (src/definition/01_algemeen.tsx)."""

from collections.abc import Iterator

from .gedeeld import keuze, tekst
from .motor import Antwoorden, SetuVraag, datum_waarde

_CAO_OF_REGELING = {
    "cao-van-toepassing": False,
    "eigen-arbeidsvoorwaardenregeling": True,
    "cao-en-eigen-arbeidsvoorwaardenregeling": True,
    "geen-cao-of-arbeidsvoorwaardenregeling": False,
}


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    yield SetuVraag("id", ["documentId", "value"], tekst(a, "id"))
    yield SetuVraag("toepassingsperiode-van", ["effectivePeriod", "validFrom"], datum_waarde(a.get("toepassingsperiode-van")))
    yield SetuVraag("toepassingsperiode-tot", ["effectivePeriod", "validTo"], datum_waarde(a.get("toepassingsperiode-tot")))
    yield SetuVraag("opdrachtgever-naam", ["customer", "name"], tekst(a, "opdrachtgever-naam"))
    yield SetuVraag("opdrachtgever-kvk", ["customer", "legalId", 0, "value"], tekst(a, "opdrachtgever-kvk"))
    yield SetuVraag("opdrachtgever-kvk-type", ["customer", "legalId", 0, "schemeAgencyId"], keuze(a, "opdrachtgever-kvk-type"))
    yield SetuVraag("sector", ["labourAgreements", "industryIdentifier", 0, "value"], tekst(a, "sector"))
    yield SetuVraag(
        "cao-of-regeling", ["labourAgreements", "customLabourAgreement"], keuze(a, "cao-of-regeling", _CAO_OF_REGELING)
    )

    # Blok "Welke cao is van toepassing?"
    cao = a.heeft("cao-of-regeling", "cao-van-toepassing") or a.heeft("cao-of-regeling", "cao-en-eigen-arbeidsvoorwaardenregeling")
    avv = cao and a.heeft("cao-van-toepassing-omdat", "algemeen-verbindend")
    yield SetuVraag("cao-naam", ["labourAgreements", "collectiveLabourAgreement", "name"], tekst(a, "cao-naam"), zichtbaar=cao)
    yield SetuVraag(
        "cao-nummer", ["labourAgreements", "collectiveLabourAgreement", "id", "value"], tekst(a, "cao-nummer"), zichtbaar=cao
    )
    yield SetuVraag(
        "cao-van-toepassing-omdat",
        ["labourAgreements", "collectiveLabourAgreement", "basedOn"],
        keuze(a, "cao-van-toepassing-omdat"),
        zichtbaar=cao,
    )
    yield SetuVraag(
        "cao-van",
        ["labourAgreements", "collectiveLabourAgreement", "effectivePeriod", "validFrom"],
        datum_waarde(a.get("cao-van")),
        zichtbaar=avv,
    )
    yield SetuVraag(
        "cao-tot",
        ["labourAgreements", "collectiveLabourAgreement", "effectivePeriod", "validTo"],
        datum_waarde(a.get("cao-tot")),
        zichtbaar=avv,
    )
