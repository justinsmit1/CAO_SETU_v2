# Invulhulp: alle vragen per sectie

Dit bestand is gemaakt met `examples\invulhulp.py`. Maak het na een wijziging in het formulier opnieuw.

Zo lees je het:
- Per vraag staat de regel die je in `maak_upload.py` schrijft. Pas alleen de waarde na het `=` aan.
- **Keuzes** schrijf je precies zoals hier staat, bijv. `JaNee.JA`.
- *(alleen als: …)* betekent dat je deze vraag alleen mag invullen als die andere vraag zo beantwoord is. Anders
  geeft het script een melding.
- **Herhaalbaar** (bijv. meerdere salaristabellen) schrijf je als een lijst: `[Rij(...), Rij(...)]`. Binnen een rij
  zet je de antwoorden tussen de haakjes: `Salaristabel(naam="Tabel 2026", geldig_vanaf=dt.date(2026, 1, 1))`.
- **Per sleutel** (bijv. per grondslag) schrijf je als `{sleutel: waarde}`, bijv. `{Grondslag.BRUTO_LOON: GrondslagInstelling(salaris=True)}`.
- **Datums:** `dt.date(2026, 1, 31)`. **Bedragen en percentages:** gewone getallen, met een punt als decimaalteken
  (`8.5`).

## Bedragen (Bedragregel)

Veel vragen vragen om een bedrag, een percentage of een aantal uren. Dat schrijf je zo:

```python
Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=50, per=Interval.MAAND))
Bedragregel(soort=BedragSoort.PERCENTAGE, percentage=Percentage(percentage=8, basis=Loonbasis.JAARLOON,
                                                               per=Interval.JAAR, grondslag=Grondslag.BRUTO_LOON))
Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=2, per=Interval.WEEK))
Bedragregel(soort=BedragSoort.NVT)            # alleen waar "N.v.t." een keuze is
```

- `Interval` ("per"): UUR, DAG, WEEK, MAAND, KWARTAAL, JAAR, DAGDEEL, DIENST, EENMALIG, GEWERKTE_DAG, ITEM, KILOMETER,
  NACHT, OP_DECLARATIEBASIS, RIT, ROUTE, THUISWERKDAG, VERHUIZING, WEKELIJKSE_REISDAG.
- `Loonbasis` ("van"): UURLOON, DAGLOON, VIERWEKENLOON, MAANDLOON, JAARLOON.
- `Grondslag` (optioneel): BASISLOON, BRUTO_LOON, SV_LOON, VAKANTIEBIJSLAG, PENSIOEN, DERTIENDE_MAAND,
  GEBRUIKELIJK_LOON.

## 01 · Algemeen

In `maak_upload.py`: `f.algemeen` (zie `vul_algemeen`).

- **Geef je arbeidsvoorwaardenregeling een naam of nummer:**  
  `f.algemeen.naam_regeling = "tekst"`
- **Geldig van**  
  `f.algemeen.geldig_van = dt.date(2026, 1, 1)`
- **tot**  
  `f.algemeen.geldig_tot = dt.date(2026, 1, 1)`
- **Naam onderneming(en) / organisatie(s):**  
  `f.algemeen.opdrachtgever_naam = "tekst"`
- **Bijbehorende KvK of een ander identificatienummer van de onderneming(en) / organisatie(s) waarvoor dit uitv…**  
  `f.algemeen.opdrachtgever_kvk = "tekst"`
- **Type identificatienummer**  
  `f.algemeen.opdrachtgever_kvk_type = TypeIdentificatienummer.KVK`  
  Keuzes: `TypeIdentificatienummer.KVK` = KvK · `TypeIdentificatienummer.OIN` = OIN · `TypeIdentificatienummer.RSIN` = RSIN
- **In welke sector ben je actief?**  
  `f.algemeen.sector = "tekst"`
- **Hoe zijn de arbeidsvoorwaarden voor jouw eigen werknemers geregeld?**  
  `f.algemeen.cao_of_regeling = CaoOfRegeling.CAO`  
  Keuzes: `CaoOfRegeling.CAO` = Er is een cao van toepassing · `CaoOfRegeling.EIGEN_REGELING` = Er is of zijn (een) eigen arbeidsvoorwaardenregeling(en) van toepassing · `CaoOfRegeling.CAO_EN_EIGEN_REGELING` = Er is een cao van toepassing en wij hebben (een) eigen arbeidsvoorwaardenregeling(en) · `CaoOfRegeling.GEEN` = Er is geen cao of arbeidsvoorwaardenregeling van toepassing
- **Naam cao:** *(alleen als: cao_of_regeling = cao-van-toepassing of cao-en-eigen-arbeidsvoorwaardenregeling)*  
  `f.algemeen.cao_naam = "tekst"`
- **Nummer cao:** *(alleen als: cao_of_regeling = cao-van-toepassing of cao-en-eigen-arbeidsvoorwaardenregeling)*  
  `f.algemeen.cao_nummer = "tekst"`
- **Wat geldt er binnen jouw onderneming?** *(alleen als: cao_of_regeling = cao-van-toepassing of cao-en-eigen-arbeidsvoorwaardenregeling)*  
  `f.algemeen.cao_van_toepassing_omdat = CaoVanToepassingOmdat.LID_BRANCHEORGANISATIE`  
  Keuzes: `CaoVanToepassingOmdat.LID_BRANCHEORGANISATIE` = Je onderneming is lid van de brancheorganisatie · `CaoVanToepassingOmdat.ALGEMEEN_VERBINDEND` = De cao is algemeen verbindend verklaard · `CaoVanToepassingOmdat.IN_ARBEIDSOVEREENKOMST` = De cao wordt van toepassing verklaard in de arbeidsovereenkomst van de werknemers
- **van** *(alleen als: cao_van_toepassing_omdat = algemeen-verbindend)*  
  `f.algemeen.cao_van = dt.date(2026, 1, 1)`
- **tot** *(alleen als: cao_van_toepassing_omdat = algemeen-verbindend)*  
  `f.algemeen.cao_tot = dt.date(2026, 1, 1)`

## 02 · Beloning

In `maak_upload.py`: `f.beloning` (zie `vul_beloning`).

