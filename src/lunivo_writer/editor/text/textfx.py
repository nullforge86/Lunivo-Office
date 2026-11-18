"""Texteffekte, die Qt am Text nicht kennt und die Lunivo über den Umrissen der Buchstaben selbst zeichnet: Farbverlauf in Füllung und Kontur,
Schatten, Spiegelung, Leuchten und 3D-Format.

Ein Effekt (``fx``) ist ein Wörterbuch; nicht gesetzte Teile fehlen:

* ``verlauf``: {"farbe1", "farbe2", "winkel"} — Farbverlauf als Füllung (dann ist ``fuell`` = "verlauf")
* ``kontur_verlauf``: wie ``verlauf``, für die Kontur
* ``kontur_form``: "einfach" | "doppelt" | "dick_duenn" — mehrfache Konturlinien
* ``schatten``: {"art": "aussen" | "innen" | "persp", "farbe", "transparenz" %, "groesse" %, "weich" pt, "abstand" pt, "winkel" Grad}
* ``reflektion``: {"groesse" %, "transparenz" %, "weich" pt, "abstand" pt}
* ``leuchten``: {"farbe", "groesse" pt, "transparenz" %}
* ``fuell_pinsel``: {"art": "muster" | "textur" | "bild", "key", "farbe", "grund", "bild_b64"} — Muster-, Textur- oder Bildfüllung (``fuell`` = "muster" | "bild")
* ``text_3d``: {"x", "y", "z" Grad, "perspektive" Grad} — 3D-Drehung des Textes (nur Text im Diagramm, ``pfad_verformen``)
* ``warp``: {"art": Schlüssel aus ``WARP_FORMEN``} — Transformieren (Textverformung, nur Text im Diagramm)
* ``d3``: {"tiefe" pt, "tiefe_farbe", "kontur" pt, "kontur_farbe", "material", "beleuchtung", "winkel" Grad}

``fx_zeichnen`` malt die Effekte zu einem Pfad (den Umrissen eines Textstücks) hinter und über den Text; ``absaetze_zeichnen`` holt die Pfade
aus dem Layout des Dokuments (Editor und PDF rufen es zusammen mit den Rahmen und Nummern auf).
"""
from __future__ import annotations

import json
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPainterPathStroker, QPen, QPolygonF, QTransform

from lunivo_writer.kern.farben import Farbe
PX = 96 / 72                                    # Punkt → Bildpunkt

MATERIAL = (("matt", "Matt"), ("plastik", "Plastik"), ("metall", "Metall"), ("dunkel", "Dunkle Kanten"), ("weich", "Weicher Rand"), ("hell", "Hell"))
BELEUCHTUNG = (("neutral", "Neutral"), ("weich", "Weich"), ("hart", "Hart"), ("warm", "Warm"), ("kalt", "Kalt"), ("kontrast", "Kontrast"))


def _farbe(hexwert: str, transparenz: float = 0.0) -> QColor:
    c = QColor(hexwert or Farbe.SCHWARZ)
    c.setAlphaF(max(0.0, min(1.0, 1.0 - transparenz / 100)))
    return c


SCHLUESSEL = ("verlauf", "kontur_verlauf", "kontur_form", "schatten", "reflektion", "leuchten", "d3", "fuell_pinsel", "text_3d", "warp")


def hat_effekt(fx: dict | None) -> bool:
    return bool(fx) and any(k in fx for k in SCHLUESSEL)


