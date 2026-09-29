# Plan: het formulier laten invullen door een LLM

*Status: concept, wacht op akkoord van Justin.*

## Doel

Je geeft een cao-pdf. Een LLM vult daarmee het `Formulier` in. Elk antwoord krijgt een bronvermelding: artikel,
pagina en citaat. Jij controleert het resultaat en maakt daarna, zoals nu, de upload.

```
cao-pdf
   │  ingest                                        bestaat al (llm_pipeline: marker-pdf, cao_index, FAISS)
   ▼
index (artikelen/leden met pagina)
   │  per sectie of blok: zoeken → LLM → JSON      nieuw
   ▼
Formulier  +  rapport (bron per antwoord, niet gevonden, meldingen)
   │  controle door jou
   ▼
naar_setu / naar_antwoorden                         bestaat al
   ▼
SETU-JSON en upload voor wijzerbelonen
```

Het LLM schrijft niet zelf in de upload of in SETU, alleen in het `Formulier`. Het model controleert dan wat mag:
keuzes, soorten bedragen en `toon_als`. Een fout antwoord kan zo nooit ongemerkt in de tool terechtkomen.

## Wat er al is

| Onderdeel | Waar | Gebruik in dit plan |
|---|---|---|
| Alle vragen, met type, keuzes, eenheid, voorwaarde en herhaalbaar | `formulier/inspectie.py` → `vragen()` | vraagteksten en keuzes voor de prompt |
| De vragen als Pydantic-modellen, één per sectie | `formulier/sNN_*.py` | hieruit komt het JSON-schema, en ze controleren het antwoord |
| Controle van voorwaarden, ook tussen secties | `voorwaarden.py`, `Formulier.controleer()` | ongeldige antwoorden terugsturen of weggooien |
| Een cao-pdf inlezen en indelen in artikelen/leden | `llm_pipeline/extraction.py`, `cao_index.py` | ongewijzigd |
| Zoeken en een antwoord met citaten (Mistral, strict JSON-schema) | `llm_pipeline/store.py`, `qa.py` | het patroon voor de nieuwe aanroep |

## Wat de analyse laat zien

Aantal vragen per sectie, uit `vragen(Formulier)`. "Altijd zichtbaar" betekent: zonder `toon_als`.

| Sectie | Vragen | Altijd zichtbaar | Opmerking |
|---|---:|---:|---|
| 01 Algemeen | 13 | 8 | grotendeels over de organisatie, niet uit de cao |
| 02 Beloning | 70 | 15 | salaristabellen en schalen: tabellen in de pdf |
| 03 Functiegroepen | 3 | 3 | |
| 04 Toeslagen | 280 | 118 | grootste sectie, veel per toeslagsoort |
| 05 Vakantiebijslag | 7 | 6 | klein, goed als eerste proef |
| 06 Vergoedingen | 141 | 30 | |
| 07 Bijzondere uitkeringen | 70 | 32 | |
| 08 Loondoorbetaling bij ziekte | 14 | 6 | |
| 09 Verlof | 84 | 37 | |
| 10 IKB | 24 | 8 | |
| 11 Pensioen | 5 | 1 | |
| 12 Duurzaam werken en leven | 230 | 16 | veel checkboxen met vervolgvragen |
| 13 Aanvullende regelingen | 140 | 121 | |
| 14 Overig | 13 | 10 | |
| 15 Grondslagen | 6 | 5 | hangt af van gekozen grondslagen elders |
| 16 Ondertekenen | 5 | 5 | niet uit de cao |
| **Totaal** | **1105** | | 684 met voorwaarde, 476 in herhaalbare blokken, 471 met vaste keuzes |

Wat hieruit volgt:

- **Eén aanroep voor het hele formulier gaat niet.** Het schema wordt te groot en de context te breed. We roepen het
  LLM aan per sectie. Grote secties (04, 06, 12, 13) splitsen we per blok: de velden op het hoogste niveau van de
  sectie.
- **Eén aanroep per vraag is te veel en verliest samenhang.** Een salaristabel met schalen en stappen hoort in één
  antwoord.
- **Voorwaarden.** Het LLM krijgt de voorwaarden als tekst mee ("vul `bedrag` alleen in als `ja_nee = ja`"). Het
  model controleert ze daarna. Bij een fout sturen we de foutmelding één keer terug; lukt het dan nog niet, dan maken
  we het veld leeg en komt het in de meldingen.
- **Niet alles staat in de cao.** Naam, KvK, sector, "waarom is de cao van toepassing" en ondertekenen komen uit
  parameters, niet van het LLM.

### Valkuilen

