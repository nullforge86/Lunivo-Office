"""Bild einfuegen: aus ``vcl.qt.rendering.formen.einfuegen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import BILDVORLAGE_DUNKEL, BILDVORLAGE_HELL


def qimage_einfuegen(ed, img: QImage, alt: str = "", art: str | None = None, daten: dict | None = None) -> None:
    """Bild an der Schreibmarke einfügen. art/daten (Form, WordArt, Diagramm, …) bleiben am Bild, damit es sich wieder bearbeiten
    lässt; „Zeichnungsobjekte drucken“ kann solche Bilder weglassen."""
    ed.bild_im_text_einfuegen(img, alt, art, daten)


# ---- Piktogramm -------------------------------------------------------------------------------------------------------
def piktogramm_bild(name: str, px: int = 96, farbe: str = Farbe.PIKTOGRAMM) -> QImage:
    from vcl.qt.widgets.bausteine.symbole.piktogramme import piktogramme
    return piktogramme.katalog_bild(name, px, farbe, 1.7 if px < 128 else 1.5)


# ---- Objekt als Symbol ----------------------------------------------------------------------------------------------------------
def datei_symbol_bild(name: str, symbol: QImage, breite: int = 120) -> QImage:
    """Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen); Name und Zusammensetzung zeichnet der Kern."""
    from writer.anbindung import zeichnen as ZW
    sym = symbol.convertToFormat(QImage.Format_RGBA8888)
    b, h, roh = ZW.datei_symbol(name, (sym.width(), sym.height(), bytes(sym.constBits())), breite, Farbe.TINTE_DUNKEL)
    return QImage(roh, b, h, b * 4, QImage.Format_RGBA8888).copy()


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
            p.fillRect(g.rect(), QColor(Farbe.HOLZ))
            p.end()
            return g
        if modus == "Schwarzweiß":
            return img.convertToFormat(QImage.Format_Mono, Qt.ThresholdDither).convertToFormat(QImage.Format_ARGB32)
        return g
    if modus in ("Heller", "Dunkler"):
        out = img.convertToFormat(QImage.Format_ARGB32)
        p = QPainter(out)
        farbe = QColor(*BILDVORLAGE_HELL) if modus == "Heller" else QColor(*BILDVORLAGE_DUNKEL)
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
        from vcl.qt.rendering.formen.bildeffekte import gespiegelt
        return gespiegelt(img, waagrecht=art == "horizontal", senkrecht=art == "vertikal")
    return img
