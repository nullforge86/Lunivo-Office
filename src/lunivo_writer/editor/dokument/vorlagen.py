"""Die mitgelieferten Gerüste (Brief, Bewerbung, Lebenslauf …) und eigene Vorlagen.

Ein Gerüst ist eine Liste von Zeilen (aus ressourcen/vorlagenmuster.json):
    «Wort»  Lücke         ''  Leerzeile        '!Text'  fett        '#Text'  Titel
    '>Text' rechtsbündig  '@absender' / '@absender2' / '@ortdatum' / '@name' / @mail  aus den Benutzerdaten
Zeilen ohne Leerzeile dazwischen werden zu einem Absatz mit Zeilenumbrüchen.
"""
from __future__ import annotations

import json
import os
from lunivo_writer.infrastruktur.pfade import ressourcen_pfade as paths
from lunivo_writer.infrastruktur.pfade import pfade
import re


LUECKE = re.compile("«[^«»]*»")
LUECKE_FARBE = "#fff3bf"


def muster() -> list[dict]:
    pfad = os.path.join(paths.RESSOURCEN, "vorlagenmuster.json")
    with open(pfad, encoding="utf-8") as fh:
        return json.load(fh)


def _benutzer_zeilen(b: dict, mit_name: bool) -> list[str]:
    z = []
    if mit_name:
        z.append(b.get("name") or "«Dein Name»")
    z.append(b.get("strasse") or "«Straße und Hausnummer»")
    z.append(b.get("plz_ort") or "«PLZ und Ort»")
    return z


def _ersetze(text: str, b: dict) -> str:
    return text.replace("@mail", b.get("mail") or "«E-Mail»").replace("@name", b.get("name") or "«Dein Name»")


def geruest_schreiben(s, zeilen: list[str], benutzer: dict, heute: str) -> None:
    """Schreibt das Gerüst einer Dokumentvorlage über die zentrale Bearbeitung (``Bearbeitungssitzung`` ``s``) in das leere Dokument: Absätze,
    Auszeichnungen und die Lücken « … » zum Ausfüllen. Ein Schritt für Rückgängig."""
    absaetze: list = []
    puffer: list = []

    def leeren():
        nonlocal puffer
        if puffer:
            absaetze.append(("text", puffer)); puffer = []
    for z in zeilen:
        if z == "":
            leeren(); absaetze.append(("leer", []))
        elif z[0] in "!#>":
            leeren(); absaetze.append(({"!": "fett", "#": "titel", ">": "rechts"}[z[0]], [_ersetze(z[1:], benutzer)]))
        elif z == "@absender":
            leeren(); absaetze.append(("text", _benutzer_zeilen(benutzer, True)))
        elif z == "@absender2":
            puffer.extend(_benutzer_zeilen(benutzer, False))
        elif z == "@ortdatum":
            leeren(); absaetze.append(("rechts", [f"{benutzer.get('ort') or '«Ort»'}, {heute}"]))
        elif z == "@name":
            leeren(); absaetze.append(("text", [benutzer.get("name") or "«Dein Name»"]))
        else:
            puffer.append(_ersetze(z, benutzer))
    leeren()
    with s.gruppe("Vorlage"):
        for i, (art, zs) in enumerate(absaetze):
            if i:
                s.absatz_teilen()
            zeichen = {"fett": {"fett": True}, "titel": {"fett": True, "groesse_pt": 20.0}}.get(art, {})
            s.absatzformat_anwenden({"ausrichtung": "rechts"} if art == "rechts" else {"abstand_nach": 6.0} if art == "titel" else {}, ersetzen=True)
            s.absatz_zeichenformat_anwenden(zeichen, ersetzen=True)
            text = " ".join(zs)
            if text:
                s.text_einfuegen(text, format=zeichen)
        s.setze_auswahl(s.dokument.anfang())


# ---- eigene Vorlagen -------------------------------------------------------------------------------------------
ENDUNGEN = (".docx", ".dotx", ".odt", ".ott", ".txt")


def vorlagenordner(settings) -> str:
    return settings.get("vorlagen/ordner", "") or pfade.vorlagen_dir()


def rubriken(ordner: str) -> tuple[dict[str, list[str]], list[str]]:
    """Der Vorlagenordner nach Rubriken: jeder Unterordner ist eine Rubrik (Name → Dateien); lose Dateien liegen im Ordner selbst."""
    rub: dict[str, list[str]] = {}
    try:
        for f in sorted(os.listdir(ordner)):
            pfad = os.path.join(ordner, f)
            if os.path.isdir(pfad) and not f.startswith("."):
                rub[f] = eigene_vorlagen(pfad)
    except OSError:
        pass
    return rub, eigene_vorlagen(ordner)


def eigene_vorlagen(ordner: str) -> list[str]:
    try:
        return sorted(os.path.join(ordner, f) for f in os.listdir(ordner) if f.lower().endswith(ENDUNGEN))
    except OSError:
        return []
