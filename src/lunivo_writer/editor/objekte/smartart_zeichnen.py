"""Zeichenfunktionen und Layouts für SmartArt."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPen, QPolygonF

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.diagramme import diagramm_format as F
from lunivo_writer.editor.objekte.smartart import BULLET, FARBEN


_ZU: dict = {"stil": 1, "rtl": False, "b": 520, "reg": {}, "ids": [], "knoten": [], "hier": "standard", "fmt": [], "fmt_alle": {}}


def _format_von(nr) -> dict | None:
    """Das Format des Knotens Nummer ``nr`` (Format wie ``teil_format`` des Diagramms): das des Knotens über dem von allen Knoten (``daten["format"]``)."""
    alle = _ZU.get("fmt_alle") or {}
    eigen = _ZU["fmt"][nr] if nr is not None and 0 <= nr < len(_ZU["fmt"]) else None
    if not alle and not eigen:
        return None
    f = {**alle, **(eigen or {})}
    for k in ("linie", "text"):
        if alle.get(k) and (eigen or {}).get(k):
            f[k] = {**alle[k], **eigen[k]}
    return f


def _spiegel(r: QRectF) -> QRectF:
    return QRectF(_ZU["b"] - r.right(), r.top(), r.width(), r.height()) if _ZU["rtl"] else QRectF(r)


def _merke(i, r: QRectF) -> None:
    """Rechteck des Knotens Nummer ``i`` (Stelle in der Knotenliste) für ``knoten_rechtecke`` merken."""
    if i is not None and 0 <= i < len(_ZU["ids"]):
        _ZU["reg"][_ZU["ids"][i]] = _spiegel(r)


def _farbe(daten: dict, ebene: int) -> QColor:
    f = FARBEN.get(daten.get("farben", "Blau"), FARBEN["Blau"])
    return QColor(f[min(ebene, 2)] if daten.get("farben") != "Bunt" else f[ebene % 3])


def _stilfarbe(c: QColor) -> QColor:
    """Die Füllfarbe, die der Formenstil aus der Farbe macht (für den Textkontrast)."""
    s = _ZU["stil"]
    return c.lighter(185) if s == 2 else c.darker(112) if s == 3 else QColor(c)


def _text_farbe(c: QColor) -> QColor:
    return QColor(Farbe.WEISS) if c.lightness() < 150 else QColor(Farbe.TINTE_DUNKEL)


def _fuellen(p: QPainter, c: QColor, r: QRectF) -> None:
    """Stift und Pinsel nach dem Formenstil: 0 flach (ohne Rand), 1 einfach, 2 hell (Farbrand), 3 kräftig (dicker dunkler Rand), 4 3D (Verlauf)."""
    s, f = _ZU["stil"], _stilfarbe(c)
    if s == 0:
        p.setPen(Qt.NoPen); p.setBrush(QBrush(f))
    elif s == 2:
        p.setPen(QPen(c, 2)); p.setBrush(QBrush(f))
    elif s == 3:
        p.setPen(QPen(c.darker(170), 3)); p.setBrush(QBrush(f))
    elif s == 4:
        g = QLinearGradient(r.topLeft(), r.bottomLeft()); g.setColorAt(0, c.lighter(150)); g.setColorAt(1, c.darker(120))
        p.setPen(QPen(c.darker(150), 1.5)); p.setBrush(QBrush(g))
    else:
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(f))


def _text_zeichnen(p: QPainter, r: QRectF, flags, t: str) -> None:
    """Text immer ungespiegelt (auch bei „von rechts nach links“, wo die Formen gespiegelt werden)."""
    if _ZU["rtl"]:
        p.save(); p.resetTransform(); p.drawText(_spiegel(r), flags, t); p.restore()
    else:
        p.drawText(r, flags, t)


def _schrift(p: QPainter, text: str, groesse: float) -> None:
    f = QFont(p.font()); f.setPointSizeF(groesse if "\n" not in text else min(groesse, 9.0)); p.setFont(f)


def _kasten(p: QPainter, r: QRectF, text: str, c: QColor, rund: float = 8, nr=None) -> None:
    fm = _format_von(nr)
    _fuellen(p, c, r)
    if fm:                                                                   # eigenes Format (Füllung, Linie, Effekte, Text) über dem Formenstil
        _kasten_format(p, r, c, fm)
    p.drawRoundedRect(r, rund, rund)
    if _ZU["stil"] == 4:                                                    # Glanz: die obere Hälfte heller
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 55))
        p.drawRoundedRect(QRectF(r.left() + 2, r.top() + 2, r.width() - 4, r.height() / 2 - 2), rund, rund)
    p.setPen(_text_farbe(_stilfarbe(c)))
    _schrift(p, text, 11)
    t = (fm or {}).get("text")
    if t:
        p.setFont(F.schrift_aus(p.font(), t))
        if t.get("farbe") or t.get("effekt"):
            p.setPen(F.textfarbe(t, p.pen().color().name()))
    _text_zeichnen(p, r.adjusted(6, 3, -6, -3), Qt.AlignCenter | Qt.TextWordWrap, text)
    _merke(nr, r)


def _kasten_format(p: QPainter, r: QRectF, c: QColor, fm: dict) -> None:
    """Füllung, Effekte und Linie des eigenen Formats auf Pinsel und Stift setzen."""
    fu, li, fx = fm.get("fuell"), fm.get("linie"), F.fx_normal(fm)
    if fx:
        F.teil_zeichnen(p, r, {"fuell": fu if fu is not None else c.name(), **fx}, c); p.setBrush(Qt.NoBrush)
    elif fu is not None:
        _pinsel_setzen(p, r, fu)
    if li:
        p.setPen(Qt.NoPen if F.linie_keine(li) else F.stift(li, c.darker(125).name(), r))


def _pinsel_setzen(p: QPainter, r: QRectF, fu) -> None:
    br, opaz = F.pinsel(fu, r)
    if br is None:
        p.setBrush(Qt.NoBrush)
        return
    if opaz < 1 and br.style() == Qt.SolidPattern:
        col = QColor(br.color()); col.setAlphaF(opaz); br = QBrush(col)
    p.setBrush(br)


def _pfeil(p: QPainter, a: QPointF, b: QPointF, c: QColor) -> None:
    p.setPen(QPen(c, 2)); p.drawLine(a, b)
    w = math.atan2(b.y() - a.y(), b.x() - a.x())
    for d in (0.45, -0.45):
        p.drawLine(b, QPointF(b.x() - 9 * math.cos(w - d), b.y() - 9 * math.sin(w - d)))


def _bild(b: float, h: float) -> tuple[QImage, QPainter]:
    img = QImage(int(b), int(h), QImage.Format_ARGB32); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    if _ZU["rtl"]:
        p.translate(int(b), 0); p.scale(-1, 1)
    return img, p


def _text(p: QPainter, r: QRectF, t: str, c: QColor, groesse: float = 11) -> None:
    p.setPen(_text_farbe(_stilfarbe(c))); _schrift(p, t, groesse)
    _text_zeichnen(p, r, Qt.AlignCenter | Qt.TextWordWrap, t)


def _gruppen(pts: list[tuple[int, str]]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])]."""
    out: list[tuple[int, str, list[tuple[int, str]]]] = []
    for i, (e, t) in enumerate(pts):
        if e == 0 or not out:
            out.append((i, t, []))
        else:
            out[-1][2].append((i, t))
    return out


