"""Eén blok invullen: zoeken → LLM → controleren → in het Formulier zetten.

Controle, in deze volgorde:
1. het antwoord volgt het schema (anders herkansing);
2. elke onderbouwing citeert letterlijk uit de fragmenten (anders telt hij niet);
3. elke ingevulde waarde heeft een onderbouwing (anders weggegooid);
4. het formuliermodel accepteert de waarden: keuzes, soorten bedragen en ``toon_als`` (anders één herkansing met de
   foutmelding; lukt het dan nog niet, dan worden de velden met een fout weggegooid).
Alles wat wegvalt, staat in het verslag. Liever een lege vraag dan een verzonnen antwoord.
"""

import json
import re
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ValidationError

from ...wijzerbelonen.formulier import Formulier
from ...wijzerbelonen.formulier.inspectie import vragen as alle_vragen
from ..llm import LLM
from ..zoeken import Fragment, Zoeker, zoek_voor_blok
from .blokken import Blok
from .omzetten import bladeren, valt_onder, van_waarden, verwijder
from .prompt import SYSTEEM, blok_bericht, herstel_bericht
from .rapport import BlokVerslag, Ingevuld, Onderbouwing
from .schema import antwoord_schema, blok_schema

MAX_WEGGOOIEN = 25


def vul_blok(
    blok: Blok, formulier: Formulier, llm: LLM, zoeker: Zoeker, top_k: int = 8, citaat_controle: bool = True
) -> BlokVerslag:
    """Vult één blok in ``formulier`` in (in place) en geeft het verslag terug."""
    verslag = BlokVerslag(blok.naam)
    model, velden = blok.model, blok.veldnamen()
    vragen = [v for v in alle_vragen(model) if re.split(r"[.\[{]", v.pad)[0] in velden]
    fragmenten = zoek_voor_blok(zoeker, blok, [v.vraag for v in vragen], top_k)
    if not fragmenten:
        verslag.meldingen.append("geen fragmenten gevonden in de cao")
    schema = antwoord_schema(blok_schema(model, velden))
    berichten = [
        {"role": "system", "content": SYSTEEM},
        {"role": "user", "content": blok_bericht(blok, vragen, fragmenten)},
    ]
    huidig = getattr(formulier, blok.sectie)

    uitkomst = None
    for poging in (1, 2):
        antwoord = llm.vraag_json(berichten, schema, blok.schema_naam)
        verslag.aanroepen += 1
        uitkomst = _verwerk(antwoord, schema, fragmenten, citaat_controle)
        if uitkomst["structuurfouten"]:
            fouten = uitkomst["structuurfouten"]
        else:
            try:
                nieuw = _valideer(model, huidig, velden, uitkomst["waarden"])
                _vastleggen(formulier, blok, nieuw, uitkomst, verslag)
                return verslag
            except ValidationError as fout:
                fouten = _foutteksten(fout)
        if poging == 1:
            verslag.meldingen.append(f"herkansing na {len(fouten)} fout(en): " + "; ".join(fouten[:3]))
            berichten += [
                {"role": "assistant", "content": json.dumps(antwoord, ensure_ascii=False)},
                {"role": "user", "content": herstel_bericht(fouten)},
            ]

    if uitkomst is None or uitkomst["structuurfouten"]:
        verslag.meldingen.append("antwoord volgt het schema niet, ook niet na de herkansing: blok niet ingevuld")
        return verslag
    return _weggooien_tot_geldig(formulier, blok, model, huidig, velden, uitkomst, verslag)


def _verwerk(antwoord: Any, schema: dict, fragmenten: list[Fragment], citaat_controle: bool) -> dict[str, Any]:
    structuurfouten = [
        f"{'/'.join(map(str, e.absolute_path)) or '(antwoord)'}: {e.message}"
        for e in Draft202012Validator(schema).iter_errors(antwoord)
    ]
    uit: dict[str, Any] = {"structuurfouten": structuurfouten, "ingevuld": [], "weggegooid": [], "niet_gevonden": []}
    if structuurfouten:
        return uit

    geldig = []
    for o in antwoord["onderbouwing"]:
        onderbouwing = Onderbouwing(o["pad"], o["document"], o["pagina"], o["artikel"], o["citaat"])
        if citaat_controle and not _staat_in(onderbouwing.citaat, fragmenten):
            uit["weggegooid"].append((onderbouwing.pad, "onderbouwing telt niet: het citaat staat niet in de fragmenten"))
            continue
        geldig.append(onderbouwing)

    waarden = antwoord["waarden"]
    for pad, waarde in bladeren(waarden):
        bron = next((o for o in geldig if valt_onder(pad, o.pad)), None)
        if bron is None:
            waarden = verwijder(waarden, pad)
            uit["weggegooid"].append((pad, f"geen onderbouwing (waarde was {waarde!r})"))
        else:
            uit["ingevuld"].append(Ingevuld(pad, waarde, bron))
    uit["waarden"] = waarden
    ingevuld = [i.pad for i in uit["ingevuld"]]
    uit["niet_gevonden"] = [p for p in antwoord["niet_gevonden"] if not any(valt_onder(i, p) for i in ingevuld)]
    return uit