- **Welke salaristabellen kent de onderneming?**  
  `f.beloning.beloningen = [Salaristabel(...), Salaristabel(...)]`: herhaalbaar; per rij:
  - **Naam**  
    `naam="tekst"`
  - **van**  
    `geldig_vanaf=dt.date(2026, 1, 1)`
  - **tot**  
    `geldig_per=dt.date(2026, 1, 1)`
  - **Deze salaristabel is van toepassing in de volgende situatie: (bijvoorbeeld bij werken in een vijf of drie p…** *(alleen als: alleen bij de 2e salaristabel en verder (i > 0))*  
    `voorwaarden="tekst"`
  - **Wat is de normale arbeidsduur per week? Hiermee wordt de arbeidsomvang per week bedoeld (...)**  
    `normale_arbeidsduur=NormaleArbeidsduur.UUR_40`  
    Keuzes: `NormaleArbeidsduur.UUR_40` = 40 uur · `NormaleArbeidsduur.UUR_38` = 38 uur · `NormaleArbeidsduur.UUR_36` = 36 uur · `NormaleArbeidsduur.ANDERS` = Anders, namelijk:
  - **Anders, namelijk: (uur)** *(alleen als: normale_arbeidsduur = anders)*  
    `normale_arbeidsduur_anders=40` (uur)
  - **Hoe is de beloning vastgesteld?**  
    `beloning_vastgesteld=BeloningInterval.PER_MAAND`  
    Keuzes: `BeloningInterval.PER_MAAND` = Per maand · `BeloningInterval.PER_VIER_WEKEN` = Per vier weken · `BeloningInterval.PER_WEEK` = Per week · `BeloningInterval.PER_UUR` = Per uur
  - **Zijn in jouw arbeidsvoorwaardenregeling of cao uurlonen voor eigen werknemers vastgelegd of kent (...) een …** *(alleen als: niet (beloning_vastgesteld = per-uur))*  
    `uurlonen_vastgelegd=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Ja, namelijk: (%)** *(alleen als: (niet (beloning_vastgesteld = per-uur)) en (uurlonen_vastgelegd = ja))*  
    `uurlonen_percentage=8` (%)
  - **Welke salarisschalen kent de onderneming?**  
    `salarisschalen=[Salarisschaal(...), Salarisschaal(...)]`: herhaalbaar; per rij:
    - **Schaal**  
      `naam="tekst"`
    - **Minimaal bedrag (€)**  
      `minimaal_bedrag=1250` (€)
    - **Maximaal bedrag (€)**  
      `maximaal_bedrag=1250` (€)
    - **Stappen**  
      `stappen=[Stap(...), Stap(...)]`: herhaalbaar; per rij:
      - **Stap / Trede**  
        `naam="tekst"`
      - **Bedrag (€)**  
        `bedrag=1250` (€)
  - **Wordt werkervaring bij de inschaling meegenomen?**  
    `werkervaring_inschaling=WerkervaringInschaling.JA_SECTOR`  
    Keuzes: `WerkervaringInschaling.JA_SECTOR` = Ja, relevante werkervaring in de sector wordt als volgt meegenomen · `WerkervaringInschaling.JA_ONDERNEMING` = Ja, relevante werkervaring bij onze onderneming wordt als volgt meegenomen · `WerkervaringInschaling.JA_FUNCTIE` = Ja, relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen · `WerkervaringInschaling.JA_ALS_VOLGT` = Ja, namelijk als volgt · `WerkervaringInschaling.NEE` = Nee
  - **Relevante werkervaring in de sector wordt als volgt meegenomen: (tekstvak)** *(alleen als: werkervaring_inschaling = ja-sector)*  
    `werkervaring_sector="tekst"`
  - **Relevante werkervaring bij onze onderneming wordt als volgt meegenomen: (tekstvak)** *(alleen als: werkervaring_inschaling = ja-onderneming)*  
    `werkervaring_onderneming="tekst"`
  - **Relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen: (tekstvak)** *(alleen als: werkervaring_inschaling = ja-functie)*  
    `werkervaring_functie="tekst"`
  - **Ja, namelijk als volgt: (tekstvak)** *(alleen als: werkervaring_inschaling = ja-als-volgt)*  
    `werkervaring_als_volgt="tekst"`
  - **Zijn er periodieke verhogingen?**  
    `periodieke_verhogingen=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Ja, deze zijn afhankelijk van een minimale duur dienstverband** *(alleen als: periodieke_verhogingen = ja)*  
    `minimale_duur_dienstverband=PeriodiekeVerhoging(...)` met:
    - **(label van de rij)** *(alleen als: ../periodieke_verhogingen = ja)*  
      `aangevinkt=True`
    - **Wanneer wordt de periodieke of andere verhoging toegekend?** *(alleen als: aangevinkt is ingevuld)*  
      `wanneer=VerhogingWanneer.VAST_MOMENT`  
      Keuzes: `VerhogingWanneer.VAST_MOMENT` = Op een vast moment, namelijk: · `VerhogingWanneer.GEWERKT_JAAR` = Per gewerkt jaar · `VerhogingWanneer.ANDERS` = Anders, namelijk:
    - **Op een vast moment, namelijk: (datum)** *(alleen als: wanneer = vast-moment)*  
      `wanneer_vast_moment=dt.date(2026, 1, 1)`
    - **Anders, namelijk: (tekstvak)** *(alleen als: wanneer = anders)*  
      `wanneer_anders="tekst"`
    - **Hoe wordt de periodieke of andere verhoging berekend?** *(alleen als: aangevinkt is ingevuld)*  
      `berekening=VerhogingBerekening.VAST_PERCENTAGE`  
      Keuzes: `VerhogingBerekening.VAST_PERCENTAGE` = Vast percentage van het loon, namelijk: · `VerhogingBerekening.VAST_BEDRAG` = Vast bedrag, namelijk: · `VerhogingBerekening.TREDEN` = Overeenkomstig de treden in de salaristabellen, namelijk: · `VerhogingBerekening.ANDERS` = Anders, namelijk:
    - **Vast percentage van het loon, namelijk: (%)** *(alleen als: berekening = vast-percentage)*  
      `berekening_vast_percentage=8` (%)
    - **Vast bedrag, namelijk: (€)** *(alleen als: berekening = vast-bedrag)*  
      `berekening_vast_bedrag=1250` (€)
    - **Overeenkomstig de treden in de salaristabellen, namelijk: (trede(n) per jaar)** *(alleen als: berekening = treden)*  
      `berekening_treden=10` (jaar)
    - **Anders, namelijk: (tekstvak)** *(alleen als: berekening = anders)*  
      `berekening_anders="tekst"`
  - **Ja, deze zijn afhankelijk van de beoordeling van de werknemer** *(alleen als: periodieke_verhogingen = ja)*  
    `beoordeling_werknemer=PeriodiekeVerhoging(...)` met:
    - dezelfde vragen als bij `PeriodiekeVerhoging` hierboven
  - **Ja** *(alleen als: periodieke_verhogingen = ja)*  
    `periodiek_ja=PeriodiekeVerhoging(...)` met:
    - dezelfde vragen als bij `PeriodiekeVerhoging` hierboven
  - **Nee, maar wij geven wel andere verhogingen (niet zijnde initiële / eenmalige verhogingen) (...)** *(alleen als: periodieke_verhogingen = ja)*  
    `andere_verhogingen=PeriodiekeVerhoging(...)` met:
    - dezelfde vragen als bij `PeriodiekeVerhoging` hierboven
  - **Zijn er initiële / eenmalige verhogingen bekend?**  
    `initiele_eenmalige_verhogingen=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Type verhoging** *(alleen als: initiele_eenmalige_verhogingen = ja)*  
    `eenmalig_type=EenmaligeVerhogingType.EURO`  
    Keuzes: `EenmaligeVerhogingType.EURO` = Een vast bedrag · `EenmaligeVerhogingType.PERCENTAGE` = Een percentage
  - **Een vast bedrag (€)** *(alleen als: eenmalig_type = Euro)*  
    `eenmalig_euro=1250` (€)
  - **Een percentage (%)** *(alleen als: eenmalig_type = Percentage)*  
    `eenmalig_percentage=8` (%)
  - **Ingangsdatum** *(alleen als: initiele_eenmalige_verhogingen = ja)*  
    `eenmalig_geldig_vanaf=dt.date(2026, 1, 1)`
  - **Voorwaarden voor toekenning** *(alleen als: initiele_eenmalige_verhogingen = ja)*  
    `eenmalig_beschrijving="tekst"`
  - **Zijn er werknemers waarvoor een afwijkende arbeidsduur geldt, bijvoorbeeld omdat zij in een ploegendienst w…**  
    `afwijkende_arbeidsduur=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Namelijk de volgende arbeidsduur:** *(alleen als: afwijkende_arbeidsduur = ja)*  
    `afwijkende_roosters=[AfwijkendRooster(...), AfwijkendRooster(...)]`: herhaalbaar; per rij:
    - **Arbeidsduur (uur)** *(alleen als: ../afwijkende_arbeidsduur = ja)*  
      `arbeidsduur=40` (uur)
    - **Per** *(alleen als: ../afwijkende_arbeidsduur = ja)*  
      `arbeidsduur_per=BeloningInterval.PER_MAAND`  
      Keuzes: `BeloningInterval.PER_MAAND` = Per maand · `BeloningInterval.PER_VIER_WEKEN` = Per vier weken · `BeloningInterval.PER_WEEK` = Per week · `BeloningInterval.PER_UUR` = Per uur
    - **in de volgende situatie: (bijvoorbeeld bij werken in een vijf of drie ploegendienst)** *(alleen als: ../afwijkende_arbeidsduur = ja)*  
      `in_situatie="tekst"`
    - **Zijn in jouw arbeidsvoorwaardenregeling of cao uurlonen vastgelegd of kent jouw cao (...) een eenduidige be…** *(alleen als: ../afwijkende_arbeidsduur = ja)*  
      `uurloon_factor_vastgelegd=JaNee.JA`  
      Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
    - **Ja, namelijk: (%)** *(alleen als: (../afwijkende_arbeidsduur = ja) en (uurloon_factor_vastgelegd = ja))*  
      `uurloon_factor=8` (%)
- **Kent jouw onderneming doorbetaalde pauzes of rusttijden?**  
  `f.beloning.betaalde_rusttijden_en_pauzes = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Ja, namelijk: (tekstvak)** *(alleen als: betaalde_rusttijden_en_pauzes = ja)*  
  `f.beloning.betaalde_rusttijden_namelijk = "tekst"`

## 03 · Functiegroepen

In `maak_upload.py`: `f.functiegroepen` (zie `vul_functiegroepen`).

- **Voor welke functie(s) of functiegroep(en) wordt het formulier ingevuld?**  
  `f.functiegroepen.functie_groepen = [Functiegroep(...), Functiegroep(...)]`: herhaalbaar; per rij:
  - **Titel**  
    `titel="tekst"`
  - **Code**  
    `code="tekst"`
  - **Salarisschaal {num} (dynamische keuzelijst: waarde "b,s" = index salaristabel, index salarisschaal uit 02 B…**  
    `salarisschaal="tekst"`

## 04 · Toeslagen

In `maak_upload.py`: `f.toeslagen` (zie `vul_toeslagen`).

- **Onregelmatigheids- toeslagen (waaronder feestdagen)**  
  `f.toeslagen.onregelmatigheids_toeslagen_aan = True`
- **Ploegentoeslagen**  
  `f.toeslagen.ploegentoeslagen_aan = True`
- **Toeslagen voor verschoven diensten**  
  `f.toeslagen.toeslagen_verschoven_diensten_aan = True`
- **Toeslagen voor (fysieke) belasting**  
  `f.toeslagen.toeslagen_fysieke_belasting_aan = True`
- **Toeslagen voor werken tijdens stand-by-, consignatie- of bereik- baarheidsdiensten**  
  `f.toeslagen.toeslagen_stand_by_aan = True`
- **Overwerk**  
  `f.toeslagen.overwerktoeslag_aan = True`
- **Waarnemingstoeslag**  
  `f.toeslagen.waarnemingstoeslag_aan = True`
- **Performancetoeslag**  
  `f.toeslagen.performancetoeslag_aan = True`
- **Anders**  
  `f.toeslagen.anders_aan = True`
- **Geen toeslagen**  
  `f.toeslagen.geen_toeslagen = True`
- **Onregelmatigheids- toeslagen (waaronder feestdagen): variaties** *(alleen als: onregelmatigheids_toeslagen_aan is ingevuld)*  
  `f.toeslagen.onregelmatigheids_toeslagen = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - **Titel** *(alleen als: alleen bij anders)*  
    `naam="tekst"`
  - **Omschrijving van deze variatie** *(alleen als: meer dan 1 variatie)*  
    `omschrijving="tekst"`
  - **Hoe wordt de toeslag uitgekeerd?**  
    `bedrag=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, tijd.
  - **Onder welke voorwaarden geldt de toeslag? Of wanneer is er sprake van deze toeslag? (bij ploegentoeslagen: …**  
    `voorwaarden="tekst"`
  - **Is deze toeslag cumulatief?**  
    `cumulatief=Cumulatief.JA_CUMULATIEF`  
    Keuzes: `Cumulatief.JA_CUMULATIEF` = Ja, toeslagen worden opgeteld · `Cumulatief.JA_COMPOUNDING` = Ja, deze toeslag wordt berekend over het resultaat na andere toeslagen, namelijk: · `Cumulatief.NEE` = Nee
  - **Toelichting** *(alleen als: cumulatief = ja-cumulative)*  
    `cumulatief_toelichting="tekst"`
  - **Eén checkbox per andere aangevinkte toeslag (label = label van die toeslag)** *(alleen als: cumulatief = ja-compounding)*  
    `compounding={sleutel: True}` (per ToeslagSoort)
  - **Wanneer is de toeslag geldig? (Toepassingsperiodes)** *(alleen als: alleen bij onregelmatigheids-toeslagen, toeslagen-verschoven-diensten, toeslagen-stand-by-consignatie-bereikbaarheidsdiensten, overwerktoeslag en anders)*  
    `toepassingsperiodes_type=ToepassingsperiodesType.ALTIJD`  
    Keuzes: `ToepassingsperiodesType.ALTIJD` = Altijd · `ToepassingsperiodesType.BEPAALD` = Bepaalde data/tijden/dagen
  - **Toepassingsperiode {num}** *(alleen als: toepassingsperiodes_type = bepaald)*  
    `toepassingsperiodes=[Toepassingsperiode(...), Toepassingsperiode(...)]`: herhaalbaar; per rij:
    - **Startdatum** *(alleen als: ../toepassingsperiodes_type = bepaald en alleen bij anders)*  
      `startdatum=dt.date(2026, 1, 1)`
    - **Einddatum** *(alleen als: ../toepassingsperiodes_type = bepaald en alleen bij anders)*  
      `einddatum=dt.date(2026, 1, 1)`
    - **Starttijd** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `starttijd=dt.time(22, 0)`
    - **Eindtijd** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `eindtijd=dt.time(22, 0)`
    - **Maandag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `maandag=True`
    - **Dinsdag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `dinsdag=True`
    - **Woensdag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `woensdag=True`
    - **Donderdag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `donderdag=True`
    - **Vrijdag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `vrijdag=True`
    - **Zaterdag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `zaterdag=True`
    - **Zondag** *(alleen als: ../toepassingsperiodes_type = bepaald)*  
      `zondag=True`
  - **Geldt er een afbouwregeling voor deze toeslag?** *(alleen als: alleen bij ploegentoeslagen, waarnemingstoeslag, performancetoeslag en anders)*  
    `afbouwregeling=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Ja, namelijk (geen vraagtekst)** *(alleen als: afbouwregeling = ja)*  
    `afbouwregeling_namelijk="tekst"`
- **Ploegentoeslagen: variaties** *(alleen als: ploegentoeslagen_aan is ingevuld)*  
  `f.toeslagen.ploegentoeslagen = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Toeslagen voor verschoven diensten: variaties** *(alleen als: toeslagen_verschoven_diensten_aan is ingevuld)*  
  `f.toeslagen.toeslagen_verschoven_diensten = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Toeslagen voor (fysieke) belasting: variaties** *(alleen als: toeslagen_fysieke_belasting_aan is ingevuld)*  
  `f.toeslagen.toeslagen_fysieke_belasting = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Toeslagen voor werken tijdens stand-by-, consignatie- of bereikbaarheidsdiensten: variaties** *(alleen als: toeslagen_stand_by_aan is ingevuld)*  
  `f.toeslagen.toeslagen_stand_by = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Overwerk: variaties** *(alleen als: overwerktoeslag_aan is ingevuld)*  
  `f.toeslagen.overwerktoeslag = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Waarnemingstoeslag: variaties** *(alleen als: waarnemingstoeslag_aan is ingevuld)*  
  `f.toeslagen.waarnemingstoeslag = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Performancetoeslag: variaties** *(alleen als: performancetoeslag_aan is ingevuld)*  
  `f.toeslagen.performancetoeslag = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven
- **Anders: variaties** *(alleen als: anders_aan is ingevuld)*  
  `f.toeslagen.anders = [ToeslagVariatie(...), ToeslagVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `ToeslagVariatie` hierboven

## 05 · Vakantiebijslag

In `maak_upload.py`: `f.vakantiebijslag` (zie `vul_vakantiebijslag`).

- **Is er een vakantiebijslag?**  
  `f.vakantiebijslag.ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Hoeveel bedraagt de vakantiebijslag?** *(alleen als: ja_nee = ja)*  
  `f.vakantiebijslag.bedrag = Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: percentage.

## 06 · Vergoedingen

In `maak_upload.py`: `f.vergoedingen` (zie `vul_vergoedingen`).

- **Reiskostenvergoeding woon- werk verkeer eigen auto / fiets etc.**  
  `f.vergoedingen.reiskosten.kent_eigen_vervoer = True`
- **Reiskostenvergoeding woon- werk verkeer OV**  
  `f.vergoedingen.reiskosten.kent_ov = True`
- **Reiskostenvergoeding zakelijke kilometers (werk – werk)**  
  `f.vergoedingen.reiskosten.kent_zakelijke_kilometers = True`
- **Reiskostenvergoeding zakelijke kilometers OV (werk – werk)**  
  `f.vergoedingen.reiskosten.kent_zakelijke_kilometers_ov = True`
- **Andere reiskostenvergoeding**  
  `f.vergoedingen.reiskosten.kent_andere = True`
- **Reiskostenvergoeding woon- werk verkeer eigen auto / fiets / bromfiets / anders.** *(alleen als: kent_eigen_vervoer is ingevuld)*  
  `f.vergoedingen.reiskosten.eigen_vervoer = [EigenVervoerVariatie(...), EigenVervoerVariatie(...)]`: herhaalbaar; per rij:
  - **(bloktitel is de vraag)**  
    `type=EigenVervoerType.STANDAARD_TARIEF`  
    Keuzes: `EigenVervoerType.STANDAARD_TARIEF` = € 0,23 per kilometer · `EigenVervoerType.ANDER_TARIEF_PER_KM` = Andere vergoeding per kilometer · `EigenVervoerType.PER_TIJDVAK` = Vergoeding per tijdvak · `EigenVervoerType.ANDERS` = Anders, namelijk:
  - **namelijk … per kilometer (€)** *(alleen als: type = ander-tarief-per-km)*  
    `ander_tarief_per_km_bedrag=1250` (€)
  - **namelijk (€)** *(alleen als: type = per-tijdvak)*  
    `per_tijdvak_bedrag=1250` (€)
  - **per** *(alleen als: type = per-tijdvak)*  
    `per_tijdvak_type=Tijdvak.UUR`  
    Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.DAGDEEL` = Dagdeel · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
  - **Anders, namelijk:** *(alleen als: type = anders)*  
    `anders_namelijk="tekst"`
  - **Voor deze vergoeding gelden de volgende voorwaarden:**  
    `voorwaarden="tekst"`
- **Reiskostenvergoeding woon- werk verkeer OV** *(alleen als: kent_ov is ingevuld)*  
  `f.vergoedingen.reiskosten.ov = OvVergoeding(...)` met:
  - **(bloktitel is de vraag)**  
    `type=OvType.VOLLEDIGE_VERGOEDING`  
    Keuzes: `OvType.VOLLEDIGE_VERGOEDING` = Volledige vergoeding van de gemaakte kosten · `OvType.PER_KILOMETER` = Vergoeding per kilometer, namelijk: · `OvType.PER_RIT` = Vergoeding per rit, namelijk: · `OvType.PER_TRAJECT` = Vergoeding per traject, namelijk: · `OvType.ANDERS` = Anders, namelijk:
  - **Bedrag per kilometer (€)** *(alleen als: type = per-kilometer)*  
    `per_kilometer_bedrag=1250` (€)
  - **Bedrag per rit (€)** *(alleen als: type = per-rit)*  
    `per_rit_bedrag=1250` (€)
  - **Bedrag per traject (€)** *(alleen als: type = per-traject)*  
    `per_traject_bedrag=1250` (€)
  - **Anders, namelijk:** *(alleen als: type = anders)*  
    `anders_namelijk="tekst"`
  - **Voor deze vergoeding gelden de volgende voorwaarden:**  
    `voorwaarden="tekst"`
- **Reiskostenvergoeding zakelijke kilometers (werk – werk) eigen vervoer** *(alleen als: kent_zakelijke_kilometers is ingevuld)*  
  `f.vergoedingen.reiskosten.zakelijke_kilometers = [EigenVervoerVariatie(...), EigenVervoerVariatie(...)]`: herhaalbaar; per rij:
  - dezelfde vragen als bij `EigenVervoerVariatie` hierboven
- **Reiskostenvergoeding werk-werk verkeer OV** *(alleen als: kent_zakelijke_kilometers_ov is ingevuld)*  
  `f.vergoedingen.reiskosten.zakelijke_kilometers_ov = OvVergoeding(...)` met:
  - dezelfde vragen als bij `OvVergoeding` hierboven
- **Andere reiskostenvergoedingen, namelijk:** *(alleen als: kent_andere is ingevuld)*  
  `f.vergoedingen.reiskosten.andere_namelijk = "tekst"`
- **Ken je een vergoeding voor reisuren of reistijd?**  
  `f.vergoedingen.reisuren.vergoeding = ReistijdVergoeding.PERCENTAGE`  
  Keuzes: `ReistijdVergoeding.PERCENTAGE` = Ja, namelijk percentage van · `ReistijdVergoeding.VASTE_VERGOEDING` = Ja, namelijk een vaste vergoeding van · `ReistijdVergoeding.ANDERS` = Ja, namelijk: · `ReistijdVergoeding.NEE` = Nee
- **Percentage (%)** *(alleen als: vergoeding = percentage)*  
  `f.vergoedingen.reisuren.percentage = 8` (%)
- **van** *(alleen als: vergoeding = percentage)*  
  `f.vergoedingen.reisuren.percentage_van = Loonbasis.UURLOON`  
  Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
- **per** *(alleen als: vergoeding = percentage)*  
  `f.vergoedingen.reisuren.percentage_tijdvak = Tijdvak.UUR`  
  Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.DAGDEEL` = Dagdeel · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **Bedrag (€)** *(alleen als: vergoeding = vaste-vergoeding)*  
  `f.vergoedingen.reisuren.vaste_vergoeding_bedrag = 1250` (€)
- **per** *(alleen als: vergoeding = vaste-vergoeding)*  
  `f.vergoedingen.reisuren.vaste_vergoeding_per = TijdvakReisuren.KILOMETER`  
  Keuzes: `TijdvakReisuren.KILOMETER` = Kilometer · `TijdvakReisuren.ROUTE` = Route · `TijdvakReisuren.UUR` = Uur · `TijdvakReisuren.DAG` = Dag · `TijdvakReisuren.DAGDEEL` = Dagdeel · `TijdvakReisuren.MAAND` = Maand · `TijdvakReisuren.WEEK` = Week · `TijdvakReisuren.JAAR` = Jaar
- **Ja, namelijk:** *(alleen als: vergoeding = anders)*  
  `f.vergoedingen.reisuren.anders_namelijk = "tekst"`
- **Voor deze vergoeding gelden de volgende voorwaarden:** *(alleen als: niet (vergoeding = nee))*  
  `f.vergoedingen.reisuren.voorwaarden = "tekst"`
- **Kent je een vergoeding voor de tijd die de werknemer stand-by of bereikbaar moet zijn?**  
  `f.vergoedingen.stand_by.ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Welke vergoeding kent jouw onderneming voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten?** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.stand_by.type = StandByType.VERGOEDING_PER_TIJDVAK`  
  Keuzes: `StandByType.VERGOEDING_PER_TIJDVAK` = Vaste vergoeding per tijdvak, namelijk: · `StandByType.PERCENTAGE_PER_TIJDVAK` = Percentage per tijdvak, namelijk: · `StandByType.ANDERS` = Anders, namelijk:
- **Bedrag (€)** *(alleen als: type = vergoeding-per-tijdvak)*  
  `f.vergoedingen.stand_by.vast_bedrag = 1250` (€)
- **per** *(alleen als: type = vergoeding-per-tijdvak)*  
  `f.vergoedingen.stand_by.vast_tijdvak = TijdvakStandBy.UUR`  
  Keuzes: `TijdvakStandBy.UUR` = Uur · `TijdvakStandBy.DAG` = Dag · `TijdvakStandBy.DAGDEEL` = Dagdeel · `TijdvakStandBy.WEEK` = Week · `TijdvakStandBy.MAAND` = Maand · `TijdvakStandBy.JAAR` = Jaar · `TijdvakStandBy.DIENST` = Dienst
- **Percentage (%)** *(alleen als: type = percentage-per-tijdvak)*  
  `f.vergoedingen.stand_by.percentage = 8` (%)
- **van:** *(alleen als: type = percentage-per-tijdvak)*  
  `f.vergoedingen.stand_by.percentage_van = Loonbasis.UURLOON`  
  Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
- **per** *(alleen als: type = percentage-per-tijdvak)*  
  `f.vergoedingen.stand_by.percentage_tijdvak = TijdvakStandBy.UUR`  
  Keuzes: `TijdvakStandBy.UUR` = Uur · `TijdvakStandBy.DAG` = Dag · `TijdvakStandBy.DAGDEEL` = Dagdeel · `TijdvakStandBy.WEEK` = Week · `TijdvakStandBy.MAAND` = Maand · `TijdvakStandBy.JAAR` = Jaar · `TijdvakStandBy.DIENST` = Dienst
- **Anders, namelijk:** *(alleen als: type = anders)*  
  `f.vergoedingen.stand_by.anders_namelijk = "tekst"`
- **Voor deze vergoeding gelden de volgende voorwaarden:** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.stand_by.voorwaarden = "tekst"`
- **Ken je een vergoeding voor de (aanvullende) zorgverzekering?**  
  `f.vergoedingen.zorgverzekering.ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Hoe ziet deze vergoeding eruit?** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.zorgverzekering.type = ZorgverzekeringType.VERGOEDING_PER_TIJDSEENHEID`  
  Keuzes: `ZorgverzekeringType.VERGOEDING_PER_TIJDSEENHEID` = Vergoeding per tijdseenheid, namelijk: · `ZorgverzekeringType.ANDERS` = Anders, namelijk:
- **Bedrag (€)** *(alleen als: type = vergoeding-per-tijdseenheid)*  
  `f.vergoedingen.zorgverzekering.bedrag = 1250` (€)
- **per** *(alleen als: type = vergoeding-per-tijdseenheid)*  
  `f.vergoedingen.zorgverzekering.tijdvak = Tijdvak.UUR`  
  Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.DAGDEEL` = Dagdeel · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **Anders, namelijk:** *(alleen als: type = anders)*  
  `f.vergoedingen.zorgverzekering.anders_namelijk = "tekst"`
- **Geldt er een minimum- of een maximumbedrag voor de vergoeding?** *(alleen als: type = vergoeding-per-tijdseenheid)*  
  `f.vergoedingen.zorgverzekering.min_max = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Minimum (€)** *(alleen als: min_max = ja)*  
  `f.vergoedingen.zorgverzekering.minimum = 1250` (€)
- **Maximum (€)** *(alleen als: min_max = ja)*  
  `f.vergoedingen.zorgverzekering.maximum = 1250` (€)
- **Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?** *(alleen als: type = vergoeding-per-tijdseenheid)*  
  `f.vergoedingen.zorgverzekering.naar_rato = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Voor deze vergoeding gelden verder de volgende voorwaarden:** *(alleen als: type = vergoeding-per-tijdseenheid)*  
  `f.vergoedingen.zorgverzekering.voorwaarden = "tekst"`
- **Ken je een thuiswerkvergoeding?**  
  `f.vergoedingen.thuiswerk.ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Bedrag (€)** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.thuiswerk.bedrag = 1250` (€)
- **per** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.thuiswerk.tijdvak = Tijdvak.UUR`  
  Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.DAGDEEL` = Dagdeel · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **Voor deze vergoeding gelden de volgende voorwaarden:** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.thuiswerk.voorwaarden = "tekst"`
- **Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.thuiswerk.naar_rato = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Zit er een internetvergoeding besloten in de thuiswerkvergoeding?** *(alleen als: ja_nee = ja)*  
  `f.vergoedingen.thuiswerk.internet_inbegrepen = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Wordt er naast de thuiswerkvergoeding ook (aanvullend) een internetvergoeding verstrekt?** *(alleen als: internet_inbegrepen = nee)*  
  `f.vergoedingen.thuiswerk.extra_internet = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Bedrag (€)** *(alleen als: extra_internet = ja)*  
  `f.vergoedingen.thuiswerk.internet_bedrag = 1250` (€)
- **tijdvak** *(alleen als: extra_internet = ja)*  
  `f.vergoedingen.thuiswerk.internet_tijdvak = Tijdvak.UUR`  
  Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.DAGDEEL` = Dagdeel · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **Voor deze vergoeding gelden verder de volgende voorwaarden:** *(alleen als: extra_internet = ja)*  
  `f.vergoedingen.thuiswerk.internet_voorwaarden = "tekst"`
- **Wordt de internetvergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur (...)** *(alleen als: extra_internet = ja)*  
  `f.vergoedingen.thuiswerk.internet_naar_rato = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Mobiliteitsvergoeding**  
  `f.vergoedingen.mobiliteit.mobiliteitsvergoeding = MobiliteitsRegeling(...)` met:
  - **<label> (aangevinkt = regeling van toepassing)**  
    `aangevinkt=True`
  - **Wat is de hoogte van de vergoeding / het leasebedrag? (€)** *(alleen als: aangevinkt is ingevuld)*  
    `bedrag=1250` (€)
  - **Per tijdvak** *(alleen als: aangevinkt is ingevuld)*  
    `tijdvak=Interval.UUR`  
    Keuzes: `Interval.UUR` = Uur · `Interval.DAG` = Dag · `Interval.WEEK` = Week · `Interval.MAAND` = Maand · `Interval.KWARTAAL` = Kwartaal · `Interval.JAAR` = Jaar · `Interval.DAGDEEL` = Dagdeel · `Interval.DIENST` = Dienst · `Interval.EENMALIG` = Eenmalig · `Interval.GEWERKTE_DAG` = Gewerkte dag · `Interval.ITEM` = Item · `Interval.KILOMETER` = Kilometer · `Interval.NACHT` = Nacht · `Interval.OP_DECLARATIEBASIS` = Op declaratie basis · `Interval.RIT` = Rit · `Interval.ROUTE` = Route · `Interval.THUISWERKDAG` = Thuiswerkdag · `Interval.VERHUIZING` = Verhuizing · `Interval.WEKELIJKSE_REISDAG` = Wekelijkse reisdag
  - **Voor deze regeling gelden de volgende voorwaarden:** *(alleen als: aangevinkt is ingevuld)*  
    `voorwaarden="tekst"`
  - **Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?** *(alleen als: aangevinkt is ingevuld)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Regeling leaseauto**  
  `f.vergoedingen.mobiliteit.regeling_leaseauto = MobiliteitsRegelingMetAlternatief(...)` met:
  - **<label> (aangevinkt = regeling van toepassing)**  
    `aangevinkt=True`
  - **Wat is de hoogte van de vergoeding / het leasebedrag? (€)** *(alleen als: aangevinkt is ingevuld)*  
    `bedrag=1250` (€)
  - **Per tijdvak** *(alleen als: aangevinkt is ingevuld)*  
    `tijdvak=Interval.UUR`  
    Keuzes: `Interval.UUR` = Uur · `Interval.DAG` = Dag · `Interval.WEEK` = Week · `Interval.MAAND` = Maand · `Interval.KWARTAAL` = Kwartaal · `Interval.JAAR` = Jaar · `Interval.DAGDEEL` = Dagdeel · `Interval.DIENST` = Dienst · `Interval.EENMALIG` = Eenmalig · `Interval.GEWERKTE_DAG` = Gewerkte dag · `Interval.ITEM` = Item · `Interval.KILOMETER` = Kilometer · `Interval.NACHT` = Nacht · `Interval.OP_DECLARATIEBASIS` = Op declaratie basis · `Interval.RIT` = Rit · `Interval.ROUTE` = Route · `Interval.THUISWERKDAG` = Thuiswerkdag · `Interval.VERHUIZING` = Verhuizing · `Interval.WEKELIJKSE_REISDAG` = Wekelijkse reisdag
  - **Voor deze regeling gelden de volgende voorwaarden:** *(alleen als: aangevinkt is ingevuld)*  
    `voorwaarden="tekst"`
  - **Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?** *(alleen als: aangevinkt is ingevuld)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Er is een alternatieve vergoeding voor <label>** *(alleen als: aangevinkt is ingevuld)*  
    `alternatief=True`
  - **Bedrag (€)** *(alleen als: alternatief is ingevuld)*  
    `alternatief_bedrag=1250` (€)
  - **per tijdvak van** *(alleen als: alternatief is ingevuld)*  
    `alternatief_tijdvak=Interval.UUR`  
    Keuzes: `Interval.UUR` = Uur · `Interval.DAG` = Dag · `Interval.WEEK` = Week · `Interval.MAAND` = Maand · `Interval.KWARTAAL` = Kwartaal · `Interval.JAAR` = Jaar · `Interval.DAGDEEL` = Dagdeel · `Interval.DIENST` = Dienst · `Interval.EENMALIG` = Eenmalig · `Interval.GEWERKTE_DAG` = Gewerkte dag · `Interval.ITEM` = Item · `Interval.KILOMETER` = Kilometer · `Interval.NACHT` = Nacht · `Interval.OP_DECLARATIEBASIS` = Op declaratie basis · `Interval.RIT` = Rit · `Interval.ROUTE` = Route · `Interval.THUISWERKDAG` = Thuiswerkdag · `Interval.VERHUIZING` = Verhuizing · `Interval.WEKELIJKSE_REISDAG` = Wekelijkse reisdag
  - **Voor deze vergoeding gelden de volgende voorwaarden:** *(alleen als: alternatief is ingevuld)*  
    `alternatief_voorwaarden="tekst"`
  - **Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?** *(alleen als: alternatief is ingevuld)*  
    `alternatief_naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Regeling leasefiets**  
  `f.vergoedingen.mobiliteit.regeling_leasefiets = MobiliteitsRegelingMetAlternatief(...)` met:
  - dezelfde vragen als bij `MobiliteitsRegelingMetAlternatief` hierboven
- **Regeling OV vergoeding**  
  `f.vergoedingen.mobiliteit.regeling_ov_vergoeding = MobiliteitsRegelingMetAlternatief(...)` met:
  - dezelfde vragen als bij `MobiliteitsRegelingMetAlternatief` hierboven
- **Fietsregeling**  
  `f.vergoedingen.mobiliteit.fietsregeling = MobiliteitsRegeling(...)` met:
  - dezelfde vragen als bij `MobiliteitsRegeling` hierboven
- **Koffiegeld**  
  `f.vergoedingen.kosten.koffiegeld = KostenVergoeding(...)` met:
  - **<label> (aangevinkt = vergoeding van toepassing)**  
    `aangevinkt=True`
  - **Bedrag (€)** *(alleen als: aangevinkt is ingevuld)*  
    `bedrag=1250` (€)
  - **per** *(alleen als: aangevinkt is ingevuld)*  
    `tijdvak=TijdvakKosten.ITEM`  
    Keuzes: `TijdvakKosten.ITEM` = Item · `TijdvakKosten.UUR` = Uur · `TijdvakKosten.DAG` = Dag · `TijdvakKosten.DAGDEEL` = Dagdeel · `TijdvakKosten.WEEK` = Week · `TijdvakKosten.MAAND` = Maand · `TijdvakKosten.JAAR` = Jaar
  - **Voor deze vergoeding gelden de volgende voorwaarden:** *(alleen als: aangevinkt is ingevuld)*  
    `voorwaarden="tekst"`
  - **Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?** *(alleen als: aangevinkt is ingevuld)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Maaltijdvergoeding**  
  `f.vergoedingen.kosten.maaltijdvergoeding = KostenVergoeding(...)` met:
  - dezelfde vragen als bij `KostenVergoeding` hierboven
- **Wasvergoeding**  
  `f.vergoedingen.kosten.wasvergoeding = KostenVergoeding(...)` met:
  - dezelfde vragen als bij `KostenVergoeding` hierboven
- **Vergoeding voor bedrijfskleding of schoenen**  
  `f.vergoedingen.kosten.bedrijfskleding_schoenen = KostenVergoeding(...)` met:
  - dezelfde vragen als bij `KostenVergoeding` hierboven
- **Arbo-vergoeding**  
  `f.vergoedingen.kosten.arbo_vergoeding = KostenVergoeding(...)` met:
  - dezelfde vragen als bij `KostenVergoeding` hierboven
- **BYOD (Bring Your Own Device) vergoeding**  
  `f.vergoedingen.kosten.byod_vergoeding = KostenVergoeding(...)` met:
  - dezelfde vragen als bij `KostenVergoeding` hierboven
- **Anders, namelijk:**  
  `f.vergoedingen.kosten.anders = True`
- **(namelijk)** *(alleen als: anders is ingevuld)*  
  `f.vergoedingen.kosten.anders_namelijk = "tekst"`
- **Geen (wist de zes vergoedingen hierboven)**  
  `f.vergoedingen.kosten.geen = True`

## 07 · Bijzondere uitkeringen

In `maak_upload.py`: `f.bijzondere_uitkeringen` (zie `vul_bijzondere_uitkeringen`).

- **Zijn er eenmalige uitkeringen bekend?**  
  `f.bijzondere_uitkeringen.eenmalige_uitkeringen_bekend = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Variaties eenmalige uitkering** *(alleen als: eenmalige_uitkeringen_bekend = ja)*  
  `f.bijzondere_uitkeringen.eenmalige_uitkeringen = [EenmaligeUitkering(...), EenmaligeUitkering(...)]`: herhaalbaar; per rij:
  - **Naam (bij >1 variatie: "Naam (variatie {num})")**  
    `naam="tekst"`
  - **Afhankelijk minimale duur dienstverband, namelijk:**  
    `min_duur_dienstverband=True`
  - **Afhankelijk van dienstverband op bepaalde datum, namelijk:**  
    `dienstverband_op_datum=True`
  - **Anders, namelijk:**  
    `voorwaarde_anders=True`
  - **(geen vraagtekst)** *(alleen als: min_duur_dienstverband is ingevuld)*  
    `min_duur_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: dienstverband_op_datum is ingevuld)*  
    `dienstverband_datum_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: voorwaarde_anders is ingevuld)*  
    `voorwaarde_anders_namelijk="tekst"`
  - **Op welk moment wordt de uitkering uitgekeerd?**  
    `toekenning_datum=dt.date(2026, 1, 1)`
  - **Hoe wordt de uitkering toegekend?**  
    `hoe_toegekend=HoeToegekend.PERCENTAGE_LOON`  
    Keuzes: `HoeToegekend.PERCENTAGE_LOON` = Vast percentage van het loon · `HoeToegekend.VAST_BEDRAG` = Vast bedrag, namelijk: · `HoeToegekend.ANDERS` = Anders, namelijk:
  - **Percentage (%) (geen vraagtekst)** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage=8` (%)
  - **van** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage_van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
  - **Bedrag (€) (geen vraagtekst)** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `vast_bedrag=1250` (€)
  - **(geen vraagtekst)** *(alleen als: hoe_toegekend = anders)*  
    `anders="tekst"`
  - **Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband?** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `naar_rato_deeltijd=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Wordt dit bedrag toegepast naar rato van de duur van het dienstverband?** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `naar_rato_duur_dienstverband=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Geldt er een minimum- of een maximumbedrag?** *(alleen als: eenmalige-uitkering-hoe-toegekend ≠ anders (slug bestaat niet: in de praktijk altijd zichtbaar))*  
    `min_max=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Minimum (€)** *(alleen als: min_max = ja)*  
    `minimum=1250` (€)
  - **Maximum (€)** *(alleen als: min_max = ja)*  
    `maximum=1250` (€)
- **Is er een vaste (onvoorwaardelijke) uitkering van toepassing?**  
  `f.bijzondere_uitkeringen.vaste_uitkering_van_toepassing = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Variaties vaste uitkering** *(alleen als: vaste_uitkering_van_toepassing = ja)*  
  `f.bijzondere_uitkeringen.vaste_uitkeringen = [VasteUitkering(...), VasteUitkering(...)]`: herhaalbaar; per rij:
  - **Naam (bij >1 variatie: "Naam (variatie {num})")**  
    `naam="tekst"`
  - **Afhankelijk minimale duur dienstverband, namelijk:**  
    `min_duur_dienstverband=True`
  - **Afhankelijk van dienstverband op bepaalde datum, namelijk:**  
    `dienstverband_op_datum=True`
  - **Anders, namelijk:**  
    `voorwaarde_anders=True`
  - **(geen vraagtekst)** *(alleen als: min_duur_dienstverband is ingevuld)*  
    `min_duur_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: dienstverband_op_datum is ingevuld)*  
    `dienstverband_datum_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: voorwaarde_anders is ingevuld)*  
    `voorwaarde_anders_namelijk="tekst"`
  - **Op welk moment wordt de uitkering uitgekeerd?**  
    `toekenning_datum=dt.date(2026, 1, 1)`
  - **Hoe wordt de uitkering toegekend?**  
    `hoe_toegekend=HoeToegekendVast.DERTIENDE_MAAND`  
    Keuzes: `HoeToegekendVast.DERTIENDE_MAAND` = Als dertiende maand · `HoeToegekendVast.PERCENTAGE_LOON` = Vast percentage van het loon · `HoeToegekendVast.VAST_BEDRAG` = Vast bedrag, namelijk: · `HoeToegekendVast.ANDERS` = Anders, namelijk:
  - **namelijk (%)** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage=8` (%)
  - **van** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage_van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
  - **Bedrag (€) (geen vraagtekst)** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `vast_bedrag=1250` (€)
  - **(geen vraagtekst)** *(alleen als: hoe_toegekend = anders)*  
    `anders="tekst"`
  - **Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur v…** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Is er een jubileumuitkering of een vergelijkbare uitkering van toepassing?**  
  `f.bijzondere_uitkeringen.jubileumuitkering_van_toepassing = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Variaties jubileumuitkering** *(alleen als: jubileumuitkering_van_toepassing = ja)*  
  `f.bijzondere_uitkeringen.jubileumuitkeringen = [Jubileumuitkering(...), Jubileumuitkering(...)]`: herhaalbaar; per rij:
  - **Naam (bij >1 variatie: "Naam (variatie {num})")**  
    `naam="tekst"`
  - **Hoe wordt de uitkering toegekend?**  
    `hoe_toegekend=HoeToegekend.PERCENTAGE_LOON`  
    Keuzes: `HoeToegekend.PERCENTAGE_LOON` = Vast percentage van het loon · `HoeToegekend.VAST_BEDRAG` = Vast bedrag, namelijk: · `HoeToegekend.ANDERS` = Anders, namelijk:
  - **namelijk (%)** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage=8` (%)
  - **van** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage_van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
  - **Bedrag (€) (geen vraagtekst)** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `vast_bedrag=1250` (€)
  - **Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur v…** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **(geen vraagtekst)** *(alleen als: hoe_toegekend = anders)*  
    `anders="tekst"`
  - **Aantal jaren**  
    `dienstverband_jaren=10`
  - **Aantal maanden**  
    `dienstverband_maanden=10`
  - **Referentiedatum**  
    `referentiedatum=Peildatum.ANCIENNITEITSDATUM`  
    Keuzes: `Peildatum.ANCIENNITEITSDATUM` = Anciënniteitsdatum · `Peildatum.DATUM_INDIENSTTREDING` = Datum indiensttreding · `Peildatum.STARTDATUM_CONTRACT` = Startdatum contract · `Peildatum.STARTDATUM_PLAATSING` = Startdatum plaatsing
  - **Op welk moment wordt de uitkering uitgekeerd?**  
    `toekenning_datum=dt.date(2026, 1, 1)`
  - **Welke voorwaarden zijn van toepassing?**  
    `voorwaarden="tekst"`
- **Is er een variabele (voorwaardelijke) uitkering van toepassing?**  
  `f.bijzondere_uitkeringen.variabele_uitkering_van_toepassing = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Variaties variabele uitkering** *(alleen als: variabele_uitkering_van_toepassing = ja)*  
  `f.bijzondere_uitkeringen.variabele_uitkeringen = [VariabeleUitkering(...), VariabeleUitkering(...)]`: herhaalbaar; per rij:
  - **Wat voor soort uitkering gaat het om?**  
    `soort=SoortVariabeleUitkering.PERFORMANCE`  
    Keuzes: `SoortVariabeleUitkering.PERFORMANCE` = Performance uitkering · `SoortVariabeleUitkering.BONUS` = Bonusuitkering · `SoortVariabeleUitkering.WINST` = Winstuitkering · `SoortVariabeleUitkering.ANDERS` = Anders, namelijk:
  - **(geen vraagtekst)** *(alleen als: soort = anders)*  
    `soort_anders_namelijk="tekst"`
  - **Bepaalde prestatie (performance), namelijk:**  
    `prestatie=True`
  - **Bepaald resultaat (winst), namelijk:**  
    `resultaat=True`
  - **Afhankelijk minimale duur dienstverband, namelijk:**  
    `min_duur_dienstverband=True`
  - **Afhankelijk van dienstverband op bepaalde datum, namelijk:**  
    `dienstverband_op_datum=True`
  - **Anders, namelijk:**  
    `voorwaarde_anders=True`
  - **(geen vraagtekst)** *(alleen als: prestatie is ingevuld)*  
    `prestatie_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: resultaat is ingevuld)*  
    `resultaat_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: min_duur_dienstverband is ingevuld)*  
    `min_duur_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: dienstverband_op_datum is ingevuld)*  
    `dienstverband_datum_namelijk="tekst"`
  - **(geen vraagtekst)** *(alleen als: voorwaarde_anders is ingevuld)*  
    `voorwaarde_anders_namelijk="tekst"`
  - **Op welk moment wordt de uitkering uitgekeerd?**  
    `toekenning_datum=dt.date(2026, 1, 1)`
  - **Hoe wordt de uitkering toegekend?**  
    `hoe_toegekend=HoeToegekend.PERCENTAGE_LOON`  
    Keuzes: `HoeToegekend.PERCENTAGE_LOON` = Vast percentage van het loon · `HoeToegekend.VAST_BEDRAG` = Vast bedrag, namelijk: · `HoeToegekend.ANDERS` = Anders, namelijk:
  - **namelijk (%)** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage=8` (%)
  - **van** *(alleen als: hoe_toegekend = percentage-loon)*  
    `percentage_van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
  - **Bedrag (€) (geen vraagtekst)** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `vast_bedrag=1250` (€)
  - **(geen vraagtekst)** *(alleen als: hoe_toegekend = anders)*  
    `anders="tekst"`
  - **Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur v…** *(alleen als: hoe_toegekend = vast-bedrag)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Geldt er een minimum- of een maximumbedrag?**  
    `min_max=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **minimum (€)** *(alleen als: min_max = ja)*  
    `minimum=1250` (€)
  - **maximum (€)** *(alleen als: min_max = ja)*  
    `maximum=1250` (€)

