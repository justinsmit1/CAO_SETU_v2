"""16 · Ondertekenen → SETU (src/definition/16_ondertekenen.tsx)."""

from collections.abc import Iterator

from .gedeeld import tekst
from .motor import Antwoorden, SetuVraag


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for i in range(a.rijen("contactpersonen")):
        rij = ["contactpersonen", i]
        yield SetuVraag([*rij, "naam"], ["customer", "personContacts", i, "name", "formattedName"], tekst(a, [*rij, "naam"]))
        yield SetuVraag(
            [*rij, "email"],
            ["customer", "personContacts", i, "communication", "email", 0, "address"],
            tekst(a, [*rij, "email"]),
        )
        yield SetuVraag(
            [*rij, "telefoon"],
            ["customer", "personContacts", i, "communication", "phone", 0, "formattedNumber"],
            tekst(a, [*rij, "telefoon"]),
        )
        yield SetuVraag([*rij, "functie"], ["customer", "personContacts", i, "positionTitle"], tekst(a, [*rij, "functie"]))
