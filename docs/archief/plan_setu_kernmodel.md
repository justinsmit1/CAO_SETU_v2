# Plan: SETU-kernmodel (Inquiry Pay Equity v2.0)

*Status: concept, wacht op akkoord van Justin.*

## Waarom

Het formuliermodel (`src/cao_setu_v2/formulier/`) beschrijft het **wijzerbelonen-formulier**. Straks moeten ook
andere bronnen, zoals inlenersbeloning.com, kunnen aansluiten. De gemeenschappelijke taal is de **SETU-standaard**.
Het kernmodel is een Python-model van die standaard dat:

- elk geldig SETU-bestand kan inlezen, van welk formulier of welke leverancier dan ook;
- alleen geldige SETU-JSON kan wegschrijven;
- de basis is voor alle vertalingen: formulier ↔ SETU, en later inlenersbeloning ↔ SETU.

```
jouw applicatie
      ↕
SETU-kernmodel  ← dit plan
  ↕                    ↕
wijzerbelonen-model    inlenersbeloning (later)
(formulier/, bestaat)
```

## Bron: het officiële JSON-schema

- `json_schema_2.0.0_draft.json`: "SETU Inquiry Pay Equity v2.0", gegenereerd door Semantic Treehouse op
  2026-03-16. Het zit in de wijzerbelonen-webform; die valideert haar eigen export ermee.
- Omvang: **87 definities**:
  - 12 keuzelijsten, waaronder 64 toeslagcodes (`EA100`…) en 19 intervalcodes;
  - 2 "kies één van"-structuren: `Occurrence` (Single / Recurring / Relative) en `Condition` (9 soorten,
    waarvan 3 recursief: AllOf / AnyOf / Not);
  - 10 regelingen (allowance, holidayAllowance, sickPay, leave, IKB, pension, …).
- Het hoogste niveau vereist `documentId`, `effectivePeriod`, `customer` en `remuneration`. Extra velden
  zijn daar niet toegestaan.

**Belangrijke bevinding:** zelfs het officiële voorbeeld (`src/Informatie_SETU/InquiryPayEquity`) valideert
**niet** tegen het schema. Er zijn 12 fouten, onder andere:

| Wat | Voorbeeld | Schema |
|---|---|---|
| terugkerende datum | `recurringInterval` / `date` | vereist `interval` (maar definieert `recurringInterval`: fout in het schema zelf) |
| toeslagcode | `ORT` | alleen `EA…`/`HT…`-codes |
| grondslag | `RegularSalary` | bestaat niet |
| interval | `Occurrence` | bestaat niet |
| conditie | `"conditionType": "..."` | plaatshouder |
| aanvullende regeling | zonder `origin` | `origin` is verplicht |

Conclusie: in de praktijk komt SETU-JSON binnen die niet helemaal klopt. Het model moet streng kunnen zijn bij
het wegschrijven en bruikbaar blijven bij het inlezen.

## Ontwerp

### Waar het komt

`src/cao_setu_v2/setu/`:

| Module | Inhoud |
|---|---|
| `codes.py` | De 12 keuzelijsten uit het schema als enums, met de omschrijving uit het schema als label (zelfde `Keuze`-idee als in het formuliermodel) |
| `basis.py` | Gedeelde bouwstenen: `Identifier`, `EffectivePeriod`, `Amount` / `BaseAmount` / `Proportional`, `Interval`, `Period` / `DatePeriod` / `TimePeriod`, de drie regeltypen (`ArrangementLine`, `…Leave`, `…Limited`) |
| `tijd.py` | `Occurrence` = Single / Recurring / Relative, gekozen op `occurrenceType` |
| `condities.py` | `Condition` = 9 soorten, gekozen op `conditionType`, incl. geneste AllOf / AnyOf / Not |
| `partij.py` | `Party` (customer), `ContactPerson`, `Communication` |
| `beloning.py` | `RemunerationPackage`, `SalaryScale`, `SalaryScaleStep`, `WorkDuration`, verhogingen, `PositionProfile`, `BaseDefinition`, `LabourAgreements` |
| `regelingen.py` | Alle `…Arrangement`-klassen |
| `bericht.py` | `InquiryPayEquity`, de hoofdklasse, met `lees()` / `schrijf()` / `valideer()` |
| `schema/inquiry_pay_equity_2.0.0_draft.json` | Het officiële schema, vastgelegd in het project |

### Namen

Python-namen in het Engels, in `snake_case`, 1-op-1 met SETU. In de JSON automatisch de camelCase-naam:
`effective_period.valid_from` ↔ `effectivePeriod.validFrom`.

Het kernmodel spreekt zo de taal van de standaard en blijft naast de SETU-documentatie herkenbaar. Het
formuliermodel blijft Nederlands.

### Handgeschreven, met een automatische controle tegen het schema

- De klassen schrijf ik met de hand. Een gegenereerd model levert slecht leesbare namen op voor de
  "kies één van"-structuren.
