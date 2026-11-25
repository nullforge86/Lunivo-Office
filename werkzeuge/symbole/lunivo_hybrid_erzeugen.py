#!/usr/bin/env python3
"""Lunivo Hybrid — eigene, unabhängige Iconfamilie (32 × 32, eigene Zeichnung, keine fremden Vorlagen).

Formsprache: klare ruhige Konturen, runde Enden, gefaltete Ecke bei Seiten, zweifarbig (Kontur + Akzentfläche).
Erzeugt je Symbol eine hell/dunkel-Variante und eine Übersichtsseite.
Starten:  python3 werkzeuge/symbole/lunivo_hybrid_erzeugen.py
"""
from __future__ import annotations

import base64
import json
import math
import os
import sys

ZIEL = os.path.join(os.path.dirname(__file__), "..", "..", "ressourcen", "icons", "lunivo-hybrid")

PALETTEN = {
    "hell": dict(ink="#243062", paper="#F6F8FF", soft="#DCE8FF",
                 blue=("#5BB4FF", "#2F7BFF"), purple=("#A987FF", "#6F45E0"), green=("#8BDC6E", "#38AE4E"),
                 yellow=("#FFD95A", "#FFAE1A"), red=("#FF8A78", "#E5483F")),
    "dunkel": dict(ink="#F3F6FF", paper="#3C4B88", soft="#51629F", sw=1.15,
                   blue=("#8AD0FF", "#4C98FF"), purple=("#C4A8FF", "#9168FF"), green=("#A8EE8C", "#52CC68"),
                   yellow=("#FFE680", "#FFC13A"), red=("#FFA192", "#FF6258")),
}
AKZENTE = ("blue", "purple", "green", "yellow", "red")


class Stift:
    """Löst Farbnamen auf: Kontur- und Flächenfarben aus der Palette."""

    def __init__(self, pal):
        self.p = pal

    def fl(self, n):          # Füllung
        if n in AKZENTE:
            return f"url(#{n})"
        return {"paper": self.p["paper"], "soft": self.p["soft"], "ink": self.p["ink"], "white": "#FFFFFF", "none": "none"}[n]

    def st(self, n):          # Kontur
        if n in AKZENTE:
            return self.p[n][1]
        return {"ink": self.p["ink"], "paper": self.p["paper"], "soft": self.p["soft"], "white": "#FFFFFF"}[n]


