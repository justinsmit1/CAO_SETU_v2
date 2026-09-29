# 08 · Loondoorbetaling bij ziekte

Bron: `src/definition/08_loondoorbetaling-bij-ziekte.tsx` (webformulier v2.1.0).

**Structuur:** één subsectie *Loondoorbetaling bij ziekte* met vier blokken: (1) de herhaalbare percentageregels
`loondoorbetaling-bij-ziekte[]` ("variaties"), (2) wachtdagen, (3) voorwaarden voor wachtdagen en (4)
wachtdagcompensatie. Alles behalve de wachtdagcompensatie komt samen in één SETU-object `sickPay[0]`. Geen
Bedragregels (B1): de bedragvragen van de wachtdagcompensatie zijn handmatig gebouwd.

## Loondoorbetaling bij ziekte

### Hoe hoog is het percentage dat bij ziekte wordt doorbetaald?

Herhaalbare rijen `loondoorbetaling-bij-ziekte[i]`; het aantal rijen komt uit `countAnswerRows`. De Store begint met
één lege rij (`"loondoorbetaling-bij-ziekte": [{}]`). Knop: *Variatie toevoegen* (onderaan het blok, voegt een lege
rij toe) en per rij *Variatie verwijderen* (alleen als er > 1 rij is).

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Percentage | `loondoorbetaling-bij-ziekte[i]/percentage` | getal (%) | — | — | | ja | `sickPay[0]` — alleen bij rij 0: bouwt SickPay {name "Loondoorbetaling bij ziekte", line[j] per rij, waitingDays} |
| Van: | `loondoorbetaling-bij-ziekte[i]/percentage_bedrag` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | — | | ja | `sickPay[0].line[j].amount.baseAmount.unitCode` |
| Grondslag: | `loondoorbetaling-bij-ziekte[i]/grondslag` | keuzelijst | [B4 Grondslag](00_bouwstenen.md#b4--grondslag) | — | ja | ja | `sickPay[0].line[j].amount.baseAmount.baseType` ¹ |
| Per (tijdvak) | `loondoorbetaling-bij-ziekte[i]/percentage_per_tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Week → `Week` · Maand → `Month` · Jaar → `Year` | — | | ja | `sickPay[0].line[j].interval.unitCode` (leeg → `Day`) |
| Voorwaarden | `loondoorbetaling-bij-ziekte[i]/voorwaarden` | tekst (textarea) | — | — | | ja | `sickPay[0].line[j].conditions[0]` (Text) |

Hulptekst bij *Voorwaarden*: *"Bijvoorbeeld: tijdens de eerste 3 dagen van de ziekte"*.

SETU: de conversie hangt aan de percentagevraag van rij 0 (andere rijen geven `null`); is die leeg, dan wordt er
helemaal geen `sickPay` gemaakt. Per rij `j` ontstaat `line[j]` = {amount {value, `unitCode: Percentage`,
baseAmount {unitCode, baseType}}, interval {1 × tijdvak}, conditions}. `origin.type = Unknown`; er is geen typeCode.

¹ **Let op (bug):** `line[j].amount.value` is voor álle regels het percentage van rij 0 (de `value` van de vraag), en
`baseType` is voor alle regels de grondslag van rij 0 (`i2` i.p.v. `j`). Alleen `percentage_bedrag`,
`percentage_per_tijdvak` en `voorwaarden` worden echt per rij overgenomen. Het percentage en de grondslag van rij 1+
staan dus alleen in `__webform_data__`. Wel verschijnt de grondslag van elke rij in [15 Grondslagen](15_grondslagen.md).

### Wachtdagen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Zijn er wachtdagen? | `wachtdagen` | radio | Ja, namelijk: → `ja` · Nee → `nee` | — | | | — |
| ↳ *(aantal)* | `wachtdagen_ja_namelijk` | getal (postfix "dagen") | — | `wachtdagen` = `ja` | | | `sickPay[0].waitingDays` {value, `unitCode: Day`} |

### Voorwaarden wachtdagen

Het hele blok is zichtbaar als `wachtdagen` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Zitten er voorwaarden aan het toekennen van de wachtdagen? | `wachtdagen_voorwaarden` | radio | Ja, namelijk: → `ja` · Nee → `nee` | (blok) | | | bij `ja`: `waitingDays.conditions` |
| ↳ *(namelijk)* | `wachtdagen_voorwaarden_ja_namelijk` | tekst (textarea) | — | `wachtdagen_voorwaarden` = `ja` | | | `sickPay[0].waitingDays.conditions[0]` (Text) |

Hulptekst: *"Bijvoorbeeld dat er pas na een bepaald aantal ziekmeldingen een wachtdag wordt gehanteerd."*

**Let op:** `waitingDays` wordt binnen de `sickPay`-conversie gezet zodra `wachtdagen_ja_namelijk` een waarde heeft —
de conversie controleert `wachtdagen` = `ja` niet. Wachtdagen komen alleen in SETU als het percentage van rij 0 is
ingevuld.

### Wachtdagcompensatie

Het hele blok is zichtbaar als `wachtdagen` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Geldt er een wachtdagcompensatie? | `wachtdagcompensatie` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | (blok) | | | `allowance[ALLOWANCE_WACHTDAGCOMPENSATIE]` — bij `ja`: AllowanceArrangement {name "Wachtdagcompensatie", typeCode EA600, line[0]} |
| ↳ Hoe wordt de wachtdagcompensatie uitgekeerd? | `wachtdagcompensatie/amount-type` | radio | Vast bedrag → `vast-bedrag` · Percentage van loon → `percentage` | `wachtdagcompensatie` = `ja` | | | bepaalt `line[0].amount` |
| ↳↳ Bedrag | `wachtdagcompensatie/amount-type/vast-bedrag/bedrag` | getal (€) | — | `wachtdagcompensatie/amount-type` = `vast-bedrag` | | | `line[0].amount.value` (`Euro`, `baseAmount: Fixed`) |
| ↳↳ Percentage | `wachtdagcompensatie/amount-type/percentage/percentage` | getal (%) | — | `wachtdagcompensatie/amount-type` = `percentage` | | | `line[0].amount.value` (`Percentage`) |
| ↳↳ van | `wachtdagcompensatie/amount-type/percentage/basis` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `wachtdagcompensatie/amount-type` = `percentage` | | | `line[0].amount.baseAmount.unitCode` |

**Let op:** de wachtdagcompensatie lijkt op een Bedragregel, maar is handmatig gebouwd: de slugs zitten onder
`wachtdagcompensatie/amount-type/...` (niet `<p>/vast-bedrag/...` zoals in B1), er is geen "per"-vraag en geen
grondslag. `line[0].interval` staat vast op 1 × `Day`; `conditions` is altijd leeg.

---

**Telling:** 6 tekst/getal · 0 datum · 0 tijd · 8 radio/keuzelijst · 0 checkbox (14 vragen, bij één rij; elke extra
rij +2 tekst/getal +3 keuzelijst), 0 alerts. Geen Bedragregels.
