"""SmartArt (in WPS „WPSArt“): Listen, Prozesse, Hierarchien, Zyklen und Pyramiden aus einem eingerückten Text.

Das Objekt ist ein freies Objekt (``frei_objekt``, Art „smartart“) mit Rahmen, acht Griffen und der Schnellleiste daneben; seine Daten sind
Layout, Text (eine Zeile je Form, Einrückung = Ebene), Farbschema, Stil, Richtung und die eigenen Angaben einzelner Formen (``knoten``:
Füllung, Kontur, Textfarbe, Größe …). Beim Zeichnen merkt sich jede Form, wo sie liegt (``knoten_rechtecke``) — so lässt sich im Dokument eine
einzelne Form anklicken, per Doppelklick beschreiben und über den Reiter „WPSArt-Design“ umbauen (``form_einfuegen``, ``level``,
``verschieben``, ``entfernen``). Kein HTML: gezeichnet wird mit QPainter.
Grenze: In DOCX steht es als Bild (Titel „lunivo:…“); Word und LibreOffice zeigen das Bild, bearbeiten es aber nicht als SmartArt."""
from __future__ import annotations

import json
import math

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, QUrl
from PySide6.QtGui import (QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF, QTextDocument,
                           QTextImageFormat)

from lunivo_writer.editor.zusatz import P_OBJEKT

from lunivo_writer.core.farben import Farbe
LAYOUTS = ["Liste", "Prozess", "Hierarchie", "Zyklus", "Pyramide", "Spalten", "Gruppen", "Matrix", "Chevron", "Radial", "Zielscheibe", "Trichter",
           "Zeitachse", "Stufen"]
FARBEN = {"Blau": (Farbe.AKZENT, "#5b9bd5", "#a9c9ea"), "Grün": ("#2d8a4e", "#5fb877", "#b4dfc0"), "Orange": ("#e67700", "#f4a259", "#fbd5ae"),
          "Grau": ("#495057", Farbe.GRAU, "#ced4da"), "Bunt": (Farbe.AKZENT, "#e67700", "#2d8a4e")}
MUSTER = {"Liste": "Erster Punkt\nZweiter Punkt\nDritter Punkt", "Prozess": "Planen\nUmsetzen\nPrüfen\nAbschließen",
          "Hierarchie": "Leitung\n  Team A\n    Aufgabe 1\n  Team B", "Zyklus": "Idee\nEntwurf\nTest\nStart", "Pyramide": "Spitze\nMitte\nBasis",
          "Spalten": "Planung\n  Ziele\n  Budget\nUmsetzung\n  Team\n  Termine\nAbschluss\n  Bericht",
          "Gruppen": "Vertrieb\n  Inland\n  Ausland\nTechnik\n  Entwicklung\n  Support",
          "Matrix": "Stärken\nSchwächen\nChancen\nRisiken", "Chevron": "Analyse\nKonzept\nBau\nÜbergabe",
          "Radial": "Kern\nIdee A\nIdee B\nIdee C\nIdee D", "Zielscheibe": "Ziel\nMaßnahme\nAufgabe", "Trichter": "Interessenten\nAngebote\nAufträge",
          "Zeitachse": "2024\n2025\n2026\n2027", "Stufen": "Einstieg\nAufbau\nProfi\nExperte"}
STILE = ["Einfach", "Hell", "Umriss", "Verlauf", "Schatten"]                 # die Stil-Galerie des Reiters WPSArt-Design
HIERARCHIE = {"standard": "Standard", "beide": "Beide", "links": "Links hängend", "rechts": "Rechts hängend"}
EINFUEGEN = {"danach": "Form danach hinzufügen", "davor": "Form davor hinzufügen", "darueber": "Form darüber hinzufügen",
             "darunter": "Form darunter hinzufügen", "assistent": "Assistent hinzufügen"}
LEER = "[Text]"                                                            # eine neue Form ohne Text (wie in WPS)
KNOTEN_SCHLUESSEL = ("fuell", "rand", "textfarbe", "pt", "fett", "kursiv", "schatten", "gross")


