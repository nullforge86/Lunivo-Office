from __future__ import annotations
import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter, QPainterPath
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import STAERKE_BILDEFFEKT_DUNKEL, STAERKE_BILDEFFEKT_HELL, STAERKE_BILDEFFEKT_RAND
from vcl.qt.widgets.bausteine.farben.farben import ALPHA_VOLL, DURCHSICHTIG, GRAU_RGB, SCHWARZ_RGB, WEISS_RGB
from writer.anbindung.bildeffekte_daten import dreht as _dreht

_MERK: dict = {}                                                    # Schlüssel → fertiges Effektbild (kleiner Zwischenspeicher der Oberfläche)


def _merken(schluessel, bauen):
    if schluessel not in _MERK:
        if len(_MERK) > 48:
            _MERK.pop(next(iter(_MERK)))
        _MERK[schluessel] = bauen()
    return _MERK[schluessel]
from writer.anbindung.bildeffekte_daten import px_pt
from writer.anbindung.bildeffekte_daten import hat_abschluss
from writer.anbindung.bildeffekte_daten import tiefe_richtung


def gespiegelt(img: QImage, waagrecht: bool = False, senkrecht: bool = False) -> QImage:
    """Das Bild gespiegelt (links ↔ rechts und/oder oben ↔ unten). Die eine Stelle dafür: ``QImage.flipped`` gibt es ab Qt 6.9,
    davor heißt es ``mirrored`` (dort inzwischen als veraltet gemeldet)."""
    if hasattr(img, "flipped"):
        richtung = (Qt.Horizontal if waagrecht else Qt.Orientation(0)) | (Qt.Vertical if senkrecht else Qt.Orientation(0))
        return img.flipped(richtung)
    return img.mirrored(waagrecht, senkrecht)


def _maske(bild: QImage, groesse: tuple[int, int], ellipse: bool) -> QImage:
    """Die Form des Bildes (Alpha) in der gewünschten Größe: das Bild selbst, in einer Ellipse beschnitten, wenn ``ellipse``."""
    w, h = groesse
    out = QImage(w, h, QImage.Format_ARGB32_Premultiplied); out.fill(Qt.transparent)
    p = QPainter(out); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
    if ellipse:
        pf = QPainterPath(); pf.addEllipse(QRectF(0, 0, w, h)); p.setClipPath(pf)
    p.drawImage(QRectF(0, 0, w, h), bild)
    p.end()
    return out


def _getoent(maske: QImage, farbe: QColor) -> QImage:
    out = QImage(maske)
    p = QPainter(out); p.setCompositionMode(QPainter.CompositionMode_SourceIn); p.fillRect(out.rect(), farbe); p.end()
    return out