def _bunt(daten: dict, i: int) -> QColor:
    return _farbe(daten, i if daten.get("farben") == "Bunt" else 0)


def _spalten(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    n = len(g)
    bw = (b - 16 - (n - 1) * 10) / n
    zeilen = max(len(k) for _i, _t, k in g)
    img, p = _bild(b, 16 + 50 + max(1, zeilen) * 34 + 14)
    for i, (ni, t, kinder) in enumerate(g):
        x = 8 + i * (bw + 10)
        c = _bunt(daten, i)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c.lighter(185)))
        p.drawRoundedRect(QRectF(x, 36, bw, img.height() - 44), 6, 6)
        _kasten(p, QRectF(x, 8, bw, 44), t, c, nr=ni)
        for j, (nj, k) in enumerate(kinder):
            r = QRectF(x + 4, 60 + j * 34, bw - 8, 30)
            _text(p, r, k, c.lighter(185)); _merke(nj, r)
    p.end()
    return img


def _gruppenliste(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    img, p = _bild(b, 16 + len(g) * 62)
    for i, (ni, t, kinder) in enumerate(g):
        y = 8 + i * 62
        c = _bunt(daten, i)
        _kasten(p, QRectF(8, y, 130, 54), t, c, nr=ni)
        n = max(1, len(kinder))
        kw = (b - 16 - 146 - (n - 1) * 8) / n
        for j, (nj, k) in enumerate(kinder):
            _kasten(p, QRectF(146 + j * (kw + 8), y + 6, kw, 42), k, _farbe(daten, 1 if daten.get("farben") != "Bunt" else i), 6, nr=nj)
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
        _kasten(p, QRectF(8 + s * (kw + 10), 8 + z * (kh + 10), kw, kh), t,
                _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 0 if (z + s) % 2 == 0 else 1), 10, nr=i)
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
        _fuellen(p, c, QRectF(x, y, w, h)); p.drawPolygon(poly)
        _text(p, QRectF(x + sp + 4, y + 4, w - 2 * sp - 8, h - 8), t, c, 10.5)
        _merke(i, QRectF(x, y, w, h))
    p.end()
    return img


