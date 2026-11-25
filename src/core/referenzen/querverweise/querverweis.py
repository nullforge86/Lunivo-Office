"""Querverweise: die möglichen Ziele (nummerierte Absätze, Überschriften, Textmarken, Noten, Beschriftungen), die Textmarke am Ziel und das Einfügen."""
from __future__ import annotations

import re

from core.suche.textsuche.suche import offset_zu_position
from core.dokument.dokument import Auswahl
from core.formatvorlagen.formatvorlagen import ueberschriftsebene
from core.listen.listen import listenmarken, nummer_text
from core.verzeichnisse.abbildungsverzeichnis.beschriftung import beschriftungen_liste, seq_lauf
from core.referenzen.querverweise.querverweis_text import querverweis_text_bilden
from core.referenzen.querverweise.textmarke import lesezeichen_liste

# Verweistyp → was eingefügt werden kann („Verweisen auf“), in der Reihenfolge des Fensters
VERWEISTYPEN = ["Nummeriertes Element", "Überschrift", "Textmarke", "Fußnote", "Endnote", "Abbildung", "Tabelle", "Gleichung"]
VERWEISEN_AUF = {
    "Nummeriertes Element": [("seite", "Seitenzahl"), ("nummer", "Absatznummer"), ("text", "Absatztext"), ("obenunten", "Oben/unten")],
    "Überschrift": [("text", "Überschriftentext"), ("seite", "Seitenzahl"), ("nummer", "Überschriftennummer"), ("obenunten", "Oben/unten")],
    "Textmarke": [("text", "Textmarkeninhalt"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
    "Fußnote": [("nummer", "Fußnotennummer"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
    "Endnote": [("nummer", "Endnotennummer"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
}
_BESCHRIFTUNG_AUF = [("text", "Vollständige Beschriftung"), ("nummer", "Nur Bezeichnung und Nummer"), ("nur_text", "Nur Beschriftungstext"),
                     ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")]


def verweisen_auf(art: str) -> list[tuple[str, str]]:
    return VERWEISEN_AUF.get(art, _BESCHRIFTUNG_AUF)


_AUFZAEHLUNG = ("•", "◦", "▪", "–", "-")                 # Listenzeichen ohne Nummer: kein Ziel für einen Querverweis


def _ziele_absaetze(k) -> list[dict]:
    """Überschriften und nummerierte Absätze."""
    d = k.sitzung.dokument
    marken = listenmarken(d)
    z, n = [], 0
    for a in d.absaetze():
        text = a.text().strip()
        nummer = marken.get(a.id, "").strip()
        ort = {"pos": n, "block": a.id, "von": n, "bis": n + a.laenge, "nummer": nummer}
        if ueberschriftsebene(d, a) and text:
            z.append({"art": "Überschrift", "text": text, **ort})
        elif nummer and not nummer.startswith(_AUFZAEHLUNG) and text:
            z.append({"art": "Nummeriertes Element", "text": f"{nummer} {text}", **ort, "inhalt": text})
        n += a.laenge + 1
    return z


def _bezeichnung_nummer(a) -> str:
    """„Abbildung 2“ — der Text der Beschriftung bis einschließlich der Nummer."""
    f = seq_lauf(a)
    return a.text()[:f[0] + len(f[1].text)].strip() if f else ""


def _beschriftungstext(a) -> str:
    """Der Text hinter der Nummer, ohne Doppelpunkt."""
    f = seq_lauf(a)
    rest = a.text()[f[0] + len(f[1].text):] if f else a.text()
    return re.sub(r"^\s*[:.–-]?\s*", "", rest).strip()


def _ziele_beschriftungen(k) -> list[dict]:
    d = k.sitzung.dokument
    z = []
    for k in beschriftungen_liste(k):
        a = k.sitzung._absatz(k["block"])
        z.append({"art": k["label"], "text": k["text"], "pos": k["pos"], "block": a.id, "von": k["pos"], "bis": k["pos"] + a.laenge,
                  "nummer": _bezeichnung_nummer(a) or k["text"], "inhalt": _beschriftungstext(a)})
    return z


def _ziele_textmarken(k) -> list[dict]:
    marken = lesezeichen_liste(k, versteckte=False)
    text = k.sitzung.text() if marken else ""
    return [{"art": "Textmarke", "text": d["name"], "pos": d["von"], "name": d["name"], "inhalt": text[d["von"]:d["bis"]].replace("\n", " ")} for d in marken]


def _ziele_noten(k) -> list[dict]:
    """Fußnoten (1, 2, …) und Endnoten (i, ii, …) in Textreihenfolge."""
    z = []
    zaehler = {"f": 0, "e": 0}
    for n in k.noten_stellen():
        zaehler[n["art"]] += 1
        nr = str(zaehler[n["art"]]) if n["art"] == "f" else nummer_text("roem_klein", zaehler[n["art"]])
        text = ((k.noten or {}).get(n["art"], {}) or {}).get(n["id"], "")
        z.append({"art": "Fußnote" if n["art"] == "f" else "Endnote", "text": f"{nr} {text}".strip(), "pos": n["von"], "von": n["von"], "bis": n["bis"], "nummer": nr})
    return z


def querverweis_ziele(k) -> list[dict]:
    """Mögliche Ziele: nummerierte Absätze, Überschriften, Textmarken, Fuß- und Endnoten, Beschriftungen.
    Jedes Ziel: art, text (Anzeige), pos, von/bis (Bereich für die Textmarke), nummer (wenn es eine hat)."""
    return _ziele_absaetze(k) + _ziele_beschriftungen(k) + _ziele_textmarken(k) + _ziele_noten(k)


def marke_sichern(k, ziel: dict) -> str:
    """Name der Textmarke am Ziel. Fehlt eine, bekommt der Bereich des Ziels eine verborgene Textmarke „_Ref…“."""
    if "name" in ziel:
        return ziel["name"]
    von, bis = ziel["von"], ziel["bis"]
    if bis <= von:
        bis = von + 1
    vorhanden = set()
    for d in lesezeichen_liste(k):
        vorhanden.add(d["name"])
        if d["von"] == von and d["bis"] == bis and d["name"].startswith(("_Ref", "Ziel_")):
            return d["name"]
    n = 1
    while f"_Ref{n:06d}" in vorhanden:
        n += 1
    name = f"_Ref{n:06d}"
    dok = k.sitzung.dokument
    k.aendern(lambda s: s.textmarke_setzen(name, Auswahl(offset_zu_position(dok, von), offset_zu_position(dok, bis))))
    return name


def querverweis_text(k, ziel: dict, wie: str, oben_unten: bool = False) -> str:
    seitenzahl = None
    if wie == "seite":
        seitenzahl = k.seiten_von([ziel["pos"]])[0]
    return querverweis_text_bilden(ziel, wie, k.position(), seitenzahl, oben_unten)


def querverweis_einfuegen(k, ziel: dict, wie: str, *, link: bool = True, oben_unten: bool = False) -> None:
    """Querverweis an der Schreibmarke (siehe ``querverweis_text``); ``link`` macht ihn zum internen Hyperlink (Strg+Klick)."""
    text = querverweis_text(k, ziel, wie, oben_unten)
    name = marke_sichern(k, ziel) if link else ""

    def f(s):
        with s.gruppe("Querverweis"):
            if name:
                s.querverweis_einfuegen(name, text)
            else:
                s.text_einfuegen(text)
            s.text_einfuegen(" ", format={})
    k.aendern(f)
