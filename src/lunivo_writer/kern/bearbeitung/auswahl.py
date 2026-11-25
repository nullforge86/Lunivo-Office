"""Schreibmarke und Auswahl der Bearbeitungssitzung. Ohne Qt."""
from __future__ import annotations

from lunivo_writer.kern.dokument.dokument import Absatz, Auswahl, Position
from .verlauf import BearbeitungsFehler


class AuswahlTeil:
    """Hält ``self._auswahl`` (Anker und Kopf; ist die Auswahl leer, ist der Kopf die Schreibmarke)."""

    @property
    def auswahl(self) -> Auswahl:
        return self._auswahl

    def setze_auswahl(self, anker: Position, kopf: Position | None = None) -> None:
        anker = self._pruefe_position(anker)
        kopf = anker if kopf is None else self._pruefe_position(kopf)
        self._auswahl = Auswahl(anker, kopf)
        self.tippformat = None

    def auswahl_nachtragen(self, auswahl: Auswahl) -> None:
        """Setzt die Auswahl nach einem Schritt, der sie nicht kannte (Eingabe in der Ansicht): sie gilt auch als Auswahl nach dem
        letzten Schritt, damit Wiederholen die Schreibmarke dorthin zurückbringt. Erzeugt keinen eigenen Schritt."""
        self._auswahl = Auswahl(self._pruefe_position(auswahl.anker), self._pruefe_position(auswahl.kopf))
        self.tippformat = None
        if self._rueck and self._offen is None:
            self._rueck[-1].nach = self._auswahl

    def _setze(self, pos: Position) -> None:
        self._auswahl = Auswahl(pos, pos)
        self.tippformat = None

    def _pruefe_position(self, pos: Position) -> Position:
        pos = Position(*pos)
        a = self._absatz(pos.absatz_id)
        if not 0 <= pos.versatz <= a.laenge:
            raise BearbeitungsFehler(f"Textstelle {pos.versatz} liegt außerhalb des Absatzes (Länge {a.laenge})")
        return pos

    def _absatz(self, absatz_id: int) -> Absatz:
        try:
            return self.dokument.absatz(absatz_id)
        except KeyError as e:
            raise BearbeitungsFehler(str(e)) from None

    def _bereich(self, auswahl: Auswahl | None = None) -> tuple:
        """(Anfang, Ende) der Auswahl in Dokumentreihenfolge."""
        auswahl = self._auswahl if auswahl is None else Auswahl(self._pruefe_position(auswahl[0]), self._pruefe_position(auswahl[1]))
        a, b = auswahl
        if a.absatz_id == b.absatz_id:
            return (a, b) if a.versatz <= b.versatz else (b, a)
        folge = self.dokument.reihenfolge()
        return (a, b) if folge[a.absatz_id] < folge[b.absatz_id] else (b, a)

    def _stuecke(self, start: Position, ende: Position) -> list:
        """Die Absätze zwischen zwei Stellen als (Absatz, von, bis) in Dokumentreihenfolge."""
        if start.absatz_id == ende.absatz_id:
            return [(self._absatz(start.absatz_id), start.versatz, ende.versatz)]
        stuecke = []
        drin = False
        for a in self.dokument.absaetze():
            if a.id == start.absatz_id:
                drin = True
                stuecke.append((a, start.versatz, a.laenge))
            elif a.id == ende.absatz_id:
                stuecke.append((a, 0, ende.versatz))
                break
            elif drin:
                stuecke.append((a, 0, a.laenge))
        return stuecke

    def _ziel_absaetze(self, auswahl: Auswahl | None = None, absatz_ids=None) -> list:
        if absatz_ids is not None:
            return [self._absatz(i) for i in absatz_ids]
        return [a for a, _v, _b in self._stuecke(*self._bereich(auswahl))]

    def _auswahl_retten(self, ersatz: Position) -> None:
        """Nach einer Operation, die Text entfernt hat: Eine Schreibmarke hinter dem Absatzende rückt ans Ende; steht sie in einem
        Absatz, den es nicht mehr gibt, geht sie nach ``ersatz``."""
        vorhanden = {a.id: a.laenge for a in self.dokument.absaetze()}
        if any(p.absatz_id not in vorhanden for p in self.auswahl):
            self._setze(ersatz)
        elif any(p.versatz > vorhanden[p.absatz_id] for p in self.auswahl):
            anker, kopf = (Position(p.absatz_id, min(p.versatz, vorhanden[p.absatz_id])) for p in self.auswahl)
            self._auswahl = Auswahl(anker, kopf)
            self.tippformat = None