- **`toon_als` binnen een Bedragregel.** De delen `vast_bedrag`/`percentage`/`tijd` hangen af van `soort`, niet
  van de vraag erboven. `vragen()` toont daar geen voorwaarde (bij 05: 6 van 7 "altijd zichtbaar"). De prompt moet
  de Bedragregel dus als één geheel uitleggen, met alleen de soorten die bij die vraag mogen (`opties`).
- **Tabellen.** Salaristabellen staan in de pdf als tabel. `cao_index` knipt stukken van meer dan 1600 tekens, dus
  een tabel kan in stukken terechtkomen. Voor 02 is waarschijnlijk een eigen zoekstap nodig die de hele bijlage
  of tabel ophaalt.
- **Zoekvraag.** Een formuliervraag als "Zijn er periodieke verhogingen?" is een zwakke zoekvraag. Per blok
  combineren we daarom de vraagteksten met een paar vaste zoektermen (bijvoorbeeld "periodiek", "trede",
  "salarisverhoging").
- **"Nee" of "niet gevonden".** Dat de cao niets zegt, is iets anders dan "nee". Het LLM moet onderscheid maken
  tussen `niet_gevonden` en een expliciet antwoord. We zetten nooit `JaNee.NEE` zonder citaat.
- **Het model.** `config.toml` gebruikt nu `open-mistral-7b`. Dat is te klein voor geneste strict-schema's met
  tientallen velden (beslispunt 1).
- **Herhaalbare blokken.** Het LLM kan rijen verzinnen, bijvoorbeeld een schaal die er niet is. Elke rij moet
  daarom een eigen citaat hebben.
- **Getallen en datums.** Komma of punt als decimaalteken, "8%" of "8", en een looptijd als tekst. Een eigen
  Pydantic-laag maakt dat gelijk voordat het in het `Formulier` gaat.

## Ontwerp

### Waar het komt

`src/cao_setu_v2/llm_pipeline/invullen/`:

| Module | Inhoud |
|---|---|
| `schema.py` | `blok_schema(model)`: van een submodel (bijv. `Vakantiebijslag`) naar een JSON-schema dat met strict mode werkt: alles `required`, lege velden als `null`, `additionalProperties: false`, keuzes als `enum` met het label in de `description`. Staat een veld `opties` toe, dan komen in de enum alleen die waarden |
| `blokken.py` | de indeling in aanroepen: welke secties heel, welke per blok, en per blok de extra zoektermen. Ook de lijst met vragen die niet uit de cao komen (overslaan of uit parameters) |
| `vraagteksten.py` | optioneel: per pad een betere vraag of uitleg voor het LLM, als de tekst van het webformulier onduidelijk is. Standaard gebruiken we de tekst van `vragen()` |
| `prompt.py` | systeemprompt en blokprompt: vragen, voorwaarden als tekst, uitleg van de Bedragregel, gevonden cao-stukken |
| `aanroep.py` | zoeken in de index, LLM-aanroep met `response_format` json_schema, `model_validate`, één herkansing met de foutmelding |
| `invullen.py` | `vul_in(index, secties, parameters) -> (Formulier, Rapport)`. Roept de blokken aan in volgorde (15 als laatste), zet de antwoorden in het `Formulier` en draait aan het eind `Formulier.controleer()` |
| `rapport.py` | per ingevuld veld: waarde, artikel, pagina, citaat. Plus wat niet gevonden is, wat na controle weggegooid is en wat uit parameters komt. Wordt geschreven als Markdown (voor jou) en als JSON |

Het antwoord van het LLM per blok:

```json
{
  "waarden": { "…": "het submodel volgens blok_schema" },
  "onderbouwing": [
    {"pad": "bedrag.percentage.percentage", "artikel": "Artikel 12 lid 1", "pagina": 14,
     "citaat": "De vakantiebijslag bedraagt 8% van het jaarsalaris."}
  ],
  "niet_gevonden": ["ja_nee"]
}
```

Een ingevuld veld zonder onderbouwing wordt weggegooid en komt in het rapport.

### Gebruik

Nieuw subcommando in `llm_pipeline/cli.py`:

```powershell
.venv\Scripts\python.exe -m cao_setu_v2.llm_pipeline.cli invul --secties 05 --uit uitvoer\llm_formulier.json
```

Dit schrijft `uitvoer\llm_formulier.json` (`Formulier.model_dump_json()`) en `uitvoer\llm_rapport.md`. Een nieuw
voorbeeld `examples\maak_upload_llm.py` leest het formulier in (`Formulier.model_validate_json`) en gebruikt de
bestaande `verwerk()` uit `maak_upload.py` voor SETU en de upload.

### Controle

