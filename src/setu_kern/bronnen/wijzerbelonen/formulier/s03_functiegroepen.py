"""03 · Functiegroepen (docs/formulier/03_functiegroepen.md)."""

from ._basis import FormulierModel, veld


class Functiegroep(FormulierModel):
    titel: str | None = veld("functie-groepen[i]/titel", "Titel")
    code: str | None = veld("functie-groepen[i]/id", "Code", optioneel=True)
    salarisschaal: str | None = veld(
        "functie-groepen[i]/salarisschalen",
        'Salarisschaal {num} (dynamische keuzelijst: waarde "b,s" = index salaristabel, index salarisschaal '
        "uit 02 Beloning)",
    )


class Functiegroepen(FormulierModel):
    # Functiegroepen
    functie_groepen: list[Functiegroep] = veld(
        "functie-groepen[i]",
        "Voor welke functie(s) of functiegroep(en) wordt het formulier ingevuld?",
        lijst=True,
    )
