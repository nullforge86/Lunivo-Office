from __future__ import annotations
import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPainterPathStroker, QPen, QTransform
from core.formatierung.farben.farben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import DURCHSICHTIG
from core.objekte.wordart.textfx_daten import _BAHNEN, _tiefe_faktor
from vcl.qt.rendering.wordart.effekt_umwandlung import zu_daten, zu_dict
from writer.funktionen.objekte import wordart as _wa
from writer.funktionen.objekte.wordart import wordart_px


def schatten_vorgaben() -> list[tuple[str, str, dict]]:
    """[(Abschnitt, Name, Schatten)]."""
    return [(v.abschnitt, v.name, zu_dict(v.effekt)) for v in _wa.schatten_vorgaben()]


def reflektion_vorgaben() -> list[tuple[str, dict]]:
    """[(Name, Spiegelung)]."""
    return [(v.name, zu_dict(v.effekt)) for v in _wa.reflektion_vorgaben()]


def leuchten_vorgaben() -> list[tuple[str, dict]]:
    """[(Name, Leuchteffekt)]."""
    return [(v.name, zu_dict(v.effekt)) for v in _wa.leuchten_vorgaben()]


def wordart_vorgaben() -> list[tuple[str, dict]]:
    """[(Name, vollständiger Effekt)]."""
    return [(v.name, zu_dict(v.effekt)) for v in _wa.wordart_vorgaben()]


def hat_effekt(fx: dict | None) -> bool:
    return _wa.hat_effekt(zu_daten(fx))


def als_text(fx: dict | None) -> str:
    return _wa.als_text(zu_daten(fx))


def aus_text(text: str | None) -> dict:
    return zu_dict(_wa.aus_text(text))


def _farbe(hexwert: str, transparenz: float = 0.0) -> QColor:
    c = QColor(hexwert or Farbe.SCHWARZ)
    c.setAlphaF(max(0.0, min(1.0, 1.0 - transparenz / 100)))
    return c


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
        from vcl.qt.rendering import formen as M
        return M.pinsel(d.get("key", "rein"), d.get("farbe", Farbe.SCHWARZ), d.get("grund") or None)
    if art == "textur":
        from vcl.qt.rendering.formen import textur_textur as textur
        return QBrush(textur(d.get("key", "papier"), 64))
    if art == "bild":
        from vcl.qt.rendering.diagramme import bild_dekodieren
        img = bild_dekodieren(d.get("bild_b64", ""))
        if img.isNull():
            return None
        return QBrush(img.scaled(max(1, int(rect.width())), max(1, int(rect.height())), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    return None


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
        pen = QPen(f, (radius + radius) * k / schritte); pen.setJoinStyle(Qt.RoundJoin); pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen); p.drawPath(pfad)
    p.setPen(Qt.NoPen)


def _richtung(winkel: float) -> QPointF:
    w = math.radians(winkel)
    return QPointF(math.cos(w), math.sin(w))


def _helligkeit(c: QColor, f: float) -> QColor:
    return c.lighter(int(100 * f)) if f >= 1.0 else c.darker(int(100 / max(f, 0.05)))


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
    from vcl.qt.rendering.wordart.texteffekt import KONTUR_ARTEN, KONTUR_ARTEN_PLUS
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
    sp = QTransform().translate(0, 2 * grundlinie + r.get("abstand", 0) * wordart_px()).scale(1, -1)
    spiegel = sp.map(pfad)
    hoch = max(1.0, schrift_px * 1.0 * r.get("groesse", 50) / 100)
    g = QLinearGradient(0, grundlinie + r.get("abstand", 0) * wordart_px(), 0, grundlinie + r.get("abstand", 0) * wordart_px() + hoch)
    g.setColorAt(0, _farbe(_basisname(basis_farbe), r.get("transparenz", 50)))
    g.setColorAt(1, QColor(*DURCHSICHTIG))
    p.save(); p.setClipPath(aussen)
    if r.get("weich", 0) > 0:
        _weich(p, spiegel, _farbe(_basisname(basis_farbe), 85), r["weich"] * wordart_px() * 0.5)
    else:
        p.fillPath(spiegel, QBrush(g))
    p.restore()


def _tiefe_farbe(basis: QColor, f: float, licht: str) -> QColor:
    c = _helligkeit(basis, max(0.3, f))
    if licht == "warm":
        c = QColor(min(255, c.red() + 25), c.green(), max(0, c.blue() - 20))
    elif licht == "kalt":
        c = QColor(max(0, c.red() - 20), c.green(), min(255, c.blue() + 25))
    return c


def _fx_3d(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, d3: dict) -> None:
    """3D-Format: Tiefenschichten hinter dem Text, optional mit Kontur."""
    tiefe = d3["tiefe"] * wordart_px()
    richt = _richtung(d3.get("winkel", 45) + 45)
    n = max(2, int(tiefe))
    basis = QColor(d3.get("tiefe_farbe", Farbe.GRAU_MITTEL))
    mat, licht = d3.get("material", "matt"), d3.get("beleuchtung", "neutral")
    p.save(); p.setClipPath(aussen); p.setPen(Qt.NoPen)
    for k in range(n, 0, -1):
        t = k / n
        c = _tiefe_farbe(basis, _tiefe_faktor(mat, licht, t), licht)
        p.fillPath(QTransform().translate(richt.x() * tiefe * t, richt.y() * tiefe * t).map(pfad), c)
    if d3.get("kontur", 0) > 0:
        pen = QPen(QColor(d3.get("kontur_farbe", Farbe.GRAU_DUNKEL)), d3["kontur"] * wordart_px())
        pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen); p.drawPath(QTransform().translate(richt.x() * tiefe, richt.y() * tiefe).map(pfad)); p.drawPath(pfad)
    p.restore()