## 08 · Loondoorbetaling bij ziekte

In `maak_upload.py`: `f.loondoorbetaling_bij_ziekte` (zie `vul_loondoorbetaling_bij_ziekte`).

- **Hoe hoog is het percentage dat bij ziekte wordt doorbetaald? (variaties)**  
  `f.loondoorbetaling_bij_ziekte.regels = [LoondoorbetalingRegel(...), LoondoorbetalingRegel(...)]`: herhaalbaar; per rij:
  - **Percentage (%)**  
    `percentage=8` (%)
  - **Van:**  
    `van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
  - **Grondslag:**  
    `grondslag=Grondslag.BASISLOON`  
    Keuzes: `Grondslag.BASISLOON` = Basisloon grondslag · `Grondslag.BRUTO_LOON` = Bruto loon grondslag · `Grondslag.SV_LOON` = SVLoon grondslag · `Grondslag.VAKANTIEBIJSLAG` = Vakantiebijslag grondslag · `Grondslag.PENSIOEN` = Pensioen grondslag · `Grondslag.DERTIENDE_MAAND` = 13e maand grondslag · `Grondslag.GEBRUIKELIJK_LOON` = Gebruikelijk loon grondslag
  - **Per**  
    `per_tijdvak=TijdvakZiekte.UUR`  
    Keuzes: `TijdvakZiekte.UUR` = Uur · `TijdvakZiekte.DAG` = Dag · `TijdvakZiekte.WEEK` = Week · `TijdvakZiekte.MAAND` = Maand · `TijdvakZiekte.JAAR` = Jaar
  - **Voorwaarden (bijvoorbeeld: tijdens de eerste 3 dagen van de ziekte)**  
    `voorwaarden="tekst"`
- **Zijn er wachtdagen?**  
  `f.loondoorbetaling_bij_ziekte.wachtdagen = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Ja, namelijk: … dagen** *(alleen als: wachtdagen = ja)*  
  `f.loondoorbetaling_bij_ziekte.wachtdagen_aantal = 10` (dagen)
