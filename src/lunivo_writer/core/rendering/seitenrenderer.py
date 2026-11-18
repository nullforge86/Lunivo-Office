"""Der Dokument-Renderer: zeichnet eine Seite des Layout-Ergebnisses (``core.layout.LayoutErgebnis``) über das Dokumentmodell auf ein ``RenderTarget``.

Reihenfolge einer Seite: Seitenfarbe und Seitenrahmen hinten, Wasserzeichen, Zellen, Textrahmen und Absatzhintergründe, Objekte hinter dem Text,
Absatzrahmen, Zeilen mit Listenmarken und Tabulatorfüllung, Kopf-/Fußzeilen, Noten, Zeilennummern, Objekte vor dem Text, Seitenrahmen vorn.
Alle Maße kommen aus dem Layout; der Renderer verändert weder Modell noch Layout. Auswahl und Schreibmarke zeichnet die Ansicht danach mit
``zeichne_auswahl`` und ``zeichne_cursor`` aus ``textrenderer``.
"""
from __future__ import annotations

from ..document.dokument import Dokument, InlineObjekt
from ..geometry import Point, Rect
from ..layout.ergebnis import Ergebnis
from ..textlayout.engine import FontSpec, TextLayoutEngine
from .backend import RenderTarget, Style
from .linien import zeichne_absatzrahmen
from .objektrenderer import zeichne_objekt
from .seitenschmuck import zeichne_seitenschmuck
from .tabellenrenderer import zeichne_textrahmen, zeichne_zelle
from .textrenderer import zeichne_listenmarke, zeichne_tabfuellung, zeichne_zeile, zeichne_zeilennummern

NOTENLINIE = Style(color=(128, 128, 128, 255), width=1.0)             # Trennstrich über Fuß- und Endnoten
HINTER_DEM_TEXT = ("hinter",)


