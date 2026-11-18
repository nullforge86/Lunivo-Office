"""Text auf dem Blatt zeichnen, ohne Qt: Zeilen eines gesetzten Absatzes mit Läufen (Schrift, Farbe, Unterstreichen, Hervorheben, hoch-/tiefgestellt,
Tabulatoren mit Füllung, Objekte in der Zeile), Aufzählungszeichen, Auswahlflächen, Schreibmarke und Zeilennummern. Alle Maße kommen aus dem Layout;
hier wird nur gezeichnet."""
from __future__ import annotations

from ..geometry import Point, Rect
from ..layout.ergebnis import Ergebnis
from .backend import RenderTarget, Style
from ..textlayout.engine import FontSpec, TextLayoutEngine
from ..textlayout.hb_engine import LEERZEICHEN
from ..textlayout.paragraph import TAB, Absatzsatz, Objekt

PX_JE_PT = 96.0 / 72.0
FUELL_STRICH = {".": "dot", "·": "dot", "-": "dash", "_": None}       # Füllzeichen der Tabstrecke → Strichart der Linie auf der Grundlinie
FUELL_LUECKE = 2.0                                                    # Abstand der Füllung zum Text davor und dahinter


def zeichne_zeile(b: RenderTarget, satz: Absatzsatz, zeile: int, rect: Rect, objekt_zeichner=None) -> None:
    """Zeile ``zeile`` des gesetzten Absatzes; ``rect`` = ihr Rechteck auf der Seite (Oberkante der Zeile, linker Rand der Spalte).
    ``objekt_zeichner(stil, Rect)`` zeichnet ein Objekt in der Zeile (Stil des Laufs, Fläche über der Grundlinie); ohne ihn gilt das Bild im Stil (``bild``)."""
    z = satz.zeilen[zeile]
    grundlinie = rect.y + z.box.ascent
    for lauf, start, ende in _stuecke(satz, zeile):
        if satz.ebenen is not None:                                   # Text mit Zeichen rechts nach links: jedes Stück steht an seiner Anzeigestelle
            x1, x2 = satz.segment(start, ende, zeile)
            x = rect.x + x1
        else:
            x = rect.x + satz.cursor_x(start, zeile)
        if isinstance(lauf.schrift, Objekt):
            if objekt_zeichner is not None:
                objekt_zeichner(lauf.stil, Rect(x, grundlinie - lauf.schrift.hoehe, lauf.schrift.breite, lauf.schrift.hoehe))
                continue
            bild = lauf.stil.get("bild")
            if bild:
                b.draw_image(bild, Rect(x, grundlinie - lauf.schrift.hoehe, lauf.schrift.breite, lauf.schrift.hoehe), smooth=True)
            continue
        text = satz.text[start:ende]
        breite = x2 - x1 if satz.ebenen is not None else satz.cursor_x(ende, zeile) - satz.cursor_x(start, zeile)
        farbe = lauf.stil.get("color") or (0, 0, 0, 255)
        if lauf.stil.get("highlight"):
            b.draw_rect(Rect(x, rect.y, breite, z.box.height), Style(color=lauf.stil["highlight"], width=0, filled=True))
        text_y = grundlinie + lauf.stil.get("versatz", 0.0) * lauf.schrift.size_pt * PX_JE_PT      # hoch-/tiefgestellt: eigene Grundlinie
        gesperrt = lauf.stil.get("sperrung") or lauf.stil.get("sperrung_prozent")
        if satz.ebenen is not None:
            b.draw_text(text.replace("\n", "").replace("\u2028", "").rstrip(), Point(x, text_y), lauf.schrift, Style(color=farbe))
        elif gesperrt:                                                  # Laufweite: Zeichen für Zeichen an seiner Stelle
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

    if z.box.trennstrich:                                             # Silbentrennung: der Trennstrich steht hinter dem letzten Zeichen der Zeile
        lauf = next((la for la in reversed(satz.laeufe) if la.start < z.ende and isinstance(la.schrift, FontSpec)), None)
        if lauf is not None:
            farbe = lauf.stil.get("color") or (0, 0, 0, 255)
            b.draw_text("-", Point(rect.x + satz.cursor_x(z.ende, zeile), grundlinie + lauf.stil.get("versatz", 0.0) * lauf.schrift.size_pt * PX_JE_PT),
                        lauf.schrift, Style(color=farbe))


