"""Qt-Backend der Rendering-Schnittstelle: setzt die Zeichenanweisungen auf einem ``QPainter`` um."""
from __future__ import annotations

from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient

from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering import ImageFill, LinearGradient, PatternFill, RadialGradient, RenderBackend, Style, TextureFill
from lunivo_writer.core.textlayout import FontSpec


def _farbe(style: Style) -> QColor:
    r, g, b, a = style.color
    return QColor(r, g, b, a)


def _stufen(verlauf, g) -> None:
    for pos, (r, gr, b, a) in verlauf.stops:
        g.setColorAt(pos, QColor(r, gr, b, a))


_BILDER: dict = {}


def _bild(data: bytes) -> QImage:
    """Die Bilddatei als ``QImage``; dieselben Bytes liefern dasselbe Objekt (die Effekte merken sich ihre Ergebnisse je Bildobjekt)."""
    schluessel = (len(data), hash(data))
    img = _BILDER.get(schluessel)
    if img is None:
        if len(_BILDER) >= 64:
            _BILDER.pop(next(iter(_BILDER)))
        img = _BILDER[schluessel] = QImage.fromData(data)
    return img


def _png(img: QImage) -> bytes:
    from lunivo_writer.editor.objekte import bilddaten as BD
    return BD.png_bytes(img)


def _pinsel(style: Style, rect: Rect | None = None):
    """Füllung des Stils: Verlauf, Muster, Textur oder Bild, wenn angegeben, sonst die Farbe."""
    v = style.fill
    if isinstance(v, PatternFill):
        from lunivo_writer.editor.text import muster as M
        return M.pinsel(v.key, v.color, v.ground)
    if isinstance(v, TextureFill):
        from lunivo_writer.editor.text.textur import textur
        return QBrush(textur(v.key, 64))
    if isinstance(v, ImageFill):
        img = _bild(v.data)
        if img.isNull() or rect is None:
            return QBrush(Qt.NoBrush)
        return QBrush(img.scaled(int(max(1, rect.width)), int(max(1, rect.height))))
    if isinstance(v, LinearGradient):
        g = QLinearGradient(QPointF(v.start.x, v.start.y), QPointF(v.end.x, v.end.y))
        _stufen(v, g)
        return QBrush(g)
    if isinstance(v, RadialGradient):
        g = QRadialGradient(QPointF(v.center.x, v.center.y), v.radius)
        _stufen(v, g)
        return QBrush(g)
    return QBrush(_farbe(style))


def _qfont(font) -> QFont:
    if isinstance(font, QFont):
        return font
    if isinstance(font, FontSpec):
        from lunivo_writer.adapter.qt.textlayout import _schrift
        return _schrift(font)
    return QFont(str(font))


def _ausgewaschen(img: QImage, grad: float) -> QImage:
    """Das Bild um ``grad`` (0…1) zum Weiß hin aufgehellt, Durchsichtiges bleibt durchsichtig."""
    out = img.convertToFormat(QImage.Format_ARGB32)
    q = QPainter(out)
    q.setCompositionMode(QPainter.CompositionMode_SourceAtop)
    q.fillRect(out.rect(), QColor(255, 255, 255, round(255 * grad)))
    q.end()
    return out


def _qrect(r: Rect) -> QRectF:
    return QRectF(r.x, r.y, r.width, r.height)


def _flags(align: str, wrap: bool, valign: str = "center") -> int:
    h = {"center": Qt.AlignHCenter, "right": Qt.AlignRight}.get(align, Qt.AlignLeft)
    v = Qt.AlignTop if valign == "top" else Qt.AlignVCenter
    return int(h | v | (Qt.TextWordWrap if wrap else 0))


