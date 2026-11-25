"""Stellen im gesetzten Absatz: Zeile eines Zeichens, Zeichenpositionen, Auswahlstreifen, Schreibmarkenstelle und Treffertest (Punkt → Zeichen). Ohne Qt.
Für ``Absatzsatz`` (``paragraph.py``)."""
from __future__ import annotations

from core.textsatz import bidi
from core.textsatz.wortumbruch import LEERZEICHEN


class TextPositionen:
    """Abfragen auf den Zeilen eines gesetzten Absatzes; setzt ``zeilen``, ``text``, ``vorschuebe``, ``ebenen``, ``basis`` und ``_zeilenpos`` voraus."""

    def zeile_von(self, index: int) -> int:
        for i, z in enumerate(self.zeilen):
            if index < z.ende or i == len(self.zeilen) - 1:
                return i
        return 0

    def zeichenpositionen(self, zeile: int) -> tuple[dict, dict]:
        """Bei Text mit Zeichen rechts nach links: (Zeichenstelle → (linke, rechte Kante vom linken Rand der Spalte), Zeichenstelle → Ebene nach
        Zeilenregel L1) für die Zeichen der Zeile in Anzeigereihenfolge."""
        if zeile in self._zeilenpos:
            return self._zeilenpos[zeile]
        z = self.zeilen[zeile]
        ordnung = bidi.zeilen_reihenfolge(self.text, self.ebenen, self.basis, z.box.start, z.ende)
        lev = {i: self.ebenen[i] for i in ordnung}
        ende = z.ende
        while ende > z.box.start and (self.text[ende - 1].isspace() or self.text[ende - 1] in "\n\u2028"):
            ende -= 1
            lev[ende] = self.basis
        breiten = {i: self.vorschuebe[i] + (z.wort_zuschlag if self.text[i] in LEERZEICHEN else 0.0) for i in ordnung}
        x = z.x
        if self.basis == 1:                                                  # Leerraum am Zeilenende steht links vom sichtbaren Text
            x -= sum(breiten[i] for i in range(ende, z.ende))
        pos = {}
        for i in ordnung:
            pos[i] = (x, x + breiten[i])
            x += breiten[i]
        self._zeilenpos[zeile] = (pos, lev)
        return pos, lev

    def segment(self, von: int, bis: int, zeile: int) -> tuple[float, float]:
        """Linke und rechte Kante der Zeichen ``von`` bis ``bis`` (ausschließlich) in der Zeile, vom linken Rand der Spalte."""
        if self.ebenen is None:
            return self.cursor_x(von, zeile), self.cursor_x(bis, zeile)
        pos, _lev = self.zeichenpositionen(zeile)
        kanten = [pos[i] for i in range(von, bis) if i in pos]
        if not kanten:
            x = self.cursor_x(von, zeile)
            return x, x
        return min(k[0] for k in kanten), max(k[1] for k in kanten)

    def auswahl_x(self, von: int, bis: int, zeile: int) -> list[tuple[float, float]]:
        """Die Streifen (links, rechts) der Zeichen ``von`` bis ``bis`` in der Zeile; bei gemischter Schreibrichtung können es mehrere sein."""
        if self.ebenen is None:
            return [(self.cursor_x(von, zeile), self.cursor_x(bis, zeile))]
        pos, _lev = self.zeichenpositionen(zeile)
        kanten = sorted(pos[i] for i in range(von, bis) if i in pos)
        aus: list[list[float]] = []
        for l, r in kanten:
            if aus and l <= aus[-1][1] + 0.01:
                aus[-1][1] = max(aus[-1][1], r)
            else:
                aus.append([l, r])
        return [(l, r) for l, r in aus]

    def cursor_x(self, index: int, zeile: int | None = None) -> float:
        """Stelle des Cursors vor dem Zeichen ``index`` vom linken Rand der Spalte (in der Zeile, die ``index`` enthält, oder in ``zeile``)."""
        zi = self.zeile_von(index) if zeile is None else zeile
        z = self.zeilen[zi]
        index = max(z.box.start, min(index, z.ende))
        if self.ebenen is not None and z.ende > z.box.start:
            pos, lev = self.zeichenpositionen(zi)
            i = index if index < z.ende else z.ende - 1
            if i in pos:
                links, rechts = pos[i]
                gerade = lev[i] % 2 == 0
                return (links if gerade else rechts) if index < z.ende else (rechts if gerade else links)
        breite = sum(self.vorschuebe[z.box.start:index])
        luecken = sum(1 for c in self.text[z.box.start:index] if c in LEERZEICHEN) if z.wort_zuschlag else 0
        return z.x + breite + luecken * z.wort_zuschlag

    def zeile_bei_y(self, y: float) -> int:
        for i, z in enumerate(self.zeilen):
            if y < z.y + z.hoehe:
                return i
        return len(self.zeilen) - 1

    def treffer(self, x: float, y: float) -> int:
        """Zeichenstelle des Cursors für den Punkt (x, y) im Absatz: die Zeile nach y, darin die nächste Zeichengrenze."""
        if not self.zeilen:
            return 0
        zi = self.zeile_bei_y(y)
        z = self.zeilen[zi]
        ende = z.ende - (1 if self.text[z.box.start:z.ende].endswith(("\n", " ")) else 0)
        best, abstand = z.box.start, float("inf")
        for i in range(z.box.start, ende + 1):
            d = abs(self.cursor_x(i, zi) - x)
            if d < abstand:
                best, abstand = i, d
        return best
