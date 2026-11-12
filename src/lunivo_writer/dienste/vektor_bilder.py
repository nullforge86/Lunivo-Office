"""Vektorbilder aus Textprogrammen lesen: EMF (Windows Enhanced Metafile). Das Format wird hier selbst ausgewertet — ohne fremde Programme.

Die Datensätze, die Textprogramme für Linien, Rechtecke, Ellipsen, Pfade, Schrift und Bitmaps schreiben, werden mit QPainter in ein
Bild gezeichnet. Unbekannte Datensätze werden übersprungen; ein Datensatz, der sich nicht lesen lässt, bricht das Bild nicht ab.
Gebraucht von ``dienste/docx_teile`` für Bilder, die Word als EMF speichert."""
from __future__ import annotations

import struct

from PySide6.QtCore import QPointF, QRect, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPainterPath, QPen, QPolygonF, QTransform

from lunivo_writer.editor.objekte import bilddaten as BD

_EMF_SIGNATUR = b" EMF"
_KOPF_BYTES = 88


def ist_emf(blob: bytes) -> bool:
    return len(blob) >= 44 and blob[40:44] == _EMF_SIGNATUR


def bild_lesen(blob: bytes) -> QImage:
    """Ein eingebettetes Bild lesen: Pixelformate direkt, EMF/WMF über den eigenen Zeichner (auch gepackt als EMZ/WMZ). Leeres QImage, wenn es
    sich nicht lesen lässt."""
    if blob[:2] == b"\x1f\x8b":
        try:
            blob = BD.entpacken(blob)
        except BD.BildFehler:
            return QImage()
    from lunivo_writer.editor.objekte.freie_bilder import bild_aus_daten
    if ist_emf(blob) or ist_wmf(blob):                        # Metafile: zuerst als Vektor; leer gezeichnet → eingebettetes Bitmap (Rückfall)
        img = (emf_bild(blob) if ist_emf(blob) else wmf_bild(blob)) or QImage()
        if not img.isNull() and not _leer(img):
            BD.merken(img, blob)
            return img
        roh = bild_aus_daten(blob)
        if not roh.isNull():
            return roh
        if not img.isNull():
            BD.merken(img, blob)
        return img
    return bild_aus_daten(blob)


