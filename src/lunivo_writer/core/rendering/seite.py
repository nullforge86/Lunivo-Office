"""Eine Seite aus dem Ergebnis des Qt-freien Seitenumbruchs (``core.layout.umbrechen``) auf ein ``RenderTarget`` zeichnen: Seitenfarbe, Tabellenzellen (Füllung, Rahmen), Absatzzeilen mit
Läufen (Schrift, Farbe, Unterstreichen, Hervorheben, hoch-/tiefgestellt, Tabulatoren, Bilder in der Zeile), Rahmen, Absatzhintergrund, Aufzählungszeichen, Fuß- und Endnoten mit Trennstrich. Alle Maße kommen aus dem Layout; hier wird nur gezeichnet."""
from __future__ import annotations

import json
from contextlib import nullcontext

from ..document.objekte import P_BILDANKER, ImageObject
from ..geometry import Point, Rect
from ..layout.objekte import objekt_rechteck
from ..layout.seitenumbruch import Ergebnis
from .backend import RenderTarget, Style, rgba
from .linien import zeichne_absatzrahmen
from .textrenderer import zeichne_auswahl, zeichne_cursor, zeichne_marke, zeichne_tabfuellung, zeichne_zeile, zeichne_zeilennummern
from .objekte import zeichne_bild
from .objektrenderer import zeichne_textfeld as _textfeld_einfach_zeichnen
from .tabelle import ausfuehren, rahmen_anweisungen, zelle_anweisungen
from ..textlayout.engine import FontSpec, TextLayoutEngine
from ..textlayout.hb_engine import LEERZEICHEN
from ..textlayout.paragraph import TAB, Absatzsatz, Objekt

PX_JE_PT = 96.0 / 72.0
NOTENLINIE = Style(color=(128, 128, 128, 255), width=1.0)             # Trennstrich über Fuß- und Endnoten
FUELL_STRICH = {".": "dot", "·": "dot", "-": "dash", "_": None}       # Füllzeichen der Tabstrecke → Strichart der Linie auf der Grundlinie
FUELL_LUECKE = 2.0                                                    # Abstand der Füllung zum Text davor und dahinter


def zeichne_absatzrahmen_der_seite(b: RenderTarget, erg: Ergebnis, index: int) -> None:
    """Die Rahmen um Absätze der Seite: aufeinanderfolgende Absätze mit gleicher Rahmenangabe teilen sich einen Rahmen (mit Linien dazwischen, wenn die Angabe „h“ nennt)."""
    gruppen: list[list] = []                                           # [Angabe, letzter Pfad, [Fläche je Absatz]]
    flaechen: dict[tuple, Rect] = {}
    for p in erg.seiten[index].plaetze:
        if p.art != "zeile" or p.kopie or not erg.absaetze[p.pfad].rahmen:
            continue
        alt = flaechen.get(p.pfad)
        neu = p.rect if alt is None else Rect(min(alt.x, p.rect.x), min(alt.y, p.rect.y), max(alt.right, p.rect.right) - min(alt.x, p.rect.x),
                                               max(alt.bottom, p.rect.bottom) - min(alt.y, p.rect.y))
        if alt is None:
            angabe = erg.absaetze[p.pfad].rahmen
            letzte = gruppen[-1] if gruppen else None
            nachbar = letzte is not None and letzte[0] == angabe and letzte[1][:-1] == p.pfad[:-1] and letzte[1][-1] + 1 == p.pfad[-1] and abs(flaechen[letzte[1]].x - p.rect.x) < 0.5
            if nachbar:
                letzte[1] = p.pfad
                letzte[2].append(p.pfad)
            else:
                gruppen.append([angabe, p.pfad, [p.pfad]])
        flaechen[p.pfad] = neu
    for angabe, _letzter, pfade in gruppen:
        rs = [flaechen[k] for k in pfade]
        x, y = min(r.x for r in rs), min(r.y for r in rs)
        gesamt = Rect(x, y, max(r.right for r in rs) - x, max(r.bottom for r in rs) - y)
        zeichne_absatzrahmen(b, angabe, gesamt, [(a.bottom + c.y) / 2 for a, c in zip(rs, rs[1:])])


