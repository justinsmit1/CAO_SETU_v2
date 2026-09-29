# 05 · Vakantiebijslag

Bron: `src/definition/05_vakantiebijslag.tsx` (webformulier v2.1.0).

**Structuur:** één subsectie *Vakantiebijslag*: een ja/nee-vraag. Bij *Ja* volgt een Bedragregel die alleen een
percentage toestaat. Er zijn geen herhaalbare delen.

## Vakantiebijslag

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er een vakantiebijslag? | `vakantiebijslag/ja-nee` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | — | | | `holidayAllowance[HOLIDAY_ALLOWANCE_PERCENTAGE_PERIOD]`: bouwt `{name: "Vakantiebijslag", origin: {type: Unknown}, line: [Bedragregel]}` bij `ja` |
| ↳ *Bedragregel* — Hoeveel bedraagt de vakantiebijslag? | `vakantiebijslag/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder vast bedrag, zonder tijd, dus alleen *Percentage van loon* (percentage, van, per, grondslag) | `vakantiebijslag/ja-nee` = `ja` (blok) | | | via `getLineAmountAnswer` → `line[0]` |

Uitgeschreven slugs van de Bedragregel: `vakantiebijslag/amount-type`, `vakantiebijslag/percentage/percentage`,
`vakantiebijslag/percentage/basis`, `vakantiebijslag/percentage/per`, `vakantiebijslag/percentage/grondslag`.

**Let op:**
- De naam in SETU is altijd de vaste tekst "Vakantiebijslag", en `origin.type` is altijd `Unknown`.
- Index `HOLIDAY_ALLOWANCE_PERCENTAGE_MINIMUM` (1) bestaat wel in `constants.ts`, maar wordt in deze sectie niet
  gebruikt. Een minimumbedrag voor de vakantiebijslag vraagt het formulier dus niet uit.
- Een gekozen grondslag laat die grondslag verschijnen in [15 Grondslagen](15_grondslagen.md).

---

**Telling:** 0 tekst · 0 datum · 0 tijd · 1 radio · 0 checkbox (1 vraag) + 1 Bedragregel, 0 alerts.
