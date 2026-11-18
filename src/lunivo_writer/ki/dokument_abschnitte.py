"""Dateien für die Dokumentensuche in Abschnitte zerlegen: ``lesen(pfad) → [(ort, titel, text)]``.

DOCX, ODT, RTF und TXT laufen über die vorhandenen Leser von Lunivo (``dienste.datei_dienst``); Überschriften des Dokuments bestimmen die
Abschnitte. PDF liest ``pypdf`` seitenweise (der Ort ist „Seite n“). Gescannte PDFs ohne Text und PDF-Tabellen bleiben außen vor — dafür
wäre Docling als optionales Extra nötig. Kennwortgeschützte Dateien werden übersprungen."""
from __future__ import annotations

import os

from lunivo_writer.ki.dokumentensuche import abschnitte_bilden


def _aus_textdokument(doc) -> list[tuple[str, str, str]]:
    zeilen = []
    b = doc.firstBlock()
    while b.isValid():
        zeilen.append((b.blockFormat().headingLevel(), b.text()))
        b = b.next()
    return [(titel, titel, text) for titel, text in abschnitte_bilden(zeilen)]


def _aus_pdf(pfad: str) -> list[tuple[str, str, str]]:
    from pypdf import PdfReader
    r = PdfReader(pfad)
    if r.is_encrypted:
        return []
    aus = []
    for n, seite in enumerate(r.pages, 1):
        text = (seite.extract_text() or "").strip()
        if not text:
            continue
        absaetze = [(0, a) for a in text.split("\n\n")] if "\n\n" in text else [(0, z) for z in text.split("\n")]
        for _t, teil in abschnitte_bilden(absaetze):
            aus.append((f"Seite {n}", f"Seite {n}", teil))
    return aus


def _aus_txt(pfad: str) -> list[tuple[str, str, str]]:
    with open(pfad, "rb") as fh:
        roh = fh.read()
    for kodierung in ("utf-8-sig", "cp1252"):
        try:
            text = roh.decode(kodierung)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = roh.decode("latin-1")
    absaetze = [(0, a) for a in text.replace("\r\n", "\n").split("\n\n")]
    return [(f"Abschnitt {n}", f"Abschnitt {n}", t) for n, (_ti, t) in enumerate(abschnitte_bilden(absaetze), 1)]


def lesen(pfad: str) -> list[tuple[str, str, str]]:
    e = os.path.splitext(pfad)[1].lower()
    if e == ".pdf":
        return _aus_pdf(pfad)
    if e == ".txt":
        return _aus_txt(pfad)
    from lunivo_writer.dienste import datei_dienst
    return _aus_textdokument(datei_dienst.load(pfad).doc)