def _leer(img: QImage) -> bool:
    """Ist das Bild ganz durchsichtig? (zur Probe auf 16 × 16 verkleinert)"""
    klein = img.scaled(16, 16, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return all(klein.pixelColor(x, y).alpha() == 0 for x in range(16) for y in range(16))


def _rgb(farbe: int) -> QColor:
    return QColor(farbe & 0xFF, (farbe >> 8) & 0xFF, (farbe >> 16) & 0xFF)


def _rechteck(b: bytes, off: int) -> QRectF:
    l, t, r, u = struct.unpack_from("<iiii", b, off)
    return QRectF(l, t, r - l, u - t)


def _dib_bild(daten: bytes, bmi_off: int, bmi_len: int, bits_off: int, bits_len: int):
    """Ein DIB (Bitmap-Kopf und Bildpunkte) als QImage; None, wenn es sich nicht lesen lässt."""
    if bmi_len <= 0 or bits_len <= 0:
        return None
    kopf = daten[bmi_off:bmi_off + bmi_len]
    bits = daten[bits_off:bits_off + bits_len]
    # BMP-Datei davor setzen (14 Byte Dateikopf), dann Qt lesen lassen
    datei = b"BM" + struct.pack("<IHHI", 14 + len(kopf) + len(bits), 0, 0, 14 + len(kopf)) + kopf + bits
    img = QImage()
    if not img.loadFromData(datei, "BMP"):
        return None
    return img


def _abbilden(p: QPainter, z: "_Zustand") -> None:
    """Weltumwandlung, dann Fenster → Ansicht (Seitenumwandlung des Metafiles), dann das Zielrechteck."""
    seite = QTransform()
    if z.modus in (7, 8) and z.fenster[2] and z.fenster[3] and z.ansicht[2] and z.ansicht[3]:
        seite.translate(z.ansicht[0], z.ansicht[1])
        seite.scale(z.ansicht[2] / z.fenster[2], z.ansicht[3] / z.fenster[3])
        seite.translate(-z.fenster[0], -z.fenster[1])
    z.seite = seite
    p.setWorldTransform(z.welt * seite * z.basis)


class _Zustand:
    """Stifte, Pinsel, Schrift und Textfarbe des Zeichnens."""

    def __init__(self):
        self.modus = 1                                            # SETMAPMODE: nur 7 und 8 (isotrop/anisotrop) nutzen Fenster und Ansicht
        self.fenster = [0.0, 0.0, 1.0, 1.0]                       # SETWINDOWORG/EXT: x, y, Breite, Höhe (logisch)
        self.ansicht = [0.0, 0.0, 1.0, 1.0]                       # SETVIEWPORTORG/EXT: dasselbe in Geräteeinheiten
        self.welt = QTransform()                                  # Weltumwandlung des Metafiles; ``basis``: Zielrechteck → Papier
        self.basis = QTransform()
        self.tiefe = 0                                            # offene SAVEDC
        self.stift = QPen(QColor("black"), 1)
        self.pinsel = QBrush(QColor("white"))
        self.schrift = QFont()
        self.textfarbe = QColor("black")
        self.objekte: dict[int, object] = {}
        self.stapel: list = []


def _stock(handle: int):
    """Vordefinierte Objekte (Bit 31 gesetzt): Pinsel 0 weiß, 4 leer; Stift 8 schwarz, 6 leer."""
    if handle == 0x80000000:
        return QBrush(QColor("white"))
    if handle == 0x80000004:
        return QBrush(Qt.NoBrush)
    if handle == 0x80000008:
        return QPen(QColor("black"), 1)
    if handle == 0x80000006:
        return QPen(Qt.NoPen)
    return None


MAX_SEITE_PX = 3000                                        # längste Seite eines gerasterten Metafile-Bildes (Schutz vor riesigen Rahmen)


def _begrenzt(breite: float, hoehe: float) -> tuple[int, int]:
    f = min(1.0, MAX_SEITE_PX / max(breite, hoehe, 1.0))
    return max(1, round(breite * f)), max(1, round(hoehe * f))


def _emf_kopf(blob: bytes) -> tuple[QRectF, QRectF] | None:
    """(Grenzen in Geräteeinheiten, Rahmen in 0,01 mm) aus dem Kopf; None, wenn die Datei kein brauchbares EMF ist."""
    if not ist_emf(blob) or len(blob) < _KOPF_BYTES:
        return None
    grenzen, rahmen = _rechteck(blob, 8), _rechteck(blob, 24)
    return (grenzen, rahmen) if grenzen.width() > 0 and grenzen.height() > 0 else None


def masse_px(blob: bytes) -> tuple[float, float] | None:
    """Die Größe, die das Metafile auf dem Blatt haben soll (96 dpi), aus Rahmen (EMF) bzw. Platzhalterkopf (WMF); sonst None."""
    kopf = _emf_kopf(blob)
    if kopf is not None and kopf[1].width() > 0 and kopf[1].height() > 0:
        return kopf[1].width() / 2540 * 96, kopf[1].height() / 2540 * 96
    if blob[:4] == _PLACEABLE and len(blob) >= 22:
        links, oben, rechts, unten = struct.unpack_from("<hhhh", blob, 6)
        einheiten = struct.unpack_from("<H", blob, 14)[0] or 1440
        if rechts > links and unten > oben:
            return (rechts - links) / einheiten * 96, (unten - oben) / einheiten * 96
    return None


def emf_zeichnen(blob: bytes, p: QPainter, ziel: QRectF) -> bool:
    """Das EMF als Vektorzeichnung in ``ziel`` malen (Maßstab folgt dem Rechteck, nichts außerhalb). False, wenn es kein lesbares EMF ist."""
    kopf = _emf_kopf(blob)
    if kopf is None:
        return False
    grenzen = kopf[0]
    p.save()
    p.setClipRect(ziel)
    p.translate(ziel.topLeft())
    p.scale(ziel.width() / grenzen.width(), ziel.height() / grenzen.height())
    p.translate(-grenzen.left(), -grenzen.top())
    z = _Zustand()
    try:
        _zeichnen(blob, p, z)
    except (struct.error, IndexError, ValueError, OverflowError):
        pass
    finally:
        for _ in range(z.tiefe):                              # nicht geschlossene SAVEDC
            p.restore()
        p.restore()
    return True


def emf_bild(blob: bytes, hoehe_px: int = 0, breite_px: int = 0) -> QImage | None:
    """Zeichnet die EMF-Datei in ein Bild. Größe: ``breite_px``/``hoehe_px`` oder aus dem Rahmen der Datei (0,01 mm), doppelt so fein wie 96 dpi,
    höchstens ``MAX_SEITE_PX``. → QImage oder None."""
    kopf = _emf_kopf(blob)
    if kopf is None:
        return None
    if not breite_px or not hoehe_px:
        breite_px, hoehe_px = _begrenzt(kopf[1].width() / 2540 * 96 * 2, kopf[1].height() / 2540 * 96 * 2)
    img = QImage(int(breite_px), int(hoehe_px), QImage.Format_ARGB32_Premultiplied)
    if img.isNull():
        return None
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.TextAntialiasing, True)
    emf_zeichnen(blob, p, QRectF(0, 0, breite_px, hoehe_px))
    p.end()
    return img


