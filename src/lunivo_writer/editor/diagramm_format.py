"""Formate der Diagrammteile (``daten["teil_format"][teil]``): Füllung, Linie, Effekte, Text und Optionen von Achse und Reihe. Keine Oberfläche.

Gezeichnet wird mit den Bausteinen, die es für freie Bilder und Formen schon gibt: Pinsel und Stift aus ``freie_bilder`` (``fuell_pinsel``, ``_stift``),
Schatten, Leuchten, Spiegelung, weiche Kanten und 3D aus ``bildeffekte`` (über ``freie_bilder.bild_zeichnen``), Texteffekte und Konturformen aus ``textfx``.

Schlüssel eines Teils (jeder darf fehlen = Automatisch):

``fuell``      ``""`` keine Füllung · ``"#rrggbb"`` einfarbig · ``{"art": "farbe"|"graduell"|"textur"|"muster"|"bild", "farbe", "dunkel", "hell", "winkel", "key",
               "grund", "bild_b64", "transparenz": 0…100}``
``linie``      ``{"keine": True}`` oder ``{"farbe", "breite" (pt), "art", "transparenz", "kombiniert" (einfach|doppelt|dick_duenn), "abschluss" (flach|rund|quadrat),
               "verknuepfung" (rund|schraeg|spitz), "rund": bool, "verlauf": {"farbe1", "farbe2", "winkel"}, "pfeil_anfang", "pfeil_ende", "pfeil_groesse"}``
``schatten``, ``reflektion``, ``leuchten``, ``weich``, ``d3``, ``drehung``   wie ``fx`` bei ``bildeffekte`` (``True`` = Vorgabe; ältere Angaben ``{"farbe",
               "abstand"}`` / ``{"farbe", "radius"}`` werden gelesen)
``text``       ``{"farbe", "groesse", "fett", "kursiv", "unter", "name", "effekt": {Werte der Texteffekte}, "feld": {"vertikal", "richtung", "winkel", "raender",
               "anpassen", "umbruch"}}``
``achse``      ``{"min", "max", "intervall", "umkehren", "beschriftung": "neben"|"keine"}`` (Wertachse: alles, Rubrikenachse: umkehren, beschriftung)
``reihe``      ``{"luecke": %, "glatt": bool, "punkte": bool}``
"""
from __future__ import annotations

import base64
import math

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF)

from lunivo_writer.editor import bildeffekte as E
from lunivo_writer.editor import freie_bilder as FB
from lunivo_writer.editor import textfx as X

FX_SCHLUESSEL = ("schatten", "reflektion", "leuchten", "weich", "d3", "drehung")
FX_NUR_HINTER = ("schatten", "reflektion", "leuchten", "d3")           # hinter einem Balken, den QtCharts selbst darüber zeichnet
PX_PT = 96.0 / 72.0
PFEILE = (("keiner", "Kein Pfeil"), ("pfeil", "Pfeil"), ("offen", "Offener Pfeil"), ("oval", "Oval"), ("raute", "Raute"))
FELD_STANDARD = {"vertikal": "mitte", "richtung": "waagerecht", "winkel": 0.0, "anpassen": True, "umbruch": True,
                 "raender": {"l": 0.0, "o": 0.0, "r": 0.0, "u": 0.0}}


# ---- Füllung ---------------------------------------------------------------------------------------------------------------------
def fuell_dict(f) -> dict | None:
    """Die Füllung als Wörterbuch; None bei Automatisch (nicht gesetzt) und bei „Keine Füllung“ (``""``)."""
    if not f:
        return None
    return {"art": "farbe", "farbe": f} if isinstance(f, str) else f


def ist_keine(f) -> bool:
    return f == "" or (isinstance(f, dict) and f.get("art") == "keine")


def hauptfarbe(f) -> str | None:
    """Die Farbe, mit der eine Reihe (Legende, Linien, Kreisstücke) gezeichnet wird, wenn der Pinsel selbst nicht möglich ist."""
    d = fuell_dict(f)
    if d is None:
        return None
    if d.get("art", "farbe") in ("graduell", "verlauf"):
        return d.get("dunkel") or d.get("farbe")
    return d.get("farbe") or d.get("dunkel")


