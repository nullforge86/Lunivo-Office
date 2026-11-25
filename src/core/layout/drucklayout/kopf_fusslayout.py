"""Kopf- und Fußzeilen der Seiten, ohne Qt: aus der Seiteneinrichtung des Abschnitts den gesetzten Text je Seite, mit Seitenzahl in der gewählten
Zahlenart (auch mit Kapitelnummer), Seitenzahl-Gesamt und der Wahl zwischen erster, gerader und gewöhnlicher Zeile.

Ergebnis sind ``Platz``-Einträge der Art ``kopfzeile`` und ``fusszeile`` auf jeder Seite; ``block_id`` ist der Index des Abschnitts, ``daten`` der
gesetzte ``Absatzsatz`` (sein Text enthält die ersetzten Platzhalter).
"""
from __future__ import annotations

from core.dokument.dokument import Dokument
from core.formatvorlagen.formatvorlagen import ueberschriftsebene
from core.listen.listen import nummer_text
from core.geometrie import Rect, mm_to_px
from core.textsatz.engine import TextLayoutEngine
from core.textsatz.paragraph import absatz_setzen
from core.layout.drucklayout import formatwerte as F
from core.layout.drucklayout.ergebnis import Ergebnis, Platz

AUSRICHTUNG = {"left": "left", "center": "center", "right": "right"}


def _ausrichtung(align: str, nummer: int) -> str:
    """links/mitte/rechts, oder aussen/innen: auf ungeraden Seiten steht „außen“ rechts, auf geraden links."""
    if align in ("aussen", "innen"):
        rechts = (align == "aussen") == (nummer % 2 == 1)
        return "right" if rechts else "left"
    return AUSRICHTUNG.get(align, "center")


def _kapitelnummern(dok: Dokument, erg: Ergebnis, ebene: int) -> dict:
    """Seitenindex → Nummer der letzten Überschrift der Ebene ``ebene``, die auf oder vor der Seite steht (0: noch keine)."""
    seite_von_absatz = {a.id: erg.seite_von(a.id) for a in dok.absaetze() if a.id in erg.absaetze}
    stand, je_seite, letzter_index = 0, {}, -1
    for a in dok.absaetze():
        s = seite_von_absatz.get(a.id)
        if s is None:
            continue
        for i in range(letzter_index + 1, s):
            je_seite.setdefault(i, stand)
        letzter_index = max(letzter_index, s - 1)
        if ueberschriftsebene(dok, a) == ebene:
            stand += 1
        je_seite[s] = stand
    for i in range(len(erg.seiten)):
        je_seite.setdefault(i, stand)
    return je_seite


def kopf_fuss_setzen(engine: TextLayoutEngine, dok: Dokument, erg: Ergebnis) -> None:
    """Setzt Kopf- und Fußzeile jeder Seite und trägt sie als Plätze ein."""
    gesamt = len(erg.seiten)
    erste_im_abschnitt: dict = {}
    for s in erg.seiten:
        erste_im_abschnitt.setdefault(s.abschnitt, s.index)
    kapitel: dict = {}
    for seite in erg.seiten:
        p = seite.einrichtung
        if p is None:
            continue
        blatt = seite.index - erste_im_abschnitt[seite.abschnitt] + 1
        kopf, fuss = p.kopf_fuss(blatt, seite.nummer)
        if p.kapitel_ebene and p.kapitel_ebene not in kapitel:
            kapitel[p.kapitel_ebene] = _kapitelnummern(dok, erg, p.kapitel_ebene)
        zahl = nummer_text(p.seiten_format, seite.nummer)
        if p.kapitel_ebene:
            k = kapitel[p.kapitel_ebene].get(seite.index, 0)
            if k:
                zahl = f"{nummer_text(p.seiten_format, k)}{p.kapitel_trenner}{zahl}"
        breite = p.content_width_px
        links = mm_to_px(p.margin_left_mm)
        for art, zeile in (("kopfzeile", kopf), ("fusszeile", fuss)):
            if zeile.is_empty():
                continue
            text = zeile.text.replace("{PAGE}", zahl).replace("{PAGES}", str(gesamt))
            z = {"schrift": zeile.fmt.get("family"), "groesse_pt": zeile.fmt.get("size_pt"), "fett": zeile.fmt.get("bold"),
                 "kursiv": zeile.fmt.get("italic"), "unterstrichen": zeile.fmt.get("underline"), "farbe": zeile.fmt.get("color")}
            z = {k: v for k, v in z.items() if v is not None}
            z = {**{k: v for k, v in dok.standardformat.items() if k in ("schrift", "groesse_pt")}, **z}
            grund = dok.standardformat.get("kopffuss") or {}                            # Zeilenabstand und Abstand nach dem Absatz der Grundvorlage
            z_art, z_wert = F.zeilenabstand(grund)
            satz = absatz_setzen(engine, [(text, F.schrift(z), F.stil(z))], breite, _ausrichtung(zeile.align, seite.nummer), zeilen_art=z_art, zeilen_wert=z_wert)
            if art == "kopfzeile":
                y = mm_to_px(p.kopf_abstand_mm)
            else:
                y = mm_to_px(p.height_mm) - mm_to_px(p.fuss_abstand_mm) - F.abstaende(grund)[1] - satz.hoehe
            seite.plaetze.append(Platz(art, Rect(links, y, breite, satz.hoehe), seite.abschnitt, daten=satz))
