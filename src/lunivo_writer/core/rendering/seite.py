"""Eine Seite aus dem Ergebnis des Qt-freien Seitenumbruchs (``core.layout.umbrechen``) auf ein ``RenderBackend`` zeichnen: Seitenfarbe, Tabellenzellen (Füllung, Rahmen), Absatzzeilen mit
Läufen (Schrift, Farbe, Unterstreichen, Hervorheben, hoch-/tiefgestellt, Tabulatoren, Bilder in der Zeile), Rahmen, Absatzhintergrund, Aufzählungszeichen, Fuß- und Endnoten mit Trennstrich. Alle Maße kommen aus dem Layout; hier wird nur gezeichnet."""
from __future__ import annotations

import json

from lunivo_writer.core.document.objekte import P_BILDANKER, ImageObject
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.layout.objekte import objekt_rechteck
from lunivo_writer.core.layout.seitenumbruch import Ergebnis
from lunivo_writer.core.rendering.backend import RenderBackend, Style, rgba
from lunivo_writer.core.rendering.linien import zeichne_absatzrahmen
from lunivo_writer.core.rendering.objekte import zeichne_bild
from lunivo_writer.core.rendering.tabelle import ausfuehren, rahmen_anweisungen, zelle_anweisungen
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine
from lunivo_writer.core.textlayout.hb_engine import LEERZEICHEN
from lunivo_writer.core.textlayout.paragraph import TAB, Absatzsatz, Objekt

PX_JE_PT = 96.0 / 72.0
NOTENLINIE = Style(color=(128, 128, 128, 255), width=1.0)             # Trennstrich über Fuß- und Endnoten
FUELL_STRICH = {".": "dot", "·": "dot", "-": "dash", "_": None}       # Füllzeichen der Tabstrecke → Strichart der Linie auf der Grundlinie
FUELL_LUECKE = 2.0                                                    # Abstand der Füllung zum Text davor und dahinter


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
        text_y = grundlinie + lauf.stil.get("versatz", 0.0) * lauf.schrift.size_pt * PX_JE_PT      # hoch-/tiefgestellt: eigene Grundlinie
        gesperrt = lauf.stil.get("sperrung") or lauf.stil.get("sperrung_prozent")
        if gesperrt:                                                  # Laufweite: Zeichen für Zeichen an seiner Stelle
            for i in range(start, ende):
                if satz.text[i].strip():
                    b.draw_text(satz.text[i], Point(rect.x + satz.cursor_x(i, zeile), text_y), lauf.schrift, Style(color=farbe))
        elif z.wort_zuschlag or TAB in text or lauf.stil.get("wortabstand"):      # Blocksatz, Tabulatoren, Wortabstand: Wort für Wort, die Lücken sind breiter
            i = start
            for wort in _woerter(text):
                if wort.strip(" \t\n\u2028"):
                    b.draw_text(wort, Point(rect.x + satz.cursor_x(i, zeile), text_y), lauf.schrift, Style(color=farbe))
                i += len(wort)
        else:
            b.draw_text(text.replace("\n", "").replace("\u2028", ""), Point(x, text_y), lauf.schrift, Style(color=farbe))
        if lauf.stil.get("underline"):
            strich = Style(color=lauf.stil.get("underline_color") or farbe, width=1.0, dash=lauf.stil.get("underline_dash"))
            b.draw_line(Point(x, grundlinie + 2), Point(x + breite, grundlinie + 2), strich)
        if lauf.stil.get("overline"):
            b.draw_line(Point(x, rect.y + 1), Point(x + breite, rect.y + 1), Style(color=farbe, width=1.0))
        if lauf.stil.get("strike"):
            b.draw_line(Point(x, grundlinie - z.box.ascent / 3), Point(x + breite, grundlinie - z.box.ascent / 3), Style(color=farbe, width=1.0))


def zeichne_tabfuellung(b: RenderBackend, satz: Absatzsatz, zeile: int, rect: Rect) -> None:
    """Die Füllzeichen (Punkte, Striche, Linie) in den Strecken der Tabulatoren dieser Zeile, als Linie knapp unter der Grundlinie."""
    z = satz.zeilen[zeile]
    for i, zeichen in satz.tab_fuell.items():
        if not z.box.start <= i < z.ende:
            continue
        x1, x2 = rect.x + satz.cursor_x(i, zeile) + FUELL_LUECKE, rect.x + satz.cursor_x(i + 1, zeile) - FUELL_LUECKE
        if x2 <= x1:
            continue
        lauf = next((la for la in satz.laeufe if la.start <= i < la.ende), None)
        farbe = (lauf.stil.get("color") if lauf is not None else None) or (0, 0, 0, 255)
        y = rect.y + z.box.ascent + (0.0 if zeichen in ".·" else 1.0) - (z.box.ascent / 3 if zeichen in "·-" else 0.0)
        b.draw_line(Point(x1, y), Point(x2, y), Style(color=farbe, width=1.0, dash=FUELL_STRICH.get(zeichen)))


