"""Kopf- und Fußzeilen, Seitenschmuck und Druckseiten-Auswahl."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat

from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.kern.farben import Farbe
from lunivo_writer.modelle.seite import PageSettings, mm_to_px


def _expand(text: str, n: int, total: int, page: PageSettings | None = None, kapitel: str = "") -> str:
    from lunivo_writer.editor.seite import seitenzahl as SZ
    return SZ.text(text, n, total, page, kapitel)


def _draw_hf(p: QPainter, hf, rect: QRectF, n: int, total: int, base: QFont, page: PageSettings | None = None, kapitel: str = "") -> None:
    """Kopf- oder Fußzeile einer Seite; ``n`` ist die angezeigte Seitennummer (bestimmt auch „außen“/„innen“)."""
    if hf.is_empty():
        return
    from PySide6.QtGui import QColor
    from lunivo_writer.editor.seite import seitenzahl as SZ
    fmt = getattr(hf, "fmt", None) or {}
    if _laeufe_eigen(hf):
        _zeichne_laeufe(p, hf, rect, n, total, base, page, kapitel)
        return
    f = _hf_schrift(base, fmt)
    if fmt.get("script") in ("sup", "sub"):                      # hoch-/tiefgestellt: nach oben bzw. unten gerückt
        px = _hf_schrift(base, {k: v for k, v in fmt.items() if k != "script"}).pixelSize()
        rect = rect.translated(0, -px * 0.25 if fmt["script"] == "sup" else px * 0.15)
    p.save()
    p.setFont(f)
    if fmt.get("color"):
        p.setPen(QColor(fmt["color"]))
    ausrichtung = SZ.ausrichtung(hf.align, n)
    flag = {"center": Qt.AlignHCenter, "right": Qt.AlignRight}.get(ausrichtung, Qt.AlignLeft)
    text = _expand(hf.text, n, total, page, kapitel)
    if fmt.get("effekt") or fmt.get("kontur"):
        _hf_effekt(p, fmt, f, rect, text, flag)
    else:
        from lunivo_writer.adapter.qt.rendering import QtRenderBackend
        from lunivo_writer.core.geometry import Rect
        from lunivo_writer.core.rendering import Style
        ziel = Rect(rect.x(), rect.y(), rect.width(), rect.height())
        ausr = ausrichtung if ausrichtung in ("center", "right") else "left"
        backend = QtRenderBackend(p)
        if fmt.get("highlight"):                                 # Hervorheben: Farbe hinter dem Text
            flaeche = backend.text_bounds(text, ziel, f, ausr)
            backend.draw_rect(flaeche, Style(color=QColor(fmt["highlight"]).getRgb(), width=0, filled=True))
        farbe = QColor(fmt["color"]) if fmt.get("color") else p.pen().color()
        backend.draw_text_box(text, ziel, f, Style(color=farbe.getRgb()), align=ausr)
    p.restore()


def _hf_schrift(base: QFont, fmt: dict) -> QFont:
    """Schrift einer Kopf-/Fußzeile aus einem Zeichenformat (``HeaderFooter.fmt``)."""
    f = QFont(base)
    f.setPixelSize(13)
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
    if fmt.get("script") in ("sup", "sub"):
        f.setPixelSize(max(1, round(f.pixelSize() * 0.65)))
    return f


def _laeufe_eigen(hf) -> bool:
    """Hat die Zeile eigene Textstücke mit Format, die den Text ergeben? Texteffekte hängen an der ganzen Zeile: dann bleibt es beim alten Weg."""
    if not hf.runs or "".join(r.get("text", "") for r in hf.runs) != hf.text:
        return False
    return not any(((r.get("fmt") or {}).get("effekt") or (r.get("fmt") or {}).get("kontur")) for r in hf.runs)


def _zeichne_laeufe(p: QPainter, hf, rect: QRectF, n: int, total: int, base: QFont, page: PageSettings | None, kapitel: str) -> None:
    """Kopf-/Fußzeile Stück für Stück: jedes Textstück in seiner Schrift und Farbe, Zeile für Zeile ausgerichtet."""
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QFontMetricsF
    from lunivo_writer.editor.seite import seitenzahl as SZ
    zeilen: list = [[]]
    for text, fmt in hf.laeufe():
        for k, teil in enumerate(_expand(text, n, total, page, kapitel).split("\n")):
            if k:
                zeilen.append([])
            if teil:
                zeilen[-1].append((teil, fmt or {}))
    satz = []                                                       # je Zeile: (Stücke, Zeilenhöhe, Grundlinie, Breite)
    for zeile in zeilen:
        stuecke, hoch, steig = [], 0.0, 0.0
        for teil, fmt in zeile:
            f = _hf_schrift(base, fmt)
            fm = QFontMetricsF(f)
            stuecke.append((teil, f, fmt, fm.horizontalAdvance(teil)))
            hoch, steig = max(hoch, fm.height()), max(steig, fm.ascent())
        if not stuecke:                                             # leere Zeile: Höhe der Zeilenschrift
            fm = QFontMetricsF(_hf_schrift(base, hf.fmt or {}))
            hoch, steig = fm.height(), fm.ascent()
        satz.append((stuecke, hoch, steig, sum(s[3] for s in stuecke)))
    y = rect.center().y() - sum(z[1] for z in satz) / 2
    ausrichtung = SZ.ausrichtung(hf.align, n)
    p.save()
    for stuecke, hoch, steig, breite in satz:
        if ausrichtung == "center":
            x = rect.center().x() - breite / 2
        elif ausrichtung == "right":
            x = rect.right() - breite
        else:
            x = rect.left()
        for teil, f, fmt, w in stuecke:
            if fmt.get("highlight"):
                p.fillRect(QRectF(x, y, w, hoch), QColor(fmt["highlight"]))
            p.setFont(f)
            farbe = fmt.get("color") or (hf.fmt or {}).get("color")
            if farbe:
                p.setPen(QColor(farbe))
            p.drawText(QPointF(x, y + steig), teil)
            x += w
        y += hoch
    p.restore()


def _hf_effekt(p: QPainter, fmt: dict, f: QFont, rect: QRectF, text: str, flag) -> None:
    """Zeilen mit Texteffekt (Schatten, Spiegelung, Leuchten, Kontur …) zeichnen: dieselben Bausteine wie im Dokument (``editor/text/textfx.py``), über das Rendering-Backend."""
    from PySide6.QtGui import QFontMetricsF
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.geometry import Point
    from lunivo_writer.editor.text import textfx
    fm = QFontMetricsF(f)
    zeilen = text.split("\n")
    farbe = QColor(fmt["color"]) if fmt.get("color") else QColor(p.pen().color())
    fx = textfx.aus_text(fmt.get("effekt"))
    k = fmt.get("kontur")
    y = rect.center().y() - fm.lineSpacing() * len(zeilen) / 2 + fm.ascent()
    rb = QtRenderBackend(p)
    for zeile in zeilen:
        w = fm.horizontalAdvance(zeile)
        x = rect.left() + (rect.width() - w) / 2 if flag & Qt.AlignHCenter else rect.right() - w if flag & Qt.AlignRight else rect.left()
        rb.draw_text_effects(zeile, f, Point(x, y), farbe.getRgb(), fx or None, k, QColor(fmt["highlight"]).getRgb() if fmt.get("highlight") else None,
                             w, fm.lineSpacing(), fm.ascent(), f.underline())
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
        stuecke = [(f.position(), f.position() + f.length()) for f in absatz_fragmente(b)
                   if f.charFormat().background().style() != _Qt.NoBrush and not f.charFormat().isImageFormat()]
        for von, bis in stuecke:
            c = QTextCursor(d); c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
            fm = QTextCharFormat(); fm.setBackground(QBrush(_Qt.NoBrush)); c.mergeCharFormat(fm)
        b = b.next()


def _ohne_links(d: QTextDocument) -> None:
    """PDF ohne Hyperlinks: der Text bleibt, nur das Linkziel entfällt (Qt schreibt sonst für jedes Linkziel einen PDF-Link)."""
    from PySide6.QtGui import QTextCursor
    b = d.firstBlock()
    while b.isValid():
        stuecke = [(f.position(), f.position() + f.length(), f.charFormat()) for f in absatz_fragmente(b) if f.charFormat().anchorHref()]
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
        for f in absatz_fragmente(b):
            if f.charFormat().isAnchor() and not f.charFormat().anchorHref():
                for n in f.charFormat().anchorNames():
                    v, e = stellen.get(n, (f.position(), f.position() + f.length()))
                    stellen[n] = (min(v, f.position()), max(e, f.position() + f.length()))
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
    """Seitenfarbe, Seitenrahmen und Wasserzeichen. Koordinaten: Seite in 96-dpi-Bildpunkten, Ursprung links oben. ``flaeche`` (QRectF) überschreibt das Seitenrechteck — der Editor
    zeichnet damit jede Seite einzeln. Die Schichten rechnet ``core/rendering/seitenschmuck.py``."""
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.geometry import Rect
    from lunivo_writer.core.rendering.seitenschmuck import zeichne_seitenschmuck
    from lunivo_writer.dienste.textsatz import standard_engine
    r = Rect(flaeche.x(), flaeche.y(), flaeche.width(), flaeche.height()) if flaeche is not None else None
    zeichne_seitenschmuck(QtRenderBackend(p), standard_engine(), page, hintergrund, r, rahmen, wasserzeichen)


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


def frei_zeichnen(p: QPainter, objekte: list, hinter: bool) -> None:
    """Freie Bilder der Seite hinter oder vor dem Text (zum Beispiel ein Band im Briefkopf, Foto, Unterschrift)."""
    from lunivo_writer.editor.objekte import freie_bilder as FB
    for a, bild, r in FB.vorne_hinten(objekte, hinter):
        FB.bild_zeichnen(p, bild, r, bool(a.get("ellipse")), a.get("rand"), float(a.get("dreh", 0.0)), a.get("fuell"),
                         a.get("_fuellbild") or (a.get("fuell") or {}).get("bild"), a.get("fx"))


def _druckmarken(p: QPainter, page: PageSettings, grenzen: bool, zuschnitt: bool) -> None:
    """Textbegrenzungen (gestrichelter Rahmen um die Textfläche) und Zuschnittsmarken (Ecken) auf der gedruckten Seite."""
    cw, ch = page.content_width_px, page.content_height_px
    ml, mt = mm_to_px(page.margin_left_mm), mm_to_px(page.margin_top_mm)
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.geometry import Point as _Pt, Rect as _Rect
    from lunivo_writer.core.rendering import Style as _Style
    rb = QtRenderBackend(p)
    grau = (0x88, 0x88, 0x88, 255)
    if grenzen:
        rb.draw_rect(_Rect(ml, mt, cw, ch), _Style(color=grau, width=0.7, dashed=True))
    if zuschnitt:
        stil = _Style(color=grau, width=0.7)
        l = mm_to_px(4)
        for x, y, dx, dy in ((ml, mt, -1, -1), (ml + cw, mt, 1, -1), (ml, mt + ch, -1, 1), (ml + cw, mt + ch, 1, 1)):
            rb.draw_line(_Pt(x + dx * 2, y), _Pt(x + dx * (2 + l), y), stil)
            rb.draw_line(_Pt(x, y + dy * 2), _Pt(x, y + dy * (2 + l)), stil)


RAND_SPIEL = 1.0             # Bildpunkte: so weit darf eine Zeile der Nachbarseite in den Ausschnitt ragen, ohne mitgezeichnet zu werden
                             # (sonst stünde sie unsichtbar ein zweites Mal im PDF und käme beim Suchen und Kopieren doppelt)


def _inhalt_zeichnen(p: QPainter, d: QTextDocument, rect: QRectF) -> None:
    """Wie ``QTextDocument.drawContents``, aber mit schwarzer Grundschrift: Text ohne eigene Farbe nähme sonst die Textfarbe des
    Programms — im dunklen Thema fast weiß, und das Papier (PDF, Druck) bekäme blasse Schrift."""
    from PySide6.QtGui import QAbstractTextDocumentLayout, QPalette
    ctx = QAbstractTextDocumentLayout.PaintContext()
    pal = QPalette(ctx.palette)
    pal.setColor(QPalette.Text, QColor(Farbe.SCHWARZ)); pal.setColor(QPalette.WindowText, QColor(Farbe.SCHWARZ))
    ctx.palette = pal
    p.save()
    p.setClipRect(rect)
    ctx.clip = rect.adjusted(0, RAND_SPIEL, 0, -RAND_SPIEL)     # Zeilen, die die Seite nur am Rand berühren, gehören zur Nachbarseite
    d.documentLayout().draw(p, ctx)
    p.restore()


def absatz_zusatz_zeichnen(p: QPainter, d: QTextDocument, faktor: float = 1.0) -> None:
    """Was an den Absätzen nicht von Qt kommt: Rahmen und die Nummern mehrstufiger Listen."""
    from lunivo_writer.editor.text.mehrstufig import nummern_zeichnen
    from lunivo_writer.editor.text.tabfuell import zeichnen as tabfuell_zeichnen
    from lunivo_writer.editor.text.textfx import absaetze_zeichnen as effekte_zeichnen
    absatzrahmen_zeichnen(p, d, faktor)
    effekte_zeichnen(p, d)
    nummern_zeichnen(p, d, faktor)
    tabfuell_zeichnen(p, d)


def _rahmengruppen(d: QTextDocument) -> list[list]:
    """[[Rahmenangabe, [Absätze], Nummer des letzten Absatzes]]: zusammenhängende sichtbare Absätze mit gleichem B_RAHMEN."""
    from lunivo_writer.editor.dokument.je_stand import je_stand
    return je_stand(d, "_rahmengruppen", _rahmengruppen_bauen)


def _rahmengruppen_bauen(d: QTextDocument) -> list[list]:
    from lunivo_writer.editor.dokument.zusatz import B_RAHMEN
    gruppen: list[list] = []
    b = d.firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_RAHMEN) and b.isVisible():
            w = b.blockFormat().stringProperty(B_RAHMEN)
            if gruppen and gruppen[-1][0] == w and gruppen[-1][2] == b.blockNumber() - 1:
                gruppen[-1][1].append(b); gruppen[-1][2] = b.blockNumber()
            else:
                gruppen.append([w, [b], b.blockNumber()])
        b = b.next()
    return gruppen


def _rahmenrechteck(r: QRectF, linie, faktor: float, polster: float) -> QRectF:
    """Rechteck des Rahmens: Absatzfläche plus Abstand (eigener Abstand der Linie in pt, sonst ``polster``)."""
    eigen = linie.polster()
    if eigen:                                                      # eigener Abstand (Rahmen und Schattierung ▸ Optionen), pt → Bildpunkte
        o, u, l, rt = (x * 96 / 72 * faktor for x in eigen)
        return r.adjusted(-l, -o, rt, u)
    pd = polster * faktor
    return r.adjusted(-pd, -pd + 1, pd, pd - 1)


def absatzrahmen_zeichnen(p: QPainter, d: QTextDocument, faktor: float = 1.0, polster: float = 4.0) -> None:
    """Rahmen um zusammenhängende Absätze mit gleichem B_RAHMEN. Koordinaten: Dokument (Layoutgerät); faktor = Zoom."""
    from lunivo_writer.editor.objekte.linie import Linie
    lay = d.documentLayout()
    for w, bloecke, _n in _rahmengruppen(d):
        linie = Linie.aus_text(w)
        if linie is None:
            continue
        r = lay.blockBoundingRect(bloecke[0]).united(lay.blockBoundingRect(bloecke[-1]))
        zwischen = [(lay.blockBoundingRect(x).bottom() + lay.blockBoundingRect(y).top()) / 2
                    for x, y in zip(bloecke, bloecke[1:])]
        linie.rahmen_zeichnen(p, _rahmenrechteck(r, linie, faktor, polster), 96 / 72 * faktor, zwischen)