def punkte(text: str) -> list[tuple[int, str]]:
    """[(Ebene, Text)] — die Ebene ergibt sich aus der Einrückung (je zwei Leerzeichen oder ein Tabulator)."""
    out = []
    for zeile in text.splitlines():
        if not zeile.strip():
            continue
        roh = zeile.replace("\t", "  ")
        out.append(((len(roh) - len(roh.lstrip(" "))) // 2, zeile.strip()))
    return out


# ---- Zeichnen: jede Form merkt sich ihre Lage und trägt ihre eigenen Angaben --------------------------------------------------------------
_LAUF: dict | None = None                                                  # nur während ``_zeichnen``


def _farbe(daten: dict, ebene: int) -> QColor:
    f = FARBEN.get(daten.get("farben", "Blau"), FARBEN["Blau"])
    return QColor(f[min(ebene, 2)] if daten.get("farben") != "Bunt" else f[ebene % 3])


def _text_farbe(c: QColor) -> QColor:
    return QColor(Farbe.WEISS) if c.lightness() < 150 else QColor(Farbe.TINTE_DUNKEL)


def _index(text: str, i: int | None) -> int | None:
    """Welche Form wird gerade gezeichnet? ``i`` direkt, sonst die erste noch nicht gezeichnete mit diesem Text."""
    L = _LAUF
    if L is None:
        return i
    if i is None:
        i = next((j for j in L["frei"] if L["pts"][j][1] == text), None)
    if i is not None and i in L["frei"]:
        L["frei"].remove(i)
    return i


def _eigen(i: int | None) -> dict:
    return (_LAUF["knoten"].get(str(i)) or {}) if _LAUF is not None and i is not None else {}


def _merken(p: QPainter, r: QRectF, i: int | None) -> None:
    if _LAUF is not None and i is not None and i not in _LAUF["rects"]:
        m, s = p.transform().mapRect(r), _LAUF["skala"]
        _LAUF["rects"][i] = QRectF(m.x() / s, m.y() / s, m.width() / s, m.height() / s)


def _gross(r: QRectF, o: dict) -> QRectF:
    g = float(o.get("gross") or 1.0)
    if abs(g - 1.0) < 1e-3:
        return r
    c = r.center()
    return QRectF(c.x() - r.width() * g / 2, c.y() - r.height() * g / 2, r.width() * g, r.height() * g)


def _flaeche(p: QPainter, pfad: QPainterPath, c: QColor, i: int | None) -> QColor:
    """Füllt eine Form im Stil des SmartArt (Einfach, Hell, Umriss, Verlauf, Schatten) mit ihren eigenen Angaben. → die sichtbare Füllfarbe."""
    o = _eigen(i)
    stil = _LAUF["stil"] if _LAUF else 0
    if o.get("fuell"):
        c = QColor(o["fuell"])
    rand = QColor(o["rand"]) if o.get("rand") else c.darker(125)
    if stil == 4 or o.get("schatten"):
        p.save(); p.translate(3, 4); p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 70)); p.drawPath(pfad); p.restore()
    sichtbar = c
    if stil == 1 and not o.get("fuell"):
        sichtbar = c.lighter(135); p.setPen(QPen(c, 1.2)); p.setBrush(sichtbar)
    elif stil == 2 and not o.get("fuell"):
        sichtbar = QColor(Farbe.WEISS); p.setPen(QPen(rand if o.get("rand") else c, 2.2)); p.setBrush(sichtbar)
    elif stil == 3:
        b = pfad.boundingRect()
        g = QLinearGradient(b.topLeft(), b.bottomLeft()); g.setColorAt(0, c.lighter(140)); g.setColorAt(1, c.darker(110))
        p.setPen(QPen(rand, 1.2)); p.setBrush(QBrush(g))
    else:
        p.setPen(QPen(rand, 1.5)); p.setBrush(QBrush(c))
    if o.get("rand") == "keine":
        p.setPen(Qt.NoPen)
    p.drawPath(pfad)
    return sichtbar


def _schrift(p: QPainter, r: QRectF, t: str, grund: QColor, o: dict, groesse: float) -> None:
    """Text in der Form; im Layout „von rechts nach links“ gespiegelt gesetzt, die Schrift selbst bleibt lesbar."""
    f = QFont(p.font()); f.setPointSizeF(float(o.get("pt") or groesse)); f.setBold(bool(o.get("fett"))); f.setItalic(bool(o.get("kursiv")))
    p.setFont(f)
    p.setPen(QColor(o["textfarbe"]) if o.get("textfarbe") else _text_farbe(grund))
    if p.transform().m11() < 0:
        m, s = p.transform().mapRect(r), (_LAUF["skala"] if _LAUF else 1.0)
        p.save(); p.resetTransform(); p.scale(s, s)
        p.drawText(QRectF(m.x() / s, m.y() / s, m.width() / s, m.height() / s), Qt.AlignCenter | Qt.TextWordWrap, t)
        p.restore()
    else:
        p.drawText(r, Qt.AlignCenter | Qt.TextWordWrap, t)


def _kasten(p: QPainter, r: QRectF, text: str, c: QColor, rund: float = 8, i: int | None = None) -> None:
    i = _index(text, i) if (text or i is not None) else None
    o = _eigen(i)
    r = _gross(r, o)
    pfad = QPainterPath(); pfad.addRoundedRect(r, rund, rund)
    grund = _flaeche(p, pfad, c, i)
    if text:
        _schrift(p, r.adjusted(6, 3, -6, -3), text, grund, o, 11)
    _merken(p, r, i)


def _form(p: QPainter, poly: QPolygonF, c: QColor, i: int) -> QColor:
    """Eine Vieleck-Form (Pfeil, Trapez, Ring …) für die Form ``i``. → die sichtbare Füllfarbe (für den Text)."""
    g = float(_eigen(i).get("gross") or 1.0)
    if abs(g - 1.0) > 1e-3:                                                 # Größer/Kleiner: um die Mitte der Form
        m = poly.boundingRect().center()
        poly = QPolygonF([QPointF(m.x() + (q.x() - m.x()) * g, m.y() + (q.y() - m.y()) * g) for q in poly])
    pfad = QPainterPath(); pfad.addPolygon(poly); pfad.closeSubpath()
    return _flaeche(p, pfad, c, i)


def _pfeil(p: QPainter, a: QPointF, b: QPointF, c: QColor) -> None:
    p.setPen(QPen(c, 2)); p.drawLine(a, b)
    w = math.atan2(b.y() - a.y(), b.x() - a.x())
    for d in (0.45, -0.45):
        p.drawLine(b, QPointF(b.x() - 9 * math.cos(w - d), b.y() - 9 * math.sin(w - d)))