def el(tag, stift, fill="none", stroke="ink", sw=1.8, extra="", **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<{tag} {attrs} fill="{stift.fl(fill)}" stroke="{stift.st(stroke) if stroke else "none"}" stroke-width="{round(sw * stift.p.get("sw", 1), 2)}" {extra}/>'


def pf(s, d, fill="none", stroke="ink", sw=1.8):
    return el("path", s, fill, stroke, sw, d=d)


def rc(s, x, y, w, h, r=2, fill="none", stroke="ink", sw=1.8, extra=""):
    return el("rect", s, fill, stroke, sw, extra, x=x, y=y, width=w, height=h, rx=r)


def kr(s, cx, cy, r, fill="none", stroke="ink", sw=1.8):
    return el("circle", s, fill, stroke, sw, cx=cx, cy=cy, r=r)


# ---------- Bausteine ----------
SEITE = "M8 3.5h11l6 6v17a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2v-21a2 2 0 0 1 2-2z"
ECKE = "M19 3.5v4.5a1.5 1.5 0 0 0 1.5 1.5H25"


def seite(s, fill="paper"):
    return pf(s, SEITE, fill) + pf(s, ECKE)


def linien(s, ys, x0=5, x1=27, farbe="ink", sw=1.9, kurz=None):
    out = ""
    for i, y in enumerate(ys):
        e = x1 if not kurz or i not in kurz else kurz[i]
        out += pf(s, f"M{x0} {y}H{e}", stroke=farbe, sw=sw)
    return out


def lupe(s, mit=""):
    return kr(s, 13.5, 13.5, 8.5, "paper") + pf(s, "M20 20l7 7", sw=2.6) + mit


def sprechblase(s, fill="paper"):
    return pf(s, "M6 5h20a2.5 2.5 0 0 1 2.5 2.5v13a2.5 2.5 0 0 1-2.5 2.5H15l-6 5v-5H6a2.5 2.5 0 0 1-2.5-2.5v-13A2.5 2.5 0 0 1 6 5z", fill)


def tabelle(s, x=4, y=6, w=24, h=20, kopf="blue", spalten=2, zeilen=2):
    out = rc(s, x, y, w, h, 3, "paper")
    out += pf(s, f"M{x} {y + 5}V{y + 3}a3 3 0 0 1 3-3h{w - 6}a3 3 0 0 1 3 3v2z".replace(f"M{x} {y + 5}", f"M{x} {y + 5.5}"), kopf, "ink")
    for i in range(1, spalten + 1):
        xx = x + w * i / (spalten + 1)
        out += pf(s, f"M{xx:.1f} {y + 5.5}V{y + h}", sw=1.4)
    for i in range(1, zeilen + 1):
        yy = y + 5.5 + (h - 5.5) * i / (zeilen + 1)
        out += pf(s, f"M{x} {yy:.1f}H{x + w}", sw=1.4)
    return out


def zahnrad(s):
    pts, n = [], 8
    for i in range(n):
        a = 2 * math.pi * i / n
        for da, r in ((-0.20, 10.2), (-0.12, 13), (0.12, 13), (0.20, 10.2)):
            pts.append((16 + r * math.cos(a + da), 16 + r * math.sin(a + da)))
    d = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
    return pf(s, d, "soft") + kr(s, 16, 16, 4.2, "blue")


def pfeil(s, d, farbe="purple"):
    return pf(s, d, stroke=farbe, sw=2.2)


# ---------- Symbole ----------
def ikonen(s):
    I = {}
    # Datei & Dokumente
    I["neu"] = seite(s) + pf(s, "M22 19v9M17.5 23.5h9", stroke="blue", sw=2.6)
    I["oeffnen"] = pf(s, "M3.5 9a2 2 0 0 1 2-2h6l3 3h11a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2h-20a2 2 0 0 1-2-2z", "blue") + pf(s, "M5 14.5h22", sw=1.6, stroke="ink")
    I["speichern"] = (pf(s, "M5 6a2 2 0 0 1 2-2h15l5 5v16a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z", "purple")
                      + pf(s, "M10 4v7h10V4", "paper") + rc(s, 9, 18, 14, 10, 1.5, "paper") + pf(s, "M12 22h8", sw=1.4))
    I["speichern_unter"] = (pf(s, "M4 6a2 2 0 0 1 2-2h13l5 5v9.5H4z", "purple") + pf(s, "M4 15.5V24a2 2 0 0 0 2 2h7", "purple")
                            + pf(s, "M8 4v6h9V4", "paper")
                            + pf(s, "M24.5 15l4 4-9.5 9.5-4.6.6.6-4.6z", "paper", "ink", 1.9) + pf(s, "M22 17.5l4 4", stroke="purple", sw=1.8))
    I["drucken"] = (pf(s, "M9 12V4.5h14V12", "paper") + rc(s, 3.5, 12, 25, 11, 3, "blue") + rc(s, 9, 18, 14, 9.5, 1.5, "paper")
                    + pf(s, "M12 22h8M12 25h5", sw=1.4) + pf(s, "M24.5 15.5h.01", sw=2.4, stroke="paper"))
    I["pdf_exportieren"] = (seite(s) + rc(s, 3, 15.5, 22, 10, 2.2, "red", "red", 1)
                            + pf(s, "M7 24v-6.5h2.2a1.9 1.9 0 0 1 0 3.8H7M12.5 17.5v6.5h1.6a3.2 3.2 0 0 0 0-6.5zM18 24v-6.5h3.5M18 20.6h2.8", stroke="paper", sw=1.5))
    # Zwischenablage
    I["ausschneiden"] = (pf(s, "M11.5 21.5L22.5 4.5M20.5 21.5L9.5 4.5") + kr(s, 9, 24.5, 4, "none", "purple", 2.4) + kr(s, 23, 24.5, 4, "none", "purple", 2.4))
    I["kopieren"] = (pf(s, "M12 5h8l5 5v11a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z", "blue") + pf(s, "M20 5v4a1 1 0 0 0 1 1h4")
                     + pf(s, "M22 25v1a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V12a2 2 0 0 1 2-2h1", "paper"))
    brett = rc(s, 5.5, 6, 21, 22, 3, "paper") + rc(s, 11, 3, 10, 6, 2, "blue")
    I["einfuegen"] = brett + linien(s, [15, 19.5, 24], 10, 22, "ink", 1.6, {2: 17})
    I["inhalte_einfuegen"] = brett + linien(s, [14, 18], 10, 22, "ink", 1.6) + pf(s, "M11.5 23l4 4 6.5-7", stroke="purple", sw=2.4)
    # Schrift & Text
    I["fett"] = pf(s, "M10 5v22M10 5h7a5 5 0 0 1 0 10h-7M10 15h8a6 6 0 0 1 0 12h-8", sw=3.2)
    I["kursiv"] = pf(s, "M13 5h11M8 27h11M18.5 5L13.5 27", sw=2.6)
    I["unterstrichen"] = pf(s, "M9 5v10a7 7 0 0 0 14 0V5", sw=2.6) + pf(s, "M7 27.5h18", stroke="purple", sw=2.8)
    I["durchgestrichen"] = pf(s, "M22 9.5c-.8-2.8-3.5-4.5-6.3-4.5-3.3 0-5.7 1.8-5.7 4.3 0 5.3 12 3.3 12 8.7 0 2.7-2.6 4.8-6.2 4.8-3 0-5.7-1.4-6.6-4.3", sw=2.6) + pf(s, "M5 16h22", stroke="purple", sw=2.8)
    I["textfarbe"] = pf(s, "M8.5 22.5L16 5l7.5 17.5M11.2 16.5h9.6", sw=2.6) + rc(s, 6.5, 25, 19, 3.6, 1.8, "red", "red", 1)
    I["markieren"] = (pf(s, "M19 4l9 9-11.5 11.5-4-.5-5.5-5.5.5-4z", "yellow") + pf(s, "M8 19l-2.5 5.5L11 22") + pf(s, "M5 28.5h12", stroke="yellow", sw=2.6))
    # Absatz & Listen
    for n, kw in (("links", {}), ("zentriert", {}), ("rechts", {}), ("blocksatz", {})):
        pass
    I["links"] = linien(s, [7, 13, 19, 25], 5, 27, kurz={1: 19, 3: 14})
    I["zentriert"] = "".join(pf(s, f"M{a} {y}H{b}", sw=1.9) for y, a, b in ((7, 5, 27), (13, 9, 23), (19, 5, 27), (25, 10, 22)))
    I["rechts"] = "".join(pf(s, f"M{a} {y}H27", sw=1.9) for y, a in ((7, 5), (13, 13), (19, 5), (25, 18)))
    I["blocksatz"] = linien(s, [7, 13, 19, 25])
    I["aufzaehlung"] = "".join(kr(s, 6.5, y, 2, "blue", "blue", 1) + pf(s, f"M12 {y}H27", sw=1.9) for y in (8, 16, 24))
    I["nummerierung"] = (pf(s, "M4.5 7.5l2-1.5v6.5M4.5 12.5h4", stroke="purple", sw=1.6)
                         + pf(s, "M4.8 15.5a2 2 0 0 1 4 0c0 1.6-4 3-4 4.5h4", stroke="purple", sw=1.6)
                         + pf(s, "M4.8 23.2h3.8l-2 2.2a2 2 0 1 1-1.8 3", stroke="purple", sw=1.6)
                         + pf(s, "M13 9H27M13 17H27M13 25H27", sw=1.9))
    # Tabelle
    I["tabelle_einfuegen"] = (tabelle(s, 3, 5, 21, 18, spalten=2, zeilen=2) + kr(s, 24, 24, 6, "blue", "blue", 1) + pf(s, "M24 21v6M21 24h6", stroke="paper", sw=2))
    I["zeile_oberhalb"] = tabelle(s, 4, 12, 24, 16, "blue", 2, 2) + pfeil(s, "M16 9V3.5M12.8 6.2L16 3l3.2 3.2")
    I["zeile_unterhalb"] = (tabelle(s, 4, 3, 24, 16, "paper", 2, 2) + rc(s, 4.9, 15.8, 22.2, 2.3, 0, "blue", None) + pfeil(s, "M16 23v5.5M12.8 25.3L16 28.5l3.2-3.2"))
    spalten_basis = lambda x: tabelle(s, x, 6, 19, 20, "soft", 2, 2)
    I["spalte_links"] = spalten_basis(9) + pfeil(s, "M6.5 16H2.5M5 13l-3 3 3 3") + rc(s, 9, 6, 6.5, 20, 2, "blue", "ink", 1.8)
    I["spalte_rechts"] = spalten_basis(4) + pfeil(s, "M25.5 16h4M27 13l3 3-3 3") + rc(s, 16.5, 6, 6.5, 20, 2, "blue", "ink", 1.8)
    I["zellen_verbinden"] = (tabelle(s, 3, 5, 26, 22, "soft", 2, 2) + rc(s, 3, 15, 26, 6.5, 1.5, "blue", "ink", 1.8)
                             + pf(s, "M9 18.2h5M11.5 16.4L9.6 18.2l1.9 1.8M23 18.2h-5M20.5 16.4l1.9 1.8-1.9 1.8", stroke="paper", sw=1.6))
    # Einfügen
    I["bild"] = (rc(s, 3.5, 5.5, 25, 21, 3, "blue") + kr(s, 21, 12.5, 2.6, "yellow", "ink", 1.4)
                 + pf(s, "M3.5 23l7-7 5 5 4-4 9 8", "green") + rc(s, 3.5, 5.5, 25, 21, 3, "none"))
    I["formen"] = kr(s, 12.5, 12.5, 8, "purple") + rc(s, 14, 14, 13.5, 13.5, 3, "blue")
    I["diagramm"] = (rc(s, 5, 17, 5.5, 10, 1.5, "blue") + rc(s, 13.2, 11, 5.5, 16, 1.5, "blue") + rc(s, 21.5, 4.5, 5.5, 22.5, 1.5, "purple")
                     + pf(s, "M3 28.5h26", sw=2))
    I["formel"] = pf(s, "M5.5 9.5h21M11.5 9.5C11 15 10 21 7.5 26.5M20 9.5v13c0 2.5.8 4 3.4 4", stroke="purple", sw=2.6)
    I["link"] = (rc(s, 3.5, 17, 15, 8, 4, "none", "blue", 2.4, 'transform="rotate(-45 11 21)"')
                 + rc(s, 13.5, 7, 15, 8, 4, "none", "purple", 2.4, 'transform="rotate(-45 21 11)"'))
    I["kommentar"] = sprechblase(s) + pf(s, "M10 11.5h12M10 16h7.5", stroke="blue", sw=1.9)
    # Seitenlayout
    I["seitenraender"] = seite(s) + rc(s, 9.5, 12.5, 12, 12, 0.5, "none", "blue", 1.6, 'stroke-dasharray="2.2 2.2"')
    I["ausrichtung"] = (rc(s, 5, 4, 15, 21, 2.5, "paper") + rc(s, 12, 15, 17, 12, 2.5, "blue"))
    I["groesse"] = seite(s) + pfeil(s, "M11 24l9-9M15 24h-4v-4M16 15h4v4")
    I["spalten"] = seite(s) + pf(s, "M16 12.5V25", sw=1.4) + linien(s, [14, 18, 22], 9.5, 14, "ink", 1.6) + linien(s, [14, 18, 22], 18, 22.5, "blue", 1.6)
    I["umbrueche"] = (pf(s, "M5 6h22M5 11h14M5 21h22M5 26h14", sw=2) + pf(s, "M3.5 16h4M11 16h4M18 16h4M25 16h3.5", stroke="purple", sw=2.4))
    I["seitenzahl"] = seite(s) + rc(s, 8.5, 14.5, 15, 11.5, 2.4, "blue", "blue", 1) + pf(s, "M14.3 17l-.8 6.5M18.8 17l-.8 6.5M12 19.2h9.6M11.6 21.8h9.6", stroke="paper", sw=1.6)
    # Überprüfen & Schreibhilfe
    abc = pf(s, "M4 14.5l3.3-8.5 3.3 8.5M5.3 11.6h4M14 6v8.5M14 6h2a2.2 2.2 0 0 1 0 4.2h-2M14 10.2h2.5a2.2 2.2 0 0 1 0 4.3H14M27 8.2a3.6 3.6 0 0 0-6.2 1v3.4a3.6 3.6 0 0 0 6.2 1", sw=1.9)
    I["rechtschreibung"] = abc + pf(s, "M6.5 22.5l5 5 14-11", stroke="green", sw=3)
    I["grammatik"] = abc + pf(s, "M4 25c2-3 4-3 6 0s4 3 6 0 4-3 6 0 3 2 4 0", stroke="purple", sw=2.2)
    I["aenderungen_nachverfolgen"] = (pf(s, "M5 4.5h13l5 5V15", "paper") + pf(s, "M5 4.5v21a2 2 0 0 0 2 2h7", "paper") + linien(s, [12, 17, 22], 9, 17, "ink", 1.5, {2: 12})
                                      + pf(s, "M25 15l4 4-9 9-4.6.6.6-4.6z", "purple") + pf(s, "M22.5 17.5l4 4", stroke="paper", sw=1.4))
    I["kommentar_einfuegen"] = sprechblase(s) + pf(s, "M16 9.5v8M12 13.5h8", stroke="purple", sw=2.4)
    I["vergleichen"] = (pf(s, "M4.5 8a2 2 0 0 1 2-2h8l4.5 4.5V21a2 2 0 0 1-2 2h-10.5a2 2 0 0 1-2-2z", "blue")
                        + pf(s, "M13 12.5a2 2 0 0 1 2-2h8l4.5 4.5v12a2 2 0 0 1-2 2h-10.5a2 2 0 0 1-2-2z", "paper") + pf(s, "M23 10.5v4.5h4.5", sw=1.6))
    I["vorlesen"] = (pf(s, "M4.5 12.5h5l7-6v19l-7-6h-5z", "paper") + pf(s, "M21 11.5a6 6 0 0 1 0 9M24.5 8a11 11 0 0 1 0 16", stroke="purple", sw=2.3))
    # Ansicht
    I["zoom_minus"] = lupe(s, pf(s, "M9.5 13.5h8", stroke="blue", sw=2.4))
    I["zoom_plus"] = lupe(s, pf(s, "M9.5 13.5h8M13.5 9.5v8", stroke="blue", sw=2.4))
    I["seitenansicht"] = (pf(s, "M10 7.5h7l4.5 4.5v12a1.5 1.5 0 0 1-1.5 1.5H10a1.5 1.5 0 0 1-1.5-1.5V9a1.5 1.5 0 0 1 1.5-1.5z", "paper") + pf(s, "M17 7.5v4a.8.8 0 0 0 .8.8h3.7")
                          + linien(s, [17, 21], 11.5, 18, "ink", 1.4) + pf(s, "M3.5 10V6a2.5 2.5 0 0 1 2.5-2.5h4M22 3.5h4a2.5 2.5 0 0 1 2.5 2.5v4M28.5 22v4a2.5 2.5 0 0 1-2.5 2.5h-4M10 28.5H6A2.5 2.5 0 0 1 3.5 26v-4", stroke="purple", sw=2.4))
    I["navigation"] = kr(s, 16, 16, 12, "soft") + pf(s, "M22.5 9.5l-3.7 9.3-9.3 3.7 3.7-9.3z", "purple") + kr(s, 16, 16, 1.4, "paper", "paper", 1)
    I["lineal"] = (rc(s, 2.5, 11.5, 27, 10, 2.5, "yellow", "ink", 1.8, 'transform="rotate(-35 16 16.5)"')
                   + pf(s, "M9.2 21.5l1.6-2.3M13.6 18.4l2-2.8M18 15.4l1.6-2.3M22.4 12.3l2-2.8", sw=1.6))
    I["gitter"] = rc(s, 4, 4, 24, 24, 3, "soft") + pf(s, "M12 4v24M20 4v24M4 12h24M4 20h24", stroke="blue", sw=1.6)
    # Serienbrief
    I["empfaenger"] = kr(s, 16, 10.5, 5.5, "blue") + pf(s, "M5 27.5c.5-6 5-9.5 11-9.5s10.5 3.5 11 9.5z", "paper")
    I["felder"] = (rc(s, 3.5, 5.5, 25, 21, 3, "paper") + rc(s, 7.5, 9.5, 17, 5, 1.5, "purple", "purple", 1) + pf(s, "M7.5 19.5h17M7.5 23h9", stroke="ink", sw=1.6)
                   + pf(s, "M11 11l-1.5 1.5L11 14M21 11l1.5 1.5L21 14", stroke="paper", sw=1.4))
    I["vorschau"] = pf(s, "M2.5 16C6 10 10.5 7 16 7s10 3 13.5 9C26 22 21.5 25 16 25S6 22 2.5 16z", "paper") + kr(s, 16, 16, 4.8, "blue") + kr(s, 16, 16, 1.6, "ink", "ink", 1)
    I["serienbrief_starten"] = (rc(s, 2.5, 7, 22, 16, 2.5, "paper") + pf(s, "M3.5 9l10 8 10-8", sw=1.8)
                                + kr(s, 24.5, 22.5, 6.2, "green", "green", 1) + pf(s, "M22.8 19.6v5.8l5-2.9z", "paper", "paper", 1.2))
    # Oberfläche & Hilfe
    I["einstellungen"] = zahnrad(s)
    I["suchen"] = lupe(s)
    I["hilfe"] = kr(s, 16, 16, 12.5, "paper") + pf(s, "M11.8 12.8a4.3 4.3 0 0 1 8.4 1.2c0 3-4.2 3.3-4.2 6.2", stroke="purple", sw=2.4) + pf(s, "M16 24.6h.01", stroke="purple", sw=3)
    I["info"] = kr(s, 16, 16, 12.5, "paper") + pf(s, "M16 14.5v8", stroke="blue", sw=2.6) + pf(s, "M16 9.6h.01", stroke="blue", sw=3.2)
    # Seitenleisten, Schnellzugriff, Chat
    I["notiz"] = pf(s, "M6 4.5h20a1.5 1.5 0 0 1 1.5 1.5v14L19 28.5H6A1.5 1.5 0 0 1 4.5 27V6A1.5 1.5 0 0 1 6 4.5z", "yellow") + pf(s, "M27.5 20H21a2 2 0 0 0-2 2v6.5", "paper") + linien(s, [11, 16], 9, 23, "ink", 1.7)
    I["gliederung"] = (kr(s, 6, 8, 2.2, "blue", "blue", 1) + pf(s, "M12 8h15", sw=2) + kr(s, 10, 16, 2, "purple", "purple", 1) + pf(s, "M16 16h11", sw=2)
                       + kr(s, 14, 24, 1.8, "green", "green", 1) + pf(s, "M19 24h8", sw=2))
    I["fussnote"] = linien(s, [7, 12, 17], 5, 27, "ink", 1.9, {1: 22}) + pf(s, "M5 21.5h10", sw=1.4) + pf(s, "M6 25l1.6-1v5.2", stroke="purple", sw=1.7) + pf(s, "M12 26.5h12", stroke="blue", sw=1.9)
    I["haken"] = kr(s, 16, 16, 12.5, "green", "green", 1) + pf(s, "M9.5 16.5l4.5 4.5 8.5-9.5", stroke="white", sw=3)
    I["brille"] = kr(s, 8.5, 19.5, 5.5, "blue") + kr(s, 23.5, 19.5, 5.5, "blue") + pf(s, "M14 19.5a2 2 0 0 1 4 0M3 18.5L6 9.5M29 18.5L26 9.5")
    I["stift"] = pf(s, "M22 4.5l5.5 5.5L11 26.5l-6.5 1.5 1.5-6.5z", "purple") + pf(s, "M18.5 8l5.5 5.5M6 21.5l4.5 4.5", sw=1.6)
    I["assistent"] = pf(s, "M13 4l2.6 7.4L23 14l-7.4 2.6L13 24l-2.6-7.4L3 14l7.4-2.6z", "purple") + pf(s, "M24.5 18l1.3 3.7 3.7 1.3-3.7 1.3-1.3 3.7-1.3-3.7-3.7-1.3 3.7-1.3z", "blue", "blue", 1.2)
    I["chat"] = (pf(s, "M4.5 6.5a2.5 2.5 0 0 1 2.5-2.5h13a2.5 2.5 0 0 1 2.5 2.5v8a2.5 2.5 0 0 1-2.5 2.5H12l-4 3.5V17H7a2.5 2.5 0 0 1-2.5-2.5z", "blue")
                 + pf(s, "M25.5 11h1a2.5 2.5 0 0 1 2.5 2.5v8a2.5 2.5 0 0 1-2.5 2.5H26v3.5L22 24h-7a2.5 2.5 0 0 1-2.2-1.3", "paper"))
    I["rueckgaengig"] = pf(s, "M12 5L5 12l7 7", stroke="blue", sw=2.8) + pf(s, "M5.5 12H19a7 7 0 0 1 0 14h-6", sw=2.2)
    I["wiederholen"] = pf(s, "M20 5l7 7-7 7", stroke="blue", sw=2.8) + pf(s, "M26.5 12H13a7 7 0 0 0 0 14h6", sw=2.2)
    I["annehmen"] = pf(s, "M6 16.5l6.5 6.5L26 9", stroke="green", sw=3.4)
    I["ablehnen"] = pf(s, "M8 8l16 16M24 8L8 24", stroke="red", sw=3.4)
    I["schliessen"] = pf(s, "M9 9l14 14M23 9L9 23", sw=2.6)
    I["kommentar_loeschen"] = sprechblase(s) + pf(s, "M11.5 10.5l9 7M20.5 10.5l-9 7", stroke="red", sw=2.2)
    I["nach_links"] = pf(s, "M19 6l-10 10 10 10", stroke="blue", sw=3)
    I["nach_rechts"] = pf(s, "M13 6l10 10-10 10", stroke="blue", sw=3)
    I["plus"] = pf(s, "M16 6v20M6 16h20", stroke="blue", sw=3)
    I["minus"] = pf(s, "M6 16h20", stroke="blue", sw=3)
    I["ersetzen"] = pf(s, "M5 11h17M18 6l5 5-5 5M27 21H10M14 16l-5 5 5 5", stroke="purple", sw=2.4)
    I["sprung"] = kr(s, 16, 16, 11, "paper") + pf(s, "M10 16h11M17 11l5 5-5 5", stroke="blue", sw=2.6)
    I["zuletzt"] = kr(s, 16, 16, 12, "paper") + pf(s, "M16 9v7l4.5 3", stroke="purple", sw=2.6)
    I["tabelle_loeschen"] = tabelle(s, 4, 6, 24, 20, "soft", 2, 2) + pf(s, "M10 10l12 12M22 10L10 22", stroke="red", sw=3)
    I["logo"] = (pf(s, "M16 2.5c7.5 0 13.5 6 13.5 13.5S23.5 29.5 16 29.5 2.5 23.5 2.5 16 8.5 2.5 16 2.5z", "blue", "blue", 1)
                 + pf(s, "M10.5 8v12.2c0 2 1.4 3.3 3.4 3.3H23", stroke="white", sw=3.6) + kr(s, 20.5, 10.5, 2.8, "purple", "white", 1.4))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from lunivo_hybrid_weitere import weitere
    I.update(weitere(s, sys.modules[__name__]))
    return I


def svg(pal, name, koerper):
    verl = "".join(f'<linearGradient id="{n}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pal[n][0]}"/><stop offset="1" stop-color="{pal[n][1]}"/></linearGradient>' for n in AKZENTE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" stroke-linecap="round" stroke-linejoin="round">'
            f'<title>{name}</title><defs>{verl}</defs>{koerper}</svg>\n')


GRUPPEN = [
    ("Datei & Dokumente", ["neu", "oeffnen", "speichern", "speichern_unter", "drucken", "pdf_exportieren"]),
    ("Zwischenablage", ["ausschneiden", "kopieren", "einfuegen", "inhalte_einfuegen"]),
    ("Schrift & Text", ["fett", "kursiv", "unterstrichen", "durchgestrichen", "textfarbe", "markieren"]),
    ("Absatz & Listen", ["links", "zentriert", "rechts", "blocksatz", "aufzaehlung", "nummerierung"]),
    ("Tabelle", ["tabelle_einfuegen", "zeile_oberhalb", "zeile_unterhalb", "spalte_links", "spalte_rechts", "zellen_verbinden"]),
    ("Einfügen", ["bild", "formen", "diagramm", "formel", "link", "kommentar"]),
    ("Seitenlayout", ["seitenraender", "ausrichtung", "groesse", "spalten", "umbrueche", "seitenzahl"]),
    ("Überprüfen & Schreibhilfe", ["rechtschreibung", "grammatik", "aenderungen_nachverfolgen", "kommentar_einfuegen", "vergleichen", "vorlesen"]),
    ("Ansicht", ["zoom_minus", "zoom_plus", "seitenansicht", "navigation", "lineal", "gitter"]),
    ("Serienbrief", ["empfaenger", "felder", "vorschau", "serienbrief_starten"]),
    ("Seitenleisten & Schnellzugriff", ["notiz", "gliederung", "fussnote", "haken", "brille", "stift", "assistent", "chat", "rueckgaengig", "wiederholen", "annehmen", "ablehnen", "schliessen", "kommentar_loeschen", "nach_links", "nach_rechts", "plus", "minus", "ersetzen", "sprung", "zuletzt", "tabelle_loeschen"]),
    ("Oberfläche & Hilfe", ["logo", "einstellungen", "suchen", "hilfe", "info"]),
]


def groessen(alle, m):
    z = "".join(f"<img src='data:image/svg+xml;base64,{base64.b64encode(alle[n][m].encode()).decode()}' width='{g}' height='{g}'>" for n in ("neu", "tabelle_einfuegen") for g in (16, 20, 24, 32))
    return f"<h2>Größen 16 · 20 · 24 · 32 px</h2><div class='z' style='align-items:flex-end'>{z}</div>"


def main():
    ziel = os.path.abspath(ZIEL)
    alle = {}
    for modus, pal in PALETTEN.items():
        os.makedirs(os.path.join(ziel, modus), exist_ok=True)
        for name, koerper in ikonen(Stift(pal)).items():
            inhalt = svg(pal, name, koerper)
            alle.setdefault(name, {})[modus] = inhalt
            with open(os.path.join(ziel, modus, f"{name}.svg"), "w", encoding="utf-8") as f:
                f.write(inhalt)
    from lunivo_hybrid_weitere import ZUORDNUNG_WEITERE
    with open(os.path.join(ziel, "zuordnung.json"), "w", encoding="utf-8") as f:
        json.dump(ZUORDNUNG_WEITERE, f, ensure_ascii=False, indent=0, sort_keys=True)
    gruppiert = {n for _, ns in GRUPPEN for n in ns}
    gruppen = GRUPPEN + [("Weitere Symbole", sorted(n for n in alle if n not in gruppiert))]
    kacheln = {m: "" for m in PALETTEN}
    for titel, namen in gruppen:
        for m in PALETTEN:
            kacheln[m] += f"<h2>{titel}</h2><div class='z'>" + "".join(
                f"<figure><img src='data:image/svg+xml;base64,{base64.b64encode(alle[n][m].encode()).decode()}' width='48' height='48'><figcaption>{n.replace('_', ' ')}</figcaption></figure>" for n in namen if n in alle) + "</div>"
    html = ("<!doctype html><meta charset='utf-8'><title>Lunivo Hybrid – Iconfamilie</title><style>"
            "body{margin:0;font:14px system-ui,sans-serif}.h{background:#fff;color:#243062;padding:24px}.d{background:#1c2340;color:#e4ebff;padding:24px}"
            "h1{margin:0 0 8px}h2{font-size:15px;margin:22px 0 8px;opacity:.8}.z{display:flex;flex-wrap:wrap;gap:18px}figure{margin:0;width:92px;text-align:center}"
            "figcaption{font-size:11px;margin-top:4px;opacity:.8}</style>"
            f"<div class='h'><h1>Lunivo Hybrid – hell</h1>{groessen(alle,'hell')}{kacheln['hell']}</div><div class='d'><h1>Lunivo Hybrid – dunkel</h1>{groessen(alle,'dunkel')}{kacheln['dunkel']}</div>")
    html = html.replace("src='hell/", "src='hell/").replace("src='dunkel/", "src='dunkel/")
    with open(os.path.join(ziel, "uebersicht.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{len(alle)} Symbole × {len(PALETTEN)} Modi → {ziel}")


if __name__ == "__main__":
    main()
