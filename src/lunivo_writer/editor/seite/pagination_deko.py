"""Kopf- und Fußzeilen, Seitenschmuck und Druckseiten-Auswahl."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QFont, QPainter, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat

from lunivo_writer.core.farben import Farbe
from lunivo_writer.models.page import PageSettings, mm_to_px


def _expand(text: str, n: int, total: int, page: PageSettings | None = None, kapitel: str = "") -> str:
    from lunivo_writer.editor.seite import seitenzahl as SZ
    return SZ.text(text, n, total, page, kapitel)


def _draw_hf(p: QPainter, hf, rect: QRectF, n: int, total: int, base: QFont, page: PageSettings | None = None, kapitel: str = "") -> None:
    """Kopf- oder Fußzeile einer Seite; ``n`` ist die angezeigte Seitennummer (bestimmt auch „außen“/„innen“)."""
    if hf.is_empty():
        return
    from PySide6.QtGui import QColor
    from lunivo_writer.editor.seite import seitenzahl as SZ
    f = QFont(base)
    f.setPixelSize(13)
    fmt = getattr(hf, "fmt", None) or {}
    if fmt.get("family"):
        f.setFamily(fmt["family"])
    if fmt.get("size_pt"):
        f.setPixelSize(max(1, round(float(fmt["size_pt"]) * 96 / 72)))
    if "bold" in fmt:
        f.setBold(bool(fmt["bold"]))
    if "italic" in fmt:
        f.setItalic(bool(fmt["italic"]))
    if "underline" in fmt:
        f.setUnderline(bool(fmt["underline"]))
    if fmt.get("strike"):
        f.setStrikeOut(True)
    if fmt.get("script") in ("sup", "sub"):                      # hoch-/tiefgestellt: kleinere Schrift, nach oben bzw. unten gerückt
        px = f.pixelSize()
        f.setPixelSize(max(1, round(px * 0.65)))
        rect = rect.translated(0, -px * 0.25 if fmt["script"] == "sup" else px * 0.15)
    p.save()
    p.setFont(f)
    if fmt.get("color"):
        p.setPen(QColor(fmt["color"]))
    flag = {"center": Qt.AlignHCenter, "right": Qt.AlignRight}.get(SZ.ausrichtung(hf.align, n), Qt.AlignLeft)
    text = _expand(hf.text, n, total, page, kapitel)
    if fmt.get("effekt") or fmt.get("kontur"):
        _hf_effekt(p, fmt, f, rect, text, flag)
    else:
        fl = int(flag | Qt.AlignVCenter | Qt.TextWordWrap)
        if fmt.get("highlight"):                                 # Hervorheben: Farbe hinter dem Text
            p.fillRect(p.boundingRect(rect, fl, text), QColor(fmt["highlight"]))
        p.drawText(rect, fl, text)
    p.restore()


def _hf_effekt(p: QPainter, fmt: dict, f: QFont, rect: QRectF, text: str, flag) -> None:
    """Zeilen mit Texteffekt (Schatten, Spiegelung, Leuchten, Kontur …) zeichnen: dieselben Bausteine wie im Dokument (``editor/text/textfx.py``)."""
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QColor, QFontMetricsF, QPen
    from lunivo_writer.editor.text import textfx
    fm = QFontMetricsF(f)
    zeilen = text.split("\n")
    farbe = QColor(fmt["color"]) if fmt.get("color") else QColor(p.pen().color())
    fx = textfx.aus_text(fmt.get("effekt"))
    k = fmt.get("kontur")
    y = rect.center().y() - fm.lineSpacing() * len(zeilen) / 2 + fm.ascent()
    p.setRenderHint(QPainter.Antialiasing)
    for zeile in zeilen:
        w = fm.horizontalAdvance(zeile)
        x = rect.left() + (rect.width() - w) / 2 if flag & Qt.AlignHCenter else rect.right() - w if flag & Qt.AlignRight else rect.left()
        pfad, gl = textfx.text_pfad(zeile, f, QPointF(x, y))
        if fmt.get("highlight"):
            p.fillRect(QRectF(x, y - fm.ascent(), w, fm.lineSpacing()), QColor(fmt["highlight"]))
        if farbe.alpha() > 0:
            p.fillPath(pfad, farbe)
        if k:
            p.strokePath(pfad, QPen(QColor(k["farbe"]), k["breite"], Qt.PenStyle(k.get("stil", 1))))
        if fx:
            kontur = None
            if "kontur_verlauf" in fx or fx.get("kontur_form", "einfach") != "einfach":
                kontur = (QColor(fx.get("kontur_farbe", "#000000")), max(0.1, fx.get("kontur_breite", 0.75)) * 96 / 72,
                          fx.get("kontur_form", "einfach"), fx.get("kontur_art", "einfach"))
            textfx.fx_zeichnen(p, pfad, fx, gl, f.pixelSize(), farbe if farbe.alpha() else QColor("black"), kontur)
        if f.underline():
            p.setPen(QPen(farbe, 1)); p.drawLine(QPointF(x, y + 2), QPointF(x + w, y + 2))
        y += fm.lineSpacing()


def _ohne_hintergruende(d: QTextDocument) -> None:
    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QBrush, QTextCursor
    c = QTextCursor(d)
    c.select(QTextCursor.Document)
    f = QTextCharFormat(); f.setBackground(QBrush(_Qt.NoBrush)); c.mergeCharFormat(f)
    b = d.firstBlock()
    while b.isValid():
        bf = b.blockFormat()
        if bf.hasProperty(QTextFormat.BackgroundBrush):
            QTextCursor(b).setBlockFormat(_bf_ohne(bf))
        b = b.next()


def _text_schwarz(d: QTextDocument) -> None:
    """„Text schwarz drucken“ in der Kopie: jede Schriftfarbe wird schwarz (Verknüpfungen und Platzhalter eingeschlossen)."""
    from PySide6.QtGui import QBrush, QColor, QTextCursor
    c = QTextCursor(d)
    c.select(QTextCursor.Document)
    f = QTextCharFormat(); f.setForeground(QBrush(QColor(Farbe.SCHWARZ))); c.mergeCharFormat(f)


def _formularteile_ausblenden(d: QTextDocument, steuer: bool, platzhalter: bool) -> None:
    """Steuerelemente (Felder mit Wert, Schaltflächen, Kästchen) und/oder Platzhaltertexte leerer Felder werden in der Kopie unsichtbar."""
    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QBrush, QColor, QTextCursor
    from lunivo_writer.editor.dokument import formular as FO
    unsichtbar = QTextCharFormat()
    unsichtbar.setForeground(QBrush(QColor(0, 0, 0, 0)))
    unsichtbar.setBackground(QBrush(_Qt.NoBrush))
    unsichtbar.setUnderlineStyle(QTextCharFormat.NoUnderline)
    for v, e, m in FO.bereiche(d):
        if (m.get("leer") and platzhalter) or (not m.get("leer") and steuer):
            c = QTextCursor(d); c.setPosition(v); c.setPosition(e, QTextCursor.KeepAnchor); c.mergeCharFormat(unsichtbar)


def _ohne_hervorhebungen(d: QTextDocument) -> None:
    """Nur die Texthervorhebung (Marker) entfällt; Absatz- und Tabellenhintergründe bleiben."""
    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QBrush, QTextCursor
    b = d.firstBlock()
    while b.isValid():
        it = b.begin()
        stuecke = []
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().background().style() != _Qt.NoBrush and not f.charFormat().isImageFormat():
                stuecke.append((f.position(), f.position() + f.length()))
            it += 1
        for von, bis in stuecke:
            c = QTextCursor(d); c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
            fm = QTextCharFormat(); fm.setBackground(QBrush(_Qt.NoBrush)); c.mergeCharFormat(fm)
        b = b.next()


def _ohne_links(d: QTextDocument) -> None:
    """PDF ohne Hyperlinks: der Text bleibt, nur das Linkziel entfällt (Qt schreibt sonst für jedes Linkziel einen PDF-Link)."""
    from PySide6.QtGui import QTextCursor
    b = d.firstBlock()
    while b.isValid():
        it = b.begin()
        stuecke = []
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().anchorHref():
                stuecke.append((f.position(), f.position() + f.length(), f.charFormat()))
            it += 1
        for von, bis, fm in stuecke:
            fm.clearProperty(QTextCharFormat.AnchorHref)
            if not fm.anchorNames():
                fm.setAnchor(False)
            c = QTextCursor(d); c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor); c.setCharFormat(fm)
        b = b.next()


def _textmarken_klammern(d: QTextDocument) -> None:
    """„Textmarken drucken“: jede Textmarke steht in eckigen Klammern im Ausdruck."""
    from PySide6.QtGui import QTextCursor
    stellen = {}
    b = d.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().isAnchor() and not f.charFormat().anchorHref():
                for n in f.charFormat().anchorNames():
                    v, e = stellen.get(n, (f.position(), f.position() + f.length()))
                    stellen[n] = (min(v, f.position()), max(e, f.position() + f.length()))
            it += 1
        b = b.next()
    einfuegungen = sorted([(e, "]") for v, e in stellen.values()] + [(v, "[") for v, e in stellen.values()], reverse=True)
    for pos, z in einfuegungen:
        c = QTextCursor(d); c.setPosition(pos); c.insertText(z)


def _bf_ohne(bf):
    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QBrush
    bf.setBackground(QBrush(_Qt.NoBrush))
    return bf


def seitenschmuck(p: QPainter, page: PageSettings, hintergrund: bool = True, flaeche=None, rahmen: str = "immer", wasserzeichen: bool = True) -> None:
    """Seitenfarbe, Seitenrahmen und Wasserzeichen. Koordinaten: Seite in 96-dpi-Bildpunkten, Ursprung links oben.
    `flaeche` (QRectF) überschreibt das Seitenrechteck — der Editor zeichnet damit jede Seite einzeln."""
    from PySide6.QtCore import QRectF as _R
    from PySide6.QtGui import QColor, QPen
    pw, ph = mm_to_px(page.width_mm), mm_to_px(page.height_mm)
    r = flaeche or _R(0, 0, pw, ph)
    p.save()
    if hintergrund and page.color:
        p.fillRect(r, QColor(page.color))
    b = page.border
    # „Immer im Vordergrund anzeigen“: der Rahmen liegt über dem Text (``rahmen="vorn"``) oder dahinter (``"hinten"``); ``"immer"`` zeichnet ihn in jedem Fall
    if b and (rahmen == "immer" or (rahmen == "vorn") == bool(b.get("vordergrund", True))):
        from lunivo_writer.editor.seite import seitenrahmen
        seitenrahmen.zeichnen(p, b, page, QRectF(r))
    if wasserzeichen and page.watermark:
        from lunivo_writer.editor.seite import wasserzeichen as WZ
        WZ.zeichnen(p, page.watermark, r)
    p.restore()


def seiten_liste(total: int, first: int, last: int, opt: dict | None) -> list[int]:
    """Welche Seiten in welcher Reihenfolge gedruckt werden (Duplex, umgekehrte Reihenfolge)."""
    seiten = list(range(first, last + 1))
    opt = opt or {}
    duplex = opt.get("duplex", "alle")
    if duplex == "vorder":
        seiten = [n for n in seiten if n % 2 == 1]
    elif duplex == "rueck":
        seiten = [n for n in seiten if n % 2 == 0]
    if opt.get("umgekehrt"):
        seiten.reverse()
    return seiten


