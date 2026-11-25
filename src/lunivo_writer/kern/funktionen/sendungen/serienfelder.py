"""Seriendruckfelder im Text: finden, einfügen (Feld, Adressblock, Regel, „Nächster Datensatz“) und hervorheben. Die Einfügefunktionen arbeiten auf einer
Bearbeitungssitzung (``s``); wie die Änderung in den Editor gelangt, entscheidet der Aufrufer."""
from __future__ import annotations

from lunivo_writer.kern.dokument.dokument import Dokument
from lunivo_writer.kern.funktionen.sendungen.konstanten import FELD, FELD_FARBE, NAECHSTER, REGEL_FARBE


def felder_im_text(dok: Dokument) -> list[str]:
    return sorted(set(m.group(1) for m in FELD.finditer(dok.text())))


def feld_einfuegen(s, name: str) -> None:
    """Fügt ``{{name}}`` mit Feldfarbe ein; dahinter geht es ohne Feldfarbe weiter."""
    with s.gruppe("Seriendruckfeld"):
        s.text_einfuegen("{{" + name + "}}", format={"marker": FELD_FARBE})
        s.tippformat = {}


def adressblock_einfuegen(s, was: str) -> None:
    with s.gruppe("Adressblock"):
        def feld(n):
            s.text_einfuegen("{{" + n + "}}", format={"marker": FELD_FARBE})

        def text(t):
            s.text_einfuegen(t, format={})
        if was in ("adresse", "beides"):
            feld("Name"); text(" "); feld("Straße"); text(" "); feld("PLZ"); text(" "); feld("Ort")
        if was == "beides":
            text("\n\n")
        if was in ("gruss", "beides"):
            text("Sehr geehrte"); feld("Anrede"); text(" "); feld("Name"); text(",")


def regel_einfuegen(s, feld: str, wert: str, dann: str, sonst: str) -> None:
    regel = "|".join(x.replace("|", "/") for x in (feld, wert, dann, sonst))
    s.text_einfuegen(dann, format={"marker": REGEL_FARBE, "regel": regel})


def felder_hervorheben(s, an: bool) -> None:
    """Hintergrund der Felder {{…}} an oder aus (ein Schritt)."""
    with s.gruppe("Seriendruckfelder hervorheben"):
        for fund in s.suche(r"\{\{\s*[^{}]+?\s*\}\}", regex=True, gross_klein=True):
            s.zeichenformat_anwenden({"marker": FELD_FARBE if an else None}, fund)


def naechster_einfuegen(s) -> None:
    """Feld „Nächster Datensatz“: dahinter füllt der nächste Satz die Felder (z. B. mehrere Etiketten auf einem Blatt)."""
    feld_einfuegen(s, NAECHSTER)