def _radial(daten: dict, pts, b: int) -> QImage:
    h = 380
    img, p = _bild(b, h)
    mx, my = b / 2, h / 2
    rest = pts[1:]
    n = max(1, len(rest))
    pos = [QPointF(mx + 190 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), my + 135 * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(len(rest))]
    for q in pos:                                                    # Pfeile vom Kern zu den Kästen, jeweils am Rand der Kästen
        dx, dy = q.x() - mx, q.y() - my
        def rand(hb, hh):
            return min(hb / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
        t0, t1 = rand(62 + 4, 40 + 4), 1 - rand(56 + 4, 24 + 4)
        if t1 > t0:
            _pfeil(p, QPointF(mx + dx * t0, my + dy * t0), QPointF(mx + dx * t1, my + dy * t1), QColor(Farbe.GRAU))
    for i, q in enumerate(pos):
        _kasten(p, QRectF(q.x() - 56, q.y() - 24, 112, 48), rest[i][1], _farbe(daten, 1 if daten.get("farben") != "Bunt" else i + 1), 24, nr=i + 1)
    _kasten(p, QRectF(mx - 62, my - 40, 124, 80), pts[0][1], _farbe(daten, 0), 40, nr=0)
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
        _fuellen(p, c, QRectF(mx - r, my - r, 2 * r, 2 * r)); p.drawEllipse(QPointF(mx, my), r, r)
        feld = QRectF(mx - r * 0.7, my - r + 4, r * 1.4, (rad - 20) / n - 6 if n > 1 else 40)
        _text(p, feld, t, c); _merke(i, feld)
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
        _fuellen(p, c, QRectF(mitte - bo, oben, 2 * bo, unten - oben))
        p.drawPolygon(QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)]))
        _text(p, QRectF(mitte - bu * 0.85, oben, bu * 1.7, unten - oben), t, c)
        _merke(i, QRectF(mitte - bo, oben, 2 * bo, unten - oben))
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
        _kasten(p, QRectF(x - min(raster - 6, 120) / 2, y - 80 if oben else y + 26, min(raster - 6, 120), 54), t, c, nr=i)
        _fuellen(p, c, QRectF(x - 8, y - 8, 16, 16)); p.drawEllipse(QPointF(x, y), 8, 8)
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
        _kasten(p, r, "", _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, min(i, 2)), 4, nr=i)
        _text(p, QRectF(r.left() + 2, r.top() + 2, r.width() - 4, 38), t, _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2)), 10.5)
    p.end()
    return img


# ---- Organigramm / Hierarchie ---------------------------------------------------------------------------------------------------------
def _baum(pts) -> list[dict]:
    """Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}."""
    kn = _ZU["knoten"]
    wurzeln: list[dict] = []
    stapel: list[dict] = []
    for i, (e, t) in enumerate(pts):
        n = {"i": i, "t": t, "e": e, "k": [], "a": bool(kn[i].get("assistent")) if i < len(kn) else False}
        while stapel and stapel[-1]["e"] >= e:
            stapel.pop()
        (stapel[-1]["k"] if stapel else wurzeln).append(n)
        stapel.append(n)
    return wurzeln


def _alle(n: dict):
    yield n
    for k in n["k"]:
        yield from _alle(k)


