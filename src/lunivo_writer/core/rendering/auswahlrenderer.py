"""Auswahl, Schreibmarke und Formatierungszeichen auf dem Blatt zeichnen, ohne Qt. Alle Maße kommen aus dem Layout (``core.layout.schreibmarke``)."""
from __future__ import annotations

from ..geometry import Point, Rect
from ..layout.ergebnis import Ergebnis
from ..textlayout.engine import FontSpec
from .backend import RenderTarget, Style

def zeichne_auswahl(b: RenderTarget, rechtecke: list[Rect], farbe: tuple[int, int, int, int]) -> None:
    """Die Flächen einer Auswahl auf der Seite (``core.layout.navigation.auswahl_rechtecke``) in der Auswahlfarbe."""
    for r in rechtecke:
        b.draw_rect(r, Style(color=farbe, width=0, filled=True))


def zeichne_cursor(b: RenderTarget, rect: Rect, farbe: tuple[int, int, int, int]) -> None:
    """Die Schreibmarke (``core.layout.navigation.cursor_rechteck``)."""
    b.draw_rect(rect, Style(color=farbe, width=0, filled=True))


FORMATZEICHEN_FARBE = (130, 140, 160, 255)


def zeichne_formatzeichen(b: RenderTarget, erg: Ergebnis, index: int, absatzmarken: bool, leerzeichen: bool) -> None:
    """Formatierungszeichen auf der Seite: ¶ am Ende jedes Absatzes, ↵ am Zeilenwechsel, · für Leerzeichen und → für Tabulatoren."""
    for p in erg.seiten[index].plaetze:
        if p.art != "zeile" or p.kopie:
            continue
        satz = erg.absaetze[p.block_id].satz
        z = satz.zeilen[p.zeile]
        erste = next((lauf for lauf in satz.laeufe if isinstance(lauf.schrift, FontSpec)), None)
        if erste is None:
            continue
        grundlinie = p.rect.y + z.box.ascent
        stil = Style(color=FORMATZEICHEN_FARBE)
        if leerzeichen:
            for i in range(z.box.start, z.ende):
                zeichen = satz.text[i]
                if zeichen == " " or zeichen == "\t":
                    x1, x2 = satz.segment(i, i + 1, p.zeile)
                    b.draw_text("→" if zeichen == "\t" else "·", Point(p.rect.x + x1 + (0.0 if zeichen == "\t" else max(0.0, (x2 - x1) / 2 - 1.5)), grundlinie),
                                erste.schrift, stil)
        if absatzmarken and p.zeile == len(satz.zeilen) - 1:
            letzte_x = satz.cursor_x(z.ende - 1 if z.ende > z.box.start and satz.text[z.ende - 1] in "\n\u2028" else z.ende, p.zeile)
            b.draw_text("¶", Point(p.rect.x + letzte_x + 1, grundlinie), erste.schrift, stil)
        elif absatzmarken and satz.text[z.box.start:z.ende].endswith("\u2028"):
            b.draw_text("↵", Point(p.rect.x + satz.cursor_x(z.ende - 1, p.zeile), grundlinie), erste.schrift, stil)
