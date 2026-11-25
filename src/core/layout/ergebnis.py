"""Das Ergebnis der Layoutberechnung: Seiten mit ihren Plätzen (Zeilen, Zellen, Rahmen, Objekte, Noten) und die gesetzten Absätze. Ohne Qt.

Das Ergebnis verweist auf Blöcke des Dokumentmodells über deren Ids und enthält selbst keine Dokumentdaten. Koordinaten sind Bildpunkte
in Seitenkoordinaten (Ursprung links oben auf dem Blatt).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.geometrie import Point, Rect
from core.textsatz.paragraph import Absatzsatz


@dataclass
class AbsatzOrt:
    """Wo ein Absatz steht: je Zeile Seite und Rechteck."""
    absatz_id: int
    satz: Absatzsatz
    zeilen: list = field(default_factory=list)              # (Seitenindex, Zeilenindex im Satz, Rechteck der Zeile auf der Seite)
    marke: str | None = None                                # Aufzählungszeichen oder Nummer der Liste (nur erste Zeile)
    marke_x: float = 0.0                                    # Abstand der Marke vom linken Rand der Spalte
    ohne_zeilennummer: bool = False
    hintergrund: tuple | None = None                        # Füllfarbe des Absatzes (r, g, b, a)
    rahmen: str | None = None                               # Absatzrahmen; gleiche Angabe an Nachbarn = ein gemeinsamer Rahmen


@dataclass
class Platz:
    """Ein Stück Seite: eine Absatzzeile, eine Tabellenzelle, ein Rahmen, ein freies Objekt, eine Note oder der Trennstrich über den Noten."""
    art: str                         # "zeile" | "zelle" | "rahmen" | "objekt" | "fussnote" | "endnote" | "notenlinie"
    rect: Rect
    block_id: int = 0                # Absatz (zeile), Tabelle (zelle), Rahmen, Objekt oder Note
    zeile: int = -1                  # Zeile im Satz (zeile) oder Zeile der Zelle (zelle)
    spalte: int = -1                 # Spalte der Zelle
    daten: object = None             # Zelle: (Zellformat, Tabellenformat); Rahmen: Rahmenformat; Fuß-/Endnote: ``Absatzsatz``; Objekt: Umbruchart
    kopie: bool = False              # wiederholte Kopfzeile einer Tabelle: wird gezeichnet, zählt aber nicht für Schreibmarke und Treffertest


@dataclass
class Seite:
    index: int
    abschnitt: int
    einrichtung: object | None       # ``PageSettings`` des Abschnitts
    plaetze: list = field(default_factory=list)
    oben: float = 0.0                # y der Blattoberkante im Blattraum (Blätter stehen untereinander mit Abstand)
    nummer: int = 0                  # angezeigte Seitenzahl (Zahlenformat und Start des Abschnitts berücksichtigt)
    breite_px: float = 0.0           # Weblayout: Größe der einen endlosen Seite (0 = Maße der Seiteneinrichtung)
    hoehe_px: float = 0.0


@dataclass
class Ergebnis:
    seiten: list = field(default_factory=list)
    absaetze: dict = field(default_factory=dict)             # Absatz-Id → AbsatzOrt
    reihenfolge: list = field(default_factory=list)          # Ids der gesetzten Absätze in Lesereihenfolge
    objekte: dict = field(default_factory=dict)              # Id eines freien Objekts → (Seitenindex, Rechteck)
    hinweise: list = field(default_factory=list)

    def cursor(self, absatz_id: int, index: int):
        """(Seite, Punkt) der oberen linken Ecke der Zeile, in der die Schreibmarke vor dem Zeichen ``index`` steht."""
        ort = self.absaetze.get(absatz_id)
        if ort is None:
            return None
        zi = ort.satz.zeile_von(index)
        for seite, z, r in ort.zeilen:
            if z == zi:
                return seite, Point(r.x + ort.satz.cursor_x(index, zi), r.y)
        return None

    def zeilennummern(self, art: str = ""):
        """(Seitenindex, y auf der Seite, Zeilenhöhe, Nummer) für jede nummerierte Zeile in Lesereihenfolge; ``art`` „seite“: auf jeder Seite neu ab 1."""
        nr, aktuell = 0, -1
        for seite in self.seiten:
            for p in seite.plaetze:
                if p.art != "zeile" or p.kopie or self.absaetze[p.block_id].ohne_zeilennummer:
                    continue
                if art == "seite" and seite.index != aktuell:
                    nr = 0
                aktuell = seite.index
                nr += 1
                yield seite.index, p.rect.y, p.rect.height, nr

    def treffer(self, seite: int, punkt: Point):
        """(Absatz-Id, Zeichenstelle) für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat."""
        zeilen = [p for p in self.seiten[seite].plaetze if p.art == "zeile" and not p.kopie]
        if not zeilen:
            return None

        def abstand(p: Platz):
            dy = max(p.rect.y - punkt.y, 0.0, punkt.y - p.rect.bottom)
            dx = max(p.rect.x - punkt.x, 0.0, punkt.x - p.rect.right)
            return dy, dx
        best = min(zeilen, key=abstand)
        satz = self.absaetze[best.block_id].satz
        return best.block_id, satz.treffer(punkt.x - best.rect.x, satz.zeilen[best.zeile].y + 0.1)

    def objekt_bei(self, seite: int, punkt: Point):
        """Id des obersten freien Objekts an dem Punkt der Seite, sonst ``None``."""
        for p in reversed(self.seiten[seite].plaetze):
            if p.art == "objekt" and p.rect.contains(punkt):
                return p.block_id
        return None

    def seite_von(self, absatz_id: int) -> int | None:
        """Der Index der Seite, auf der der Absatz beginnt."""
        ort = self.absaetze.get(absatz_id)
        return ort.zeilen[0][0] if ort is not None and ort.zeilen else None
