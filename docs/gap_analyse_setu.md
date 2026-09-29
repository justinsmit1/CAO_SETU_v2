# Gap-analyse: SETU-standaard tegenover kern en Wijzerbelonen

*Bron: `SETU-Inquiry-Pay-Equity-v2-1-InquiryPayEquity (6).xlsx` (718 elementpaden). Gemaakt met `tools/gap_analyse.py`.*

- **Kern**: het pad staat in het schema waar het kernmodel conform aan is.
- **Wijzerbelonen**: het pad komt voor in de SETU-uitvoer van het volledige voorbeeld (`examples/maak_upload_full.py`).

## Samenvatting

Van de 718 elementen dekt de kern er 717 (100%) en vult Wijzerbelonen er 317 (44%).

| Sectie | Elementen | Kern | Wijzerbelonen | Ontbreekt bij Wijzerbelonen | Waarvan verplicht (1..x) |
|---|---:|---:|---:|---:|---:|
| `documentId` | 3 | 3 | 3 | 0 | 0 |
| `versionId` | 2 | 2 | 0 | 2 | 1 |
| `issued` | 1 | 1 | 1 | 0 | 0 |
| `effectivePeriod` | 3 | 3 | 3 | 0 | 0 |
| `customer` | 19 | 19 | 14 | 5 | 2 |
| `baseDefinition` | 9 | 9 | 9 | 0 | 0 |
| `labourAgreements` | 12 | 12 | 12 | 0 | 0 |
| `positionProfile` | 8 | 8 | 6 | 2 | 0 |
| `remuneration` | 70 | 70 | 52 | 18 | 3 |
| `allowance` | 57 | 57 | 36 | 21 | 7 |
| `holidayAllowance` | 40 | 40 | 14 | 26 | 8 |
| `sickPay` | 44 | 43 | 19 | 25 | 8 |
| `leave` | 218 | 218 | 61 | 157 | 48 |
| `individualChoiceBudget` | 41 | 41 | 15 | 26 | 8 |
| `pension` | 41 | 41 | 17 | 24 | 8 |
| `sustainableEmployability` | 41 | 41 | 18 | 23 | 6 |
| `supplementaryArrangement` | 55 | 55 | 21 | 34 | 10 |
| `otherArrangement` | 54 | 54 | 16 | 38 | 14 |

## Gaten per familie

Dezelfde gaten keren in veel regelingen terug; per familie één keer oplossen.

| Familie | Ontbrekende elementen | Secties |
|---|---:|---|
| id/description | 99 | `leave` 29, `allowance` 9, `holidayAllowance` 8, `sickPay` 8, `individualChoiceBudget` 8, `pension` 8, `sustainableEmployability` 8, `supplementaryArrangement` 8, `otherArrangement` 8, `customer` 3, `remuneration` 2 |
| min/maxValue | 82 | `leave` 40, `supplementaryArrangement` 8, `otherArrangement` 8, `remuneration` 4, `holidayAllowance` 4, `sickPay` 4, `individualChoiceBudget` 4, `pension` 4, `sustainableEmployability` 4, `allowance` 2 |
| regelingspecifiek | 77 | `leave` 43, `otherArrangement` 9, `remuneration` 5, `supplementaryArrangement` 4, `versionId` 2, `customer` 2, `positionProfile` 2, `allowance` 2, `sickPay` 2, `individualChoiceBudget` 2, `sustainableEmployability` 2, `holidayAllowance` 1, `pension` 1 |
| proportional | 42 | `leave` 15, `supplementaryArrangement` 6, `otherArrangement` 6, `remuneration` 3, `holidayAllowance` 3, `sickPay` 3, `individualChoiceBudget` 3, `pension` 3 |
| lineId | 28 | `leave` 10, `remuneration` 2, `allowance` 2, `holidayAllowance` 2, `sickPay` 2, `individualChoiceBudget` 2, `pension` 2, `sustainableEmployability` 2, `supplementaryArrangement` 2, `otherArrangement` 2 |
| effectivePeriod | 27 | `allowance` 3, `holidayAllowance` 3, `sickPay` 3, `leave` 3, `individualChoiceBudget` 3, `pension` 3, `sustainableEmployability` 3, `supplementaryArrangement` 3, `otherArrangement` 3 |
| ikbReference | 26 | `leave` 10, `allowance` 2, `holidayAllowance` 2, `sickPay` 2, `individualChoiceBudget` 2, `pension` 2, `sustainableEmployability` 2, `supplementaryArrangement` 2, `otherArrangement` 2 |
| contributionSource | 11 | `leave` 5, `remuneration` 1, `allowance` 1, `holidayAllowance` 1, `sickPay` 1, `individualChoiceBudget` 1, `sustainableEmployability` 1 |
| conditions | 7 | `leave` 2, `remuneration` 1, `holidayAllowance` 1, `individualChoiceBudget` 1, `pension` 1, `supplementaryArrangement` 1 |
| payDate / occurrence | 2 | `holidayAllowance` 1, `sustainableEmployability` 1 |

