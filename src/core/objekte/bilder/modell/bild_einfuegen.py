"""Bild einfuegen: aus ``core.bearbeitung.einfuegen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from core.formatierung.farben.farben import Farbe


def qimage_einfuegen(ed, img: QImage, alt: str = "", art: str | None = None, daten: dict | None = None) -> None:
    """Bild an der Schreibmarke einfügen. art/daten (Form, WordArt, Diagramm, …) bleiben am Bild, damit es sich wieder bearbeiten
    lässt; „Zeichnungsobjekte drucken“ kann solche Bilder weglassen."""
    ed.bild_im_text_einfuegen(img, alt, art, daten)


# ---- Piktogramm -------------------------------------------------------------------------------------------------------
def piktogramm_bild(name: str, px: int = 96, farbe: str = "#1f2328") -> QImage:
    from vcl.qt.widgets.bausteine.symbole.piktogramme import piktogramme
    return piktogramme.katalog_bild(name, px, farbe, 1.7 if px < 128 else 1.5)


# ---- Objekt als Symbol ----------------------------------------------------------------------------------------------------------
def datei_symbol_bild(name: str, symbol: QImage, breite: int = 120) -> QImage:
    """Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen); Name und Zusammensetzung zeichnet der Kern."""
    from vcl.qt.rendering.formen.anzeige import kern_bild
    from core.geometrie import Point, Rect
    from core.layout.drucklayout.ausgabe.backend import Style, rgba
    from core.layout.drucklayout.ausgabe.bild.bildeffekte import png_bytes
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    f = FontSpec("Liberation Sans", 9.0)
    zeile = name
    if engine.measure_text(zeile, f) > breite - 8:                           # in der Mitte kürzen, bis der Name passt
        rest, links, rechts = name, 0, 0
        while len(rest) > 2 and engine.measure_text(name[:links + 1] + "…" + name[len(name) - rechts:], f) <= breite - 8:
            if links <= rechts:
                links += 1
            else:
                rechts += 1
        zeile = name[:links] + "…" + (name[len(name) - rechts:] if rechts else "")
    m = engine.font_metrics(f)
    sym = symbol.convertToFormat(QImage.Format_RGBA8888)
    png = png_bytes(sym.width(), sym.height(), bytes(sym.constBits()))
    b, h = breite, symbol.height() + 12 + int(m.line_spacing)

    def zeichnen(z) -> None:
        z.draw_image(png, Rect((breite - symbol.width()) // 2, 4, symbol.width(), symbol.height()), smooth=True)
        z.draw_text(zeile, Point((breite - engine.measure_text(zeile, f)) / 2, symbol.height() + 8 + m.ascent), f, Style(color=rgba(Farbe.TINTE_DUNKEL)))
    return kern_bild(b, h, zeichnen)


# ---- Bild bearbeiten (Farbe, Zuschneiden, Drehen) -----------------------------------------------------------------------
def bild_ersetzen(ed, wandle) -> bool:
    """wandle(QImage) → QImage; das Bild im Text wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, Seitenverhältnis folgt)."""
    o = ed.inline_gewaehlt()
    if o is None:
        return False
    img = ed.bild_ressource(o.ressource)
    if img is None or img.isNull():
        return False
    neu = wandle(QImage(img))
    if neu is None or neu.isNull():
        return False
    faktor = (o.breite / img.width()) if o.breite and img.width() else 1.0
    orig = o.daten.get("orig") or o.ressource
    return ed.inline_aendern(o.id, ressource=ed.bild_ressource_neu(neu), breite=neu.width() * faktor, hoehe=neu.height() * faktor, daten={**o.daten, "orig": orig})


def bild_original(ed) -> bool:
    o = ed.inline_gewaehlt()
    if o is None or not o.daten.get("orig"):
        return False
    img, alt = ed.bild_ressource(o.daten["orig"]), ed.bild_ressource(o.ressource)
    if img is None:
        return False
    faktor = (o.breite / alt.width()) if o.breite and alt is not None and alt.width() else 1.0
    daten = {k: v for k, v in o.daten.items() if k != "orig"}
    return ed.inline_aendern(o.id, ressource=o.daten["orig"], breite=img.width() * faktor, hoehe=img.height() * faktor, daten=daten)


def farbe_anwenden(img: QImage, modus: str) -> QImage:
    if modus in ("Graustufen", "Sepia", "Schwarzweiß"):
        g = img.convertToFormat(QImage.Format_Grayscale8).convertToFormat(QImage.Format_ARGB32)
        if modus == "Sepia":
            p = QPainter(g)
            p.setCompositionMode(QPainter.CompositionMode_Multiply)
            p.fillRect(g.rect(), QColor("#d9b98a"))
            p.end()
            return g
        if modus == "Schwarzweiß":
            return img.convertToFormat(QImage.Format_Mono, Qt.ThresholdDither).convertToFormat(QImage.Format_ARGB32)
        return g
    if modus in ("Heller", "Dunkler"):
        out = img.convertToFormat(QImage.Format_ARGB32)
        p = QPainter(out)
        farbe = QColor(255, 255, 255, 70) if modus == "Heller" else QColor(0, 0, 0, 70)
        p.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        p.fillRect(out.rect(), farbe)
        p.end()
        return out
    return img


def zuschneiden(img: QImage, links: int, oben: int, rechts: int, unten: int) -> QImage:
    r = QRectF(links, oben, img.width() - links - rechts, img.height() - oben - unten).toRect()
    return img.copy(r) if r.width() > 0 and r.height() > 0 else img


def drehen(img: QImage, art: str) -> QImage:
    from PySide6.QtGui import QTransform
    if art == "rechts":
        return img.transformed(QTransform().rotate(90))
    if art == "links":
        return img.transformed(QTransform().rotate(-90))
    if art in ("horizontal", "vertikal"):
        from core.objekte.bilder.modell.bildeffekte import gespiegelt
        return gespiegelt(img, waagrecht=art == "horizontal", senkrecht=art == "vertikal")
    return img
