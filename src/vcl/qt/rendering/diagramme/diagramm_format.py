from __future__ import annotations
import base64
import math
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF)
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import STIFT_BILDCHEN
from vcl.qt.widgets.bausteine.farben.farben import DURCHSICHTIG
from vcl.qt.rendering import formen as E
from vcl.qt.rendering.formen import freie_bilder as FB
from vcl.qt.rendering.wordart import textfx as X
from vcl.qt.rendering import wordart as T
from core.diagramme.formatierung.diagramm_format_daten import _BILDER, fuell_dict, linie_keine
from writer.anbindung.diagramm_format_daten import fx_nur_hinter
from writer.anbindung.diagramm_format_daten import fx_schluessel
from writer.anbindung.diagramm_format_daten import px_pt
from writer.anbindung.diagramm_format_daten import effekt_von
from writer.anbindung.diagramm_format_daten import feld_von


def bild_kodieren(img: QImage, laengste_seite: int = 256) -> str:
    """Ein Füllbild für die Daten des Diagramms: höchstens ``laengste_seite`` Bildpunkte, PNG, als Text (steckt im „lunivo:“-Titel der DOCX-Datei)."""
    if img.isNull():
        return ""
    if max(img.width(), img.height()) > laengste_seite:
        img = img.scaled(laengste_seite, laengste_seite, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    ba = QByteArray(); buf = QBuffer(ba); buf.open(QIODevice.WriteOnly); img.save(buf, "PNG"); buf.close()
    return base64.b64encode(bytes(ba)).decode("ascii")


def bild_dekodieren(text: str) -> QImage:
    if text not in _BILDER:
        img = QImage()
        try:
            img.loadFromData(base64.b64decode(text), "PNG")
        except (ValueError, TypeError):
            pass
        if len(_BILDER) > 16:
            _BILDER.clear()
        _BILDER[text] = img
    return _BILDER[text]


def pinsel(fuell, r: QRectF | None = None) -> tuple[QBrush | None, float]:
    """(Pinsel, Deckkraft 0…1) der Füllung; ``r`` ist das Rechteck, das gefüllt wird (ohne: der Pinsel gilt für das jeweils gezeichnete Objekt,
    Verläufe bleiben relativ). ``(None, 1)`` ohne Füllung."""
    d = fuell_dict(fuell)
    if d is None or d.get("art") == "keine":
        return None, 1.0
    opaz = max(0.0, min(1.0, 1.0 - float(d.get("transparenz", 0) or 0) / 100.0))
    art = d.get("art", "farbe")
    if art == "farbe":
        return QBrush(QColor(d.get("farbe", Farbe.AKZENT_DUNKEL))), opaz
    if art in ("graduell", "verlauf"):
        w = math.radians(float(d.get("winkel", 90)))
        dx, dy = math.cos(w) / 2, math.sin(w) / 2
        g = QLinearGradient(QPointF(0.5 - dx, 0.5 - dy), QPointF(0.5 + dx, 0.5 + dy))
        g.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        g.setColorAt(0, QColor(d.get("hell", Farbe.WEISS))); g.setColorAt(1, QColor(d.get("dunkel", d.get("farbe", Farbe.DIAGRAMM_BLAU_DUNKEL))))
        return QBrush(g), opaz
    if art == "bild":
        img = bild_dekodieren(d.get("bild_b64", ""))
        if img.isNull():
            return None, opaz
        if r is not None:
            img = img.scaled(max(1, int(r.width())), max(1, int(r.height())), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        return QBrush(img), opaz
    return FB.fuell_pinsel(d, r or QRectF(0, 0, 64, 64)), opaz                  # Textur und Muster


def flaeche_zeichnen(p: QPainter, r: QRectF, fuell) -> None:
    pi, opaz = pinsel(fuell, r)
    if pi is None:
        return
    p.save(); p.setOpacity(p.opacity() * opaz)
    p.fillRect(r, pi)
    p.restore()


def flaeche_bild(fuell, w: int, h: int, aufl: float = 2.0) -> QImage:
    """Die Füllung als Bild (für die Effekte, die mit einem Bild arbeiten)."""
    img = QImage(max(1, int(w * aufl)), max(1, int(h * aufl)), QImage.Format_ARGB32_Premultiplied); img.fill(Qt.transparent)
    q = QPainter(img); q.scale(aufl, aufl); flaeche_zeichnen(q, QRectF(0, 0, w, h), fuell); q.end()
    return img




def _strichmuster(art: str):
    """(Strichmuster in Linienbreiten, runde Enden) der neuen Strichtypen; None für die, die ``freie_bilder._stift`` kennt."""
    if art in T.KONTUR_ARTEN_PLUS:
        return T.KONTUR_ARTEN_PLUS[art]
    return {"lang": ([8.0, 3.0], False), "lang_strichpunkt": ([8.0, 3.0, 1.0, 3.0], False)}.get(art)


_ABSCHLUSS = {"flach": Qt.FlatCap, "rund": Qt.RoundCap, "quadrat": Qt.SquareCap}


_VERKNUEPFUNG = {"rund": Qt.RoundJoin, "schraeg": Qt.BevelJoin, "spitz": Qt.MiterJoin}


def stift(linie: dict | None, standard_farbe: str = Farbe.DIAGRAMM_LINIE, r: QRectF | None = None) -> QPen:
    """Der Stift einer ``linie`` (Breite in pt): Strichart über ``freie_bilder._stift``, dazu Transparenz, Abschluss, Verknüpfung und Farbverlauf."""
    linie = linie or {}
    pen = FB._stift({"b": float(linie.get("breite", 1.0)) * px_pt(), "farbe": linie.get("farbe", standard_farbe), "art": linie.get("art", "einfach")})
    c = QColor(linie.get("farbe", standard_farbe))
    c.setAlphaF(max(0.0, min(1.0, 1.0 - float(linie.get("transparenz", 0) or 0) / 100.0)))
    pen.setColor(c)
    m = _strichmuster(linie.get("art", "einfach"))
    if m:
        pen.setDashPattern(m[0])
    pen.setCapStyle(Qt.RoundCap if m and m[1] and "abschluss" not in linie else _ABSCHLUSS.get(linie.get("abschluss", "flach"), Qt.FlatCap))
    pen.setJoinStyle(_VERKNUEPFUNG.get(linie.get("verknuepfung", "rund"), Qt.RoundJoin))
    v = linie.get("verlauf")
    if v:
        pen.setBrush(_verlauf_pinsel(v, r or QRectF(0, 0, 100, 100), c.alphaF()))
    return pen


def _verlauf_pinsel(v: dict, r: QRectF, alpha: float = 1.0) -> QBrush:
    w = math.radians(float(v.get("winkel", 0)))
    m = r.center(); dx, dy = math.cos(w) * r.width() / 2, math.sin(w) * r.height() / 2
    g = QLinearGradient(QPointF(m.x() - dx, m.y() - dy), QPointF(m.x() + dx, m.y() + dy))
    a, b = QColor(v.get("farbe1", Farbe.DIAGRAMM_ROT)), QColor(v.get("farbe2", Farbe.DIAGRAMM_BLAU_DUNKEL))
    a.setAlphaF(alpha); b.setAlphaF(alpha)
    g.setColorAt(0, a); g.setColorAt(1, b)
    return QBrush(g)


def rahmen_zeichnen(p: QPainter, r: QRectF, linie: dict | None) -> None:
    """Die Linie um ein Rechteck; ``kombiniert`` (Doppelt, Dick–dünn) zeichnet die Konturformen von ``textfx``, ``rund`` rundet die Ecken."""
    if not linie or linie_keine(linie):
        return
    pen = stift(linie, r=r)
    k = pen.widthF() / 2
    innen = r.adjusted(k, k, -k, -k)
    pfad = QPainterPath()
    if linie.get("rund"):
        rad = min(innen.width(), innen.height()) / 2
        pfad.addRoundedRect(innen, min(rad, 6 + pen.widthF()), min(rad, 6 + pen.widthF()))
    else:
        pfad.addRect(innen)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    form = linie.get("kombiniert", "einfach")
    if form != "einfach":
        brush = pen.brush()
        for flaeche in X._kontur_pfade(pfad, pen.widthF(), form, "einfach"):
            p.fillPath(flaeche, brush)
    else:
        p.setPen(pen); p.setBrush(Qt.NoBrush); p.drawPath(pfad)
    p.restore()


# ---- Effekte ---------------------------------------------------------------------------------------------------------------------
def fx_normal(fmt: dict | None) -> dict:
    """Die Effekte eines Teils im Format von ``bildeffekte`` (``True`` und ältere Angaben ergänzt)."""
    from vcl.qt.rendering.wordart import zu_dict
    from writer.funktionen.objekte import bildeffekte as BEW
    fmt = fmt or {}
    fx = {}
    vorgabe = zu_dict(BEW.vorgabe())
    for k in fx_schluessel():
        v = fmt.get(k)
        if not v:
            continue
        v = {} if v is True else dict(v)
        if k == "schatten" and "winkel" not in v:                                   # ältere Angabe {"farbe", "abstand"}
            v = {**vorgabe["schatten"],**({"farbe": v["farbe"]} if "farbe" in v else {}), **({"abstand": v["abstand"]} if "abstand" in v else {})}
        elif k == "leuchten" and "radius" in v:                                     # ältere Angabe {"farbe", "radius"}
            v = {**vorgabe["leuchten"],"farbe": v.get("farbe", Farbe.LEUCHTEN_GELB), "groesse": v["radius"]}
        basis = {a: b for a, b in vorgabe[k].items() if a not in ("oben", "unten")}          # ein Abschluss gilt nur, wenn er gewählt wurde
        fx[k] = {**basis, **v}
    return fx


def teil_zeichnen(p: QPainter, r: QRectF, fmt: dict | None, grund: QColor, nur_hinter: bool = False) -> None:
    """Füllung und Effekte eines Teils unter dem Diagramm. Ohne Füllung brauchen die Effekte eine Fläche: dann dient ``grund`` (Hintergrund des Stils)."""
    fmt = fmt or {}
    fx = fx_normal(fmt)
    if nur_hinter:
        fx = {k: v for k, v in fx.items() if k in fx_nur_hinter()}
    fuell = fmt.get("fuell")
    if not fx:
        flaeche_zeichnen(p, r, fuell)
        return
    if not fuell_dict(fuell):
        fuell = {"art": "farbe", "farbe": grund.name()}
    img = flaeche_bild(fuell, max(1, round(r.width())), max(1, round(r.height())))
    FB.bild_zeichnen(p, img, r, False, None, 0.0, None, None, fx)


def textfarbe(t: dict | None, standard: str = Farbe.DIAGRAMM_LINIE) -> QColor:
    """Farbe des Textes mit Transparenz; „Keine Füllung“ ist ganz durchsichtig."""
    t = t or {}
    e = effekt_von(t)
    if e.get("fuell") in ("keine", "muster", "bild"):                              # Muster und Bild zeichnet ``textfx`` über den Buchstaben
        return QColor(*DURCHSICHTIG)
    c = QColor(e.get("farbe") or t.get("farbe") or standard)
    if e.get("fuell") == "verlauf" and e.get("verlauf"):
        c = QColor(e["verlauf"].get("farbe1", c.name()))
    c.setAlphaF(max(0.0, min(1.0, 1.0 - float(e.get("transparenz", 0) or 0) / 100.0)))
    return c


def box_rect(teil: str, r: QRectF, t: dict | None, gesamt_breite: float) -> QRectF:
    """Das Feld des Teils um den Text: ohne „Größe der Form dem Text anpassen“ ist der Titel so breit wie das Diagramm; die Ränder liegen außen herum."""
    f = feld_von(t)
    rr = QRectF(r)
    if f["anpassen"] is False and teil == "titel":
        rr = QRectF(6, r.top(), max(r.width(), gesamt_breite - 12), r.height() * 1.8)
    m = f["raender"]
    return rr.adjusted(-float(m["l"]), -float(m["o"]), float(m["r"]), float(m["u"]))


def text_feld(box: QRectF, t: dict | None) -> QRectF:
    """Der Platz für den Text im Feld des Teils (``box_rect`` ohne die Ränder)."""
    m = feld_von(t)["raender"]
    return box.adjusted(float(m["l"]), float(m["o"]), -float(m["r"]), -float(m["u"]))


def pfeil_zeichnen(p: QPainter, spitze: QPointF, von: QPointF, art: str, breite_pt: float, groesse: float, farbe: QColor) -> None:
    """Ein Linienende an ``spitze``; ``von`` ist der benachbarte Punkt der Linie (gibt die Richtung)."""
    if art in ("", "keiner", None):
        return
    dx, dy = spitze.x() - von.x(), spitze.y() - von.y()
    n = math.hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    s = max(5.0, breite_pt * px_pt() * (2.0 + 1.2 * groesse))
    px, py = -dy, dx
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    if art in ("pfeil", "offen"):
        a = QPointF(spitze.x() - dx * s + px * s / 2, spitze.y() - dy * s + py * s / 2)
        b = QPointF(spitze.x() - dx * s - px * s / 2, spitze.y() - dy * s - py * s / 2)
        if art == "pfeil":
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawPolygon(QPolygonF([spitze, a, b]))
        else:
            pen = QPen(farbe, max(STIFT_BILDCHEN, breite_pt * px_pt())); pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
            p.drawLine(spitze, a); p.drawLine(spitze, b)
    elif art == "oval":
        p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(spitze, s / 2, s / 2)
    elif art == "raute":
        m = spitze
        p.setPen(Qt.NoPen); p.setBrush(farbe)
        p.drawPolygon(QPolygonF([QPointF(m.x() + dx * s / 2, m.y() + dy * s / 2), QPointF(m.x() + px * s / 2, m.y() + py * s / 2),
                                 QPointF(m.x() - dx * s / 2, m.y() - dy * s / 2), QPointF(m.x() - px * s / 2, m.y() - py * s / 2)]))
    p.restore()
