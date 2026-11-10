"""Was Lunivo am Text selbst zeichnet, das Qt nicht kann und das nicht zu den Effekten von ``textfx`` gehört: Unterstreichungsarten,
doppelt Durchgestrichenes, Betonungszeichen, umschlossene Zeichen, Ruby (Leittext) — und der Lauf über die Textstücke des Dokuments
(``absaetze_zeichnen``), der dazu auch die Effekte von ``textfx.fx_zeichnen`` aufruft.

``textfx`` führt die Namen von hier wieder auf (Aufrufer bleiben bei ``textfx.<Name>``); dieses Modul wird nur über ``textfx`` geladen.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QPainter, QPainterPath, QPen, QPolygonF

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.text import zeichenzusatz
from lunivo_writer.editor.text.textfx import PX, aus_text, fx_zeichnen


def _woerter(text: str) -> list[tuple[int, int]]:
    """Die Wörter eines Textes als (Anfang, Ende); Leerzeichen bleiben frei („Nur Wörter“)."""
    aus, start = [], None
    for i, ch in enumerate(text + " "):
        if ch.isspace():
            if start is not None:
                aus.append((start, i)); start = None
        elif start is None:
            start = i
    return aus


# Strichmuster der selbst gezeichneten Unterstreichungen (in Linienbreiten) und ob sie dick, doppelt oder wellig sind
_UNTER_MUSTER = {"einfach": ([], 1, False), "gepunktet": ([1.0, 1.0], 1, False), "gestrichelt": ([3.0, 2.0], 1, False),
                 "strichpunkt": ([4.0, 2.0, 1.0, 2.0], 1, False), "strichpunktpunkt": ([4.0, 2.0, 1.0, 2.0, 1.0, 2.0], 1, False),
                 "wellig": ([], 1, True), "woerter": ([], 1, False), "doppelt": ([], 1, False), "dick": ([], 2, False), "dick_gepunktet": ([1.0, 1.0], 2, False),
                 "dick_gestrichelt": ([3.0, 2.0], 2, False), "lang": ([7.0, 3.0], 1, False), "dick_lang": ([7.0, 3.0], 2, False),
                 "dick_strichpunkt": ([4.0, 2.0, 1.0, 2.0], 2, False), "dick_strichpunktpunkt": ([4.0, 2.0, 1.0, 2.0, 1.0, 2.0], 2, False),
                 "dick_wellig": ([], 2, True), "doppelwellig": ([], 1, True)}


def _unterstrich(p: QPainter, strecken: list[tuple[float, float]], art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Unterstreichungen, die Qt nicht kennt: doppelt, dick, lang gestrichelt, Wellen in zwei Stärken, nur Wörter."""
    muster, dicke, wellig = _UNTER_MUSTER.get(art, ([], 1, False))
    w = max(1.0, groesse * 0.05) * dicke
    y = grundlinie + max(1.5, groesse * 0.12)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(farbe, w); pen.setCapStyle(Qt.FlatCap)
    if muster:
        pen.setDashPattern(muster)
    p.setPen(pen)
    for x0, x1 in strecken:
        if x1 <= x0:
            continue
        zeilen = (y, y + w * 2.2) if art == "doppelt" else (y,)
        for yy in zeilen:
            if wellig:
                pf = QPainterPath(); pf.moveTo(x0, yy)
                x, rich = x0, 1
                schritt = max(2.0, groesse * 0.12)
                while x < x1:
                    pf.quadTo(x + schritt / 2, yy + rich * schritt * 0.5, min(x + schritt, x1), yy); x += schritt; rich = -rich
                p.drawPath(pf)
                if art == "doppelwellig":
                    p.translate(0, w * 2.6); p.drawPath(pf); p.translate(0, -w * 2.6)
            else:
                p.drawLine(QPointF(x0, yy), QPointF(x1, yy))
    p.restore()