## Vakantiebijslag (`holidayAllowance`) in detail

| Pad | Mult | Type | Kern | Wijzerbelonen |
|---|---|---|:-:|:-:|
| `holidayAllowance` | 0..n | HolidayAllowanceArrangement | ja | ja |
| `id` | 0..1 |  | ja | nee |
| `id/value` | 1..1 | IdValue | ja | nee |
| `id/schemeAgencyId` | 1..1 | SchemeAgencyId | ja | nee |
| `name` | 1..1 | string | ja | ja |
| `origin` | 1..1 | LabourAgreementReference | ja | ja |
| `origin/type` | 1..1 | string | ja | ja |
| `effectivePeriod` | 0..1 | EffectivePeriod | ja | nee |
| `effectivePeriod/validFrom` | 0..1 |  | ja | nee |
| `effectivePeriod/validTo` | 0..1 |  | ja | nee |
| `line` | 0..n | ArrangementLine | ja | ja |
| `line/lineId` | 0..1 | Id | ja | nee |
| `line/lineId/value` | 1..1 | IdValue | ja | nee |
| `line/amount` | 0..1 | Amount | ja | ja |
| `line/amount/value` | 1..1 | decimal | ja | ja |
| `line/amount/minValue` | 0..1 | decimal | ja | nee |
| `line/amount/maxValue` | 0..1 | decimal | ja | nee |
| `line/amount/unitCode` | 1..1 | AmountUnitCode | ja | ja |
| `line/amount/baseAmount` | 1..1 | BaseAmount | ja | ja |
| `line/amount/baseAmount/unitCode` | 1..1 | BaseUnitCode | ja | ja |
| `line/amount/baseAmount/baseType` | 0..1 | BaseDefinitionCode | ja | ja |
| `line/amount/baseAmount/value` | 0..1 | decimal | ja | nee |
| `line/amount/baseAmount/minValue` | 0..1 | decimal | ja | nee |
| `line/amount/baseAmount/maxValue` | 0..1 | decimal | ja | nee |
| `line/amount/proportional` | 0..1 | Proportional | ja | nee |
| `line/amount/proportional/partTimePercentage` | 1..1 | boolean | ja | nee |
| `line/amount/proportional/employmentDuration` | 1..1 | boolean | ja | nee |
| `line/amount/proportional/description` | 0..1 | string | ja | nee |
| `line/interval` | 0..1 | Interval | ja | ja |
| `line/interval/value` | 1..1 | decimal | ja | ja |
| `line/interval/unitCode` | 1..1 | IntervalCode | ja | ja |
| `line/conditions` | 0..n | Condition | ja | nee |
| `line/contributionSource` | 0..1 | ContributionSourceType | ja | nee |
| `line/ikbReference` | 0..n | IkbReference | ja | nee |
| `line/ikbReference/relationType` | 1..1 | string | ja | nee |
| `line/ikbReference/id` | 1..1 |  | ja | nee |
| `line/ikbReference/id/value` | 1..1 | IdValue | ja | nee |
| `line/ikbReference/description` | 0..1 | string | ja | nee |
| `payDate` | 0..1 | Occurrence | ja | nee |
| `description` | 0..1 | string | ja | nee |

## Volledige lijst: niet gevuld door Wijzerbelonen

### `versionId` (2)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `versionId` | 0..1 | regelingspecifiek | ja |
| `value` | 1..1 | regelingspecifiek | ja |

### `customer` (5)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..2 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `personContacts/communication/email/useCode` | 0..1 | regelingspecifiek | ja |
| `personContacts/roleCode` | 0..1 | regelingspecifiek | ja |

### `positionProfile` (2)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `referenceTitle` | 0..1 | regelingspecifiek | ja |
| `workDescription` | 0..1 | regelingspecifiek | ja |