- **Zitten er voorwaarden aan het toekennen van de wachtdagen?** *(alleen als: wachtdagen = ja)*  
  `f.loondoorbetaling_bij_ziekte.wachtdagen_voorwaarden = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Ja, namelijk:** *(alleen als: wachtdagen_voorwaarden = ja)*  
  `f.loondoorbetaling_bij_ziekte.wachtdagen_voorwaarden_namelijk = "tekst"`
- **Geldt er een wachtdagcompensatie?** *(alleen als: wachtdagen = ja)*  
  `f.loondoorbetaling_bij_ziekte.wachtdagcompensatie = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Hoe wordt de wachtdagcompensatie uitgekeerd?** *(alleen als: wachtdagcompensatie = ja)*  
  `f.loondoorbetaling_bij_ziekte.compensatie_soort = WachtdagcompensatieSoort.VAST_BEDRAG`  
  Keuzes: `WachtdagcompensatieSoort.VAST_BEDRAG` = Vast bedrag · `WachtdagcompensatieSoort.PERCENTAGE` = Percentage van loon
- **Bedrag (€)** *(alleen als: compensatie_soort = vast-bedrag)*  
  `f.loondoorbetaling_bij_ziekte.compensatie_bedrag = 1250` (€)
- **Percentage (%)** *(alleen als: compensatie_soort = percentage)*  
  `f.loondoorbetaling_bij_ziekte.compensatie_percentage = 8` (%)