def bild_kodieren(img: QImage, laengste_seite: int = 256) -> str:
    """Ein Füllbild für die Daten des Diagramms: höchstens ``laengste_seite`` Bildpunkte, PNG, als Text (steckt im „lunivo:“-Titel der DOCX-Datei)."""
    if img.isNull():
        return ""
    if max(img.width(), img.height()) > laengste_seite:
        img = img.scaled(laengste_seite, laengste_seite, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    ba = QByteArray(); buf = QBuffer(ba); buf.open(QIODevice.WriteOnly); img.save(buf, "PNG"); buf.close()
    return base64.b64encode(bytes(ba)).decode("ascii")


_BILDER: dict = {}


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
        return QBrush(QColor(d.get("farbe", "#4a8fd8"))), opaz
    if art in ("graduell", "verlauf"):
        w = math.radians(float(d.get("winkel", 90)))
        dx, dy = math.cos(w) / 2, math.sin(w) / 2
        g = QLinearGradient(QPointF(0.5 - dx, 0.5 - dy), QPointF(0.5 + dx, 0.5 + dy))
        g.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        g.setColorAt(0, QColor(d.get("hell", "#ffffff"))); g.setColorAt(1, QColor(d.get("dunkel", d.get("farbe", "#1864ab"))))
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


# ---- Linie -----------------------------------------------------------------------------------------------------------------------
_ABSCHLUSS = {"flach": Qt.FlatCap, "rund": Qt.RoundCap, "quadrat": Qt.SquareCap}
_VERKNUEPFUNG = {"rund": Qt.RoundJoin, "schraeg": Qt.BevelJoin, "spitz": Qt.MiterJoin}


def linie_keine(linie) -> bool:
    return isinstance(linie, dict) and bool(linie.get("keine"))


def stift(linie: dict | None, standard_farbe: str = "#3c4043", r: QRectF | None = None) -> QPen:
    """Der Stift einer ``linie`` (Breite in pt): Strichart über ``freie_bilder._stift``, dazu Transparenz, Abschluss, Verknüpfung und Farbverlauf."""
    linie = linie or {}
    pen = FB._stift({"b": float(linie.get("breite", 1.0)) * PX_PT, "farbe": linie.get("farbe", standard_farbe), "art": linie.get("art", "einfach")})
    c = QColor(linie.get("farbe", standard_farbe))
    c.setAlphaF(max(0.0, min(1.0, 1.0 - float(linie.get("transparenz", 0) or 0) / 100.0)))
    pen.setColor(c)
    pen.setCapStyle(_ABSCHLUSS.get(linie.get("abschluss", "flach"), Qt.FlatCap))
    pen.setJoinStyle(_VERKNUEPFUNG.get(linie.get("verknuepfung", "rund"), Qt.RoundJoin))
    v = linie.get("verlauf")
    if v:
        pen.setBrush(_verlauf_pinsel(v, r or QRectF(0, 0, 100, 100), c.alphaF()))
    return pen


def _verlauf_pinsel(v: dict, r: QRectF, alpha: float = 1.0) -> QBrush:
    w = math.radians(float(v.get("winkel", 0)))
    m = r.center(); dx, dy = math.cos(w) * r.width() / 2, math.sin(w) * r.height() / 2
    g = QLinearGradient(QPointF(m.x() - dx, m.y() - dy), QPointF(m.x() + dx, m.y() + dy))
    a, b = QColor(v.get("farbe1", "#c0392b")), QColor(v.get("farbe2", "#1864ab"))
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
    fmt = fmt or {}
    fx = {}
    for k in FX_SCHLUESSEL:
        v = fmt.get(k)
        if not v:
            continue
        v = {} if v is True else dict(v)
        if k == "schatten" and "winkel" not in v:                                   # ältere Angabe {"farbe", "abstand"}
            v = {**E.VORGABE["schatten"], **({"farbe": v["farbe"]} if "farbe" in v else {}), **({"abstand": v["abstand"]} if "abstand" in v else {})}
        elif k == "leuchten" and "radius" in v:                                     # ältere Angabe {"farbe", "radius"}
            v = {**E.VORGABE["leuchten"], "farbe": v.get("farbe", "#ffc000"), "groesse": v["radius"]}
        basis = {a: b for a, b in E.VORGABE[k].items() if a not in ("oben", "unten")}          # ein Abschluss gilt nur, wenn er gewählt wurde
        fx[k] = {**basis, **v}
    return fx


def teil_zeichnen(p: QPainter, r: QRectF, fmt: dict | None, grund: QColor, nur_hinter: bool = False) -> None:
    """Füllung und Effekte eines Teils unter dem Diagramm. Ohne Füllung brauchen die Effekte eine Fläche: dann dient ``grund`` (Hintergrund des Stils)."""
    fmt = fmt or {}
    fx = fx_normal(fmt)
    if nur_hinter:
        fx = {k: v for k, v in fx.items() if k in FX_NUR_HINTER}
    fuell = fmt.get("fuell")
    if not fx:
        flaeche_zeichnen(p, r, fuell)
        return
    if not fuell_dict(fuell):
        fuell = {"art": "farbe", "farbe": grund.name()}
    img = flaeche_bild(fuell, max(1, round(r.width())), max(1, round(r.height())))
    FB.bild_zeichnen(p, img, r, False, None, 0.0, None, None, fx)


# ---- Text ------------------------------------------------------------------------------------------------------------------------
def feld_von(t: dict | None) -> dict:
    f = (t or {}).get("feld") or {}
    return {**FELD_STANDARD, **f, "raender": {**FELD_STANDARD["raender"], **(f.get("raender") or {})}}


def textwinkel(t: dict | None) -> float:
    """Der Winkel des Textes in Grad (im Uhrzeigersinn): Textrichtung und benutzerdefinierter Winkel zusammen."""
    f = feld_von(t)
    basis = {"waagerecht": 0.0, "dreh90": 90.0, "dreh270": -90.0, "gestapelt": 0.0}.get(f["richtung"], 0.0)
    return max(-180.0, min(180.0, basis + float(f["winkel"] or 0.0)))


def effekt_von(t: dict | None) -> dict:
    return (t or {}).get("effekt") or {}


def text_eigen(t: dict | None) -> bool:
    """Muss der Text selbst gezeichnet werden (QtCharts kann Verläufe, Kontur, Schatten … nicht)? Gilt für Titel und Legende."""
    if not t:
        return False
    e = effekt_von(t)
    if e.get("fuell") in ("keine", "verlauf") or e.get("kontur") or any(e.get(k) for k in ("schatten", "reflektion", "leuchten", "d3")):
        return True
    f = feld_von(t)
    return bool(f["richtung"] != "waagerecht" or f["winkel"] or f["anpassen"] is False)


def textfarbe(t: dict | None, standard: str = "#3c4043") -> QColor:
    """Farbe des Textes mit Transparenz; „Keine Füllung“ ist ganz durchsichtig."""
    t = t or {}
    e = effekt_von(t)
    if e.get("fuell") == "keine":
        return QColor(0, 0, 0, 0)
    c = QColor(e.get("farbe") or t.get("farbe") or standard)
    if e.get("fuell") == "verlauf" and e.get("verlauf"):
        c = QColor(e["verlauf"].get("farbe1", c.name()))
    c.setAlphaF(max(0.0, min(1.0, 1.0 - float(e.get("transparenz", 0) or 0) / 100.0)))
    return c


def schrift_aus(basis: QFont, t: dict | None) -> QFont:
    f = QFont(basis)
    if t:
        if t.get("name"):
            f.setFamily(t["name"])
        if t.get("groesse"):
            f.setPointSizeF(float(t["groesse"]))
        if "fett" in t:
            f.setBold(bool(t["fett"]))
        if "kursiv" in t:
            f.setItalic(bool(t["kursiv"]))
        if "unter" in t:
            f.setUnderline(bool(t["unter"]))
    return f


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


def _umbrechen(text: str, fm: QFontMetricsF, breite: float) -> list[str]:
    zeilen: list[str] = []
    for absatz in text.split("\n"):
        akt = ""
        for w in absatz.split(" "):
            probe = (akt + " " + w).strip()
            if akt and fm.horizontalAdvance(probe) > breite:
                zeilen.append(akt); akt = w
            else:
                akt = probe
        zeilen.append(akt)
    return zeilen


def text_zeichnen(p: QPainter, feld: QRectF, text: str, font: QFont, t: dict | None, standard: str = "#3c4043", umbrechbar: bool = False) -> None:
    """Text mit Textfüllung, -kontur und Effekten (Schatten, Spiegelung, Leuchten, 3D) in ``feld``: waagerecht mittig, senkrecht nach ``vertikal``,
    gedreht um die Mitte des Feldes um ``textwinkel``."""
    t = t or {}
    f = feld_von(t)
    e = effekt_von(t)
    if f["richtung"] == "gestapelt":
        text = "\n".join(text.replace("\n", ""))
    fm = QFontMetricsF(font)
    zeilen = _umbrechen(text, fm, feld.width()) if umbrechbar and f["umbruch"] else text.split("\n")
    gesamt = len(zeilen) * fm.lineSpacing()
    y0 = {"oben": feld.top(), "unten": feld.bottom() - gesamt}.get(f["vertikal"], feld.center().y() - gesamt / 2)
    face = textfarbe(t, standard)
    fx = {k: v for k, v in e.items() if k in ("verlauf", "kontur_verlauf", "kontur_form", "schatten", "reflektion", "leuchten", "d3")}
    kontur = None
    if e.get("kontur"):
        kontur = (QColor(e.get("kontur_farbe", "#000000")), float(e.get("kontur_breite", 0.75)) * X.PX, e.get("kontur_form", "einfach"), e.get("kontur_art", "einfach"))
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    w = textwinkel(t)
    if w:
        p.translate(feld.center()); p.rotate(w); p.translate(-feld.center())
    px = font.pixelSize() if font.pixelSize() > 0 else font.pointSizeF() * X.PX
    for i, z in enumerate(zeilen):
        x = feld.center().x() - fm.horizontalAdvance(z) / 2
        y = y0 + i * fm.lineSpacing() + fm.ascent()
        pfad, gl = X.text_pfad(z, font, QPointF(x, y))
        if face.alpha() > 0:
            p.fillPath(pfad, face)
        if fx or kontur is not None:
            X.fx_zeichnen(p, pfad, fx, gl, px, face if face.alpha() else QColor(standard), kontur)
    p.restore()


# ---- Achse und Reihe --------------------------------------------------------------------------------------------------------------
def achse_anwenden(achse, opt: dict | None, wert: bool) -> None:
    """Die Optionen einer Achse (``achse`` im Teilformat) auf die QtCharts-Achse. ``wert``: Wertachse (Minimum, Maximum, Hauptintervall)."""
    if not opt:
        return
    if wert and hasattr(achse, "setRange"):
        lo, hi = opt.get("min"), opt.get("max")
        if lo is not None or hi is not None:
            a = float(lo) if lo is not None else achse.min()
            b = float(hi) if hi is not None else achse.max()
            if b > a:
                achse.setRange(a, b)
        if opt.get("intervall") and hasattr(achse, "setTickInterval") and float(opt["intervall"]) > 0:
            achse.setTickType(achse.TickType.TicksDynamic)
            achse.setTickAnchor(achse.min()); achse.setTickInterval(float(opt["intervall"]))
    if opt.get("umkehren") and hasattr(achse, "setReverse"):
        achse.setReverse(True)
    if opt.get("beschriftung") == "keine":
        achse.setLabelsVisible(False)


def luecke_zu_breite(prozent: float) -> float:
    """Lückenbreite in Prozent der Säulenbreite → ``barWidth`` der Serie (Anteil der Kategorie, den die Säulen füllen)."""
    return 1.0 / (1.0 + max(0.0, min(500.0, float(prozent))) / 100.0)


def pfeil_zeichnen(p: QPainter, spitze: QPointF, von: QPointF, art: str, breite_pt: float, groesse: float, farbe: QColor) -> None:
    """Ein Linienende an ``spitze``; ``von`` ist der benachbarte Punkt der Linie (gibt die Richtung)."""
    if art in ("", "keiner", None):
        return
    dx, dy = spitze.x() - von.x(), spitze.y() - von.y()
    n = math.hypot(dx, dy) or 1.0
    dx, dy = dx / n, dy / n
    s = max(5.0, breite_pt * PX_PT * (2.0 + 1.2 * groesse))
    px, py = -dy, dx
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    if art in ("pfeil", "offen"):
        a = QPointF(spitze.x() - dx * s + px * s / 2, spitze.y() - dy * s + py * s / 2)
        b = QPointF(spitze.x() - dx * s - px * s / 2, spitze.y() - dy * s - py * s / 2)
        if art == "pfeil":
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawPolygon(QPolygonF([spitze, a, b]))
        else:
            pen = QPen(farbe, max(1.2, breite_pt * PX_PT)); pen.setCapStyle(Qt.RoundCap); p.setPen(pen)
            p.drawLine(spitze, a); p.drawLine(spitze, b)
    elif art == "oval":
        p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(spitze, s / 2, s / 2)
    elif art == "raute":
        m = spitze
        p.setPen(Qt.NoPen); p.setBrush(farbe)
        p.drawPolygon(QPolygonF([QPointF(m.x() + dx * s / 2, m.y() + dy * s / 2), QPointF(m.x() + px * s / 2, m.y() + py * s / 2),
                                 QPointF(m.x() - dx * s / 2, m.y() - dy * s / 2), QPointF(m.x() - px * s / 2, m.y() - py * s / 2)]))
    p.restore()