def _zeichnen(b: bytes, p: QPainter, z: _Zustand) -> None:
    z.basis = p.worldTransform()
    off = 0
    pfad: QPainterPath | None = None
    pos = QPointF(0, 0)
    while off + 8 <= len(b):
        typ, groesse = struct.unpack_from("<II", b, off)
        if groesse < 8 or off + groesse > len(b):
            break
        try:
            d = off                                               # Beginn des Datensatzes; Daten ab d+8
            if typ == 14:                                         # EOF
                break
            elif typ in (27, 54):                                 # MOVETOEX, LINETO
                x, y = struct.unpack_from("<ii", b, d + 8)
                if typ == 27:
                    pos = QPointF(x, y)
                    if pfad is not None:
                        pfad.moveTo(pos)
                else:
                    if pfad is not None:
                        pfad.lineTo(QPointF(x, y))
                    else:
                        p.setPen(z.stift); p.drawLine(pos, QPointF(x, y))
                    pos = QPointF(x, y)
            elif typ == 37:                                       # SELECTOBJECT
                h = struct.unpack_from("<I", b, d + 8)[0]
                obj = _stock(h) if h & 0x80000000 else z.objekte.get(h)
                if isinstance(obj, QPen):
                    z.stift = obj
                elif isinstance(obj, QBrush):
                    z.pinsel = obj
                elif isinstance(obj, QFont):
                    z.schrift = obj
            elif typ == 40:                                       # DELETEOBJECT
                z.objekte.pop(struct.unpack_from("<I", b, d + 8)[0], None)
            elif typ == 38:                                       # CREATEPEN
                h, stil, breite, _x, farbe = struct.unpack_from("<IIiiI", b, d + 8)
                pen = QPen(_rgb(farbe), max(0, breite) or 1)
                if stil == 5:                                     # PS_NULL
                    pen = QPen(Qt.NoPen)
                z.objekte[h] = pen
            elif typ == 95:                                       # EXTCREATEPEN: Stiftangaben ab d+28 (Stil, Breite, Pinselstil, Farbe)
                h = struct.unpack_from("<I", b, d + 8)[0]
                stil, breite, _pinsel, farbe = struct.unpack_from("<IIII", b, d + 28)
                pen = QPen(QColor("black") if stil == 5 else _rgb(farbe), max(1, breite) or 1)
                z.objekte[h] = QPen(Qt.NoPen) if stil == 5 else pen
            elif typ == 39:                                       # CREATEBRUSHINDIRECT
                h, stil, farbe, _hatch = struct.unpack_from("<IIII", b, d + 8)
                if stil == 1:                                     # BS_NULL
                    z.objekte[h] = QBrush(Qt.NoBrush)
                else:
                    z.objekte[h] = QBrush(_rgb(farbe))
            elif typ == 82:                                       # EXTCREATEFONTINDIRECTW
                h = struct.unpack_from("<I", b, d + 8)[0]
                z.objekte[h] = _schrift(b, d + 12)
            elif typ == 24:                                       # SETTEXTCOLOR
                z.textfarbe = _rgb(struct.unpack_from("<I", b, d + 8)[0])
            elif typ == 43:                                       # RECTANGLE
                r = _rechteck(b, d + 8)
                _umrissen(p, z, pfad, lambda: p.drawRect(r))
            elif typ == 42:                                       # ELLIPSE
                r = _rechteck(b, d + 8)
                _umrissen(p, z, pfad, lambda: p.drawEllipse(r))
            elif typ == 44:                                       # ROUNDRECT
                r = _rechteck(b, d + 8)
                bw, bh = struct.unpack_from("<ii", b, d + 24)
                _umrissen(p, z, pfad, lambda: p.drawRoundedRect(r, bw / 2 or 1, bh / 2 or 1, Qt.AbsoluteSize))
            elif typ in (2, 3, 4, 5, 6, 85, 86, 87, 88, 89):          # POLYBEZIER, POLYGON, POLYLINE (und …TO, 16-Bit-Varianten)
                wide = typ < 85
                n = struct.unpack_from("<I", b, d + 24)[0]
                fmt = "<ii" if wide else "<hh"
                werte = [struct.unpack_from(fmt, b, d + 28 + i * (8 if wide else 4)) for i in range(n)]
                punkte = [QPointF(x, y) for x, y in werte]
                if typ in (5, 6, 88, 89):                         # …TO: ab der aktuellen Position
                    punkte = [pos] + punkte
                if typ in (2, 5, 85, 88):
                    _kurve(p, z, pfad, punkte)
                else:
                    _mehrfach(p, z, pfad, typ in (3, 86), punkte)
                if punkte:
                    pos = punkte[-1]
            elif typ == 59:                                       # BEGINPATH
                pfad = QPainterPath(pos)
            elif typ == 61:                                       # CLOSEFIGURE
                if pfad is not None:
                    pfad.closeSubpath()
            elif typ == 60:                                       # ENDPATH
                pass
            elif typ in (62, 63, 64):                             # FILLPATH, STROKEANDFILLPATH, STROKEPATH
                if pfad is not None:
                    if typ in (62, 63):
                        p.setPen(Qt.NoPen); p.setBrush(z.pinsel); p.drawPath(pfad)
                    if typ in (63, 64):
                        p.setBrush(Qt.NoBrush); p.setPen(z.stift); p.drawPath(pfad)
                pfad = None
            elif typ == 30:                                       # INTERSECTCLIPRECT
                p.setClipRect(_rechteck(b, d + 8), Qt.IntersectClip)
            elif typ == 33:                                       # SAVEDC
                z.stapel.append((z.stift, z.pinsel, z.schrift, z.textfarbe, QPointF(pos), QTransform(z.welt)))
                p.save(); z.tiefe += 1
            elif typ == 34:                                       # RESTOREDC
                if z.stapel and z.tiefe:
                    z.stift, z.pinsel, z.schrift, z.textfarbe, pos, z.welt = z.stapel.pop()
                    p.restore(); z.tiefe -= 1
            elif typ == 17:                                       # SETMAPMODE
                z.modus = struct.unpack_from("<I", b, d + 8)[0]
                _abbilden(p, z)
            elif typ in (9, 10, 11, 12):                          # SETWINDOWEXTEX, SETWINDOWORGEX, SETVIEWPORTEXTEX, SETVIEWPORTORGEX
                x, y = struct.unpack_from("<ii", b, d + 8)
                ziel = z.fenster if typ in (9, 10) else z.ansicht
                ziel[2:] = [x, y] if typ in (9, 11) else ziel[2:]
                ziel[:2] = [x, y] if typ in (10, 12) else ziel[:2]
                _abbilden(p, z)
            elif typ in (7, 8, 90, 91):                           # POLYPOLYLINE, POLYPOLYGON (32 und 16 Bit)
                _vielfach(p, z, pfad, b, d, typ in (8, 91), typ < 90)
            elif typ in (35, 36):                                 # SETWORLDTRANSFORM, MODIFYWORLDTRANSFORM
                m = QTransform(*struct.unpack_from("<6f", b, d + 8))
                modus = 4 if typ == 35 else struct.unpack_from("<I", b, d + 32)[0]
                z.welt = (QTransform() if modus == 1 else m * z.welt if modus == 2 else z.welt * m if modus == 3 else m)
                _abbilden(p, z)
            elif typ == 84:                                       # EXTTEXTOUTW
                _text(p, b, d, z)
            elif typ in (76, 81):                                 # BITBLT und STRETCHDIBITS mit eingebetteter Bitmap
                _bitmap(p, b, d, typ)
        except (struct.error, IndexError, ValueError, OverflowError):
            pass                                              # ein nicht lesbarer Befehl wird übersprungen, die übrigen werden gezeichnet
        off += groesse