### `remuneration` (18)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `hourlyWageConversion/hourlyWageFactor` | 0..1 | regelingspecifiek | ja |
| `salaryScale/salaryStep/minimumWage` | 0..1 | regelingspecifiek | ja |
| `salaryScale/salaryStep/conditions` | 0..n | conditions | ja |
| `salaryScale/positionProfileReference/startSalaryStep` | 0..1 | regelingspecifiek | ja |
| `salaryScale/positionProfileReference/description` | 0..1 | id/description | ja |
| `individualSalaryIncrease/line/lineId` | 0..1 | lineId | ja |
| `individualSalaryIncrease/line/lineId/value` | 1..1 | lineId | ja |
| `individualSalaryIncrease/line/amount/minValue` | 0..1 | min/maxValue | ja |
| `individualSalaryIncrease/line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `individualSalaryIncrease/line/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `individualSalaryIncrease/line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `individualSalaryIncrease/line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `individualSalaryIncrease/line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `individualSalaryIncrease/line/amount/proportional` | 0..1 | proportional | ja |
| `individualSalaryIncrease/line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `individualSalaryIncrease/line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `individualSalaryIncrease/line/amount/proportional/description` | 0..1 | id/description | ja |
| `individualSalaryIncrease/line/contributionSource` | 0..1 | contributionSource | ja |

### `allowance` (21)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/contributionSource` | 0..1 | contributionSource | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `reference/id` | 0..1 | id/description | ja |
| `reference/id/value` | 1..1 | id/description | ja |

### `holidayAllowance` (26)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional` | 0..1 | proportional | ja |
| `line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/conditions` | 0..n | conditions | ja |
| `line/contributionSource` | 0..1 | contributionSource | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `payDate` | 0..1 | payDate / occurrence | ja |
| `description` | 0..1 | id/description | ja |

### `sickPay` (25)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `Sickness_cause` | 0..1 | regelingspecifiek | nee |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional` | 0..1 | proportional | ja |
| `line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/contributionSource` | 0..1 | contributionSource | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `description` | 0..1 | id/description | ja |