def _stuecke(satz: Absatzsatz, zeile: int):
    """(Lauf, Anfang, Ende) der Stücke einer Zeile: je Lauf eines; bei Text mit Zeichen rechts nach links je Lauf und Richtungsebene."""
    z = satz.zeilen[zeile]
    for lauf in satz.laeufe:
        start, ende = max(lauf.start, z.box.start), min(lauf.ende, z.ende)
        if start >= ende:
            continue
        if satz.ebenen is None or isinstance(lauf.schrift, Objekt):
            yield lauf, start, ende
            continue
        _pos, lev = satz.zeichenpositionen(zeile)
        a = start
        for i in range(start + 1, ende + 1):
            if i == ende or lev[i] != lev[a]:
                yield lauf, a, i
                a = i


def zeichne_tabfuellung(b: RenderTarget, satz: Absatzsatz, zeile: int, rect: Rect) -> None:
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


def zeichne_marke(b: RenderTarget, engine: TextLayoutEngine, satz: Absatzsatz, marke: str, rect: Rect) -> None:
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


def zeichne_zeilennummern(b: RenderTarget, erg: Ergebnis, index: int, grund: FontSpec) -> None:
    """Zeilennummern links neben dem Text der Seite (kleine graue Schrift, rechtsbündig), wenn die Seiteneinrichtung ``zeilennummern`` verlangt."""
    einr = erg.seiten[index].einrichtung
    if einr is None or not getattr(einr, "zeilennummern", False):
        return
    klein = FontSpec(grund.family, 9 * 72 / 96, 400)
    links = einr.margin_left_mm * 96 / 25.4
    for seite, y, h, nr in erg.zeilennummern("seite" if getattr(einr, "zeilennummern_neu", "") == "seite" else ""):
        if seite == index:
            b.draw_text_box(str(nr), Rect(links - 48, y, 42, h), klein, Style(color=(160, 160, 164, 255)), align="right", wrap=False)


def zeichne_listenmarke(b: RenderTarget, engine: TextLayoutEngine, satz: Absatzsatz, marke: str, marke_x: float, rect: Rect) -> None:
    """Aufzählungszeichen oder Nummer einer Liste an ihrer Stelle (``marke_x`` vom linken Rand der Spalte, wie das Layout sie liefert) in der ersten Zeile."""
    if not satz.laeufe or not satz.zeilen:
        return
    erste = next((lauf for lauf in satz.laeufe if isinstance(lauf.schrift, FontSpec)), None)
    if erste is None:
        return
    m = engine.font_metrics(erste.schrift)
    farbe = erste.stil.get("color") or (0, 0, 0, 255)
    x, grundlinie = rect.x + marke_x, rect.y + satz.zeilen[0].box.ascent
    if marke in ("•", "◦", "▪"):
        d = (m.ascent + m.descent) / 3.0
        mx, my = x + d, grundlinie - m.ascent / 2.4
        stil = Style(color=farbe, width=1.0, filled=marke != "◦")
        if marke == "▪":
            b.draw_rect(Rect(mx - d / 2, my - d / 2, d, d), stil)
        else:
            b.draw_ellipse(Point(mx, my), d / 2, d / 2, stil)
    else:
        b.draw_text(marke, Point(x, grundlinie), erste.schrift, Style(color=farbe))


from .auswahlrenderer import zeichne_auswahl, zeichne_cursor, zeichne_formatzeichen  # noqa: E402,F401  (stehen in auswahlrenderer.py)
