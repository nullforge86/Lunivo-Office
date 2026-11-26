"""Kleine Texte außerhalb des Dokuments setzen und zeichnen: das Textfeld eines Objekts, das WordArt-Objekt und die Absatzvorschau der
Formatfenster. Der Kern baut dafür ein eigenes kleines Dokument, setzt und rendert es; hinaus gehen Maße und Rasterbilder."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from framework.anbindung import Daten
from framework.zeichnen.raster import Flaeche, Rasterbild, Rechteck, _malen


class _Textsatz:
    """Das gesetzte Textfeld: ein Dokument in der Größe des Feldes (Innenabstand = Seitenrand), gesetzt von der Layout-Engine des Kerns. Was nicht mehr
    passt, steht auf Seite 2 — daran erkennen verknüpfte Felder, wie viel Text in ein Feld passt."""

    def __init__(self, d, laeufe, b: float, h: float, standard_farbe: str, farbe_ueber: str | None = None):
        from core.bearbeitung import WORDART_VORLAGEN
        from core.dokument import Absatz, Lauf, neues_dokument
        from core.dokument.abschnitte import PageSettings
        from core.layout import LayoutEngine
        from core.layout.drucklayout.ausgabe.text import listenmarken, zeilen_laeufe
        from core.objekte.textfelder.modell import innen, zeichen_dict
        vorlage = None
        if d.get("vorlage") is not None:
            vorlage = WORDART_VORLAGEN[int(d["vorlage"])]
        self.farbe = d.get("fuell") if d.get("fuell") else (vorlage[1] if vorlage and "fuell" not in d else d.get("farbe", standard_farbe))
        li, ob, re_, un = innen(d)
        self.innen_oben = ob
        breit = max(10.0, b - li - re_)
        mm = 25.4 / 96.0                                               # Bildpunkte → Millimeter
        seite = PageSettings(width_mm=(li + breit + min(4.0, breit * 0.01) + re_) * mm, height_mm=max(1.0, h) * mm, margin_left_mm=li * mm,
                             margin_right_mm=re_ * mm, margin_top_mm=ob * mm, margin_bottom_mm=un * mm)    # kleine Toleranz: Schriftmaße weichen um Bruchteile ab
        self.dok = neues_dokument(seite)
        af: dict = {"ausrichtung": "block" if d.get("ausr") in ("block", "verteilt") else d.get("ausr") if d.get("ausr") in ("mitte", "rechts") else "links"}
        if d.get("einzug"):
            af["einzug_links"] = 24.0 * int(d["einzug"])
        if d.get("zeilenabstand"):
            af.update({"zeilenabstand_art": "vielfach", "zeilenabstand": float(d["zeilenabstand"]) * 100})
        zeilen = zeilen_laeufe(laeufe) or [[]]
        self.marken = listenmarken(d.get("liste"), len(zeilen))
        self.absatz_ids: list[int] = []
        self.laengen: list[int] = []
        bloecke = []
        for m_, zl in zip(self.marken, zeilen):
            inhalte = []
            if m_:
                inhalte.append(Lauf(m_, zeichen_dict(d, {}, vorlage, farbe_ueber, self.farbe)))
            inhalte += [Lauf(r["t"], zeichen_dict(d, r, vorlage, farbe_ueber, self.farbe)) for r in zl]
            a = Absatz(self.dok.neue_id(), inhalte, dict(af))
            bloecke.append(a)
            self.absatz_ids.append(a.id)
            self.laengen.append(sum(len(r["t"]) for r in zl))
        self.dok.abschnitte[0].bloecke = bloecke
        self.layout = LayoutEngine()
        self.erg = self.layout.berechnen(self.dok)

    def _zeilen_seite1(self):
        return [p.rect for p in self.erg.seiten[0].plaetze if p.art == "zeile" and not p.kopie]


_SAETZE: dict[int, _Textsatz] = {}
_naechste = [1]


def textfeld_setzen(d: Mapping[str, Daten], laeufe: Sequence[Mapping[str, Daten]], b: float, h: float, standard_farbe: str, farbe_ueber: str | None = None) -> int:
    """Den Text eines Textfelds (Angaben ``d``, Läufe ``laeufe``) in ein Feld ``b`` × ``h`` setzen; → Nummer des Satzes (mit ``textfeld_freigeben`` beenden).
    ``farbe_ueber``: alle Zeichen in dieser Farbe (für den Schatten)."""
    nummer = _naechste[0]
    _naechste[0] += 1
    _SAETZE[nummer] = _Textsatz(d, laeufe, b, h, standard_farbe, farbe_ueber)
    return nummer


def textfeld_freigeben(nummer: int) -> None:
    _SAETZE.pop(nummer, None)


def textfeld_zeilen(nummer: int) -> tuple[Rechteck, ...]:
    """Die Rechtecke der Textzeilen, die auf dem Feld stehen."""
    return tuple(Rechteck(r.x, r.y, r.width, r.height) for r in _SAETZE[nummer]._zeilen_seite1())


def textfeld_hoehe(nummer: int) -> float:
    """Obere Kante des Innenraums bis zur Unterkante der letzten Zeile auf dem Feld."""
    s = _SAETZE[nummer]
    return max([r.bottom for r in s._zeilen_seite1()] + [s.innen_oben])


def textfeld_farbe(nummer: int) -> str:
    """Die Textfarbe des Feldes (Füllung des Textes, Farbe der Vorlage oder die eigene Farbe)."""
    return _SAETZE[nummer].farbe


def textfeld_blatt(nummer: int) -> tuple[float, float]:
    """Breite und Höhe des gesetzten Feldes in Bildpunkten (96 dpi)."""
    from core.geometrie import mm_to_px
    einr = _SAETZE[nummer].erg.seiten[0].einrichtung
    return (mm_to_px(einr.width_mm), mm_to_px(einr.height_mm)) if einr is not None else (mm_to_px(210), mm_to_px(297))


def textfeld_bild(nummer: int, faktor: float) -> Rasterbild:
    """Der gesetzte Text des Feldes (durchsichtiger Grund) in der Auflösung ``faktor``."""
    from core.layout.drucklayout.ausgabe import DokumentRenderer, RasterZiel
    s = _SAETZE[nummer]
    b, h = textfeld_blatt(nummer)
    ziel = RasterZiel(s.layout.engine, b, h, faktor, (255, 255, 255, 0))
    DokumentRenderer(s.layout.engine).zeichne_seite(ziel, s.dok, s.erg, 0, None)
    breite, hoehe, roh = ziel.als_rgba()
    return Rasterbild(breite, hoehe, bytes(roh))


def textfeld_passt(d: Mapping[str, Daten], laeufe: Sequence[Mapping[str, Daten]], b: float, h: float, standard_farbe: str) -> int:
    """Wie viele Zeichen der Läufe im Feld ``b`` × ``h`` stehen (Anfang der ersten Zeile, die nicht mehr passt) — für verknüpfte Textfelder."""
    from core.layout.drucklayout.ausgabe.text import laeufe_text
    satz = _Textsatz(d, laeufe, b, h, standard_farbe)
    vorher = 0                                                         # Zeichen der Absätze davor samt Zeilenwechsel
    for i, aid in enumerate(satz.absatz_ids):
        ort = satz.erg.absaetze.get(aid)
        if ort is not None:
            for seite, zi, _r in ort.zeilen:
                if seite > 0:
                    return max(0, vorher + max(0, ort.satz.zeilen[zi].box.start - len(satz.marken[i] or "")))
        vorher += satz.laengen[i] + 1
    return len(laeufe_text(laeufe))


def wordart_objekt(d: Mapping[str, Daten]) -> tuple[Rasterbild, tuple[tuple[int, int], ...]]:
    """Das WordArt-Objekt ``d`` (nach einer Vorlage der Galerie) als Bild in doppelter Auflösung; dazu (oben, Höhe) jeder Zeile in Bildpunkten des Bildes."""
    from core.bearbeitung import WORDART_VORLAGEN
    from core.layout.drucklayout.ausgabe.text import wordart_rgba
    from core.objekte.textfelder.modell import SS
    from framework.dokumentverwaltung.ausgabe import standard_engine
    erg = wordart_rgba(d, standard_engine(), WORDART_VORLAGEN, SS)
    ys, asz, hoehen, faktor = erg["ys"], erg["asz"], erg["hoehen"], erg["faktor"]
    return (Rasterbild(erg["w"], erg["h"], bytes(erg["rgba"])),
            tuple((int((ys[i] - asz[i]) * SS), int(hoehen[i] * faktor * SS)) for i in range(erg["zeilen"])))


def absaetze(flaeche: Flaeche, r: Rechteck, texte: Sequence[tuple[Mapping[str, Daten], Mapping[str, Daten], str]], mittig: bool = False) -> Rasterbild:
    """Absätze (Absatzformat, Zeichenformat, Text) in das Rechteck ``r`` setzen und zeichnen: die Vorschau der Formatierungsfenster.
    ``mittig``: der Text steht senkrecht in der Mitte."""
    from core.dokument import Absatz, Lauf, neues_dokument
    from core.dokument.abschnitte import PageSettings
    from core.geometrie import Point
    from core.layout import LayoutEngine
    from core.layout.drucklayout.ausgabe import DokumentRenderer
    px_mm = 25.4 / 96.0
    seite = PageSettings(width_mm=max(1.0, r[2] * px_mm), height_mm=max(1.0, r[3] * px_mm), margin_top_mm=0.0, margin_bottom_mm=0.0,
                         margin_left_mm=0.0, margin_right_mm=0.0)
    dok = neues_dokument(seite)
    dok.abschnitte[0].bloecke = [Absatz(dok.neue_id(), [Lauf(text, dict(zf))] if text else [], dict(af)) for af, zf, text in texte]
    layout = LayoutEngine()
    erg = layout.berechnen(dok)
    hoehe = max([pl.rect.bottom for pl in erg.seiten[0].plaetze] + [0.0])
    versatz = max(0.0, (r[3] - hoehe) / 2) if mittig else 0

    def zeichne(z) -> None:
        z.push_state(translate=Point(r[0], r[1] + versatz))
        DokumentRenderer(layout.engine).zeichne_seite(z, dok, erg, 0, None)
        z.pop_state()
    return _malen(flaeche, zeichne)
