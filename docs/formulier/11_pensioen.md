# 11 · Pensioen

Bron: `src/definition/11_pensioen.tsx` (webformulier v2.1.0).

**Structuur:** één subsectie zonder menu-label. Een ja/nee-vraag opent drie vervolgblokken: naam van het
pensioenfonds, de werkgeverspremie (percentage) en de franchise. Er zijn geen herhaalbare delen. Alles komt in één
SETU-object `pension[0]`.

## Pensioen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ken je een pensioenregeling? | `pensioenregeling/van-toepassing` | radio | Ja → `ja` · Nee → `nee` | — | | | `pension[0]`, bouwt Pension {name, origin, line: [werkgeverspremie], franchise?} |

### Pensioenfonds

Het hele blok is zichtbaar als `pensioenregeling/van-toepassing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Wat is de naam van het pensioenfonds? | `pensioenregeling/pensioenfonds/naam` | tekst | — | (blok) | | | `pension[0].name` (leeg → "Pensioenregeling") |

### Wat is de hoogte van de werkgeverspremie?

Het hele blok is zichtbaar als `pensioenregeling/van-toepassing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| … % van de pensioengrondslag | `pensioenregeling/werkgeverspremie/percentage` | getal (postfix %) | — | (blok) | | | `pension[0].line[0].amount.value` |

Alert: *"De grondslag wordt later in het formulier uitgevraagd"*.

De regel `line[0]` krijgt vaste waarden: `amount.unitCode: Percentage`, `baseAmount` {unitCode `YearlyRate`, baseType
`Pension`}, `interval` {1, `Year`}, `contributionSource: Employer`, `conditions: []`.

### Hanteer je een franchise?

Het hele blok is zichtbaar als `pensioenregeling/van-toepassing` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `pensioenregeling/franchise/van-toepassing` | radio | Ja, namelijk: → `ja` · Nee → `nee` | (blok) | | | bij `ja`: `pension[0].franchise` |
| ↳ *(placeholder: "Geef een beschrijving van de franchise")* | `pensioenregeling/franchise/namelijk` | tekst (textarea) | — | `pensioenregeling/franchise/van-toepassing` = `ja` | | | `pension[0].franchise.description` |

**Let op:**
- `setuPath` is `["pension", 0]`, met een letterlijke 0 in plaats van een constante uit `constants.ts`.
- Loonbasis (`YearlyRate`), grondslag (`Pension`), interval (`Year`) en premiebron (`Employer`) staan vast in de
  code. Het formulier vraagt alleen naar een werkgeverspremie; een werknemersbijdrage kan niet worden ingevuld.
- De franchise is alleen vrije tekst (`description`), zonder bedrag.
- In [15 Grondslagen](15_grondslagen.md) wordt de grondslag `Pension` toegevoegd als `pensioenregeling` = `ja`.
  Die slug bestaat niet: de vraag heet `pensioenregeling/van-toepassing`. Die koppeling werkt daardoor
  waarschijnlijk nooit.

---

**Telling:** 3 tekst/getal · 0 datum · 0 tijd · 2 radio/keuzelijst · 0 checkbox (5 vragen), 1 alert.
