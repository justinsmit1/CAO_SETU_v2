"""10 Individueel keuzebudget, 11 Pensioen, 12 Duurzaam werken en leven: formulier → antwoorden → SETU,
vergeleken met de webform."""

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, VastBedrag
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Grondslag, Interval, JaNee, Loonbasis
from setu_kern.bronnen.wijzerbelonen.formulier.s10_individueel_keuzebudget import IkbVan
from setu_kern.bronnen.wijzerbelonen.formulier.s12_duurzaam_werken_en_leven import (
    BudgetOfGemiddeld,
    DagenPer,
    RegelingBudgetType,
    RegelingVraagset,
    SamenlevingBudgetHoogte,
    ScholingWanneer,
    TijdEenheid,
    Tijdvak,
)
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import naar_antwoorden
from referentie_kern.controle import antwoord_problemen, vergelijk_setu

JA, NEE = JaNee.JA, JaNee.NEE


def _percentage(**kw) -> RegelingVraagset:
    return RegelingVraagset(
        aangevinkt=True,
        budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.PERCENTAGE,
        percentage=kw.get("percentage", 1.5),
        percentage_van=Loonbasis.JAARLOON,
        percentage_tijdvak=Tijdvak.JAAR,
        naar_rato=JA,
        uitgekeerd=JA,
        uitgekeerd_voorwaarden="Bij uitdiensttreding",
        voorwaarden=JA,
        voorwaarden_namelijk="Na goedkeuring leidinggevende",
    )


def _vast_bedrag() -> RegelingVraagset:
    return RegelingVraagset(
        aangevinkt=True,
        budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.VAST_BEDRAG,
        vast_bedrag=500,
        vast_bedrag_tijdvak=Tijdvak.MAAND,
        naar_rato=NEE,
        uitgekeerd=NEE,
        voorwaarden=NEE,
    )


def _dagen() -> RegelingVraagset:
    return RegelingVraagset(
        aangevinkt=True,
        budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.AANTAL_DAGEN_PER_JAAR,
        aantal_dagen_per_jaar=2.5,
        naar_rato=JA,
        uitgekeerd=NEE,
    )


def _gemiddeld(namelijk: str | None = None) -> RegelingVraagset:
    return RegelingVraagset(
        aangevinkt=True,
        namelijk=namelijk,
        budget=BudgetOfGemiddeld.NEE_GEMIDDELD,
        gemiddeld_bedrag=250.75,
        gemiddeld_tijdvak=Tijdvak.JAAR,
        uitgekeerd=JA,  # zonder voorwaarden → "null" in de tekst
        voorwaarden=JA,  # zonder tekst → geen voorwaarde
    )


