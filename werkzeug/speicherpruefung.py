#!/usr/bin/env python3
"""Prüft den Speicherweg für alle Formate und schreibt ein Prüfprotokoll in eine SQLite-Datenbank.

    .venv/bin/python werkzeug/speicherpruefung.py [--db PFAD] [--formate .docx,.odt,...]

Läuft ohne Bildschirm in einem eigenen Temp-Ordner mit eigens erzeugten Testdokumenten; vorhandene Dokumente werden nie angefasst.
Je Format und Testfall wird gespeichert, die Struktur geprüft, erneut geöffnet und der Inhalt verglichen.

In der Datenbank (Vorgabe: ``$XDG_CACHE_HOME/lunivo-writer/speicherpruefung.sqlite3``) stehen je Lauf: Test-ID, Zeitpunkt, Format,
Testfall, Ergebnis von Speichern, Strukturprüfung und erneutem Öffnen, Inhaltsvergleich, Dateigröße, SHA-256, Fehlerkategorie und
technische Einzelheiten. **Keine Dokumentinhalte** — es gibt nur eigene Testtexte, und auch die werden nicht abgelegt.
Die Datenbank ist ein Prüfwerkzeug, kein Teil der Anwendung und kein Ersatz für Sicherungskopien.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import sys
import tempfile
import time
import uuid

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HIER), "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

TABELLE = """
CREATE TABLE IF NOT EXISTS pruefung (
    test_id TEXT NOT NULL,
    lauf_id TEXT NOT NULL,
    zeit TEXT NOT NULL,
    format TEXT NOT NULL,
    testfall TEXT NOT NULL,
    speichern_ok INTEGER NOT NULL,
    struktur_ok INTEGER,
    oeffnen_ok INTEGER,
    inhalt_ok INTEGER,
    groesse INTEGER,
    sha256 TEXT,
    fehlerkategorie TEXT,
    details TEXT
)"""

FALLE = {
    "neu": "Erste Zeile\nZweite Zeile mit äöü ß",
    "leer": "",
    "unicode": "Grüße – „Ärger“ 𝄞 ✓ 日本語 Ωmega",
    "gross": "\n".join(f"Absatz {i}: Lorem ipsum dolor sit amet." for i in range(5000)),
}


def _db_pfad() -> str:
    basis = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(basis, "lunivo-writer", "speicherpruefung.sqlite3")


def _kategorie(e: BaseException) -> str:
    text = str(e)
    for schluessel, kat in (("Platz", "speicherplatz"), ("Schreibrechte", "rechte"), ("beschädigt", "struktur"),
                            ("Umwandl", "umwandler"), ("gespeichert", "sperre")):
        if schluessel in text:
            return kat
    return type(e).__name__


def pruefen(formate: list[str], db: str) -> list[tuple]:
    from PySide6.QtGui import QTextCursor, QTextDocument
    from PySide6.QtWidgets import QApplication
    from lunivo_writer.models.page import PageSettings
    from lunivo_writer.services import file_service as formats
    from lunivo_writer.services import sicher_schreiben as S
    from lunivo_writer.services.integrations import libreoffice

    app = QApplication.instance() or QApplication([])  # noqa: F841 — QTextDocument braucht eine Anwendung
    lauf = uuid.uuid4().hex[:12]
    zeilen = []
    with tempfile.TemporaryDirectory(prefix="lunivo-speicherpruefung-") as ordner:
        S.sicherungs_ordner = lambda: os.path.join(ordner, "_sicherungen")   # Sicherungskopien bleiben im Temp-Ordner
        for endung in formate:
            if endung in (".doc", ".rtf") and not libreoffice.verfuegbar():
                zeilen.append((uuid.uuid4().hex[:12], lauf, time.strftime("%Y-%m-%dT%H:%M:%S"), endung, "alle", 0, None, None,
                               None, None, None, "umwandler", "LibreOffice nicht installiert"))
                continue
            for fall, text in list(FALLE.items()) + [("mehrfach", "Fassung 5")]:
                name = ("Übersicht ✓ " if fall == "unicode" else "") + fall + endung
                pfad = os.path.join(ordner, name)
                ergebnis = dict(speichern_ok=0, struktur_ok=None, oeffnen_ok=None, inhalt_ok=None, groesse=None, sha=None, kat=None, det=None)
                try:
                    for i in range(6 if fall == "mehrfach" else 1):
                        d = QTextDocument()
                        QTextCursor(d).insertText(f"Fassung {i}" if fall == "mehrfach" else text)
                        formats.save(pfad, d, PageSettings())
                    ergebnis["speichern_ok"] = 1
                    with open(pfad, "rb") as fh:
                        daten = fh.read()
                    ergebnis["groesse"], ergebnis["sha"] = len(daten), hashlib.sha256(daten).hexdigest()
                    S.pruefe_format(pfad, endung)
                    ergebnis["struktur_ok"] = 1
                    gelesen = formats.load(pfad).doc.toPlainText()
                    ergebnis["oeffnen_ok"] = 1
                    ergebnis["inhalt_ok"] = int(gelesen.strip("\n") == text.strip("\n"))
                    if not ergebnis["inhalt_ok"]:
                        ergebnis["kat"], ergebnis["det"] = "inhalt", f"Zeichen gelesen: {len(gelesen)}, erwartet: {len(text)}"
                except Exception as e:                    # jeder Fehler wird protokolliert, der Lauf geht weiter
                    for k in ("struktur_ok", "oeffnen_ok", "inhalt_ok"):
                        if ergebnis[k] is None and ergebnis["speichern_ok"]:
                            ergebnis[k] = 0
                            break
                    ergebnis["kat"], ergebnis["det"] = _kategorie(e), str(e)[:500]
                zeilen.append((uuid.uuid4().hex[:12], lauf, time.strftime("%Y-%m-%dT%H:%M:%S"), endung, fall,
                               ergebnis["speichern_ok"], ergebnis["struktur_ok"], ergebnis["oeffnen_ok"], ergebnis["inhalt_ok"],
                               ergebnis["groesse"], ergebnis["sha"], ergebnis["kat"], ergebnis["det"]))
    os.makedirs(os.path.dirname(os.path.abspath(db)), exist_ok=True)
    with sqlite3.connect(db) as con:
        con.execute(TABELLE)
        con.executemany("INSERT INTO pruefung VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", zeilen)
    return zeilen


def bericht(zeilen: list[tuple]) -> str:
    """Kurzer Markdown-Bericht über einen Lauf."""
    zeichen = {1: "ja", 0: "**nein**", None: "–"}
    out = ["| Format | Testfall | Speichern | Struktur | Öffnen | Inhalt | Größe | Fehler |", "|---|---|---|---|---|---|---|---|"]
    for z in zeilen:
        out.append(f"| {z[3]} | {z[4]} | {zeichen[z[5]]} | {zeichen[z[6]]} | {zeichen[z[7]]} | {zeichen[z[8]]} | "
                   f"{z[9] if z[9] is not None else '–'} | {z[11] or ''} |")
    fehler = sum(1 for z in zeilen if z[11])
    out.append(f"\n{len(zeilen)} Prüfungen, davon {fehler} mit Fehler.")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=_db_pfad(), help="SQLite-Datei für das Prüfprotokoll")
    ap.add_argument("--formate", default=".docx,.txt,.odt,.rtf,.doc", help="Komma-Liste der Endungen")
    a = ap.parse_args()
    zeilen = pruefen([f.strip() for f in a.formate.split(",") if f.strip()], a.db)
    print(bericht(zeilen))
    print(f"\nProtokoll: {a.db}")
    return 1 if any(z[11] for z in zeilen) else 0


if __name__ == "__main__":
    sys.exit(main())