- **van** *(alleen als: compensatie_soort = percentage)*  
  `f.loondoorbetaling_bij_ziekte.compensatie_basis = Loonbasis.UURLOON`  
  Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon

## 09 · Verlof

In `maak_upload.py`: `f.verlof` (zie `vul_verlof`).

- **Is er een betaalde ADV / ATV regeling van toepassing?**  
  `f.verlof.adv_atv.adv_regeling = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **(Ja,) namelijk:** *(alleen als: adv_regeling = ja)*  
  `f.verlof.adv_atv.namelijk = "tekst"`
- **Hoe wordt ADV / ATV toegekend?** *(alleen als: adv_regeling = ja)*  
  `f.verlof.adv_atv.toekenning = AdvToekenning(...)` met:
  - **(bloktitel is de vraag)**  
    `toekenning=AdvToekenningSoort.TIJD_DAGEN`  
    Keuzes: `AdvToekenningSoort.TIJD_DAGEN` = In tijd (dagen) · `AdvToekenningSoort.TIJD_UREN` = In tijd (uren) · `AdvToekenningSoort.GELD` = In geld
  - **dagen** *(alleen als: toekenning = tijd-dagen)*  
    `dagen_aantal=10`
  - **per** *(alleen als: toekenning = tijd-dagen)*  
    `dagen_tijdvak=Tijdvak.DAG`  
    Keuzes: `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
  - **uren** *(alleen als: toekenning = tijd-uren)*  
    `uren_aantal=10`
  - **per** *(alleen als: toekenning = tijd-uren)*  
    `uren_tijdvak=Tijdvak.DAG`  
    Keuzes: `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
  - **percentage (%)** *(alleen als: toekenning = geld)*  
    `geld_percentage=8` (%)
  - **van** *(alleen als: toekenning = geld)*  
    `geld_van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
