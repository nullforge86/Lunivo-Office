"""Prüft nach dem Verschieben von Modulen, ob alle Importpfade noch stimmen. Schreibt Markdown (kein HTML).

1. Jedes Modul von ``lunivo_writer`` lässt sich importieren (``__main__`` ausgenommen).
2. Jeder Pfad ``lunivo_writer.a.b`` im Quelltext, in Tests, Werkzeugen und Doku zeigt auf ein vorhandenes Modul oder Paket
   (oder auf einen Namen darin).
3. Keine Weiterleitungs-Module (``sys.modules[__name__] = …``): alte Pfade werden nicht weiter geführt.

Aufruf: ``QT_QPA_PLATFORM=offscreen PYTHONPATH=src python werkzeug/importpruefung.py`` — Rückgabewert 1 bei Fehlern.
"""
from __future__ import annotations

import importlib
import pkgutil
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
PAKET = "lunivo_writer"
PFAD = re.compile(rf"\b{PAKET}(?:\.\w+)+")
TEXTE = {".py", ".md"}


def module_importieren() -> list[str]:
    fehler = []
    paket = importlib.import_module(PAKET)
    for m in pkgutil.walk_packages(paket.__path__, f"{PAKET}."):
        if m.name.endswith("__main__"):
            continue
        try:
            importlib.import_module(m.name)
        except Exception as e:  # noqa: BLE001 - jede Art Fehler ist hier ein Befund
            fehler.append(f"Import {m.name}: {type(e).__name__}: {e}")
    return fehler


def _loest_auf(pfad: str) -> bool:
    teile = pfad.split(".")
    k = len(teile)
    while k > 0:
        basis = WURZEL / "src" / Path(*teile[:k])
        if basis.with_suffix(".py").is_file() or basis.is_dir():
            break
        k -= 1
    if k == len(teile):
        return True
    if k == 0:
        return False
    basis = WURZEL / "src" / Path(*teile[:k])
    datei = basis.with_suffix(".py") if basis.with_suffix(".py").is_file() else basis / "__init__.py"
    return datei.is_file() and re.search(rf"\b{re.escape(teile[k])}\b", datei.read_text(encoding="utf-8")) is not None


def pfade_pruefen() -> list[str]:
    fehler = []
    for ordner in ("src", "tests", "werkzeug", "docs"):
        for p in (WURZEL / ordner).rglob("*"):
            if not p.is_file() or p.suffix not in TEXTE or "__pycache__" in p.parts or p == Path(__file__).resolve():
                continue
            for n, zeile in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
                for pfad in PFAD.findall(zeile):
                    if pfad.split(".")[-1] in {"__file__", "__path__"} or not _loest_auf(pfad):
                        if pfad.split(".")[-1] in {"__file__", "__path__"}:
                            continue
                        fehler.append(f"{p.relative_to(WURZEL)}:{n}: {pfad}")
    return fehler


def weiterleitungen() -> list[str]:
    return [str(p.relative_to(WURZEL)) for p in (WURZEL / "src" / PAKET).rglob("*.py") if "sys.modules[__name__]" in p.read_text(encoding="utf-8")]


def pruefen() -> dict[str, list[str]]:
    return {"Importfehler": module_importieren(), "Unbekannte Pfade": pfade_pruefen(), "Weiterleitungen": weiterleitungen()}


if __name__ == "__main__":
    sys.path.insert(0, str(WURZEL / "src"))
    ergebnis = pruefen()
    for titel, liste in ergebnis.items():
        print(f"## {titel}: {len(liste)}")
        for z in liste:
            print(f"- {z}")
    sys.exit(1 if any(ergebnis.values()) else 0)