def _umrissen(p: QPainter, z: _Zustand, pfad, zeichnen) -> None:
    """Form mit aktuellem Stift und Pinsel zeichnen — oder in den Pfad aufnehmen (das ist dann noch nicht gezeichnet)."""
    if pfad is not None:
        return
    p.setPen(z.stift); p.setBrush(z.pinsel)
    zeichnen()


def _kurve(p: QPainter, z: "_Zustand", pfad, punkte: list) -> None:
    """POLYBEZIER: ein Anfangspunkt, dann je drei Punkte (zwei Steuerpunkte und das Ende) als Kubikkurve."""
    if len(punkte) < 4:
        return
    k = pfad if pfad is not None else QPainterPath()
    if pfad is None or pfad.elementCount() == 0:
        k.moveTo(punkte[0])
    for i in range(1, len(punkte) - 2, 3):
        k.cubicTo(punkte[i], punkte[i + 1], punkte[i + 2])
    if pfad is None:
        p.setPen(z.stift); p.setBrush(Qt.NoBrush); p.drawPath(k)


def _vielfach(p: QPainter, z: "_Zustand", pfad, b: bytes, d: int, geschlossen: bool, breit: bool) -> None:
    """POLYPOLYGON/POLYPOLYLINE: Anzahl der Teile und Punkte, die Punktzahl je Teil, dann alle Punkte; Flächen nach Wechselregel (Löcher)."""
    teile, gesamt = struct.unpack_from("<II", b, d + 24)
    if teile > 65536 or gesamt > 1_000_000:
        return
    zaehler = struct.unpack_from("<%dI" % teile, b, d + 32)
    ab = d + 32 + 4 * teile
    gross = 8 if breit else 4
    k = pfad if pfad is not None else QPainterPath()
    k.setFillRule(Qt.OddEvenFill)
    i = 0
    for n in zaehler:
        pts = [QPointF(*struct.unpack_from("<ii" if breit else "<hh", b, ab + (i + j) * gross)) for j in range(n)]
        i += n
        if not pts:
            continue
        k.moveTo(pts[0])
        for q in pts[1:]:
            k.lineTo(q)
        if geschlossen:
            k.closeSubpath()
    if pfad is None:
        p.setPen(z.stift); p.setBrush(z.pinsel if geschlossen else Qt.NoBrush); p.drawPath(k)