def _standard_baum(daten: dict, wurzeln, b: int) -> QImage:
    """Blätter nebeneinander, Eltern mittig über ihren Kindern; Assistenten stehen eine Zeile unter dem Eltern, die übrigen Kinder darunter."""
    blaetter = [0]
    maxz = [0]

    def zeilen(n, z):
        n["z"] = z; maxz[0] = max(maxz[0], z)
        ass = [c for c in n["k"] if c["a"]]
        for c in ass:
            zeilen(c, z + 1)
        for c in (c for c in n["k"] if not c["a"]):
            zeilen(c, z + 1 + (1 if ass else 0))

    def setze(n):
        if not n["k"]:
            n["x"] = blaetter[0]; blaetter[0] += 1
        else:
            kinder = [c for c in n["k"] if c["a"]] + [c for c in n["k"] if not c["a"]]
            for k in kinder:
                setze(k)
            n["x"] = (kinder[0]["x"] + kinder[-1]["x"]) / 2
    for w in wurzeln:
        zeilen(w, 0); setze(w)
    spalten = max(1, blaetter[0])
    bw = min(130.0, (b - 16) / spalten - 8)
    img, p = _bild(b, 16 + (maxz[0] + 1) * 78)
    raster = (b - 16) / spalten

    def box(n):
        return QRectF(8 + n["x"] * raster + (raster - bw) / 2, 8 + n["z"] * 78, bw, 50)

    def mal(n):
        r = box(n)
        for k in n["k"]:
            kr = box(k)
            mitte = (r.bottom() + kr.top()) / 2
            p.setPen(QPen(QColor(Farbe.GRAU), 1.5))
            p.drawLine(QPointF(r.center().x(), r.bottom()), QPointF(r.center().x(), mitte))
            p.drawLine(QPointF(r.center().x(), mitte), QPointF(kr.center().x(), mitte))
            p.drawLine(QPointF(kr.center().x(), mitte), QPointF(kr.center().x(), kr.top()))
        _kasten(p, r, n["t"], _farbe(daten, n["e"]), nr=n["i"])
        for k in n["k"]:
            mal(k)
    for w in wurzeln:
        mal(w)
    p.end()
    return img


def _haengend_baum(daten: dict, wurzeln, b: int, variante: str) -> QImage:
    """Hängende Layouts: die Kinder stehen untereinander neben einer senkrechten Linie unter dem Eltern (links, rechts oder abwechselnd beidseits)."""
    tiefe = max((n["e"] for w in wurzeln for n in _alle(w)), default=0)
    versatz = 26.0
    bw = max(70.0, min(150.0, b - 16 - (tiefe + 1) * versatz * (2 if variante == "beide" else 1)))
    zh = 46.0

    def platz(n, x, z, seite):
        """Knoten bei Spalte x (linke Kante) und Zeile z; → nächste freie Zeile. ``seite``: rechts | links | beide."""
        n["x"], n["z"], n["seite"] = x, z, seite
        if not n["k"]:
            return z + 1
        if seite == "beide":
            zz = {"rechts": z + 1, "links": z + 1}
            for j, c in enumerate(n["k"]):
                s = "rechts" if j % 2 == 0 else "links"
                cx = x + bw / 2 + 10 if s == "rechts" else x + bw / 2 - 10 - bw
                zz[s] = platz(c, cx, zz[s], s)
            return max(zz.values())
        zn = z + 1
        for c in n["k"]:
            zn = platz(c, x + versatz if seite == "rechts" else x - versatz, zn, seite)
        return zn
    zeile = 0
    for w in wurzeln:
        zeile = platz(w, 0.0, zeile, "beide" if variante == "beide" else variante.replace("haengend_", ""))
    alle = [n for w in wurzeln for n in _alle(w)]
    links = min(n["x"] for n in alle)
    breite = max(n["x"] for n in alle) + bw - links
    ox = 8 - links + max(0.0, (b - 16 - breite) / 2)
    img, p = _bild(b, 16 + zeile * zh + 4)

    def box(n):
        return QRectF(n["x"] + ox, 8 + n["z"] * zh, bw, zh - 8)

    def mal(n):
        r = box(n)
        if n["k"]:
            tx = r.center().x() if n["seite"] == "beide" else r.left() + versatz / 2 if n["seite"] == "rechts" else r.right() - versatz / 2
            p.setPen(QPen(QColor(Farbe.GRAU), 1.5))
            p.drawLine(QPointF(tx, r.bottom()), QPointF(tx, max(box(c).center().y() for c in n["k"])))
            for c in n["k"]:
                kr = box(c)
                p.drawLine(QPointF(tx, kr.center().y()), QPointF(kr.left() if kr.center().x() > tx else kr.right(), kr.center().y()))
        _kasten(p, r, n["t"], _farbe(daten, n["e"]), 6, nr=n["i"])
        for c in n["k"]:
            mal(c)
    for w in wurzeln:
        mal(w)
    p.end()
    return img