def _rijk() -> Formulier:
    f = Formulier()
    ikb = f.individueel_keuzebudget
    ikb.ja_nee = JA
    ikb.waarde = Bedragregel(
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=16.5, basis=Loonbasis.MAANDLOON, per=Interval.MAAND, grondslag=Grondslag.BASISLOON),
    )
    ikb.arbeidsvoorwaarden_opgenomen = JA
    ikb.bovenwettelijke_vakantiedagen = True
    ikb.bovenwettelijke_vakantiedagen_percentage = 3.2
    ikb.bovenwettelijke_vakantiedagen_van = IkbVan.UURLOON
    ikb.adv_dagen = True
    ikb.adv_dagen_percentage = 4
    ikb.adv_dagen_van = IkbVan.WEEKLOON
    ikb.eindejaarsuitkering = True
    ikb.eindejaarsuitkering_percentage = 8.33
    ikb.eindejaarsuitkering_van = IkbVan.MAANDLOON
    ikb.vakantiebijslag = True
    ikb.vakantiebijslag_percentage = 8
    ikb.vakantiebijslag_van = IkbVan.PERIODELOON
    ikb.anders = True
    ikb.anders_namelijk = "Fietsplan"

    p = f.pensioen
    p.van_toepassing = JA
    p.pensioenfonds_naam = "PFZW"
    p.werkgeverspremie_percentage = 14.2
    p.franchise = JA
    p.franchise_namelijk = "Franchise € 17.545 per jaar"

    d = f.duurzaam_werken_en_leven
    d.opleidingen = _percentage()
    d.loopbaancoaching = _vast_bedrag()
    d.outplacementtrajecten = _dagen()
    d.voorlichting_nederland = _gemiddeld()
    d.scholing_nederland = _percentage(percentage=2)
    d.sociale_begeleiding_nederland = _vast_bedrag()
    d.inzetbaarheid_anders = _gemiddeld("Mentorprogramma")
    d.fysieke_gezondheid = _dagen().model_copy(update={"namelijk": "Sportabonnement"})
    d.mentale_gezondheid = _percentage().model_copy(update={"namelijk": "Coach"})
    d.financiele_gezondheid = _vast_bedrag().model_copy(update={"namelijk": "Financieel planner"})
    d.vitaliteitsbudget = _gemiddeld()
    d.vitaliteit_anders = _percentage().model_copy(update={"namelijk": "Yoga"})

    d.verplichte_scholing = JA
    d.verplichte_scholing_namelijk = "VCA"
    d.scholing_tijd = 16
    d.scholing_tijd_type = TijdEenheid.UUR
    d.scholing_wanneer = ScholingWanneer.TIJDENS_WERKTIJD
    d.scholing_tijdens_werktijd = "op maandag"
    d.scholing_kosten = 350.5

    d.samenleving_regeling = JA
    d.samenleving_budget = JA
    d.budget_hoogte = SamenlevingBudgetHoogte.UREN_OF_DAGEN
    d.uren_of_dagen_aantal = 2
    d.uren_of_dagen_type = TijdEenheid.DAG
    d.uren_of_dagen_per = DagenPer.JAAR
    d.budget_naar_rato = JA
    d.budget_uitgekeerd = JA
    d.budget_uitgekeerd_voorwaarden = "Aan het eind van het jaar"
    d.budget_voorwaarden = JA
    d.budget_voorwaarden_namelijk = "Alleen voor erkende goede doelen"
    return f


def _variant() -> Formulier:
    """Andere takken: vast bedrag, geen opgenomen arbeidsvoorwaarden, geen fondsnaam, ander moment, percentage."""
    f = Formulier()
    ikb = f.individueel_keuzebudget
    ikb.ja_nee = JA
    ikb.waarde = Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=1200, per=Interval.JAAR))
    ikb.arbeidsvoorwaarden_opgenomen = NEE

    p = f.pensioen
    p.van_toepassing = JA
    p.werkgeverspremie_percentage = 10
    p.franchise = NEE

    d = f.duurzaam_werken_en_leven
    d.loopbaancoaching = RegelingVraagset(aangevinkt=True)  # alleen aangevinkt: lege regel
    d.inzetbaarheid_anders = RegelingVraagset(aangevinkt=True)  # zonder namelijk → "Anders, namelijk: null"
    d.vitaliteitsbudget = RegelingVraagset(aangevinkt=True, budget=BudgetOfGemiddeld.JA)  # geen type → lege regel
    d.verplichte_scholing = JA
    d.scholing_wanneer = ScholingWanneer.ANDER_MOMENT
    d.scholing_ander_moment = "in het weekend"
    d.scholing_tijd = 2
    d.scholing_tijd_type = TijdEenheid.DAG
    d.samenleving_regeling = JA
    d.samenleving_budget = JA
    d.budget_hoogte = SamenlevingBudgetHoogte.PERCENTAGE
    d.percentage = 0.5
    d.percentage_van = Loonbasis.JAARLOON  # geen tijdvak → "Year"
    d.budget_uitgekeerd = NEE
    d.budget_voorwaarden = JA  # zonder tekst → geen voorwaarde
    return f