- **Geldt er een aanvullende ADV / ATV regeling voor specifieke werknemers?** *(alleen als: adv_regeling = ja)*  
  `f.verlof.adv_atv.aanvullende_regeling = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Ouderen, namelijk:** *(alleen als: aanvullende_regeling = ja)*  
  `f.verlof.adv_atv.ouderen = True`
- **(namelijk)** *(alleen als: ouderen is ingevuld)*  
  `f.verlof.adv_atv.ouderen_namelijk = "tekst"`
- **Op basis van duur dienstverband, namelijk:** *(alleen als: aanvullende_regeling = ja)*  
  `f.verlof.adv_atv.duur_dienstverband = True`
- **(namelijk)** *(alleen als: duur_dienstverband is ingevuld)*  
  `f.verlof.adv_atv.duur_dienstverband_namelijk = "tekst"`
- **Anders, namelijk:** *(alleen als: aanvullende_regeling = ja)*  
  `f.verlof.adv_atv.anders = True`
- **(namelijk)** *(alleen als: anders is ingevuld)*  
  `f.verlof.adv_atv.anders_namelijk = "tekst"`
- **Hoe wordt de aanvullende ADV / ATV voor ouderen toegekend?** *(alleen als: ouderen is ingevuld)*  
  `f.verlof.adv_atv.toekenning_ouderen = AdvToekenning(...)` met:
  - dezelfde vragen als bij `AdvToekenning` hierboven
- **Hoe wordt de aanvullende ADV / ATV op basis van duur dienstverband toegekend?** *(alleen als: duur_dienstverband is ingevuld)*  
  `f.verlof.adv_atv.toekenning_duur_dienstverband = AdvToekenning(...)` met:
  - dezelfde vragen als bij `AdvToekenning` hierboven
- **Hoe wordt de aanvullende ADV / ATV op basis van andere voorwaarden toegekend?** *(alleen als: anders is ingevuld)*  
  `f.verlof.adv_atv.toekenning_anders = AdvToekenning(...)` met:
  - dezelfde vragen als bij `AdvToekenning` hierboven
- **Aantal**  
  `f.verlof.vakantiedagen.aantal = 10`
- **(dagen / uren)**  
  `f.verlof.vakantiedagen.type = VakantiedagenType.DAGEN`  
  Keuzes: `VakantiedagenType.DAGEN` = dagen · `VakantiedagenType.UREN` = uren
- **per:**  
  `f.verlof.vakantiedagen.tijdvak = Tijdvak.DAG`  
  Keuzes: `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **Ja, extra dagen vanaf een bepaalde leeftijd, namelijk:**  
  `f.verlof.vakantiedagen.dagen_leeftijd = True`
- **Extra dagen per leeftijd** *(alleen als: dagen_leeftijd is ingevuld)*  
  `f.verlof.vakantiedagen.leeftijd = [ExtraDagenLeeftijd(...), ExtraDagenLeeftijd(...)]`: herhaalbaar; per rij:
  - **vanaf … jaar oud**  
    `leeftijd=10` (jaar)
  - **in totaal … dagen**  
    `dagen=10` (dagen)
- **Ja, extra dagen per duur dienstverband, namelijk:**  
  `f.verlof.vakantiedagen.dagen_duur_dienstverband = True`
- **Extra dagen per duur dienstverband** *(alleen als: dagen_duur_dienstverband is ingevuld)*  
  `f.verlof.vakantiedagen.duur_dienstverband = [ExtraDagenDuurDienstverband(...), ExtraDagenDuurDienstverband(...)]`: herhaalbaar; per rij:
  - **vanaf … jaar dienstverband**  
    `jaar=10` (jaar)
  - **in totaal … dagen**  
    `dagen=10` (dagen)
- **Ja, anders, namelijk:**  
  `f.verlof.vakantiedagen.dagen_anders = True`
- **Extra dagen anders** *(alleen als: dagen_anders is ingevuld)*  
  `f.verlof.vakantiedagen.anders = [ExtraDagenAnders(...), ExtraDagenAnders(...)]`: herhaalbaar; per rij:
  - **in totaal … dagen**  
    `dagen=10` (dagen)
  - **voor**  
    `namelijk="tekst"`
- **Kent jouw onderneming bijzonder verlofregelingen, zoals bijvoorbeeld verlof voor een huwelijk, bij overlijd…**  
  `f.verlof.bijzonder_verlof.aanwezig = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Variaties bijzonder verlof** *(alleen als: aanwezig = ja)*  
  `f.verlof.bijzonder_verlof.variaties = [BijzonderVerlofVariatie(...), BijzonderVerlofVariatie(...)]`: herhaalbaar; per rij:
  - **Hoeveel**  
    `hoeveel=10`
  - **wat**  
    `wat=BijzonderVerlofEenheid.UUR`  
    Keuzes: `BijzonderVerlofEenheid.UUR` = Uur · `BijzonderVerlofEenheid.DAGEN` = Dagen · `BijzonderVerlofEenheid.WEKEN` = Weken · `BijzonderVerlofEenheid.MAANDEN` = Maanden · `BijzonderVerlofEenheid.JAREN` = Jaren
  - **In welk geval**  
    `voorwaarden="tekst"`
- **Ken je een regeling waarin gewerkte uren (bijvoorbeeld meeruren, overuren) niet tot uitkering komen, maar w…**  
  `f.verlof.tijd_voor_tijd.tijd_voor_tijd = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **(Ja,) namelijk:** *(alleen als: tijd_voor_tijd = ja)*  
  `f.verlof.tijd_voor_tijd.namelijk = "tekst"`
- **Kent jouw onderneming aanvullende regelingen indien de werknemer een Wazo uitkering geniet, (...)**  
  `f.verlof.aanvulling_wazo.wazo_aanvulling = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Een aanvulling op het betaalde ouderschapsverlof van** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.betaald_ouderschapsverlof = WazoRegel(...)` met:
  - **(checkbox-label uit de lijst)**  
    `aangevinkt=True`
  - **(namelijk)** *(alleen als: aangevinkt is ingevuld)*  
    `namelijk="tekst"`
- **Een aanvulling op het onbetaalde ouderschapsverlof van** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.onbetaald_ouderschapsverlof = WazoRegel(...)` met:
  - dezelfde vragen als bij `WazoRegel` hierboven
- **Een aanvulling op het aanvullend geboorteverlof** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.geboorteverlof = WazoRegel(...)` met:
  - dezelfde vragen als bij `WazoRegel` hierboven
- **Een aanvulling op het kortdurend zorgverlof** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.kortdurend_zorgverlof = WazoRegel(...)` met:
  - dezelfde vragen als bij `WazoRegel` hierboven
- **Een tegemoetkoming bij langdurend zorgverlof** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.langdurend_zorgverlof = WazoRegel(...)` met:
  - dezelfde vragen als bij `WazoRegel` hierboven
- **Een langere verlofduur:** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.langere_verlofduur = WazoRegel(...)` met:
  - dezelfde vragen als bij `WazoRegel` hierboven
- **Anders, namelijk:** *(alleen als: wazo_aanvulling = ja)*  
  `f.verlof.aanvulling_wazo.anders = WazoRegel(...)` met:
  - dezelfde vragen als bij `WazoRegel` hierboven
- **Kent jouw onderneming periodes, dagen of uren waarbij sprake is van een bedrijfssluiting waarvoor de werkne…**  
  `f.verlof.verplichte_aanwending.verplichte_aanwending = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Geef aan voor welke periode/dagen/uren de werknemer verplicht verlof moet aanwenden** *(alleen als: verplichte_aanwending = ja)*  
  `f.verlof.verplichte_aanwending.periode_dagen_uren = "tekst"`
- **Welk verlof dient de werknemer te gebruiken voor de hiervoor genoemde verplichte vrije periodes, (...)** *(alleen als: verplichte_aanwending = ja)*  
  `f.verlof.verplichte_aanwending.welk_verlof = "tekst"`
- **Hoeveel feestdagen kent jouw onderneming?**  
  `f.verlof.feestdagen.aantal = 10`
- **Welke feestdagen kent jouw onderneming?**  
  `f.verlof.feestdagen.welke = "tekst"`
- **Gelden er voorwaarden voor het genieten van een feestdag?**  
  `f.verlof.feestdagen.voorwaarden = "tekst"`
- **Ken je feestdagen die niet elk jaar worden toegekend?**  
  `f.verlof.feestdagen.niet_elk_jaar = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Om welke feestdagen gaat het en wat zijn de voorwaarden voor toekenning?** *(alleen als: niet_elk_jaar = ja)*  
  `f.verlof.feestdagen.niet_elk_jaar_voorwaarden = "tekst"`
- **Ken je persoonlijke feestdagen?**  
  `f.verlof.feestdagen.persoonlijke_feestdagen = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Hoeveel persoonlijke feestdagen kent jouw onderneming?** *(alleen als: persoonlijke_feestdagen = ja)*  
  `f.verlof.feestdagen.persoonlijk_aantal = 10`
- **Welke persoonlijke feestdagen kent jouw onderneming?** *(alleen als: persoonlijke_feestdagen = ja)*  
  `f.verlof.feestdagen.persoonlijk_namelijk = "tekst"`
