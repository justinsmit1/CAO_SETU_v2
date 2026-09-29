# 07 · Bijzondere uitkeringen

Bron: `src/definition/07_bijzondere-uitkeringen.tsx` (webformulier v2.1.0).

**Structuur:** vier subsecties — *Eenmalige uitkeringen*, *Vaste (onvoorwaardelijke) uitkeringen*,
*Jubileumuitkering* en *Variabele (voorwaardelijke) uitkeringen*. Elke subsectie begint met een ja/nee-vraag; bij
`ja` wordt een herhaalbare lijst **variaties** aangemaakt (`eenmalige-uitkeringen[i]`, `vaste-uitkeringen[i]`,
`jubileumuitkeringen[i]`, `variabele-uitkeringen[i]`). Knoppen per subsectie: *Variatie toevoegen* (blok
"Variaties", kloont de laatste variatie) en *Variatie {num} verwijderen* (alleen bij meer dan één variatie).
Hulptekst bij "Variaties" (alle vier): *"Zijn er variaties van deze uitkering, bijvoorbeeld na een ander aantal
jaren dienstverband? Voeg dan een variatie toe."* De SETU-conversie zit volledig in de ja/nee-vraag: die bouwt per
variatie één AllowanceArrangement en voegt die toe aan `allowance_EXTRA_ALLOWANCES` (achteraan in `allowance[]`).
De vaste indexen `ALLOWANCE_EENMALIGE_UITKERINGEN`, `ALLOWANCE_VASTE_UITKERINGEN`, `ALLOWANCE_JUBILEUMUITKERING` en
`ALLOWANCE_VARIABELE_UITKERINGEN` (31–34) worden niet gebruikt.

## Eenmalige uitkeringen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Zijn er eenmalige uitkeringen bekend? | `eenmalige-uitkeringen-bekend` | radio | Ja → `ja` · Nee → `nee` | — | | | `allowance_EXTRA_ALLOWANCES` ¹ |

Hulptekst: *"Denk bijvoorbeeld aan een eenmalige vergoeding ter vervanging van een loonsverhoging of een eenmalige
vergoeding vanwege de hoge energiekosten."* en *"Als deze later bekend worden, moeten deze alsnog per omgaande
worden doorgegeven."*

### Variatie (herhaalbaar, `eenmalige-uitkeringen[i]`)

Alle blokken zijn zichtbaar als `eenmalige-uitkeringen-bekend` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam (bij >1 variatie: "Naam (variatie {num})") | `eenmalige-uitkeringen[i]/namelijk` | tekst | — | (blok) | | ja | `name` = "Eenmalige uitkering: " + naam |
| **Welke voorwaarden zijn van toepassing?** (bloktitel) | | | | | | | |
| Afhankelijk minimale duur dienstverband, namelijk: | `eenmalige-uitkeringen[i]/voorwaarden/min-duur-dienstverband` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Afhankelijk van dienstverband op bepaalde datum, namelijk: | `eenmalige-uitkeringen[i]/voorwaarden/dienstverband-op-datum` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Anders, namelijk: | `eenmalige-uitkeringen[i]/voorwaarden/anders` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| ↳ *(geen vraagtekst)* | `eenmalige-uitkeringen[i]/voorwaarden_min-duur_namelijk` | tekst | — | `voorwaarden/min-duur-dienstverband` aangevinkt | | ja | `conditions[].description` |
| ↳ *(geen vraagtekst)* | `eenmalige-uitkeringen[i]/voorwaarden_dienstverband-datum_namelijk` | tekst | — | `voorwaarden/dienstverband-op-datum` aangevinkt | | ja | `conditions[].description` = "Afhankelijk van dienstverband op bepaalde datum, namelijk: " + tekst |
| ↳ *(geen vraagtekst)* | `eenmalige-uitkeringen[i]/voorwaarden_anders_namelijk` | tekst | — | `voorwaarden/anders` aangevinkt | | ja | `conditions[].description` |
| Op welk moment wordt de uitkering uitgekeerd? | `eenmalige-uitkeringen[i]/toekenning-datum` | datum | — | (blok) | | ja | `payDate {occurrenceType: Single, date}` |
| **Hoe wordt de uitkering toegekend?** (bloktitel) | `eenmalige-uitkeringen[i]/hoe-toegekend` | radio | Vast percentage van het loon → `percentage-loon` · Vast bedrag, namelijk: → `vast-bedrag` · Anders, namelijk: → `anders` | (blok) | | ja | bepaalt `line[0].amount` |
| ↳ *(geen vraagtekst)* | `eenmalige-uitkeringen[i]/type_ander-percentage_percentage` | getal (%) | — | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.value`, `unitCode: Percentage` |
| ↳ van | `eenmalige-uitkeringen[i]/type_ander-percentage_van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.baseAmount.unitCode` |
| ↳ *(geen vraagtekst)* | `eenmalige-uitkeringen[i]/vast-bedrag_namelijk` | getal (€) | — | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.value`, `unitCode: Euro`, `baseAmount.unitCode: Fixed` |
| ↳ *(geen vraagtekst)* | `eenmalige-uitkeringen[i]/anders` | tekst | — | `hoe-toegekend` = `anders` | | ja | toegevoegd aan `name` (": " + tekst) |
| ↳ Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband? | `eenmalige-uitkeringen[i]/naar-rato-deeltijd` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.proportional.partTimePercentage` |
| ↳ Wordt dit bedrag toegepast naar rato van de duur van het dienstverband? | `eenmalige-uitkeringen[i]/naar-rato-duur-dienstverband` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.proportional.employmentDuration` |
| Geldt er een minimum- of een maximumbedrag? | `eenmalige-uitkeringen[i]/min-max` | radio | Ja, namelijk: → `ja` · Nee → `nee` | `eenmalige-uitkeringen-bekend` = `ja` en `eenmalige-uitkering-hoe-toegekend` ≠ `anders` ² | | ja | — |
| ↳ Minimum | `eenmalige-uitkeringen[i]/min-max/ja/minimum` | getal (€) | — | `min-max` = `ja` | ja | ja | `line[0].amount.minValue` |
| ↳ Maximum | `eenmalige-uitkeringen[i]/min-max/ja/maximum` | getal (€) | — | `min-max` = `ja` | ja | ja | `line[0].amount.maxValue` |