### `leave` (157)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `paidLeave/name` | 0..1 | regelingspecifiek | ja |
| `paidLeave/lineId` | 0..1 | lineId | ja |
| `paidLeave/lineId/value` | 1..1 | lineId | ja |
| `paidLeave/amount/minValue` | 0..1 | min/maxValue | ja |
| `paidLeave/amount/maxValue` | 0..1 | min/maxValue | ja |
| `paidLeave/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `paidLeave/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `paidLeave/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `paidLeave/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `paidLeave/amount/proportional` | 0..1 | proportional | ja |
| `paidLeave/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `paidLeave/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `paidLeave/amount/proportional/description` | 0..1 | id/description | ja |
| `paidLeave/contributionSource` | 0..1 | contributionSource | ja |
| `paidLeave/leaveDayValue/minValue` | 0..1 | min/maxValue | ja |
| `paidLeave/leaveDayValue/maxValue` | 0..1 | min/maxValue | ja |
| `paidLeave/leaveDayValue/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `paidLeave/leaveDayValue/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `paidLeave/leaveDayValue/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `paidLeave/leaveDayValue/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `paidLeave/ikbReference` | 0..n | ikbReference | ja |
| `paidLeave/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `paidLeave/ikbReference/id` | 1..1 | id/description | ja |
| `paidLeave/ikbReference/id/value` | 1..1 | id/description | ja |
| `paidLeave/ikbReference/description` | 0..1 | id/description | ja |
| `paidLeave/description` | 0..1 | id/description | ja |
| `workingHoursReduction/name` | 0..1 | regelingspecifiek | ja |
| `workingHoursReduction/lineId` | 0..1 | lineId | ja |
| `workingHoursReduction/lineId/value` | 1..1 | lineId | ja |
| `workingHoursReduction/amount/minValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/amount/maxValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `workingHoursReduction/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `workingHoursReduction/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/amount/proportional` | 0..1 | proportional | ja |
| `workingHoursReduction/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `workingHoursReduction/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `workingHoursReduction/amount/proportional/description` | 0..1 | id/description | ja |
| `workingHoursReduction/conditions` | 0..n | conditions | ja |
| `workingHoursReduction/contributionSource` | 0..1 | contributionSource | ja |
| `workingHoursReduction/leaveDayValue` | 0..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/value` | 1..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/minValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/leaveDayValue/maxValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/leaveDayValue/unitCode` | 1..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/baseAmount` | 1..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/baseAmount/unitCode` | 1..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `workingHoursReduction/leaveDayValue/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/leaveDayValue/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `workingHoursReduction/ikbReference` | 0..n | ikbReference | ja |
| `workingHoursReduction/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `workingHoursReduction/ikbReference/id` | 1..1 | id/description | ja |
| `workingHoursReduction/ikbReference/id/value` | 1..1 | id/description | ja |
| `workingHoursReduction/ikbReference/description` | 0..1 | id/description | ja |
| `workingHoursReduction/description` | 0..1 | id/description | ja |
| `holidays/lineId` | 0..1 | lineId | ja |
| `holidays/lineId/value` | 1..1 | lineId | ja |
| `holidays/amount/minValue` | 0..1 | min/maxValue | ja |
| `holidays/amount/maxValue` | 0..1 | min/maxValue | ja |
| `holidays/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `holidays/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `holidays/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `holidays/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `holidays/amount/proportional` | 0..1 | proportional | ja |
| `holidays/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `holidays/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `holidays/amount/proportional/description` | 0..1 | id/description | ja |
| `holidays/contributionSource` | 0..1 | contributionSource | ja |
| `holidays/leaveDayValue` | 0..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/value` | 1..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/minValue` | 0..1 | min/maxValue | ja |
| `holidays/leaveDayValue/maxValue` | 0..1 | min/maxValue | ja |
| `holidays/leaveDayValue/unitCode` | 1..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/baseAmount` | 1..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/baseAmount/unitCode` | 1..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `holidays/leaveDayValue/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `holidays/leaveDayValue/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `holidays/ikbReference` | 0..n | ikbReference | ja |
| `holidays/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `holidays/ikbReference/id` | 1..1 | id/description | ja |
| `holidays/ikbReference/id/value` | 1..1 | id/description | ja |
| `holidays/ikbReference/description` | 0..1 | id/description | ja |
| `holidays/description` | 0..1 | id/description | ja |
| `specialLeave/name` | 0..1 | regelingspecifiek | ja |
| `specialLeave/lineId` | 0..1 | lineId | ja |
| `specialLeave/lineId/value` | 1..1 | lineId | ja |
| `specialLeave/amount/minValue` | 0..1 | min/maxValue | ja |
| `specialLeave/amount/maxValue` | 0..1 | min/maxValue | ja |
| `specialLeave/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `specialLeave/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `specialLeave/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `specialLeave/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `specialLeave/amount/proportional` | 0..1 | proportional | ja |
| `specialLeave/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `specialLeave/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `specialLeave/amount/proportional/description` | 0..1 | id/description | ja |
| `specialLeave/contributionSource` | 0..1 | contributionSource | ja |
| `specialLeave/leaveDayValue` | 0..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/value` | 1..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/minValue` | 0..1 | min/maxValue | ja |
| `specialLeave/leaveDayValue/maxValue` | 0..1 | min/maxValue | ja |
| `specialLeave/leaveDayValue/unitCode` | 1..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/baseAmount` | 1..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/baseAmount/unitCode` | 1..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `specialLeave/leaveDayValue/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `specialLeave/leaveDayValue/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `specialLeave/ikbReference` | 0..n | ikbReference | ja |
| `specialLeave/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `specialLeave/ikbReference/id` | 1..1 | id/description | ja |
| `specialLeave/ikbReference/id/value` | 1..1 | id/description | ja |
| `specialLeave/ikbReference/description` | 0..1 | id/description | ja |
| `specialLeave/description` | 0..1 | id/description | ja |
| `additionalParentalLeave/lineId` | 0..1 | lineId | ja |
| `additionalParentalLeave/lineId/value` | 1..1 | lineId | ja |
| `additionalParentalLeave/amount/minValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/amount/maxValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `additionalParentalLeave/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `additionalParentalLeave/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/amount/proportional` | 0..1 | proportional | ja |
| `additionalParentalLeave/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `additionalParentalLeave/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `additionalParentalLeave/amount/proportional/description` | 0..1 | id/description | ja |
| `additionalParentalLeave/conditions` | 0..n | conditions | ja |
| `additionalParentalLeave/contributionSource` | 0..1 | contributionSource | ja |
| `additionalParentalLeave/leaveDayValue` | 0..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/value` | 1..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/minValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/leaveDayValue/maxValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/leaveDayValue/unitCode` | 1..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/baseAmount` | 1..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/baseAmount/unitCode` | 1..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `additionalParentalLeave/leaveDayValue/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/leaveDayValue/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `additionalParentalLeave/ikbReference` | 0..n | ikbReference | ja |
| `additionalParentalLeave/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `additionalParentalLeave/ikbReference/id` | 1..1 | id/description | ja |
| `additionalParentalLeave/ikbReference/id/value` | 1..1 | id/description | ja |
| `additionalParentalLeave/ikbReference/description` | 0..1 | id/description | ja |
| `additionalParentalLeave/description` | 0..1 | id/description | ja |
| `description` | 0..1 | id/description | ja |

### `individualChoiceBudget` (26)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional` | 0..1 | proportional | ja |
| `line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/conditions` | 0..n | conditions | ja |
| `line/contributionSource` | 0..1 | contributionSource | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `description` | 0..1 | id/description | ja |

