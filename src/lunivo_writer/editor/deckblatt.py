"""Deckblätter (Einfügen ▸ Deckblatt): 17 Gestaltungen in den Gruppen der Vorlage (Artikel, Firma, Lebenslauf, Abschlussarbeit), je im
Hoch- oder Querformat. Keine Oberfläche.

Ein Deckblatt ist ein eigener erster Abschnitt: die Grafik liegt als ganzseitiges Bild hinter dem Text (Wasserzeichen des Abschnitts mit
``"ganzseitig": True``, siehe ``editor/wasserzeichen.py``), die Platzhalter sind gewöhnliche Absätze, die man überschreibt. Das übrige
Dokument beginnt danach auf einer neuen Seite mit seiner bisherigen Einrichtung (Kopf- und Fußzeilen, Wasserzeichen, Format).
Ein neues Deckblatt ersetzt das vorhandene; ``entfernen`` nimmt es wieder heraus.

    zeichnen(p, name, rechteck, mit_text=True)    # Vorschau und Grafik, Seite in beliebigem Maßstab
    einfuegen(ed, name, quer=False)              # ed: DocumentEditor (document(), page)
    entfernen(ed) -> bool
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF, QRadialGradient,
    QTextBlockFormat, QTextCharFormat, QTextCursor, QTextFormat,
)

from lunivo_writer.models.page import mm_to_px

B_DECKBLATT = QTextFormat.UserProperty + 60          # an jedem Absatz des Deckblatts: Name der Gestaltung
B_DECKBLATT_UMBRUCH = QTextFormat.UserProperty + 61  # am ersten Absatz danach: sein Seitenumbruch gehört zum Deckblatt

ARTIKEL, FIRMA, LEBENSLAUF, ARBEIT = "Artikel", "Firma", "Lebenslauf", "Abschlussarbeit"


@dataclass
class Feld:
    """Ein Platzhalter-Absatz: ``y`` = Oberkante als Anteil der Blatthöhe, ``x`` = linker Rand als Anteil der Blattbreite (bei links)."""
    text: str
    pt: float
    y: float
    ausrichtung: str = "links"            # links | mitte | rechts
    fett: bool = False
    farbe: str = "#262626"
    schrift: str = "Liberation Sans"
    x: float = 0.12


@dataclass
class Gestaltung:
    name: str
    gruppe: str
    felder: list[Feld] = field(default_factory=list)


def _kontakt(y: float, farbe: str = "#262626", x: float = 0.12, ausrichtung: str = "links", abstand: float = 0.022) -> list[Feld]:
    return [Feld(t, 9, y + i * abstand, ausrichtung, False, farbe, x=x) for i, t in
            enumerate(("Name: [Ihr Name]", "Telefon: [Telefonnummer]", "E-Mail: [E-Mail-Adresse]", "Adresse: [Straße, PLZ Ort]"))]


def _arbeit(y: float, farbe: str = "#262626") -> list[Feld]:
    return [Feld(t, 10, y + i * 0.03, "mitte", False, farbe) for i, t in
            enumerate(("Name: [Ihr Name]", "Matrikelnummer: [Nummer]", "Studiengang: [Studiengang]", "Betreuer: [Name]",
                       "Abgabedatum: [Datum]"))]


SERIF = "Liberation Serif"

GESTALTUNGEN: list[Gestaltung] = [
    Gestaltung("Mosaik", ARTIKEL, [Feld("[Titel des Artikels]", 20, 0.66, fett=True), Feld("[Untertitel]", 11, 0.72),
                                   Feld("[Kurzfassung: Fassen Sie hier den Inhalt in zwei, drei Sätzen zusammen.]", 9, 0.76, farbe="#595959")]),
    Gestaltung("Himmel", ARTIKEL, [Feld("[Titel des Artikels]", 20, 0.36, "mitte", farbe="#404040", schrift=SERIF),
                                   Feld("[Kurzfassung des Inhalts]", 9, 0.42, "mitte", farbe="#595959"),
                                   Feld("[Autor]", 10, 0.80, "rechts"), Feld("[Datum]", 10, 0.83, "rechts")]),
    Gestaltung("Sonne", ARTIKEL, [Feld("[Titel des Artikels]", 20, 0.74, "mitte", True, schrift=SERIF), Feld("[Autor]", 10, 0.80, "mitte")]),
    Gestaltung("Kopfbalken", ARTIKEL, [Feld("[Firmenname]", 9, 0.07, "links", farbe="#ffffff", x=0.20),
                                       Feld("[Titel in zwei bis fünf Wörtern]", 18, 0.24, "mitte", farbe="#2f6eba"),
                                       Feld("[Kurzfassung des Inhalts]", 9, 0.30, "mitte", farbe="#595959"),
                                       Feld("[Autor]", 10, 0.42, "mitte")]),
    Gestaltung("Wellen", FIRMA, [Feld("LOGO · [Firmenname]", 10, 0.06, farbe="#7b2f8f", x=0.18),
                                 Feld("[Titel des Dokuments]", 18, 0.22, farbe="#7b2f8f", x=0.18),
                                 Feld("[Untertitel]", 10, 0.27, farbe="#a65fb8", x=0.18)]),
    Gestaltung("Blaurand", LEBENSLAUF, [Feld("LEBENSLAUF", 26, 0.20, "mitte", True, "#2f6eba", SERIF)]
               + _kontakt(0.52, x=0.30)),
    Gestaltung("Stadt", LEBENSLAUF, _kontakt(0.08, x=0.30)
               + [Feld("LEBENSLAUF", 32, 0.32, "mitte", True, "#262626", SERIF)]),
    Gestaltung("Notizzettel", LEBENSLAUF, [Feld("LEBENSLAUF", 18, 0.44, "rechts", True, "#5a4a00", SERIF)]
               + _kontakt(0.51, "#3b3200", ausrichtung="rechts")),
    Gestaltung("Sonnenblume", LEBENSLAUF, [Feld("LEBENSLAUF", 30, 0.14, "mitte", True, "#e08a00", SERIF)]
               + _kontakt(0.64, x=0.56)),
    Gestaltung("Grün", LEBENSLAUF, [Feld("LEBENSLAUF", 26, 0.14, "links", True, "#6b8e23", SERIF)] + _kontakt(0.58)),
    Gestaltung("Puzzle", LEBENSLAUF, [Feld("LEBENSLAUF", 24, 0.48, "mitte", True, "#6b8e23", SERIF)] + _kontakt(0.58, x=0.30)),
    Gestaltung("Segel", LEBENSLAUF, _kontakt(0.08, "#ffffff", x=0.18)
               + [Feld("LEBENSLAUF", 28, 0.44, "mitte", True, "#ffffff", SERIF)]),
    Gestaltung("Schlicht", ARBEIT, [Feld("[Name der Hochschule]", 11, 0.12, "mitte", True), Feld("[TITEL DER ARBEIT]", 13, 0.22, "mitte"),
                                    Feld("[Art der Arbeit]", 10, 0.27, "mitte")] + _arbeit(0.50)),
    Gestaltung("Abschlussarbeit", ARBEIT, [Feld("[Name der Hochschule]", 10, 0.10, "mitte"),
                                           Feld("ABSCHLUSSARBEIT", 22, 0.20, "mitte", True, schrift=SERIF),
                                           Feld("[TITEL DER ARBEIT]", 12, 0.27, "mitte")] + _arbeit(0.52)),
    Gestaltung("Rahmen", ARBEIT, [Feld("[Logo der Hochschule]", 9, 0.10, "mitte", farbe="#7f7f7f"),
                                  Feld("ABSCHLUSSARBEIT", 18, 0.22, "mitte", True, "#2f5597", SERIF),
                                  Feld("[TITEL DER ARBEIT]", 11, 0.28, "mitte")] + _arbeit(0.50)),
    Gestaltung("Linien", ARBEIT, [Feld("[Logo der Hochschule]", 9, 0.06, "mitte", farbe="#7f7f7f"),
                                  Feld("ABSCHLUSSARBEIT", 24, 0.14, "mitte", True, "#1f3864", SERIF),
                                  Feld("[TITEL DER ARBEIT]", 11, 0.22, "mitte")] + _arbeit(0.42)),
    Gestaltung("Siegel", ARBEIT, [Feld("[Name der Hochschule]", 12, 0.22, "mitte", True), Feld("BACHELORARBEIT", 10, 0.27, "mitte", True),
                                  Feld("[TITEL DER ARBEIT]", 10, 0.31, "mitte")] + _arbeit(0.42)),
]
NAMEN = [g.name for g in GESTALTUNGEN]
_NACH_NAME = {g.name: g for g in GESTALTUNGEN}


def gestaltung(name: str) -> Gestaltung:
    return _NACH_NAME.get(name, GESTALTUNGEN[0])


# ---- Grafik ----------------------------------------------------------------------------------------------------------------------
def _verlauf(r: QRectF, farben, senkrecht: bool = True) -> QLinearGradient:
    g = QLinearGradient(r.topLeft(), r.bottomLeft() if senkrecht else r.topRight())
    for i, f in enumerate(farben):
        g.setColorAt(i / max(1, len(farben) - 1), QColor(f))
    return g


def _wolken(p: QPainter, r: QRectF, y: float, farbe: str = "#ffffff", n: int = 5) -> None:
    p.setPen(Qt.NoPen); p.setBrush(QColor(farbe))
    for i in range(n):
        cx = r.left() + r.width() * (0.1 + 0.2 * i)
        cy = r.top() + r.height() * (y + 0.03 * math.sin(i * 1.7))
        for dx, dy, s in ((0, 0, 0.09), (0.06, 0.01, 0.07), (-0.06, 0.015, 0.06)):
            p.drawEllipse(QPointF(cx + dx * r.width(), cy + dy * r.height()), s * r.width(), s * r.width() * 0.55)


def _segelboot(p: QPainter, x: float, y: float, s: float) -> None:
    p.setPen(Qt.NoPen); p.setBrush(QColor("#f2f2f2"))
    p.drawPolygon(QPolygonF([QPointF(x, y), QPointF(x, y - 2.2 * s), QPointF(x + 1.1 * s, y)]))
    p.drawPolygon(QPolygonF([QPointF(x - 0.1 * s, y), QPointF(x - 0.1 * s, y - 1.8 * s), QPointF(x - 0.9 * s, y)]))
    p.setBrush(QColor("#d9d9d9")); p.drawRect(QRectF(x - 1.0 * s, y, 2.3 * s, 0.18 * s))


def _puzzle(p: QPainter, x: float, y: float, s: float, farbe: str) -> None:
    pfad = QPainterPath(); pfad.addRect(QRectF(x, y, s, s))
    nase = QPainterPath(); nase.addEllipse(QPointF(x + s, y + s / 2), s * 0.18, s * 0.18)
    nase.addEllipse(QPointF(x + s / 2, y), s * 0.18, s * 0.18)
    p.setPen(QPen(QColor("#ffffff"), max(1.0, s * 0.04))); p.setBrush(QColor(farbe)); p.drawPath(pfad.united(nase))


def _blume(p: QPainter, cx: float, cy: float, s: float) -> None:
    p.setPen(Qt.NoPen); p.setBrush(QColor("#f5b400"))
    for i in range(14):
        a = i * math.tau / 14
        p.save(); p.translate(cx, cy); p.rotate(math.degrees(a))
        p.drawEllipse(QPointF(s * 0.75, 0), s * 0.42, s * 0.14); p.restore()
    p.setBrush(QColor("#5b3a12")); p.drawEllipse(QPointF(cx, cy), s * 0.48, s * 0.48)


def _grafik(p: QPainter, name: str, r: QRectF) -> None:
    """Die Grafik einer Gestaltung (ohne Text) auf das Blatt ``r``."""
    w, h, x0, y0 = r.width(), r.height(), r.left(), r.top()

    def R(x, y, b, hh) -> QRectF:
        return QRectF(x0 + x * w, y0 + y * h, b * w, hh * h)
    p.save(); p.setRenderHint(QPainter.Antialiasing); p.setClipRect(r)
    if name == "Mosaik":
        farben = ("#e8175d", "#f05a28", "#f7b500", "#ff8c00", "#d4145a", "#ff4e50", "#fc913a", "#f9d423")
        n = 9
        for i in range(n):
            for j in range(int(0.56 * h / (w / n))):                     # Mosaik bis gut zur Hälfte, darunter Platz für den Titel
                k = (i * 7 + j * 3) % len(farben)
                gr = 0.9 - 0.05 * ((i + j) % 4)
                p.setPen(Qt.NoPen); p.setBrush(QColor(farben[k]))
                p.drawRect(QRectF(x0 + (i + (1 - gr) / 2) * w / n, y0 + (j + (1 - gr) / 2) * w / n, gr * w / n, gr * w / n))
        p.fillRect(R(0, 0.57, 1, 0.012), QColor("#e8175d"))
    elif name == "Himmel":
        p.fillRect(R(0, 0, 1, 0.55), _verlauf(R(0, 0, 1, 0.55), ("#9fd3f2", "#e6f4fc", "#ffffff")))
        p.setOpacity(0.7); _wolken(p, r, 0.12, "#ffffff", 4); p.setOpacity(1)
    elif name == "Sonne":
        p.fillRect(R(0, 0, 1, 0.68), _verlauf(R(0, 0, 1, 0.68), ("#f7a600", "#fbd34d", "#fff1b8")))
        g = QRadialGradient(QPointF(x0 + 0.7 * w, y0 + 0.36 * h), 0.3 * w)
        g.setColorAt(0, QColor("#ffffff")); g.setColorAt(0.25, QColor("#fff6c9")); g.setColorAt(1, QColor(255, 246, 201, 0))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(g)); p.drawEllipse(QPointF(x0 + 0.7 * w, y0 + 0.36 * h), 0.3 * w, 0.3 * w)
        p.setOpacity(0.8); _wolken(p, r, 0.16, "#ffffff", 5); p.setOpacity(1)
        p.setBrush(QColor("#1a1a1a")); p.drawEllipse(QPointF(x0 + 0.88 * w, y0 + 0.6 * h), 0.03 * w, 0.06 * h)
    elif name == "Kopfbalken":
        p.fillRect(R(0.06, 0.04, 0.88, 0.14), _verlauf(R(0.06, 0.04, 0.88, 0.14), ("#2f6eba", "#8fc1ef"), False))
        p.fillRect(R(0.06, 0.035, 0.88, 0.004), QColor("#9dc3e6"))
    elif name == "Wellen":
        p.setPen(QPen(QColor("#7b2f8f"), max(1.0, w * 0.004))); p.setBrush(Qt.NoBrush)
        p.drawRect(R(0.15, 0.045, 0.28, 0.04))
        for i in range(7):
            pfad = QPainterPath(QPointF(x0, y0 + (0.55 + i * 0.06) * h))
            for k in range(1, 9):
                pfad.quadTo(QPointF(x0 + (k - 0.5) / 8 * w, y0 + (0.52 + i * 0.06 + 0.05 * ((k % 2) * 2 - 1)) * h),
                            QPointF(x0 + k / 8 * w, y0 + (0.55 + i * 0.06) * h))
            p.setPen(QPen(QColor(200, 200, 210, 140), max(1.0, w * 0.01))); p.drawPath(pfad)
    elif name == "Blaurand":
        for x in (0.0, 0.94):
            p.fillRect(R(x, 0, 0.06, 1), QColor("#2f6eba"))
        p.fillRect(R(0, 0, 1, 0.012), QColor("#2f6eba")); p.fillRect(R(0, 0.988, 1, 0.012), QColor("#2f6eba"))
    elif name == "Stadt":
        p.setPen(Qt.NoPen); p.setBrush(QColor("#e3e3e3"))
        hoehen = (0.10, 0.16, 0.08, 0.20, 0.13, 0.18, 0.09, 0.15, 0.22, 0.11, 0.17, 0.12)
        for i, hh in enumerate(hoehen):
            p.drawRect(R(i / len(hoehen), 1 - hh, 1 / len(hoehen) * 0.9, hh))
        p.setBrush(QColor("#f2f2f2"))
        for i, hh in enumerate(hoehen[::-1]):
            p.drawRect(R((i + 0.4) / len(hoehen), 1 - hh * 0.6, 1 / len(hoehen) * 0.6, hh * 0.6))
    elif name == "Notizzettel":
        p.fillRect(r, QColor("#5b8fd6"))
        for i in range(9):
            _puzzle(p, x0 + (0.04 + 0.025 * i + 0.01 * (i % 2)) * w, y0 + (0.05 + 0.03 * i) * h, 0.05 * w, "#f6d32d")
        p.save(); p.translate(x0 + 0.62 * w, y0 + 0.47 * h); p.rotate(-6)
        p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 50)); p.drawRect(QRectF(-0.25 * w + 4, -0.08 * h + 4, 0.52 * w, 0.18 * h))
        p.setBrush(QColor("#f6d32d")); p.drawRect(QRectF(-0.25 * w, -0.08 * h, 0.52 * w, 0.18 * h)); p.restore()
    elif name == "Sonnenblume":
        p.fillRect(R(0, 0, 1, 0.7), _verlauf(R(0, 0, 1, 0.7), ("#5aa9e6", "#bfe1f7", "#ffffff")))
        p.setOpacity(0.9); _wolken(p, r, 0.42, "#ffffff", 5); p.setOpacity(1)
        p.setPen(QPen(QColor("#3c7a1e"), max(1.0, w * 0.02)))
        for cx in (0.2, 0.42):
            p.drawLine(QPointF(x0 + cx * w, y0 + 0.82 * h), QPointF(x0 + cx * w, y0 + h))
        _blume(p, x0 + 0.2 * w, y0 + 0.8 * h, 0.14 * w); _blume(p, x0 + 0.42 * w, y0 + 0.9 * h, 0.1 * w)
    elif name == "Grün":
        p.setPen(Qt.NoPen)
        for i, (fx, fy, s, f) in enumerate(((0.86, 0.62, 0.22, "#c5e17a"), (0.95, 0.72, 0.18, "#9acd32"), (0.80, 0.80, 0.16, "#e2f0b8"))):
            p.save(); p.translate(x0 + fx * w, y0 + fy * h); p.rotate(30 + i * 40); p.setBrush(QColor(f))
            p.drawEllipse(QPointF(0, 0), s * w, s * w * 0.35); p.restore()
    elif name == "Puzzle":
        pfad = QPainterPath(QPointF(x0, y0 + 0.02 * h)); pfad.quadTo(QPointF(x0 + 0.5 * w, y0 + 0.02 * h), QPointF(x0 + w, y0 + 0.24 * h))
        pfad.lineTo(x0 + w, y0); pfad.lineTo(x0, y0); pfad.closeSubpath()
        p.setPen(Qt.NoPen); p.setBrush(_verlauf(R(0, 0, 1, 0.24), ("#3a8dde", "#bfe0fb"), False)); p.drawPath(pfad)
        for i, (fx, fy, f) in enumerate(((0.62, 0.10, "#2e86de"), (0.72, 0.08, "#20bf6b"), (0.66, 0.18, "#f7b731"), (0.78, 0.17, "#2e86de"),
                                         (0.86, 0.12, "#20bf6b"), (0.02, 0.92, "#2e86de"))):
            _puzzle(p, x0 + fx * w, y0 + fy * h, 0.09 * w, f)
    elif name == "Segel":
        p.fillRect(r, _verlauf(r, ("#0b1f44", "#1b3f7a", "#5c86c4")))
        p.fillRect(R(0, 0.82, 1, 0.18), _verlauf(R(0, 0.82, 1, 0.18), ("#2c5aa0", "#0b1f44")))
        _segelboot(p, x0 + 0.3 * w, y0 + 0.86 * h, 0.12 * w); _segelboot(p, x0 + 0.66 * w, y0 + 0.88 * h, 0.09 * w)
        p.setPen(QPen(QColor("#ffffff"), max(1.0, w * 0.003))); p.drawLine(QPointF(x0 + 0.18 * w, y0 + 0.43 * h), QPointF(x0 + 0.82 * w, y0 + 0.43 * h))
    elif name == "Rahmen":
        p.setPen(QPen(QColor("#2f5597"), max(1.0, w * 0.004))); p.setBrush(Qt.NoBrush); p.drawRect(R(0.07, 0.05, 0.86, 0.9))
        p.setPen(QPen(QColor("#9dc3e6"), max(1.0, w * 0.002))); p.drawRect(R(0.38, 0.08, 0.24, 0.04))
    elif name == "Linien":
        p.fillRect(R(0, 0, 1, 0.012), QColor("#2f5597")); p.fillRect(R(0, 0.985, 1, 0.015), QColor("#2f5597"))
        p.setPen(QPen(QColor("#9dc3e6"), max(1.0, w * 0.002))); p.setBrush(Qt.NoBrush); p.drawRect(R(0.38, 0.045, 0.24, 0.035))
    elif name == "Siegel":
        p.setPen(QPen(QColor("#404040"), max(1.0, w * 0.006))); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(x0 + 0.2 * w, y0 + 0.1 * h), 0.06 * w, 0.06 * w)
        p.drawEllipse(QPointF(x0 + 0.2 * w, y0 + 0.1 * h), 0.035 * w, 0.035 * w)
    p.restore()


def _schrift(f: Feld, blatt_hoehe_px: float, quer: bool) -> QFont:
    """Schrift eines Feldes im Maßstab des Blattes (Original: A4 hoch = 1123 Bildpunkte; quer etwas kleiner)."""
    s = QFont(f.schrift); s.setBold(f.fett)
    s.setPixelSize(max(1, round(f.pt * 96 / 72 * blatt_hoehe_px / 1123 * (0.85 if quer else 1.0))))
    return s


def zeichnen(p: QPainter, name: str, r: QRectF, mit_text: bool = True) -> None:
    """Gestaltung ``name`` auf das Blatt ``r`` (weißer Grund, Grafik, auf Wunsch die Platzhalter): für die Galerie."""
    g = gestaltung(name)
    quer = r.width() > r.height()
    p.save()
    p.fillRect(r, QColor("#ffffff"))
    _grafik(p, name, r)
    if mit_text:
        for f in g.felder:
            s = _schrift(f, r.height() if not quer else r.width(), quer)
            p.setFont(s); p.setPen(QColor(f.farbe))
            fm = QFontMetricsF(s)
            x = r.left() + (f.x if f.ausrichtung == "links" else 0.1) * r.width()
            breite = r.right() - 0.1 * r.width() - x
            fl = {"links": Qt.AlignLeft, "mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight}[f.ausrichtung]
            p.drawText(QRectF(x, r.top() + f.y * r.height(), breite, fm.height() * 3), fl | Qt.AlignTop | Qt.TextWordWrap, f.text)
    p.restore()


def grafik_bild(name: str, breite_px: int, hoehe_px: int) -> QImage:
    img = QImage(breite_px, hoehe_px, QImage.Format_ARGB32)
    img.fill(QColor("#ffffff"))
    p = QPainter(img)
    _grafik(p, name, QRectF(0, 0, breite_px, hoehe_px))
    p.end()
    return img


# ---- Einfügen und Entfernen ------------------------------------------------------------------------------------------------------
def hat_deckblatt(doc) -> bool:
    return doc.firstBlock().blockFormat().hasProperty(B_DECKBLATT)


def entfernen(ed) -> bool:
    """Das Deckblatt (erster Abschnitt mit ``B_DECKBLATT``) herausnehmen; das Dokument bekommt die Einrichtung des zweiten Abschnitts."""
    from lunivo_writer.editor import abschnitte as AB
    doc = ed.document()
    if not hat_deckblatt(doc) or AB.anzahl(doc) < 2:
        return False
    rest = AB.einrichtung(doc, ed.page, 1)
    if (rest.watermark or {}).get("deckblatt_leer"):
        rest.watermark = None
    elif rest.watermark:
        rest.watermark = {k: v for k, v in rest.watermark.items() if k != "abschnitt"}
    c = QTextCursor(doc)
    c.beginEditBlock()
    c.setPosition(0); c.setPosition(AB.beginn(doc, 1), QTextCursor.KeepAnchor); c.removeSelectedText()
    bf = c.blockFormat()
    if bf.hasProperty(B_DECKBLATT_UMBRUCH):
        bf.clearProperty(B_DECKBLATT_UMBRUCH); bf.setPageBreakPolicy(QTextFormat.PageBreak_Auto); c.setBlockFormat(bf)
    c.endEditBlock()
    ed.page = rest
    doc.setModified(True)
    return True


def einfuegen(ed, name: str, quer: bool = False) -> None:
    """Deckblatt ``name`` als ersten Abschnitt an den Anfang setzen (ersetzt ein vorhandenes)."""
    from lunivo_writer.editor import abschnitte as AB
    entfernen(ed)
    doc = ed.document()
    g = gestaltung(name)
    alt = copy.deepcopy(ed.page)
    rest = copy.deepcopy(alt)                           # das Dokument nach dem Deckblatt: alles wie bisher, Wasserzeichen nur dort
    rest.watermark = {**(alt.watermark or {}), "abschnitt": True} if alt.watermark else {"abschnitt": True, "deckblatt_leer": True}
    deck = copy.deepcopy(alt)
    deck.set_orientation(quer)
    for hf in ("header", "footer", "first_header", "first_footer"):
        getattr(deck, hf).text = ""
    deck.diff_first = False
    bw, bh = mm_to_px(deck.width_mm), mm_to_px(deck.height_mm)
    deck.watermark = {"bild": _bild_text(grafik_bild(name, round(bw), round(bh))), "bild_name": f"Deckblatt {name}", "ganzseitig": True,
                      "auswaschen": False, "transparenz": 0, "winkel": 0, "abschnitt": True}
    c = QTextCursor(doc)
    c.beginEditBlock()
    c.setPosition(0)
    c.insertBlock(); c.movePosition(QTextCursor.PreviousBlock)        # neuer erster Absatz; der bisherige rückt nach unten
    oben_px = mm_to_px(deck.margin_top_mm)
    links_px, rechts_px = mm_to_px(deck.margin_left_mm), mm_to_px(deck.margin_right_mm)
    y = oben_px
    luecke = g.felder[0].y * bh - oben_px
    if luecke > 2:                                      # Qt lässt den oberen Abstand eines Absatzes oben auf der Seite weg: ein Abstandshalter
        bf = QTextBlockFormat(); bf.setLineHeight(luecke, QTextBlockFormat.LineHeightTypes.FixedHeight.value); bf.setProperty(B_DECKBLATT, name)
        cf = QTextCharFormat(); cf.setFontPointSize(1)
        c.setBlockFormat(bf); c.setBlockCharFormat(cf)
        c.insertText(" ", cf)                           # ein leerer erster Absatz verlöre beim Kopieren (Druck, PDF) seine Höhe
        y += luecke
    for i, f in enumerate(g.felder):
        s = _schrift(f, bh if not quer else bw, quer)
        ziel = f.y * bh
        bf = QTextBlockFormat()
        bf.setTopMargin(max(0.0, ziel - y))
        bf.setAlignment({"links": Qt.AlignLeft, "mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight}[f.ausrichtung])
        if f.ausrichtung == "links":
            bf.setLeftMargin(max(0.0, f.x * bw - links_px))
        else:
            bf.setLeftMargin(max(0.0, 0.1 * bw - links_px)); bf.setRightMargin(max(0.0, 0.1 * bw - rechts_px))
        bf.setProperty(B_DECKBLATT, name)
        cf = QTextCharFormat(); cf.setFont(s); cf.setForeground(QColor(f.farbe))
        cf.setFontPointSize(f.pt * (0.85 if quer else 1.0))
        if i or luecke > 2:
            c.insertBlock(bf, cf)
        else:
            c.setBlockFormat(bf); c.setBlockCharFormat(cf)
        c.insertText(f.text, cf)
        y = max(y, ziel) + QFontMetricsF(s).height() * 1.15
    bf = c.blockFormat(); bf.setProperty(AB.B_ABSCHNITT, AB.eintrag("naechste", rest)); c.setBlockFormat(bf)   # Deckblatt endet hier
    c.movePosition(QTextCursor.NextBlock)               # das Dokument beginnt auch in der Bearbeitungsansicht auf einem neuen Blatt
    bf = c.blockFormat()
    if not bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore:
        bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore); bf.setProperty(B_DECKBLATT_UMBRUCH, True); c.setBlockFormat(bf)
    c.endEditBlock()
    ed.page = deck
    doc.setModified(True)


def _bild_text(img: QImage) -> str:
    from lunivo_writer.editor.wasserzeichen import bild_zu_text
    return bild_zu_text(img)
