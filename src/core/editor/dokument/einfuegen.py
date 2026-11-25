"""Einfügen: Formen, WordArt, Diagramme, Piktogramme, Formeln, Schnelltabellen, Deckblätter, Text aus Datei.

Formen, WordArt, Diagramme und Piktogramme entstehen als Bild (mit Alternativtext) — sie sind im Dokument nicht
nachträglich als Zeichnung bearbeitbar; in DOCX landen sie als normales Bild.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QUrl
from PySide6.QtGui import QColor, QImage, QPainter

from core.dokument.dokument import Auswahl, Position
from core.layout import formatwerte as F

from core.dokument.farben import Farbe
from core.editor.objekte.formen import formen_katalog as K
FORMEN = ["Rechteck", "Abgerundetes Rechteck", "Ellipse", "Dreieck", "Raute", "Pfeil nach rechts", "Stern", "Sprechblase", "Linie"]
FORMEN += [n for n in K.namen() if n not in FORMEN]           # die ganze Galerie (Einfügen ▸ Formen), auch im Fenster „Form“


def qimage_einfuegen(ed, img: QImage, alt: str = "", art: str | None = None, daten: dict | None = None) -> None:
    """Bild an der Schreibmarke einfügen. art/daten (Form, WordArt, Diagramm, …) bleiben am Bild, damit es sich wieder bearbeiten
    lässt; „Zeichnungsobjekte drucken“ kann solche Bilder weglassen."""
    ed.bild_im_text_einfuegen(img, alt, art, daten)


def _leer(w: int, h: int) -> QImage:
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    return img


# ---- Formen ---------------------------------------------------------------------------------------------------
TEXTFELD_VERTIKAL = "Textfeld vertikal"


# ---- Formen: Umrisse als Vektoranweisungen, gezeichnet vom Kern (Qt hält nur Katalogpfade als Geometrie) ----------------------------
_GRUNDFORMEN = ("Rechteck", "Abgerundetes Rechteck", "Ellipse", "Dreieck", "Raute", "Pfeil nach rechts", "Stern", "Sprechblase", "Linie")
_KAPPA = 0.5522847498


def _abgerundet(x: float, y: float, w: float, h: float, rad: float) -> list:
    rad = min(rad, w / 2, h / 2)
    k = rad * _KAPPA
    r, b = x + w, y + h
    return [("M", x + rad, y), ("L", r - rad, y), ("C", r - rad + k, y, r, y + rad - k, r, y + rad), ("L", r, b - rad), ("C", r, b - rad + k, r - rad + k, b, r - rad, b),
            ("L", x + rad, b), ("C", x + rad - k, b, x, b - rad + k, x, b - rad), ("L", x, y + rad), ("C", x, y + rad - k, x + rad - k, y, x + rad, y), ("Z",)]


def _polygon(punkte: list) -> list:
    return [("M", *punkte[0])] + [("L", *q) for q in punkte[1:]] + [("Z",)]


def _form_pfad(art: str, r, adj, punkte):
    """(Umriss als Pfad, offen?) für Freiformen, Anpassungsformen und Katalogformen; ``None`` für die eingebauten Grundformen."""
    if punkte:
        from core.editor.objekte.formen import freiform as FF
        return FF.pfad(punkte, r), not FF.geschlossen(punkte)
    if adj and K.anpassbar(art):
        return K.pfad(art, r, adj), False
    if art not in _GRUNDFORMEN and K.hat(art):
        return K.pfad(art, r), bool(K.ist_linie(art))
    return None


def _grundform_ops(art: str, x: float, y: float, w: float, h: float) -> tuple[list, bool]:
    """(Umriss, offen?) einer eingebauten Grundform im Rechteck (x, y, w, h)."""
    cx, cy = x + w / 2, y + h / 2
    if art == "Abgerundetes Rechteck":
        return _abgerundet(x, y, w, h, 16), False
    if art == "Ellipse":
        return [("E", cx, cy, w / 2, h / 2)], False
    if art == "Dreieck":
        return _polygon([(cx, y), (x + w, y + h), (x, y + h)]), False
    if art == "Raute":
        return _polygon([(cx, y), (x + w, cy), (cx, y + h), (x, cy)]), False
    if art == "Pfeil nach rechts":
        h4, r3 = h / 4, x + w - w * .3
        return _polygon([(x, y + h4), (r3, y + h4), (r3, y), (x + w, cy), (r3, y + h), (r3, y + h - h4), (x, y + h - h4)]), False
    if art == "Stern":
        ra, ri = min(w, h) / 2, min(w, h) / 4.6
        return _polygon([(cx + (ra if i % 2 == 0 else ri) * math.cos(-math.pi / 2 + i * math.pi / 5), cy + (ra if i % 2 == 0 else ri) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]), False
    if art == "Sprechblase":
        korper_h = h * 0.78
        spitze = _polygon([(x + w * .2, y + korper_h - 1), (x + w * .12, y + h), (x + w * .36, y + korper_h - 1)])
        return _abgerundet(x, y, w, korper_h, 14) + spitze, False
    if art == "Linie":
        return [("M", x, cy), ("L", x + w, cy)], True
    return [("R", x, y, w, h)], False                                    # Rechteck und das Textfeld mit senkrechtem Text


def _fuellstil(fuell: str, art: str, x: float, y: float, w: float, h: float):
    """Füllung einer Form als ``Style``: einfarbig, ``verlauf`` (hell nach Farbe), ``abgestuft`` (drei Stufen), ``glanz`` (obere Hälfte heller)."""
    from core.geometrie import Point
    from core.rendering.ausgabe.backend import LinearGradient, Style, rgba
    from core.rendering.objekte.objekte import dunkler, heller
    c = rgba(fuell)
    if art not in ("verlauf", "abgestuft", "glanz"):
        return Style(color=c, width=0, filled=True)
    if art == "verlauf":
        stops = ((0.0, heller(c, 170)), (1.0, c))
    elif art == "abgestuft":
        stops = tuple((pos, heller(c, f)) for pos, f in ((0, 150), (0.33, 150), (0.34, 115), (0.66, 115), (0.67, 100), (1, 100)))
    else:
        stops = ((0.0, heller(c, 165)), (0.49, heller(c, 125)), (0.5, dunkler(c, 108)), (1.0, c))
    return Style(color=c, width=0, filled=True, fill=LinearGradient(Point(x, y), Point(x, y + h), stops))


def form_bild(art: str, breite: int = 240, hoehe: int = 140, fuell: str = Farbe.AKZENT_DUNKEL, linie: str = "#1f3864",
              strich: float = 2.0, text: str = "", skala: float = 1.0, adj=None, fuell_art: str = "", punkte=None) -> QImage:
    """``skala``: Bild in dieser Auflösung (Maße und Strich bleiben logisch, das Bild ist ``skala``-mal so groß) — für scharfe freie Formen.
    ``adj``: Parameter der Anpassungsgriffe (``formen_anpassen``); ``fuell_art``: Verlauf der Füllung; ``punkte``: Punktliste einer Freiform (``editor/objekte/freiform.py``).
    Gezeichnet wird vom Kern (``RasterZiel``); Qt liefert nur den Pfad der Katalog- und Freiformen als Geometrie."""
    from vcl.qt.rendering.zeichnen.anzeige import kern_bild
    from vcl.qt.rendering.zeichnen.pfad import pfad_zu_vektor
    from core.geometrie import Point, Rect
    from core.rendering.ausgabe.backend import Style, rgba
    from core.textsatz import FontSpec
    strich = max(float(strich), 1.0)                         # eine Haarlinie (Word: 0,25–0,75 pt) bleibt auf dem Bildschirm mindestens einen Bildpunkt dick
    x, y, w, h = strich, strich, breite - 2 * strich, hoehe - 2 * strich
    r = QRectF(x, y, w, h)
    gefunden = _form_pfad(art, r, adj, punkte)
    if gefunden is not None:
        ops, offen = list(pfad_zu_vektor(gefunden[0]).ops), gefunden[1]
    else:
        ops, offen = _grundform_ops(art, x, y, w, h)

    def zeichnen(z) -> None:
        if fuell and not offen and art != "Linie":
            z.draw_path(ops, _fuellstil(fuell, fuell_art, x, y, w, h), True, True)
        lc = rgba(linie)
        if lc[3] > 0:
            z.draw_path(ops, Style(color=lc, width=strich, join="round"), True, True)
        if art == TEXTFELD_VERTIKAL:                                     # Textfeld mit senkrecht laufendem Text (90° gedreht)
            z.draw_rect(Rect(x, y, w, h), Style(color=lc, width=strich))
        if text:
            hell = rgba(fuell) if fuell else None
            weiss = hell is not None and (max(hell[:3]) + min(hell[:3])) / 2 < 140
            farbe = (255, 255, 255, 255) if weiss else (0, 0, 0, 255)
            schrift = FontSpec("Liberation Sans", 12)
            if art == TEXTFELD_VERTIKAL:
                z.push_state(translate=Point(x + w / 2, y + h / 2), rotate=90)
                z.draw_text_box(text, Rect(-h / 2 + 6, -w / 2 + 6, h - 12, w - 12), schrift, Style(color=farbe), align="left", wrap=True, valign="top")
                z.pop_state()
            else:
                z.draw_text_box(text, Rect(x, y, w, h), schrift, Style(color=farbe), align="center", wrap=True, valign="center")
    return kern_bild(breite, hoehe, zeichnen, faktor=skala)


# ---- WordArt --------------------------------------------------------------------------------------------------------
WORDART_STILE = ["Verlauf", "Schatten", "Umriss", "Regenbogen", "Welle"]
# Galerie „Formatvorlage“ (Einfügen ▸ WordArt ▾): 15 eigene Stile, angelehnt an die Vorlage (Neun oben, sechs darunter).
# (Name, Füllung oben, Füllung unten oder None = nur Kontur, Kontur oder None, Konturbreite, Schatten oder None)
WORDART_VORLAGEN = [
    ("Schwarz mit Schatten", "#111111", "#111111", None, 0, "#9aa0a6"),
    ("Blau, Verlauf", "#8fc1ec", "#2f78bd", None, 0, None),
    ("Orange, Verlauf", "#f6a96a", "#d9601a", None, 0, None),
    ("Blaue Kontur", "#ffffff", "#ffffff", "#4f93d1", 2.0, None),
    ("Gold", "#ffc933", "#f0a500", None, 0, None),
    ("Grau", "#9a9a9a", "#7c7c7c", None, 0, None),
    ("Dunkelblau, Verlauf", "#5b86d6", "#1f3f8f", None, 0, "#b8c4dc"),
    ("Gelb mit heller Kontur", "#ffe27a", "#ffd23f", "#fff3c4", 1.6, None),
    ("Hellblaue Kontur", "#ffffff", "#e8f1fb", "#9cc3ea", 2.0, None),
    ("Grau mit Schatten", "#8a8a8a", "#6e6e6e", None, 0, "#2b2b2b"),
    ("Schwarz, blauer Rand", "#141414", "#141414", "#5b86d6", 1.6, "#b8c4dc"),
    ("Dunkle Kontur, blauer Schatten", "#ffffff", "#eef2f8", "#1f2d4d", 2.0, "#5b86d6"),
    ("Blau mit heller Kontur", "#3b7fcf", "#2461a8", "#b9d6f2", 1.8, None),
    ("Orange Kontur", "#ffffff", "#fdeadb", "#e8803a", 2.0, "#f4c9a5"),
    ("Hellgrau, verblasst", "#e6e6e6", "#c4c4c4", "#d9d9d9", 1.2, None),
]
WORDART_VORGABEN = [(n, "Vorlage", Farbe.AKZENT) for n, *_r in WORDART_VORLAGEN]    # bleibt für ältere Aufrufer (Name, Stil, Farbe)
WORDART_STANDARDTEXT = "Hier Text einfügen"


def wordart_vorlage_bild(text: str, nr: int, schrift: str = "Liberation Sans", pt: int = 48) -> QImage:
    """WordArt nach einem der 15 Stile der Galerie: Füllverlauf, Kontur und Schatten (gezeichnet über ``core/rendering/wordart.py``)."""
    from vcl.qt.rendering.zeichnen.anzeige import kern_bild
    from core.rendering.text import wordart
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    b, h = wordart.masse(engine, text, schrift, pt)
    return kern_bild(b, h, lambda z: wordart.zeichne(z, engine, text, WORDART_VORLAGEN[nr], schrift, pt))


def wordart_bild(text: str, stil: str = "Verlauf", schrift: str = "Liberation Sans", pt: int = 48, farbe: str = Farbe.AKZENT,
                 vorlage: int | None = None) -> QImage:
    """WordArt in einem der älteren Stile (Verlauf, Schatten, Umriss, Regenbogen, Welle) oder nach einer Vorlage der Galerie; gezeichnet vom Kern."""
    if vorlage is not None:
        return wordart_vorlage_bild(text, vorlage, schrift, pt)
    import math as _m
    from vcl.qt.rendering.zeichnen.anzeige import kern_bild
    from core.geometrie import Point
    from core.rendering.ausgabe.backend import LinearGradient, Style, rgba
    from core.rendering.objekte.objekte import dunkler, heller
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    f = FontSpec(schrift, float(pt), 700)
    m = engine.font_metrics(f)
    b, h = int(engine.measure_text(text, f)) + 40, int(m.line_spacing) + 40
    ops = engine.glyphen_pfad(text, f, 20.0, 20.0 + m.ascent)
    if stil == "Welle":                                                      # Wellenlinie über die Breite
        ops = [op if op[0] == "Z" else (op[0],) + tuple(v + (_m.sin(op[i - 1] / 18) * h * 0.08 if i % 2 == 0 else 0.0) for i, v in enumerate(op[1:], 1)) for op in ops]

    def zeichnen(z) -> None:
        if stil == "Schatten":
            z.push_state(translate=Point(4, 4))
            z.draw_path(ops, Style(color=(0, 0, 0, 90), width=0, filled=True), True, True)
            z.pop_state()
        if stil == "Umriss":
            z.draw_path(ops, Style(color=rgba(farbe), width=2.2), True, True)
            return
        if stil == "Regenbogen":
            cs = ("#e03131", "#f08c00", "#ffd43b", Farbe.GRUEN, "#1971c2", "#7048a8")
            fill = LinearGradient(Point(0, 0), Point(b, 0), tuple((i / 5, rgba(c)) for i, c in enumerate(cs)))
        else:
            c = rgba(farbe)
            fill = LinearGradient(Point(0, 0), Point(0, h), ((0.0, heller(c, 150)), (1.0, dunkler(c, 150))))
        z.draw_path(ops, Style(color=rgba(farbe), width=0, filled=True, fill=fill), True, True)
    return kern_bild(b, h, zeichnen)


# ---- Diagramm --------------------------------------------------------------------------------------------------------
DIAGRAMMARTEN = ["Säulen", "Balken", "Linie", "Kreis"]


def diagramm_bild(art: str, titel: str, kategorien: list[str], reihen: dict[str, list[float]], b: int = 640, h: int = 400) -> QImage:
    """``art``: Untertyp aus ``editor.diagramme.diagramm.TYPEN`` oder einer der früheren Namen (Säulen, Balken, Linie, Kreis)."""
    from core.editor.diagramme import diagramm as D
    return D.bild(art, titel, kategorien, reihen, b, h)


# ---- Piktogramm -------------------------------------------------------------------------------------------------------
def piktogramm_bild(name: str, px: int = 96, farbe: str = "#1f2328") -> QImage:
    from vcl.qt.widgets.bausteine.piktogramme import piktogramme
    return piktogramme.katalog_bild(name, px, farbe, 1.7 if px < 128 else 1.5)


# ---- Formel -----------------------------------------------------------------------------------------------------------------
_GRIECH = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "theta": "θ", "lambda": "λ", "mu": "μ",
           "pi": "π", "rho": "ρ", "sigma": "σ", "phi": "φ", "omega": "ω", "Delta": "Δ", "Sigma": "Σ", "Omega": "Ω",
           "infty": "∞", "sum": "∑", "int": "∫", "partial": "∂", "pm": "±", "leq": "≤", "geq": "≥", "neq": "≠", "approx": "≈",
           "times": "×", "cdot": "·", "to": "→", "in": "∈", "forall": "∀", "exists": "∃"}


def formel_teile(text: str) -> list[tuple[str, str]]:
    """Einfache Schreibweise → [(Text, "normal"|"hoch"|"tief")]:  a^2  x_{12}  sqrt(x)  frac(a,b)  \\alpha"""
    import re
    t = re.sub(r"\\([A-Za-z]+)", lambda m: _GRIECH.get(m.group(1), m.group(0)), text)
    t = re.sub(r"sqrt\(([^()]*)\)", r"√(\1)", t)
    t = re.sub(r"frac\(([^(),]*),([^()]*)\)", r"(\1)⁄(\2)", t)
    teile: list[tuple[str, str]] = []
    i = 0
    puffer = ""
    while i < len(t):
        ch = t[i]
        if ch in "^_" and i + 1 < len(t):
            if t[i + 1] == "{":
                j = t.find("}", i + 2)
                j = len(t) if j < 0 else j
                inhalt, naechst = t[i + 2:j], j + 1
            else:
                inhalt, naechst = t[i + 1], i + 2
            if puffer:
                teile.append((puffer, "normal")); puffer = ""
            teile.append((inhalt, "hoch" if ch == "^" else "tief"))
            i = naechst
        else:
            puffer += ch; i += 1
    if puffer:
        teile.append((puffer, "normal"))
    return teile


# Galerie „Integriert“ (Einfügen ▸ Gleichung ▾): (Name, Formel in der einfachen Schreibweise von ``formel_teile``)
GLEICHUNGEN = [("Kreisfläche", "A = \\pi r^2"),
               ("Binomischer Lehrsatz", "(x + a)^n = \\sum_{k=0}^{n} C(n,k) x^k a^{n−k}"),
               ("Summenentwicklung", "(1 + x)^n = 1 + nx/1! + n(n − 1)x^2/2! + …"),
               ("Fourier-Reihe", "f(x) = a_0 + \\sum_{n=1}^{\\infty} (a_n cos(n\\pi x/L) + b_n sin(n\\pi x/L))"),
               ("Satz des Pythagoras", "a^2 + b^2 = c^2"),
               ("Quadratische Formel", "x = (−b \\pm sqrt(b^2 − 4ac)) / 2a"),
               ("Taylor-Entwicklung", "e^x = 1 + x/1! + x^2/2! + x^3/3! + …,  −\\infty < x < \\infty")]


def formel_bild(text: str, pt: int = 16, farbe: str = Farbe.SCHWARZ) -> QImage:
    """Die Formel als Bild (Vorschau im Fenster „Formel“ und in der Gleichungsgalerie): kursive Stücke, Hoch- und Tiefgestelltes verkleinert und versetzt; gezeichnet vom Kern."""
    from vcl.qt.rendering.zeichnen.anzeige import kern_bild
    from core.geometrie import Point
    from core.rendering.ausgabe.backend import Style, rgba
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    basis, klein = FontSpec("DejaVu Serif", float(pt), 400, True), FontSpec("DejaVu Serif", pt * 2 / 3, 400, True)
    stuecke, x = [], 0.0
    for t, a in formel_teile(text):
        f = klein if a in ("hoch", "tief") else basis
        stuecke.append((t, a, f, x))
        x += engine.measure_text(t, f)
    m = engine.font_metrics(basis)
    grund = 2 + pt * 0.45 + m.ascent
    b, h = int(x) + 8, int(grund + m.descent + pt * 0.3) + 4

    def zeichnen(z) -> None:
        for t, a, f, x0 in stuecke:
            z.draw_text(t, Point(4 + x0, grund - pt * 0.4 if a == "hoch" else grund + pt * 0.2 if a == "tief" else grund), f, Style(color=rgba(farbe)))
    return kern_bild(b, h, zeichnen)


def formel_einfuegen(ed, text: str) -> None:
    """Fügt die Formel als Text mit hoch- und tiefgestellten Teilen an der Schreibmarke ein."""
    with ed.sitzung.gruppe("Formel"):
        for stueck, art in formel_teile(text):
            fmt = {"schrift": "DejaVu Serif", "kursiv": True}
            if art in ("hoch", "tief"):
                fmt["hoch_tief"] = art
            ed.sitzung.text_einfuegen(stueck, format=fmt)
        ed.sitzung.text_einfuegen(" ", format={})
    ed.ansicht.nach_aenderung()


# ---- Schnelltabellen -----------------------------------------------------------------------------------------------------------
def _tabelle(ed, zeilen: list[list[str]], kopf: bool = True, breit: bool = True):
    """Fügt eine Tabelle mit Rahmen und dem Text je Zelle ein (erste Zeile als Kopfzeile, wenn ``kopf``)."""
    spalten = max(len(z) for z in zeilen)

    def f(sitz):
        with sitz.gruppe("Tabelle einfügen"):
            fmt = {"rahmen_breite": 1.0, "rahmen_farbe": "#333333", "rahmen_art": "einfach", "zellpolster": 4.0, "breite_art": "prozent", "breite": 100.0 if breit else 60.0}
            if kopf:
                fmt["kopfzeilen"] = 1
            tid = sitz.tabelle_einfuegen(len(zeilen), spalten, format=fmt)
            for r, z in enumerate(zeilen):
                for k, v in enumerate(z):
                    if v:
                        sitz.text_einfuegen(v, sitz.zelle_anfang(tid, r, k), format={"fett": True} if kopf and r == 0 else None)
            if kopf:
                sitz.zellformat_anwenden(tid, {"hintergrund": "#e7eef8"}, [(0, k) for k in range(spalten)])
            sitz.setze_auswahl(sitz.zelle_anfang(tid, 0, 0))
    ed.ansicht._aendern(f)


SCHNELLTABELLEN = ["Tabelle mit Kopfzeile (3 × 4)", "Zwei Spalten", "Kalender (Monat)", "Matrix (3 × 3)", "Zeitplan"]


def schnelltabelle(ed, name: str) -> None:
    if name.startswith("Tabelle mit Kopfzeile"):
        _tabelle(ed, [["Spalte 1", "Spalte 2", "Spalte 3"]] + [["", "", ""] for _ in range(3)])
    elif name == "Zwei Spalten":
        _tabelle(ed, [["Begriff", "Erklärung"]] + [["", ""] for _ in range(4)])
    elif name.startswith("Kalender"):
        import calendar
        import datetime
        h = datetime.date.today()
        tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        zeilen = [tage]
        for woche in calendar.Calendar(0).monthdayscalendar(h.year, h.month):
            zeilen.append([str(d) if d else "" for d in woche])
        _tabelle(ed, zeilen)
    elif name.startswith("Matrix"):
        _tabelle(ed, [["", "A", "B"], ["A", "", ""], ["B", "", ""]], kopf=True)
    else:
        _tabelle(ed, [["Zeit", "Was", "Wer"]] + [["", "", ""] for _ in range(5)])


# ---- Deckblatt ----------------------------------------------------------------------------------------------------------------
DECKBLATT_VORLAGEN = ["Schlicht", "Mit Linie", "Zentriert", "Farbband"]


def deckblatt_einfuegen(ed, vorlage: str, titel: str, untertitel: str, autor: str, datum: str) -> None:
    """Setzt ein Deckblatt an den Anfang des Dokuments; danach beginnt der Text auf einer neuen Seite."""
    zentriert = vorlage in ("Zentriert", "Mit Linie")
    teile = [(titel, 30, True, 120), (untertitel, 16, False, 6), ("", 12, False, 160), (autor, 13, False, 4), (datum, 12, False, 4)]

    def f(s):
        with s.gruppe("Deckblatt"):
            anfang = s.dokument.anfang()
            texte = [t[0] for t in teile]
            s.text_einfuegen("\n".join(texte) + "\n\n", anfang)
            absaetze = list(s.dokument.absaetze())
            for (text, pt, fett, abstand), a in zip(teile, absaetze):
                af = {"abstand_vor": abstand / 0.75, "ausrichtung": "mitte" if zentriert else "links"}
                zf = {"groesse_pt": float(pt), "fett": True if fett else None}
                if vorlage == "Farbband" and fett:                  # Titel weiß auf farbigem Band über die ganze Breite
                    af.update(hintergrund=Farbe.AKZENT, abstand_nach=18 / 0.75)
                    zf["farbe"] = Farbe.WEISS
                s.absatzformat_anwenden(af, absatz_ids=[a.id])
                if a.laenge:
                    s.zeichenformat_anwenden(zf, Auswahl(Position(a.id, 0), Position(a.id, a.laenge)))
                s.absatz_zeichenformat_anwenden(zf, absatz_ids=[a.id])
            s.absatzformat_anwenden({"seitenumbruch_nach": True}, absatz_ids=[absaetze[len(teile)].id])
            s.setze_auswahl(Position(absaetze[len(teile)].id, 0))
    ed.ansicht._aendern(f)


# ---- Objekt als Symbol ----------------------------------------------------------------------------------------------------------
def datei_symbol_bild(name: str, symbol: QImage, breite: int = 120) -> QImage:
    """Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen); Name und Zusammensetzung zeichnet der Kern."""
    from vcl.qt.rendering.zeichnen.anzeige import kern_bild
    from core.geometrie import Point, Rect
    from core.rendering.ausgabe.backend import Style, rgba
    from core.rendering.bild.bildeffekte import png_bytes
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    f = FontSpec("Liberation Sans", 9.0)
    zeile = name
    if engine.measure_text(zeile, f) > breite - 8:                           # in der Mitte kürzen, bis der Name passt
        rest, links, rechts = name, 0, 0
        while len(rest) > 2 and engine.measure_text(name[:links + 1] + "…" + name[len(name) - rechts:], f) <= breite - 8:
            if links <= rechts:
                links += 1
            else:
                rechts += 1
        zeile = name[:links] + "…" + (name[len(name) - rechts:] if rechts else "")
    m = engine.font_metrics(f)
    sym = symbol.convertToFormat(QImage.Format_RGBA8888)
    png = png_bytes(sym.width(), sym.height(), bytes(sym.constBits()))
    b, h = breite, symbol.height() + 12 + int(m.line_spacing)

    def zeichnen(z) -> None:
        z.draw_image(png, Rect((breite - symbol.width()) // 2, 4, symbol.width(), symbol.height()), smooth=True)
        z.draw_text(zeile, Point((breite - engine.measure_text(zeile, f)) / 2, symbol.height() + 8 + m.ascent), f, Style(color=rgba(Farbe.TINTE_DUNKEL)))
    return kern_bild(b, h, zeichnen)


# ---- Text aus Datei ---------------------------------------------------------------------------------------------------------------
def _fremde_bloecke(s, fremd) -> list:
    """Die Blöcke des Haupttextes eines geladenen Dokuments für die Sitzung ``s``: Listen werden angelegt, Bilddaten unter neuen Namen abgelegt."""
    import copy
    from core.dokument.dokument import Absatz, InlineObjekt, Rahmen, Tabelle
    bloecke = copy.deepcopy([b for a in fremd.abschnitte for b in a.bloecke])
    listen: dict = {}
    namen: dict = {}

    def absatz(a):
        if a.liste_id is not None:
            if a.liste_id not in listen:
                d = fremd.listen.get(a.liste_id)
                listen[a.liste_id] = s.liste_anlegen(copy.deepcopy(d.ebenen)) if d is not None and d.ebenen else None
            a.liste_id = listen[a.liste_id]
        for x in a.inhalte:
            if isinstance(x, InlineObjekt) and x.ressource and x.ressource in fremd.ressourcen:
                if x.ressource not in namen:
                    namen[x.ressource] = f"import-{len(s.dokument.ressourcen) + len(namen) + 1}-{x.ressource}"
                    s.ressource_setzen(namen[x.ressource], fremd.ressourcen[x.ressource])
                x.ressource = namen[x.ressource]

    def lauf(liste):
        for b in liste:
            if isinstance(b, Absatz):
                absatz(b)
            elif isinstance(b, Tabelle):
                for zeile in b.zellen:
                    for z in zeile:
                        lauf(z.bloecke)
            elif isinstance(b, Rahmen):
                lauf(b.bloecke)
    lauf(bloecke)
    return bloecke


def text_aus_datei(ed, pfad: str):
    """Fügt den Inhalt einer Datei (DOCX, ODT, RTF, TXT …) an der Schreibmarke ein; → Bericht über Nicht-Übernommenes."""
    from framework.dokumentverwaltung.dateizugriff.modell_laden import lade_modell
    geladen = lade_modell(pfad)

    def f(s):
        with s.gruppe("Text aus Datei"):
            s.ausschnitt_einfuegen(_fremde_bloecke(s, geladen.document))
    ed.ansicht._aendern(f)
    return geladen.report


# ---- Datum und Uhrzeit ----------------------------------------------------------------------------------------------------------------
DATUMSFORMATE = ["dd.MM.yyyy", "dddd, d. MMMM yyyy", "d. MMMM yyyy", "dd.MM.yy", "yyyy-MM-dd", "d. MMM yy", "dd.MM.", "MMMM yy",
                 "MMM yy", "dd.MM.yyyy HH:mm", "dd.MM.yyyy HH:mm:ss", "HH:mm", "HH:mm:ss", "d. MMMM yyyy, HH:mm 'Uhr'"]
# Sprache → (Beschriftung, Formate) für das Fenster „Datum und Uhrzeit“
DATUM_SPRACHEN = {
    "de_DE": ("Deutsch (Deutschland)", DATUMSFORMATE),
    "de_AT": ("Deutsch (Österreich)", DATUMSFORMATE),
    "de_CH": ("Deutsch (Schweiz)", DATUMSFORMATE),
    "en_US": ("Englisch (USA)", ["M/d/yyyy", "dddd, MMMM d, yyyy", "MMMM d, yyyy", "M/d/yy", "yyyy-MM-dd", "d-MMM-yy", "M.d.yyyy",
                                 "MMM. d, yy", "d MMMM yyyy", "MMMM yy", "MMM-yy", "M/d/yyyy h:mm AP", "M/d/yyyy h:mm:ss AP", "h:mm AP",
                                 "h:mm:ss AP", "HH:mm"]),
    "en_GB": ("Englisch (Großbritannien)", ["dd/MM/yyyy", "dddd, d MMMM yyyy", "d MMMM yyyy", "dd/MM/yy", "yyyy-MM-dd", "d-MMM-yy",
                                            "dd.MM.yyyy", "d MMM. yy", "MMMM yy", "MMM-yy", "dd/MM/yyyy HH:mm", "dd/MM/yyyy HH:mm:ss",
                                            "HH:mm", "HH:mm:ss"]),
}


def datum_feldanweisung(fmt: str) -> str:
    """Qt-Datumsformat → DOCX-Feld (DATE, bei reinen Uhrzeiten TIME) für „Automatisch aktualisieren“."""
    bild = fmt.replace("AP", "AM/PM").replace('"', "'")
    art = "TIME" if not any(z in fmt for z in "dMy") else "DATE"
    return f'{art} \\@ "{bild}"'


def datum_text(fmt: str, sprache: str = "de_DE") -> str:
    from PySide6.QtCore import QDateTime, QLocale
    return QLocale(sprache).toString(QDateTime.currentDateTime(), fmt)


# ---- Initiale -------------------------------------------------------------------------------------------------------------------------------
def initiale(ed, zeilen: int = 3) -> bool:
    """Erster Buchstabe des Absatzes groß und fett (im Absatz, in der Zeile)."""
    s = ed.sitzung
    a = s._absatz(s.auswahl.kopf.absatz_id)
    if not a.text.strip():
        return False
    pt = float(F.zeichenformat(s.dokument, a, {}).get("groesse_pt") or 11.0) * zeilen * 1.4
    return ed.ansicht._aendern(lambda sitz: sitz.zeichenformat_anwenden({"groesse_pt": pt, "fett": True}, Auswahl(Position(a.id, 0), Position(a.id, 1))))


def textfeld(ed, text: str = "Text hier eingeben", breite: int = 50) -> None:
    """Ein Textfeld als einzellige Tabelle mit Rahmen."""
    def f(sitz):
        with sitz.gruppe("Textfeld"):
            tid = sitz.tabelle_einfuegen(1, 1, format={"rahmen_breite": 1.5, "rahmen_farbe": "#1f3864", "rahmen_art": "einfach", "zellpolster": 8.0,
                                                       "breite_art": "prozent", "breite": float(breite)})
            sitz.text_einfuegen(text, sitz.zelle_anfang(tid, 0, 0))
    ed.ansicht._aendern(f)


# ---- Bild bearbeiten (Farbe, Zuschneiden, Drehen) -----------------------------------------------------------------------
def bild_ersetzen(ed, wandle) -> bool:
    """wandle(QImage) → QImage; das Bild im Text wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, Seitenverhältnis folgt)."""
    o = ed.inline_gewaehlt()
    if o is None:
        return False
    img = ed.bild_ressource(o.ressource)
    if img is None or img.isNull():
        return False
    neu = wandle(QImage(img))
    if neu is None or neu.isNull():
        return False
    faktor = (o.breite / img.width()) if o.breite and img.width() else 1.0
    orig = o.daten.get("orig") or o.ressource
    return ed.inline_aendern(o.id, ressource=ed.bild_ressource_neu(neu), breite=neu.width() * faktor, hoehe=neu.height() * faktor, daten={**o.daten, "orig": orig})


def bild_original(ed) -> bool:
    o = ed.inline_gewaehlt()
    if o is None or not o.daten.get("orig"):
        return False
    img, alt = ed.bild_ressource(o.daten["orig"]), ed.bild_ressource(o.ressource)
    if img is None:
        return False
    faktor = (o.breite / alt.width()) if o.breite and alt is not None and alt.width() else 1.0
    daten = {k: v for k, v in o.daten.items() if k != "orig"}
    return ed.inline_aendern(o.id, ressource=o.daten["orig"], breite=img.width() * faktor, hoehe=img.height() * faktor, daten=daten)


def farbe_anwenden(img: QImage, modus: str) -> QImage:
    if modus in ("Graustufen", "Sepia", "Schwarzweiß"):
        g = img.convertToFormat(QImage.Format_Grayscale8).convertToFormat(QImage.Format_ARGB32)
        if modus == "Sepia":
            p = QPainter(g)
            p.setCompositionMode(QPainter.CompositionMode_Multiply)
            p.fillRect(g.rect(), QColor("#d9b98a"))
            p.end()
            return g
        if modus == "Schwarzweiß":
            return img.convertToFormat(QImage.Format_Mono, Qt.ThresholdDither).convertToFormat(QImage.Format_ARGB32)
        return g
    if modus in ("Heller", "Dunkler"):
        out = img.convertToFormat(QImage.Format_ARGB32)
        p = QPainter(out)
        farbe = QColor(255, 255, 255, 70) if modus == "Heller" else QColor(0, 0, 0, 70)
        p.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        p.fillRect(out.rect(), farbe)
        p.end()
        return out
    return img


def zuschneiden(img: QImage, links: int, oben: int, rechts: int, unten: int) -> QImage:
    r = QRectF(links, oben, img.width() - links - rechts, img.height() - oben - unten).toRect()
    return img.copy(r) if r.width() > 0 and r.height() > 0 else img


def drehen(img: QImage, art: str) -> QImage:
    from PySide6.QtGui import QTransform
    if art == "rechts":
        return img.transformed(QTransform().rotate(90))
    if art == "links":
        return img.transformed(QTransform().rotate(-90))
    if art in ("horizontal", "vertikal"):
        from core.editor.objekte.bild.bildeffekte import gespiegelt
        return gespiegelt(img, waagrecht=art == "horizontal", senkrecht=art == "vertikal")
    return img