def als_text(fx: dict | None) -> str:
    """Nur die Teile, die Lunivo selbst zeichnet, als JSON für das Zeichenformat (leer = keiner)."""
    if not hat_effekt(fx):
        return ""
    erlaubt = list(SCHLUESSEL)
    if "kontur_verlauf" in fx or fx.get("kontur_form"):                  # die Kontur zeichnet dann Lunivo: Farbe, Breite und Strichart gehören dazu
        erlaubt += ["kontur_art", "kontur_breite", "kontur_farbe"]
    return json.dumps({k: v for k, v in fx.items() if k in erlaubt}, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def aus_text(text: str | None) -> dict:
    try:
        d = json.loads(text) if text else {}
        return d if isinstance(d, dict) else {}
    except ValueError:
        return {}


# ---- Bausteine -------------------------------------------------------------------------------------------------------------
def _verlauf(rect: QRectF, v: dict) -> QLinearGradient:
    w = math.radians(v.get("winkel", 90))
    mitte = rect.center()
    r = (abs(math.cos(w)) * rect.width() + abs(math.sin(w)) * rect.height()) / 2 or 1.0       # halbe Länge der Verlaufsstrecke durch das Rechteck
    d = QPointF(math.cos(w) * r, math.sin(w) * r)
    g = QLinearGradient(mitte - d, mitte + d)
    g.setColorAt(0, QColor(v.get("farbe1", Farbe.SCHWARZ))); g.setColorAt(1, QColor(v.get("farbe2", Farbe.WEISS)))
    return g


def fuell_pinsel_von(d: dict, rect: QRectF) -> QBrush | None:
    """Der Pinsel zu ``fuell_pinsel`` (Muster, Textur, Bild); ``rect``: Fläche, über die ein Bild gestreckt wird."""
    art = d.get("art", "muster")
    if art == "muster":
        from lunivo_writer.editor.text import muster as M
        return M.pinsel(d.get("key", "rein"), d.get("farbe", Farbe.SCHWARZ), d.get("grund") or None)
    if art == "textur":
        from lunivo_writer.editor.text.textur import textur
        return QBrush(textur(d.get("key", "papier"), 64))
    if art == "bild":
        from lunivo_writer.editor.diagramme.diagramm_format import bild_dekodieren
        img = bild_dekodieren(d.get("bild_b64", ""))
        if img.isNull():
            return None
        return QBrush(img.scaled(max(1, int(rect.width())), max(1, int(rect.height())), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    return None


WARP_FORMEN = (("keine", "Keine Transformation"), ("bogen", "Bogen nach oben"), ("bogen_unten", "Bogen nach unten"), ("welle", "Welle"),
               ("trichter", "Trichter"), ("kaskade_auf", "Kaskade aufwärts"), ("kaskade_ab", "Kaskade abwärts"))


def _warp_y(art: str, x: float, y: float, u: float, hoehe: float, mitte_y: float) -> float:
    """Die Höhe eines Punktes nach der Textverformung ``art`` (``u``: Lage 0..1 in der Breite des Pfades)."""
    if art == "bogen":
        return y - hoehe * 0.7 * math.sin(math.pi * u)
    if art == "bogen_unten":
        return y + hoehe * 0.7 * math.sin(math.pi * u)
    if art == "welle":
        return y + hoehe * 0.4 * math.sin(2 * math.pi * u)
    if art == "trichter":
        return mitte_y + (y - mitte_y) * (1.0 - 0.6 * u)
    if art == "kaskade_auf":
        return y - hoehe * 0.8 * u
    if art == "kaskade_ab":
        return y + hoehe * 0.8 * u
    return y


def _drehen_3d(x: float, y: float, m: QPointF, rx: float, ry: float, rz: float, dist: float) -> tuple[float, float]:
    """Ein Punkt nach der Drehung um Z, X, Y (Bogenmaß) um die Mitte ``m`` mit Perspektive (``dist``: Augenabstand, 0 = keine)."""
    a, b, c = x - m.x(), y - m.y(), 0.0
    a, b = a * math.cos(rz) - b * math.sin(rz), a * math.sin(rz) + b * math.cos(rz)             # Z
    b, c = b * math.cos(rx) - c * math.sin(rx), b * math.sin(rx) + c * math.cos(rx)             # X
    a, c = a * math.cos(ry) + c * math.sin(ry), -a * math.sin(ry) + c * math.cos(ry)           # Y
    f = dist / max(dist - c, dist * 0.2) if dist else 1.0
    return m.x() + a * f, m.y() + b * f


def _augenabstand(d3: dict, breite: float, hoehe: float) -> float:
    """Abstand des Auges für die Perspektive (0 = ohne) aus dem Blickwinkel ``perspektive``."""
    persp = max(0.0, min(120.0, float(d3.get("perspektive", 45) or 0)))
    return (max(breite, hoehe) / 2) / math.tan(math.radians(persp) / 2) if persp > 1 else 0.0


def _polygon_verformen(poly: QPolygonF, art: str, r: QRectF, m: QPointF, drehung: tuple[float, float, float], dist: float) -> list[QPointF]:
    """Die Punkte eines feinen Linienzugs (in vierfacher Größe) nach Verformung und 3D-Drehung."""
    breite, hoehe = max(r.width(), 1.0), max(r.height(), 1.0)
    pts = []
    for i in range(poly.count()):
        q = poly.at(i); x, y = q.x() / 4, q.y() / 4
        y = _warp_y(art, x, y, (x - r.left()) / breite, hoehe, m.y())
        if any(drehung):
            x, y = _drehen_3d(x, y, m, *drehung, dist)
        pts.append(QPointF(x, y))
    return pts


def pfad_verformen(pfad: QPainterPath, fx: dict | None) -> QPainterPath:
    """Der Textpfad nach ``warp`` (Transformieren) und ``text_3d`` (3D-Drehung um X, Y, Z mit Perspektive); ohne beides unverändert.
    Die Punkte werden einzeln abgebildet (der Pfad wird dafür in feine Linienzüge zerlegt)."""
    fx = fx or {}
    art = (fx.get("warp") or {}).get("art", "keine")
    d3 = fx.get("text_3d") or {}
    drehung = tuple(math.radians(float(d3.get(k, 0) or 0)) for k in ("x", "y", "z"))
    if art == "keine" and not any(drehung) or pfad.isEmpty():
        return pfad
    r = pfad.boundingRect()
    dist = _augenabstand(d3, max(r.width(), 1.0), max(r.height(), 1.0))
    aus = QPainterPath()
    for poly in QTransform().scale(4, 4).map(pfad).toSubpathPolygons():
        pts = _polygon_verformen(poly, art, r, r.center(), drehung, dist)
        if pts:
            aus.addPolygon(QPolygonF(pts)); aus.closeSubpath()
    return aus


def _weich(p: QPainter, pfad: QPainterPath, farbe: QColor, radius: float) -> None:
    """Pfad mit weichem Rand: gefüllt, dazu Striche in wachsender Breite und sinkender Deckkraft."""
    if radius <= 0.3:
        p.fillPath(pfad, farbe); return
    schritte = 7
    a = farbe.alphaF()
    kern = QColor(farbe); kern.setAlphaF(a * 0.55)
    p.fillPath(pfad, kern)
    for k in range(1, schritte + 1):
        f = QColor(farbe); f.setAlphaF(a * 0.45 / schritte * (1.0 + (schritte - k) / schritte))
        pen = QPen(f, 2 * radius * k / schritte); pen.setJoinStyle(Qt.RoundJoin); pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen); p.drawPath(pfad)
    p.setPen(Qt.NoPen)


def _richtung(winkel: float) -> QPointF:
    w = math.radians(winkel)
    return QPointF(math.cos(w), math.sin(w))


def _helligkeit(c: QColor, f: float) -> QColor:
    return c.lighter(int(100 * f)) if f >= 1.0 else c.darker(int(100 / max(f, 0.05)))


# Bahnen der Mehrfachlinien: (Abstand von der Mitte, Dicke) in Linienbreiten (negativ = links der Laufrichtung)
_BAHNEN = {"dick_duenn": ((-0.9, 1.2), (0.9, 0.6)), "duenn_dick": ((-0.9, 0.6), (0.9, 1.2)), "dreifach": ((-1.4, 0.6), (0.0, 0.6), (1.4, 0.6))}


def _normale(a: QPointF | None, q: QPointF, b: QPointF | None) -> tuple[float, float]:
    """Die Einheitsnormale am Eckpunkt ``q`` zwischen Vorgänger ``a`` und Nachfolger ``b`` (fehlende Nachbarn zählen nicht)."""
    nx = ny = 0.0
    for u, v in ((a, q), (q, b)):
        if u is None or v is None:
            continue
        dx, dy = v.x() - u.x(), v.y() - u.y(); L = math.hypot(dx, dy) or 1.0
        nx += -dy / L; ny += dx / L
    L = math.hypot(nx, ny) or 1.0
    return nx / L, ny / L


def _linienzug_versetzt(pts: list[QPointF], zu: bool, abstand: float) -> list[QPointF]:
    """Die Eckpunkte eines Linienzugs entlang ihrer Normalen um ``abstand`` verschoben (``zu``: geschlossen)."""
    n = len(pts)
    neu = []
    for i, q in enumerate(pts):
        nx, ny = _normale(pts[i - 1] if (i > 0 or zu) else None, q, pts[(i + 1) % n] if (i < n - 1 or zu) else None)
        neu.append(QPointF(q.x() + nx * abstand, q.y() + ny * abstand))
    return neu


def _versetzt(pfad: QPainterPath, abstand: float) -> QPainterPath:
    """Der Pfad seitlich um ``abstand`` verschoben (Eckpunkte entlang ihrer Normalen, mit begrenzter Spitze); für Linien und geschlossene Formen."""
    aus = QPainterPath()
    for poly in pfad.toSubpathPolygons():
        pts = [poly.at(i) for i in range(poly.count())]
        if len(pts) < 2:
            continue
        zu = len(pts) > 2 and pts[0] == pts[-1]
        neu = _linienzug_versetzt(pts[:-1] if zu else pts, zu, abstand)
        aus.moveTo(neu[0])
        for q in neu[1:]:
            aus.lineTo(q)
        if zu:
            aus.closeSubpath()
    return aus


def _kontur_pfade(pfad: QPainterPath, breite: float, form: str, art: str = "einfach") -> list[QPainterPath]:
    """Die Flächen einer Konturlinie: einfach ein Strich, doppelt zwei Streifen mit Lücke, dick–dünn/dünn–dick zwei ungleiche, dreifach drei Streifen."""
    from lunivo_writer.editor.text.texteffekt import KONTUR_ARTEN, KONTUR_ARTEN_PLUS
    rund = False
    if art in KONTUR_ARTEN_PLUS:
        st, rund = KONTUR_ARTEN_PLUS[art]
    else:
        st = KONTUR_ARTEN.get(art, KONTUR_ARTEN["einfach"])[1]

    def strich(w: float, gestrichelt: bool = False, bahn: QPainterPath | None = None) -> QPainterPath:
        s = QPainterPathStroker(); s.setWidth(max(0.1, w)); s.setJoinStyle(Qt.RoundJoin)
        s.setCapStyle(Qt.RoundCap if rund or not gestrichelt else Qt.FlatCap)
        if gestrichelt and st != Qt.SolidLine:
            s.setDashPattern(st)
        return s.createStroke(bahn if bahn is not None else pfad)
    if form == "einfach":
        return [strich(breite, True)]
    punkte = st != Qt.SolidLine                       # gewählte Strichart: Mehrfachlinien werden dann je Bahn in dieser Art gestrichelt
    if form == "doppelt":
        if punkte:
            return [strich(breite, True, _versetzt(pfad, o * breite)) for o in (-1.0, 1.0)]
        return [strich(3 * breite).subtracted(strich(breite))]
    if form in _BAHNEN:
        return [strich(d * breite, punkte, _versetzt(pfad, o * breite)) for o, d in _BAHNEN[form]]
    return [strich(breite)]


def _basisname(basis_farbe: QColor | None) -> str:
    return basis_farbe.name() if basis_farbe else Farbe.SCHWARZ


def _fx_reflektion(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, r: dict, grundlinie: float, schrift_px: float, basis_farbe: QColor | None) -> None:
    """Spiegelung unter der Grundlinie, nur außerhalb der Buchstaben."""
    sp = QTransform().translate(0, 2 * grundlinie + r.get("abstand", 0) * PX).scale(1, -1)
    spiegel = sp.map(pfad)
    hoch = max(1.0, schrift_px * 1.0 * r.get("groesse", 50) / 100)
    g = QLinearGradient(0, grundlinie + r.get("abstand", 0) * PX, 0, grundlinie + r.get("abstand", 0) * PX + hoch)
    g.setColorAt(0, _farbe(_basisname(basis_farbe), r.get("transparenz", 50)))
    g.setColorAt(1, QColor(0, 0, 0, 0))
    p.save(); p.setClipPath(aussen)
    if r.get("weich", 0) > 0:
        _weich(p, spiegel, _farbe(_basisname(basis_farbe), 85), r["weich"] * PX * 0.5)
    else:
        p.fillPath(spiegel, QBrush(g))
    p.restore()


def _tiefe_faktor(mat: str, licht: str, t: float) -> float:
    """Helligkeitsfaktor einer Tiefenschicht ``t`` (0..1) nach Material und Beleuchtung."""
    f = {"plastik": 1.25 - 0.5 * t, "metall": 1.0 + 0.45 * math.sin(t * math.pi * 2), "dunkel": 0.6 + 0.4 * (1 - t), "weich": 1.15 - 0.25 * t,
         "hell": 1.3}.get(mat, 1.0)
    return f * {"neutral": 1.0, "weich": 1.08, "hart": 0.8 + 0.5 * (1 - t), "warm": 1.0, "kalt": 1.0, "kontrast": 0.7 + 0.7 * t}.get(licht, 1.0)


def _tiefe_farbe(basis: QColor, f: float, licht: str) -> QColor:
    c = _helligkeit(basis, max(0.3, f))
    if licht == "warm":
        c = QColor(min(255, c.red() + 25), c.green(), max(0, c.blue() - 20))
    elif licht == "kalt":
        c = QColor(max(0, c.red() - 20), c.green(), min(255, c.blue() + 25))
    return c


def _fx_3d(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, d3: dict) -> None:
    """3D-Format: Tiefenschichten hinter dem Text, optional mit Kontur."""
    tiefe = d3["tiefe"] * PX
    richt = _richtung(d3.get("winkel", 45) + 45)
    n = max(2, int(tiefe))
    basis = QColor(d3.get("tiefe_farbe", "#808080"))
    mat, licht = d3.get("material", "matt"), d3.get("beleuchtung", "neutral")
    p.save(); p.setClipPath(aussen); p.setPen(Qt.NoPen)
    for k in range(n, 0, -1):
        t = k / n
        c = _tiefe_farbe(basis, _tiefe_faktor(mat, licht, t), licht)
        p.fillPath(QTransform().translate(richt.x() * tiefe * t, richt.y() * tiefe * t).map(pfad), c)
    if d3.get("kontur", 0) > 0:
        pen = QPen(QColor(d3.get("kontur_farbe", "#404040")), d3["kontur"] * PX)
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen); p.drawPath(QTransform().translate(richt.x() * tiefe, richt.y() * tiefe).map(pfad)); p.drawPath(pfad)
    p.restore()


def _fx_schatten_aussen(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, s: dict, rect: QRectF, grundlinie: float) -> None:
    """Schatten hinter dem Text (``aussen`` oder ``persp``)."""
    abst = s.get("abstand", 3) * PX
    dr = _richtung(s.get("winkel", 45))
    sk = s.get("groesse", 100) / 100
    farbe = _farbe(s.get("farbe", Farbe.SCHWARZ), s.get("transparenz", 50))
    if s.get("art") == "persp":                       # flach auf den Boden gelegt und in Richtung des Lichts geneigt
        t = QTransform()
        t.translate(dr.x() * abst * 0.5, grundlinie + abst * 0.3); t.shear(-dr.x() * 0.8, 0); t.scale(sk, -0.4 * sk); t.translate(0, -grundlinie)
    else:
        t = QTransform().translate(rect.center().x(), rect.center().y()).scale(sk, sk).translate(-rect.center().x(), -rect.center().y()) \
            * QTransform().translate(dr.x() * abst, dr.y() * abst)
    p.save(); p.setClipPath(aussen); p.setPen(Qt.NoPen)
    _weich(p, t.map(pfad), farbe, s.get("weich", 4) * PX * 0.6)
    p.restore()


def _fx_leuchten(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, g: dict) -> None:
    farbe = _farbe(g.get("farbe", Farbe.BLAU), g.get("transparenz", 60))
    p.save(); p.setClipPath(aussen); p.setPen(Qt.NoPen)
    _weich(p, pfad, farbe, g["groesse"] * PX)
    p.restore()


def _fx_fuellung(p: QPainter, pfad: QPainterPath, fx: dict, rect: QRectF) -> None:
    """Verlauf- und Pinselfüllung (Muster, Textur, Bild) über den Buchstaben."""
    if "verlauf" in fx:
        p.save(); p.setClipPath(pfad); p.fillRect(rect.adjusted(-2, -2, 2, 2), QBrush(_verlauf(rect, fx["verlauf"]))); p.restore()
    if fx.get("fuell_pinsel"):
        pi = fuell_pinsel_von(fx["fuell_pinsel"], rect)
        if pi is not None:
            p.save(); p.setClipPath(pfad); p.fillRect(rect.adjusted(-2, -2, 2, 2), pi); p.restore()


def _fx_schatten_innen(p: QPainter, pfad: QPainterPath, s: dict, rect: QRectF) -> None:
    abst = s.get("abstand", 3) * PX
    dr = _richtung(s.get("winkel", 45))
    farbe = _farbe(s.get("farbe", Farbe.SCHWARZ), s.get("transparenz", 50))
    innen = QPainterPath(); innen.addRect(rect.adjusted(-50, -50, 50, 50))
    loch = QTransform().translate(dr.x() * abst, dr.y() * abst).map(pfad)
    p.save(); p.setClipPath(pfad); p.setPen(Qt.NoPen)
    _weich(p, innen.subtracted(loch), farbe, s.get("weich", 4) * PX * 0.5)
    p.restore()


def _fx_kontur(p: QPainter, pfad: QPainterPath, fx: dict, rect: QRectF, kontur: tuple[QColor, float, str] | None) -> None:
    """Konturlinie (einfach/mehrfach, Farbe oder Verlauf), wenn sie Lunivo zeichnet."""
    if kontur is None and "kontur_verlauf" not in fx and fx.get("kontur_form", "einfach") == "einfach":
        return
    farbe, breite, form, *rest = kontur if kontur else (QColor(Farbe.SCHWARZ), 0.75 * PX, fx.get("kontur_form", "einfach"))
    brush = QBrush(_verlauf(rect, fx["kontur_verlauf"])) if "kontur_verlauf" in fx else QBrush(farbe)
    for flaeche in _kontur_pfade(pfad, breite, fx.get("kontur_form", form), rest[0] if rest else fx.get("kontur_art", "einfach")):
        p.fillPath(flaeche, brush)


def fx_zeichnen(p: QPainter, pfad: QPainterPath, fx: dict, grundlinie: float, schrift_px: float, basis_farbe: QColor | None = None,
                kontur: tuple[QColor, float, str] | None = None) -> None:
    """Die Effekte zu einem Textstück zeichnen. ``pfad``: Umrisse in Zeichenkoordinaten, ``grundlinie``: y der Schriftlinie, ``schrift_px``: Schriftgröße.
    Der Text selbst ist schon gezeichnet (Qt); alles, was hinter ihm liegt, wird auf die Fläche außerhalb der Buchstaben beschränkt."""
    if pfad.isEmpty():
        return
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    grenze = QPainterPath(); grenze.addRect(pfad.boundingRect().adjusted(-200, -200, 200, 400 + schrift_px))
    aussen = grenze.subtracted(pfad)
    rect = pfad.boundingRect()
    _fx_hinter(p, pfad, aussen, fx, rect, grundlinie, schrift_px, basis_farbe)
    _fx_ueber(p, pfad, fx, rect, kontur)
    p.restore()


def _fx_hinter(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, fx: dict, rect: QRectF, grundlinie: float, schrift_px: float,
               basis_farbe: QColor | None) -> None:
    """Die Effekte hinter dem Text: Spiegelung, 3D-Tiefe, Schatten außen, Leuchten."""
    if fx.get("reflektion"):
        _fx_reflektion(p, pfad, aussen, fx["reflektion"], grundlinie, schrift_px, basis_farbe)
    d3 = fx.get("d3")
    if d3 and d3.get("tiefe", 0) > 0:
        _fx_3d(p, pfad, aussen, d3)
    s = fx.get("schatten")
    if s and s.get("art", "aussen") != "innen":
        _fx_schatten_aussen(p, pfad, aussen, s, rect, grundlinie)
    g = fx.get("leuchten")
    if g and g.get("groesse", 0) > 0:
        _fx_leuchten(p, pfad, aussen, g)


def _fx_ueber(p: QPainter, pfad: QPainterPath, fx: dict, rect: QRectF, kontur: tuple[QColor, float, str] | None) -> None:
    """Die Effekte über dem Text: Füllung, Schatten innen, Kontur."""
    _fx_fuellung(p, pfad, fx, rect)
    s = fx.get("schatten")
    if s and s.get("art") == "innen":
        _fx_schatten_innen(p, pfad, s, rect)
    _fx_kontur(p, pfad, fx, rect, kontur)


def text_pfad(text: str, font, ursprung: QPointF) -> tuple[QPainterPath, float]:
    """Umrisse eines Textes (für Vorschauen); → (Pfad, y der Grundlinie)."""
    pf = QPainterPath()
    pf.addText(ursprung, font, text)
    return pf, ursprung.y()


def vorschau_zeichnen(p: QPainter, rect: QRectF, text: str, font, fx: dict, farbe: QColor, kontur: tuple[QColor, float, str] | None = None) -> None:
    """Text mit Effekt zentriert in ein Rechteck zeichnen (Kacheln und Vorschau der Fenster); der Text selbst wird hier mitgezeichnet."""
    from PySide6.QtGui import QFontMetricsF
    fm = QFontMetricsF(font)
    x = rect.center().x() - fm.horizontalAdvance(text) / 2
    y = rect.center().y() + (fm.ascent() - fm.descent()) / 2
    pfad, gl = text_pfad(text, font, QPointF(x, y))
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    if farbe.alpha() > 0:                                   # erst der Text (wie im Dokument, wo Qt ihn zeichnet), dann die Effekte
        p.fillPath(pfad, farbe)
    fx_zeichnen(p, pfad, fx, gl, font.pixelSize() if font.pixelSize() > 0 else font.pointSizeF() * PX, farbe, kontur)
    p.restore()



# ---- Wiederaufführung: Zeichenzusätze/Dokumentlauf und Voreinstellungen stehen in eigenen Modulen (Aufrufer nutzen weiter ``textfx.<Name>``)
from lunivo_writer.editor.text.textfx_zeichen import (_P, _betonung, _doppelt_durch, _ruby, _stueck, _umschlossen, _unterstrich, _woerter,  # noqa: E402,F401
                                                      absaetze_zeichnen, hat_zeichen_effekt, unter_symbol, unter_zeichnen)
from lunivo_writer.editor.text.textfx_vorgaben import (form_kachel_icon, leuchten_vorgaben, reflektion_vorgaben, schatten_vorgaben,  # noqa: E402,F401
                                                       text_kachel_icon, voreinstellung_icon, wordart_icon, wordart_vorgaben)
