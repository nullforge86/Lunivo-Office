"""Eine Seite aus dem Ergebnis des Qt-freien Seitenumbruchs (``core.layout.umbrechen``) auf ein ``RenderBackend`` zeichnen: Seitenfarbe, Tabellenzellen (Füllung, Rahmen), Absatzzeilen mit
Läufen (Schrift, Farbe, Unterstreichen, Hervorheben, Bilder in der Zeile), Aufzählungszeichen und Fußnoten. Alle Maße kommen aus dem Layout; hier wird nur gezeichnet."""
from __future__ import annotations

import json

from lunivo_writer.core.document.objekte import P_BILDANKER, ImageObject
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.layout.objekte import objekt_rechteck
from lunivo_writer.core.layout.seitenumbruch import Ergebnis
from lunivo_writer.core.rendering.backend import RenderBackend, Style, rgba
from lunivo_writer.core.rendering.objekte import zeichne_bild
from lunivo_writer.core.rendering.tabelle import ausfuehren, zelle_anweisungen
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine
from lunivo_writer.core.textlayout.hb_engine import LEERZEICHEN
from lunivo_writer.core.textlayout.paragraph import Absatzsatz, Objekt


def zeichne_zeile(b: RenderBackend, satz: Absatzsatz, zeile: int, rect: Rect) -> None:
    """Zeile ``zeile`` des gesetzten Absatzes; ``rect`` = ihr Rechteck auf der Seite (Oberkante der Zeile, linker Rand der Spalte)."""
    z = satz.zeilen[zeile]
    grundlinie = rect.y + z.box.ascent
    for lauf in satz.laeufe:
        start, ende = max(lauf.start, z.box.start), min(lauf.ende, z.ende)
        if start >= ende:
            continue
        x = rect.x + satz.cursor_x(start, zeile)
        if isinstance(lauf.schrift, Objekt):
            bild = lauf.stil.get("bild")
            if bild:
                b.draw_image(bild, Rect(x, grundlinie - lauf.schrift.hoehe, lauf.schrift.breite, lauf.schrift.hoehe), smooth=True)
            continue
        text = satz.text[start:ende]
        breite = satz.cursor_x(ende, zeile) - satz.cursor_x(start, zeile)
        farbe = lauf.stil.get("color") or (0, 0, 0, 255)
        if lauf.stil.get("highlight"):
            b.draw_rect(Rect(x, rect.y, breite, z.box.height), Style(color=lauf.stil["highlight"], width=0, filled=True))
        if z.wort_zuschlag:                                           # Blocksatz: Wort für Wort, die Lücken sind breiter
            i = start
            for wort in _woerter(text):
                if wort.strip(" \t"):
                    b.draw_text(wort, Point(rect.x + satz.cursor_x(i, zeile), grundlinie), lauf.schrift, Style(color=farbe))
                i += len(wort)
        else:
            b.draw_text(text.replace("\n", "").replace(" ", ""), Point(x, grundlinie), lauf.schrift, Style(color=farbe))
        if lauf.stil.get("underline"):
            b.draw_line(Point(x, grundlinie + 2), Point(x + breite, grundlinie + 2), Style(color=farbe, width=1.0))
        if lauf.stil.get("strike"):
            b.draw_line(Point(x, grundlinie - z.box.ascent / 3), Point(x + breite, grundlinie - z.box.ascent / 3), Style(color=farbe, width=1.0))


def _woerter(text: str) -> list[str]:
    """Der Text in Wörter und Leerzeichen-Folgen (zusammen ergeben sie den Text)."""
    aus, aktuell, leer = [], "", None
    for c in text:
        ist_leer = c in LEERZEICHEN
        if leer is not None and ist_leer != leer:
            aus.append(aktuell)
            aktuell = ""
        aktuell += c
        leer = ist_leer
    if aktuell:
        aus.append(aktuell)
    return aus


def zeichne_marke(b: RenderBackend, engine: TextLayoutEngine, satz: Absatzsatz, marke: str, rect: Rect) -> None:
    """Aufzählungszeichen oder Nummer links vor der ersten Zeile (wie bei Qt: Zeichen als Form, Nummer als Text)."""
    if not satz.laeufe or not satz.zeilen:
        return
    erste = next((lauf for lauf in satz.laeufe if isinstance(lauf.schrift, FontSpec)), None)
    if erste is None:
        return
    m = engine.font_metrics(erste.schrift)
    farbe = erste.stil.get("color") or (0, 0, 0, 255)
    x, grundlinie = rect.x + satz.zeilen[0].x, rect.y + satz.zeilen[0].box.ascent
    if marke in ("•", "◦", "▪"):
        d = (m.ascent + m.descent) / 3.0
        mx, my = x - d * 1.8, grundlinie - m.ascent / 2.4
        stil = Style(color=farbe, width=1.0, filled=marke != "◦")
        if marke == "▪":
            b.draw_rect(Rect(mx - d / 2, my - d / 2, d, d), stil)
        else:
            b.draw_ellipse(Point(mx, my), d / 2, d / 2, stil)
    else:
        b.draw_text(marke, Point(x - engine.measure_text(marke + " ", erste.schrift), grundlinie), erste.schrift, Style(color=farbe))


