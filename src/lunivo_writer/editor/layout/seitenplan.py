"""Seitenplan: die eine Quelle dafür, wie ein Dokument in Bereiche (Abschnitte), Seiten und Spalten gegliedert ist.

Das Dokument (``QTextDocument``) bleibt das Modell; der Seitenplan liest daraus (Abschnittsumbrüche in ``editor/seite/abschnitte.py``,
Seiteneinrichtung in ``modelle/seite.py``) und schreibt nichts zurück. Er beantwortet:

- Welche Bereiche hat das Dokument, mit welcher Seiteneinrichtung, und beginnt ein Bereich auf einer neuen Seite oder fortlaufend auf der Seite
  des vorigen? (``Bereich.neue_seite``)
- Wie ist die Textfläche eines Bereichs in Spalten geteilt (auch ungleich breit)? (``Bereich.spalten``)
- Welche Blöcke gehören zu welchem Bereich? (``Seitenplan.bereich_von_block``)

Die späteren Phasen (Absatzfluss, Display-Liste) stützen sich nur auf diesen Plan, nicht auf eigene Rechnungen mit ``PageSettings``."""
from __future__ import annotations

from dataclasses import dataclass, field

from lunivo_writer.modelle.seite import PageSettings, mm_to_px


@dataclass(frozen=True)
class Spalte:
    """Eine Textspalte: ``x`` vom linken Textrand und ``breite`` in Bildpunkten."""
    x: float
    breite: float


@dataclass
class Bereich:
    """Ein Stück des Dokuments mit einheitlicher Seiteneinrichtung (ein oder mehrere aufeinanderfolgende Abschnitte gleicher Geometrie)."""
    index: int                                   # laufende Nummer des Bereichs (0-basiert)
    seite: PageSettings                          # Einrichtung (Maße, Ränder, Spalten, Kopf/Fuß …)
    beginn: str                                  # "naechste", "fortlaufend", "gerade" oder "ungerade" (Abschnittsart laut Datei)
    von_abschnitt: int                           # erster und letzter Abschnitt (0-basiert), die im Bereich aufgehen
    bis_abschnitt: int
    neue_seite: bool                             # beginnt der Bereich auf einer neuen Seite? (bei "fortlaufend" nur, wenn die Geometrie wechselt)
    hinweis: str = ""                            # Begründung, wenn die Ausgabe von der Datei abweicht
    spalten: list[Spalte] = field(default_factory=list)
    auf_seite: bool = False                      # „fortlaufend“ auf dem Blatt des vorigen Bereichs (gleiche Blattgröße, andere Ränder oder Spalten)

    @property
    def blatt_px(self) -> tuple[float, float]:
        return mm_to_px(self.seite.width_mm), mm_to_px(self.seite.height_mm)

    @property
    def text_links_px(self) -> float:
        return mm_to_px(self.seite.margin_left_mm)

    @property
    def text_oben_px(self) -> float:
        return mm_to_px(self.seite.margin_top_mm)


def spalten(ps: PageSettings) -> list[Spalte]:
    return [Spalte(x, b) for x, b in ps.spaltenraster_px()]


def gleiche_geometrie(a: PageSettings, b: PageSettings) -> bool:
    """Haben zwei Einrichtungen dieselbe Seitengeometrie (Blatt, Ränder, Spaltenraster)? Dann bilden sie bei „fortlaufend“ einen Bereich."""
    if abs(a.width_mm - b.width_mm) >= .01 or abs(a.height_mm - b.height_mm) >= .01 or a.spalten != b.spalten:
        return False
    if any(abs(x - y) >= .01 for x, y in ((a.margin_left_mm, b.margin_left_mm), (a.margin_right_mm, b.margin_right_mm),
                                            (a.margin_top_mm, b.margin_top_mm), (a.margin_bottom_mm, b.margin_bottom_mm),
                                            (a.spalten_abstand_mm, b.spalten_abstand_mm))):
        return False
    ra = [(round(x, 1), round(w, 1)) for x, w in a.spaltenraster_px()]
    rb = [(round(x, 1), round(w, 1)) for x, w in b.spaltenraster_px()]
    return ra == rb and a.spalten_linie == b.spalten_linie


class Seitenplan:
    """Die Bereiche eines Dokuments, in Reihenfolge."""

    def __init__(self, bereiche: list[Bereich], hinweise: list[str] | None = None):
        self.bereiche = bereiche
        self.hinweise = hinweise or []

    @staticmethod
    def aus_dokument(qdoc, basis: PageSettings) -> "Seitenplan":
        """Der Plan für ``qdoc`` mit der Dokumenteinrichtung ``basis``. Ein „fortlaufender“ Umbruch zu gleicher Geometrie geht im vorigen
        Bereich auf; wechselt die Geometrie, bekommt der Bereich ``neue_seite=True`` und einen Hinweis (die Ausgabe kennt noch keine zwei
        Geometrien auf einer Seite — das ist Aufgabe der späteren Phasen)."""
        from lunivo_writer.editor.seite import abschnitte as AB
        if not AB.umbrueche(qdoc):
            return Seitenplan([Bereich(0, basis, "naechste", 0, 0, True, spalten=spalten(basis))])
        bereiche: list[Bereich] = []
        hinweise: list[str] = []
        for i, (typ, ps) in enumerate(AB.alle_einrichtungen(qdoc, basis)):
            ps.color, ps.silbentrennung = basis.color, basis.silbentrennung
            if not (ps.watermark or {}).get("abschnitt"):                # Wasserzeichen „nur dieser Abschnitt“ bleibt, sonst gilt das des Dokuments
                ps.watermark = basis.watermark
            hinweis = ""
            if i and typ == "fortlaufend":
                if gleiche_geometrie(bereiche[-1].seite, ps):
                    bereiche[-1].bis_abschnitt = i
                    continue
                hinweis = f"Abschnitt {i + 1}: Ein fortlaufender Abschnittsumbruch mit anderer Seitengeometrie beginnt in der Ausgabe auf einer neuen Seite."
                hinweise.append(hinweis)
            auf_seite = bool(i and typ == "fortlaufend" and abs(ps.width_mm - bereiche[-1].seite.width_mm) < .01
                             and abs(ps.height_mm - bereiche[-1].seite.height_mm) < .01)
            bereiche.append(Bereich(len(bereiche), ps, typ, i, i, True, hinweis, spalten(ps), auf_seite))
        return Seitenplan(bereiche, hinweise)

    def bereich_von_abschnitt(self, abschnitt: int) -> Bereich:
        for b in self.bereiche:
            if b.von_abschnitt <= abschnitt <= b.bis_abschnitt:
                return b
        return self.bereiche[-1]

    def bereich_von_block(self, qdoc, blocknummer: int) -> Bereich:
        """Der Bereich, in dem der Block mit dieser Nummer steht."""
        from lunivo_writer.editor.seite import abschnitte as AB
        return self.bereich_von_abschnitt(sum(1 for n, _t, _p in AB.umbrueche(qdoc) if n < blocknummer))