1. **Zonder LLM (unit tests).** `blok_schema` voor elke sectie en elk blok: het schema is geldig, en een voorbeeld
   uit `maak_upload_full.py` valideert ertegen. Een nep-client met vaste antwoorden test het invullen, de
   herkansing, het weggooien bij een schending en de ontbrekende onderbouwing.
2. **Rondgang.** `maak_upload_full.py` → per blok als "LLM-antwoord" → `vul_in` moet precies hetzelfde `Formulier`
   opleveren. Zo weten we dat schema en invullen niets verliezen.
3. **Kwaliteit met een echte cao.** Voor `data/cao_test.pdf` vul je per sectie één keer met de hand een
   referentie in (`tests/referentie/cao_test_formulier.json`). Een los script (geen pytest, want het kost
   API-aanroepen) vergelijkt het LLM-resultaat daarmee: goed, fout, gemist en verzonnen, per sectie.

## Stappen

Na elke stap is er een review door jou.

| Stap | Inhoud | Moeilijkheid |
|---|---|---|
| **0** | Raamwerk: `schema.py`, `prompt.py`, `aanroep.py`, `invullen.py`, `rapport.py`, het CLI-commando en de tests met de nep-client. Helemaal af voor **05 Vakantiebijslag**, getest op `cao_test.pdf` | middel |
| **A** | Eenvoudige secties: 01 (alleen het cao-deel, de rest uit parameters), 08 Ziekte, 10 IKB, 11 Pensioen, 14 Overig. Referentie-invulling voor deze secties plus het vergelijkingsscript | laag |
| **B** | 02 Beloning en 03 Functiegroepen: salaristabellen, schalen en stappen, met een aparte zoekstap voor tabellen/bijlagen | hoog |
| **C** | 06 Vergoedingen, 07 Bijzondere uitkeringen, 09 Verlof: per blok | middel |
| **D** | 04 Toeslagen, 12 Duurzaam werken, 13 Aanvullende regelingen: veel blokken en voorwaarden | hoog |
| **E** | 15 Grondslagen (als laatste; hangt af van de rest), controle over het hele formulier, `maak_upload_llm.py` en de kwaliteitsmeting over alle secties | middel |

Na stap A werkt het al van begin tot eind voor een deel van het formulier. De secties die dan nog ontbreken, blijven
leeg en staan in het rapport als "nog niet ondersteund".

## Beslispunten voor Justin

1. **Welk model?**
   - *Voorstel:* bij Mistral blijven (API-sleutel en embeddings zijn er al) en voor het invullen overstappen naar
     `mistral-large-latest`. `open-mistral-7b` blijft voor `ask`.
   - Dit wordt een aparte instelling in `config.toml` (`invul_model`), zodat je later makkelijk kunt vergelijken.
2. **Hoe fijn de aanroepen zijn.**
   - *Voorstel:* per sectie, en grote secties per blok (zie Ontwerp).
   - *Alternatief:* per vraag, stap voor stap langs de voorwaarden. Preciezer, maar tientallen keren meer aanroepen en
     de samenhang binnen een blok gaat verloren.
3. **Vraagteksten.**
   - *Voorstel:* de teksten van het webformulier houden en alleen herschrijven waar de kwaliteitsmeting laat zien dat
     het misgaat (`vraagteksten.py`).
   - *Alternatief:* alle 1105 vragen vooraf herschrijven voor het LLM. Veel werk, en het voordeel is onzeker.
4. **Vragen die niet uit de cao komen.**
   - *Voorstel:* naam en KvK van de organisatie, sector en contactgegevens als parameters (`--parameters
     organisatie.toml`). Ondertekenen blijft leeg, dat doe je in de tool.
5. **Wat bij twijfel?**
   - *Voorstel:* leeg laten en in het rapport zetten als "niet gevonden". Liever een lege vraag die je zelf invult dan
     een verzonnen antwoord.
   - *Alternatief:* het LLM een beste gok laten doen, gemarkeerd als "onzeker".
6. **Waar het resultaat heen gaat.**
   - *Voorstel:* eerst `llm_formulier.json` en het rapport, niet direct een upload. De upload maak je pas na je
     controle, met `maak_upload_llm.py`.

## Niet in dit plan

- Betere zoekmethodes in `llm_pipeline`, zoals hybride zoeken (BM25), een aparte index voor tabellen buiten stap B,
  of werkingssfeer. Die staan al als "niet in scope" in `cao_index.py`.
- Meerdere cao's of versies tegelijk invullen (de index kan het wel, het invullen kiest één versie).
- Een eigen arbeidsvoorwaardenregeling zonder cao als bron. Dat werkt in principe hetzelfde, maar is niet getest.
- Een gebruikersinterface om het rapport te controleren; voorlopig is dat het Markdown-bestand.