¹ Bouwt per variatie AllowanceArrangement `{name: "Eenmalige uitkering: <naam>[: <anders>]", typeCode EA801,
origin, payDate?, line: [{interval: 1 × Once, conditions, amount?}]}`.

² De voorwaarde gebruikt de slug `eenmalige-uitkering-hoe-toegekend`, die niet bestaat (de echte slug is
`eenmalige-uitkeringen[i]/hoe-toegekend`); in de praktijk is de vraag dus altijd zichtbaar bij `bekend` = `ja`.

**Let op:**
- `line[0]` wordt alleen aan `allowance.line` toegevoegd als er een voorwaarde, percentage, vast bedrag of naar-rato is; bij `anders` zonder voorwaarden is `line` leeg.
- Bij `min-max` = `ja` terwijl er geen `amount` is (bijv. `hoe-toegekend` = `anders`) faalt de conversie (`line.amount` is undefined).
- De voorwaarden min. duur / datum worden als vrije tekst (`conditionType: Text`) opgeslagen, niet als `EmploymentDuration` (TODO in de code).

## Vaste (onvoorwaardelijke) uitkeringen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er een vaste (onvoorwaardelijke) uitkering van toepassing? | `vaste-uitkering-van-toepassing` | radio | Ja → `ja` · Nee → `nee` | — | | | `allowance_EXTRA_ALLOWANCES` ¹ |

Hulptekst: *"Denk bijvoorbeeld aan een vaste dertiende maand of een vaste eindejaarsuitkering."*

### Variatie (herhaalbaar, `vaste-uitkeringen[i]`)

