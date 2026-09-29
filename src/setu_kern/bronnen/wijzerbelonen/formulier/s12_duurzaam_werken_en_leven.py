"""12 · Duurzaam werken en leven (docs/formulier/12_duurzaam-werken-en-leven.md).

Elke regeling uit *Duurzame inzetbaarheid* en *Vitaliteit en gezondheid* is een checkbox die dezelfde
vraagset uitklapt (``makeBlockItems``). ``<r>`` in de slugs van ``RegelingVraagset`` is de slug van de regeling.
"""


from ._basis import FormulierModel, Keuze, veld
from .codes import JaNee, Loonbasis
from .voorwaarden import Als


class Tijdvak(Keuze):
    """Lokale keuzelijst Tijdvak (intervalUnitCodeOptions)."""

    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"


class TijdEenheid(Keuze):
    UUR = "Hour", "Uur / Uren"
    DAG = "Day", "Dagen"


class DagenPer(Keuze):
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"


class BudgetOfGemiddeld(Keuze):
    JA = "ja", "Ja"
    NEE_GEMIDDELD = "nee-gemiddeld", "Nee, geef aan wat er gemiddeld per werknemer aan dit onderwerp wordt besteed."


class RegelingBudgetType(Keuze):
    PERCENTAGE = "percentage", "Percentage van"
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag namelijk:"
    AANTAL_DAGEN_PER_JAAR = "aantal-dagen-per-jaar", "Aantal dagen per jaar"


class ScholingWanneer(Keuze):
    TIJDENS_WERKTIJD = "tijdens-werktijd", "Tijdens werktijd, namelijk:"
    ANDER_MOMENT = "ander-moment", "Op een ander moment, namelijk:"


class SamenlevingBudgetHoogte(Keuze):
    PERCENTAGE = "percentage", "Percentage van"
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag namelijk:"
    UREN_OF_DAGEN = "uren-of-dagen", "Uren of dagen"


_AANGEVINKT = Als("aangevinkt")
_BUDGET_TYPE_PERCENTAGE = Als("budget_type", RegelingBudgetType.PERCENTAGE)
_BUDGET_TYPE_VAST_BEDRAG = Als("budget_type", RegelingBudgetType.VAST_BEDRAG)
_GEMIDDELD = Als("budget", BudgetOfGemiddeld.NEE_GEMIDDELD)

_SCHOLING = Als("verplichte_scholing", JaNee.JA)
_SAMENLEVING = Als("samenleving_regeling", JaNee.JA)
_SAMENLEVING_BUDGET = Als("samenleving_budget", JaNee.JA)
_HOOGTE_PERCENTAGE = Als("budget_hoogte", SamenlevingBudgetHoogte.PERCENTAGE)
_HOOGTE_VAST_BEDRAG = Als("budget_hoogte", SamenlevingBudgetHoogte.VAST_BEDRAG)
_HOOGTE_UREN_OF_DAGEN = Als("budget_hoogte", SamenlevingBudgetHoogte.UREN_OF_DAGEN)


