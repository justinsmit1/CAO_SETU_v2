# 12 · Duurzaam werken en leven

Bron: `src/definition/12_duurzaam-werken-en-leven.tsx` (webformulier v2.1.0).

**Structuur:** vier subsecties. *Duurzame inzetbaarheid* en *Vitaliteit en gezondheid* zijn allebei een
checkboxlijst van regelingen (7 en 5 stuks) plus *Geen*. Die lijst wordt gegenereerd met de lokale helper
`makeBlockItems`: elke aangevinkte regeling klapt dezelfde set vervolgvragen uit (budget, hoogte, naar rato,
uitkering, voorwaarden). *Verplichte scholing* en *Duurzame samenleving* zijn vaste ja/nee-vragen met
vervolgblokken. Er zijn geen herhaalbare rijen. Alles komt terecht in de SETU-lijst `sustainableEmployability`, op
een vaste index.

Lokale keuzelijst **Tijdvak** (`intervalUnitCodeOptions`, dus niet [B2](00_bouwstenen.md#b2--interval-per)):
Uur → `Hour` · Dag → `Day` · Week → `Week` · Maand → `Month` · Jaar → `Year`.

## Duurzame inzetbaarheid

### Duurzame inzetbaarheid

Blok: *"Welke regelingen kent jouw onderneming die de duurzame inzetbaarheid van de werknemer bevorderen?"*
(hulptekst: *"Aanvinken wat van toepassing is (meerdere opties mogelijk)"*).

Regelingen (elke regeling is een checkbox met de vraagset [Regeling-vraagset](#regeling-vraagset-makeblockitems)):

| # | Slug `<r>` | Label | typeCode | SETU-index | *namelijk*-veld |
|---|---|---|---|---|---|
| 1 | `duurzame-inzetbaarheid-regelingen/opleidingen` | Opleidingen | `Education` | `SUSTAINABLE_EMPLOYABILITY_OPLEIDINGEN` | — |
| 2 | `duurzame-inzetbaarheid-regelingen/loopbaancoaching` | Loopbaancoaching | `CareerCoaching` | `SUSTAINABLE_EMPLOYABILITY_LOOPBAANCOACHING` | — |
| 3 | `duurzame-inzetbaarheid-regelingen/outplacementtrajecten` | Outplacementtrajecten | `OutplacementPrograms` | `SUSTAINABLE_EMPLOYABILITY_OUTPLACEMENTTRAJECTEN` | — |
| 4 | `duurzame-inzetbaarheid-regelingen/voorlichting-nederland` | Voorlichting met betrekking tot het in Nederland werken en verblijven van de niet permanent in Nederland woonachtige werknemer | `InformationProvision` | `SUSTAINABLE_EMPLOYABILITY_VOORLICHTING_NEDERLAND` | — |
| 5 | `duurzame-inzetbaarheid-regelingen/scholing-nederland` | Scholing met betrekking tot het in Nederland werken en verblijven van de niet permanent in Nederland woonachtige werknemer | `Education` | `SUSTAINABLE_EMPLOYABILITY_SCHOLING_NEDERLAND` | — |
| 6 | `duurzame-inzetbaarheid-regelingen/sociale-begeleiding-nederland` | Sociale begeleiding met betrekking tot het in Nederland werken en verblijven van de niet permanent in Nederland woonachtige werknemer | `SocialSupport` | `SUSTAINABLE_EMPLOYABILITY_SOCIALE_BEGELEIDING_NEDERLAND` | — |
| 7 | `duurzame-inzetbaarheid-regelingen/anders` | Anders, namelijk: | `Other` | `SUSTAINABLE_EMPLOYABILITY_ANDERS` | ja (hulptekst leeg) |

Na de regelingen volgt:

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Geen | `duurzame-inzetbaarheid-regelingen/geen` | checkbox | — | — | | | — |

Als je *Geen* aanvinkt, worden de 7 regeling-checkboxes leeggemaakt. Hun vervolgantwoorden worden daarbij niet
gewist.

### Regeling-vraagset (`makeBlockItems`)

Deze vraagset hoort bij elke regeling `<r>` uit deze subsectie en uit [Vitaliteit en gezondheid](#vitaliteit-en-gezondheid).

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(label van de regeling)* | `<r>` | checkbox | — | — | | | `sustainableEmployability[<index>]`: bouwt SustainableEmployability {name, typeCode, origin, line[0]} ¹ |
| ↳ *(geen vraagtekst; hulptekst = andersHelp)* | `<r>/namelijk` | tekst | — | `<r>` aangevinkt; bestaat alleen bij regelingen met *namelijk*-veld | | | in `name` |
| ↳ Is er een (individueel) budget verbonden aan deze regeling? | `<r>/budget` | radio | Ja → `ja` · Nee, geef aan wat er gemiddeld per werknemer aan dit onderwerp wordt besteed. → `nee-gemiddeld` | `<r>` aangevinkt | | | bepaalt `line[0]` |
| ↳↳ Hoe hoog is het budget? | `<r>/budget/type` | radio | Percentage van → `percentage` · Vast bedrag namelijk: → `vast-bedrag` · Aantal dagen per jaar → `aantal-dagen-per-jaar` | `<r>/budget` = `ja` | | | bepaalt `line[0]` |
| ↳↳↳ percentage | `<r>/budget/percentage/percentage` | getal (%) | — | `<r>/budget/type` = `percentage` | | | `line[0].amount.value`, `unitCode: Percentage` |
| ↳↳↳ van | `<r>/budget/percentage/van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `<r>/budget/type` = `percentage` | | | `line[0].amount.baseAmount.unitCode` |
| ↳↳↳ per | `<r>/budget/percentage/tijdvak` | keuzelijst | Tijdvak (lokaal, zie boven) | `<r>/budget/type` = `percentage` | | | `line[0].interval.unitCode` |
| ↳↳↳ bedrag | `<r>/budget/vast-bedrag/bedrag` | getal (€) | — | `<r>/budget/type` = `vast-bedrag` | | | `line[0].amount.value`, `unitCode: Euro`, `baseAmount.unitCode: Fixed` |
| ↳↳↳ per | `<r>/budget/vast-bedrag/tijdvak` | keuzelijst | Tijdvak (lokaal) | `<r>/budget/type` = `vast-bedrag` | | | `line[0].interval.unitCode` |
| ↳↳↳ dagen | `<r>/budget/aantal-dagen-per-jaar/aantal` | getal | — | `<r>/budget/type` = `aantal-dagen-per-jaar` | | | `line[0].amount.value`, `unitCode: Day`, `baseAmount: Fixed`, `interval: 1 Year` |
| ↳↳ bedrag | `<r>/gemiddeld/vast-bedrag/bedrag` | getal (€) | — | `<r>/budget` = `nee-gemiddeld` | | | `line[0].amount.value`, `unitCode: Euro`, `baseAmount: Fixed` |
| ↳↳ per | `<r>/gemiddeld/vast-bedrag/tijdvak` | keuzelijst | Tijdvak (lokaal) | `<r>/budget` = `nee-gemiddeld` | | | `line[0].interval.unitCode` |
| ↳ Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur van het dienstverband? | `<r>/naar-rato` | radio | Ja → `ja` · Nee → `nee` | `<r>` aangevinkt | | | `ja` → `line[0].amount.proportional {partTimePercentage: true, employmentDuration: true}` |
| ↳ Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt? | `<r>/uitgekeerd` | radio | Ja, onder de volgende voorwaarden: → `ja` · Nee → `nee` | `<r>` aangevinkt | | | `line[0].conditions[]` (Text) ² |
| ↳↳ *(geen vraagtekst, textarea)* | `<r>/uitgekeerd/ja/namelijk` | tekst | — | `<r>/uitgekeerd` = `ja` | | | in conditie-tekst ² |
| ↳ Zijn er voorwaarden verbonden aan de toekenning van het budget? | `<r>/voorwaarden` | radio | Ja → `ja` · Nee → `nee` | `<r>` aangevinkt | | | — |
| ↳↳ *(geen vraagtekst, textarea)* | `<r>/voorwaarden/ja/namelijk` | tekst | — | `<r>/voorwaarden` = `ja` | | | `line[0].conditions[]` {conditionType: Text, description: tekst} |

¹ `name` = het label. Bij regelingen met een *namelijk*-veld is dat `"<label> <namelijk>"`. Verder:
`origin.type = Unknown` ([B10](00_bouwstenen.md#b10--vaste-setu-standaardwaarden-van-het-formulier)) en
`conditions` begint leeg. `interval.value` is altijd 1.

² Bij `uitgekeerd = ja`: *"Dit budget wordt uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt,
onder de volgende voorwaarden: <tekst>"*. Bij `nee`: *"Dit bedrag wordt NIET uitgekeerd als er geen of niet
geheel gebruik van wordt gemaakt."*

**Let op:**
- Voor `naar-rato = ja`, `uitgekeerd` en `voorwaarden` gaat de code ervan uit dat `line[0]` al bestaat. Als
  `budget` (of `budget/type`) niet is ingevuld, bestaat `line[0]` niet en loopt de conversie vast met een
  JS-fout.
- *"Aantal dagen per jaar"* wordt vastgelegd als `unitCode: Day` met `interval` 1 × `Year`. De tijdvak-keuze is
  hier altijd vast.
- De keuze tussen *budget* en *gemiddelde besteding* (`nee-gemiddeld`) is in SETU niet terug te zien. Beide
  worden een gewone `line[0]` met een bedrag.
- Het label *"Vast bedrag namelijk:"* heeft geen apart *namelijk*-tekstveld.

## Vitaliteit en gezondheid

### Vitaliteit en gezondheid

Blok: *"Welke regelingen kent jouw onderneming die de vitaliteit en gezondheid van de werknemer bevorderen?"*

Regelingen (elke regeling is een checkbox met de [Regeling-vraagset](#regeling-vraagset-makeblockitems)):

| # | Slug `<r>` | Label | typeCode | SETU-index | *namelijk*-veld (hulptekst) |
|---|---|---|---|---|---|
| 1 | `vitaliteit-gezondheid-regelingen/fysieke-gezondheid` | Regeling ter bevordering van de fysieke gezondheid, namelijk: | `ArrangementForHealth` | `SUSTAINABLE_EMPLOYABILITY_FYSIEKE_GEZONDHEID` | ja: *"denk vergoeding voor aan (periodieke) gezondheidschecks, vitaliteitsbudget, coaching voor een gezonde leefstijl etc."* |
| 2 | `vitaliteit-gezondheid-regelingen/mentale-gezondheid` | Regeling ter bevordering van de mentale gezondheid, namelijk: | `ArrangementForMentalHealth` | `SUSTAINABLE_EMPLOYABILITY_MENTALE_GEZONDHEID` | ja: *"denk aan vitaliteitsbudget gericht op mentaal welzijn, inzet coach, psycholoog etc."* |
| 3 | `vitaliteit-gezondheid-regelingen/financiele-gezondheid` | Regeling ter bevordering van de financiële gezondheid, namelijk: | `ArrangementForFinancialHealth` | `SUSTAINABLE_EMPLOYABILITY_FINANCIELE_GEZONDHEID` | ja: *"denk aan inzet financieel planner etc."* |
| 4 | `vitaliteit-gezondheid-regelingen/vitaliteitsbudget` | Vitaliteitsbudget | `VitalityBudget` | `SUSTAINABLE_EMPLOYABILITY_VITALITEITSBUDGET` | — |
| 5 | `vitaliteit-gezondheid-regelingen/anders` | Anders, namelijk: | `Other` | `SUSTAINABLE_EMPLOYABILITY_VITALITEIT_ANDERS` | ja (hulptekst leeg) |

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Geen | `vitaliteit-gezondheid-regelingen/geen` | checkbox | — | — | | | — |

Als je *Geen* aanvinkt, worden de 5 regeling-checkboxes leeggemaakt.

## Verplichte scholing

### Verplichte scholing

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er sprake van scholing die op grond van de wet of cao noodzakelijk is voor de uitvoering van het werk? | `verplichte-scholing` | radio | Ja, namelijk: → `ja` · Nee → `nee` | — | | | `sustainableEmployability[SUSTAINABLE_EMPLOYABILITY_VERPLICHTE_SCHOLING]`: bouwt SustainableEmployability {name, typeCode `Other`, line[0] tijd, line[1] kosten} ³ |
| ↳ *(geen vraagtekst, textarea)* | `verplichte-scholing/ja/namelijk` | tekst | — | `verplichte-scholing` = `ja` | | | `name` = `"Verplichte scholing: <tekst>"` |

Blok zonder titel. Het hele blok is zichtbaar als `verplichte-scholing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Hoeveel kost de verplichte scholing in tijd? | `verplichte-scholing-tijd` | getal | — | (blok) | | | `line[0].amount.value` |
| *(geen vraagtekst, eenheid)* | `verplichte-scholing-tijd-type` | keuzelijst (zonder lege optie) | Uur → `Hour` · Dagen → `Day` | (blok) | | | `line[0].amount.unitCode` |

### Wanneer wordt de verplichte scholing gevolgd?

Het hele blok is zichtbaar als `verplichte-scholing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `verplichte-scholing-wanneer` | radio | Tijdens werktijd, namelijk: → `tijdens-werktijd` · Op een ander moment, namelijk: → `ander-moment` | (blok) | | | `line[0].conditions[0]` (Text) ⁴ |
| ↳ *(geen vraagtekst)* | `verplichte-scholing-wanneer/tijdens-werktijd/namelijk` | tekst | — | `verplichte-scholing-wanneer` = `tijdens-werktijd` | | | in conditie-tekst |
| ↳ *(geen vraagtekst)* | `verplichte-scholing-wanneer/ander-moment/namelijk` | tekst | — | `verplichte-scholing-wanneer` = `ander-moment` | | | in conditie-tekst |

### Hoeveel kost de verplichte scholing inclusief alle bijkomende kosten (studiemateriaal, examengelden etc.)?

Het hele blok is zichtbaar als `verplichte-scholing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `verplichte-scholing-kosten` | getal (€) | — | (blok) | | | `line[1].amount.value`, `unitCode: Euro` |

³ `line[0]` = tijd: {amount {value, unitCode Hour/Day, baseAmount Fixed}, interval 1 × `Item`, conditions}.
`line[1]` = kosten: {amount {value, Euro, baseAmount Fixed}, interval 1 × `Item`}.

⁴ Bij `tijdens-werktijd` wordt het *"Tijdens werktijd, namelijk: <tekst>"*. In **alle andere gevallen**, ook als
er niets is ingevuld, wordt het *"Op een ander moment, namelijk: <tekst>"*.

**Let op:** typeCode staat vast op `Other` (er is geen specifieke code voor verplichte scholing). "Per scholing"
wordt vastgelegd als `interval.unitCode: Item`.

## Duurzame samenleving

### Duurzame samenleving

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming regelingen voor een duurzame samenleving en groene aarde? Zoals klimaatbudget, vrije dagen voor vrijwilligerswerk, etc. | `duurzame-samenleving-regeling` | radio | Ja → `ja` · Nee → `nee` | — | | | — |

Het hele blok is zichtbaar als `duurzame-samenleving-regeling` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er een (individueel) budget verbonden aan regelingen voor een duurzame samenleving en een groene aarde? | `duurzame-samenleving-budget` | radio | Ja → `ja` · Nee → `nee` | (blok) | | | `sustainableEmployability[SUSTAINABLE_EMPLOYABILITY_DUURZAME_SAMENLEVING]`: bouwt SustainableEmployability {name "Duurzame samenleving", typeCode `SustainableSociety`, line[0]} ⁵ |

### Hoe hoog is het budget?

Het hele blok is zichtbaar als `duurzame-samenleving-budget` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `duurzame-samenleving-budget-hoogte` | radio | Percentage van → `percentage` · Vast bedrag namelijk: → `vast-bedrag` · Uren of dagen → `uren-of-dagen` | (blok) | | | bepaalt `line[0]` |
| ↳ percentage | `duurzame-samenleving-budget-hoogte/percentage/percentage` | getal (%) | — | `…-hoogte` = `percentage` | | | `line[0].amount.value`, `unitCode: Percentage` |
| ↳ van | `duurzame-samenleving-budget-hoogte/percentage/van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `…-hoogte` = `percentage` | | | `line[0].amount.baseAmount.unitCode` |
| ↳ per | `duurzame-samenleving-budget-hoogte/percentage/tijdvak` | keuzelijst | Tijdvak (lokaal) | `…-hoogte` = `percentage` | | | `line[0].interval.unitCode` (standaard `Year`) |
| ↳ Bedrag | `duurzame-samenleving-budget-hoogte/vast-bedrag/bedrag` | getal (€) | — | `…-hoogte` = `vast-bedrag` | | | `line[0].amount.value`, `unitCode: Euro`, `baseAmount: Fixed` |
| ↳ per (tijdvak) | `duurzame-samenleving-budget-hoogte/vast-bedrag/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `…-hoogte` = `vast-bedrag` | | | `line[0].interval.unitCode` (standaard `Year`) |
| ↳ aantal | `duurzame-samenleving-budget-hoogte/uren-of-dagen/aantal` | getal | — | `…-hoogte` = `uren-of-dagen` | | | `line[0].amount.value` |
| ↳ type | `duurzame-samenleving-budget-hoogte/uren-of-dagen/type` | keuzelijst (zonder lege optie) | Uren → `Hour` · Dagen → `Day` | `…-hoogte` = `uren-of-dagen` | | | `line[0].amount.unitCode` |
| ↳ per | `duurzame-samenleving-budget-hoogte/dagen-per/per` | keuzelijst | Week → `Week` · Maand → `Month` · Jaar → `Year` | `…-hoogte` = `uren-of-dagen` | | | `line[0].interval.unitCode` (standaard `Year`) |

### Naar rato

Blok zonder titel. Het hele blok is zichtbaar als `duurzame-samenleving-budget` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur van het dienstverband? | `duurzame-samenleving-budget-naar-rato` | radio | Ja → `ja` · Nee → `nee` | (blok) | | | `ja` → `line[0].amount.proportional {partTimePercentage: true, employmentDuration: true}` |

### Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt?

Het hele blok is zichtbaar als `duurzame-samenleving-budget` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `duurzame-samenleving-budget-uitgekeerd` | radio | Ja → `ja` · Nee → `nee` | (blok) | | | `line[0].conditions[]` (Text) ⁶ |
| ↳ onder de volgende voorwaarden | `duurzame-samenleving-budget-uitgekeerd/ja/voorwaarden` | tekst (textarea) | — | `…-uitgekeerd` = `ja` | | | in conditie-tekst |

### Zijn er voorwaarden verbonden aan de toekenning van het budget?

Het hele blok is zichtbaar als `duurzame-samenleving-budget` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `duurzame-samenleving-budget-voorwaarden` | radio | Ja, namelijk: → `ja` · Nee → `nee` | (blok) | | | — |
| ↳ *(geen vraagtekst, textarea)* | `duurzame-samenleving-budget-voorwaarden/ja/namelijk` | tekst | — | `…-voorwaarden` = `ja` | | | `line[0].conditions[]` {conditionType: Text, description: tekst} |

⁵ `line[0]` begint als {amount 0 Euro Fixed, interval 1 × `Year`} en wordt daarna overschreven op basis van
`duurzame-samenleving-budget-hoogte`. `origin.type = Unknown`.

⁶ Bij `ja` met voorwaarden: *"Dit budget wordt uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt,
onder de volgende voorwaarden: <tekst>"*. Bij `ja` zonder tekst: dezelfde zin zonder de voorwaarden. Bij `nee`:
*"Dit budget wordt NIET uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt."*

**Let op:**
- Als `duurzame-samenleving-regeling` = `ja` is en `duurzame-samenleving-budget` = `nee`, wordt er **niets** naar
  SETU geschreven. Dat er een regeling bestaat zonder budget, is dan alleen terug te zien in `__webform_data__`.
- Als er geen hoogte gekozen is, schrijft de code een budget van €0 per jaar weg.
- Bij *Uren of dagen* staat de slug van de "per"-vraag onder `…/dagen-per/per` en niet onder `…/uren-of-dagen/`.

## Uitgeschakeld in de code

Niets.

---

**Telling:** 87 tekst/getal · 0 datum · 0 tijd · 122 radio/keuzelijst · 14 checkbox (223 vragen, na uitklappen
van 12 regelingen × vraagset van 16 vragen + 5 *namelijk*-velden), 0 alerts.