def unter_zeichnen(p: QPainter, x0: float, y: float, x1: float, art: str, farbe, groesse: float = 11.0) -> None:
    """Eine Unterstreichungsart als Linie von ``x0`` bis ``x1`` in Höhe ``y`` (für Auswahllisten wie das Menü am Knopf „Unterstrichen“)."""
    _unterstrich(p, [(x0, x1)], art, y - max(1.5, groesse * 0.12), groesse, QColor(farbe))


def unter_symbol(art: str, groesse=(70, 16), farbe: str = "#e6e9ec"):
    """Bildchen einer Unterstreichungsart für Auswahllisten (dieselbe Zeichnung wie im Text)."""
    from PySide6.QtGui import QIcon, QPixmap
    pm = QPixmap(*groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    if art:
        _unterstrich(p, [(3, groesse[0] - 3)], art, groesse[1] * 0.38, 9.0, QColor(farbe))
    p.end()
    return QIcon(pm)


def _doppelt_durch(p: QPainter, rect: QRectF, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Die zweite Durchstreichlinie (die erste zeichnet Qt): zwei Linien in Höhe der Kleinbuchstaben."""
    p.save(); p.setPen(QPen(farbe, max(1.0, groesse * 0.05)))
    for dy in (0.26, 0.38):
        y = grundlinie - groesse * dy
        p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
    p.restore()


def _betonung(p: QPainter, glyphen: list[tuple[float, float, float]], art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Betonungszeichen: ein Punkt, Kreis oder Komma über (oder ein Punkt unter) jedem Buchstaben."""
    r = max(1.2, groesse * 0.065)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    for x, oben, unten in glyphen:
        if art == "unten":
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(QPointF(x, max(unten, grundlinie) + r * 2.2), r, r)
            continue
        y = oben - r * 2.2
        if art == "kreis":
            p.setPen(QPen(farbe, max(0.8, r * 0.5))); p.setBrush(Qt.NoBrush); p.drawEllipse(QPointF(x, y), r, r)
        elif art == "komma":
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(QPointF(x, y), r, r)
            p.setPen(QPen(farbe, max(0.8, r * 0.6))); p.drawLine(QPointF(x + r * 0.6, y + r * 0.4), QPointF(x - r * 0.4, y + r * 2.0))
        else:
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(QPointF(x, y), r, r)
    p.restore()


# ---- im Dokument -----------------------------------------------------------------------------------------------------------
def absaetze_zeichnen(p: QPainter, d) -> None:
    """Die Effekte aller Textstücke des Dokuments zeichnen (Textstücke mit ``P_EFFEKT``). Koordinaten: Dokument."""
    b = d.firstBlock()
    while b.isValid():
        tl = b.layout()
        if tl is not None and b.isVisible() and tl.lineCount():
            it = b.begin()
            while not it.atEnd():
                fr = it.fragment()
                cf = fr.charFormat()
                if fr.isValid() and hat_zeichen_effekt(cf):
                    _stueck(p, b, tl, fr.position() - b.position(), fr.length(), cf, aus_text(cf.stringProperty(_P("P_EFFEKT"))))
                it += 1
        b = b.next()


def _P(name: str):
    from lunivo_writer.editor.dokument import zusatz
    return getattr(zusatz, name)


def hat_zeichen_effekt(cf) -> bool:
    """Hat dieses Zeichenformat etwas, das Lunivo selbst zeichnet: Effekte, doppelt durchgestrichen oder Betonungszeichen?"""
    return bool(cf.stringProperty(_P("P_EFFEKT")) or cf.stringProperty(_P("P_BETONUNG")) or cf.stringProperty(_P("P_UNTER"))
                or cf.stringProperty(_P("P_UMSCHLOSSEN")) or cf.stringProperty(_P("P_RUBY"))
                or (cf.hasProperty(_P("P_DOPPELT")) and cf.property(_P("P_DOPPELT"))))


def _glyphlauf(z, a: int, e: int):
    """(Glyphenpfad, Position) aller Glyphen der Zeile ``z`` von ``a`` bis ``e``."""
    for run in z.glyphRuns(a, e - a):
        rf = run.rawFont()
        for idx, pos in zip(run.glyphIndexes(), run.positions()):
            yield rf.pathForGlyph(idx), pos


def _zeilenpfad(z, a: int, e: int, ursprung: QPointF) -> tuple[QPainterPath, list[tuple[float, float, float]]]:
    """Umrisse der Zeichen ``a``..``e`` der Zeile (in Dokumentkoordinaten) und je Buchstabe (Mitte, Ober-, Unterkante) für Betonungszeichen."""
    pfad = QPainterPath()
    glyphen = []
    for g, pos in _glyphlauf(z, a, e):
        if not g.isEmpty():
            br = g.boundingRect().translated(pos + ursprung)
            glyphen.append((br.center().x(), br.top(), br.bottom()))
        g.translate(pos); pfad.addPath(g)
    pfad.translate(ursprung)
    return pfad, glyphen


def _textfarbe(cf) -> QColor:
    from PySide6.QtGui import QTextFormat
    farbe = cf.foreground().color() if cf.hasProperty(QTextFormat.ForegroundBrush) else QColor("black")
    return QColor("black") if farbe.alpha() == 0 else farbe


def _kontur_von(fx: dict):
    """Die Kontur, die Lunivo selbst zeichnet (aus den Konturteilen des Effekts), sonst ``None``."""
    if "kontur_verlauf" in fx or fx.get("kontur_form", "einfach") != "einfach":
        return (QColor(fx.get("kontur_farbe", Farbe.SCHWARZ)), max(0.1, fx.get("kontur_breite", 0.75)) * PX, fx.get("kontur_form", "einfach"),
                fx.get("kontur_art", "einfach"))
    return None


def _unter_zeichnen_stueck(p: QPainter, b, tl, z, a: int, e: int, cf, art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    x0, x1 = tl.position().x() + z.cursorToX(a)[0], tl.position().x() + z.cursorToX(e)[0]
    woerter = [(tl.position().x() + z.cursorToX(a + i)[0], tl.position().x() + z.cursorToX(a + j)[0]) for i, j in _woerter(b.text()[a:e])] \
        if art == "woerter" else [(x0, x1)]
    _unterstrich(p, woerter, art, grundlinie, groesse, cf.underlineColor() if cf.underlineColor().isValid() and cf.underlineStyle() != 0 else farbe)


def _zusaetze_zeichnen(p: QPainter, tl, z, a: int, e: int, ursprung: QPointF, cf, glyphen: list, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Betonungszeichen, umschlossene Zeichen und Ruby einer Zeilenstrecke."""
    betonung = cf.stringProperty(_P("P_BETONUNG"))
    if betonung:
        _betonung(p, glyphen, betonung, grundlinie, groesse, farbe)
    umschlossen = zeichenzusatz.umschlossen_lesen(cf.stringProperty(_P("P_UMSCHLOSSEN")))
    if umschlossen and glyphen:
        _umschlossen(p, QRectF(tl.position().x() + z.cursorToX(a)[0], ursprung.y(), z.cursorToX(e)[0] - z.cursorToX(a)[0], z.height()),
                     umschlossen, farbe, groesse)
    ruby = zeichenzusatz.ruby_lesen(cf.stringProperty(_P("P_RUBY")))
    if ruby:
        _ruby(p, tl.position().x() + z.cursorToX(a)[0], tl.position().x() + z.cursorToX(e)[0], grundlinie, groesse, ruby, farbe)


def _zeile_zeichnen(p: QPainter, b, tl, z, a: int, e: int, cf, fx: dict) -> None:
    pfad, glyphen = _zeilenpfad(z, a, e, tl.position() + z.position())
    if pfad.isEmpty():
        return
    ursprung = tl.position() + z.position()
    farbe = _textfarbe(cf)
    groesse = cf.font().pixelSize() if cf.font().pixelSize() > 0 else cf.font().pointSizeF() * PX
    grundlinie = ursprung.y() + z.ascent()
    if fx:
        fx_zeichnen(p, pfad, fx, grundlinie, groesse, farbe, _kontur_von(fx))
    if cf.hasProperty(_P("P_DOPPELT")) and cf.property(_P("P_DOPPELT")):
        _doppelt_durch(p, pfad.boundingRect(), grundlinie, groesse, farbe)
    art = cf.stringProperty(_P("P_UNTER"))
    if art:
        _unter_zeichnen_stueck(p, b, tl, z, a, e, cf, art, grundlinie, groesse, farbe)
    _zusaetze_zeichnen(p, tl, z, a, e, ursprung, cf, glyphen, grundlinie, groesse, farbe)


def _stueck(p: QPainter, b, tl, von: int, laenge: int, cf, fx: dict) -> None:
    """Ein Textstück (Zeichenformat ``cf``) zeilenweise mit Effekten und Zeichenzusätzen zeichnen."""
    for i in range(tl.lineCount()):
        z = tl.lineAt(i)
        a, e = max(von, z.textStart()), min(von + laenge, z.textStart() + z.textLength())
        if e > a:
            _zeile_zeichnen(p, b, tl, z, a, e, cf, fx)


def _umschlossen(p: QPainter, kasten: QRectF, wie: tuple[str, str], farbe: QColor, groesse: float) -> None:
    """Die Form um die Zeichen: „reduzieren“ legt sie eng an, „erweitern“ lässt dem Symbol Raum."""
    form, vorlage = wie
    rand = groesse * (0.08 if vorlage == "reduzieren" else 0.22)
    r = kasten.adjusted(-rand, 0, rand, 0)
    if form in ("kreis", "raute"):
        r = r.adjusted(-groesse * 0.1, 0, groesse * 0.1, 0)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(farbe, max(0.6, groesse * 0.06))); p.setBrush(Qt.NoBrush)
    if form == "kreis":
        p.drawEllipse(r)
    elif form == "quadrat":
        p.drawRect(r)
    elif form == "dreieck":
        p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.bottom()), QPointF(r.left(), r.bottom())]))
    else:
        p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()), QPointF(r.center().x(), r.bottom()),
                                 QPointF(r.left(), r.center().y())]))
    p.restore()


def _ruby(p: QPainter, x0: float, x1: float, grundlinie: float, groesse: float, ruby: dict, farbe: QColor) -> None:
    """Der Leittext über dem Basistext, in kleinerer Schrift, nach der gewählten Ausrichtung."""
    f = p.font(); f.setPixelSize(max(4, int(ruby["groesse"] * PX))); p.save(); p.setFont(f); p.setPen(farbe)
    fm = QFontMetricsF(f)
    breite = fm.horizontalAdvance(ruby["ruby"])
    y = grundlinie - groesse * 0.95 - ruby["abstand"] * PX
    if ruby["ausrichtung"] == "links":
        x = x0
    elif ruby["ausrichtung"] == "rechts":
        x = x1 - breite
    else:
        x = (x0 + x1 - breite) / 2
    if ruby["ausrichtung"] == "verteilt" and len(ruby["ruby"]) > 1 and x1 - x0 > breite:
        schritt = (x1 - x0 - breite) / (len(ruby["ruby"]) - 1)
        for i, ch in enumerate(ruby["ruby"]):
            p.drawText(QPointF(x0 + fm.horizontalAdvance(ruby["ruby"][:i]) + schritt * i, y), ch)
    else:
        p.drawText(QPointF(max(x0, x) if breite < x1 - x0 else x, y), ruby["ruby"])
    p.restore()
