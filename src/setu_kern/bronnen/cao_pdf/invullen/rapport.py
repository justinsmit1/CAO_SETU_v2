"""Het rapport van het invullen: per waarde waar hij vandaan komt, en wat niet gevonden of weggegooid is."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Onderbouwing:
    pad: str
    document: str
    pagina: int
    artikel: str | None
    citaat: str


@dataclass
class Ingevuld:
    pad: str
    waarde: Any
    onderbouwing: Onderbouwing | None  # None = uit de parameters


@dataclass
class BlokVerslag:
    blok: str
    ingevuld: list[Ingevuld] = field(default_factory=list)
    niet_gevonden: list[str] = field(default_factory=list)
    weggegooid: list[tuple[str, str]] = field(default_factory=list)  # (pad, reden)
    meldingen: list[str] = field(default_factory=list)
    aanroepen: int = 0


@dataclass
class Rapport:
    blokken: list[BlokVerslag] = field(default_factory=list)
    uit_parameters: list[Ingevuld] = field(default_factory=list)
    niet_ondersteund: list[str] = field(default_factory=list)  # secties zonder blok
    uit_basis: list[str] = field(default_factory=list)  # secties die uit het basisformulier komen, niet uit de cao
    controle: list[str] = field(default_factory=list)  # Formulier.controleer() na het invullen

    def meldingen(self) -> list[str]:
        """Korte meldingen voor het Resultaat van de adapter."""
        uit = [f"uit parameters: {i.pad}" for i in self.uit_parameters]
        for b in self.blokken:
            uit += [f"{b.blok}: {p} niet gevonden in de cao" for p in b.niet_gevonden]
            uit += [f"{b.blok}: {p} weggegooid ({reden})" for p, reden in b.weggegooid]
            uit += [f"{b.blok}: {m}" for m in b.meldingen]
        uit += [f"sectie {s}: nog niet ondersteund door het LLM-invullen" for s in self.niet_ondersteund]
        uit += [f"sectie {s}: uit het basisformulier, niet uit de cao" for s in self.uit_basis]
        uit += [f"controle: {c}" for c in self.controle]
        return uit

    def naar_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(asdict(self), default=str))

    def naar_markdown(self) -> str:
        regels = ["# Rapport LLM-invullen", ""]
        for b in self.blokken:
            regels += [f"## {b.blok}", "", f"Aanroepen: {b.aanroepen}", ""]
            if b.ingevuld:
                regels += ["| Veld | Waarde | Bron | Citaat |", "|---|---|---|---|"]
                for i in b.ingevuld:
                    o = i.onderbouwing
                    bron = f"{o.document}, p. {o.pagina}" + (f", {o.artikel}" if o.artikel else "") if o else "parameters"
                    citaat = (o.citaat if o else "").replace("|", "\\|").replace("\n", " ")
                    regels.append(f"| `{i.pad}` | {i.waarde} | {bron} | {citaat} |")
                regels.append("")
            for kop, lijst in (
                ("Niet gevonden", b.niet_gevonden),
                ("Weggegooid", [f"{p}: {r}" for p, r in b.weggegooid]),
                ("Meldingen", b.meldingen),
            ):
                if lijst:
                    regels += [f"**{kop}**", "", *[f"- {x}" for x in lijst], ""]
        if self.uit_parameters:
            regels += ["## Uit de parameters", "", *[f"- `{i.pad}` = {i.waarde}" for i in self.uit_parameters], ""]
        if self.niet_ondersteund:
            regels += ["## Nog niet ondersteund", "", *[f"- {s}" for s in self.niet_ondersteund], ""]
        if self.uit_basis:
            regels += ["## Uit het basisformulier (niet uit de cao)", "", *[f"- {s}" for s in self.uit_basis], ""]
        if self.controle:
            regels += ["## Controle van het hele formulier", "", *[f"- {c}" for c in self.controle], ""]
        return "\n".join(regels)

    def schrijf(self, map_: str | Path, naam: str = "llm_rapport") -> None:
        map_ = Path(map_)
        map_.mkdir(parents=True, exist_ok=True)
        (map_ / f"{naam}.md").write_text(self.naar_markdown(), encoding="utf-8")
        (map_ / f"{naam}.json").write_text(json.dumps(self.naar_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