def zeichne_absatzrahmen_der_seite(b: RenderBackend, erg: Ergebnis, index: int) -> None:
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
    """Frei positionierte Bilder und Formen der Absätze auf dieser Seite; Formen werden nativ gezeichnet, sofern unterstützt."""
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
            if a.get("art") == "textfeld" and isinstance(a.get("daten"), dict) and _textfeld_einfach_zeichnen(b, obj, r, a["daten"]):
                continue
            if a.get("art") == "form" and isinstance(a.get("daten"), dict):
                from lunivo_writer.core.document.objekte import ShapeObject
                from lunivo_writer.core.rendering.objekte import zeichne_form
                form = ShapeObject.aus_parametern(a["daten"])
                form.kind = form.kind.casefold()
                form.width, form.height = obj.width, obj.height
                form.anchor, form.transform, form.opacity = obj.anchor, obj.transform, obj.opacity
                form.wrap = obj.wrap
                if zeichne_form(b, form, r):
                    continue
            fuell = dok.media.get((a.get("fuell") or {}).get("n", ""))
            zeichne_bild(b, obj, r, None, fuell.raster_png if fuell is not None else None)


def _textfeld_einfach_zeichnen(b: RenderBackend, obj: ImageObject, rect: Rect, daten: dict) -> bool:
    """Ein Klartextfeld mit einem Format nativ zeichnen; für Runs, Ketten und Effekte bleibt das Bild der Rückfall."""
    if not isinstance(daten.get("text", ""), str) or daten.get("laeufe") or daten.get("von") or daten.get("weiter"):
        return False
    if any(daten.get(k) for k in ("effekt", "kontur", "vorlage", "liste", "einzug", "zeilenabstand", "hervor", "hoch", "tief", "durch")):
        return False
    if daten.get("richtung") not in (None, "", "waagerecht"):
        return False
    from lunivo_writer.core.rendering.objekte import fuellstil, kontur_stil
    font = FontSpec(str(daten.get("schrift") or "Liberation Sans"), float(daten.get("pt") or 11.0), 700 if daten.get("fett") else 400, bool(daten.get("kursiv")))
    style = Style(color=rgba(str(daten.get("farbe") or "#1f1f1f")))
    ausrichtung = {"mitte": "center", "rechts": "right", "block": "justify", "verteilt": "justify"}.get(str(daten.get("ausr") or "links"), "left")
    innen = daten.get("innen")
    try:
        li, ob, re, un = (max(0.0, float(v)) for v in innen) if isinstance(innen, (list, tuple)) and len(innen) == 4 else (0.0, 0.0, 0.0, 0.0)
    except (TypeError, ValueError):
        li = ob = re = un = 0.0

    transform = obj.transform
    veraendert = bool(transform.rotation or transform.flip_h or transform.flip_v)
    b.push_state(opacity=obj.opacity, translate=Point(rect.x + rect.width / 2, rect.y + rect.height / 2) if veraendert else None,
                 rotate=transform.rotation, antialias=True, flip_h=transform.flip_h, flip_v=transform.flip_v)
    ziel = Rect(-rect.width / 2, -rect.height / 2, rect.width, rect.height) if veraendert else rect
    if obj.fill:
        fuellung = fuellstil(obj.fill, ziel)
        if fuellung is not None:
            b.draw_rect(ziel, fuellung)
    if obj.stroke:
        b.draw_rect(ziel, kontur_stil(obj.stroke))
    text_rect = Rect(ziel.x + li, ziel.y + ob, max(0.0, ziel.width - li - re), max(0.0, ziel.height - ob - un))
    b.draw_text_box(daten.get("text", ""), text_rect, font, style, align=ausrichtung, wrap=True, valign="top")
    b.pop_state()
    return True


def zeichne_seite(b: RenderBackend, erg: Ergebnis, index: int, engine: TextLayoutEngine, hintergrund: bool = True, dok=None) -> None:
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
            if zelle is not None:
                b.push_state(clip=zelle.rect)
            try:
                zeichne_zeile(b, ort.satz, p.zeile, p.rect)
                if ort.satz.tab_fuell:
                    zeichne_tabfuellung(b, ort.satz, p.zeile, p.rect)
                if p.zeile == 0 and ort.marke:
                    zeichne_marke(b, engine, ort.satz, ort.marke, p.rect)
            finally:
                if zelle is not None:
                    b.pop_state()
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


def zeichne_auswahl(b: RenderBackend, rechtecke: list[Rect], farbe: tuple[int, int, int, int]) -> None:
    """Die Flächen einer Auswahl auf der Seite (``core.layout.navigation.auswahl_rechtecke``) in der Auswahlfarbe."""
    for r in rechtecke:
        b.draw_rect(r, Style(color=farbe, width=0, filled=True))


def zeichne_cursor(b: RenderBackend, rect: Rect, farbe: tuple[int, int, int, int]) -> None:
    """Die Schreibmarke (``core.layout.navigation.cursor_rechteck``)."""
    b.draw_rect(rect, Style(color=farbe, width=0, filled=True))


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