def zeichne_freie_bilder(b: RenderBackend, dok, erg: Ergebnis, index: int, hinter: bool) -> None:
    """Die frei positionierten Bilder (und Formen als Bilder) der Absätze, die auf dieser Seite beginnen: ``hinter`` = die hinter dem Text, sonst die davor. Lage über ``core.layout.objekte``."""
    from lunivo_writer.core.editing import absatz_bei
    seite = erg.seiten[index]
    einr = seite.einrichtung
    if einr is None:
        return
    ml, mt = einr.margin_left_mm * 96 / 25.4, einr.margin_top_mm * 96 / 25.4
    bw, bh = einr.width_mm * 96 / 25.4, einr.height_mm * 96 / 25.4
    cb, ch = einr.content_width_px, einr.content_height_px
    for p in seite.plaetze:
        if p.art != "zeile" or p.zeile != 0:
            continue
        roh = absatz_bei(dok, p.pfad).format.properties.get(P_BILDANKER)
        if not isinstance(roh, str):
            continue
        try:
            angaben = json.loads(roh)
        except ValueError:
            continue
        for a in angaben if isinstance(angaben, list) else []:
            if bool(a.get("hinter")) != hinter or a.get("n") not in dok.media:
                continue
            bild = dok.media[a["n"]]
            obj = ImageObject.aus_angabe(a, bild.original if bild.original_format == "svg" else bild.raster_png)
            r = objekt_rechteck(obj.anchor, obj.width, obj.height, bw, bh, ml, mt, cb, ch, p.rect.y, p.rect.x, index + 1)
            fuell = dok.media.get((a.get("fuell") or {}).get("n", ""))
            zeichne_bild(b, obj, r, None, fuell.raster_png if fuell is not None else None)


def zeichne_seite(b: RenderBackend, erg: Ergebnis, index: int, engine: TextLayoutEngine, hintergrund: bool = True, dok=None) -> None:
    """Seite ``index`` des Layout-Ergebnisses: erst Seitenfarbe und Zellen (hinter dem Text), dann Zeilen, Aufzählungszeichen und Fußnoten."""
    seite = erg.seiten[index]
    einr = seite.einrichtung
    if hintergrund and getattr(einr, "color", None):
        pw, ph = einr.width_mm * 96 / 25.4, einr.height_mm * 96 / 25.4
        b.draw_rect(Rect(0, 0, pw, ph), Style(color=rgba(einr.color), width=0, filled=True))
    for p in seite.plaetze:
        if p.art == "zelle":
            zelle, tabelle = p.daten
            ausfuehren(b, zelle_anweisungen(p.rect, zelle, tabelle, float(tabelle.get("FrameBorder", 0.0) or 0.0), 1.0))
    if dok is not None:
        zeichne_freie_bilder(b, dok, erg, index, True)
    for p in seite.plaetze:
        if p.art == "zeile":
            ort = erg.absaetze[p.pfad]
            zeichne_zeile(b, ort.satz, p.zeile, p.rect)
            if p.zeile == 0 and ort.marke:
                zeichne_marke(b, engine, ort.satz, ort.marke, p.rect)
        elif p.art == "fussnote" and p.daten is not None:
            for i in range(len(p.daten.zeilen)):
                z = p.daten.zeilen[i]
                zeichne_zeile(b, p.daten, i, Rect(p.rect.x, p.rect.y + z.y, p.rect.width, z.hoehe))
    if dok is not None:
        zeichne_freie_bilder(b, dok, erg, index, False)


def zeichne_zeilennummern(b: RenderBackend, erg: Ergebnis, index: int, grund: FontSpec) -> None:
    """Zeilennummern links neben dem Text der Seite (kleine graue Schrift, rechtsbündig), wenn die Seiteneinrichtung ``zeilennummern`` verlangt."""
    einr = erg.seiten[index].einrichtung
    if einr is None or not getattr(einr, "zeilennummern", False):
        return
    klein = FontSpec(grund.family, 9 * 72 / 96, 400)
    links = einr.margin_left_mm * 96 / 25.4
    for seite, y, h, nr in erg.zeilennummern("seite" if getattr(einr, "zeilennummern_neu", "") == "seite" else ""):
        if seite == index:
            b.draw_text_box(str(nr), Rect(links - 48, y, 42, h), klein, Style(color=(160, 160, 164, 255)), align="right", wrap=False)
