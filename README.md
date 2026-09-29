# CAO SETU v2

Arbeidsvoorwaarden vastleggen volgens de SETU-standaard **Inquiry Pay Equity v2.0** (Gelijkwaardig Belonen) en
uitwisselen met de wijzerbelonen-webform (https://standaard-uitvraag.wijzerbelonen.nl/).

## Snel starten

```powershell
uv sync                                          # eenmalig: omgeving en pakketten
.venv\Scripts\python.exe examples\maak_upload.py
```

`maak_upload.py` doet drie dingen:

1. **Vult het Python-formulier** (`vul_formulier()`). Pas dit aan met je eigen gegevens. Het model controleert
   direct of een optie mag en of een vraag zichtbaar is.
2. **Maakt het SETU-kernmodel** (`InquiryPayEquity`) en schrijft dat als `uitvoer\setu_kernmodel.json`. Dit is de
   standaard, geschikt om te vergelijken met SETU uit andere formulieren of bronnen.
3. **Schrijft een uploadbestand** voor wijzerbelonen.nl: `uitvoer\wijzerbelonen_upload.json`. Dit bestand upload je
   in de tool via **Importeren**.

## Mappen

| Map | Inhoud |
|---|---|
| `examples/` | `maak_upload.py`: het hoofdscript, met het hele formulier; `maak_upload_full.py`: voorbeeld waarin vrijwel elke vraag is ingevuld; `invulhulp.py`: maakt `INVULHULP.md` (alle vragen en keuzes per sectie) |
| `src/cao_setu_v2/formulier/` | het wijzerbelonen-formulier als Python-model, één module per sectie |
| `src/cao_setu_v2/setu/` | het SETU-kernmodel (`InquiryPayEquity`): inlezen, wegschrijven en valideren tegen het officiële schema (`setu/schema/`) |
| `src/cao_setu_v2/koppeling/wijzerbelonen/` | de omzetting van formulier naar de antwoorden van de tool (`__webform_data__`) en naar SETU-JSON |
| `src/cao_setu_v2/llm_pipeline/` | losse tool: cao-pdf's doorzoeken en er vragen over stellen met Mistral (gebruikt `config.toml`) |
| `tests/` | alle tests; `tests/referentie/` bevat de echte webformcode om tegen te testen |
| `tools/` | `extraheer_schema.py`: haalt het SETU-schema opnieuw uit de webform (bij een nieuwe versie van de tool) |
| `docs/` | documentatie, zie hieronder |
| `data/` | voorbeeldbestanden (cao-pdf voor de LLM-tool) |
| `uitvoer/` | wat de scripts schrijven |

## Documentatie

- `docs/koppeling_wijzerbelonen.md`: hoe de koppeling werkt en getest is, met de fouten van de tool die bewust zijn
  nagedaan.
- `docs/formulier/`: alle vragen van het webformulier, per sectie.
- `docs/setu_bron/`: de SETU-documentatie en het officiële voorbeeld.
- `docs/plan_setu_naar_wijzerbelonen.md`: een open plan om het SETU-model als enige invoer te gebruiken.
- `docs/plan_llm_invullen.md`: een open plan om het formulier door een LLM te laten invullen vanuit een cao-pdf.
- `docs/nieuwe_versie_setu_of_webform.md`: stappenplan voor een nieuwe versie van SETU of van de webform.
- `docs/archief/`: afgeronde plannen.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest -q tests
```

De tests vergelijken de uitvoer met de échte webformcode (v2.1.0). Die draait zonder browser via `mini-racer`, een
dev-afhankelijkheid.
