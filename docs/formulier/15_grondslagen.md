# 15 · Grondslagen

Bron: `src/definition/15_grondslagen.tsx` (webformulier v2.1.0).

**Structuur:** deze sectie is **dynamisch**. Ze verschijnt alleen als elders in het formulier minstens één
grondslag gekozen is, en bevat dan **één subsectie per gebruikte grondslag**. Elke subsectie heeft dezelfde
vragenset.

## Welke grondslagen verschijnen?

Het formulier verzamelt de grondslagcodes (uniek, in deze volgorde) uit:

| Bron | Slug |
|---|---|
| Vakantiebijslag | `vakantiebijslag/percentage/grondslag` |
| Individueel keuzebudget | `individueel-keuzebudget/percentage/grondslag` |
| Pensioen | `Pension` als `pensioenregeling` = `ja` ² |
| Elke toeslagrij × variant (zie [04 Toeslagen](04_toeslagen.md)) | `<toeslag-slug>[i]/percentage/grondslag` |
| Loondoorbetaling bij ziekte, per rij | `loondoorbetaling-bij-ziekte[i]/grondslag` |
| Aanvullende sociale-zekerheidsregelingen (zie [13](13_aanvullende-regelingen.md)) | `<regeling-slug>/werkgeverspremie/percentage/grondslag`, `<regeling-slug>/werknemerspremie/percentage/grondslag` |
| Andere sociale regelingen, per rij | `andere-sociale-regelingen[i]/werkgeverspremie[0]/percentage/grondslag`, idem `werknemerspremie[0]` |
| Overige regelingen, per rij | `overige-regelingen[i]/percentage/grondslag` |

² **Bug in de webform:** de slug `pensioenregeling` bestaat niet, want de vraag heet
`pensioenregeling/van-toepassing` (zie [11 Pensioen](11_pensioen.md)). Daardoor verschijnt de grondslag
*Pensioen* hier in de praktijk nooit, tenzij hij via een andere bron gekozen is.

Mogelijke codes: zie [B4 Grondslag](00_bouwstenen.md#b4--grondslag). Het menu-label van de subsectie is het label
van de grondslag, bijvoorbeeld "Basisloon grondslag".

## Per grondslag `<code>` (subsectie "Grondslag {label}")

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Salaris wordt meegenomen bij deze grondslag | `grondslag/<code>/salaris` | checkbox | — | — | | per grondslag | `baseDefinition[n]`: bouwt het hele BaseDefinition-object (zie hieronder) |
| Vakantietoeslag wordt meegenomen bij deze grondslag | `grondslag/<code>/vakantietoeslag` | checkbox | — | — | | per grondslag | `baseDefinition[n].holidayAllowanceIndicator` |
| Betaald verlof wordt meegenomen bij deze grondslag | `grondslag/<code>/betaald-verlof` | checkbox | — | — | | per grondslag | `baseDefinition[n].paidLeaveDayIndicator` |
| Worden toeslagen meegenomen bij deze grondslag? | `grondslag/<code>/toeslagen` | radio | Alle toeslagen → `all` · Geen toeslagen → `none` · Sommige toeslagen: → `some` | — | | per grondslag | `allAllowancesIndicator` = (`all`) |
| ↳ *(label van de toeslagrij)* | `grondslag/<code>/toeslag-<toeslag-slug>` | checkbox | één checkbox per toeslagrij uit [04 Toeslagen](04_toeslagen.md) | `grondslag/<code>/toeslagen` = `some` | | per grondslag | `baseDefinition[n].allowances[] = {typeCode}` van de aangevinkte rijen |
| Peildatum voor deze grondslag | `grondslag/<code>/peildatum` | datum | — | — | ja | per grondslag | `baseDefinition[n].referenceDate` |

`n` is de volgorde (index) van de grondslag in de lijst hierboven.

SETU-object dat per grondslag wordt gebouwd (ook als er niets aangevinkt is, via `shouldConvertNullSetuValue`):

```
baseDefinition[n] = {
  baseType: <code>,
  remunerationIndicator:     salaris aangevinkt,
  holidayAllowanceIndicator: vakantietoeslag aangevinkt,
  paidLeaveDayIndicator:     betaald-verlof aangevinkt,
  allAllowancesIndicator:    toeslagen == "all",
  referenceDate:  { occurrenceType: "Recurring", interval: "R/<peildatum>/P1Y" }   // alleen als peildatum
  allowances:     [{ typeCode }, ...]                                              // alleen als toeslagen == "some"
}
```

**Let op:**
- De grondslagen staan in de antwoorden onder de **code** (`grondslag/BaseWage/...`), niet onder een index. Een
  grondslag die niet meer gebruikt wordt, verdwijnt uit het formulier, maar de antwoorden kunnen in
  `__webform_data__` blijven staan.
- Bij `toeslagen` = `none` wordt niets naar `allowances` geschreven. Het verschil tussen `none` en "niet
  ingevuld" is in SETU dus niet te zien.
- `referenceDate` gebruikt hier het veld `interval`, terwijl de SETU-documentatie `date` noemt. Het officiële
  schema (`Recurring`) is zelf inconsistent: het **vereist** `interval`, maar **definieert** alleen
  `recurringInterval`. De webform-output (`interval`) valideert dus wel. Dit is een aandachtspunt voor de
  mappingfase.

---

**Telling (per grondslag):** 0 tekst · 1 datum · 0 tijd · 1 radio · 3 checkbox + 1 checkbox per toeslagrij (5 vragen + toeslagrijen), 0 alerts.
