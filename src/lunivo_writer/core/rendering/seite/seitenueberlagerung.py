"""Alles, was über dem Seitenbild eines Blattes liegt und zum Dokument gehört — Auswahl, Suchtreffer, Rechtschreibwellen, Kommentar- und Änderungsmarken,
Formatzeichen, Gitter, Textgrenzen, Lese- und Zeilenfokus, Schreibmarke —, wird vom Kern gezeichnet (``RasterZiel``, ohne Qt). Die Oberfläche zeigt die fertigen
Bilder nur an: Das Überlagerungsbild liegt als durchsichtige Ebene über dem Blatt, die Schreibmarke ist ein eigenes kleines Bild."""
from __future__ import annotations

from dataclasses import dataclass, field

from lunivo_writer.core.geometrie import Point, Rect, mm_to_px
from lunivo_writer.core.rendering.objekte.auswahlrenderer import zeichne_auswahl, zeichne_cursor, zeichne_formatzeichen
from lunivo_writer.core.rendering.ausgabe.backend import Style, rgba
from lunivo_writer.core.rendering.objekte.linien import zeichne_linie
from lunivo_writer.core.rendering.ausgabe.rasterziel import RasterZiel

DURCHSICHTIG = (0, 0, 0, 0)
TREFFER_FARBE = (255, 214, 0, 110)


@dataclass
class Ueberlagerung:
    """Was auf dem Blatt über dem Text zu sehen ist (Flächen je Seite, in Dokument-Bildpunkten)."""
    formatzeichen: tuple = (False, False)                     # Absatzmarken, Leerzeichen und Tabulatoren
    markup: list = field(default_factory=list)                # (Art, Rechteck, Farbe): „kommentar“, „unter“, „durch“
    wellen: list = field(default_factory=list)                # (Rechteck, Farbe)
    treffer: list = field(default_factory=list)               # Rechtecke der Suchtreffer
    flaechen: list = field(default_factory=list)              # Rechtecke der Auswahl
    auswahlfarbe: tuple = (0, 120, 215, 90)
    gitter: bool = False
    textgrenzen: bool = False
    lesefokus: float = 1.0                                    # < 1: alles außer dem Absatz der Schreibmarke wird abgedeckt
    fokus_absatz_id: object = None
    zeilenfokus: bool = False
    marke: tuple | None = None                                # (Seite, Rechteck) der Schreibmarke
    papier: str = "#ffffff"

    def schluessel(self) -> tuple:
        """Wenn sich dieser Wert nicht ändert, bleibt das Überlagerungsbild gleich (die Schreibmarke zählt nicht dazu, sie hat ein eigenes Bild)."""
        def r(x):
            return (x.x, x.y, x.width, x.height)
        return (self.formatzeichen, tuple((a, r(x), f) for a, x, f in self.markup), tuple((r(x), f) for x, f in self.wellen), tuple(r(x) for x in self.treffer),
                tuple(r(x) for x in self.flaechen), self.auswahlfarbe, self.gitter, self.textgrenzen, self.lesefokus, self.fokus_absatz_id, self.zeilenfokus,
                self.papier, None if self.marke is None else (self.marke[0], r(self.marke[1])) if self.zeilenfokus else None)


def _hilfen(b, erg, i: int, u: Ueberlagerung) -> None:
    """Gitter, Textgrenzen, Lesefokus und Zeilenfokus über dem Blatt."""
    einr = erg.seiten[i].einrichtung
    if einr is None:
        return
    links, oben = mm_to_px(einr.margin_left_mm), mm_to_px(einr.margin_top_mm)
    breite, hoehe = einr.content_width_px, einr.content_height_px
    if u.gitter:
        raster = Style(color=(160, 170, 185, 90), width=0.5)
        for x in range(0, int(mm_to_px(einr.width_mm)), 20):
            b.draw_line(Point(x, 0), Point(x, mm_to_px(einr.height_mm)), raster)
        for y in range(0, int(mm_to_px(einr.height_mm)), 20):
            b.draw_line(Point(0, y), Point(mm_to_px(einr.width_mm), y), raster)
    if u.textgrenzen:
        ecke, linie = 12.0, Style(color=(130, 140, 160, 200), width=1.0)
        for x, y, dx, dy in ((links, oben, 1, 1), (links + breite, oben, -1, 1), (links, oben + hoehe, 1, -1), (links + breite, oben + hoehe, -1, -1)):
            b.draw_line(Point(x, y), Point(x + dx * ecke, y), linie)
            b.draw_line(Point(x, y), Point(x, y + dy * ecke), linie)
    if u.lesefokus < 0.999:
        alpha = round((1.0 - u.lesefokus) * 255)
        papier = rgba(u.papier, alpha)
        for p in erg.seiten[i].plaetze:
            if p.art == "zeile" and p.block_id != u.fokus_absatz_id:
                b.draw_rect(p.rect, Style(color=papier, width=0, filled=True))
    if u.zeilenfokus and u.marke is not None and u.marke[0] == i:
        r = u.marke[1]
        b.draw_rect(Rect(links, r.y, breite, r.height), Style(color=(255, 214, 0, 45), width=0, filled=True))


def rendere_ueberlagerung(engine, erg, i: int, u: Ueberlagerung, massstab: float):
    """Die durchsichtige Ebene des Blattes ``i`` als ``(breite, hoehe, rgba)`` in Geräte-Pixeln (``massstab`` = Zoom mal Bildschirmfaktor)."""
    einr = erg.seiten[i].einrichtung
    z = RasterZiel(engine, mm_to_px(einr.width_mm), mm_to_px(einr.height_mm), massstab, DURCHSICHTIG)
    if any(u.formatzeichen):
        zeichne_formatzeichen(z, erg, i, *u.formatzeichen)
    for art, r, farbe in u.markup:
        if art == "kommentar":
            z.draw_rect(r, Style(color=farbe, width=0, filled=True))
        else:
            y = r.bottom - 2 if art == "unter" else r.y + r.height * 0.55
            z.draw_line(Point(r.x, y), Point(r.right, y), Style(color=farbe, width=1.2))
    for r, farbe in u.wellen:
        zeichne_linie(z, farbe, 0.8, "wellig", r.x, r.bottom - 1.5, r.right, r.bottom - 1.5, 96.0 / 72.0)
    zeichne_auswahl(z, u.treffer, TREFFER_FARBE)
    zeichne_auswahl(z, u.flaechen, u.auswahlfarbe)
    _hilfen(z, erg, i, u)
    return z.als_rgba()


def rendere_cursor(engine, rect: Rect, farbe: tuple, massstab: float):
    """Die Schreibmarke als kleines Bild: ``(x, y, breite, hoehe, rgba)`` mit der Lage in Geräte-Pixeln des Blattes."""
    x0, y0 = int(rect.x * massstab) - 1, int(rect.y * massstab) - 1
    b, h = int(rect.width * massstab) + 4, int(rect.height * massstab) + 4
    z = RasterZiel(engine, b / massstab, h / massstab, massstab, DURCHSICHTIG)
    z.push_state(translate=Point(-x0 / massstab, -y0 / massstab))
    zeichne_cursor(z, rect, farbe)
    z.pop_state()
    breite, hoehe, roh = z.als_rgba()
    return x0, y0, breite, hoehe, roh