- Een **conformiteitstest** loopt alle 87 definities van het schema langs en controleert:
  - dat elk veld in het model bestaat;
  - dat verplicht/optioneel klopt;
  - dat elke keuzelijst dezelfde waarden heeft.

  Zo mis je niets, en merk je het meteen als een nieuwe schemaversie iets verandert.

### Gebruik

```python
from cao_setu_v2.setu import InquiryPayEquity

bericht = InquiryPayEquity.lees(pad_of_json)             # streng: ongeldige SETU → duidelijke fout
bericht, meldingen = InquiryPayEquity.lees(pad, tolerant=True)   # zie hieronder

bericht.customer.name
for toeslag in bericht.allowance:
    print(toeslag.type_code, toeslag.line[0].amount.value)

bericht.schrijf("uit.json")      # altijd geldig volgens het schema
bericht.valideer()               # extra check met het officiële schema (jsonschema) → lijst fouten
```

### Streng en tolerant inlezen

- **Streng (standaard):** alleen wat het schema toestaat. Wegschrijven is altijd streng.
- **Tolerant** (`tolerant=True`): bekende afwijkingen worden rechtgezet, en je krijgt een lijst meldingen van
  wat er is aangepast. De eerste lijst regels, op basis van het voorbeeld en de webform:
  - `recurringInterval` ↔ `interval` (terugkerende datum);
  - `typeCode` als object `{ "value": … }` → als tekst;
  - `intervalCode` → `interval`;
  - getallen als tekst (`"1"`) → getal;
  - spelvarianten zoals `occurenceType` / `Recuring` en `Days`;
  - plaatshouders zoals `"conditionType": "..."` → weglaten, met een melding.

  Wat niet te herstellen is (bijv. `ORT` als toeslagcode) blijft een fout. In tolerante modus wordt het een
  melding, en het onderdeel wordt als "niet te lezen" bewaard.

  De lijst wordt aangevuld zodra er echte exports zijn, van wijzerbelonen en later van inlenersbeloning.

### Extra velden buiten SETU

`__webform_data__` (wijzerbelonen) en eventuele extra velden van andere leveranciers staan niet in het schema.
Die worden bij inlezen apart bewaard (`bericht.extensies`) en bij wegschrijven weer toegevoegd. Er gaat dus
niets verloren, en het SETU-deel blijft zuiver.

### Fout in het schema zelf (Recurring)

Het schema **vereist** `interval`, maar **definieert** `recurringInterval`. Voorstel: in Python één veld
(`recurring_interval`), dat bij wegschrijven onder **beide** namen wordt gezet. Het bestand valideert dan, en
elke lezer vindt de waarde. Dit kan eruit zodra SETU het schema repareert. Het is ook het melden waard bij
SETU / Semantic Treehouse.

## Stappen

1. **Schema vastleggen:** `tools/extraheer_schema.py` haalt het schema uit de webform-bundle en zet het in
   `src/cao_setu_v2/setu/schema/`. Bij een nieuwe webform-versie draai je het opnieuw.
2. **Afhankelijkheden** via `uv add`: `pydantic` (nu alleen indirect aanwezig), `jsonschema`, en als
   dev-afhankelijkheid `pytest`. `pyproject.toml` en `uv.lock` veranderen hierdoor.
3. **Bouwen:** `codes.py`, `basis.py`, `tijd.py` en `condities.py` eerst, daarna de regelingen en de
   hoofdklasse.
4. **`lees` / `schrijf` / `valideer`**, de extensies en de tolerante modus met meldingen.
5. **Tests** (`tests/test_setu.py`):
   - de conformiteitstest (model ↔ schema, alle 87 definities);
   - elk weggeschreven bericht valideert tegen het officiële schema;
   - het officiële voorbeeld: streng geeft precies de bekende fouten; tolerant leest het in en geeft meldingen;
   - inlezen → wegschrijven → inlezen geeft hetzelfde resultaat;
   - de keuzes tussen de conditie- en datumsoorten, incl. geneste AllOf / AnyOf / Not;
   - `__webform_data__` blijft bewaard.
6. **Demo** `examples/demo_setu.py`: een klein bericht opbouwen, valideren, wegschrijven en inlezen.

## Niet in dit plan

- De vertaling tussen het wijzerbelonen-formulier en SETU. Dat is de volgende fase; de SETU-kolom in
  `docs/formulier/` is daar de basis voor.
- Import en export van `__webform_data__` voor de wijzerbelonen-tool.
- Inlenersbeloning. Daarvoor is eerst een voorbeeldexport of API-documentatie nodig.

## Beslispunten voor Justin

1. **Namen in het Engels (SETU)** in het kernmodel, en Nederlands in het formuliermodel. Akkoord?
2. **Tolerant inlezen** als optie, met streng als standaard. Akkoord?
3. **Recurring onder beide veldnamen wegschrijven** als oplossing voor de schemafout. Akkoord?
4. **`pyproject.toml` / `uv.lock` aanpassen** (pydantic, jsonschema, pytest). Akkoord?
5. **Echte exports:** heb je een paar exports van wijzerbelonen? Die maken de tolerante regels en de tests
   veel sterker. Het is niet nodig om te beginnen.