- **Welke voorwaarden gelden er voor de persoonlijke feestdagen?** *(alleen als: persoonlijke_feestdagen = ja)*  
  `f.verlof.feestdagen.persoonlijk_voorwaarden = "tekst"`
- **Kennen jouw arbeidsvoorwaardenregeling(en) en/of cao een regeling om de waarde van een (verlof)dag te bepal…**  
  `f.verlof.waarde_verlofdag.waarde_verlofdag = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **(Ja, namelijk) percentage (%)** *(alleen als: waarde_verlofdag = ja)*  
  `f.verlof.waarde_verlofdag.percentage = 8` (%)

## 10 · Individueel keuzebudget

In `maak_upload.py`: `f.individueel_keuzebudget` (zie `vul_individueel_keuzebudget`).

- **Ken je een individueel keuze budget (IKB) of een vergelijkbaar budget waarbij de werknemer kan kiezen uit d…**  
  `f.individueel_keuzebudget.ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Wat is de waarde van dit budget?** *(alleen als: ja_nee = ja)*  
  `f.individueel_keuzebudget.waarde = Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage.
- **Zijn er bepaalde arbeidsvoorwaarden in het budget opgenomen?** *(alleen als: ja_nee = ja)*  
  `f.individueel_keuzebudget.arbeidsvoorwaarden_opgenomen = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Bovenwettelijke vakantiedagen voor** *(alleen als: (ja_nee = ja) en (arbeidsvoorwaarden_opgenomen = ja))*  
  `f.individueel_keuzebudget.bovenwettelijke_vakantiedagen = True`
- **percentage (%)** *(alleen als: bovenwettelijke_vakantiedagen is ingevuld)*  
  `f.individueel_keuzebudget.bovenwettelijke_vakantiedagen_percentage = 8` (%)
- **van** *(alleen als: bovenwettelijke_vakantiedagen is ingevuld)*  
  `f.individueel_keuzebudget.bovenwettelijke_vakantiedagen_van = IkbVan.UURLOON`  
  Keuzes: `IkbVan.UURLOON` = uurloon · `IkbVan.WEEKLOON` = weekloon · `IkbVan.MAANDLOON` = maandloon · `IkbVan.PERIODELOON` = periodeloon · `IkbVan.MINIMUMLOON` = minimumloon
- **ADV dagen voor** *(alleen als: (ja_nee = ja) en (arbeidsvoorwaarden_opgenomen = ja))*  
  `f.individueel_keuzebudget.adv_dagen = True`
- **percentage (%)** *(alleen als: adv_dagen is ingevuld)*  
  `f.individueel_keuzebudget.adv_dagen_percentage = 8` (%)
- **van** *(alleen als: adv_dagen is ingevuld)*  
  `f.individueel_keuzebudget.adv_dagen_van = IkbVan.UURLOON`  
  Keuzes: `IkbVan.UURLOON` = uurloon · `IkbVan.WEEKLOON` = weekloon · `IkbVan.MAANDLOON` = maandloon · `IkbVan.PERIODELOON` = periodeloon · `IkbVan.MINIMUMLOON` = minimumloon
- **Eindejaarsuitkering voor** *(alleen als: (ja_nee = ja) en (arbeidsvoorwaarden_opgenomen = ja))*  
  `f.individueel_keuzebudget.eindejaarsuitkering = True`
- **percentage (%)** *(alleen als: eindejaarsuitkering is ingevuld)*  
  `f.individueel_keuzebudget.eindejaarsuitkering_percentage = 8` (%)
- **van** *(alleen als: eindejaarsuitkering is ingevuld)*  
  `f.individueel_keuzebudget.eindejaarsuitkering_van = IkbVan.UURLOON`  
  Keuzes: `IkbVan.UURLOON` = uurloon · `IkbVan.WEEKLOON` = weekloon · `IkbVan.MAANDLOON` = maandloon · `IkbVan.PERIODELOON` = periodeloon · `IkbVan.MINIMUMLOON` = minimumloon
- **Vakantiebijslag voor** *(alleen als: (ja_nee = ja) en (arbeidsvoorwaarden_opgenomen = ja))*  
  `f.individueel_keuzebudget.vakantiebijslag = True`
- **percentage (%)** *(alleen als: vakantiebijslag is ingevuld)*  
  `f.individueel_keuzebudget.vakantiebijslag_percentage = 8` (%)
- **van** *(alleen als: vakantiebijslag is ingevuld)*  
  `f.individueel_keuzebudget.vakantiebijslag_van = IkbVan.UURLOON`  
  Keuzes: `IkbVan.UURLOON` = uurloon · `IkbVan.WEEKLOON` = weekloon · `IkbVan.MAANDLOON` = maandloon · `IkbVan.PERIODELOON` = periodeloon · `IkbVan.MINIMUMLOON` = minimumloon
- **Anders, namelijk:** *(alleen als: (ja_nee = ja) en (arbeidsvoorwaarden_opgenomen = ja))*  
  `f.individueel_keuzebudget.anders = True`
- **(namelijk)** *(alleen als: anders is ingevuld)*  
  `f.individueel_keuzebudget.anders_namelijk = "tekst"`

## 11 · Pensioen

In `maak_upload.py`: `f.pensioen` (zie `vul_pensioen`).

- **Ken je een pensioenregeling?**  
  `f.pensioen.van_toepassing = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Wat is de naam van het pensioenfonds?** *(alleen als: van_toepassing = ja)*  
  `f.pensioen.pensioenfonds_naam = "tekst"`
- **Wat is de hoogte van de werkgeverspremie? … % van de pensioengrondslag** *(alleen als: van_toepassing = ja)*  
  `f.pensioen.werkgeverspremie_percentage = 8` (%)
- **Hanteer je een franchise? (Ja, namelijk: / Nee)** *(alleen als: van_toepassing = ja)*  
  `f.pensioen.franchise = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Geef een beschrijving van de franchise** *(alleen als: franchise = ja)*  
  `f.pensioen.franchise_namelijk = "tekst"`

## 12 · Duurzaam werken en leven

In `maak_upload.py`: `f.duurzaam_werken_en_leven` (zie `vul_duurzaam_werken_en_leven`).

- **Opleidingen**  
  `f.duurzaam_werken_en_leven.opleidingen = RegelingVraagset(...)` met:
  - **(label van de regeling)**  
    `aangevinkt=True`
  - **(geen vraagtekst; hulptekst = andersHelp)** *(alleen als: aangevinkt is ingevuld)*  
    `namelijk="tekst"`
  - **Is er een (individueel) budget verbonden aan deze regeling?** *(alleen als: aangevinkt is ingevuld)*  
    `budget=BudgetOfGemiddeld.JA`  
    Keuzes: `BudgetOfGemiddeld.JA` = Ja · `BudgetOfGemiddeld.NEE_GEMIDDELD` = Nee, geef aan wat er gemiddeld per werknemer aan dit onderwerp wordt besteed.
  - **Hoe hoog is het budget?** *(alleen als: budget = ja)*  
    `budget_type=RegelingBudgetType.PERCENTAGE`  
    Keuzes: `RegelingBudgetType.PERCENTAGE` = Percentage van · `RegelingBudgetType.VAST_BEDRAG` = Vast bedrag namelijk: · `RegelingBudgetType.AANTAL_DAGEN_PER_JAAR` = Aantal dagen per jaar
  - **percentage (%)** *(alleen als: budget_type = percentage)*  
    `percentage=8` (%)
  - **van** *(alleen als: budget_type = percentage)*  
    `percentage_van=Loonbasis.UURLOON`  
    Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
  - **per** *(alleen als: budget_type = percentage)*  
    `percentage_tijdvak=Tijdvak.UUR`  
    Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
  - **bedrag (€)** *(alleen als: budget_type = vast-bedrag)*  
    `vast_bedrag=1250` (€)
  - **per** *(alleen als: budget_type = vast-bedrag)*  
    `vast_bedrag_tijdvak=Tijdvak.UUR`  
    Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
  - **dagen** *(alleen als: budget_type = aantal-dagen-per-jaar)*  
    `aantal_dagen_per_jaar=10`
  - **bedrag (€)** *(alleen als: budget = nee-gemiddeld)*  
    `gemiddeld_bedrag=1250` (€)
  - **per** *(alleen als: budget = nee-gemiddeld)*  
    `gemiddeld_tijdvak=Tijdvak.UUR`  
    Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
  - **Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur v…** *(alleen als: aangevinkt is ingevuld)*  
    `naar_rato=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt? (Ja = 'Ja, onder de volge…** *(alleen als: aangevinkt is ingevuld)*  
    `uitgekeerd=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **(geen vraagtekst, textarea)** *(alleen als: uitgekeerd = ja)*  
    `uitgekeerd_voorwaarden="tekst"`
  - **Zijn er voorwaarden verbonden aan de toekenning van het budget?** *(alleen als: aangevinkt is ingevuld)*  
    `voorwaarden=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **(geen vraagtekst, textarea)** *(alleen als: voorwaarden = ja)*  
    `voorwaarden_namelijk="tekst"`
- **Loopbaancoaching**  
  `f.duurzaam_werken_en_leven.loopbaancoaching = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Outplacementtrajecten**  
  `f.duurzaam_werken_en_leven.outplacementtrajecten = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Voorlichting met betrekking tot het in Nederland werken en verblijven van de niet permanent in Nederland wo…**  
  `f.duurzaam_werken_en_leven.voorlichting_nederland = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Scholing met betrekking tot het in Nederland werken en verblijven van de niet permanent in Nederland woonac…**  
  `f.duurzaam_werken_en_leven.scholing_nederland = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Sociale begeleiding met betrekking tot het in Nederland werken en verblijven van de niet permanent in Neder…**  
  `f.duurzaam_werken_en_leven.sociale_begeleiding_nederland = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Anders, namelijk: (met namelijk-veld)**  
  `f.duurzaam_werken_en_leven.inzetbaarheid_anders = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Geen**  
  `f.duurzaam_werken_en_leven.inzetbaarheid_geen = True`
- **Regeling ter bevordering van de fysieke gezondheid, namelijk: (met namelijk-veld)**  
  `f.duurzaam_werken_en_leven.fysieke_gezondheid = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Regeling ter bevordering van de mentale gezondheid, namelijk: (met namelijk-veld)**  
  `f.duurzaam_werken_en_leven.mentale_gezondheid = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Regeling ter bevordering van de financiële gezondheid, namelijk: (met namelijk-veld)**  
  `f.duurzaam_werken_en_leven.financiele_gezondheid = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Vitaliteitsbudget**  
  `f.duurzaam_werken_en_leven.vitaliteitsbudget = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Anders, namelijk: (met namelijk-veld)**  
  `f.duurzaam_werken_en_leven.vitaliteit_anders = RegelingVraagset(...)` met:
  - dezelfde vragen als bij `RegelingVraagset` hierboven
- **Geen**  
  `f.duurzaam_werken_en_leven.vitaliteit_geen = True`
- **Is er sprake van scholing die op grond van de wet of cao noodzakelijk is voor de uitvoering van het werk? (…**  
  `f.duurzaam_werken_en_leven.verplichte_scholing = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **(geen vraagtekst, textarea)** *(alleen als: verplichte_scholing = ja)*  
  `f.duurzaam_werken_en_leven.verplichte_scholing_namelijk = "tekst"`
- **Hoeveel kost de verplichte scholing in tijd?** *(alleen als: verplichte_scholing = ja)*  
  `f.duurzaam_werken_en_leven.scholing_tijd = 10`
