"""Module in Unterpakete verschieben und alle Verweise mitziehen (Quelltext, Tests, Werkzeuge, Doku).

Aufruf: ``python werkzeug/module_verschieben.py <Paket> <Ziel-Unterpaket>:<modul>,<modul> ...``
Beispiel: ``python werkzeug/module_verschieben.py lunivo_writer.editor seite:pagination,umbruch``
Angepasst werden ``lunivo_writer.<Paket>.<modul>`` (auch in Text), ``from <Paket> import <modul>`` (je Name getrennt)
und Weiterleitungen. Schreibt kein HTML; arbeitet nur auf Textdateien.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SUCHE = ("src", "tests", "werkzeug", "docs", "CLAUDE.md", ".github")
ENDUNGEN = {".py", ".md", ".yml", ".yaml", ".toml", ".txt", ".json"}


def _dateien():
    for name in SUCHE:
        p = WURZEL / name
        if p.is_file():
            yield p
        elif p.is_dir():
            for q in p.rglob("*"):
                if q.is_file() and q.suffix in ENDUNGEN and "__pycache__" not in q.parts:
                    yield q


def verschieben(paket: str, karte: dict[str, str]) -> int:
    """``karte``: Modulname -> Unterpaket. Verschiebt die Dateien und schreibt die Verweise um."""
    ordner = WURZEL / "src" / Path(*paket.split("."))
    for modul, ziel in karte.items():
        quelle = ordner / f"{modul}.py"
        if not quelle.is_file() and (ordner / ziel / f"{modul}.py").is_file():
            continue                                   # schon dort: nur die Verweise werden umgeschrieben
        if not quelle.is_file():
            raise SystemExit(f"fehlt: {quelle}")
        (ordner / ziel).mkdir(exist_ok=True)
        init = ordner / ziel / "__init__.py"
        if not init.exists():
            init.write_text(f'"""Unterpaket ``{ziel}`` von ``{paket}``."""\n', encoding="utf-8")
        quelle.rename(ordner / ziel / f"{modul}.py")
    namen = "|".join(sorted(map(re.escape, karte), key=len, reverse=True))
    punkt = re.compile(rf"{re.escape(paket)}\.({namen})\b")
    # „from <paket> import a, b as c“ (eine Zeile; Klammern/Fortsetzungen werden gemeldet)
    von = re.compile(rf"^(\s*)from {re.escape(paket)} import (.+?)(\s*#.*)?$", re.M)
    kurz = paket.split(".")[-1]                        # Kurzformen in Kommentaren: ``editor/modul.py``, ``editor.modul``
    slash = re.compile(rf"(?<![\w/.]){re.escape(kurz)}/({namen})\b")
    kurzpunkt = re.compile(rf"(?<![\w/.]){re.escape(kurz)}\.({namen})\b")
    pfadform = "/".join(paket.split(".")[1:])          # ``ui/document``: auch mit Vorsatz (``src/lunivo_writer/ui/document/bearbeitung/base.py``)
    pfad_re = re.compile(rf"(?<![\w.]){re.escape(pfadform)}/({namen})\b") if pfadform else None
    geaendert = 0

    def trennen(m: re.Match) -> str:
        einr, liste, kommentar = m.group(1), m.group(2), m.group(3) or ""
        if liste.strip().startswith("(") or liste.rstrip().endswith("\\"):
            return m.group(0)
        teile = [t.strip() for t in liste.split(",") if t.strip()]
        if not any(t.split(" as ")[0] in karte for t in teile):
            return m.group(0)
        bleibt, zeilen = [], []
        for t in teile:
            n = t.split(" as ")[0]
            if n in karte:
                zeilen.append(f"{einr}from {paket}.{karte[n]} import {t}")
            else:
                bleibt.append(t)
        if bleibt:
            zeilen.insert(0, f"{einr}from {paket} import {', '.join(bleibt)}")
        return "\n".join(zeilen) + kommentar

    for p in _dateien():
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        t = von.sub(trennen, s)
        t = punkt.sub(lambda m: f"{paket}.{karte[m.group(1)]}.{m.group(1)}", t)
        t = slash.sub(lambda m: f"{kurz}/{karte[m.group(1)]}/{m.group(1)}", t)
        if pfad_re:
            t = pfad_re.sub(lambda m: f"{pfadform}/{karte[m.group(1)]}/{m.group(1)}", t)
        t = kurzpunkt.sub(lambda m: f"{kurz}.{karte[m.group(1)]}.{m.group(1)}", t)
        if t != s:
            p.write_text(t, encoding="utf-8")
            geaendert += 1
    return geaendert


if __name__ == "__main__":
    paket = sys.argv[1]
    karte = {}
    for arg in sys.argv[2:]:
        ziel, _, liste = arg.partition(":")
        for m in liste.split(","):
            karte[m] = ziel
    print(verschieben(paket, karte), "Dateien angepasst")
