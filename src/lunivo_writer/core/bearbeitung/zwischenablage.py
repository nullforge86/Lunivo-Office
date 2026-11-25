"""Ausschnitte der Sitzung: Bereiche als Blockliste kopieren und einfügen (Zwischenablage, Textbausteine). Ohne Qt."""
from __future__ import annotations

import copy
import dataclasses

from lunivo_writer.core.dokument.dokument import Absatz, Auswahl, InlineObjekt, Position, Rahmen, teile
from .verlauf import schritt


class ZwischenablageTeil:
    def ausschnitt(self, auswahl: Auswahl | None = None) -> list:
        """Eine unabhängige Kopie des Bereichs als Blockliste. Liegt der Bereich in einem Textfluss, sind Tabellen dazwischen
        enthalten; sonst nur die Absätze."""
        start, ende = self._bereich(auswahl)
        if start == ende:
            return []
        if start.absatz_id == ende.absatz_id:
            a = self._absatz(start.absatz_id)
            mitte = teile(teile(a.inhalte, start.versatz)[1], ende.versatz - start.versatz)[0]
            return [Absatz(0, copy.deepcopy(mitte), dict(a.format), dict(a.zeichenformat), a.liste_id, a.ebene)]
        _b1, liste1, i, a = self.dokument.finde(start.absatz_id)
        _b2, liste2, j, b = self.dokument.finde(ende.absatz_id)
        if liste1 is liste2:
            bloecke = copy.deepcopy(liste1[i:j + 1])
            bloecke[0].inhalte = teile(bloecke[0].inhalte, start.versatz)[1]
            bloecke[-1].inhalte = teile(bloecke[-1].inhalte, ende.versatz)[0]
            return bloecke
        kopien = []
        for absatz, von, bis in self._stuecke(start, ende):
            mitte = teile(teile(absatz.inhalte, von)[1], bis - von)[0]
            kopien.append(Absatz(0, copy.deepcopy(mitte), dict(absatz.format), dict(absatz.zeichenformat), absatz.liste_id, absatz.ebene))
        return kopien

    @schritt("Einfügen", "text")
    def ausschnitt_einfuegen(self, bloecke: list, pos: Position | None = None) -> Position:
        """Fügt eine Blockliste (aus ``ausschnitt`` oder selbst gebaut) ein. Ein einzelner Absatz fließt in den Text; bei mehreren
        Blöcken wächst der erste an den Text davor, der letzte an den Text danach. Alle Ids werden neu vergeben."""
        if pos is None:
            if not self.auswahl.leer:
                self.loeschen()
            pos = self.auswahl.kopf
        pos = self._pruefe_position(pos)
        bloecke = copy.deepcopy(list(bloecke))
        if not bloecke:
            return pos
        self._neue_ids(bloecke)
        _bes, liste, i, a = self.dokument.finde(pos.absatz_id)
        if len(bloecke) == 1 and isinstance(bloecke[0], Absatz):
            n = bloecke[0].laenge
            if a.laenge == 0:
                self._attr(a, "format", bloecke[0].format)
                self._attr(a, "format_aufgeloest", bloecke[0].format_aufgeloest)
                self._attr(a, "zeichenformat", bloecke[0].zeichenformat)
                self._attr(a, "liste_id", bloecke[0].liste_id)
                self._attr(a, "ebene", bloecke[0].ebene)
            self._einsetzen(a, pos.versatz, bloecke[0].inhalte)
            ziel = Position(a.id, pos.versatz + n)
            self._setze(ziel)
            return ziel
        hinten = self._absatz(self._teilen(pos).absatz_id)
        mitte = bloecke
        if isinstance(bloecke[0], Absatz):
            erster, mitte = bloecke[0], bloecke[1:]
            if a.laenge == 0:
                self._attr(a, "format", erster.format); self._attr(a, "liste_id", erster.liste_id); self._attr(a, "ebene", erster.ebene)
                self._attr(a, "format_aufgeloest", erster.format_aufgeloest)
            self._einsetzen(a, a.laenge, erster.inhalte)
        ziel = Position(hinten.id, 0)
        if mitte and isinstance(mitte[-1], Absatz):
            letzter, mitte = mitte[-1], mitte[:-1]
            n = letzter.laenge
            if hinten.laenge == 0:
                self._attr(hinten, "format_aufgeloest", letzter.format_aufgeloest)
                self._attr(hinten, "format", letzter.format); self._attr(hinten, "liste_id", letzter.liste_id)
                self._attr(hinten, "ebene", letzter.ebene)
            self._einsetzen(hinten, 0, letzter.inhalte)
            ziel = Position(hinten.id, n)
        self._liste(liste, i + 1, 0, mitte)
        self._beruehrt(*(b.id for b in mitte))
        self._setze(ziel)
        return ziel

    def _neue_ids(self, bloecke: list) -> None:
        for b in bloecke:
            b.id = self._id()
            if isinstance(b, Absatz):
                b.inhalte = [dataclasses.replace(x, id=self._id()) if isinstance(x, InlineObjekt) else x for x in b.inhalte]
                if b.liste_id is not None and b.liste_id not in self.dokument.listen:
                    b.liste_id = None; b.ebene = 0
            elif isinstance(b, Rahmen):
                self._neue_ids(b.bloecke)
            else:
                for zeile in b.zellen:
                    for zelle in zeile:
                        self._neue_ids(zelle.bloecke)