def _mehrfach(p: QPainter, z: _Zustand, pfad, geschlossen: bool, punkte: list) -> None:
    if not punkte:
        return
    if pfad is not None:
        pfad.moveTo(punkte[0])
        for q in punkte[1:]:
            pfad.lineTo(q)
        if geschlossen:
            pfad.closeSubpath()
        return
    p.setPen(z.stift)
    if geschlossen:
        p.setBrush(z.pinsel)
        p.drawPolygon(QPolygonF(punkte))
    else:
        p.setBrush(Qt.NoBrush)
        p.drawPolyline(QPolygonF(punkte))


def _schrift(b: bytes, off: int) -> QFont:
    """LOGFONTW ab ``off``: Höhe, Gewicht, Kursiv, Unterstrichen und Schriftname."""
    hoehe, _breite, _esc, _ori, gewicht = struct.unpack_from("<iiiii", b, off)
    kursiv, unterstrichen, durchgestrichen = b[off + 20], b[off + 21], b[off + 22]
    name = b[off + 28:off + 28 + 64].decode("utf-16-le", "ignore").split("\x00")[0]
    f = QFont(name or "Liberation Sans")
    if hoehe:
        f.setPixelSize(max(1, abs(hoehe)))
    f.setBold(gewicht >= 600)
    f.setItalic(bool(kursiv))
    f.setUnderline(bool(unterstrichen))
    f.setStrikeOut(bool(durchgestrichen))
    return f


def _text(p: QPainter, b: bytes, d: int, z: _Zustand) -> None:
    """EXTTEXTOUTW: Text an der Referenzposition, mit Schrift und Textfarbe des Zustands."""
    # EMR_EXTTEXTOUTW: Grenzen (16), Modus (4), Skalierung (8), dann EMRTEXT ab d+8+16+4+8 = d+36
    t = d + 36
    refx, refy, zeichen, text_off = struct.unpack_from("<iiII", b, t)
    if zeichen == 0 or text_off <= 0:
        return
    text = b[d + text_off:d + text_off + zeichen * 2].decode("utf-16-le", "ignore")
    p.setFont(z.schrift)
    p.setPen(z.textfarbe)
    p.drawText(QPointF(refx, refy), text)


def _bitmap(p: QPainter, b: bytes, d: int, typ: int) -> None:
    """BITBLT (76) und STRETCHDIBITS (81) mit eingebetteter Bitmap; ohne Bitmap bleibt es still.
    Feldlagen (ab Datensatzbeginn d): BITBLT Ziel x/y/Breite/Höhe ab 24, Bitmapkopf-Versatz ab 84, Bildpunkt-Versatz ab 92;
    STRETCHDIBITS Ziel x/y ab 24, Bitmapkopf ab 48, Bildpunkte ab 56, Zielbreite/-höhe ab 72."""
    if typ == 81:
        x, y = struct.unpack_from("<ii", b, d + 24)
        bmi_off, bmi_len, bits_off, bits_len = struct.unpack_from("<IIII", b, d + 48)
        breite, hoehe = struct.unpack_from("<ii", b, d + 72)
    else:
        x, y, breite, hoehe = struct.unpack_from("<iiii", b, d + 24)
        bmi_off, bmi_len, bits_off, bits_len = struct.unpack_from("<IIII", b, d + 84)
    if bmi_len == 0 or bits_len == 0:
        return
    img = _dib_bild(b, d + bmi_off, bmi_len, d + bits_off, bits_len)
    if img is not None:
        p.drawImage(QRectF(x, y, breite, hoehe), img)


# ---------------------------------------------------------------- WMF (Windows Metafile, 16 Bit)

_PLACEABLE = b"\xd7\xcd\xc6\x9a"


def ist_wmf(blob: bytes) -> bool:
    if blob[:4] == _PLACEABLE:
        return True
    return len(blob) >= 18 and struct.unpack_from("<HH", blob, 0) in ((1, 9), (2, 9))


