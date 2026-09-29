"""15 · Grondslagen → SETU (src/definition/15_grondslagen.tsx).

De sectie is dynamisch: er komt één subsectie per grondslagcode die elders in de antwoorden gekozen is
(``gebruikte_grondslagen``). De webform leest daarvoor de ruwe antwoorden, dus ook antwoorden van vragen die
op dat moment verborgen zijn (bijv. een grondslag bij een Bedragregel waarvan de soort later is gewijzigd).
"""

from collections.abc import Iterator
from functools import partial
from typing import Any

from ...formulier.s04_toeslagen import ToeslagSoort
from .motor import CHECKED, Antwoorden, Opbouw, SetuVraag, to_date_string
from .setu_s13_aanvullende_regelingen import REGELINGEN, js_tekst

# typeCode per toeslagrij (makeToeslagRows); ToeslagSoort heeft dezelfde volgorde.
TOESLAG_TYPE_CODES = {
    ToeslagSoort.ONREGELMATIGHEIDSTOESLAGEN: "HT320",
    ToeslagSoort.PLOEGENTOESLAGEN: "HT300",
    ToeslagSoort.VERSCHOVEN_DIENSTEN: "HT101",
    ToeslagSoort.FYSIEKE_BELASTING: "EA301",
    ToeslagSoort.STAND_BY: "HT602",
    ToeslagSoort.OVERWERK: "HT200",
    ToeslagSoort.WAARNEMINGSTOESLAG: "EA300",
    ToeslagSoort.PERFORMANCETOESLAG: "EA300",
    ToeslagSoort.ANDERS: "EA300",
}


def gebruikte_grondslagen(a: Antwoorden) -> list[str]:
    """De grondslagcodes waarvoor de webform een subsectie maakt, uniek en in de volgorde van makeGrondslagen."""
    ruw: list[str | None] = [
        # Zonder "|| null": een lege tekst telt hier wél als grondslag.
        js_tekst(a.get("vakantiebijslag/percentage/grondslag")),
        js_tekst(a.get("individueel-keuzebudget/percentage/grondslag")),
        # Webform-bug: de pensioenvraag heet "pensioenregeling/van-toepassing", dus dit is in de praktijk nooit waar.
        "Pension" if a.get("pensioenregeling") == "ja" else None,
    ]

    def of_null(slug: Any) -> str | None:  # ``getAnswer(...)?.toString() || null``
        return js_tekst(a.get(slug)) or None

    for soort in ToeslagSoort:
        for i in range(a.rijen(soort.value)):
            ruw.append(of_null([soort.value, i, "percentage/grondslag"]))
    for i in range(a.rijen("loondoorbetaling-bij-ziekte")):
        ruw.append(of_null(["loondoorbetaling-bij-ziekte", i, "grondslag"]))
    for regeling in REGELINGEN:
        ruw.append(of_null(f"{regeling.slug}/werkgeverspremie/percentage/grondslag"))
        ruw.append(of_null(f"{regeling.slug}/werknemerspremie/percentage/grondslag"))
    for i in range(a.rijen("andere-sociale-regelingen")):
        ruw.append(of_null(["andere-sociale-regelingen", i, "werkgeverspremie", 0, "percentage/grondslag"]))
        ruw.append(of_null(["andere-sociale-regelingen", i, "werknemerspremie", 0, "percentage/grondslag"]))
    for i in range(a.rijen("overige-regelingen")):
        ruw.append(of_null(["overige-regelingen", i, "percentage/grondslag"]))

    codes: list[str] = []
    for code in ruw:
        if code is not None and code not in codes:
            codes.append(code)
    return codes


def _grondslag(code: str, waarde: Any, opbouw: Opbouw) -> dict[str, Any]:
    a = opbouw.antwoorden
    p = f"grondslag/{code}"
    toeslagen = js_tekst(a.get(f"{p}/toeslagen"))
    basis: dict[str, Any] = {
        "baseType": code,
        "remunerationIndicator": a.get(f"{p}/salaris") is CHECKED,
        "holidayAllowanceIndicator": a.get(f"{p}/vakantietoeslag") is CHECKED,
        "paidLeaveDayIndicator": a.get(f"{p}/betaald-verlof") is CHECKED,
        "allAllowancesIndicator": toeslagen == "all",
    }
    peildatum = a.get(f"{p}/peildatum")
    if peildatum:
        basis["referenceDate"] = {"occurrenceType": "Recurring", "interval": f"R/{to_date_string(peildatum)}/P1Y"}
    if toeslagen == "some":
        basis["allowances"] = [
            {"typeCode": type_code}
            for soort, type_code in TOESLAG_TYPE_CODES.items()
            if a.get(f"{p}/toeslag-{soort.value}") is CHECKED
        ]
    return basis


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for index, code in enumerate(gebruikte_grondslagen(a)):
        slug = f"grondslag/{code}/salaris"
        yield SetuVraag(
            slug,
            ["baseDefinition", index],
            a.get(slug),
            omzetten=partial(_grondslag, code),
            omzetten_bij_leeg=True,
        )
