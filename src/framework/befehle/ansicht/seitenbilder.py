"""Die Bilder der Ansicht: Blatt, durchsichtige Ebene darüber (Auswahl, Markup, Wellenlinien, Suchtreffer, Hilfen) und Schreibmarke.

Das Framework rendert anhand der Kennung des Dokuments; die Oberfläche gibt nur Seitenindex, Maßstab und ihre Anzeigeangaben und legt die fertigen
Bildpunkte auf ihren Zeichner."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from framework.befehle.ansicht.layout import Kasten, _ergebnis, _kasten, _layout, _sitzung
from framework.zeichnen import Rasterbild

Farbe = tuple[int, int, int, int]


@dataclass(frozen=True)
class Anzeige:
    """Was die Ansicht über dem Text zeigt."""
    formatzeichen: tuple[bool, bool]             # Absatzmarken, Leerzeichen und Tabulatoren
    auswahlfarbe: Farbe
    gitter: bool
    textgrenzen: bool
    lesefokus: float                             # < 1: alles außer dem Absatz der Schreibmarke tritt zurück
    zeilenfokus: bool
    papier: str
    markup: bool                                 # Kommentare und nachverfolgte Änderungen zeigen
    autor_farben: tuple[str, ...]


def seitenbild(kennung: int, index: int, faktor: float, papier: str) -> Rasterbild:
    """Das Blatt ``index`` in der Auflösung ``faktor`` (Zoom mal Bildschirmfaktor) auf der Papierfarbe ``papier``."""
    from core.geometrie import mm_to_px
    from core.layout.drucklayout import schrift
    from core.layout.drucklayout.ausgabe import RasterZiel, rgba
    l, erg, dok = _layout(kennung), _ergebnis(kennung), _sitzung(kennung).dokument
    einr = erg.seiten[index].einrichtung
    ziel = RasterZiel(l.rechner.engine, mm_to_px(einr.width_mm), mm_to_px(einr.height_mm), faktor, rgba(papier))
    l.renderer.zeichne_seite(ziel, dok, erg, index, schrift(dict(dok.standardformat)))
    breite, hoehe, roh = ziel.als_rgba()
    return Rasterbild(breite, hoehe, bytes(roh))


def _markup_flaechen(kennung: int, markup: bool, autor_farben: Sequence[str]):
    """Seitenindex → [(Art, Rechteck, Farbe)] für Kommentare (Hintergrund) und nachverfolgte Änderungen (unterstrichen/durchgestrichen), je Layout einmal."""
    erg, l, s = _ergebnis(kennung), _layout(kennung), _sitzung(kennung)
    if l.markup is not None and l.markup[0] == l.stand:
        return l.markup[1]
    aus: dict = {}
    if markup:
        from core.dokument import teile
        from core.layout.drucklayout import auswahl_rechtecke
        from core.layout.drucklayout.ausgabe import rgba

        def format_bei(pos):
            rest = teile(s.dokument.absatz(pos.absatz_id).inhalte, pos.versatz)[1]
            return rest[0].format if rest else {}
        farben = autor_farben
        for b in s.bereiche(lambda f: "aenderung" in f, lambda f: (f["aenderung"], f.get("autor", ""))):
            art, autor = format_bei(b.anker)["aenderung"], format_bei(b.anker).get("autor", "")
            farbe = rgba(farben[sum(map(ord, autor)) % len(farben)])
            for seite_nr, rects in auswahl_rechtecke(erg, b).items():
                aus.setdefault(seite_nr, []).extend(("unter" if art == "ins" else "durch", r, farbe) for r in rects)
        for b in s.bereiche(lambda f: "kommentar" in f, lambda f: f.get("kommentar")):
            for seite_nr, rects in auswahl_rechtecke(erg, b).items():
                aus.setdefault(seite_nr, []).extend(("kommentar", r, (255, 200, 60, 70)) for r in rects)
    l.markup = (l.stand, aus)
    return aus


def ueberlagerung_setzen(kennung: int, anzeige: Anzeige, wellen: Sequence[tuple[int, int, str]], treffer: Sequence[tuple[int, int]]) -> tuple[int, Kasten] | None:
    """Vor dem Zeichnen: was über dem Text liegt. ``wellen``: (von, bis, Farbe) der Funde der Schreibhilfe, ``treffer``: (von, bis) der Suchtreffer,
    jeweils als Stellen im Rohtext. → (Seite, Rechteck) der Schreibmarke oder ``None``."""
    from core.dokument import Auswahl
    from core.layout.drucklayout import auswahl_rechtecke, cursor_rechteck
    from core.layout.drucklayout.ausgabe.seite import Ueberlagerung
    from core.suche.textsuche import offset_zu_position
    erg, l, s = _ergebnis(kennung), _layout(kennung), _sitzung(kennung)
    dok = s.dokument
    if l.ueber_stand.get("stand") != l.stand:
        l.ueber_stand = {"stand": l.stand}
    je_welle: dict = {}
    for von, bis, farbe in wellen:
        for seite_nr, rects in auswahl_rechtecke(erg, Auswahl(offset_zu_position(dok, von), offset_zu_position(dok, bis))).items():
            je_welle.setdefault(seite_nr, []).extend((r, farbe) for r in rects)
    je_treffer: dict = {}
    for von, bis in treffer:
        for seite_nr, rects in auswahl_rechtecke(erg, Auswahl(offset_zu_position(dok, von), offset_zu_position(dok, bis))).items():
            je_treffer.setdefault(seite_nr, []).extend(rects)
    marke = cursor_rechteck(erg, s.auswahl.kopf)
    u = Ueberlagerung(
        formatzeichen=anzeige.formatzeichen, auswahlfarbe=anzeige.auswahlfarbe, gitter=anzeige.gitter, textgrenzen=anzeige.textgrenzen,
        lesefokus=anzeige.lesefokus, fokus_absatz_id=s.auswahl.kopf.absatz_id, zeilenfokus=anzeige.zeilenfokus, marke=marke, papier=anzeige.papier,
    )
    l.ueber = (u, (_markup_flaechen(kennung, anzeige.markup, anzeige.autor_farben), je_welle, je_treffer,
                   auswahl_rechtecke(erg, s.auswahl) if not s.auswahl.leer else {}))
    return None if marke is None else (marke[0], _kasten(marke[1]))


def _ueberlagerung(kennung: int, index: int):
    l = _layout(kennung)
    u, (markup, wellen, treffer, flaechen) = l.ueber
    u.markup, u.wellen, u.treffer, u.flaechen = markup.get(index, []), wellen.get(index, []), treffer.get(index, []), flaechen.get(index, [])
    return l, u


def ueberlagerung_stand(kennung: int, index: int, faktor: float) -> tuple[int, bool]:
    """(Nummer, leer?) der durchsichtigen Ebene des Blattes ``index``: Die Nummer bleibt gleich, solange sich Inhalt, Maßstab und Layout nicht ändern."""
    l, u = _ueberlagerung(kennung, index)
    schluessel = (faktor, u.schluessel())
    alt = l.ueber_stand.get(index)
    if alt is None or alt[0] != schluessel:
        leer = not (any(u.formatzeichen) or u.markup or u.wellen or u.treffer or u.flaechen or u.gitter or u.textgrenzen or u.lesefokus < 0.999
                    or (u.zeilenfokus and u.marke and u.marke[0] == index))
        l.ueber_nummer += 1
        alt = l.ueber_stand[index] = (schluessel, l.ueber_nummer, bool(leer))
    return alt[1], alt[2]


def ueberlagerungsbild(kennung: int, index: int, faktor: float) -> Rasterbild:
    """Die durchsichtige Ebene des Blattes ``index`` in Geräte-Pixeln (``faktor`` = Zoom mal Bildschirmfaktor)."""
    from core.layout.drucklayout.ausgabe.seite import rendere_ueberlagerung
    l, u = _ueberlagerung(kennung, index)
    breite, hoehe, roh = rendere_ueberlagerung(l.rechner.engine, _ergebnis(kennung), index, u, faktor)
    return Rasterbild(breite, hoehe, bytes(roh))


def cursorbild(kennung: int, faktor: float, farbe: str) -> tuple[int, int, Rasterbild] | None:
    """Die Schreibmarke als kleines Bild: (x, y, Bild) mit der Lage in Geräte-Pixeln des Blattes; ``None`` ohne Schreibmarke."""
    from core.layout.drucklayout.ausgabe import rgba
    from core.layout.drucklayout.ausgabe.seite import rendere_cursor
    l = _layout(kennung)
    marke = l.ueber[0].marke if l.ueber is not None else None
    if marke is None:
        return None
    x, y, b, h, roh = rendere_cursor(l.rechner.engine, marke[1], rgba(farbe), faktor)
    return x, y, Rasterbild(b, h, bytes(roh))
