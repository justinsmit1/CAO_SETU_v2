"""16 · Ondertekenen (docs/formulier/16_ondertekenen.md)."""

from ._basis import FormulierModel, veld


class Contactpersoon(FormulierModel):
    naam: str | None = veld("contactpersonen[i]/naam", "Naam:")
    email: str | None = veld("contactpersonen[i]/email", "E-mailadres:")
    telefoon: str | None = veld("contactpersonen[i]/telefoon", "Telefoonnummer:")
    functie: str | None = veld("contactpersonen[i]/functie", "Functie:")


class Ondertekenen(FormulierModel):
    contactpersonen: list[Contactpersoon] = veld(
        "contactpersonen[i]",
        "Contactpersonen (eerste = persoon die het formulier invult)",
        lijst=True,
    )
    akkoord: bool | None = veld(
        "ondertekening-akkoord",
        "Ik verklaar bevoegd te zijn tot het het verstrekken van de gevraagde informatie aan de uitzendonderneming. (...)",
    )
