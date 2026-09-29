# setu_kern: één SETU-kern, een adapter per bron

```
 bron                                   adapter                        kern
 ─────────────────────────────────      ─────────────────────────      ─────────────────────────────
 wijzerbelonen: Formulier in Python ─►  van_formulier(f)          ─┐
 wijzerbelonen: download (.json)    ─►  van_export(pad)           ─┼─►  Resultaat(bericht, meldingen, bron)
 later: LLM uit CAO-pdf, Excel, …   ─►  bronnen/<bron>/adapter.py ─┘        │
                                                                           ▼
                                                     InquiryPayEquity → SETU-JSON, valideren, vergelijken
```

## Drie begrippen

- **Kern (`kern/`).** `InquiryPayEquity`, het SETU-bericht Inquiry Pay Equity v2.0. Het wordt gecontroleerd tegen
  het officiële schema (`kern/schema/`). De kern weet niets van formulieren of tools.
- **Bron (`bronnen/<naam>/`).** Alles wat gegevens aanlevert. Een bron mag een eigen interne weergave hebben. Het
  wijzerbelonen-`Formulier` is zo'n interne weergave; het is niet de standaard.
- **Adapter.** Per bron de functies die naar de kern gaan. Ze geven altijd een `Resultaat` terug
  (`bronnen/__init__.py`):

  ```python
  @dataclass
  class Resultaat:
      bericht: InquiryPayEquity
      meldingen: list[str]   # wat is rechtgezet of weggelaten: niets verdwijnt stil
      bron: str              # bijv. "wijzerbelonen:export"
  ```

Vergelijken gebeurt altijd op de kern: bron A → `Resultaat`, bron B → `Resultaat`, en daarna vergelijk je de twee
berichten. Een formulier wordt nooit rechtstreeks met een ander formulier vergeleken.

## Bron wijzerbelonen

| Functie | Van | Naar |
|---|---|---|
| `van_formulier(f)` | `Formulier`, ingevuld in Python | `Resultaat` |
| `van_export(pad)` | download van wijzerbelonen.nl | `Resultaat` |
| `schrijf_upload(f, pad)` | `Formulier` | bestand om te importeren op wijzerbelonen.nl |

Een download bevat de SETU-JSON en `__webform_data__` (de antwoorden).
- `van_export` gaat uit van de antwoorden, net als de import van de tool. Een download en een `Formulier` met
  dezelfde antwoorden geven daardoor hetzelfde bericht.
- Een bestand met alleen SETU wordt rechtstreeks en tolerant ingelezen.
- Een afwijkende webform-versie geeft een melding.

De adapter vult aan wat SETU verplicht stelt, telkens met een melding. De constanten staan in `adapter.py`.
- Geen contactpersoon met naam → `STANDAARD_CONTACTPERSOON` (`"John Doe"`).
- Extra vakantiedagen per duur dienstverband: de webform laat `duration` en `referenceDateType` weg (bug).
  - De duur komt uit het antwoord (`jaar` → `P10Y`).
  - De referentiedatum vraagt het formulier niet. Die wordt `STANDAARD_REFERENTIEDATUM` (`HireDate`).

Scripts:
- `setu_kern_examples/maak_upload.py`: Formulier → upload + kernmodel.
- `setu_kern_examples/lees_export.py download.json`: download → kernmodel.

## Bron cao_pdf (LLM, raamwerk)

Een LLM vult per blok het wijzerbelonen-`Formulier` in op basis van de cao. De wijzerbelonen-adapter brengt het
daarna naar de kern. Een LLM-resultaat en een handmatige download komen zo via dezelfde weg in de kern.

```
cao-pdf ─► pijplijn (index) ─► per blok: zoeken → LLM (strict JSON) → controle ─► Formulier + Rapport
                                                                                   │ wijzerbelonen.van_formulier
                                                                                   ▼
                                                                         Resultaat(bron="cao_pdf")
```

