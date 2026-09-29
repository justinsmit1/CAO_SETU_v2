# Plan: setu_kern, één SETU-kern met een adapter per bron

*Status 2026-09-28: kern + bron wijzerbelonen klaar; raamwerk bron cao_pdf (LLM) klaar, getest met een nep-LLM.
Het model is nog niet gekozen.*

## Het idee

```
 bron                                   adapter                        kern
 wijzerbelonen: Formulier in Python ─►  van_formulier(f)          ─┐
 wijzerbelonen: download (.json)    ─►  van_export(pad)           ─┼─►  Resultaat(bericht, meldingen, bron)
 cao-pdf via LLM                    ─►  van_cao_pdf(llm, zoeker)  ─┘        │
                                                                           ▼
                                                     InquiryPayEquity → SETU-JSON, valideren, vergelijken
```

- **Kern** (`src/setu_kern/kern/`): `InquiryPayEquity`, gecontroleerd tegen het officiële SETU-schema.
- **Bron** (`src/setu_kern/bronnen/<naam>/`): alles wat gegevens aanlevert, met een eigen adapter.
- **Contract:** elke adapter geeft `Resultaat(bericht, meldingen, bron)` terug. Wat wegvalt of wordt aangevuld,
  staat in de meldingen.
- **Randvoorwaarde:** de oude code (`src/cao_setu_v2`, `tests/`, `examples/`) blijft ongewijzigd. De nieuwe map
  bestaat uit kopieën plus nieuwe code.

Uitleg per onderdeel: `src/setu_kern/README.md`.

## Wat klaar is

| Onderdeel | Waar | Status |
|---|---|---|
| Kern (kopie van `cao_setu_v2/setu`) | `src/setu_kern/kern/` | klaar |
| Bron wijzerbelonen: Formulier → kern, download → kern, upload | `src/setu_kern/bronnen/wijzerbelonen/adapter.py` | klaar |
| Aanvullingen: contactpersoon "John Doe", duur dienstverband (`P10Y` + `HireDate`) | idem, `STANDAARD_*`-constanten | klaar |
| Download inlezen | `setu_kern_examples/lees_export.py` | klaar, getest met de echte Koppert-download |
| LLM-raamwerk: schema, omzetting, prompt, controle, herkansing, rapport, parameters | `src/setu_kern/bronnen/cao_pdf/` | klaar voor blok **05 Vakantiebijslag** |
| Nep-LLM en eenvoudige zoeker voor tests | `src/setu_kern/bronnen/cao_pdf/nep.py` | klaar |
| Demo zonder API | `setu_kern_examples/vul_met_llm.py --nep` | klaar |
| Tests | `setu_kern_tests/` (170, waarvan 15 voor het LLM) | groen |

## Nog te doen (in deze volgorde, na elke stap een review)

| Stap | Inhoud | Moeilijkheid |
|---|---|---|
| **1** | **Model kiezen.** Zet `[invullen] model = "..."` in `config.toml`. Daarna één echte proef met 05 op een cao-pdf, bijv. de Koppert-cao | beslissing |
| **2** | **02 Beloning** als blok: salaristabellen, schalen en stappen. Er is waarschijnlijk een aparte zoekstap nodig die een hele tabel of bijlage ophaalt, omdat `cao_index` tabellen in stukken knipt. Zonder 02 komt er geen kernmodel uit de cao, want SETU eist een salaristabel | hoog |
| **3** | **Vergelijken op de kern:** `vergelijk(bericht_a, bericht_b)` (begin in `kern/conformiteit.py`). Daarmee leg je het LLM-resultaat naast de handmatige Koppert-download | middel |
| **4** | Eenvoudige secties als blok: 08 Ziekte, 10 IKB, 11 Pensioen, 14 Overig, en het cao-deel van 01 | laag |
| **5** | 06 Vergoedingen, 07 Bijzondere uitkeringen, 09 Verlof, per blok | middel |
| **6** | 04 Toeslagen, 12 Duurzaam werken, 13 Aanvullende regelingen, gesplitst per blok. Het schema van 04 is ~95.000 tekens en moet dus in blokken | hoog |
| **7** | 15 Grondslagen als laatste (hangt af van de rest), daarna een kwaliteitsmeting over alle secties | middel |

Later en los hiervan:
- een download terug inlezen als `Formulier`, om aan te passen en opnieuw te uploaden;
- SETU → wijzerbelonen-upload (`docs/plan_setu_naar_wijzerbelonen.md`).

## Open beslissingen

1. **Welk model?** Nog niet gekozen. Er is bewust geen standaardmodel.
2. **Welke cao-pdf wordt de testcase?** Het liefst de Koppert-cao, want van Koppert is er al een handmatig
   ingevulde download als referentie.
3. **`referenceDateType`** bij extra vakantiedagen per duur dienstverband: nu `HireDate`. Aan te passen via
   `STANDAARD_REFERENTIEDATUM` in `bronnen/wijzerbelonen/adapter.py`.

## Handige commando's

```powershell
# alle tests van de nieuwe map (apart van de oude tests draaien)
.venv\Scripts\python.exe -m pytest setu_kern_tests

# een download van wijzerbelonen.nl inlezen als kernmodel
.venv\Scripts\python.exe setu_kern_examples\lees_export.py C:\Users\JustinSmit\Downloads\ingevuld_wijzerbelonen.json

# LLM-demo zonder API
.venv\Scripts\python.exe setu_kern_examples\vul_met_llm.py --nep

# echt: cao indexeren en invullen (na stap 1)
.venv\Scripts\python.exe -m setu_kern.bronnen.cao_pdf.pijplijn.cli ingest data\cao.pdf --index-dir index
.venv\Scripts\python.exe setu_kern_examples\vul_met_llm.py --index index --parameters organisatie.toml
```