def _fx_schatten_aussen(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, s: dict, rect: QRectF, grundlinie: float) -> None:
    """Schatten hinter dem Text (``aussen`` oder ``persp``)."""
    abst = s.get("abstand", 3) * wordart_px()
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
    _weich(p, t.map(pfad), farbe, s.get("weich", 4) * wordart_px() * 0.6)
    p.restore()


def _fx_leuchten(p: QPainter, pfad: QPainterPath, aussen: QPainterPath, g: dict) -> None:
    farbe = _farbe(g.get("farbe", Farbe.BLAU), g.get("transparenz", 60))
    p.save(); p.setClipPath(aussen); p.setPen(Qt.NoPen)
    _weich(p, pfad, farbe, g["groesse"] * wordart_px())
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
    abst = s.get("abstand", 3) * wordart_px()
    dr = _richtung(s.get("winkel", 45))
    farbe = _farbe(s.get("farbe", Farbe.SCHWARZ), s.get("transparenz", 50))
    innen = QPainterPath(); innen.addRect(rect.adjusted(-50, -50, 50, 50))
    loch = QTransform().translate(dr.x() * abst, dr.y() * abst).map(pfad)
    p.save(); p.setClipPath(pfad); p.setPen(Qt.NoPen)
    _weich(p, innen.subtracted(loch), farbe, s.get("weich", 4) * wordart_px() * 0.5)
    p.restore()


def _fx_kontur(p: QPainter, pfad: QPainterPath, fx: dict, rect: QRectF, kontur: tuple[QColor, float, str] | None) -> None:
    """Konturlinie (einfach/mehrfach, Farbe oder Verlauf), wenn sie Lunivo zeichnet."""
    if kontur is None and "kontur_verlauf" not in fx and fx.get("kontur_form", "einfach") == "einfach":
        return
    farbe, breite, form, *rest = kontur if kontur else (QColor(Farbe.SCHWARZ), 0.75 * wordart_px(), fx.get("kontur_form", "einfach"))
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


def vorschau_zeichnen(p: QPainter, rect: QRectF, text: str, font, fx: dict, farbe: QColor, kontur: tuple[QColor, float, str] | None = None) -> None:
    """Text mit Effekt zentriert in ein Rechteck zeichnen (Kacheln und Vorschau der Fenster); der Text selbst wird hier mitgezeichnet."""
    from vcl.qt.rendering.formen import kern_malen
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe.text.texteffekte import zeichne_text_mit_effekt
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    pt = (font.pixelSize() * 72.0 / 96.0) if font.pixelSize() > 0 else font.pointSizeF()      # die Schrift wird als Beschreibung gelesen, gemessen und gezeichnet wird vom Kern
    fs = FontSpec(font.family(), pt, 700 if font.bold() else 400, font.italic())
    m = engine.font_metrics(fs)
    x = rect.center().x() - engine.measure_text(text, fs) / 2
    y = rect.center().y() + (m.ascent - m.descent) / 2
    face = (farbe.red(), farbe.green(), farbe.blue(), farbe.alpha()) if farbe.alpha() else (0, 0, 0, 255)
    k = None
    if kontur is not None:
        c, breite = kontur[0], float(kontur[1])
        k = ((c.red(), c.green(), c.blue(), c.alpha()), breite)

    def zeichnen(z) -> None:
        zeichne_text_mit_effekt(z, engine, text, Point(x, y), fs, (farbe.red(), farbe.green(), farbe.blue(), farbe.alpha()), fx, k)
    kern_malen(p, rect, zeichnen, rand=24.0)