class RegelingVraagset(FormulierModel):
    """Regeling-vraagset (makeBlockItems); ``<r>`` = slug van de regeling."""

    aangevinkt: bool | None = veld("<r>", "(label van de regeling)")
    namelijk: str | None = veld(
        "<r>/namelijk",
        "(geen vraagtekst; hulptekst = andersHelp)",
        toon_als=_AANGEVINKT,  # veld bestaat alleen bij regelingen met namelijk-veld
    )

    # Budget
    budget: BudgetOfGemiddeld | None = veld(
        "<r>/budget", "Is er een (individueel) budget verbonden aan deze regeling?", toon_als=_AANGEVINKT, vraagtype="radio"
    )
    budget_type: RegelingBudgetType | None = veld(
        "<r>/budget/type", "Hoe hoog is het budget?", toon_als=Als("budget", BudgetOfGemiddeld.JA), vraagtype="radio"
    )
    percentage: float | None = veld(
        "<r>/budget/percentage/percentage", "percentage (%)", toon_als=_BUDGET_TYPE_PERCENTAGE, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld(
        "<r>/budget/percentage/van", "van", toon_als=_BUDGET_TYPE_PERCENTAGE, vraagtype="keuzelijst"
    )
    percentage_tijdvak: Tijdvak | None = veld(
        "<r>/budget/percentage/tijdvak", "per", toon_als=_BUDGET_TYPE_PERCENTAGE, vraagtype="keuzelijst"
    )
    vast_bedrag: float | None = veld(
        "<r>/budget/vast-bedrag/bedrag", "bedrag (€)", toon_als=_BUDGET_TYPE_VAST_BEDRAG, eenheid="€"
    )
    vast_bedrag_tijdvak: Tijdvak | None = veld(
        "<r>/budget/vast-bedrag/tijdvak", "per", toon_als=_BUDGET_TYPE_VAST_BEDRAG, vraagtype="keuzelijst"
    )
    aantal_dagen_per_jaar: float | None = veld(
        "<r>/budget/aantal-dagen-per-jaar/aantal", "dagen", toon_als=Als("budget_type", RegelingBudgetType.AANTAL_DAGEN_PER_JAAR)
    )

    # Gemiddelde besteding per werknemer
    gemiddeld_bedrag: float | None = veld("<r>/gemiddeld/vast-bedrag/bedrag", "bedrag (€)", toon_als=_GEMIDDELD, eenheid="€")
    gemiddeld_tijdvak: Tijdvak | None = veld("<r>/gemiddeld/vast-bedrag/tijdvak", "per", toon_als=_GEMIDDELD, vraagtype="keuzelijst")

    # Naar rato, uitkering en voorwaarden
    naar_rato: JaNee | None = veld(
        "<r>/naar-rato",
        "Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van "
        "de duur van het dienstverband?",
        toon_als=_AANGEVINKT, vraagtype="radio",
    )
    uitgekeerd: JaNee | None = veld(
        "<r>/uitgekeerd",
        "Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt? "
        "(Ja = 'Ja, onder de volgende voorwaarden:')",
        toon_als=_AANGEVINKT, vraagtype="radio",
    )
    uitgekeerd_voorwaarden: str | None = veld(
        "<r>/uitgekeerd/ja/namelijk", "(geen vraagtekst, textarea)", toon_als=Als("uitgekeerd", JaNee.JA)
    )
    voorwaarden: JaNee | None = veld(
        "<r>/voorwaarden", "Zijn er voorwaarden verbonden aan de toekenning van het budget?", toon_als=_AANGEVINKT, vraagtype="radio"
    )
    voorwaarden_namelijk: str | None = veld(
        "<r>/voorwaarden/ja/namelijk", "(geen vraagtekst, textarea)", toon_als=Als("voorwaarden", JaNee.JA)
    )


class DuurzaamWerkenEnLeven(FormulierModel):
    # Duurzame inzetbaarheid
    # "Welke regelingen kent jouw onderneming die de duurzame inzetbaarheid van de werknemer bevorderen?"
    opleidingen: RegelingVraagset | None = veld("duurzame-inzetbaarheid-regelingen/opleidingen", "Opleidingen")
    loopbaancoaching: RegelingVraagset | None = veld(
        "duurzame-inzetbaarheid-regelingen/loopbaancoaching", "Loopbaancoaching"
    )
    outplacementtrajecten: RegelingVraagset | None = veld(
        "duurzame-inzetbaarheid-regelingen/outplacementtrajecten", "Outplacementtrajecten"
    )
    voorlichting_nederland: RegelingVraagset | None = veld(
        "duurzame-inzetbaarheid-regelingen/voorlichting-nederland",
        "Voorlichting met betrekking tot het in Nederland werken en verblijven van de niet permanent in "
        "Nederland woonachtige werknemer",
    )
    scholing_nederland: RegelingVraagset | None = veld(
        "duurzame-inzetbaarheid-regelingen/scholing-nederland",
        "Scholing met betrekking tot het in Nederland werken en verblijven van de niet permanent in "
        "Nederland woonachtige werknemer",
    )
    sociale_begeleiding_nederland: RegelingVraagset | None = veld(
        "duurzame-inzetbaarheid-regelingen/sociale-begeleiding-nederland",
        "Sociale begeleiding met betrekking tot het in Nederland werken en verblijven van de niet permanent "
        "in Nederland woonachtige werknemer",
    )
    inzetbaarheid_anders: RegelingVraagset | None = veld(
        "duurzame-inzetbaarheid-regelingen/anders", "Anders, namelijk: (met namelijk-veld)"
    )
    inzetbaarheid_geen: bool | None = veld("duurzame-inzetbaarheid-regelingen/geen", "Geen")

    # Vitaliteit en gezondheid
    # "Welke regelingen kent jouw onderneming die de vitaliteit en gezondheid van de werknemer bevorderen?"
    fysieke_gezondheid: RegelingVraagset | None = veld(
        "vitaliteit-gezondheid-regelingen/fysieke-gezondheid",
        "Regeling ter bevordering van de fysieke gezondheid, namelijk: (met namelijk-veld)",
    )
    mentale_gezondheid: RegelingVraagset | None = veld(
        "vitaliteit-gezondheid-regelingen/mentale-gezondheid",
        "Regeling ter bevordering van de mentale gezondheid, namelijk: (met namelijk-veld)",
    )
    financiele_gezondheid: RegelingVraagset | None = veld(
        "vitaliteit-gezondheid-regelingen/financiele-gezondheid",
        "Regeling ter bevordering van de financiële gezondheid, namelijk: (met namelijk-veld)",
    )
    vitaliteitsbudget: RegelingVraagset | None = veld(
        "vitaliteit-gezondheid-regelingen/vitaliteitsbudget", "Vitaliteitsbudget"
    )
    vitaliteit_anders: RegelingVraagset | None = veld(
        "vitaliteit-gezondheid-regelingen/anders", "Anders, namelijk: (met namelijk-veld)"
    )
    vitaliteit_geen: bool | None = veld("vitaliteit-gezondheid-regelingen/geen", "Geen")

    # Verplichte scholing
    verplichte_scholing: JaNee | None = veld(
        "verplichte-scholing",
        "Is er sprake van scholing die op grond van de wet of cao noodzakelijk is voor de uitvoering van "
        "het werk? (Ja = 'Ja, namelijk:')", vraagtype="radio",
    )
    verplichte_scholing_namelijk: str | None = veld(
        "verplichte-scholing/ja/namelijk", "(geen vraagtekst, textarea)", toon_als=_SCHOLING
    )
    scholing_tijd: float | None = veld(
        "verplichte-scholing-tijd", "Hoeveel kost de verplichte scholing in tijd?", toon_als=_SCHOLING
    )
    scholing_tijd_type: TijdEenheid | None = veld(
        "verplichte-scholing-tijd-type", "(geen vraagtekst, eenheid)", toon_als=_SCHOLING, vraagtype="keuzelijst"
    )

    # Wanneer wordt de verplichte scholing gevolgd?
    scholing_wanneer: ScholingWanneer | None = veld(
        "verplichte-scholing-wanneer", "Wanneer wordt de verplichte scholing gevolgd?", toon_als=_SCHOLING, vraagtype="radio"
    )
    scholing_tijdens_werktijd: str | None = veld(
        "verplichte-scholing-wanneer/tijdens-werktijd/namelijk",
        "(geen vraagtekst)",
        toon_als=Als("scholing_wanneer", ScholingWanneer.TIJDENS_WERKTIJD),
    )
    scholing_ander_moment: str | None = veld(
        "verplichte-scholing-wanneer/ander-moment/namelijk",
        "(geen vraagtekst)",
        toon_als=Als("scholing_wanneer", ScholingWanneer.ANDER_MOMENT),
    )

    # Hoeveel kost de verplichte scholing inclusief alle bijkomende kosten?
    scholing_kosten: float | None = veld(
        "verplichte-scholing-kosten",
        "Hoeveel kost de verplichte scholing inclusief alle bijkomende kosten (studiemateriaal, "
        "examengelden etc.)? (€)",
        toon_als=_SCHOLING, eenheid="€",
    )

    # Duurzame samenleving
    samenleving_regeling: JaNee | None = veld(
        "duurzame-samenleving-regeling",
        "Kent jouw onderneming regelingen voor een duurzame samenleving en groene aarde? Zoals "
        "klimaatbudget, vrije dagen voor vrijwilligerswerk, etc.", vraagtype="radio",
    )
    samenleving_budget: JaNee | None = veld(
        "duurzame-samenleving-budget",
        "Is er een (individueel) budget verbonden aan regelingen voor een duurzame samenleving en een "
        "groene aarde?",
        toon_als=_SAMENLEVING, vraagtype="radio",
    )

    # Hoe hoog is het budget?
    budget_hoogte: SamenlevingBudgetHoogte | None = veld(
        "duurzame-samenleving-budget-hoogte", "Hoe hoog is het budget?", toon_als=_SAMENLEVING_BUDGET, vraagtype="radio"
    )
    percentage: float | None = veld(
        "duurzame-samenleving-budget-hoogte/percentage/percentage", "percentage (%)", toon_als=_HOOGTE_PERCENTAGE, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld(
        "duurzame-samenleving-budget-hoogte/percentage/van", "van", toon_als=_HOOGTE_PERCENTAGE, vraagtype="keuzelijst"
    )
    percentage_tijdvak: Tijdvak | None = veld(
        "duurzame-samenleving-budget-hoogte/percentage/tijdvak", "per", toon_als=_HOOGTE_PERCENTAGE, vraagtype="keuzelijst"
    )
    vast_bedrag: float | None = veld(
        "duurzame-samenleving-budget-hoogte/vast-bedrag/bedrag", "Bedrag (€)", toon_als=_HOOGTE_VAST_BEDRAG, eenheid="€"
    )
    vast_bedrag_tijdvak: Tijdvak | None = veld(
        "duurzame-samenleving-budget-hoogte/vast-bedrag/tijdvak", "per (tijdvak)", toon_als=_HOOGTE_VAST_BEDRAG, vraagtype="keuzelijst"
    )
    uren_of_dagen_aantal: float | None = veld(
        "duurzame-samenleving-budget-hoogte/uren-of-dagen/aantal", "aantal", toon_als=_HOOGTE_UREN_OF_DAGEN
    )
    uren_of_dagen_type: TijdEenheid | None = veld(
        "duurzame-samenleving-budget-hoogte/uren-of-dagen/type", "type", toon_als=_HOOGTE_UREN_OF_DAGEN, vraagtype="keuzelijst"
    )
    uren_of_dagen_per: DagenPer | None = veld(
        "duurzame-samenleving-budget-hoogte/dagen-per/per", "per", toon_als=_HOOGTE_UREN_OF_DAGEN, vraagtype="keuzelijst"
    )

    # Naar rato
    budget_naar_rato: JaNee | None = veld(
        "duurzame-samenleving-budget-naar-rato",
        "Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van "
        "de duur van het dienstverband?",
        toon_als=_SAMENLEVING_BUDGET, vraagtype="radio",
    )

    # Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt?
    budget_uitgekeerd: JaNee | None = veld(
        "duurzame-samenleving-budget-uitgekeerd",
        "Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt?",
        toon_als=_SAMENLEVING_BUDGET, vraagtype="radio",
    )
    budget_uitgekeerd_voorwaarden: str | None = veld(
        "duurzame-samenleving-budget-uitgekeerd/ja/voorwaarden",
        "onder de volgende voorwaarden",
        toon_als=Als("budget_uitgekeerd", JaNee.JA),
    )

    # Zijn er voorwaarden verbonden aan de toekenning van het budget?
    budget_voorwaarden: JaNee | None = veld(
        "duurzame-samenleving-budget-voorwaarden",
        "Zijn er voorwaarden verbonden aan de toekenning van het budget? (Ja = 'Ja, namelijk:')",
        toon_als=_SAMENLEVING_BUDGET, vraagtype="radio",
    )
    budget_voorwaarden_namelijk: str | None = veld(
        "duurzame-samenleving-budget-voorwaarden/ja/namelijk",
        "(geen vraagtekst, textarea)",
        toon_als=Als("budget_voorwaarden", JaNee.JA),
    )
