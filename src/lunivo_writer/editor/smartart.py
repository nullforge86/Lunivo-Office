"""SmartArt: Listen, Prozesse, Hierarchien, Zyklen und Pyramiden aus einem eingerückten Text.

Das Objekt ist ein Bild mit gespeicherten Daten (P_OBJEKT, art „smartart“): Layout, Text und Farbschema. Es lässt sich jederzeit
umstellen und neu schreiben, auch nach dem Speichern als DOCX und erneutem Öffnen in Lunivo Writer.
Grenze: In DOCX steht es als Bild (Titel „lunivo:…“); Word und LibreOffice zeigen das Bild, bearbeiten es aber nicht als SmartArt."""
from __future__ import annotations

import json
import math

from PySide6.QtCore import QPointF, QRectF, Qt, QUrl
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPainterPath, QPen, QPolygonF, QTextCursor, QTextDocument, QTextImageFormat

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


def punkte(text: str) -> list[tuple[int, str]]:
    """[(Ebene, Text)] — die Ebene ergibt sich aus der Einrückung (je zwei Leerzeichen oder ein Tabulator)."""
    out = []
    for zeile in text.splitlines():
        if not zeile.strip():
            continue
        roh = zeile.replace("\t", "  ")
        out.append(((len(roh) - len(roh.lstrip(" "))) // 2, zeile.strip()))
    return out


def _farbe(daten: dict, ebene: int) -> QColor:
    f = FARBEN.get(daten.get("farben", "Blau"), FARBEN["Blau"])
    return QColor(f[min(ebene, 2)] if daten.get("farben") != "Bunt" else f[ebene % 3])


def _text_farbe(c: QColor) -> QColor:
    return QColor(Farbe.WEISS) if c.lightness() < 150 else QColor(Farbe.TINTE_DUNKEL)


def _kasten(p: QPainter, r: QRectF, text: str, c: QColor, rund: float = 8) -> None:
    p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c))
    p.drawRoundedRect(r, rund, rund)
    p.setPen(_text_farbe(c))
    f = QFont(p.font()); f.setPointSizeF(11); p.setFont(f)
    p.drawText(r.adjusted(6, 3, -6, -3), Qt.AlignCenter | Qt.TextWordWrap, text)


def _pfeil(p: QPainter, a: QPointF, b: QPointF, c: QColor) -> None:
    p.setPen(QPen(c, 2)); p.drawLine(a, b)
    w = math.atan2(b.y() - a.y(), b.x() - a.x())
    for d in (0.45, -0.45):
        p.drawLine(b, QPointF(b.x() - 9 * math.cos(w - d), b.y() - 9 * math.sin(w - d)))


def _bild(b: float, h: float) -> tuple[QImage, QPainter]:
    img = QImage(int(b), int(h), QImage.Format_ARGB32); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    return img, p


def _text(p: QPainter, r: QRectF, t: str, c: QColor, groesse: float = 11) -> None:
    p.setPen(_text_farbe(c)); f = QFont(p.font()); f.setPointSizeF(groesse); p.setFont(f)
    p.drawText(r, Qt.AlignCenter | Qt.TextWordWrap, t)