def _wmf_kopf(blob: bytes) -> tuple[QRectF, int, tuple[float, float], tuple[bool, bool]] | None:
    """(Logische Grenzen, Beginn der Datensätze, Größe in px bei 96 dpi, Spiegelung waagerecht/senkrecht); ohne Platzhalterkopf gilt ein Quadrat
    1000 × 1000 mit 400 px. Eine negative Fensterausdehnung (y nach oben, wie oft in Office-Metafiles) wird als Spiegelung gemeldet."""
    if not ist_wmf(blob) or len(blob) < 40:
        return None
    start = 22 + 18 if blob[:4] == _PLACEABLE else 18
    fenster, spiegel = _wmf_fenster(blob, start)
    if blob[:4] == _PLACEABLE:
        links, oben, rechts, unten = struct.unpack_from("<hhhh", blob, 6)
        einheiten = struct.unpack_from("<H", blob, 14)[0] or 1440
        if rechts > links and unten > oben:
            return fenster or QRectF(links, oben, rechts - links, unten - oben), start, ((rechts - links) / einheiten * 96, (unten - oben) / einheiten * 96), spiegel
    return fenster or QRectF(0, 0, 1000, 1000), start, (400.0, 400.0), spiegel


def _wmf_fenster(b: bytes, off: int) -> tuple[QRectF | None, tuple[bool, bool]]:
    """Das logische Fenster aus SETWINDOWORG/SETWINDOWEXT: die Koordinaten der Zeichenbefehle beziehen sich darauf, nicht auf den Platzhalterkopf."""
    org, ext = (0, 0), None
    while off + 6 <= len(b):
        groesse, fn = struct.unpack_from("<IH", b, off)
        if groesse < 3 or off + groesse * 2 > len(b) or fn == 0:
            break
        if fn == 0x020B and groesse >= 5:
            org = struct.unpack_from("<hh", b, off + 6)[::-1]               # y, x
        elif fn == 0x020C and groesse >= 5:                                  # die letzte Angabe gilt (Office schreibt sie oft zweimal)
            ext = struct.unpack_from("<hh", b, off + 6)[::-1]
        off += groesse * 2
    if ext is None or not ext[0] or not ext[1]:
        return None, (False, False)
    return QRectF(org[0], org[1], ext[0], ext[1]).normalized(), (ext[0] < 0, ext[1] < 0)


def wmf_zeichnen(blob: bytes, p: QPainter, ziel: QRectF) -> bool:
    """Das WMF als Vektorzeichnung in ``ziel`` malen. False, wenn es kein lesbares WMF ist."""
    kopf = _wmf_kopf(blob)
    if kopf is None:
        return False
    grenzen, start, _mass, (spiegel_x, spiegel_y) = kopf
    p.save()
    p.setClipRect(ziel)
    p.translate(ziel.topLeft())
    p.scale(ziel.width() / grenzen.width(), ziel.height() / grenzen.height())
    p.translate(-grenzen.left(), -grenzen.top())
    if spiegel_x or spiegel_y:                                # negative Ausdehnung: die Achse zeigt in die Gegenrichtung
        p.translate(grenzen.left() * 2 + grenzen.width() if spiegel_x else 0, grenzen.top() * 2 + grenzen.height() if spiegel_y else 0)
        p.scale(-1 if spiegel_x else 1, -1 if spiegel_y else 1)
    try:
        _wmf_zeichnen(blob, start, p)
    except (struct.error, IndexError, ValueError, OverflowError):
        pass
    finally:
        p.restore()
    return True


def wmf_bild(blob: bytes, breite_px: int = 0, hoehe_px: int = 0) -> QImage | None:
    """Zeichnet die WMF-Datei in ein Bild (doppelt so fein wie 96 dpi, höchstens ``MAX_SEITE_PX``). → QImage oder None."""
    kopf = _wmf_kopf(blob)
    if kopf is None:
        return None
    if not breite_px or not hoehe_px:
        breite_px, hoehe_px = _begrenzt(kopf[2][0] * 2, kopf[2][1] * 2)
    img = QImage(int(breite_px), int(hoehe_px), QImage.Format_ARGB32_Premultiplied)
    if img.isNull():
        return None
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.TextAntialiasing, True)
    wmf_zeichnen(blob, p, QRectF(0, 0, breite_px, hoehe_px))
    p.end()
    return img


