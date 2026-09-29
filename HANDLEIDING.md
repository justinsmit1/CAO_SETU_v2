# Handleiding: arbeidsvoorwaarden naar wijzerbelonen.nl

## Waar is deze map voor?

Met deze map zet je de arbeidsvoorwaarden van een opdrachtgever in één keer klaar voor
[wijzerbelonen.nl](https://standaard-uitvraag.wijzerbelonen.nl/). Je hoeft het formulier op de website dan niet met
de hand in te vullen: je uploadt een bestand, en het formulier staat ingevuld klaar.

Je krijgt twee bestanden in de map `uitvoer`:

| Bestand | Waarvoor |
|---|---|
| `wijzerbelonen_upload.json` | Uploaden op wijzerbelonen.nl. Het formulier wordt dan automatisch ingevuld. |
| `setu_kernmodel.json` | Dezelfde gegevens volgens de landelijke SETU-standaard, bijvoorbeeld voor een uitzendbureau of om te vergelijken met andere regelingen. |

## Eenmalig: klaarzetten

Dit hoeft maar één keer per computer.

1. Open het Startmenu, typ **PowerShell** en open het.
2. Installeer het hulpprogramma *uv*: plak deze regel en druk op Enter.
   ```
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Sluit PowerShell en open het opnieuw.
4. Ga naar deze map en zet alles klaar. Pas het pad aan als de map bij jou ergens anders staat.
   ```
   cd "$env:USERPROFILE\OneDrive - Next Standard B.V\Bureaublad\CAO_SETU_v2"
   uv sync
   ```

## Elke keer: het formulier invullen en het bestand maken

1. **Vul het formulier in** in `examples\maak_upload.py` (zie hieronder). Dit doe je in plaats van op de website.
2. Open PowerShell en ga naar deze map (zie stap 4 hierboven, de regel met `cd`).
3. Maak de bestanden:
   ```
   .venv\Scripts\python.exe examples\maak_upload.py
   ```
4. Staat er onderaan **"0"** bij de controle met de echte webform? Dan is het goed gegaan.

## Het formulier invullen in `maak_upload.py`

Open `examples\maak_upload.py`, bijvoorbeeld in Kladblok, VS Code of PyCharm. Het bestand bevat **het hele
formulier**, in dezelfde volgorde als op de website. Elke sectie heeft een eigen blok:

| Sectie op de website | Blok in `maak_upload.py` |
|---|---|
| 01 Algemeen | `vul_algemeen` |
| 02 Beloning | `vul_beloning` |
| 03 Functiegroepen | `vul_functiegroepen` |
| 04 Toeslagen | `vul_toeslagen` |
| 05 Vakantiebijslag | `vul_vakantiebijslag` |
| 06 Vergoedingen | `vul_vergoedingen` |
| 07 Bijzondere uitkeringen | `vul_bijzondere_uitkeringen` |
| 08 Loondoorbetaling bij ziekte | `vul_loondoorbetaling_bij_ziekte` |
| 09 Verlof | `vul_verlof` |
| 10 Individueel keuzebudget | `vul_individueel_keuzebudget` |
| 11 Pensioen | `vul_pensioen` |
| 12 Duurzaam werken en leven | `vul_duurzaam_werken_en_leven` |
| 13 Aanvullende regelingen | `vul_aanvullende_regelingen` |
| 14 Overig | `vul_overig` |
| 15 Grondslagen | `vul_grondslagen` |
| 16 Ondertekenen | `vul_ondertekenen` |

In elk blok staat een ingevuld voorbeeld van een fictieve bouwonderneming. Loop de blokken één voor één door en
vervang de voorbeeldwaarden door die van jouw opdrachtgever.

### Een voorbeeld van álles: `maak_upload_full.py`

Naast `maak_upload.py` staat **`examples\maak_upload_full.py`**. Daarin is vrijwel elke vraag van het formulier
ingevuld: alle toeslagsoorten, alle vergoedingen, alle soorten uitkeringen, alle verlofregelingen, enzovoort. Een
keuzevraag kan maar één antwoord hebben. Waar mogelijk laten extra rijen de andere keuzes zien; anders staan ze als
commentaar (`#`) in het bestand.

Gebruik het als naslag: zoek het onderdeel dat je nodig hebt en neem het over in `maak_upload.py`. Je kunt het ook
zelf draaien en uploaden, om op de website te zien hoe alles eruitziet:

```
.venv\Scripts\python.exe examples\maak_upload_full.py
```

Dit schrijft `uitvoer\wijzerbelonen_upload_full.json`.

### Welke vragen zijn er, en wat mag ik invullen?

Open **`INVULHULP.md`** in de hoofdmap. Daarin staat per sectie elke vraag van de website, met de regel die je
daarvoor schrijft en alle keuzes. Een voorbeeld:

> **Is er een vakantiebijslag?**
> `f.vakantiebijslag.ja_nee = JaNee.JA`
> Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee

### Zo schrijf je de antwoorden

| Soort antwoord | Zo schrijf je het | Let op |
|---|---|---|
| Tekst | `a.sector = "Bouw en infra"` | tussen aanhalingstekens |
| Getal of bedrag | `p.werkgeverspremie_percentage = 14.5` | punt als decimaalteken, zonder € of % |
| Datum | `a.geldig_van = dt.date(2026, 1, 31)` | jaar, maand, dag |
| Ja / Nee | `JaNee.JA` of `JaNee.NEE` | |
| Keuze uit een lijst | `CaoOfRegeling.CAO` | precies zoals in `INVULHULP.md` |
| Vinkje aan | `t.overwerktoeslag_aan = True` | niet aangevinkt: regel weglaten |
| Meerdere rijen | `[Rij(...), Rij(...)]` | bijv. meerdere salarisschalen of contactpersonen; zie de voorbeelden |

### Iets is niet van toepassing?

Zet de ja/nee-vraag op `JaNee.NEE` en haal de regels met de details eronder weg, of zet er een `#` voor. Een regel
met `#` ervoor telt niet mee. Voorbeeld: geen pensioenregeling?

```
p.van_toepassing = JaNee.NEE
# p.pensioenfonds_naam = "bpfBOUW"
```

### Het script bewaakt de regels van het formulier

Vul je iets in wat op de website niet getoond zou worden, zoals een cao-naam terwijl er "geen cao" is gekozen? Of
een keuze die niet bestaat? Dan stopt het script met een melding die zegt welke vraag niet klopt. Pas het aan en
draai het script opnieuw.

## Uploaden op wijzerbelonen.nl

1. Ga naar https://standaard-uitvraag.wijzerbelonen.nl/.
2. Kies **Importeren** en selecteer `uitvoer\wijzerbelonen_upload.json`.
3. Het formulier staat nu volledig ingevuld, inclusief de ondertekening. Wil je iets wijzigen? Doe dat in
   `maak_upload.py` en maak het bestand opnieuw. Zo blijven het Python-bestand en de website gelijk.

## Hulp nodig?

| Wat zie je? | Wat doe je? |
|---|---|
| `uv` of `python` wordt niet herkend | De stappen onder *Eenmalig: klaarzetten* zijn nog niet (goed) gedaan. |
| Een foutmelding na het aanpassen van de gegevens | Lees de melding: die zegt welke vraag niet klopt. Veelvoorkomend: een vergeten aanhalingsteken of komma, of een vraag ingevuld terwijl de ja/nee-vraag erboven op `NEE` staat. Kom je er niet uit, stuur de melding naar Justin. |
| "punt(en)" bij de *SETU-controle* | Geen probleem voor de upload. Dit gaat alleen over het SETU-bestand en komt vaak door een fout in de website zelf. |
| De website geeft een waarschuwing bij Importeren | Controleer of je het bestand `wijzerbelonen_upload.json` hebt gekozen, en niet `setu_kernmodel.json`. |

Laat de andere mappen (`src`, `tests`, `docs`, …) zoals ze zijn. Daar staat de techniek achter het script.
