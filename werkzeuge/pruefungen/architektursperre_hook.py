#!/usr/bin/env python3
"""Architektursperre als Vorabprüfung für Änderungen (Hook ``PreToolUse`` in ``.claude/settings.json``).

Liest die geplante Änderung (Edit, Write, MultiEdit) von der Standardeingabe, bildet den Quelltext, der entstünde, und lässt ihn von
``architekturpruefung`` mit dem Rest des Projekts prüfen. Führt die Änderung einen **neuen** Verstoß ein (mehr Verstöße je Regel, Datei und Stelle als
vorher), wird sie blockiert (Rückgabewert 2, Meldung an die Entwickler-KI). Bereits vorhandene Verstöße blockieren nur Änderungen, die weitere hinzufügen;
so lässt sich Altlast beseitigen, aber nichts Neues einbauen. Es gibt keine Ausnahmenliste.

Ebenso blockiert: Shell-Befehle (``Bash``), die Qt-Bezeichner in Quelldateien des Projekts schreiben wollen (Heuristik über den Befehlstext).
Bei einem Fehler in der Sperre selbst wird nicht blockiert, aber laut gemeldet (damit die Arbeit nicht stillsteht)."""
from __future__ import annotations

import collections
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(os.path.dirname(HIER))
sys.path.insert(0, HIER)

QT_ZEICHEN = re.compile(r"PySide6|PyQt[56]|shiboken|QtCharts|QtGui|QtCore|QtWidgets|\bQ(?:Image|Pixmap|Painter|Text[A-Za-z]+|PlainTextEdit|AbstractTextDocumentLayout)\b")
QUELLPFAD = re.compile(r"src/lunivo_writer/(?:core|modelle|dienste)/")


def _melden(text: str, blockieren: bool) -> int:
    print(text, file=sys.stderr)
    return 2 if blockieren else 0


def _ergebnisquelltext(werkzeug: str, eingabe: dict, pfad: str) -> str | None:
    """Der Quelltext der Datei nach der geplanten Änderung; ``None``, wenn er sich nicht bestimmen lässt."""
    if werkzeug == "Write":
        return eingabe.get("content")
    try:
        with open(pfad, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    aenderungen = eingabe.get("edits") if werkzeug == "MultiEdit" else [eingabe]
    for a in aenderungen or []:
        alt, neu = a.get("old_string"), a.get("new_string")
        if alt is None or neu is None or alt not in text:
            return None                                                       # die Änderung wird ohnehin abgelehnt
        text = text.replace(alt, neu) if a.get("replace_all") else text.replace(alt, neu, 1)
    return text


def _zaehlen(verstoesse) -> collections.Counter:
    return collections.Counter((v.regel, v.datei, v.stelle) for v in verstoesse)


def main() -> int:
    try:
        daten = json.load(sys.stdin)
        werkzeug, eingabe = daten.get("tool_name", ""), daten.get("tool_input") or {}
        if werkzeug == "Bash":
            befehl = eingabe.get("command", "")
            if QUELLPFAD.search(befehl) and QT_ZEICHEN.search(befehl) and re.search(r"\b(sed|python3?|tee|cat|perl|awk|echo|printf)\b|>>?", befehl):
                return _melden("ARCHITEKTURSPERRE — blockiert: Der Befehl schreibt Qt-Bezeichner in Quelldateien unter src/lunivo_writer. "
                               "Das Dokument (core, modelle, Dokument-Adapter in dienste) muss Qt-frei bleiben; Qt gehört nur in Oberfläche und adapter/qt. "
                               "Lösung im Kern suchen oder den Eigentümer fragen.", True)
            return 0
        if werkzeug not in ("Edit", "Write", "MultiEdit"):
            return 0
        pfad = os.path.abspath(eingabe.get("file_path", ""))
        quelle = os.path.join(PROJEKT, "src", "lunivo_writer") + os.sep
        if not pfad.startswith(quelle) or not pfad.endswith(".py"):
            return 0
        neu_text = _ergebnisquelltext(werkzeug, eingabe, pfad)
        if neu_text is None:
            return 0
        import ast
        try:
            ast.parse(neu_text)
        except SyntaxError:
            return 0                                                          # Syntax ist nicht Aufgabe der Sperre
        from architekturpruefung import pruefen
        vorher, _ = pruefen(PROJEKT)
        nachher, _ = pruefen(PROJEKT, {pfad: neu_text})
        mehr = _zaehlen(nachher) - _zaehlen(vorher)
        if not mehr:
            return 0
        neue = [v for v in nachher if (v.regel, v.datei, v.stelle) in mehr]
        text = "ARCHITEKTURSPERRE — Änderung blockiert (neuer Architekturverstoß, nicht umsetzen):\n\n" + "\n\n".join(v.text() for v in neue)
        text += ("\n\nDie Änderung wurde nicht geschrieben. Eine architekturkonforme Lösung in der zuständigen bestehenden Komponente entwickeln "
                 "(CLAUDE.md, Abschnitt „Architektursperre“). Die Sperre nicht abschwächen und keine Ausnahme einbauen; neue Ausnahmen genehmigt nur der Eigentümer.")
        return _melden(text, True)
    except Exception as e:                                                    # noqa: BLE001 — eine defekte Sperre darf die Arbeit nicht lahmlegen, muss aber auffallen
        return _melden(f"ARCHITEKTURSPERRE — INTERNER FEHLER, Änderung nicht geprüft: {type(e).__name__}: {e}", False)


if __name__ == "__main__":
    sys.exit(main())