def _organigramm(daten: dict, pts, b: int) -> QImage:
    wurzeln = _baum(pts)
    v = _ZU["hier"]
    return _haengend_baum(daten, wurzeln, b, v) if v in ("beide", "haengend_links", "haengend_rechts") else _standard_baum(daten, wurzeln, b)


def _liste(daten: dict, pts, b: int) -> QImage:
    img, p = _bild(b, 16 + len(pts) * 46)
    for i, (e, t) in enumerate(pts):
        _kasten(p, QRectF(8 + e * 36, 8 + i * 46, b - 16 - e * 36, 38), t, _farbe(daten, e), nr=i)
    p.end()
    return img


def _prozess(daten: dict, pts, b: int) -> QImage:
    je_zeile = 4
    zeilen = -(-len(pts) // je_zeile)
    bw = (b - 16 - (min(len(pts), je_zeile) - 1) * 34) / min(len(pts), je_zeile)
    img, p = _bild(b, 16 + zeilen * 96)
    for i, (e, t) in enumerate(pts):
        z, s = divmod(i, je_zeile)
        r = QRectF(8 + s * (bw + 34), 8 + z * 96, bw, 80)
        _kasten(p, r, t, _farbe(daten, 0 if daten.get("farben") != "Bunt" else i), nr=i)
        if i < len(pts) - 1 and s < je_zeile - 1:
            _pfeil(p, QPointF(r.right() + 4, r.center().y()), QPointF(r.right() + 30, r.center().y()), QColor(Farbe.GRAU))
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
        a, c = pos[i], pos[(i + 1) % n]
        if n > 1:
            w = math.atan2(c.y() - a.y(), c.x() - a.x())
            _pfeil(p, QPointF(a.x() + 62 * math.cos(w), a.y() + 30 * math.sin(w)), QPointF(c.x() - 66 * math.cos(w), c.y() - 33 * math.sin(w)),
                   QColor(Farbe.GRAU))
    for i, (e, t) in enumerate(pts):
        _kasten(p, QRectF(pos[i].x() - 56, pos[i].y() - 26, 112, 52), t, _farbe(daten, i if daten.get("farben") == "Bunt" else 0), 26, nr=i)
    p.end()
    return img


def _pyramide(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    zh = 54
    img, p = _bild(b, 16 + n * zh)
    mitte = b / 2
    for i, (e, t) in enumerate(pts):
        oben, unten = 8 + i * zh, 8 + (i + 1) * zh - 4
        bo, bu = (i / n) * (b - 16) / 2 + 0.0, ((i + 1) / n) * (b - 16) / 2
        poly = QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)])
        c = _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2))
        _fuellen(p, c, QRectF(mitte - bu, oben, 2 * bu, unten - oben)); p.drawPolygon(poly)
        p.setPen(_text_farbe(_stilfarbe(c))); _schrift(p, t, 11)
        _text_zeichnen(p, QRectF(mitte - bu * 0.8, oben, bu * 1.6, unten - oben), Qt.AlignCenter | Qt.TextWordWrap, t)
        _merke(i, QRectF(mitte - bu, oben, 2 * bu, unten - oben))
    p.end()
    return img


# ---- Layouts des Dialogs (Foto-Katalog): Raster, Listen mit Aufzählung, Spaltenrahmen, Bildliste, Perspektive, Konvergenz, Karten, Kreise ------
def _eintraege(pts) -> list[tuple[int, str, list[str], list[int]]]:
    """Oberste Ebene als Eintrag: [(Nr., Überschrift, Textzeilen (Aufzählungspunkte und Unterpunkte), [Nr. der Unterpunkte])]."""
    out = []
    for ni, t, kinder in _gruppen(pts):
        kopf, *rest = t.split("\n")
        zeilen = [z.removeprefix(BULLET).strip() for z in rest]
        for _nj, k in kinder:
            zeilen += [z.removeprefix(BULLET).strip() for z in k.split("\n")]
        out.append((ni, kopf, zeilen, [nj for nj, _k in kinder]))
    return out