| Onderdeel | Inhoud |
|---|---|
| `adapter.py` | `vul_formulier(llm, zoeker, parameters)` → (Formulier, Rapport); `van_cao_pdf(...)` → Resultaat |
| `llm.py` | het protocol `LLM.vraag_json(berichten, schema, naam)`; `MistralLLM(model)`. Er is geen standaardmodel: gebruik `[invullen] model = "..."` in config.toml of geef het model op |
| `zoeken.py` | het protocol `Zoeker.zoek(vraag, top_k)`; `IndexZoeker.laad("index")` (FAISS + Mistral-embeddings) |
| `parameters.py` | wat niet in de cao staat: naam, KvK, looptijd, contactpersoon (uit een TOML-bestand) |
| `invullen/blokken.py` | welke blokken het LLM invult; nu alleen **05 Vakantiebijslag** |
| `invullen/schema.py` | Formulier-(sub)model → strikt JSON-schema, met keuzes als enum en alleen de toegestane soorten bedragen |
| `invullen/omzetten.py` | LLM-JSON ↔ formuliermodel (voor alle 16 secties getest: zonder verlies heen en terug) |
| `invullen/uitvoeren.py` | per blok: zoeken → LLM → controle → in het Formulier zetten |
| `invullen/rapport.py` | per waarde document, pagina, artikel en citaat; wat niet gevonden of weggegooid is |
| `nep.py` | `NepLLM` en `LijstZoeker`, voor tests zonder API |
| `pijplijn/` | KOPIE van `cao_setu_v2/llm_pipeline` (pdf inlezen, index, zoeken) |

Controle per blok:
1. Het antwoord volgt het schema; anders volgt een herkansing.
2. Een citaat telt alleen als het letterlijk in de gevonden fragmenten staat.
3. Een waarde zonder geldige onderbouwing wordt weggegooid.
4. Het formuliermodel accepteert het antwoord: keuzes, soorten bedragen en `toon_als`. Zo niet, dan krijgt het LLM
   één herkansing met de foutmelding. Daarna worden de foute velden weggegooid.
5. "Niet gevonden" blijft leeg; het wordt nooit "nee".

Alles wat wegvalt, staat in het rapport.

Uitbreiden gaat per blok: voeg een `Blok` toe aan `BLOKKEN`, met een sectie, eventueel `velden` en zoektermen.
Salaristabellen (02) en de grote secties (04, 06, 12, 13) vragen waarschijnlijk extra werk aan het zoeken en een
splitsing in blokken.

Script: `setu_kern_examples/vul_met_llm.py --nep` is een demo zonder API. Met `--index index --parameters …`
gebruik je het echte LLM.

## Een nieuwe bron toevoegen

1. Maak `bronnen/<naam>/adapter.py` met een of meer functies `van_…(invoer) -> Resultaat`.
2. Zet alles wat de bron kent en SETU niet in `meldingen`.
3. Tests: het `bericht` is geldig (`resultaat.geldig`) en de meldingen dekken precies wat wegvalt.

## Herkomst

Dit pakket is een kopie. Het oude pakket `src/cao_setu_v2` blijft ongewijzigd bestaan.

| Map in setu_kern | Kopie van |
|---|---|
| `kern/` | `cao_setu_v2/setu/` |
| `bronnen/wijzerbelonen/formulier/` | `cao_setu_v2/formulier/` |
| `bronnen/wijzerbelonen/koppeling/` | `cao_setu_v2/koppeling/wijzerbelonen/` |

In de kopieën zijn alleen de imports aangepast. Nieuw zijn `bronnen/__init__.py` (het contract) en
`bronnen/wijzerbelonen/adapter.py`.

De tests staan in `setu_kern_tests/`; draai ze apart met `.venv\Scripts\python.exe -m pytest setu_kern_tests`.
Het pakket wordt niet geïnstalleerd: de tests en scripts zetten `src/` op `sys.path`.