def _bild(b: float, h: float) -> tuple[QImage, QPainter]:
    s = _LAUF["skala"] if _LAUF else 1.0
    img = QImage(max(1, int(b * s)), max(1, int(h * s)), QImage.Format_ARGB32); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
    p.scale(s, s)
    if _LAUF and _LAUF["rtl"]:                                              # Layout von rechts nach links: gespiegelt
        p.translate(b, 0); p.scale(-1, 1)
    return img, p


def _text(p: QPainter, r: QRectF, t: str, c: QColor, groesse: float = 11, i: int | None = None) -> None:
    i = _index(t, i)
    _schrift(p, r, t, c, _eigen(i), groesse)
    _merken(p, r, i)


def _gruppen(pts: list[tuple[int, str]]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Index, Text, [(Index, Text)])]."""
    out: list = []
    for j, (e, t) in enumerate(pts):
        if e == 0 or not out:
            out.append((j, t, []))
        else:
            out[-1][2].append((j, t))
    return out


def _bunt(daten: dict, i: int) -> QColor:
    return _farbe(daten, i if daten.get("farben") == "Bunt" else 0)


def _liste(daten: dict, pts, b: int) -> QImage:
    img, p = _bild(b, 16 + len(pts) * 46)
    for i, (e, t) in enumerate(pts):
        _kasten(p, QRectF(8 + e * 36, 8 + i * 46, b - 16 - e * 36, 38), t, _farbe(daten, e), i=i)
    p.end()
    return img


def _prozess(daten: dict, pts, b: int) -> QImage:
    je = 4
    n = min(len(pts), je)
    bw = (b - 16 - (n - 1) * 34) / n
    img, p = _bild(b, 16 + -(-len(pts) // je) * 96)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, je)
        r = QRectF(8 + s * (bw + 34), 8 + z * 96, bw, 80)
        _kasten(p, r, t, _bunt(daten, i), i=i)
        if i < len(pts) - 1 and s < je - 1:
            _pfeil(p, QPointF(r.right() + 4, r.center().y()), QPointF(r.right() + 30, r.center().y()), QColor(Farbe.GRAU))
    p.end()
    return img


def _hierarchie(daten: dict, pts, b: int) -> QImage:
    """Organigramm: Eltern mittig über ihren Kindern, verbunden mit Winkellinien. Layout „Beide“/„Links hängend“/„Rechts hängend“ (wie WPS):
    die letzten Kinder einer Form stehen untereinander an einer senkrechten Linie, statt nebeneinander."""
    modus = daten.get("hierarchie", "standard")
    baum: list[dict] = []
    stapel: list[dict] = []
    for i, (e, t) in enumerate(pts):
        n = {"t": t, "e": e, "i": i, "k": []}
        while stapel and stapel[-1]["e"] >= e:
            stapel.pop()
        (stapel[-1]["k"] if stapel else baum).append(n)
        stapel.append(n)
    bw, bh, sx, sy = 112.0, 48.0, 12.0, 34.0

    def haengt(n):
        return modus != "standard" and n["k"] and all(not k["k"] for k in n["k"])

    def mass(n) -> tuple[float, float]:
        if haengt(n):
            z = len(n["k"]) if modus != "beide" else -(-len(n["k"]) // 2)
            w = bw + (bw * 0.85 + 24 if modus != "beide" else bw * 0.85 * 2 + 24 - bw)
            n["w"], n["h"] = max(bw, w), bh + 18 + z * (bh * 0.8 + 12)
        elif n["k"]:
            for k in n["k"]:
                mass(k)
            n["w"] = max(bw, sum(k["w"] for k in n["k"]) + sx * (len(n["k"]) - 1))
            n["h"] = bh + sy + max(k["h"] for k in n["k"])
        else:
            n["w"], n["h"] = bw, bh
        return n["w"], n["h"]
    for w in baum:
        mass(w)
    breite = max(float(b), sum(w["w"] for w in baum) + sx * (len(baum) - 1) + 16)
    img, p = _bild(breite, 16 + max(w["h"] for w in baum))
    linie = QPen(QColor(Farbe.GRAU), 1.5)

    def setze(n, x, y):
        if haengt(n):
            mitte = x + n["w"] / 2 if modus == "beide" else (x + bw / 2 if modus == "rechts" else x + n["w"] - bw / 2)
            r = QRectF(mitte - bw / 2, y, bw, bh)
            kb, kh = bw * 0.85, bh * 0.8
            unten = y + bh + 18 + (kh + 12) * ((len(n["k"]) if modus != "beide" else -(-len(n["k"]) // 2)) - 1) + kh / 2
            p.setPen(linie); p.drawLine(QPointF(mitte, r.bottom()), QPointF(mitte, unten))
            for j, k in enumerate(n["k"]):
                zeile = j if modus != "beide" else j // 2
                rechts = modus == "rechts" or (modus == "beide" and j % 2 == 1)
                ky = y + bh + 18 + zeile * (kh + 12)
                kr = QRectF(mitte + 12 if rechts else mitte - 12 - kb, ky, kb, kh)
                p.setPen(linie); p.drawLine(QPointF(mitte, kr.center().y()), QPointF(kr.left() if rechts else kr.right(), kr.center().y()))
                _kasten(p, kr, k["t"], _farbe(daten, k["e"]), 4, i=k["i"])
            _kasten(p, r, n["t"], _farbe(daten, n["e"]), 4, i=n["i"])
            return mitte
        if not n["k"]:
            _kasten(p, QRectF(x + (n["w"] - bw) / 2, y, bw, bh), n["t"], _farbe(daten, n["e"]), 4, i=n["i"])
            return x + n["w"] / 2
        innen = sum(k["w"] for k in n["k"]) + sx * (len(n["k"]) - 1)
        kx = x + (n["w"] - innen) / 2
        mitten = []
        for k in n["k"]:
            mitten.append(setze(k, kx, y + bh + sy))
            kx += k["w"] + sx
        mitte = (mitten[0] + mitten[-1]) / 2
        quer = y + bh + sy / 2
        p.setPen(linie)
        p.drawLine(QPointF(mitte, y + bh), QPointF(mitte, quer))
        p.drawLine(QPointF(mitten[0], quer), QPointF(mitten[-1], quer))
        for m in mitten:
            p.drawLine(QPointF(m, quer), QPointF(m, y + bh + sy))
        _kasten(p, QRectF(mitte - bw / 2, y, bw, bh), n["t"], _farbe(daten, n["e"]), 4, i=n["i"])
        return mitte
    x = (breite - (sum(w["w"] for w in baum) + sx * (len(baum) - 1))) / 2
    for w in baum:
        setze(w, x, 8)
        x += w["w"] + sx
    p.end()
    return img


def _zyklus(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    durchm = 380
    img, p = _bild(b, durchm + 16)
    mx, my, rad = b / 2, (durchm + 16) / 2, (durchm - 90) / 2
    pos = [QPointF(mx + rad * 1.35 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), my + rad * math.sin(-math.pi / 2 + 2 * math.pi * i / n))
           for i in range(n)]
    for i in range(n):
        a, z = pos[i], pos[(i + 1) % n]
        if n > 1:
            w = math.atan2(z.y() - a.y(), z.x() - a.x())
            _pfeil(p, QPointF(a.x() + 62 * math.cos(w), a.y() + 30 * math.sin(w)), QPointF(z.x() - 66 * math.cos(w), z.y() - 33 * math.sin(w)),
                   QColor(Farbe.GRAU))
    for i, (_e, t) in enumerate(pts):
        _kasten(p, QRectF(pos[i].x() - 56, pos[i].y() - 26, 112, 52), t, _bunt(daten, i), 26, i=i)
    p.end()
    return img


def _pyramide(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    zh = 54
    img, p = _bild(b, 16 + n * zh)
    mitte = b / 2
    for i, (_e, t) in enumerate(pts):
        oben, unten = 8 + i * zh, 8 + (i + 1) * zh - 4
        bo, bu = (i / n) * (b - 16) / 2, ((i + 1) / n) * (b - 16) / 2
        c = _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2))
        grund = _form(p, QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)]), c, i)
        _text(p, QRectF(mitte - bu * 0.8, oben, bu * 1.6, unten - oben), t, grund, i=i)
    p.end()
    return img


def _spalten(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    n = len(g)
    bw = (b - 16 - (n - 1) * 10) / n
    zeilen = max(len(k) for _i, _t, k in g)
    img, p = _bild(b, 16 + 50 + max(1, zeilen) * 34 + 14)
    hoehe = 16 + 50 + max(1, zeilen) * 34 + 14
    for s, (i, t, kinder) in enumerate(g):
        x = 8 + s * (bw + 10)
        c = _bunt(daten, s)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c.lighter(185)))
        p.drawRoundedRect(QRectF(x, 36, bw, hoehe - 44), 6, 6)
        _kasten(p, QRectF(x, 8, bw, 44), t, c, i=i)
        for j, (ki, k) in enumerate(kinder):
            _text(p, QRectF(x + 4, 60 + j * 34, bw - 8, 30), k, c.lighter(185), i=ki)
    p.end()
    return img


def _gruppenliste(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    img, p = _bild(b, 16 + len(g) * 62)
    for s, (i, t, kinder) in enumerate(g):
        y = 8 + s * 62
        c = _bunt(daten, s)
        _kasten(p, QRectF(8, y, 130, 54), t, c, i=i)
        n = max(1, len(kinder))
        kw = (b - 16 - 146 - (n - 1) * 8) / n
        for j, (ki, k) in enumerate(kinder):
            _kasten(p, QRectF(146 + j * (kw + 8), y + 6, kw, 42), k, _farbe(daten, 1 if daten.get("farben") != "Bunt" else s), 6, i=ki)
    p.end()
    return img


def _matrix(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    sp = 2 if n > 1 else 1
    zl = -(-n // sp)
    kw, kh = (b - 16 - (sp - 1) * 10) / sp, 84
    img, p = _bild(b, 16 + zl * kh + (zl - 1) * 10)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, sp)
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 0 if (z + s) % 2 == 0 else 1)
        _kasten(p, QRectF(8 + s * (kw + 10), 8 + z * (kh + 10), kw, kh), t, c, 10, i=i)
    p.end()
    return img


def _chevron(daten: dict, pts, b: int) -> QImage:
    je = 4
    zeilen = -(-len(pts) // je)
    n = min(len(pts), je)
    sp = 14.0
    w = (b - 16 + (n - 1) * 8) / n                                          # Pfeile greifen ineinander
    img, p = _bild(b, 16 + zeilen * 84)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, je)
        x, y, h = 8 + s * (w - 8), 8 + z * 84, 72
        poly = QPolygonF([QPointF(x, y), QPointF(x + w - sp, y), QPointF(x + w, y + h / 2), QPointF(x + w - sp, y + h), QPointF(x, y + h),
                          QPointF(x + sp, y + h / 2)])
        grund = _form(p, poly, _bunt(daten, i), i)
        _text(p, QRectF(x + sp + 4, y + 4, w - 2 * sp - 8, h - 8), t, grund, 10.5, i=i)
    p.end()
    return img


def _radial(daten: dict, pts, b: int) -> QImage:
    h = 380
    img, p = _bild(b, h)
    mx, my = b / 2, h / 2
    rest = pts[1:]
    n = len(rest)
    pos = [QPointF(mx + 190 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), my + 135 * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(n)]
    for q in pos:
        p.setPen(QPen(QColor(Farbe.GRAU), 2)); p.drawLine(QPointF(mx, my), q)
    for i, q in enumerate(pos):
        _kasten(p, QRectF(q.x() - 56, q.y() - 24, 112, 48), rest[i][1], _farbe(daten, 1 if daten.get("farben") != "Bunt" else i + 1), 24, i=i + 1)
    _kasten(p, QRectF(mx - 62, my - 40, 124, 80), pts[0][1], _farbe(daten, 0), 40, i=0)
    p.end()
    return img


def _zielscheibe(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    band = 34.0
    rad = max(150.0, band * n + 20)
    img, p = _bild(b, 2 * rad + 16)
    mx, my = b / 2, rad + 8
    for i, (_e, t) in enumerate(pts):
        r = rad - i * (rad - 20) / n
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, min(i, 2)).lighter(100 + 25 * max(0, i - 2))
        pfad = QPainterPath(); pfad.addEllipse(QPointF(mx, my), r, r)
        grund = _flaeche(p, pfad, c, i)
        _text(p, QRectF(mx - r * 0.7, my - r + 4, r * 1.4, (rad - 20) / n - 6 if n > 1 else 40), t, grund, i=i)
    p.end()
    return img


def _trichter(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    zh = 54
    img, p = _bild(b, 16 + n * zh)
    mitte, halb = b / 2, (b - 16) / 2
    for i, (_e, t) in enumerate(pts):
        oben, unten = 8 + i * zh, 8 + (i + 1) * zh - 4
        bo, bu = halb * (1 - i / (n + 1)), halb * (1 - (i + 1) / (n + 1))
        c = _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2))
        grund = _form(p, QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)]), c, i)
        _text(p, QRectF(mitte - bu * 0.85, oben, bu * 1.7, unten - oben), t, grund, i=i)
    p.end()
    return img


def _zeitachse(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    img, p = _bild(b, 220)
    y = 110.0
    p.setPen(QPen(QColor(Farbe.GRAU), 3)); p.drawLine(QPointF(8, y), QPointF(b - 8, y))
    raster = (b - 16) / n
    for i, (_e, t) in enumerate(pts):
        x = 8 + raster * (i + 0.5)
        c = _bunt(daten, i)
        oben = i % 2 == 0
        p.setPen(QPen(QColor(Farbe.GRAU), 1.5)); p.drawLine(QPointF(x, y), QPointF(x, y - 26 if oben else y + 26))
        _kasten(p, QRectF(x - min(raster - 6, 120) / 2, y - 80 if oben else y + 26, min(raster - 6, 120), 54), t, c, i=i)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c)); p.drawEllipse(QPointF(x, y), 8, 8)
    p.end()
    return img


def _stufen(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    sh = 44
    h = 16 + n * sh + 20
    img, p = _bild(b, h)
    sw = (b - 16) / n
    for i, (_e, t) in enumerate(pts):
        r = QRectF(8 + i * sw, h - 8 - (i + 1) * sh, sw - 4, (i + 1) * sh)
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, min(i, 2))
        _kasten(p, r, "", c, 4, i=i)
        _text(p, QRectF(r.left() + 2, r.top() + 2, r.width() - 4, 38), t, QColor(_eigen(i).get("fuell") or c), 10.5, i=i)
    p.end()
    return img


_ZEICHNER = {"Liste": _liste, "Prozess": _prozess, "Hierarchie": _hierarchie, "Zyklus": _zyklus, "Pyramide": _pyramide, "Spalten": _spalten,
             "Gruppen": _gruppenliste, "Matrix": _matrix, "Chevron": _chevron, "Radial": _radial, "Zielscheibe": _zielscheibe,
             "Trichter": _trichter, "Zeitachse": _zeitachse, "Stufen": _stufen}


def _zeichnen(daten: dict, skala: float = 1.0) -> tuple[QImage, dict]:
    global _LAUF
    pts = punkte(daten.get("text", "")) or [(0, LEER)]
    _LAUF = {"pts": pts, "frei": list(range(len(pts))), "rects": {}, "knoten": daten.get("knoten") or {}, "stil": int(daten.get("stil", 0) or 0),
             "rtl": bool(daten.get("rtl")), "skala": float(skala)}
    try:
        img = _ZEICHNER.get(daten.get("layout", "Liste"), _liste)(daten, pts, 520)
        return img, _LAUF["rects"]
    finally:
        _LAUF = None


def zeichnen(daten: dict, skala: float = 1.0) -> QImage:
    """Das Bild des SmartArt (``skala`` > 1: in höherer Auflösung, die logische Größe ist Bildgröße / ``skala``)."""
    return _zeichnen(daten, skala)[0]


_RECHTECKE: dict = {}


def knoten_rechtecke(daten: dict) -> tuple[QSizeF, dict]:
    """(Logische Größe des Bildes, {Index der Form: Rechteck darin}) — wo welche Form liegt, für Anklicken, Griffe und Schreiben."""
    schl = json.dumps(daten, sort_keys=True, ensure_ascii=False)
    if schl not in _RECHTECKE:
        if len(_RECHTECKE) > 64:
            _RECHTECKE.clear()
        img, rects = _zeichnen(daten, 1.0)
        ganz = QRectF(0, 0, img.width(), img.height())                      # eine vergrößerte Form ragt nie aus dem Bild heraus
        _RECHTECKE[schl] = (QSizeF(img.width(), img.height()), {i: q.intersected(ganz) for i, q in rects.items()})
    return _RECHTECKE[schl]


# ---- Umbauen: Formen einfügen, verschieben, Ebenen ändern (die eigenen Angaben ziehen mit) ---------------------------------------------------
def _knoten(daten: dict) -> list[dict]:
    o = daten.get("knoten") or {}
    return [{"e": e, "t": t, "o": dict(o.get(str(i)) or {})} for i, (e, t) in enumerate(punkte(daten.get("text", "")))]


def _aus(daten: dict, liste: list[dict]) -> dict:
    neu = dict(daten)
    neu["text"] = "\n".join("  " * n["e"] + n["t"] for n in liste)
    neu["knoten"] = {str(i): n["o"] for i, n in enumerate(liste) if n["o"]}
    if not neu["knoten"]:
        neu.pop("knoten")
    return neu


def _ende(liste: list[dict], i: int) -> int:
    """Index hinter der Form ``i`` und allem, was unter ihr eingerückt ist."""
    j = i + 1
    while j < len(liste) and liste[j]["e"] > liste[i]["e"]:
        j += 1
    return j


def form_einfuegen(daten: dict, i: int | None, wo: str = "danach") -> tuple[dict, int]:
    """Neue Form „[Text]“ danach, davor, darüber, darunter oder als Assistent der Form ``i`` (ohne Wahl: am Ende). → (Daten, neuer Index)."""
    liste = _knoten(daten)
    if i is None or not 0 <= i < len(liste):
        liste.append({"e": 0, "t": LEER, "o": {}})
        return _aus(daten, liste), len(liste) - 1
    e = liste[i]["e"]
    if wo == "davor":
        liste.insert(i, {"e": e, "t": LEER, "o": {}}); j = i
    elif wo == "darueber":
        for n in liste[i:_ende(liste, i)]:
            n["e"] += 1
        liste.insert(i, {"e": e, "t": LEER, "o": {}}); j = i
    elif wo == "darunter":
        j = _ende(liste, i); liste.insert(j, {"e": e + 1, "t": LEER, "o": {}})
    elif wo == "assistent":                                                 # direkt unter der Form, vor ihren übrigen Kindern
        j = i + 1; liste.insert(j, {"e": e + 1, "t": LEER, "o": {}})
    else:
        j = _ende(liste, i); liste.insert(j, {"e": e, "t": LEER, "o": {}})
    return _aus(daten, liste), j


def kann_level(daten: dict, i: int | None, schritt: int) -> bool:
    """``schritt`` −1 = Level erhöhen (eine Ebene nach links), +1 = Level reduzieren (unter die vorige Form)."""
    liste = _knoten(daten)
    if i is None or not 0 <= i < len(liste):
        return False
    return liste[i]["e"] > 0 if schritt < 0 else i > 0 and liste[i - 1]["e"] >= liste[i]["e"]


def level(daten: dict, i: int, schritt: int) -> dict | None:
    if not kann_level(daten, i, schritt):
        return None
    liste = _knoten(daten)
    for n in liste[i:_ende(liste, i)]:
        n["e"] = max(0, n["e"] + (1 if schritt > 0 else -1))
    return _aus(daten, liste)


def _nachbar(liste: list[dict], i: int, schritt: int) -> int | None:
    """Die vorige (−1) oder nächste (+1) Form derselben Ebene unter demselben Elternteil."""
    e = liste[i]["e"]
    if schritt < 0:
        j = i - 1
        while j >= 0 and liste[j]["e"] > e:
            j -= 1
        return j if j >= 0 and liste[j]["e"] == e else None
    j = _ende(liste, i)
    return j if j < len(liste) and liste[j]["e"] == e else None


def kann_verschieben(daten: dict, i: int | None, schritt: int) -> bool:
    liste = _knoten(daten)
    return i is not None and 0 <= i < len(liste) and _nachbar(liste, i, schritt) is not None


def verschieben(daten: dict, i: int, schritt: int) -> tuple[dict, int] | None:
    """Vorwärts (−1) / Rückwärts (+1): die Form tauscht mit ihrer Nachbarin, samt allem darunter. → (Daten, neuer Index)."""
    liste = _knoten(daten)
    if not kann_verschieben(daten, i, schritt):
        return None
    j = _nachbar(liste, i, schritt)
    a, b = (j, i) if schritt < 0 else (i, j)
    erst, zweit = liste[a:_ende(liste, a)], liste[b:_ende(liste, b)]
    liste[a:a + len(erst) + len(zweit)] = zweit + erst
    return _aus(daten, liste), (a if schritt < 0 else a + len(zweit))


def entfernen(daten: dict, i: int) -> dict | None:
    """Die Form löschen; was unter ihr stand, rückt eine Ebene auf. Die letzte Form bleibt (sonst wäre das SmartArt leer)."""
    liste = _knoten(daten)
    if not 0 <= i < len(liste) or len(liste) <= 1:
        return None
    for n in liste[i + 1:_ende(liste, i)]:
        n["e"] = max(0, n["e"] - 1)
    liste.pop(i)
    return _aus(daten, liste)


def text_setzen(daten: dict, i: int, text: str) -> dict:
    liste = _knoten(daten)
    if 0 <= i < len(liste):
        liste[i]["t"] = " ".join(text.split()) or LEER
    return _aus(daten, liste)


def knoten_text(daten: dict, i: int) -> str:
    pts = punkte(daten.get("text", ""))
    return pts[i][1] if 0 <= i < len(pts) else ""


def knoten_setzen(daten: dict, i: int | None, **angaben) -> dict:
    """Eigene Angaben (``KNOTEN_SCHLUESSEL``) für die Form ``i`` — ohne ``i`` für alle Formen. ``None`` löscht eine Angabe."""
    liste = _knoten(daten)
    for j, n in enumerate(liste):
        if i is None or j == i:
            for k, v in angaben.items():
                if v is None:
                    n["o"].pop(k, None)
                else:
                    n["o"][k] = v
    return _aus(daten, liste)


# ---- Im Dokument --------------------------------------------------------------------------------------------------------------------------
def einfuegen(ed, daten: dict) -> None:
    """Als freies Objekt einfügen und auswählen (Rahmen, acht Griffe, Schnellleiste; Reiter WPSArt-Design/-Format)."""
    from lunivo_writer.editor import frei_objekt as FO
    ed._sa_knoten = None
    FO.einfuegen(ed, "smartart", dict(daten))


def _frei(ed):
    from lunivo_writer.editor import frei_objekt as FO
    z = FO.ziel(ed) if ed is not None else None
    return z if z is not None and z[0] == "smartart" else None


def gewaehlt(ed) -> bool:
    return _frei(ed) is not None


def knoten(ed) -> int | None:
    """Die im gewählten SmartArt angeklickte Form (Index) oder None."""
    z = _frei(ed)
    i = getattr(ed, "_sa_knoten", None)
    return i if z is not None and i is not None and 0 <= i < len(punkte(z[1].get("text", "")) or [0]) else None


def daten_der_auswahl(ed) -> dict | None:
    z = _frei(ed)
    if z is not None:
        return z[1]
    f = ed.bild_format()
    if f is None or not f.hasProperty(P_OBJEKT):
        return None
    try:
        o = json.loads(f.property(P_OBJEKT))
    except (ValueError, TypeError):
        return None
    return dict(o.get("daten", {})) if o.get("art") == "smartart" else None


def aendern(ed, **felder) -> bool:
    """Daten des gewählten SmartArt ändern und neu zeichnen. Freies Objekt: über ``frei_objekt.aendern`` (Maßstab bleibt). Ältere Dokumente mit
    SmartArt als Bild im Text: Breite im Text bleibt, Seitenverhältnis folgt."""
    if _frei(ed) is not None:
        from lunivo_writer.editor import frei_objekt as FO
        return FO.aendern(ed, "smartart", **felder)
    c = ed._bild_cursor()
    d = daten_der_auswahl(ed)
    if c is None or d is None:
        return False
    d.update({k: v for k, v in felder.items() if v is not None})
    img = zeichnen(d)
    f = c.charFormat().toImageFormat()
    name = f"obj-{id(img)}-{ed.document().revision()}"
    ed.document().addResource(QTextDocument.ImageResource, QUrl(name), img)
    breite = f.width() or img.width()
    f2 = QTextImageFormat(f)
    f2.setName(name); f2.setWidth(breite); f2.setHeight(breite * img.height() / img.width())
    f2.setProperty(P_OBJEKT, json.dumps({"art": "smartart", "daten": d}, ensure_ascii=False, separators=(",", ":")))
    f2.setProperty(0x100000 + 0x101 + 1, "SmartArt: " + d.get("layout", "Liste") + " mit " + str(len(punkte(d.get("text", "")))) + " Punkten")
    c.setCharFormat(f2)
    ed.document().setModified(True)
    return True


def _alles(ed, neu: dict, knoten_neu: int | None = None) -> bool:
    """Die ganzen Daten ersetzen (Text, eigene Angaben der Formen) und die gewählte Form neu setzen."""
    z = _frei(ed)
    if z is None or neu is None:
        return False
    kw = {k: neu.get(k) for k in set(z[1]) | set(neu)}
    ok = aendern(ed, **kw)
    if ok:
        ed._sa_knoten = knoten_neu
        ed.viewport().update()
    return ok


def form_hinzufuegen(ed, wo: str = "danach") -> bool:
    z = _frei(ed)
    if z is None:
        return False
    neu, j = form_einfuegen(z[1], knoten(ed), wo)
    return _alles(ed, neu, j)


def level_aendern(ed, schritt: int) -> bool:
    z, i = _frei(ed), knoten(ed)
    return z is not None and i is not None and _alles(ed, level(z[1], i, schritt), i)


def form_verschieben(ed, schritt: int) -> bool:
    z, i = _frei(ed), knoten(ed)
    r = verschieben(z[1], i, schritt) if z is not None and i is not None else None
    return r is not None and _alles(ed, r[0], r[1])


def form_loeschen(ed) -> bool:
    z, i = _frei(ed), knoten(ed)
    return z is not None and i is not None and _alles(ed, entfernen(z[1], i), None)


def form_formatieren(ed, **angaben) -> bool:
    """Eigene Angaben für die gewählte Form, ohne gewählte Form für alle Formen (Reiter WPSArt-Format, Leiste neben der Form)."""
    z = _frei(ed)
    return z is not None and _alles(ed, knoten_setzen(z[1], knoten(ed), **angaben), knoten(ed))


def form_text(ed, i: int, text: str) -> bool:
    z = _frei(ed)
    return z is not None and _alles(ed, text_setzen(z[1], i, text), i)


def knoten_auf_bildschirm(ed) -> dict:
    """{Index: Rechteck im Editor} der Formen des gewählten SmartArt (folgt Zoom und Größe des Rahmens)."""
    sel = getattr(ed, "_frei_sel", None)
    if sel is None:
        return {}
    for key, a, _bild, r, _h, _n in ed._frei_liste():
        if key == sel and a.get("art") == "smartart":
            groesse, rects = knoten_rechtecke(a.get("daten", {}))
            fx, fy = r.width() / max(1.0, groesse.width()), r.height() / max(1.0, groesse.height())
            return {i: QRectF(r.x() + q.x() * fx, r.y() + q.y() * fy, q.width() * fx, q.height() * fy) for i, q in rects.items()}
    return {}


def knoten_bei(ed, pos: QPointF) -> int | None:
    for i, q in sorted(knoten_auf_bildschirm(ed).items(), key=lambda t: t[1].width() * t[1].height()):     # die kleinste zuerst (Zielscheibe)
        if q.contains(pos):
            return i
    return None


# ---- Direkt in einer Form schreiben (Doppelklick, F2, Enter oder einfach lostippen) ----------------------------------------------------------
def schreiben_starten(ed, erstes: str = "") -> bool:
    """Ein Eingabefeld über der gewählten Form; Enter oder ein Klick daneben übernimmt, Esc verwirft. ``erstes``: das schon getippte Zeichen."""
    from PySide6.QtWidgets import QLineEdit
    i = knoten(ed)
    z = _frei(ed)
    if i is None or z is None:
        return False
    schreiben_beenden(ed, True)

    class Feld(QLineEdit):
        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                schreiben_beenden(ed, False); return
            if e.key() in (Qt.Key_Return, Qt.Key_Enter):
                schreiben_beenden(ed, True); return
            super().keyPressEvent(e)

        def focusOutEvent(self, e):
            super().focusOutEvent(e)
            if getattr(ed, "_sa_edit", None) is self and e.reason() not in (Qt.PopupFocusReason, Qt.ActiveWindowFocusReason):
                schreiben_beenden(ed, True)

    w = Feld(ed.viewport())
    alt = knoten_text(z[1], i)
    w.setText(erstes if erstes else ("" if alt == LEER else alt))
    w.setAlignment(Qt.AlignCenter)
    o = (z[1].get("knoten") or {}).get(str(i)) or {}
    w.setStyleSheet("QLineEdit { background: #ffffff; color: %s; border: 1px dashed #1c7ed6; }" % (o.get("textfarbe") or Farbe.TINTE_DUNKEL))
    ed._sa_edit, ed._sa_edit_knoten = w, i
    schreiben_platzieren(ed)
    w.show(); w.setFocus()
    if not erstes:
        w.selectAll()
    return True


def schreiben_platzieren(ed) -> None:
    w = getattr(ed, "_sa_edit", None)
    if w is None:
        return
    q = knoten_auf_bildschirm(ed).get(ed._sa_edit_knoten)
    if q is None:
        return
    f = QFont(w.font()); f.setPixelSize(max(9, int(min(q.height() * 0.42, 15 * ed.zoom)))); w.setFont(f)
    hoehe = max(int(q.height() * 0.6), w.fontMetrics().height() + 6)
    w.setGeometry(int(q.x() + 2), int(q.center().y() - hoehe / 2), max(36, int(q.width() - 4)), hoehe)


def schreiben_beenden(ed, uebernehmen: bool = True) -> None:
    w = getattr(ed, "_sa_edit", None)
    if w is None:
        return
    ed._sa_edit = None
    if uebernehmen and _frei(ed) is not None:
        z = _frei(ed)
        if " ".join(w.text().split()) != knoten_text(z[1], ed._sa_edit_knoten):
            form_text(ed, ed._sa_edit_knoten, w.text())
    w.hide(); w.deleteLater()
    ed.viewport().update(); ed.setFocus()