def _gruppen(pts: list[tuple[int, str]]) -> list[tuple[str, list[str]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte."""
    out: list[tuple[str, list[str]]] = []
    for e, t in pts:
        if e == 0 or not out:
            out.append((t, []))
        else:
            out[-1][1].append(t)
    return out


def _bunt(daten: dict, i: int) -> QColor:
    return _farbe(daten, i if daten.get("farben") == "Bunt" else 0)


def _spalten(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    n = len(g)
    bw = (b - 16 - (n - 1) * 10) / n
    zeilen = max(len(k) for _t, k in g)
    img, p = _bild(b, 16 + 50 + max(1, zeilen) * 34 + 14)
    for i, (t, kinder) in enumerate(g):
        x = 8 + i * (bw + 10)
        c = _bunt(daten, i)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c.lighter(185)))
        p.drawRoundedRect(QRectF(x, 36, bw, img.height() - 44), 6, 6)
        _kasten(p, QRectF(x, 8, bw, 44), t, c)
        for j, k in enumerate(kinder):
            _text(p, QRectF(x + 4, 60 + j * 34, bw - 8, 30), k, c.lighter(185))
    p.end()
    return img


def _gruppenliste(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    img, p = _bild(b, 16 + len(g) * 62)
    for i, (t, kinder) in enumerate(g):
        y = 8 + i * 62
        c = _bunt(daten, i)
        _kasten(p, QRectF(8, y, 130, 54), t, c)
        n = max(1, len(kinder))
        kw = (b - 16 - 146 - (n - 1) * 8) / n
        for j, k in enumerate(kinder):
            _kasten(p, QRectF(146 + j * (kw + 8), y + 6, kw, 42), k, _farbe(daten, 1 if daten.get("farben") != "Bunt" else i), 6)
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
        _kasten(p, QRectF(8 + s * (kw + 10), 8 + z * (kh + 10), kw, kh), t, _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 0 if (z + s) % 2 == 0 else 1), 10)
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
        c = _bunt(daten, i)
        poly = QPolygonF([QPointF(x, y), QPointF(x + w - sp, y), QPointF(x + w, y + h / 2), QPointF(x + w - sp, y + h), QPointF(x, y + h),
                          QPointF(x + sp, y + h / 2)])
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c)); p.drawPolygon(poly)
        _text(p, QRectF(x + sp + 4, y + 4, w - 2 * sp - 8, h - 8), t, c, 10.5)
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
        _kasten(p, QRectF(q.x() - 56, q.y() - 24, 112, 48), rest[i][1], _farbe(daten, 1 if daten.get("farben") != "Bunt" else i + 1), 24)
    _kasten(p, QRectF(mx - 62, my - 40, 124, 80), pts[0][1], _farbe(daten, 0), 40)
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
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c)); p.drawEllipse(QPointF(mx, my), r, r)
        _text(p, QRectF(mx - r * 0.7, my - r + 4, r * 1.4, (rad - 20) / n - 6 if n > 1 else 40), t, c)
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
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c))
        p.drawPolygon(QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)]))
        _text(p, QRectF(mitte - bu * 0.85, oben, bu * 1.7, unten - oben), t, c)
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
        _kasten(p, QRectF(x - min(raster - 6, 120) / 2, y - 80 if oben else y + 26, min(raster - 6, 120), 54), t, c)
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
        r = QRectF(8 + i * sw, h - 8 - (i + 1) * sh - 0, sw - 4, (i + 1) * sh)
        _kasten(p, r, "", _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, min(i, 2)), 4)
        _text(p, QRectF(r.left() + 2, r.top() + 2, r.width() - 4, 38), t, _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2)), 10.5)
    p.end()
    return img


_ZEICHNER = {"Spalten": _spalten, "Gruppen": _gruppenliste, "Matrix": _matrix, "Chevron": _chevron, "Radial": _radial, "Zielscheibe": _zielscheibe,
             "Trichter": _trichter, "Zeitachse": _zeitachse, "Stufen": _stufen}


def zeichnen(daten: dict) -> QImage:
    pts = punkte(daten.get("text", "")) or [(0, "…")]
    layout = daten.get("layout", "Liste")
    breite = 520
    if layout in _ZEICHNER:
        return _ZEICHNER[layout](daten, pts, breite)
    if layout == "Liste":
        h = 16 + len(pts) * 46
        img = QImage(breite, h, QImage.Format_ARGB32); img.fill(Qt.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
        for i, (e, t) in enumerate(pts):
            _kasten(p, QRectF(8 + e * 36, 8 + i * 46, breite - 16 - e * 36, 38), t, _farbe(daten, e))
    elif layout == "Prozess":
        je_zeile = 4
        zeilen = -(-len(pts) // je_zeile)
        bw = (breite - 16 - (min(len(pts), je_zeile) - 1) * 34) / min(len(pts), je_zeile)
        h = 16 + zeilen * 96
        img = QImage(breite, h, QImage.Format_ARGB32); img.fill(Qt.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
        for i, (e, t) in enumerate(pts):
            z, s = divmod(i, je_zeile)
            r = QRectF(8 + s * (bw + 34), 8 + z * 96, bw, 80)
            _kasten(p, r, t, _farbe(daten, 0 if daten.get("farben") != "Bunt" else i))
            if i < len(pts) - 1 and s < je_zeile - 1:
                _pfeil(p, QPointF(r.right() + 4, r.center().y()), QPointF(r.right() + 30, r.center().y()), QColor(Farbe.GRAU))
    elif layout == "Hierarchie":
        # Blätter nebeneinander, Eltern mittig über ihren Kindern
        baum: list[dict] = []
        stack: list[dict] = []
        for e, t in pts:
            n = {"t": t, "e": e, "k": []}
            while stack and stack[-1]["e"] >= e:
                stack.pop()
            (stack[-1]["k"] if stack else baum).append(n)
            stack.append(n)
        tiefe = max(e for e, _t in pts) + 1
        blaetter = [0]

        def setze(n):
            if not n["k"]:
                n["x"] = blaetter[0]; blaetter[0] += 1
            else:
                for k in n["k"]:
                    setze(k)
                n["x"] = (n["k"][0]["x"] + n["k"][-1]["x"]) / 2
        for w in baum:
            setze(w)
        spalten = max(1, blaetter[0])
        bw = min(130.0, (breite - 16) / spalten - 8)
        h = 16 + tiefe * 78
        img = QImage(breite, h, QImage.Format_ARGB32); img.fill(Qt.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
        raster = (breite - 16) / spalten

        def mal(n):
            r = QRectF(8 + n["x"] * raster + (raster - bw) / 2, 8 + n["e"] * 78, bw, 50)
            for k in n["k"]:
                kr = QRectF(8 + k["x"] * raster + (raster - bw) / 2, 8 + k["e"] * 78, bw, 50)
                p.setPen(QPen(QColor(Farbe.GRAU), 1.5))
                p.drawLine(QPointF(r.center().x(), r.bottom()), QPointF(kr.center().x(), kr.top()))
            _kasten(p, r, n["t"], _farbe(daten, n["e"]))
            for k in n["k"]:
                mal(k)
        for w in baum:
            mal(w)
    elif layout == "Zyklus":
        n = len(pts)
        durchm = 380
        img = QImage(breite, durchm + 16, QImage.Format_ARGB32); img.fill(Qt.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
        mx, my, rad = breite / 2, (durchm + 16) / 2, (durchm - 90) / 2
        pos = [QPointF(mx + rad * 1.35 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), my + rad * math.sin(-math.pi / 2 + 2 * math.pi * i / n))
               for i in range(n)]
        for i in range(n):
            a, b = pos[i], pos[(i + 1) % n]
            if n > 1:
                w = math.atan2(b.y() - a.y(), b.x() - a.x())
                _pfeil(p, QPointF(a.x() + 62 * math.cos(w), a.y() + 30 * math.sin(w)), QPointF(b.x() - 66 * math.cos(w), b.y() - 33 * math.sin(w)),
                       QColor(Farbe.GRAU))
        for i, (e, t) in enumerate(pts):
            _kasten(p, QRectF(pos[i].x() - 56, pos[i].y() - 26, 112, 52), t, _farbe(daten, i if daten.get("farben") == "Bunt" else 0), 26)
    else:                                                                   # Pyramide
        n = len(pts)
        zh = 54
        h = 16 + n * zh
        img = QImage(breite, h, QImage.Format_ARGB32); img.fill(Qt.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
        mitte = breite / 2
        for i, (e, t) in enumerate(pts):
            oben, unten = 8 + i * zh, 8 + (i + 1) * zh - 4
            bo, bu = (i / n) * (breite - 16) / 2 + 0.0, ((i + 1) / n) * (breite - 16) / 2
            poly = QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)])
            c = _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2))
            p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c)); p.drawPolygon(poly)
            p.setPen(_text_farbe(c)); f = QFont(p.font()); f.setPointSizeF(11); p.setFont(f)
            p.drawText(QRectF(mitte - bu * 0.8, oben, bu * 1.6, unten - oben), Qt.AlignCenter | Qt.TextWordWrap, t)
    p.end()
    return img


def einfuegen(ed, daten: dict) -> None:
    from lunivo_writer.editor import einfuegen as E
    E.qimage_einfuegen(ed, zeichnen(daten), "SmartArt: " + daten.get("layout", "Liste") + " mit " + str(len(punkte(daten.get("text", "")))) + " Punkten",
                       "smartart", daten)


def daten_der_auswahl(ed) -> dict | None:
    f = ed.bild_format()
    if f is None or not f.hasProperty(P_OBJEKT):
        return None
    try:
        o = json.loads(f.property(P_OBJEKT))
    except (ValueError, TypeError):
        return None
    return dict(o.get("daten", {})) if o.get("art") == "smartart" else None


def aendern(ed, **felder) -> bool:
    """Daten des markierten SmartArt-Bildes ändern und neu zeichnen (Breite im Text bleibt, Seitenverhältnis folgt)."""
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
