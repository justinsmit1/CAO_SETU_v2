"""01 Algemeen, 05 Vakantiebijslag, 16 Ondertekenen: formulier → antwoorden → SETU, vergeleken met de webform."""

import datetime as dt

from cao_setu_v2.formulier import Formulier
from cao_setu_v2.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage
from cao_setu_v2.formulier.codes import Grondslag, Interval, JaNee, Loonbasis
from cao_setu_v2.formulier.s01_algemeen import CaoOfRegeling, CaoVanToepassingOmdat, TypeIdentificatienummer
from cao_setu_v2.formulier.s16_ondertekenen import Contactpersoon
from cao_setu_v2.koppeling.wijzerbelonen import naar_setu
from cao_setu_v2.koppeling.wijzerbelonen.antwoorden import naar_antwoorden
from referentie.controle import antwoord_problemen, vergelijk_setu


def _formulier() -> Formulier:
    f = Formulier()
    a = f.algemeen
    a.naam_regeling = "Regeling Bouw 2026"
    a.geldig_van = dt.date(2026, 1, 1)
    a.geldig_tot = dt.date(2026, 12, 31)
    a.opdrachtgever_naam = "Voorbeeld Bouw B.V."
    a.opdrachtgever_kvk = "12345678"
    a.opdrachtgever_kvk_type = TypeIdentificatienummer.KVK
    a.sector = "Bouw"
    a.cao_of_regeling = CaoOfRegeling.CAO_EN_EIGEN_REGELING
    a.cao_naam = "Cao Bouw & Infra"
    a.cao_nummer = "1496"
    a.cao_van_toepassing_omdat = CaoVanToepassingOmdat.ALGEMEEN_VERBINDEND
    a.cao_van = dt.date(2025, 6, 1)
    a.cao_tot = dt.date(2027, 5, 31)
    f.vakantiebijslag.ja_nee = JaNee.JA
    f.vakantiebijslag.bedrag = Bedragregel(
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=8.5, basis=Loonbasis.JAARLOON, per=Interval.JAAR, grondslag=Grondslag.BRUTO_LOON),
    )
    f.ondertekenen.contactpersonen.append(Contactpersoon(naam="J. Jansen", email="hr@voorbeeld.nl", telefoon="+31201234567", functie="HR"))
    f.ondertekenen.contactpersonen.append(Contactpersoon(naam="P. de Vries"))
    f.ondertekenen.akkoord = True
    return f


def test_antwoorden_passen_op_de_webform(webform):
    assert antwoord_problemen(webform, naar_antwoorden(_formulier())) == []


def test_setu_gelijk_aan_webform(webform):
    antwoorden = naar_antwoorden(_formulier())
    # Inclusief Grondslagen (15): de grondslag bij de vakantiebijslag levert een baseDefinition op.
    assert vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden)) == []


def test_leeg_formulier(webform):
    antwoorden = naar_antwoorden(Formulier())
    assert antwoord_problemen(webform, antwoorden) == []
    assert vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden)) == []