- **(geen vraagtekst, eenheid)** *(alleen als: verplichte_scholing = ja)*  
  `f.duurzaam_werken_en_leven.scholing_tijd_type = TijdEenheid.UUR`  
  Keuzes: `TijdEenheid.UUR` = Uur / Uren · `TijdEenheid.DAG` = Dagen
- **Wanneer wordt de verplichte scholing gevolgd?** *(alleen als: verplichte_scholing = ja)*  
  `f.duurzaam_werken_en_leven.scholing_wanneer = ScholingWanneer.TIJDENS_WERKTIJD`  
  Keuzes: `ScholingWanneer.TIJDENS_WERKTIJD` = Tijdens werktijd, namelijk: · `ScholingWanneer.ANDER_MOMENT` = Op een ander moment, namelijk:
- **(geen vraagtekst)** *(alleen als: scholing_wanneer = tijdens-werktijd)*  
  `f.duurzaam_werken_en_leven.scholing_tijdens_werktijd = "tekst"`
- **(geen vraagtekst)** *(alleen als: scholing_wanneer = ander-moment)*  
  `f.duurzaam_werken_en_leven.scholing_ander_moment = "tekst"`
- **Hoeveel kost de verplichte scholing inclusief alle bijkomende kosten (studiemateriaal, examengelden etc.)? (€)** *(alleen als: verplichte_scholing = ja)*  
  `f.duurzaam_werken_en_leven.scholing_kosten = 1250` (€)
- **Kent jouw onderneming regelingen voor een duurzame samenleving en groene aarde? Zoals klimaatbudget, vrije …**  
  `f.duurzaam_werken_en_leven.samenleving_regeling = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Is er een (individueel) budget verbonden aan regelingen voor een duurzame samenleving en een groene aarde?** *(alleen als: samenleving_regeling = ja)*  
  `f.duurzaam_werken_en_leven.samenleving_budget = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Hoe hoog is het budget?** *(alleen als: samenleving_budget = ja)*  
  `f.duurzaam_werken_en_leven.budget_hoogte = SamenlevingBudgetHoogte.PERCENTAGE`  
  Keuzes: `SamenlevingBudgetHoogte.PERCENTAGE` = Percentage van · `SamenlevingBudgetHoogte.VAST_BEDRAG` = Vast bedrag namelijk: · `SamenlevingBudgetHoogte.UREN_OF_DAGEN` = Uren of dagen
- **percentage (%)** *(alleen als: budget_hoogte = percentage)*  
  `f.duurzaam_werken_en_leven.percentage = 8` (%)
- **van** *(alleen als: budget_hoogte = percentage)*  
  `f.duurzaam_werken_en_leven.percentage_van = Loonbasis.UURLOON`  
  Keuzes: `Loonbasis.UURLOON` = Uurloon · `Loonbasis.DAGLOON` = Dagloon · `Loonbasis.VIERWEKENLOON` = 4-weken loon · `Loonbasis.MAANDLOON` = Maandloon · `Loonbasis.JAARLOON` = Jaarloon
- **per** *(alleen als: budget_hoogte = percentage)*  
  `f.duurzaam_werken_en_leven.percentage_tijdvak = Tijdvak.UUR`  
  Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **Bedrag (€)** *(alleen als: budget_hoogte = vast-bedrag)*  
  `f.duurzaam_werken_en_leven.vast_bedrag = 1250` (€)
- **per (tijdvak)** *(alleen als: budget_hoogte = vast-bedrag)*  
  `f.duurzaam_werken_en_leven.vast_bedrag_tijdvak = Tijdvak.UUR`  
  Keuzes: `Tijdvak.UUR` = Uur · `Tijdvak.DAG` = Dag · `Tijdvak.WEEK` = Week · `Tijdvak.MAAND` = Maand · `Tijdvak.JAAR` = Jaar
- **aantal** *(alleen als: budget_hoogte = uren-of-dagen)*  
  `f.duurzaam_werken_en_leven.uren_of_dagen_aantal = 10`
- **type** *(alleen als: budget_hoogte = uren-of-dagen)*  
  `f.duurzaam_werken_en_leven.uren_of_dagen_type = TijdEenheid.UUR`  
  Keuzes: `TijdEenheid.UUR` = Uur / Uren · `TijdEenheid.DAG` = Dagen
- **per** *(alleen als: budget_hoogte = uren-of-dagen)*  
  `f.duurzaam_werken_en_leven.uren_of_dagen_per = DagenPer.WEEK`  
  Keuzes: `DagenPer.WEEK` = Week · `DagenPer.MAAND` = Maand · `DagenPer.JAAR` = Jaar
- **Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur v…** *(alleen als: samenleving_budget = ja)*  
  `f.duurzaam_werken_en_leven.budget_naar_rato = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Wordt dit budget uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt?** *(alleen als: samenleving_budget = ja)*  
  `f.duurzaam_werken_en_leven.budget_uitgekeerd = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **onder de volgende voorwaarden** *(alleen als: budget_uitgekeerd = ja)*  
  `f.duurzaam_werken_en_leven.budget_uitgekeerd_voorwaarden = "tekst"`
- **Zijn er voorwaarden verbonden aan de toekenning van het budget? (Ja = 'Ja, namelijk:')** *(alleen als: samenleving_budget = ja)*  
  `f.duurzaam_werken_en_leven.budget_voorwaarden = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **(geen vraagtekst, textarea)** *(alleen als: budget_voorwaarden = ja)*  
  `f.duurzaam_werken_en_leven.budget_voorwaarden_namelijk = "tekst"`

## 13 · Aanvullende regelingen

In `maak_upload.py`: `f.aanvullende_regelingen` (zie `vul_aanvullende_regelingen`).

- **Kent jouw onderneming een PAWW (private aanvulling WW) regeling?**  
  `f.aanvullende_regelingen.paww = AanvullendeRegelingMetDekking(...)` met:
  - **(vraagtekst verschilt per regeling)**  
    `ja_nee=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Omschrijf de inhoud van de regeling** *(alleen als: ja_nee = ja)*  
    `omschrijving="tekst"`
  - **Wat is de werkgeverspremie?** *(alleen als: ja_nee = ja)*  
    `werkgeverspremie=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, n/a.
  - **Wat is de werknemerspremie?** *(alleen als: ja_nee = ja)*  
    `werknemerspremie=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, n/a.
  - **Wat is de dekkingswaarde?** *(alleen als: ja_nee = ja)*  
    `dekkingswaarde=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, tijd.
- **Kent jouw onderneming een PAZW (private aanvulling Ziektewet) regeling?**  
  `f.aanvullende_regelingen.pazw = AanvullendeRegelingMetDekking(...)` met:
  - dezelfde vragen als bij `AanvullendeRegelingMetDekking` hierboven
- **Kent jouw onderneming een RVU regeling, een generatiepact of regeling om minder te gaan werken richting het…**  
  `f.aanvullende_regelingen.rvu_regeling = AanvullendeRegeling(...)` met:
  - **(vraagtekst verschilt per regeling)**  
    `ja_nee=JaNee.JA`  
    Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
  - **Omschrijf de inhoud van de regeling** *(alleen als: ja_nee = ja)*  
    `omschrijving="tekst"`
  - **Wat is de werkgeverspremie?** *(alleen als: ja_nee = ja)*  
    `werkgeverspremie=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, n/a.
  - **Wat is de werknemerspremie?** *(alleen als: ja_nee = ja)*  
    `werknemerspremie=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, n/a.
- **Kent jouw onderneming een WGA-Hiaat regeling?**  
  `f.aanvullende_regelingen.wga_hiaat = AanvullendeRegelingMetDekking(...)` met:
  - dezelfde vragen als bij `AanvullendeRegelingMetDekking` hierboven
- **Kent jouw onderneming een ongevallenverzekering?**  
  `f.aanvullende_regelingen.ongevallenverzekering = AanvullendeRegelingMetDekking(...)` met:
  - dezelfde vragen als bij `AanvullendeRegelingMetDekking` hierboven
- **Kent jouw onderneming andere aanvullende sociale zekerheidsregeling?**  
  `f.aanvullende_regelingen.andere_ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Andere aanvullende sociale zekerheidsregelingen (rijen hebben geen showIf; knop 'Regeling toevoegen' alleen…**  
  `f.aanvullende_regelingen.andere_regelingen = [AndereSocialeRegeling(...), AndereSocialeRegeling(...)]`: herhaalbaar; per rij:
  - **Omschrijf de inhoud van de regeling**  
    `omschrijving="tekst"`
  - **Wat is de werkgeverspremie? (alleen positie 0)**  
    `werkgeverspremie=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan).
  - **Wat is de werknemerspremie? (alleen positie 0)**  
    `werknemerspremie=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan).

## 14 · Overig

In `maak_upload.py`: `f.overig` (zie `vul_overig`).

- **Zijn er overige regelingen of arbeidsvoorwaarden van toepassing?**  
  `f.overig.ja_nee = JaNee.JA`  
  Keuzes: `JaNee.JA` = Ja · `JaNee.NEE` = Nee
- **Overige regelingen** *(alleen als: ja_nee = ja)*  
  `f.overig.overige_regelingen = [OverigeRegeling(...), OverigeRegeling(...)]`: herhaalbaar; per rij:
  - **Naam** *(alleen als: ../ja_nee = ja)*  
    `naam="tekst"`
  - **Voorwaarden** *(alleen als: ../ja_nee = ja)*  
    `voorwaarden="tekst"`
  - **Hoe wordt de waarde uitgekeerd?** *(alleen als: ../ja_nee = ja)*  
    `waarde=Bedragregel(...)`: een bedrag (zie *Bedragen* bovenaan). Toegestaan: vast-bedrag, percentage, tijd.

## 15 · Grondslagen

In `maak_upload.py`: `f.grondslagen` (zie `vul_grondslagen`).

- **Instellingen per gebruikte grondslag**  
  `f.grondslagen.per_grondslag = {sleutel: GrondslagInstelling(...)}` (per Grondslag); per sleutel:
  - **Salaris wordt meegenomen bij deze grondslag**  
    `salaris=True`
  - **Vakantietoeslag wordt meegenomen bij deze grondslag**  
    `vakantietoeslag=True`
  - **Betaald verlof wordt meegenomen bij deze grondslag**  
    `betaald_verlof=True`
  - **Worden toeslagen meegenomen bij deze grondslag?**  
    `toeslagen=ToeslagenMeegenomen.ALLE`  
    Keuzes: `ToeslagenMeegenomen.ALLE` = Alle toeslagen · `ToeslagenMeegenomen.GEEN` = Geen toeslagen · `ToeslagenMeegenomen.SOMMIGE` = Sommige toeslagen:
  - **Eén checkbox per toeslagsoort** *(alleen als: toeslagen = some)*  
    `toeslag={sleutel: True}` (per ToeslagSoort)
  - **Peildatum voor deze grondslag**  
    `peildatum=dt.date(2026, 1, 1)`

## 16 · Ondertekenen

In `maak_upload.py`: `f.ondertekenen` (zie `vul_ondertekenen`).

- **Contactpersonen (eerste = persoon die het formulier invult)**  
  `f.ondertekenen.contactpersonen = [Contactpersoon(...), Contactpersoon(...)]`: herhaalbaar; per rij:
  - **Naam:**  
    `naam="tekst"`
  - **E-mailadres:**  
    `email="tekst"`
  - **Telefoonnummer:**  
    `telefoon="tekst"`
  - **Functie:**  
    `functie="tekst"`
- **Ik verklaar bevoegd te zijn tot het het verstrekken van de gevraagde informatie aan de uitzendonderneming. …**  
  `f.ondertekenen.akkoord = True`