def zeichne_freie_bilder(b: RenderTarget, dok, erg: Ergebnis, index: int, hinter: bool) -> None:
    """Frei positionierte Bilder und Formen der Absätze auf dieser Seite; Formen werden nativ gezeichnet, sofern unterstützt."""
    from ..document.zugriff import absatz_bei
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
            if a.get("art") == "textfeld" and isinstance(a.get("daten"), dict) and _textfeld_einfach_zeichnen(b, obj, r, a["daten"]):
                continue
            if a.get("art") == "form" and isinstance(a.get("daten"), dict):
                from ..document.objekte import ShapeObject
                from .objekte import zeichne_form
                form = ShapeObject.aus_parametern(a["daten"])
                form.kind = form.kind.casefold()
                form.width, form.height = obj.width, obj.height
                form.anchor, form.transform, form.opacity = obj.anchor, obj.transform, obj.opacity
                form.wrap = obj.wrap
                if zeichne_form(b, form, r):
                    continue
            fuell = dok.media.get((a.get("fuell") or {}).get("n", ""))
            zeichne_bild(b, obj, r, None, fuell.raster_png if fuell is not None else None)


def zeichne_seite(b: RenderTarget, erg: Ergebnis, index: int, engine: TextLayoutEngine, hintergrund: bool = True, dok=None) -> None:
    """Seite ``index`` des Layout-Ergebnisses: erst Seitenfarbe und Zellen (hinter dem Text), dann Zeilen, Aufzählungszeichen und Fußnoten."""
    seite = erg.seiten[index]
    einr = seite.einrichtung
    if hintergrund and getattr(einr, "color", None):
        pw, ph = einr.width_mm * 96 / 25.4, einr.height_mm * 96 / 25.4
        b.draw_rect(Rect(0, 0, pw, ph), Style(color=rgba(einr.color), width=0, filled=True))
    for p in seite.plaetze:                                           # hinter dem Text: Rahmen, Zellen, Absatzhintergrund (in der Reihenfolge des Layouts)
        if p.art == "zelle":
            zelle, tabelle = p.daten[:2]
            ausfuehren(b, zelle_anweisungen(p.rect, zelle, tabelle, float(tabelle.get("FrameBorder", 0.0) or 0.0), 1.0))
        elif p.art == "rahmen" and isinstance(p.daten, dict):
            ausfuehren(b, rahmen_anweisungen(p.rect, p.daten))
        elif p.art == "zeile" and erg.absaetze[p.pfad].hintergrund:
            b.draw_rect(p.rect, Style(color=erg.absaetze[p.pfad].hintergrund, width=0, filled=True))
    if dok is not None:
        zeichne_freie_bilder(b, dok, erg, index, True)
    zeichne_absatzrahmen_der_seite(b, erg, index)
    exakte_zellen = [p for p in seite.plaetze if p.art == "zelle" and len(p.daten) > 2 and p.daten[2] is not None and p.daten[2].kind == "exact"]
    for p in seite.plaetze:
        if p.art == "zeile":
            ort = erg.absaetze[p.pfad]
            zelle = next((z for z in exakte_zellen if p.pfad[:len(z.pfad)] == z.pfad), None)
            with b.state(clip=zelle.rect) if zelle is not None else nullcontext(b):
                zeichne_zeile(b, ort.satz, p.zeile, p.rect)
                if ort.satz.tab_fuell:
                    zeichne_tabfuellung(b, ort.satz, p.zeile, p.rect)
                if p.zeile == 0 and ort.marke:
                    zeichne_marke(b, engine, ort.satz, ort.marke, p.rect)
        elif p.art == "endnote" and p.daten is not None:
            zeichne_zeile(b, p.daten, p.zeile, p.rect)
        elif p.art == "notenlinie":
            b.draw_line(Point(p.rect.x, p.rect.y), Point(p.rect.right, p.rect.y), NOTENLINIE)
        elif p.art == "fussnote" and p.daten is not None:
            for i in range(len(p.daten.zeilen)):
                z = p.daten.zeilen[i]
                zeichne_zeile(b, p.daten, i, Rect(p.rect.x, p.rect.y + z.y, p.rect.width, z.hoehe))
    if dok is not None:
        zeichne_freie_bilder(b, dok, erg, index, False)