def _vast_bedrag_samenleving() -> Formulier:
    f = Formulier()
    d = f.duurzaam_werken_en_leven
    d.samenleving_regeling = JA
    d.samenleving_budget = JA
    d.budget_hoogte = SamenlevingBudgetHoogte.VAST_BEDRAG
    d.vast_bedrag = 100
    d.budget_uitgekeerd = JA  # zonder voorwaarden: de korte tekst
    f.pensioen.van_toepassing = NEE
    f.individueel_keuzebudget.ja_nee = NEE
    d.verplichte_scholing = NEE
    return f


def _half() -> Formulier:
    """Alleen de hoofdvragen met "ja": de webform vult "null" en standaardwaarden in."""
    f = Formulier()
    f.individueel_keuzebudget.ja_nee = JA
    f.individueel_keuzebudget.arbeidsvoorwaarden_opgenomen = JA
    f.individueel_keuzebudget.adv_dagen = True  # zonder percentage en "van"
    f.pensioen.van_toepassing = JA
    f.pensioen.franchise = JA  # zonder beschrijving
    d = f.duurzaam_werken_en_leven
    d.verplichte_scholing = JA
    d.samenleving_regeling = JA
    d.samenleving_budget = JA
    d.budget_naar_rato = JA
    d.opleidingen = RegelingVraagset(aangevinkt=True, budget=BudgetOfGemiddeld.NEE_GEMIDDELD, naar_rato=JA)
    return f


def _uren_zonder_per() -> Formulier:
    f = Formulier()
    d = f.duurzaam_werken_en_leven
    d.samenleving_regeling = JA
    d.samenleving_budget = JA
    d.budget_hoogte = SamenlevingBudgetHoogte.UREN_OF_DAGEN
    d.uren_of_dagen_aantal = 8
    d.inzetbaarheid_geen = True
    d.vitaliteit_geen = True
    return f


SCENARIOS = {
    "rijk": _rijk,
    "variant": _variant,
    "vast_bedrag_samenleving": _vast_bedrag_samenleving,
    "half": _half,
    "uren_zonder_per": _uren_zonder_per,
    "leeg": Formulier,
}


def _zonder_grondslagen(verschillen: list[str]) -> list[str]:
    # Grondslagen (15) volgt uit de gekozen grondslag bij het IKB; die sectie is apart getest.
    return [v for v in verschillen if not v.startswith(".baseDefinition")]


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    antwoorden = naar_antwoorden(SCENARIOS[naam]())
    assert _zonder_grondslagen(vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))) == []


def test_rijk_bevat_alle_onderdelen():
    data = naar_setu.setu_json(_rijk())
    assert len(data["individualChoiceBudget"][0]["option"]) == 5
    assert data["pension"][0]["franchise"]["description"].startswith("Franchise")
    assert len(data["sustainableEmployability"]) == 14


def test_verborgen_budget_duurzame_samenleving_telt_niet(webform):
    """Een (achtergebleven) budgetantwoord zonder "ja" op de regeling wordt niet omgezet."""
    antwoorden = naar_antwoorden(_uren_zonder_per())
    antwoorden["duurzame-samenleving-regeling"] = "nee"
    onze = naar_setu.setu_json(antwoorden)
    assert "sustainableEmployability" not in onze
    assert vergelijk_setu(webform, antwoorden, onze) == []


@pytest.mark.parametrize("vervolg", [{"naar-rato": "ja"}, {"uitgekeerd": "nee"}, {"voorwaarden": "ja", "voorwaarden/ja/namelijk": "x"}])
def test_regeling_zonder_budgetregel_loopt_vast(webform, vervolg):
    """Webform-bug: zonder budgetregel leest de webform ``line[0]`` van een lege lijst en loopt de export vast."""
    slug = "vitaliteit-gezondheid-regelingen/vitaliteitsbudget"
    antwoorden = naar_antwoorden(Formulier())
    antwoorden[slug] = True
    antwoorden.update({f"{slug}/{k}": v for k, v in vervolg.items()})
    with pytest.raises(Exception, match="Cannot read properties of undefined"):
        webform.setu(antwoorden)
    with pytest.raises(TypeError, match="Cannot read properties of undefined"):
        naar_setu.setu_json(antwoorden)