def _merke_mehrere(nummern, r: QRectF) -> None:
    for nj in nummern:
        _merke(nj, r)


def _zeilen(p: QPainter, r: QRectF, zeilen: list[str], grund: QColor, kopf: str = "") -> None:
    """Aufzählungszeilen linksbündig in ``r`` (Textfarbe nach dem Untergrund ``grund``); ``kopf`` steht vorweg, wenn gegeben."""
    p.setPen(_text_farbe(_stilfarbe(grund))); _schrift(p, "x", 10)
    t = "\n".join(([kopf] if kopf else []) + [BULLET + z for z in zeilen])
    _text_zeichnen(p, r, Qt.AlignLeft | Qt.AlignVCenter, t)


def _blockraster(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    kw, kh = (b - 16 - 10) / 2, 64
    zl = -(-n // 2)
    img, p = _bild(b, 16 + zl * kh + (zl - 1) * 10)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, 2)
        allein = i == n - 1 and n % 2 == 1                                  # ein einzelner letzter Block steht mittig
        x = (b - kw) / 2 if allein else 8 + s * (kw + 10)
        _kasten(p, QRectF(x, 8 + z * (kh + 10), kw, kh), t, _bunt(daten, i), 4, nr=i)
    p.end()
    return img


def _punktliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    hoehen = [44 + 6 + max(1, len(z)) * 17 for _ni, _k, z, _c in es]
    img, p = _bild(b, 16 + sum(hoehen) + (len(es) - 1) * 12)
    y = 8.0
    for (ni, kopf, zeilen, kinder), h in zip(es, hoehen):
        c = _bunt(daten, ni)
        _kasten(p, QRectF(8, y, b - 16, 44), kopf, c, 4, nr=ni)
        feld = QRectF(16, y + 48, b - 32, h - 48)
        _zeilen(p, feld, zeilen, QColor("white")); _merke_mehrere(kinder, feld)
        y += h + 12
    p.end()
    return img


def _balkenliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    zh = 60
    img, p = _bild(b, 16 + len(es) * zh)
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        y = 8 + i * zh
        c = _bunt(daten, i)
        rahmen = QRectF(b * 0.34, y + 6, b * 0.66 - 8, zh - 14)
        _fuellen(p, c.lighter(185), rahmen); p.drawRect(rahmen)
        _kasten(p, QRectF(8, y, b * 0.5, zh - 6), kopf, c, 3, nr=ni)
        feld = QRectF(b * 0.5 + 10, y + 8, b * 0.5 - 20, zh - 18)
        _zeilen(p, feld, zeilen, c.lighter(185)); _merke_mehrere(kinder, feld)
    p.end()
    return img


def _beschreibungsliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    zh = 66
    img, p = _bild(b, 16 + len(es) * zh)
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        y = 8 + i * zh
        c = _bunt(daten, i)
        rahmen = QRectF(b * 0.36, y, b * 0.64 - 8, zh - 8)
        _fuellen(p, c.lighter(185), rahmen); p.drawRect(rahmen)
        _kasten(p, QRectF(8, y, b * 0.3, zh - 8), kopf, c, 3, nr=ni)
        feld = QRectF(b * 0.36 + 10, y + 4, b * 0.64 - 28, zh - 16)
        _zeilen(p, feld, zeilen, c.lighter(185)); _merke_mehrere(kinder, feld)
    p.end()
    return img


def _spaltenrahmen(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    spalten = g[0][2] if g else []
    fuss = g[-1] if len(g) > 1 else None
    n = max(1, len(spalten))
    h = 300
    img, p = _bild(b, h)
    c = _bunt(daten, 0)
    rahmen = QRectF(8, 8, b - 16, h - 16)
    _fuellen(p, c.lighter(185), rahmen); p.drawRect(rahmen)
    kopf = QRectF(8, 8, b - 16, 52)
    _kasten(p, kopf, g[0][1] if g else "", c, 0, nr=g[0][0] if g else None)
    fu = QRectF(8, h - 8 - 44, b - 16, 44)
    _kasten(p, fu, fuss[1] if fuss else "", c, 0, nr=fuss[0] if fuss else None)
    breite = (b - 16) / n
    for i, (nj, t) in enumerate(spalten):
        r = QRectF(8 + i * breite, 60, breite, h - 16 - 52 - 44)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(Qt.NoBrush); p.drawRect(r)
        _text(p, r.adjusted(4, 4, -4, -4), t, c.lighter(185)); _merke(nj, r)
    p.end()
    return img


def _bildliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    zh = 80
    img, p = _bild(b, 16 + len(es) * zh)
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        y = 8 + i * zh
        c = _bunt(daten, i)
        r = QRectF(8, y, b - 16, zh - 8)
        _fuellen(p, c, r); p.drawRect(r)
        bild = QRectF(16, y + 8, zh - 24, zh - 24)                           # Platzhalter für das Bild: Rahmen mit Sonne und Hügel
        p.setPen(QPen(c.darker(150), 1)); p.setBrush(QColor("white")); p.drawRect(bild)
        p.setPen(Qt.NoPen); p.setBrush(c.lighter(150))
        p.drawEllipse(QPointF(bild.left() + bild.width() * 0.7, bild.top() + bild.height() * 0.3), bild.width() * 0.1, bild.width() * 0.1)
        p.drawPolygon(QPolygonF([QPointF(bild.left() + 3, bild.bottom() - 3), QPointF(bild.left() + bild.width() * 0.4, bild.top() + bild.height() * 0.45),
                                 QPointF(bild.right() - 3, bild.bottom() - 3)]))
        feld = QRectF(bild.right() + 12, y + 4, r.right() - bild.right() - 20, zh - 16)
        _zeilen(p, feld, zeilen, c, kopf); _merke(ni, r); _merke_mehrere(kinder, r)
    p.end()
    return img


def _perspektive(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    n = len(es)
    h = 300
    img, p = _bild(b, h)
    w = (b - 16 - (n - 1) * 8) / n
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        x = 8 + i * (w + 8)
        c = _bunt(daten, i)
        poly = QPolygonF([QPointF(x, 8 + 36), QPointF(x + w, 8), QPointF(x + w, h - 8), QPointF(x, h - 8 - 36)])      # links niedriger: perspektivisch geneigt
        _fuellen(p, c, QRectF(x, 8, w, h - 16)); p.drawPolygon(poly)
        feld = QRectF(x + 6, 52, w - 12, h - 104)
        _zeilen(p, feld, zeilen, c, kopf)
        _merke(ni, QRectF(x, 8, w, h - 16)); _merke_mehrere(kinder, QRectF(x, 8, w, h - 16))
    p.end()
    return img


def _konvergenz(daten: dict, pts, b: int) -> QImage:
    quellen, ziel = (pts[:-1], pts[-1]) if len(pts) > 1 else ([], pts[0])
    h = 320
    img, p = _bild(b, h)
    mx, my, rad = b / 2, h - 8 - 52, 52.0
    n = len(quellen)
    boxen = []
    for i in range(n):
        t = 0.0 if n == 1 else -1 + 2 * i / (n - 1)
        boxen.append(QRectF(mx + t * (b / 2 - 80) - 65, 12 + 60 * abs(t), 130, 62))
    for r in boxen:                                                           # Pfeile zuerst, die Kästen decken ihre Enden
        a = QPointF(r.center().x(), r.bottom())
        w = math.atan2(my - a.y(), mx - a.x())
        _pfeil(p, QPointF(r.center().x(), r.bottom() + 3), QPointF(mx - (rad + 4) * math.cos(w), my - (rad + 4) * math.sin(w)), QColor(Farbe.GRAU))
    for i, r in enumerate(boxen):
        _kasten(p, r, quellen[i][1], _bunt(daten, i), 4, nr=i)
    _kasten(p, QRectF(mx - rad, my - rad, 2 * rad, 2 * rad), ziel[1], _farbe(daten, 0 if daten.get("farben") != "Bunt" else n), rad, nr=len(pts) - 1)
    p.end()
    return img


def _kartenprozess(daten: dict, pts, b: int) -> QImage:
    je = 3
    zeilen = -(-len(pts) // je)
    n = min(len(pts), je)
    bw = (b - 16 - (n - 1) * 60 - 20) / n
    img, p = _bild(b, 16 + zeilen * 110 + 10)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, je)
        r = QRectF(8 + s * (bw + 60) + 20, 8 + z * 110 + 20, bw, 70)
        c = _bunt(daten, i)
        for d in (2, 1):                                                      # zwei Karten dahinter, leicht versetzt
            _fuellen(p, c.lighter(150 + 20 * d), QRectF(r.x() - 10 * d, r.y() - 10 * d, bw, 70)); p.drawRoundedRect(QRectF(r.x() - 10 * d, r.y() - 10 * d, bw, 70), 4, 4)
        _kasten(p, r, t, c, 4, nr=i)
        if i < len(pts) - 1 and s < je - 1:
            _pfeil(p, QPointF(r.right() + 4, r.center().y()), QPointF(r.right() + 36, r.center().y()), QColor(Farbe.GRAU))
    p.end()
    return img


def _kreisbeziehung(daten: dict, pts, b: int) -> QImage:
    h = 400
    img, p = _bild(b, h)
    mx, my, rad = b / 2, h / 2, 120.0
    rest = pts[1:]
    n = len(rest)
    c0 = _farbe(daten, 0)
    _fuellen(p, c0, QRectF(mx - rad, my - rad, 2 * rad, 2 * rad)); p.drawEllipse(QPointF(mx, my), rad, rad)
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        q = QPointF(mx + rad * math.cos(a), my + rad * math.sin(a))             # die kleinen Kreise sitzen auf dem Rand des großen
        c = _bunt(daten, i + 1) if daten.get("farben") == "Bunt" else _farbe(daten, 1)
        c.setAlpha(215)
        r = QRectF(q.x() - 48, q.y() - 48, 96, 96)
        _kasten(p, r, rest[i][1], c, 48, nr=i + 1)
    _text(p, QRectF(mx - 60, my - 40, 120, 80), pts[0][1], c0); _merke(0, QRectF(mx - 60, my - 40, 120, 80))
    p.end()
    return img


def _segmentzyklus(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    h = 360
    img, p = _bild(b, h)
    mx, my, rad = b / 2, h / 2, 100.0
    kreis = QRectF(mx - rad, my - rad, 2 * rad, 2 * rad)
    for i in range(n):
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 0 if i % 2 == 0 else 1)
        _fuellen(p, c, kreis)
        p.drawPie(kreis, int((90 - 360 * i / n) * 16), int(-360 / n * 16))
    p.setPen(QPen(QColor("white"), 3)); p.setBrush(QColor("white")); p.drawEllipse(QPointF(mx, my), 30, 30)
    p.setPen(QPen(QColor(Farbe.GRAU), 3)); p.setBrush(Qt.NoBrush)
    p.drawArc(QRectF(mx - 16, my - 16, 32, 32), 30 * 16, 290 * 16)
    for i, (_e, t) in enumerate(pts):
        a = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 1)
        cx = min(max(mx + (rad + 95) * math.cos(a), 8 + 75), b - 8 - 75)
        cy = min(max(my + (rad + 30) * math.sin(a), 8 + 31), h - 8 - 31)
        _kasten(p, QRectF(cx - 75, cy - 31, 150, 62), t, c.lighter(160), 3, nr=i)
    p.end()
    return img


_ZEICHNER = {"Organigramm": _organigramm, "Hierarchie": _organigramm, "Liste": _liste, "Prozess": _prozess, "Zyklus": _zyklus, "Pyramide": _pyramide,
             "Spalten": _spalten, "Gruppen": _gruppenliste, "Matrix": _matrix, "Chevron": _chevron, "Radial": _radial,
             "Zielscheibe": _zielscheibe, "Trichter": _trichter, "Zeitachse": _zeitachse, "Stufen": _stufen,
             "Blockraster": _blockraster, "Punktliste": _punktliste, "Balkenliste": _balkenliste, "Beschreibungsliste": _beschreibungsliste,
             "Spaltenrahmen": _spaltenrahmen, "Bildliste": _bildliste, "Perspektive": _perspektive, "Konvergenz": _konvergenz,
             "Kartenprozess": _kartenprozess, "Kreisbeziehung": _kreisbeziehung, "Segmentzyklus": _segmentzyklus}


