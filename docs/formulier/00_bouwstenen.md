# 00 · Gedeelde bouwstenen

Patronen en keuzelijsten die in meerdere secties terugkomen. Sectiebestanden verwijzen hiernaar in plaats van
ze te herhalen.

Bron: `src/definition/constants.ts`, `util.ts`, `util_question_makers.tsx` (webformulier v2.1.0).

---

## B1 · Bedragregel (`makeLineAmountQuestions`)

Een set vragen om één bedrag, percentage of aantal uren vast te leggen. Wordt aangeroepen met een
**slug-prefix** (bijv. `vakantiebijslag`); alle slugs hieronder staan dan onder `<prefix>/...`.

Varianten per aanroep (opties van `makeLineAmountQuestions`):

| Optie | Standaard | Effect |
|---|---|---|
| `includeFixedAmountQuestions` | ja | toont keuze *Vast bedrag* + bijbehorende vragen |
| `includeTimeQuestions` | ja | toont keuze *In tijd* + bijbehorende vragen |
| `includeIntervalQuestions` | ja | toont de "per"-vragen |
| `includeNotApplicable` | nee | voegt keuze *N.v.t.* toe |
| `optional` | nee | de hoofdvraag `amount-type` is optioneel |

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | SETU |
|---|---|---|---|---|---|---|
| *(vraagtekst verschilt per aanroep)* | `<p>/amount-type` | radio | Vast bedrag → `vast-bedrag` · Percentage van loon → `percentage` · In tijd → `tijd` · N.v.t. → `n/a` | — | var. | bepaalt `line[]` |
| ↳ Bedrag (€) | `<p>/vast-bedrag/bedrag` | getal | — | amount-type = `vast-bedrag` | | `amount.value`, `unitCode: Euro`, `baseAmount.unitCode: Fixed` |
| ↳ per | `<p>/vast-bedrag/per` | keuzelijst | [B2 Interval](#b2--interval-per) | amount-type = `vast-bedrag` | | `interval.unitCode` (`interval.value` = 1) |
| ↳ Percentage (%) | `<p>/percentage/percentage` | getal | — | amount-type = `percentage` | | `amount.value`, `unitCode: Percentage` |
| ↳ van | `<p>/percentage/basis` | keuzelijst | [B3 Loonbasis](#b3--loonbasis-van) | amount-type = `percentage` | | `amount.baseAmount.unitCode` |
| ↳ per | `<p>/percentage/per` | keuzelijst | [B2 Interval](#b2--interval-per) | amount-type = `percentage` | | `interval.unitCode` |
| ↳ grondslag | `<p>/percentage/grondslag` | keuzelijst | [B4 Grondslag](#b4--grondslag) | amount-type = `percentage` | ja | `amount.baseAmount.baseType` |
| ↳ Aantal (uur) | `<p>/tijd/uur` | getal | — | amount-type = `tijd` | | `amount.value`, `unitCode: Hour`, `baseAmount.unitCode: Fixed` |
| ↳ per | `<p>/tijd/per` | keuzelijst | [B2 Interval](#b2--interval-per) | amount-type = `tijd` | | `interval.unitCode` |

Bij `n/a` levert de regel een leeg object op en wordt er niets naar SETU geschreven.

**Let op:** een gekozen grondslag (`percentage/grondslag`) zorgt ervoor dat die grondslag verschijnt in sectie
[15 Grondslagen](15_grondslagen.md).

---

## B2 · Interval "per" (`intervalCodeOptions`)

| Label | Waarde |
|---|---|
| Uur | `Hour` |
| Dag | `Day` |
| Week | `Week` |
| Maand | `Month` |
| Kwartaal | `Quarter` |
| Jaar | `Year` |
| Dagdeel | `DayPart` |
| Dienst | `Shift` |
| Eenmalig | `Once` |
| Gewerkte dag | `WorkedDay` |
| Item | `Item` |
| Kilometer | `Kilometer` |
| Nacht | `Night` |
| Op declaratie basis | `OnExpenseBasis` |
| Rit | `Trip` |
| Route | `Route` |
| Thuiswerkdag | `WorkFromHomeDay` |
| Verhuizing | `Relocation` |
| Wekelijkse reisdag | `WeeklyTravelDay` |

## B3 · Loonbasis "van" (`baseUnitOptions`)

| Label | Waarde |
|---|---|
| Uurloon | `HourlyRate` |
| Dagloon | `DailyRate` |
| 4-weken loon | `FourWeeklyRate` |
| Maandloon | `MonthlyRate` |
| Jaarloon | `YearlyRate` |

(In de code uitgeschakeld: *Uitgave* `Expense`, *Vast bedrag* `Fixed`.)

## B4 · Grondslag (`baseDefinitionOptions`)

| Label | Waarde |
|---|---|
| Basisloon grondslag | `BaseWage` |
| Bruto loon grondslag | `GrossSalary` |
| SVLoon grondslag | `SocialInsuranceWage` |
| Vakantiebijslag grondslag | `HolidayAllowance` |
| Pensioen grondslag | `Pension` |
| 13e maand grondslag | `13thMonth` |
| Gebruikelijk loon grondslag | `UsualWage` |

## B5 · Peildatum / referentiedatum (`referenceDateOptions`)

| Label | Waarde | Hulptekst |
|---|---|---|
| Anciënniteitsdatum | `SeniorityDate` | In geval van opvolgend werkgeverschap of overname |
| Datum indiensttreding | `HireDate` | |
| Startdatum contract | `ContractStartDate` | |
| Startdatum plaatsing | `AssignmentStartDate` | |

## B6 · Ja / Nee

Radio met opties *Ja* → `ja` en *Nee* → `nee`. Vervolgvragen hebben meestal de voorwaarde `<slug> = ja`.

## B7 · "Anders, namelijk"

Constante `ANDERS_NAMELIJK = "anders"`. Een optie met waarde `anders` gaat vrijwel altijd samen met een
tekstveld `<slug>/anders/namelijk` (of vergelijkbaar), dat alleen zichtbaar is als `anders` gekozen is.

## B8 · Werkduur-interval (`workDuration2Interval`)

Gebruikt in [02 Beloning](02_beloning.md) om het salaristabel-interval om te zetten naar SETU:

| Formulierwaarde | SETU `interval` |
|---|---|
| `per-maand` | 1 × `Month` |
| `per-vier-weken` | 4 × `Week` |
| `per-week` | 1 × `Week` |
| `per-uur` | 1 × `Hour` |

## B9 · Loonbasis → interval (`baseAmountUnitCodeToInterval`)

| Loonbasis | Interval |
|---|---|
| `DailyRate` | `Day` |
| `HourlyRate` | `Hour` |
| `MonthlyRate` | `Month` |
| `Fixed` | `Once` |
| `YearlyRate` | `Year` |

---

## B10 · Vaste SETU-standaardwaarden van het formulier

Het formulier vult een aantal SETU-velden altijd met een vaste waarde, omdat het formulier er (nog) niet naar vraagt:

| Constante | Waarde | Gebruikt voor |
|---|---|---|
| `TODO_REPLACE_WITH_REAL_ORIGIN` | `Unknown` | `origin.type` van alle regelingen |
| `TODO_REPLACE_WITH_REAL_CURRENCY` | `EUR` | `salaryScale.currency` |
| `TODO_REPLACE_WITH_REAL_TYPECODE` | `EA100` | standaard `typeCode` als er geen specifieke is |

Verder zet de export altijd een nieuw `documentId` (uuid, `schemeAgencyId: Customer`) en `issued` (tijdstip van
export). Zie ook [02 Beloning](02_beloning.md) en [15 Grondslagen](15_grondslagen.md).

## B11 · Vaste posities in SETU-lijsten (`constants.ts`)

Het formulier schrijft vaste onderdelen naar een vaste index in de SETU-lijst. Dat bepaalt de volgorde in de
export en is nodig voor de mapping in een latere fase.

| SETU-lijst | Indexen (0, 1, 2, …) |
|---|---|
| `holidayAllowance` | PERCENTAGE_PERIOD, PERCENTAGE_MINIMUM |
| `allowance` | PAID_BREAKS, TRAVEL_HOME_WORK_OV, TRAVEL_WORK_WORK_OV, TRAVEL_OTHER, REISKOSTEN, STANDBY, ZORGVERZEKERING, THUISWERKVERGOEDING, INTERNETVERGOEDING, ONREGELMATIGHEIDS_TOESLAGEN, PLOEGETOESLAGEN, TOESLAGEN_VERSCHOVEN_DIENSTEN, TOESLAGEN_FYSIEKE_BELAS, TOESLAGEN_STANDBY, OVERWERK_TOESLAG, WAARNEMINGSTOESLAG, PERFORMANCETOESLAG, TIJD_VOOR_TIJD, TOESLAGEN_ANDERS, KOFFIEGELD, MAALTIJDVERGOEDING, WASVERGOEDING, VERGOEDING_BEDRIJFSKLEDING_SCHOENEN, ARBO_VERGOEDING, BYOD_VERGOEDING, VERGOEDING_ANDERS, MOBILITEITSVERGOEDING, REGELING_LEASEAUTO, REGELING_LEASEFIETS, REGELING_OV_VERGOEDING, FIETSREGELING, EENMALIGE_UITKERINGEN, VASTE_UITKERINGEN, JUBILEUMUITKERING, VARIABELE_UITKERINGEN, WACHTDAGCOMPENSATIE, ONGEVALLENVERZEKERING |
| `leave` (let op: na `clean()` blijft alleen de volgorde over, de indexen niet; zie [09 Verlof](09_verlof.md)) | ADV, ADV_AANVULLING_OUDEREN, ADV_AANVULLING_DUUR_DIENSTVERBAND, ADV_AANVULLING_ANDERS, VAKANTIE, BIJZONDER_VERLOF, WAZO_BETAALD_OUDERSCHAPSVERLOF, WAZO_ONBETAALD_OUDERSCHAPSVERLOF, WAZO_GEBOORTEVERLOF, WAZO_KORTDUREND_ZORGVERLOF, WAZO_LANGDUREND_ZORGVERLOF, WAZO_LANGE_VERLOFDUUR, WAZO_ANDERS, VERPLICHT, FEESTDAGEN, PERSOONLIJKE_FEESTDAGEN, WAARDE_VERLOFDAG |
| `individualChoiceBudget` | INDIVIDUAL_CHOICE_BUDGET |
| `sustainableEmployability` | OPLEIDINGEN, LOOPBAANCOACHING, OUTPLACEMENTTRAJECTEN, VOORLICHTING_NEDERLAND, SCHOLING_NEDERLAND, SOCIALE_BEGELEIDING_NEDERLAND, ANDERS, FYSIEKE_GEZONDHEID, MENTALE_GEZONDHEID, FINANCIELE_GEZONDHEID, VITALITEITSBUDGET, VITALITEIT_ANDERS, VERPLICHTE_SCHOLING, DUURZAME_SAMENLEVING |
| `OTHER_*` | PAWW, PAZW, ANDERS, RVU_REGELING, WGA_HIAAT, ACCIDENT_BENEFIT: gebruikt als index in **`supplementaryArrangement`** (zie [13](13_aanvullende-regelingen.md)); OVERIG_START + i: index in **`otherArrangement`** (vrije regelingen uit [14 Overig](14_overig.md)) |
| `remuneration[..].individualSalaryIncrease` | DUUR_DIENSTVERBAND, BEOORDELING_WERKNEMER, ANDERS, OVERIG |
