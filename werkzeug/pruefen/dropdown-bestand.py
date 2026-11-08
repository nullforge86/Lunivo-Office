#!/usr/bin/env python3
"""Schreibt docs/dropdown-bestand.md: alle Dropdown-Bausteine und ihre Verwendung (Markdown, aus dem Quelltext erzeugt)."""
import ast, pathlib, re

WURZEL = pathlib.Path(__file__).resolve().parents[2]
SRC = WURZEL / "src" / "lunivo_writer"
PAKET = "ui/baukasten/dropdown/"
BASEN = {"MenueListe", "PopupVerhalten", "Auswahlfeld", "Schriftauswahl", "DropdownKnopf", "DropdownTaste", "UeberlaufLeiste", "FlacheReiterLeiste"}

klassen, verwendung = [], {n: {} for n in ("MenueListe(", "Auswahlfeld(", "Schriftauswahl(", "DropdownKnopf(", "DropdownTaste(", "menue_setzen(")}
for p in sorted(SRC.rglob("*.py")):
    rel = p.relative_to(SRC).as_posix(); text = p.read_text(encoding="utf-8")
    for k in ast.walk(ast.parse(text)):
        if isinstance(k, ast.ClassDef):
            basen = {getattr(b, "id", getattr(b, "attr", "")) for b in k.bases}
            if basen & BASEN or k.name in BASEN:
                klassen.append((k.name, ", ".join(sorted(b for b in (getattr(b, "id", getattr(b, "attr", "")) for b in k.bases) if b)), rel))
    for n in verwendung:
        z = len(re.findall(r"(?<![A-Za-z_])" + re.escape(n), text))
        if z and not (rel.startswith(PAKET) and n != "menue_setzen("):
            verwendung[n][rel] = z

z = ["# Dropdown-Bestand", "", "Erzeugt mit `werkzeug/pruefen/dropdown-bestand.py` (nicht von Hand ändern). Alle Dropdown-Bausteine liegen im Paket "
     "`ui/baukasten/dropdown/`; Regeln und Pyramide stehen in `docs/baukasten.md`.", "", "## Klassen (Baustein → Basis → Datei)", "",
     "| Klasse | Basis | Datei |", "|---|---|---|"]
for n, b, r in sorted(klassen, key=lambda x: (x[2], x[0])):
    z.append(f"| `{n}` | {b} | `{r}` |")
for n, d in verwendung.items():
    z += ["", f"## Verwendung von `{n}…` außerhalb des Pakets ({sum(d.values())} Stellen in {len(d)} Dateien)", ""]
    z += [f"- `{r}`: {c}" for r, c in sorted(d.items())] or ["- keine"]
(WURZEL / "docs" / "dropdown-bestand.md").write_text("\n".join(z) + "\n", encoding="utf-8")
print("docs/dropdown-bestand.md:", len(klassen), "Klassen")