class SeitenRenderer:
    def __init__(self, engine: TextLayoutEngine):
        self.engine = engine

    def zeichne_seite(self, b: RenderTarget, dok: Dokument, erg: Ergebnis, index: int, zeilennummern_schrift: FontSpec | None = None) -> None:
        """Seite ``index`` zeichnen. Der Ursprung des Backends liegt an der linken oberen Ecke der Seite."""
        seite = erg.seiten[index]
        einr = seite.einrichtung
        if einr is not None:
            zeichne_seitenschmuck(b, self.engine, einr, True, rahmen="hinten")
        inline = self._inline_objekte(dok, erg, seite)

        def objekt_zeichner(stil: dict, rect: Rect) -> None:
            o = inline.get(stil.get("objekt"))
            if o is not None:
                zeichne_objekt(b, dok, o.art, o.breite, o.hoehe, o.ressource, o.daten, rect)

        for p in seite.plaetze:                                         # hinter dem Text: Zellen, Textrahmen, Absatzhintergrund
            if p.art == "zelle":
                zeichne_zelle(b, p.rect, *p.daten[:2])
            elif p.art == "rahmen" and isinstance(p.daten, dict):
                zeichne_textrahmen(b, p.rect, p.daten)
            elif p.art == "zeile" and not p.kopie and erg.absaetze[p.block_id].hintergrund:
                b.draw_rect(p.rect, Style(color=erg.absaetze[p.block_id].hintergrund, width=0, filled=True))
        self._freie_objekte(b, dok, seite, hinten=True)
        self._seitenbilder(b, dok, erg, seite, hinten=True)                 # Kopf-/Fußbilder hinter dem Text
        self._absatzrahmen(b, erg, seite)
        for p in seite.plaetze:
            if p.art == "zeile":
                ort = erg.absaetze[p.block_id]
                zeichne_zeile(b, ort.satz, p.zeile, p.rect, objekt_zeichner)
                if ort.satz.tab_fuell:
                    zeichne_tabfuellung(b, ort.satz, p.zeile, p.rect)
                if p.zeile == 0 and ort.marke and not p.kopie:
                    zeichne_listenmarke(b, self.engine, ort.satz, ort.marke, ort.marke_x, p.rect)
            elif p.art in ("kopfzeile", "fusszeile") and p.daten is not None:
                self._satz(b, p.daten, p.rect)
            elif p.art == "endnote" and p.daten is not None:
                zeichne_zeile(b, p.daten, p.zeile, p.rect)
            elif p.art == "notenlinie":
                b.draw_line(Point(p.rect.x, p.rect.y), Point(p.rect.right, p.rect.y), NOTENLINIE)
            elif p.art == "fussnote" and p.daten is not None:
                self._satz(b, p.daten, p.rect)
        if zeilennummern_schrift is not None:
            zeichne_zeilennummern(b, erg, index, zeilennummern_schrift)
        self._freie_objekte(b, dok, seite, hinten=False)
        self._seitenbilder(b, dok, erg, seite, hinten=False)                # Kopf-/Fußbilder vor dem Text
        if einr is not None:
            zeichne_seitenschmuck(b, self.engine, einr, False, rahmen="vorn", wasserzeichen=False)

    @staticmethod
    def _satz(b: RenderTarget, satz, rect: Rect) -> None:
        """Alle Zeilen eines gesetzten Textes (Note, Kopf-/Fußzeile) ab der Oberkante von ``rect``."""
        for i, z in enumerate(satz.zeilen):
            zeichne_zeile(b, satz, i, Rect(rect.x, rect.y + z.y, rect.width, z.hoehe))

    @staticmethod
    def _inline_objekte(dok: Dokument, erg: Ergebnis, seite) -> dict:
        """Id → ``InlineObjekt`` für die Absätze der Seite."""
        ids = {p.block_id for p in seite.plaetze if p.art == "zeile"}
        return {x.id: x for a in dok.absaetze() if a.id in ids for x in a.inhalte if isinstance(x, InlineObjekt)}

    @staticmethod
    def _seitenbilder(b: RenderTarget, dok: Dokument, erg: Ergebnis, seite, hinten: bool) -> None:
        """Bilder der Kopf- und Fußzeilen (``PageSettings.bilder``): Angaben mit ``ort`` kopf/fuss (kopf1/fuss1 auf dem ersten Blatt bei „Erste Seite anders“) und
        ``ressource`` (Schlüssel der Bilddaten im Dokument); Lage und Größe in Bildpunkten wie bei frei positionierten Bildern."""
        from ..document.objekte import ImageObject
        from ..geometry import mm_to_px
        from ..layout.objekte import objekt_rechteck
        from .objekte import zeichne_bild
        einr = seite.einrichtung
        if einr is None or not einr.bilder:
            return
        erste = min((s.index for s in erg.seiten if s.abschnitt == seite.abschnitt), default=seite.index)
        art = einr.kopf_fuss_art(seite.index - erste + 1, seite.nummer)
        orte = ("kopf1", "fuss1") if art == "first" else ("kopf", "fuss")
        blatt_b, blatt_h = mm_to_px(einr.width_mm), mm_to_px(einr.height_mm)
        ml, mt = mm_to_px(einr.margin_left_mm), mm_to_px(einr.margin_top_mm)
        for a in einr.bilder:
            if not isinstance(a, dict) or a.get("ort") not in orte or bool(a.get("hinter")) != hinten:
                continue
            daten = dok.ressourcen.get(str(a.get("ressource", ""))) or (bytes(a["bild"]) if isinstance(a.get("bild"), (bytes, bytearray)) else None)
            if daten is None:
                continue
            obj = ImageObject.aus_angabe(a, daten)
            r = objekt_rechteck(obj.anchor, obj.width, obj.height, blatt_b, blatt_h, ml, mt, blatt_b - ml - mm_to_px(einr.margin_right_mm),
                                blatt_h - mt - mm_to_px(einr.margin_bottom_mm), 0.0, None, seite.nummer)
            zeichne_bild(b, obj, r, None, None)

    @staticmethod
    def _freie_objekte(b: RenderTarget, dok: Dokument, seite, hinten: bool) -> None:
        """Frei positionierte Objekte der Seite in Stapelreihenfolge, hinter oder vor dem Text."""
        liste = [p for p in seite.plaetze if p.art == "objekt" and (p.daten in HINTER_DEM_TEXT) == hinten and p.block_id in dok.objekte]
        for p in sorted(liste, key=lambda x: dok.objekte[x.block_id].ebene):
            o = dok.objekte[p.block_id]
            zeichne_objekt(b, dok, o.art, o.breite, o.hoehe, o.ressource, o.daten, p.rect)

    @staticmethod
    def _absatzrahmen(b: RenderTarget, erg: Ergebnis, seite) -> None:
        """Rahmen um Absätze: aufeinanderfolgende Absätze mit gleicher Angabe teilen sich einen Rahmen (mit Linien dazwischen, wenn die Angabe „h“ nennt)."""
        rang = {aid: i for i, aid in enumerate(erg.reihenfolge)}
        flaechen: dict = {}
        gruppen: list = []                                              # [Angabe, letzter Absatz, [Absätze]]
        for p in seite.plaetze:
            if p.art != "zeile" or p.kopie or not erg.absaetze[p.block_id].rahmen:
                continue
            alt = flaechen.get(p.block_id)
            if alt is None:
                angabe = erg.absaetze[p.block_id].rahmen
                letzte = gruppen[-1] if gruppen else None
                nachbar = (letzte is not None and letzte[0] == angabe and rang.get(letzte[1], -9) + 1 == rang.get(p.block_id, -1)
                           and abs(flaechen[letzte[1]].x - p.rect.x) < 0.5)
                if nachbar:
                    letzte[1] = p.block_id
                    letzte[2].append(p.block_id)
                else:
                    gruppen.append([angabe, p.block_id, [p.block_id]])
                flaechen[p.block_id] = p.rect
            else:
                x, y = min(alt.x, p.rect.x), min(alt.y, p.rect.y)
                flaechen[p.block_id] = Rect(x, y, max(alt.right, p.rect.right) - x, max(alt.bottom, p.rect.bottom) - y)
        for angabe, _letzter, ids in gruppen:
            rs = [flaechen[k] for k in ids]
            x, y = min(r.x for r in rs), min(r.y for r in rs)
            gesamt = Rect(x, y, max(r.right for r in rs) - x, max(r.bottom for r in rs) - y)
            zeichne_absatzrahmen(b, angabe, gesamt, [(a.bottom + c.y) / 2 for a, c in zip(rs, rs[1:])])
