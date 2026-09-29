# 10 · Individueel keuzebudget

Bron: `src/definition/10_individueel-keuzebudget.tsx` (webformulier v2.1.0). Menu-label: "Individueel keuze budget".

**Structuur:** één subsectie zonder menu-label. Een ja/nee-vraag opent drie vervolgblokken: de waarde van het budget
(Bedragregel), of er arbeidsvoorwaarden in het budget zitten, en zo ja welke (vijf checkboxen, vier met
percentage + loonbasis). Er zijn geen herhaalbare delen. Alles komt in één SETU-object
`individualChoiceBudget[INDIVIDUAL_CHOICE_BUDGET]`.

## Individueel keuze budget

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ken je een individueel keuze budget (IKB) of een vergelijkbaar budget waarbij de werknemer kan kiezen uit door de werkgever bepaalde keuzes? | `individueel-keuzebudget` | radio | Ja → `ja` · Nee → `nee` | — | | | `individualChoiceBudget[INDIVIDUAL_CHOICE_BUDGET]`, bouwt IndividualChoiceBudget {name "Individueel keuze budget", origin, line: [Bedragregel], option[]} |

### Waarde van het budget

Het hele blok is zichtbaar als `individueel-keuzebudget` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *Bedragregel*: Wat is de waarde van dit budget? | `individueel-keuzebudget/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd (alleen Vast bedrag / Percentage van loon) | (blok) | | | `line[0]` (via `getLineAmountAnswer`) |

**Let op:** de prefix van de Bedragregel is gelijk aan de slug van de ja/nee-vraag, dus de slugs zijn
`individueel-keuzebudget/amount-type`, `individueel-keuzebudget/vast-bedrag/bedrag` enzovoort. Een gekozen
`individueel-keuzebudget/percentage/grondslag` verschijnt in [15 Grondslagen](15_grondslagen.md).

### Zijn er bepaalde arbeidsvoorwaarden in het budget opgenomen?

Het hele blok is zichtbaar als `individueel-keuzebudget` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `ikb-arbeidsvoorwaarden-opgenomen` | radio | Ja → `ja` · Nee → `nee` | (blok) | | | bij `ja` wordt `option[]` gevuld |

### Welke arbeidsvoorwaarden zijn in het budget opgenomen?

Het hele blok is zichtbaar als `individueel-keuzebudget` = `ja` **en** `ikb-arbeidsvoorwaarden-opgenomen` = `ja`.

Keuzelijst "van" (`vanOptions`, alleen in deze sectie): uurloon → `uurloon` · weekloon → `weekloon` · maandloon →
`maandloon` · periodeloon → `periodeloon` · minimumloon → `minimumloon`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Bovenwettelijke vakantiedagen voor | `ikb-opgenomen-arbeidsvoorwaarden/bovenwettelijke-vakantiedagen` | checkbox | — | (blok) | | | `option[]`: {description "Bovenwettelijke vakantiedagen voor <percentage>% van <van>"} |
| ↳ percentage | `ikb-opgenomen-arbeidsvoorwaarden/bovenwettelijke-vakantiedagen/percentage` | getal (postfix %) | — | checkbox aangevinkt | | | in `description` |
| ↳ van | `ikb-opgenomen-arbeidsvoorwaarden/bovenwettelijke-vakantiedagen/van` | keuzelijst | `vanOptions` | checkbox aangevinkt | | | in `description` |
| ADV dagen voor | `ikb-opgenomen-arbeidsvoorwaarden/adv-dagen` | checkbox | — | (blok) | | | `option[]`: {description "ADV dagen voor <percentage>% van <van>"} |
| ↳ percentage | `ikb-opgenomen-arbeidsvoorwaarden/adv-dagen/percentage` | getal (postfix %) | — | checkbox aangevinkt | | | in `description` |
| ↳ van | `ikb-opgenomen-arbeidsvoorwaarden/adv-dagen/van` | keuzelijst | `vanOptions` | checkbox aangevinkt | | | in `description` |
| Eindejaarsuitkering voor | `ikb-opgenomen-arbeidsvoorwaarden/eindejaarsuitkering` | checkbox | — | (blok) | | | `option[]`: {description "Eindejaarsuitkering voor <percentage>% van <van>"} |
| ↳ percentage | `ikb-opgenomen-arbeidsvoorwaarden/eindejaarsuitkering/percentage` | getal (postfix %) | — | checkbox aangevinkt | | | in `description` |
| ↳ van | `ikb-opgenomen-arbeidsvoorwaarden/eindejaarsuitkering/van` | keuzelijst | `vanOptions` | checkbox aangevinkt | | | in `description` |
| Vakantiebijslag voor | `ikb-opgenomen-arbeidsvoorwaarden/vakantiebijslag` | checkbox | — | (blok) | | | `option[]`: {description "Vakantiebijslag voor <percentage>% van <van>"} |
| ↳ percentage | `ikb-opgenomen-arbeidsvoorwaarden/vakantiebijslag/percentage` | getal (postfix %) | — | checkbox aangevinkt | | | in `description` |
| ↳ van | `ikb-opgenomen-arbeidsvoorwaarden/vakantiebijslag/van` | keuzelijst | `vanOptions` | checkbox aangevinkt | | | in `description` |
| Anders, namelijk: | `ikb-opgenomen-arbeidsvoorwaarden/anders` | checkbox | — | (blok) | | | `option[]`: {description "Anders: <namelijk>"} |
| ↳ *(zonder vraagtekst)* | `ikb-opgenomen-arbeidsvoorwaarden/anders/namelijk` | tekst | — | `…/anders` aangevinkt | | | in `description` |

In de code staan eerst de vijf checkboxen en daarna de vervolgvelden. Door `renderBelow: "showIf"` worden de
vervolgvelden onder hun checkbox getoond.

**Let op:**
- Percentage en loonbasis van de opgenomen arbeidsvoorwaarden worden alleen als vrije tekst in
  `option[].description` gezet, niet als gestructureerd bedrag. De "van"-waarden zijn Nederlandse formulierwaarden
  (`uurloon`, `periodeloon`, …) en geen SETU-codes zoals `HourlyRate`.
- De volgorde in `option[]` staat vast: bovenwettelijke vakantiedagen, ADV, eindejaarsuitkering, vakantiebijslag,
  anders (alleen aangevinkte items).

---

**Telling:** 5 tekst/getal · 0 datum · 0 tijd · 6 radio/keuzelijst · 5 checkbox + 1 Bedragregel (17 vragen, de
Bedragregel telt als 1), 0 alerts.