def _weich(img: QImage, radius: float) -> QImage:
    """Weichzeichnen durch Verkleinern und Vergrößern (billig und gleichmäßig); der Rand muss vorher frei sein."""
    if radius < 1.0:
        return img
    f = max(2, int(radius))
    klein = img.scaled(max(1, img.width() // f), max(1, img.height() // f), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    klein = klein.scaled(max(1, klein.width() // 2 + 1), max(1, klein.height() // 2 + 1), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return klein.scaled(img.width(), img.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


def weiche_kanten(bild: QImage, r: QRectF, ellipse: bool, radius_pt: float) -> QImage:
    """Das Bild mit weich auslaufendem Rand (Alpha nimmt zum Rand hin ab), in der Größe ``r``."""
    w, h = max(1, int(r.width())), max(1, int(r.height()))
    rad = radius_pt * px_pt()

    def bauen():
        m = _maske(bild, (w, h), ellipse)
        pad = int(rad * 2) + 2
        gross = QImage(w + 2 * pad, h + 2 * pad, QImage.Format_ARGB32_Premultiplied); gross.fill(Qt.transparent)
        p = QPainter(gross); p.drawImage(pad, pad, _getoent(m, QColor("white")).scaled(w, h)); p.end()      # die Form als weiße Fläche
        innen = QImage(gross.size(), QImage.Format_ARGB32_Premultiplied); innen.fill(Qt.transparent)
        q = QPainter(innen); q.drawImage(0, 0, gross); q.end()
        # Form verkleinern (Rand wegnehmen), dann weichzeichnen → Maske, die zum Rand hin ausläuft
        schmal = QImage(gross.size(), QImage.Format_ARGB32_Premultiplied); schmal.fill(Qt.transparent)
        q = QPainter(schmal); q.setRenderHint(QPainter.SmoothPixmapTransform)
        q.drawImage(QRectF(pad + rad, pad + rad, max(1.0, w - 2 * rad), max(1.0, h - 2 * rad)), _getoent(m, QColor("white")))
        q.end()
        weich = _weich(schmal, rad)
        out = QImage(w, h, QImage.Format_ARGB32_Premultiplied); out.fill(Qt.transparent)
        p = QPainter(out); p.setRenderHint(QPainter.SmoothPixmapTransform); p.drawImage(0, 0, m)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn); p.drawImage(0, 0, weich.copy(pad, pad, w, h)); p.end()
        return out
    return _merken(("weich", id(bild), w, h, ellipse, round(radius_pt, 1)), bauen)


def _schatten_bild(bild: QImage, w: int, h: int, ellipse: bool, farbe: QColor, weich_px: float, faktor: float) -> tuple[QImage, int]:
    """(Bild des Schattens mit Rand ringsum, Randbreite): die getönte Form, um ``faktor`` skaliert und weichgezeichnet."""
    pad = int(weich_px * 2 + max(w, h) * max(0.0, faktor - 1.0) / 2) + 4
    m = _getoent(_maske(bild, (w, h), ellipse), farbe)
    gross = QImage(w + 2 * pad, h + 2 * pad, QImage.Format_ARGB32_Premultiplied); gross.fill(Qt.transparent)
    p = QPainter(gross); p.setRenderHint(QPainter.SmoothPixmapTransform)
    sw, sh = w * faktor, h * faktor
    p.drawImage(QRectF(pad + (w - sw) / 2, pad + (h - sh) / 2, sw, sh), m); p.end()
    return _weich(gross, weich_px), pad


def unter_zeichnen(p: QPainter, bild: QImage, r: QRectF, ellipse: bool, fx: dict) -> None:
    """Leuchten, Schatten und Reflektion hinter dem Bild (in der Reihenfolge der Schichten: Leuchten zuerst)."""
    w, h = max(1, int(r.width())), max(1, int(r.height()))
    dreh = fx.get("drehung") or {}
    boden = max(0.0, float(dreh.get("boden", 0.0))) * px_pt()          # Abstand vom Boden: Schatten und Spiegelung bleiben unten, das Objekt „schwebt“
    if _dreht(dreh):                                             # Schatten, Leuchten und Tiefe gehören zur gedrehten Form (auch bei „Text nicht drehen“)
        bild, ellipse = drehung_3d(bild, r, ellipse, {**dreh, "text_gerade": False}), False
    p.save(); p.setRenderHint(QPainter.SmoothPixmapTransform)
    leu = fx.get("leuchten")
    if leu:
        c = QColor(leu.get("farbe", Farbe.BLAU)); c.setAlphaF(max(0.0, min(1.0, 1 - leu.get("transparenz", 60) / 100)))
        rad = float(leu.get("groesse", 8.0)) * px_pt()
        faktor = 1.0 + 2 * rad / max(w, h)

        def bauen_l():
            return _schatten_bild(bild, w, h, ellipse, c, rad * 0.9, faktor)
        img, pad = _merken(("leuchten", id(bild), w, h, ellipse, c.name(QColor.HexArgb), round(rad, 1)), bauen_l)
        from PySide6.QtCore import QPointF
        p.drawImage(QPointF(r.left() - pad, r.top() - pad), img)
    sch = fx.get("schatten")
    if sch:
        c = QColor(sch.get("farbe", Farbe.SCHWARZ)); c.setAlphaF(max(0.0, min(1.0, 1 - sch.get("transparenz", 60) / 100)))
        weich = float(sch.get("weich", 4.0)) * px_pt()
        faktor = max(0.2, sch.get("groesse", 100) / 100.0)

        def bauen_s():
            return _schatten_bild(bild, w, h, ellipse, c, weich, faktor)
        img, pad = _merken(("schatten", id(bild), w, h, ellipse, c.name(QColor.HexArgb), round(weich, 1), round(faktor, 2)), bauen_s)
        a = math.radians(float(sch.get("winkel", 45)))
        d = float(sch.get("abstand", 4.0)) * px_pt()
        from PySide6.QtCore import QPointF
        p.drawImage(QPointF(r.left() - pad + math.cos(a) * d, r.top() - pad + math.sin(a) * d + boden), img)
    if (fx.get("d3") or {}).get("tiefe", 0) > 0 or (fx.get("d3") or {}).get("kontur", 0) > 0:
        extrusion_zeichnen(p, bild, r, ellipse, fx["d3"], fx.get("drehung"))
    refl = fx.get("reflektion")
    if refl:
        hoehe = max(1, int(h * refl.get("groesse", 50) / 100.0))
        abst = float(refl.get("abstand", 0.0)) * px_pt()
        alpha0 = max(0.0, min(1.0, 1 - refl.get("transparenz", 50) / 100))

        def bauen_r():
            m = gespiegelt(_maske(bild, (w, h), ellipse), senkrecht=True).copy(0, 0, w, hoehe)     # gespiegelt, nur der obere Streifen
            out = QImage(w, hoehe, QImage.Format_ARGB32_Premultiplied); out.fill(Qt.transparent)
            q = QPainter(out); q.drawImage(0, 0, m)
            q.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            g = QLinearGradient(0, 0, 0, hoehe); g.setColorAt(0, QColor(*SCHWARZ_RGB, int(ALPHA_VOLL * alpha0))); g.setColorAt(1, QColor(*DURCHSICHTIG))
            q.fillRect(out.rect(), g); q.end()
            return out
        img = _merken(("refl", id(bild), w, h, ellipse, hoehe, round(alpha0, 2)), bauen_r)
        from PySide6.QtCore import QPointF
        p.drawImage(QPointF(r.left(), r.bottom() + abst + boden), img)
    p.restore()


# ---- 3D-Format: Tiefe (Extrusion) ----------------------------------------------------------------------------------------------
def _stufenfarbe(basis: QColor, material: str, licht: str, t: float) -> QColor:
    """Farbe der Tiefe in Stufe ``t`` (0 = vorn, 1 = hinten) nach Material und Beleuchtung (dieselben Namen wie bei den Texteffekten)."""
    f = {"plastik": 1.25 - 0.5 * t, "metall": 1.0 + 0.45 * math.sin(t * math.pi * 2), "dunkel": 0.6 + 0.4 * (1 - t), "weich": 1.15 - 0.25 * t,
         "hell": 1.3}.get(material, 1.0)
    f *= {"weich": 1.08, "hart": 0.8 + 0.5 * (1 - t), "kontrast": 0.7 + 0.7 * t}.get(licht, 1.0)
    hsl = basis.toHsl()
    c = QColor.fromHslF(hsl.hslHueF() if hsl.hslHueF() >= 0 else 0.0, hsl.hslSaturationF(), max(0.0, min(1.0, hsl.lightnessF() * max(0.3, f))))
    if licht == "warm":
        c = QColor(min(255, c.red() + 25), c.green(), max(0, c.blue() - 20))
    elif licht == "kalt":
        c = QColor(max(0, c.red() - 20), c.green(), min(255, c.blue() + 25))
    return c


def extrusion_zeichnen(p: QPainter, bild: QImage, r: QRectF, ellipse: bool, d3: dict, dreh: dict | None = None) -> None:
    """3D-Format: die Form des Bildes (Alpha) als Tiefe nach hinten gestapelt (``tiefe`` pt, Farbe, Material, Beleuchtung), dazu eine Kontur
    (``kontur`` pt) am vorderen und hinteren Ende. Das Bild selbst wird danach vorn darübergemalt."""
    from PySide6.QtCore import QPointF
    w, h = max(1, int(r.width())), max(1, int(r.height()))
    tiefe = max(0.0, float(d3.get("tiefe", 0))) * px_pt()
    unten = d3.get("unten") if (d3.get("unten") or {}).get("art", "keine") != "keine" else None
    if unten and tiefe > 0:
        tiefe += max(0.0, float(unten.get("hoehe", 0.0))) * px_pt() * 0.5          # unterer Abschluss: die Rückseite wird um seine Höhe tiefer
    kontur = max(0.0, float(d3.get("kontur", 0))) * px_pt()
    dx, dy = tiefe_richtung(dreh)
    basis = QColor(d3.get("tiefe_farbe", Farbe.GRAU))
    mat, licht = d3.get("material", "matt"), d3.get("beleuchtung", "neutral")
    stufen = 8
    m = _merken(("d3maske", id(bild), w, h, ellipse), lambda: _maske(bild, (w, h), ellipse))

    def getoent(c: QColor) -> QImage:
        return _merken(("d3ton", id(bild), w, h, ellipse, c.name()), lambda: _getoent(m, c))
    p.save(); p.setRenderHint(QPainter.SmoothPixmapTransform)

    def ring(ox: float, oy: float) -> None:
        if kontur <= 0:
            return
        img = getoent(QColor(d3.get("kontur_farbe", Farbe.TINTE)))
        for k in range(8):
            a = k * math.pi / 4
            p.drawImage(QPointF(r.left() + ox + math.cos(a) * kontur, r.top() + oy + math.sin(a) * kontur), img)
    if unten and tiefe > 0:                                      # unterer Abschluss: ein dunkler Rand um das hintere Ende
        img = getoent(_stufenfarbe(basis, mat, licht, 1.0).darker(150)); rad = max(1.0, float(unten.get("breite", 4.0)) * px_pt())
        for k in range(8):
            a = k * math.pi / 4
            p.drawImage(QPointF(r.left() + dx * tiefe + math.cos(a) * rad, r.top() + dy * tiefe + math.sin(a) * rad), img)
    ring(dx * tiefe, dy * tiefe); ring(0, 0)
    n = int(min(120, max(1, tiefe))) if tiefe > 0 else 0
    for k in range(n, 0, -1):
        t = k / n
        band = min(stufen - 1, int(t * stufen))
        c = _stufenfarbe(basis, mat, licht, (band + 0.5) / stufen)
        p.drawImage(QPointF(r.left() + dx * tiefe * t, r.top() + dy * tiefe * t), getoent(c))
    p.restore()


def bild_nachbearbeiten(bild: QImage, r: QRectF, ellipse: bool, fx: dict) -> QImage:
    """Das Bild für das Zeichnen vorbereiten: oberer Abschluss des 3D-Formats eingearbeitet, dann im Raum gedreht (3D-Drehung). Die Form ist danach
    schon ausgeschnitten (``ellipse`` gilt nicht mehr)."""
    if hat_abschluss(fx):
        bild = abschluss_oben(bild, r, ellipse, fx["d3"]["oben"]); ellipse = False
    if _dreht(fx.get("drehung")):
        bild = drehung_3d(bild, r, ellipse, fx["drehung"])
    return bild


def _projektion(w: int, h: int, dreh: dict):
    """(Zielviereck, Faktor) der gedrehten Bildfläche: Drehung um X, Y, Z und Perspektive (Sichtwinkel ``persp``, 0 = parallel), eingepasst in ``w`` × ``h``."""
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QPolygonF
    x, y, z, pers = (float(dreh.get(k, 0.0)) for k in ("x", "y", "z", "persp"))
    a, b, c = math.radians(x), math.radians(y), math.radians(z)
    punkte = []
    for px, py in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        X, Y, Z = px, py, 0.0
        Y, Z = Y * math.cos(a) - Z * math.sin(a), Y * math.sin(a) + Z * math.cos(a)          # um X
        X, Z = X * math.cos(b) + Z * math.sin(b), -X * math.sin(b) + Z * math.cos(b)          # um Y
        X, Y = X * math.cos(c) - Y * math.sin(c), X * math.sin(c) + Y * math.cos(c)          # um Z
        punkte.append((X, Y, Z))
    if pers > 1:
        d = max(w, h) / (2 * math.tan(math.radians(min(pers, 150.0)) / 2))
        punkte = [(X * d / max(d * 0.1, d - Z), Y * d / max(d * 0.1, d - Z), Z) for X, Y, Z in punkte]
    xs, ys = [q[0] for q in punkte], [q[1] for q in punkte]
    f = min(1.0, w / max(1.0, max(xs) - min(xs)), h / max(1.0, max(ys) - min(ys)))
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return QPolygonF([QPointF(w / 2 + (q[0] - mx) * f, h / 2 + (q[1] - my) * f) for q in punkte]), (max(xs) - min(xs)) * f, (max(ys) - min(ys)) * f


def drehung_3d(bild: QImage, r: QRectF, ellipse: bool, dreh: dict) -> QImage:
    """Das Bild (Größe ``r``) im Raum gedreht (``x``, ``y``, ``z`` Grad, ``persp``); dieselbe Größe, die Fläche passt vollständig hinein.
    ``text_gerade``: der Inhalt (der Text im Objekt) bleibt aufrecht und wird nur so verkleinert, dass er in die gedrehte Fläche passt."""
    from PySide6.QtGui import QTransform
    w, h = max(1, int(r.width())), max(1, int(r.height()))
    gerade = bool(dreh.get("text_gerade"))

    def bauen():
        ziel, bw, bh = _projektion(w, h, dreh)
        out = QImage(w, h, QImage.Format_ARGB32_Premultiplied); out.fill(Qt.transparent)
        q = QPainter(out); q.setRenderHint(QPainter.Antialiasing); q.setRenderHint(QPainter.SmoothPixmapTransform)
        m = _maske(bild, (w, h), ellipse)
        if gerade:
            f = min(1.0, bw / w, bh / h) * 0.9
            q.drawImage(QRectF(w / 2 - w * f / 2, h / 2 - h * f / 2, w * f, h * f), m)
        else:
            from PySide6.QtCore import QPointF
            from PySide6.QtGui import QPolygonF
            t = QTransform()
            if QTransform.quadToQuad(QPolygonF([QPointF(0, 0), QPointF(w, 0), QPointF(w, h), QPointF(0, h)]), ziel, t):
                q.setTransform(t); q.drawImage(0, 0, m)
        q.end()
        return out
    return _merken(("dreh3d", id(bild), w, h, ellipse, gerade, *(round(float(dreh.get(k, 0.0)), 1) for k in ("x", "y", "z", "persp"))), bauen)


# ---- Oberer Abschluss (Fase) des 3D-Formats ------------------------------------------------------------------------------------
def _erodiert(m: QImage, rad: float) -> QImage:
    """Die Form um ``rad`` px nach innen verkleinert (Schnitt der in acht Richtungen verschobenen Form)."""
    from PySide6.QtCore import QPointF
    out = QImage(m)
    for k in range(8):
        a = k * math.pi / 4
        s = QImage(m.size(), QImage.Format_ARGB32_Premultiplied); s.fill(Qt.transparent)
        q = QPainter(s); q.drawImage(QPointF(math.cos(a) * rad, math.sin(a) * rad), m); q.end()
        q = QPainter(out); q.setCompositionMode(QPainter.CompositionMode_DestinationIn); q.drawImage(0, 0, s); q.end()
    return out


def _band(aussen: QImage, innen: QImage) -> QImage:
    b = QImage(aussen)
    q = QPainter(b); q.setCompositionMode(QPainter.CompositionMode_DestinationOut); q.drawImage(0, 0, innen); q.end()
    return b


def _licht(band: QImage, art: str, st: float, umgekehrt: bool = False) -> QImage:
    """Das Band mit Licht von links oben: hell oben links, dunkel unten rechts (``st`` = Stärke 0…1)."""
    w, h = band.width(), band.height()
    ov = QImage(w, h, QImage.Format_ARGB32_Premultiplied); ov.fill(Qt.transparent)
    hell, dunkel = QColor(*WEISS_RGB, int(ALPHA_VOLL * st)), QColor(*SCHWARZ_RGB, int(ALPHA_VOLL * st))
    if umgekehrt:
        hell, dunkel = dunkel, hell
    g = QLinearGradient(0, 0, w, h)
    if art == "rahmen":
        g.setColorAt(0, QColor(*SCHWARZ_RGB, int(ALPHA_VOLL * st * STAERKE_BILDEFFEKT_DUNKEL))); g.setColorAt(1, QColor(*SCHWARZ_RGB, int(ALPHA_VOLL * st * STAERKE_BILDEFFEKT_DUNKEL)))
    elif art in ("winkel", "kreuz"):
        g.setColorAt(0, hell); g.setColorAt(0.499, hell); g.setColorAt(0.501, dunkel); g.setColorAt(1, dunkel)
    elif art == "weich":
        g.setColorAt(0, QColor(*WEISS_RGB, int(ALPHA_VOLL * st * STAERKE_BILDEFFEKT_HELL))); g.setColorAt(0.6, QColor(*WEISS_RGB, 0)); g.setColorAt(1, QColor(*SCHWARZ_RGB, int(ALPHA_VOLL * st * STAERKE_BILDEFFEKT_RAND)))
    else:                                                        # rund: weicher Übergang von hell nach dunkel
        g.setColorAt(0, hell); g.setColorAt(0.5, QColor(*GRAU_RGB, 0)); g.setColorAt(1, dunkel)
    q = QPainter(ov); q.fillRect(ov.rect(), g); q.setCompositionMode(QPainter.CompositionMode_DestinationIn); q.drawImage(0, 0, band); q.end()
    return ov


def abschluss_oben(bild: QImage, r: QRectF, ellipse: bool, ab: dict) -> QImage:
    """Oberer Abschluss: ein Rand der Breite ``breite`` pt rundum, von links oben beleuchtet; ``hoehe`` pt bestimmt die Stärke von Licht und Schatten.
    Arten (``ABSCHLUSS``): rund, winkel, weich, kreuz (äußere Hälfte so, innere umgekehrt), rahmen (gleichmäßig dunkel). Ergebnis: Bild in der Form."""
    art = ab.get("art", "keine")
    w, h = max(1, int(r.width())), max(1, int(r.height()))
    rad = max(1.0, min(float(ab.get("breite", 4.0)) * px_pt(), min(w, h) / 2 - 1))
    st = max(0.1, min(0.9, 0.15 + float(ab.get("hoehe", 6.0)) / 20.0 * 0.55))

    def bauen():
        m = _maske(bild, (w, h), ellipse)
        if art == "keine":
            return m
        voll = _erodiert(m, rad)
        if art == "kreuz":
            halb = _erodiert(m, rad / 2)
            ov = _licht(_band(m, halb), art, st); ov2 = _licht(_band(halb, voll), art, st, True)
        else:
            band = _band(m, voll)
            ov = _licht(_weich(band, rad * 0.5) if art in ("rund", "weich") else band, art, st)
            ov2 = None
        out = QImage(m); q = QPainter(out); q.setCompositionMode(QPainter.CompositionMode_SourceAtop); q.drawImage(0, 0, ov)
        if ov2 is not None:
            q.drawImage(0, 0, ov2)
        q.end()
        return out
    return _merken(("abschluss", id(bild), w, h, ellipse, art, round(rad, 1), round(st, 2)), bauen)


def abschluss_symbol(art: str, groesse: int = 40):
    """Bildchen für die Auswahl der Abschlussart: eine graue Fläche mit dem Abschluss."""
    from PySide6.QtGui import QPixmap
    n = groesse
    b = QImage(n, n, QImage.Format_ARGB32_Premultiplied); b.fill(QColor(Farbe.BILDEFFEKT_GRUND))
    g = abschluss_oben(b, QRectF(0, 0, n, n), False, {"art": art, "breite": 5.0, "hoehe": 12.0}) if art != "keine" else b
    pm = QPixmap(n + 8, n + 8); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    pf = QPainterPath(); pf.addRoundedRect(QRectF(4, 4, n, n), 6, 6); p.setClipPath(pf); p.drawImage(4, 4, g); p.end()
    return pm