### `pension` (24)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional` | 0..1 | proportional | ja |
| `line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/conditions` | 0..n | conditions | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `description` | 0..1 | id/description | ja |

### `sustainableEmployability` (23)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/contributionSource` | 0..1 | contributionSource | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `payDate` | 0..1 | payDate / occurrence | ja |
| `description` | 0..1 | id/description | ja |

### `supplementaryArrangement` (34)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional` | 0..1 | proportional | ja |
| `line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/conditions` | 0..n | conditions | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `coverage/minValue` | 0..1 | min/maxValue | ja |
| `coverage/maxValue` | 0..1 | min/maxValue | ja |
| `coverage/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `coverage/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `coverage/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `coverage/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `coverage/proportional` | 0..1 | proportional | ja |
| `coverage/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `coverage/proportional/employmentDuration` | 1..1 | proportional | ja |
| `coverage/proportional/description` | 0..1 | id/description | ja |

### `otherArrangement` (38)

| Pad | Mult | Familie | In kern |
|---|---|---|:-:|
| `id` | 0..1 | id/description | ja |
| `id/value` | 1..1 | id/description | ja |
| `id/schemeAgencyId` | 1..1 | id/description | ja |
| `effectivePeriod` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validFrom` | 0..1 | effectivePeriod | ja |
| `effectivePeriod/validTo` | 0..1 | effectivePeriod | ja |
| `line/lineId` | 0..1 | lineId | ja |
| `line/lineId/value` | 1..1 | lineId | ja |
| `line/amount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `line/amount/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `line/amount/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `line/amount/proportional` | 0..1 | proportional | ja |
| `line/amount/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `line/amount/proportional/employmentDuration` | 1..1 | proportional | ja |
| `line/amount/proportional/description` | 0..1 | id/description | ja |
| `line/ikbReference` | 0..n | ikbReference | ja |
| `line/ikbReference/relationType` | 1..1 | ikbReference | ja |
| `line/ikbReference/id` | 1..1 | id/description | ja |
| `line/ikbReference/id/value` | 1..1 | id/description | ja |
| `line/ikbReference/description` | 0..1 | id/description | ja |
| `coverage` | 0..1 | regelingspecifiek | ja |
| `coverage/value` | 1..1 | regelingspecifiek | ja |
| `coverage/minValue` | 0..1 | min/maxValue | ja |
| `coverage/maxValue` | 0..1 | min/maxValue | ja |
| `coverage/unitCode` | 1..1 | regelingspecifiek | ja |
| `coverage/baseAmount` | 1..1 | regelingspecifiek | ja |
| `coverage/baseAmount/unitCode` | 1..1 | regelingspecifiek | ja |
| `coverage/baseAmount/baseType` | 0..1 | regelingspecifiek | ja |
| `coverage/baseAmount/value` | 0..1 | regelingspecifiek | ja |
| `coverage/baseAmount/minValue` | 0..1 | min/maxValue | ja |
| `coverage/baseAmount/maxValue` | 0..1 | min/maxValue | ja |
| `coverage/proportional` | 0..1 | proportional | ja |
| `coverage/proportional/partTimePercentage` | 1..1 | proportional | ja |
| `coverage/proportional/employmentDuration` | 1..1 | proportional | ja |
| `coverage/proportional/description` | 0..1 | id/description | ja |

## Afwijkingen tussen Excel en schema

Elementen uit de Excel die niet in het schema staan (kern kan ze niet dragen): `sickPay/Sickness_cause`.
