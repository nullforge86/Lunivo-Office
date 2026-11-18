"""Einfügen: Formen, WordArt, Diagramme, Piktogramme, Formeln, Schnelltabellen, Deckblätter, Text aus Datei.

Formen, WordArt, Diagramme und Piktogramme entstehen als Bild (mit Alternativtext) — sie sind im Dokument nicht
nachträglich als Zeichnung bearbeitbar; in DOCX landen sie als normales Bild.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QUrl
from PySide6.QtGui import (
    QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF,
    QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextDocumentFragment, QTextFormat, QTextFrameFormat, QTextImageFormat, QTextLength,
    QTextTableFormat,
)

from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.core.document.dokument import Auswahl, Position
from lunivo_writer.core.layout import formatwerte as F

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.editor.objekte import formen_katalog as K
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


def form_pinsel(fuell: str, art: str, r: QRectF) -> QBrush:
    """Füllung einer Form: ``art`` leer = einfarbig, ``verlauf`` (hell nach Farbe), ``abgestuft`` (drei Stufen), ``glanz`` (obere Hälfte heller)."""
    c = QColor(fuell)
    if art not in ("verlauf", "abgestuft", "glanz"):
        return QBrush(c)
    g = QLinearGradient(r.topLeft(), r.bottomLeft())
    if art == "verlauf":
        g.setColorAt(0, c.lighter(170)); g.setColorAt(1, c)
    elif art == "abgestuft":
        for pos, f in ((0, 150), (0.33, 150), (0.34, 115), (0.66, 115), (0.67, 100), (1, 100)):
            g.setColorAt(pos, c.lighter(f))
    else:
        g.setColorAt(0, c.lighter(165)); g.setColorAt(0.49, c.lighter(125)); g.setColorAt(0.5, c.darker(108)); g.setColorAt(1, c)
    return QBrush(g)


def _form_dreieck(p, r) -> None:
    p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.bottom()), QPointF(r.left(), r.bottom())]))


def _form_raute(p, r) -> None:
    p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()),
                             QPointF(r.center().x(), r.bottom()), QPointF(r.left(), r.center().y())]))


def _form_pfeil(p, r) -> None:
    h4 = r.height() / 4
    p.drawPolygon(QPolygonF([QPointF(r.left(), r.top() + h4), QPointF(r.right() - r.width() * .3, r.top() + h4),
                             QPointF(r.right() - r.width() * .3, r.top()), QPointF(r.right(), r.center().y()),
                             QPointF(r.right() - r.width() * .3, r.bottom()), QPointF(r.right() - r.width() * .3, r.bottom() - h4),
                             QPointF(r.left(), r.bottom() - h4)]))


def _form_stern(p, r) -> None:
    c, ra, ri = r.center(), min(r.width(), r.height()) / 2, min(r.width(), r.height()) / 4.6
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = ra if i % 2 == 0 else ri
        pts.append(QPointF(c.x() + rad * math.cos(ang), c.y() + rad * math.sin(ang)))
    p.drawPolygon(QPolygonF(pts))


def _form_sprechblase(p, r) -> None:
    koerper = QRectF(r.left(), r.top(), r.width(), r.height() * 0.78)
    pfad = QPainterPath()
    pfad.addRoundedRect(koerper, 14, 14)
    spitze = QPainterPath()
    spitze.addPolygon(QPolygonF([QPointF(r.left() + r.width() * .2, koerper.bottom() - 1),
                                 QPointF(r.left() + r.width() * .12, r.bottom()),
                                 QPointF(r.left() + r.width() * .36, koerper.bottom() - 1)]))
    p.drawPath(pfad.united(spitze))


_FORM_ZEICHNER = {
    "Rechteck": lambda p, r: p.drawRect(r),
    "Abgerundetes Rechteck": lambda p, r: p.drawRoundedRect(r, 16, 16),
    "Ellipse": lambda p, r: p.drawEllipse(r),
    "Dreieck": _form_dreieck,
    "Raute": _form_raute,
    "Pfeil nach rechts": _form_pfeil,
    "Stern": _form_stern,
    "Sprechblase": _form_sprechblase,
    "Linie": lambda p, r: p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y())),
}


def _form_zeichnen(p, art: str, r, adj, punkte) -> None:
    """Der Pfad der Form: Freiform-Punkte, Anpassungsgriffe, eingebaute Form oder Formenkatalog."""
    if punkte:
        from lunivo_writer.editor.objekte import freiform as FF
        if not FF.geschlossen(punkte):
            p.setBrush(Qt.NoBrush)
        p.drawPath(FF.pfad(punkte, r))
    elif adj and K.anpassbar(art):
        p.drawPath(K.pfad(art, r, adj))
    elif art in _FORM_ZEICHNER:
        _FORM_ZEICHNER[art](p, r)
    elif K.hat(art):
        if K.ist_linie(art):
            p.setBrush(Qt.NoBrush)
        p.drawPath(K.pfad(art, r))


def _form_pfad(art: str, r, adj, punkte):
    """(Umriss als Qt-Pfad, offen?) für Freiformen, Anpassungsformen und Katalogformen; ``None`` für die eingebauten Grundformen, die direkt gezeichnet werden."""
    if punkte:
        from lunivo_writer.editor.objekte import freiform as FF
        return FF.pfad(punkte, r), not FF.geschlossen(punkte)
    if adj and K.anpassbar(art):
        return K.pfad(art, r, adj), False
    if art not in _FORM_ZEICHNER and K.hat(art):
        return K.pfad(art, r), bool(K.ist_linie(art))
    return None


def _form_ueber_backend(p, art, r, adj, punkte, fuell: str, fuell_art: str, linie: str, strich: float) -> bool:
    """Die Form als Vektorpfad (``ShapeObject``) über das Rendering-Backend zeichnen: Füllung einfarbig oder als Verlauf, Kontur mit runden Ecken."""
    from lunivo_writer.adapter.qt.pfad import pfad_zu_vektor
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.document.objekte import FillStyle, ShapeObject, StrokeStyle
    from lunivo_writer.core.rendering.backend import LinearGradient, Style
    from lunivo_writer.core.geometry import Point
    from lunivo_writer.core.rendering.objekte import heller
    if fuell_art not in ("", "verlauf"):
        return False
    gefunden = _form_pfad(art, r, adj, punkte)
    if gefunden is None:
        return False
    pfad, offen = gefunden
    fc = QColor(fuell).getRgb() if fuell else None
    stil_fuell = None
    if fc is not None and not offen:
        if fuell_art == "verlauf":
            stil_fuell = Style(width=0, filled=True, fill=LinearGradient(Point(r.left(), r.top()), Point(r.left(), r.bottom()), ((0.0, heller(fc, 170)), (1.0, fc))))
        else:
            stil_fuell = Style(color=fc, width=0, filled=True)
    kontur = Style(color=QColor(linie).getRgb(), width=strich, join="round")
    ops = list(pfad_zu_vektor(pfad).ops)
    rb = QtRenderBackend(p)
    if stil_fuell is not None:
        rb.draw_path(ops, stil_fuell, antialias=True)
    rb.draw_path(ops, kontur, antialias=True)
    return True


def _form_text(p, art: str, r, text: str, fuell: str) -> None:
    p.setPen(QColor(Farbe.WEISS if fuell and QColor(fuell).lightness() < 140 else Farbe.SCHWARZ))
    f = p.font(); f.setPointSizeF(12); p.setFont(f)
    if art == TEXTFELD_VERTIKAL:
        p.translate(r.center()); p.rotate(90)
        p.drawText(QRectF(-r.height() / 2 + 6, -r.width() / 2 + 6, r.height() - 12, r.width() - 12),
                   Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, text)
    else:
        p.drawText(r, Qt.AlignCenter | Qt.TextWordWrap, text)


def form_bild(art: str, breite: int = 240, hoehe: int = 140, fuell: str = Farbe.AKZENT_DUNKEL, linie: str = "#1f3864",
              strich: float = 2.0, text: str = "", skala: float = 1.0, adj=None, fuell_art: str = "", punkte=None) -> QImage:
    """``skala``: Bild in dieser Auflösung (Maße und Strich bleiben logisch, das Bild ist ``skala``-mal so groß) — für scharfe freie Formen.
    ``adj``: Parameter der Anpassungsgriffe (``formen_anpassen``); ``fuell_art``: Verlauf der Füllung (``form_pinsel``).
    ``punkte``: Punktliste einer Freiform (``editor/objekte/freiform.py``); sie ersetzt den Pfad der Form."""
    img = _leer(max(1, round(breite * skala)), max(1, round(hoehe * skala)))
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    if skala != 1.0:
        p.scale(skala, skala)
    strich = max(float(strich), 1.0)                         # eine Haarlinie (Word: 0,25–0,75 pt) bleibt auf dem Bildschirm mindestens einen Bildpunkt dick
    pen = QPen(QColor(linie)); pen.setWidthF(strich); pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    r = QRectF(strich, strich, breite - 2 * strich, hoehe - 2 * strich)
    p.setBrush(form_pinsel(fuell, fuell_art, r) if fuell else Qt.NoBrush)
    if not _form_ueber_backend(p, art, r, adj, punkte, fuell, fuell_art, linie, strich):
        _form_zeichnen(p, art, r, adj, punkte)
    if art == TEXTFELD_VERTIKAL:                                     # Textfeld mit senkrecht laufendem Text (90° gedreht)
        p.drawRect(r)
    if text:
        _form_text(p, art, r, text, fuell)
    p.end()
    return img


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
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.rendering import wordart
    from lunivo_writer.dienste.textsatz import standard_engine
    engine = standard_engine()
    b, h = wordart.masse(engine, text, schrift, pt)
    img = _leer(b, h)
    p = QPainter(img)
    wordart.zeichne(QtRenderBackend(p), engine, text, WORDART_VORLAGEN[nr], schrift, pt)
    p.end()
    return img


def wordart_bild(text: str, stil: str = "Verlauf", schrift: str = "Liberation Sans", pt: int = 48, farbe: str = Farbe.AKZENT,
                 vorlage: int | None = None) -> QImage:
    if vorlage is not None:
        return wordart_vorlage_bild(text, vorlage, schrift, pt)
    f = QFont(schrift); f.setPointSizeF(pt); f.setBold(True)
    fm = QFontMetricsF(f)
    b, h = int(fm.horizontalAdvance(text)) + 40, int(fm.height()) + 40
    img = _leer(b, h)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    pfad = QPainterPath()
    pfad.addText(20, 20 + fm.ascent(), f, text)
    if stil == "Welle":
        pfad2 = QPainterPath()
        for poly in pfad.toSubpathPolygons():
            neu = QPolygonF([QPointF(pt_.x(), pt_.y() + math.sin(pt_.x() / 18) * h * 0.08) for pt_ in poly])
            pfad2.addPolygon(neu)
        pfad = pfad2
    if stil == "Schatten":
        p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 90))
        p.translate(4, 4); p.drawPath(pfad); p.translate(-4, -4)
    if stil == "Umriss":
        pen = QPen(QColor(farbe)); pen.setWidthF(2.2); p.setPen(pen); p.setBrush(Qt.NoBrush)
    else:
        p.setPen(Qt.NoPen)
        g = QLinearGradient(0, 0, 0 if stil != "Regenbogen" else b, h if stil != "Regenbogen" else 0)
        if stil == "Regenbogen":
            for i, c in enumerate(("#e03131", "#f08c00", "#ffd43b", Farbe.GRUEN, "#1971c2", "#7048a8")):
                g.setColorAt(i / 5, QColor(c))
        else:
            g.setColorAt(0, QColor(farbe).lighter(150)); g.setColorAt(1, QColor(farbe).darker(150))
        p.setBrush(QBrush(g))
    p.drawPath(pfad)
    p.end()
    return img


# ---- Diagramm --------------------------------------------------------------------------------------------------------
DIAGRAMMARTEN = ["Säulen", "Balken", "Linie", "Kreis"]


def diagramm_bild(art: str, titel: str, kategorien: list[str], reihen: dict[str, list[float]], b: int = 640, h: int = 400) -> QImage:
    """``art``: Untertyp aus ``editor.diagramme.diagramm.TYPEN`` oder einer der früheren Namen (Säulen, Balken, Linie, Kreis)."""
    from lunivo_writer.editor.diagramme import diagramm as D
    return D.bild(art, titel, kategorien, reihen, b, h)


# ---- Piktogramm -------------------------------------------------------------------------------------------------------
def piktogramm_bild(name: str, px: int = 96, farbe: str = "#1f2328") -> QImage:
    from lunivo_writer.kern import piktogramme
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
    """Die Formel als Bild (Vorschau im Fenster „Formel“ und in der Gleichungsgalerie)."""
    d = QTextDocument(); d.setDefaultFont(QFont("DejaVu Serif", pt)); c = QTextCursor(d)
    for t, a in formel_teile(text):
        cf = QTextCharFormat(); cf.setFontItalic(True); cf.setForeground(QColor(farbe))
        if a == "hoch":
            cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        elif a == "tief":
            cf.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        c.insertText(t, cf)
    d.setDocumentMargin(2); d.setTextWidth(-1)
    img = _leer(int(d.idealWidth()) + 8, int(d.size().height()) + 4)
    p = QPainter(img); p.translate(4, 2); d.drawContents(p); p.end()
    return img


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
    """Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen)."""
    f = QFont(); f.setPointSizeF(9)
    fm = QFontMetricsF(f)
    zeilen = [fm.elidedText(name, Qt.ElideMiddle, breite - 8)]
    img = _leer(breite, symbol.height() + 12 + int(fm.height()) * len(zeilen))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    p.drawImage((breite - symbol.width()) // 2, 4, symbol)
    p.setFont(f); p.setPen(QColor(Farbe.TINTE_DUNKEL))
    p.drawText(QRectF(0, symbol.height() + 8, breite, fm.height() + 2), Qt.AlignHCenter, zeilen[0])
    p.end()
    return img


# ---- Text aus Datei ---------------------------------------------------------------------------------------------------------------
def _fremde_bloecke(s, fremd) -> list:
    """Die Blöcke des Haupttextes eines geladenen Dokuments für die Sitzung ``s``: Listen werden angelegt, Bilddaten unter neuen Namen abgelegt."""
    import copy
    from lunivo_writer.core.document.dokument import Absatz, InlineObjekt, Rahmen, Tabelle
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
    from lunivo_writer.dienste.modell_laden import lade_modell
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
        from lunivo_writer.editor.objekte.bildeffekte import gespiegelt
        return gespiegelt(img, waagrecht=art == "horizontal", senkrecht=art == "vertikal")
    return img