class QtRenderBackend(RenderBackend):
    def __init__(self, painter: QPainter):
        self.p = painter

    def _stift(self, style: Style) -> QPen:
        pen = QPen(QColor(*style.outline) if style.outline else _farbe(style), style.width)
        if style.cap != "square":
            pen.setCapStyle({"flat": Qt.FlatCap, "round": Qt.RoundCap}.get(style.cap, Qt.SquareCap))
        if style.join != "miter":
            pen.setJoinStyle({"round": Qt.RoundJoin, "bevel": Qt.BevelJoin}.get(style.join, Qt.MiterJoin))
        if style.dashed:
            pen.setStyle(Qt.DashLine)
        elif isinstance(style.dash, tuple):
            pen.setDashPattern(list(style.dash))
        elif style.dash:
            pen.setStyle({"dot": Qt.DotLine, "dash": Qt.DashLine, "dashdot": Qt.DashDotLine, "dashdotdot": Qt.DashDotDotLine}.get(style.dash, Qt.SolidLine))
        return pen

    def draw_text(self, text: str, position: Point, font, style: Style) -> None:
        self.p.save()
        self.p.setFont(_qfont(font))
        self.p.setPen(QPen(_farbe(style)))
        self.p.drawText(QPointF(position.x, position.y), text)
        self.p.restore()

    def draw_text_box(self, text: str, rect: Rect, font, style: Style, align: str = "left", wrap: bool = True, valign: str = "center") -> None:
        self.p.save()
        self.p.setFont(_qfont(font))
        self.p.setPen(QPen(_farbe(style)))
        self.p.drawText(_qrect(rect), _flags(align, wrap, valign), text)
        self.p.restore()

    def text_bounds(self, text: str, rect: Rect, font, align: str = "left", wrap: bool = True) -> Rect:
        self.p.save()
        self.p.setFont(_qfont(font))
        b = self.p.boundingRect(_qrect(rect), _flags(align, wrap), text)
        self.p.restore()
        return Rect(b.x(), b.y(), b.width(), b.height())

    def draw_rect(self, rect: Rect, style: Style) -> None:
        self.p.save()
        self.p.setPen(self._stift(style) if style.width > 0 else Qt.NoPen)
        if style.filled:
            self.p.setBrush(_pinsel(style, rect))
        else:
            self.p.setBrush(Qt.NoBrush)
        if style.filled and style.width <= 0:
            self.p.fillRect(_qrect(rect), _pinsel(style, rect))
        else:
            self.p.drawRect(_qrect(rect))
        self.p.restore()

    def draw_ellipse(self, center: Point, rx: float, ry: float, style: Style) -> None:
        self.p.save()
        self.p.setPen(self._stift(style) if style.width > 0 else Qt.NoPen)
        self.p.setBrush(_pinsel(style) if style.filled else Qt.NoBrush)
        self.p.drawEllipse(QPointF(center.x, center.y), rx, ry)
        self.p.restore()

    @staticmethod
    def _pfade(ops: list) -> list[QPainterPath]:
        """Teilpfade der Anweisungen: ein neues ``M``, ``E`` oder ``R`` beginnt einen eigenen Pfad."""
        pfade: list[QPainterPath] = []
        aktuell: QPainterPath | None = None
        for op in ops:
            k = op[0]
            if k == "M":
                aktuell = QPainterPath(QPointF(op[1], op[2]))
                pfade.append(aktuell)
            elif k == "L" and aktuell is not None:
                aktuell.lineTo(op[1], op[2])
            elif k == "Q" and aktuell is not None:
                aktuell.quadTo(QPointF(op[1], op[2]), QPointF(op[3], op[4]))
            elif k == "C" and aktuell is not None:
                aktuell.cubicTo(*op[1:7])
            elif k == "Z" and aktuell is not None:
                aktuell.closeSubpath()
            elif k == "E":
                pf = QPainterPath()
                pf.addEllipse(QPointF(op[1], op[2]), op[3], op[4])
                pfade.append(pf)
            elif k == "R":
                pf = QPainterPath()
                pf.addRect(QRectF(op[1], op[2], op[3], op[4]))
                pfade.append(pf)
        return pfade

    @staticmethod
    def _vereinigt(teile: list[QPainterPath], union: bool) -> QPainterPath:
        if union:
            pf = teile[0]
            for t in teile[1:]:
                pf = pf.united(t)
            return pf
        pf = QPainterPath()
        for t in teile:
            pf.addPath(t)
        return pf

    def draw_path(self, ops: list, style: Style, antialias: bool | None = True, union: bool = False) -> None:
        teile = self._pfade(ops)
        if not teile:
            return
        pf = self._vereinigt(teile, union)
        self.p.save()
        if antialias is not None:
            self.p.setRenderHint(QPainter.Antialiasing, antialias)
        self.p.setPen(self._stift(style) if style.width > 0 else Qt.NoPen)
        self.p.setBrush(_pinsel(style) if style.filled else Qt.NoBrush)
        self.p.drawPath(pf)
        self.p.restore()

    def push_state(self, opacity: float = 1.0, translate: Point | None = None, rotate: float = 0.0, clip: Rect | None = None,
                   antialias: bool | None = None, clip_ellipse: Rect | None = None, flip_h: bool = False, flip_v: bool = False) -> None:
        self.p.save()
        if clip is not None:
            self.p.setClipRect(_qrect(clip))
        if clip_ellipse is not None:
            pfad = QPainterPath()
            pfad.addEllipse(_qrect(clip_ellipse))
            self.p.setClipPath(pfad, Qt.IntersectClip)
        if antialias is not None:
            self.p.setRenderHint(QPainter.Antialiasing, antialias)
        self.p.setOpacity(self.p.opacity() * opacity)
        if translate is not None:
            self.p.translate(translate.x, translate.y)
        if rotate:
            self.p.rotate(rotate)
        if flip_h or flip_v:
            self.p.scale(-1.0 if flip_h else 1.0, -1.0 if flip_v else 1.0)

    def pop_state(self) -> None:
        self.p.restore()

    def draw_image(self, data: bytes, rect: Rect, smooth: bool = False, wash: float = 0.0, source_rect: Rect | None = None) -> None:
        from lunivo_writer.core.document.bildformat import format_erkennen
        fmt = format_erkennen(data[:2048]) if data else None
        if fmt == "svg" and source_rect is None:
            from PySide6.QtSvg import QSvgRenderer
            from lunivo_writer.editor.objekte import bilddaten as BD
            rd = QSvgRenderer(QByteArray(BD.svg_bereinigen(data)))
            if rd.isValid():
                rd.render(self.p, _qrect(rect))
            return
        if fmt in ("emf", "wmf") and source_rect is None:
            from lunivo_writer.dienste import vektor_bilder as V
            if (V.emf_zeichnen if fmt == "emf" else V.wmf_zeichnen)(data, self.p, _qrect(rect)):
                return
        img = _bild(data)
        if not img.isNull():
            if smooth:
                self.p.setRenderHint(QPainter.SmoothPixmapTransform)
            if wash > 0:
                img = _ausgewaschen(img, wash)
            if source_rect is None:
                self.p.drawImage(_qrect(rect), img)
            else:
                x = max(0.0, min(1.0, source_rect.x))
                y = max(0.0, min(1.0, source_rect.y))
                w = max(0.0, min(1.0 - x, source_rect.width))
                h = max(0.0, min(1.0 - y, source_rect.height))
                if w > 0 and h > 0:
                    quelle = QRectF(x * img.width(), y * img.height(), w * img.width(), h * img.height())
                    self.p.drawImage(_qrect(rect), img, quelle)

    def apply_image_effects(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> tuple[bytes, bool]:
        from lunivo_writer.editor.objekte import bildeffekte as E
        img, r = _bild(data), _qrect(rect)
        if effects.get("weich"):
            img = E.weiche_kanten(img, r, ellipse, float(effects["weich"].get("radius", 6.0)))
        if E.hat_nachbearbeitung(effects):
            return _png(E.bild_nachbearbeiten(img, r, ellipse, effects)), False
        return (_png(img) if effects.get("weich") else data), ellipse

    def draw_effects_behind(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> None:
        from lunivo_writer.editor.objekte import bildeffekte as E
        E.unter_zeichnen(self.p, _bild(data), _qrect(rect), ellipse, effects)

    def draw_text_effects(self, text: str, font, origin: Point, color: tuple, effects: dict | None, contour: dict | None, highlight: tuple | None,
                          width: float, line_height: float, ascent: float, underline: bool = False) -> None:
        from lunivo_writer.editor.text import textfx
        f, p = _qfont(font), self.p
        farbe = QColor(*color)
        pfad, gl = textfx.text_pfad(text, f, QPointF(origin.x, origin.y))
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        if highlight:
            p.fillRect(QRectF(origin.x, origin.y - ascent, width, line_height), QColor(*highlight))
        if farbe.alpha() > 0:
            p.fillPath(pfad, farbe)
        if contour:
            p.strokePath(pfad, QPen(QColor(contour["farbe"]), contour["breite"], Qt.PenStyle(contour.get("stil", 1))))
        if effects:
            kontur = None
            if "kontur_verlauf" in effects or effects.get("kontur_form", "einfach") != "einfach":
                kontur = (QColor(effects.get("kontur_farbe", "#000000")), max(0.1, effects.get("kontur_breite", 0.75)) * 96 / 72,
                          effects.get("kontur_form", "einfach"), effects.get("kontur_art", "einfach"))
            textfx.fx_zeichnen(p, pfad, effects, gl, f.pixelSize(), farbe if farbe.alpha() else QColor("black"), kontur)
        if underline:
            p.setPen(QPen(farbe, 1))
            p.drawLine(QPointF(origin.x, origin.y + 2), QPointF(origin.x + width, origin.y + 2))
        p.restore()

    def draw_text_path(self, text: str, font, origin: Point, style: Style) -> None:
        pf = QPainterPath()
        pf.addText(origin.x, origin.y, _qfont(font), text)
        self.p.save()
        self.p.setRenderHint(QPainter.Antialiasing)
        self.p.setPen(self._stift(style) if style.width > 0 else Qt.NoPen)
        self.p.setBrush(_pinsel(style) if style.filled else Qt.NoBrush)
        self.p.drawPath(pf)
        self.p.restore()

    def draw_shadow(self, ops: list, color: tuple, blur: float, dx: float, dy: float) -> None:
        from lunivo_writer.editor.objekte import bildeffekte as E
        pf = self._vereinigt(self._pfade(ops), False)
        grenzen = pf.boundingRect()
        rand = int(blur * 2) + 2
        w, h = max(1, int(grenzen.width()) + 2 * rand), max(1, int(grenzen.height()) + 2 * rand)
        img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        q = QPainter(img)
        q.setRenderHint(QPainter.Antialiasing)
        q.translate(rand - grenzen.x(), rand - grenzen.y())
        q.fillPath(pf, QColor(*color))
        q.end()
        if blur > 0:
            img = E._weich(img, blur)
        self.p.drawImage(QPointF(grenzen.x() - rand + dx, grenzen.y() - rand + dy), img)

    def draw_line(self, start: Point, end: Point, style: Style) -> None:
        self.p.save()
        self.p.setPen(self._stift(style))
        self.p.drawLine(QPointF(start.x, start.y), QPointF(end.x, end.y))
        self.p.restore()