def _wmf_zeichnen(b: bytes, off: int, p: QPainter) -> None:
    objekte: list = []
    stift, pinsel, schrift = QPen(QColor("black"), 1), QBrush(QColor("white")), QFont()
    textfarbe, hintergrund = QColor("black"), QColor("white")
    ausrichtung = 0
    stapel: list = []
    pos = QPointF(0, 0)

    def stock(idx: int):
        return {0: QBrush(QColor("white")), 4: QBrush(Qt.NoBrush), 8: QPen(QColor("black"), 1), 6: QPen(Qt.NoPen)}.get(idx)

    def ablegen(obj) -> None:
        """Neue Objekte belegen wie bei GDI den ersten freien Platz (gelöschte Plätze werden wiederverwendet)."""
        for i, alt in enumerate(objekte):
            if alt is None:
                objekte[i] = obj
                return
        objekte.append(obj)

    def worte(o: int, n: int) -> list[int]:
        return list(struct.unpack_from("<%dh" % n, b, o))

    while off + 6 <= len(b):
        groesse, fn = struct.unpack_from("<IH", b, off)
        if groesse < 3 or off + groesse * 2 > len(b):
            break
        try:
            d = off + 6                          # Beginn der Parameter
            ende = off + groesse * 2
            if fn == 0:                          # META_EOF
                break
            if fn == 0x020B or fn == 0x020C:     # SETWINDOWORG, SETWINDOWEXT (Lage schon aus dem Kopf)
                pass
            elif fn == 0x0418:                   # ELLIPSE
                u, r_, o, l = worte(d, 4)
                p.setPen(stift); p.setBrush(pinsel); p.drawEllipse(QRectF(QPointF(l, o), QPointF(r_, u)).normalized())
            elif fn == 0x0416:                   # INTERSECTCLIPRECT
                u, r_, o, l = worte(d, 4)
                p.setClipRect(QRectF(QPointF(l, o), QPointF(r_, u)).normalized(), Qt.IntersectClip)
            elif fn == 0x0538:                   # POLYPOLYGON: Anzahl der Teile, Punktzahl je Teil, dann alle Punkte (Wechselregel: Löcher)
                n = worte(d, 1)[0]
                zaehler = worte(d + 2, n)
                k = QPainterPath(); k.setFillRule(Qt.OddEvenFill)
                ab = d + 2 + 2 * n
                for c in zaehler:
                    pts = [QPointF(*struct.unpack_from("<hh", b, ab + j * 4)) for j in range(c)]
                    ab += c * 4
                    if pts:
                        k.addPolygon(QPolygonF(pts)); k.closeSubpath()
                p.setPen(stift); p.setBrush(pinsel); p.drawPath(k)
            elif fn == 0x0214:                   # MOVETO (y, x)
                y, x = worte(d, 2); pos = QPointF(x, y)
            elif fn == 0x0213:                   # LINETO (y, x)
                y, x = worte(d, 2)
                p.setPen(stift); p.drawLine(pos, QPointF(x, y)); pos = QPointF(x, y)
            elif fn in (0x0324, 0x0325):         # POLYGON, POLYLINE: Anzahl, dann x, y
                n = worte(d, 1)[0]
                pts = [QPointF(x, y) for x, y in (worte(d + 2 + i * 4, 2) for i in range(n))]
                if fn == 0x0324:
                    p.setPen(stift); p.setBrush(pinsel); p.drawPolygon(QPolygonF(pts))
                else:
                    p.setPen(stift); p.setBrush(Qt.NoBrush); p.drawPolyline(QPolygonF(pts))
            elif fn == 0x061D:                   # ROUNDRECT: Höhe, Breite, unten, rechts, oben, links (umgekehrt)
                eh, ew, u, r_, o, l = worte(d, 6)
                p.setPen(stift); p.setBrush(pinsel)
                p.drawRoundedRect(QRectF(QPointF(l, o), QPointF(r_, u)).normalized(), ew / 2 or 1, eh / 2 or 1, Qt.AbsoluteSize)
            elif fn == 0x041B:                   # RECTANGLE
                u, r_, o, l = worte(d, 4)
                p.setPen(stift); p.setBrush(pinsel); p.drawRect(QRectF(QPointF(l, o), QPointF(r_, u)).normalized())
            elif fn == 0x0418:                   # ELLIPSE
                u, r_, o, l = worte(d, 4)
                p.setPen(stift); p.setBrush(pinsel); p.drawEllipse(QRectF(QPointF(l, o), QPointF(r_, u)).normalized())
            elif fn == 0x012D:                   # SELECTOBJECT
                idx = struct.unpack_from("<H", b, d)[0]
                obj = stock(idx & 0x7FFF) if idx & 0x8000 else (objekte[idx] if idx < len(objekte) else None)
                if isinstance(obj, QPen):
                    stift = obj
                elif isinstance(obj, QBrush):
                    pinsel = obj
                elif isinstance(obj, QFont):
                    schrift = obj
            elif fn == 0x01F0:                   # DELETEOBJECT
                idx = struct.unpack_from("<H", b, d)[0]
                if idx < len(objekte):
                    objekte[idx] = None
            elif fn == 0x02FA:                   # CREATEPENINDIRECT: Stil, Breite (x), Farbe
                stil = struct.unpack_from("<H", b, d)[0]
                breite = struct.unpack_from("<h", b, d + 2)[0]
                farbe = struct.unpack_from("<I", b, d + 6)[0]
                ablegen(QPen(Qt.NoPen) if stil == 5 else QPen(_rgb(farbe), max(1, breite) or 1))
            elif fn == 0x02FC:                   # CREATEBRUSHINDIRECT: Stil, Farbe, Schraffur
                stil = struct.unpack_from("<H", b, d)[0]
                farbe = struct.unpack_from("<I", b, d + 2)[0]
                ablegen(QBrush(Qt.NoBrush) if stil == 1 else QBrush(_rgb(farbe)))
            elif fn == 0x02FB:                   # CREATEFONTINDIRECT (LOGFONT, 16 Bit)
                hoehe, _b, _e, _o, gewicht = struct.unpack_from("<hhhhh", b, d)
                kursiv, unterstrichen, durchgestrichen = b[d + 10], b[d + 11], b[d + 12]
                name = b[d + 18:d + 18 + 32].split(b"\x00")[0].decode("cp1252", "ignore")
                f = QFont(name or "Liberation Sans")
                if hoehe:
                    f.setPixelSize(max(1, abs(hoehe)))
                f.setBold(gewicht >= 600); f.setItalic(bool(kursiv)); f.setUnderline(bool(unterstrichen)); f.setStrikeOut(bool(durchgestrichen))
                ablegen(f)
            elif fn == 0x0209:                   # SETTEXTCOLOR
                textfarbe = _rgb(struct.unpack_from("<I", b, d)[0])
            elif fn == 0x0201:                   # SETBKCOLOR
                hintergrund = _rgb(struct.unpack_from("<I", b, d)[0])
            elif fn == 0x012E:                   # SETTEXTALIGN
                ausrichtung = struct.unpack_from("<H", b, d)[0]
            elif fn == 0x001E:                   # SAVEDC
                stapel.append((stift, pinsel, schrift, textfarbe, QPointF(pos))); p.save()
            elif fn == 0x0127:                   # RESTOREDC
                if stapel:
                    stift, pinsel, schrift, textfarbe, pos = stapel.pop()
                    p.restore()
            elif fn == 0x0A32:                   # EXTTEXTOUT: y, x, Länge, Optionen, [Rechteck], Text
                y, x, laenge, optionen = worte(d, 4)
                t = d + 8 + (8 if optionen & 6 else 0)
                text = b[t:t + laenge].decode("cp1252", "ignore")
                _wmf_text(p, x, y, text, schrift, textfarbe, ausrichtung)
            elif fn == 0x0521:                   # TEXTOUT: Länge, Text, y, x
                laenge = worte(d, 1)[0]
                text = b[d + 2:d + 2 + laenge].decode("cp1252", "ignore")
                y, x = struct.unpack_from("<hh", b, d + 2 + laenge + (laenge & 1))
                _wmf_text(p, x, y, text, schrift, textfarbe, ausrichtung)
            elif fn == 0x0F43:                   # STRETCHDIB: Ziel-Lage und Größe stehen am Anfang der Parameter, dann das DIB
                _wmf_dib(p, b, d, ende)
        except (struct.error, IndexError, ValueError, OverflowError):
            pass                                              # ein nicht lesbarer Befehl wird übersprungen, die übrigen werden gezeichnet
        off = ende
    for _ in stapel:                                          # nicht geschlossene SAVEDC
        p.restore()