def _staat_in(citaat: str, fragmenten: list[Fragment]) -> bool:
    gewoon = _normaal(citaat)
    return bool(gewoon) and any(gewoon in _normaal(f.tekst) for f in fragmenten)


def _normaal(tekst: str) -> str:
    return " ".join(re.sub(r"[*_`#>|]", " ", tekst).split()).lower()


def _valideer(model: type[BaseModel], huidig: BaseModel, velden: list[str], waarden: dict[str, Any]) -> BaseModel:
    """Het nieuwe sectiemodel: de bestaande waarden buiten het blok plus de waarden van het blok."""
    behouden = {k: getattr(huidig, k) for k in type(huidig).model_fields if k not in velden}
    return model.model_validate({**behouden, **van_waarden(model, waarden, velden)})


def _vastleggen(formulier: Formulier, blok: Blok, nieuw: BaseModel, uitkomst: dict, verslag: BlokVerslag) -> None:
    try:
        setattr(formulier, blok.sectie, nieuw)
    except ValidationError as fout:
        # Een voorwaarde tussen secties; het blok blijft staan, de eindcontrole meldt het ook.
        formulier.__dict__[blok.sectie] = nieuw
        verslag.meldingen.append("voorwaarde met een andere sectie klopt niet: " + "; ".join(_foutteksten(fout)))
    verslag.ingevuld += uitkomst["ingevuld"]
    verslag.weggegooid += uitkomst["weggegooid"]
    verslag.niet_gevonden += uitkomst["niet_gevonden"]


def _weggooien_tot_geldig(
    formulier: Formulier, blok: Blok, model, huidig, velden: list[str], uitkomst: dict, verslag: BlokVerslag
) -> BlokVerslag:
    """Na de herkansing: velden met een fout één voor één leeg maken, tot het model het accepteert."""
    waarden = uitkomst["waarden"]
    for _ in range(MAX_WEGGOOIEN):
        try:
            nieuw = _valideer(model, huidig, velden, waarden)
        except ValidationError as fout:
            weg = _velden_met_fout(fout, model, velden, waarden)
            if not weg:
                break
            reden = "voldoet niet aan het formulier: " + "; ".join(_foutteksten(fout)[:2])
            for veld in weg:
                waarden = {**waarden, veld: None}
                uitkomst["weggegooid"].append((veld, reden))
                uitkomst["ingevuld"] = [i for i in uitkomst["ingevuld"] if not valt_onder(i.pad, veld)]
            continue
        uitkomst["waarden"] = waarden
        _vastleggen(formulier, blok, nieuw, uitkomst, verslag)
        return verslag
    verslag.weggegooid += uitkomst["weggegooid"]
    verslag.meldingen.append("antwoord bleef ongeldig na de herkansing: blok niet ingevuld")
    return verslag


def _velden_met_fout(fout: ValidationError, model: type[BaseModel], velden: list[str], waarden: dict) -> list[str]:
    for e in fout.errors():
        if e["loc"] and e["loc"][0] in velden and waarden.get(e["loc"][0]) is not None:
            return [str(e["loc"][0])]
    # Een voorwaarde (toon_als) op het niveau van de sectie zelf: de melding noemt "Klasse.veld mag alleen ...".
    genoemd = re.findall(rf"\b{model.__name__}\.(\w+) mag alleen", str(fout))
    weg = [v for v in genoemd if v in velden and waarden.get(v) is not None]
    if weg:
        return weg
    return [v for v in velden if model.model_fields[v].json_schema_extra.get("toon_als") and waarden.get(v) is not None]


def _foutteksten(fout: ValidationError) -> list[str]:
    return [f"{'.'.join(map(str, e['loc'])) or '(blok)'}: {e['msg']}" for e in fout.errors()]