Alle blokken zijn zichtbaar als `vaste-uitkering-van-toepassing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam (bij >1 variatie: "Naam (variatie {num})") | `vaste-uitkeringen[i]/namelijk` | tekst | — | (blok) | | ja | `name` = "Vaste uitkering: " + naam |
| **Welke voorwaarden zijn van toepassing?** (bloktitel) | | | | | | | |
| Afhankelijk minimale duur dienstverband, namelijk: | `vaste-uitkeringen[i]/voorwaarden/min-duur-dienstverband` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Afhankelijk van dienstverband op bepaalde datum, namelijk: | `vaste-uitkeringen[i]/voorwaarden/dienstverband-op-datum` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Anders, namelijk: | `vaste-uitkeringen[i]/voorwaarden/anders` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| ↳ *(geen vraagtekst)* | `vaste-uitkeringen[i]/voorwaarden_min-duur_namelijk` | tekst | — | `voorwaarden/min-duur-dienstverband` aangevinkt | | ja | `conditions[].description` |
| ↳ *(geen vraagtekst)* | `vaste-uitkeringen[i]/voorwaarden_dienstverband-datum_namelijk` | tekst | — | `voorwaarden/dienstverband-op-datum` aangevinkt | | ja | `conditions[].description` = "Afhankelijk van dienstverband op bepaalde datum, namelijk: " + tekst |
| ↳ *(geen vraagtekst)* | `vaste-uitkeringen[i]/voorwaarden_anders_namelijk` | tekst | — | `voorwaarden/anders` aangevinkt | | ja | `conditions[].description` |
| Op welk moment wordt de uitkering uitgekeerd? | `vaste-uitkeringen[i]/toekenning-datum` | datum | — | (blok) | | ja | `payDate {occurrenceType: Single, date}` |
| **Hoe wordt de uitkering toegekend?** (bloktitel) | `vaste-uitkeringen[i]/hoe-toegekend` | radio | Als dertiende maand → `dertiende-maand` · Vast percentage van het loon → `percentage-loon` · Vast bedrag, namelijk: → `vast-bedrag` · Anders, namelijk: → `anders` | (blok) | | ja | bepaalt `line[0].amount` |
| ↳ namelijk | `vaste-uitkeringen[i]/type_ander-percentage_percentage` | getal (%) | — | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.value`, `unitCode: Percentage` |
| ↳ van | `vaste-uitkeringen[i]/type_ander-percentage_van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.baseAmount.unitCode` |
| ↳ *(geen vraagtekst)* | `vaste-uitkeringen[i]/vast-bedrag_namelijk` | getal (€) | — | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.value`, `unitCode: Euro`, `baseAmount.unitCode: Fixed` |
| ↳ *(geen vraagtekst)* | `vaste-uitkeringen[i]/anders` | tekst | — | `hoe-toegekend` = `anders` | | ja | toegevoegd aan `name` (": " + tekst) |
| ↳ Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur van het dienstverband? | `vaste-uitkeringen[i]/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.proportional` ³ |

¹ Bouwt per variatie AllowanceArrangement `{name: "Vaste uitkering: <naam>[: <anders>]", typeCode EA801, origin,
payDate?, line: [{interval: 1 × Year, conditions, amount?}]}`. Bij `dertiende-maand`: `amount` = 100 % van
`MonthlyRate` (hardcoded).

³ `naar-rato` = `ja` → `proportional {partTimePercentage: true, employmentDuration: false}`; de vraag noemt
deeltijd **en/of** duur dienstverband, maar alleen deeltijd wordt vastgelegd.

**Let op:**
- De conversie leest ook `vaste-uitkeringen[i]/min-max` en `min-max/ja/minimum|maximum`, maar deze vragen bestaan niet in deze subsectie (alleen via gekloonde of oude data te vullen).
- De conversie kent een tak `hoe-toegekend` = `ander-percentage` (percentage van `Fixed`), maar die optie staat niet in het formulier.
- `interval` is altijd 1 × `Year` en `payDate.occurrenceType` altijd `Single`.
- Voorwaarden min. duur / datum als `conditionType: Text` (TODO in de code).

## Jubileumuitkering

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er een jubileumuitkering of een vergelijkbare uitkering van toepassing? | `jubileumuitkering-van-toepassing` | radio | Ja → `ja` · Nee → `nee` | — | | | `allowance_EXTRA_ALLOWANCES` ¹ |

### Variatie (herhaalbaar, `jubileumuitkeringen[i]`)

Alle blokken zijn zichtbaar als `jubileumuitkering-van-toepassing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam (bij >1 variatie: "Naam (variatie {num})") | `jubileumuitkeringen[i]/namelijk` | tekst | — | (blok) | | ja | `name` = "Jubileumuitkering: " + naam |
| **Hoe wordt de uitkering toegekend?** (bloktitel) | `jubileumuitkeringen[i]/hoe-toegekend` | radio | Vast percentage van het loon → `percentage-loon` · Vast bedrag, namelijk: → `vast-bedrag` · Anders, namelijk: → `anders` | (blok) | | ja | bepaalt `line[0].amount` |
| ↳ namelijk | `jubileumuitkeringen[i]/type_ander-percentage_percentage` | getal (%) | — | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.value`, `unitCode: Percentage` |
| ↳ van | `jubileumuitkeringen[i]/type_ander-percentage_van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.baseAmount.unitCode` |
| ↳ *(geen vraagtekst)* | `jubileumuitkeringen[i]/vast-bedrag_namelijk` | getal (€) | — | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.value`, `unitCode: Euro`, `baseAmount.unitCode: Fixed` |
| ↳ Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur van het dienstverband? | `jubileumuitkeringen[i]/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.proportional {partTimePercentage: true, employmentDuration: false}` |
| ↳ *(geen vraagtekst)* | `jubileumuitkeringen[i]/anders` | tekst | — | `hoe-toegekend` = `anders` | | ja | vervangt `line` door `[{conditions: [Text "Anders toegekend, namelijk: …"]}]` |
| **Na hoeveel jaar dienstverband ontstaat recht op een jubileumuitkering?** (bloktitel) | | | | | | | |
| Aantal jaren | `jubileumuitkeringen[i]/dienstverband-duur/jaren` | getal (geheel) | — | (blok) | | ja | `line[0].conditions[]` EmploymentDuration `duration` (`P<j>Y`) |
| Aantal maanden | `jubileumuitkeringen[i]/dienstverband-duur/maanden` | getal (geheel) | — | (blok) | ja | ja | idem (`…<m>M`) |
| Referentiedatum | `jubileumuitkeringen[i]/dienstverband-duur/referentiedatum` | keuzelijst | [B5 Peildatum](00_bouwstenen.md#b5--peildatum--referentiedatum-referencedateoptions) | (blok) | | ja | `conditions[].referenceDateType` |
| Op welk moment wordt de uitkering uitgekeerd? | `jubileumuitkeringen[i]/toekenning-datum` | datum | — | (blok) | | ja | `payDate {occurrenceType: Single, date}` |
| Welke voorwaarden zijn van toepassing? | `jubileumuitkeringen[i]/voorwaarden` | tekst (textarea) | — | (blok) | ja | ja | `line[0].conditions[]` (Text) |

Hulptekst bij `voorwaarden`: *"Bijvoorbeeld wel / niet meetellen arbeidsverleden in dezelfde holding of bij een
gelieerde onderneming of organisatie."*

¹ Bouwt per variatie AllowanceArrangement `{name: "Jubileumuitkering: <naam>", typeCode EA903, origin, payDate?,
line: [{conditions, amount?}]}` — zonder `interval`. Dienstverbandduur → condition
`{conditionType: EmploymentDuration, operator: eq, duration: "P<jaren>Y<maanden>M", referenceDateType}`.

**Let op:**
- Bij `hoe-toegekend` = `anders` wordt `line` volledig vervangen: de EmploymentDuration-voorwaarde gaat dan verloren (alleen de Text-condition "Anders toegekend…" en daarna `voorwaarden` blijven over).
- De conversie leest ook `voorwaarden/min-duur-dienstverband` en `voorwaarden/dienstverband-op-datum` (+ `_namelijk`-teksten), maar die checkboxes bestaan niet in deze subsectie.
- typeCode `EA903` wordt ook gebruikt voor variabele uitkeringen; alleen `name` onderscheidt ze.

## Variabele (voorwaardelijke) uitkeringen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er een variabele (voorwaardelijke) uitkering van toepassing? | `variabele-uitkering-van-toepassing` | radio | Ja → `ja` · Nee → `nee` | — | | | `allowance_EXTRA_ALLOWANCES` ¹ |

### Variatie (herhaalbaar, `variabele-uitkeringen[i]`)

Alle blokken zijn zichtbaar als `variabele-uitkering-van-toepassing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Wat voor soort uitkering gaat het om? | `variabele-uitkeringen[i]/soort` | radio | Performance uitkering → `performance` · Bonusuitkering → `bonus` · Winstuitkering → `winst` · Anders, namelijk: → `anders` | (blok) | | ja | `name` = "Variabele uitkering: " + waarde |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/soort_anders_namelijk` | tekst | — | `soort` = `anders` | | ja | vervangt de waarde in `name` |
| Welke voorwaarden zijn van toepassing? — Bepaalde prestatie (performance), namelijk: | `variabele-uitkeringen[i]/voorwaarden/prestatie` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Bepaald resultaat (winst), namelijk: | `variabele-uitkeringen[i]/voorwaarden/resultaat` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Afhankelijk minimale duur dienstverband, namelijk: | `variabele-uitkeringen[i]/voorwaarden/min-duur-dienstverband` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Afhankelijk van dienstverband op bepaalde datum, namelijk: | `variabele-uitkeringen[i]/voorwaarden/dienstverband-op-datum` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| Anders, namelijk: | `variabele-uitkeringen[i]/voorwaarden/anders` | checkbox | — | (blok) | | ja | `line[0].conditions[]` (Text) |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/voorwaarden_prestatie_namelijk` | tekst | — | `voorwaarden/prestatie` aangevinkt | | ja | "Bepaalde prestatie (performance), namelijk: " + tekst |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/voorwaarden_resultaat_namelijk` | tekst | — | `voorwaarden/resultaat` aangevinkt | | ja | "Bepaald resultaat (winst), namelijk: " + tekst |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/voorwaarden_min-duur_namelijk` | tekst | — | `voorwaarden/min-duur-dienstverband` aangevinkt | | ja | "Afhankelijk minimale duur dienstverband, namelijk: " + tekst |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/voorwaarden_dienstverband-datum_namelijk` | tekst | — | `voorwaarden/dienstverband-op-datum` aangevinkt | | ja | "Afhankelijk van dienstverband op bepaalde datum, namelijk: " + tekst |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/voorwaarden_anders_namelijk` | tekst | — | `voorwaarden/anders` aangevinkt | | ja | "Anders, namelijk: " + tekst |
| Op welk moment wordt de uitkering uitgekeerd? | `variabele-uitkeringen[i]/toekenning-datum` | datum | — | (blok) | | ja | `payDate {occurrenceType: Single, date}` |
| **Hoe wordt de uitkering toegekend?** (bloktitel) | `variabele-uitkeringen[i]/hoe-toegekend` | radio | Vast percentage van het loon → `percentage-loon` · Vast bedrag, namelijk: → `vast-bedrag` · Anders, namelijk: → `anders` | (blok) | | ja | bepaalt `line[0].amount` |
| ↳ namelijk | `variabele-uitkeringen[i]/type_ander-percentage_percentage` | getal (%) | — | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.value`, `unitCode: Percentage` |
| ↳ van | `variabele-uitkeringen[i]/type_ander-percentage_van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `hoe-toegekend` = `percentage-loon` | | ja | `line[0].amount.baseAmount.unitCode` |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/vast-bedrag_namelijk` | getal (€) | — | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.value`, `unitCode: Euro`, `baseAmount.unitCode: Fixed` |
| ↳ *(geen vraagtekst)* | `variabele-uitkeringen[i]/anders` | tekst | — | `hoe-toegekend` = `anders` | | ja | toegevoegd aan `name` (": " + tekst) |
| ↳ Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur van het dienstverband? | `variabele-uitkeringen[i]/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `hoe-toegekend` = `vast-bedrag` | | ja | `line[0].amount.proportional {partTimePercentage: true, employmentDuration: false}` |
| Geldt er een minimum- of een maximumbedrag? | `variabele-uitkeringen[i]/min-max` | radio | Ja, namelijk: → `ja` · Nee → `nee` | (blok) | | ja | — |
| ↳ minimum | `variabele-uitkeringen[i]/min-max/ja/minimum` | getal (€) | — | `min-max` = `ja` | | ja | `line[0].amount.minValue` |
| ↳ maximum | `variabele-uitkeringen[i]/min-max/ja/maximum` | getal (€) | — | `min-max` = `ja` | | ja | `line[0].amount.maxValue` |

Hulptekst bij de voorwaarden: *"Hieronder volgen meerdere opties, kies welke optie(s) van toepassing is / zijn en
licht de voorwaarden toe"*.

¹ Bouwt per variatie AllowanceArrangement `{name: "Variabele uitkering: <soort>[: <anders>]", typeCode EA903,
origin, payDate?, line: [{interval: 1 × Month, conditions, amount?}]}`.

**Let op:**
- In `name` komt de **waarde** van `soort` (`performance`, `bonus`, `winst`), niet het label.
- `interval` is hardcoded 1 × `Month`, ook al gaat het vaak om een jaarlijkse of eenmalige uitkering.
- Conversie-tak `hoe-toegekend` = `ander-percentage` bestaat, maar die optie staat niet in het formulier.
- Bij `min-max` = `ja` zonder `amount` (bijv. `hoe-toegekend` = `anders`) faalt de conversie.
- Alle voorwaarden worden als `conditionType: Text` opgeslagen (TODO EmploymentDuration in de code).

## Uitgeschakeld in de code

Alleen de commentaarregels `// conditionType: 'EmploymentDuration', // TODO: add form fields to properly fill
EmploymentDuration` in de conversies van min. duur / dienstverband op datum (eenmalig, vast, jubileum, variabel);
er wordt `Text` gebruikt.

---

**Telling:** 34 tekst/getal · 4 datum · 0 tijd · 21 radio/keuzelijst · 11 checkbox (70 vragen), 0 alerts.
(Eenmalig 19, vast 15, jubileum 13, variabel 23; geteld per subsectie met 1 variatie.)