def _wmf_text(p: QPainter, x: int, y: int, text: str, schrift, farbe, ausrichtung: int) -> None:
    from PySide6.QtGui import QFontMetricsF
    p.setFont(schrift); p.setPen(farbe)
    grundlinie = y if (ausrichtung & 24) == 24 else y + QFontMetricsF(schrift).ascent()     # sonst: oben links
    p.drawText(QPointF(x, grundlinie), text)


def _wmf_dib(p: QPainter, b: bytes, d: int, ende: int) -> None:
    """STRETCHDIB: Parameter (Rop, Farbe, Quellgröße, Quellausschnitt, Ziel) gefolgt von BITMAPINFO und Bildpunkten."""
    rop, _usage, srchoehe, srcbreite, ysrc, xsrc, zielhoehe, zielbreite, ydest, xdest = struct.unpack_from("<IHhhhhhhhh", b, d)
    dib = d + 22
    kopf_groesse = struct.unpack_from("<I", b, dib)[0]
    _w, _h, _planes, bpp, komp = struct.unpack_from("<iiHHI", b, dib + 4)
    clr_used = struct.unpack_from("<I", b, dib + 32)[0] if kopf_groesse >= 40 else 0
    paletten = clr_used or (1 << bpp if bpp <= 8 else 0)
    palette_bytes = paletten * 4
    breite_zeile = ((abs(_w) * bpp + 31) // 32) * 4
    bild_bytes = breite_zeile * abs(_h) if komp == 0 else struct.unpack_from("<I", b, dib + 20)[0]
    kopf = b[dib:dib + kopf_groesse + palette_bytes]
    bits = b[dib + kopf_groesse + palette_bytes:dib + kopf_groesse + palette_bytes + bild_bytes]
    datei = b"BM" + struct.pack("<IHHI", 14 + len(kopf) + len(bits), 0, 0, 14 + len(kopf)) + kopf + bits
    img = QImage()
    if img.loadFromData(datei, "BMP"):
        p.drawImage(QRectF(xdest, ydest, zielbreite, zielhoehe), img)
