"""Abschnittsoperationen der Sitzung: Abschnittswechsel, Seiteneinrichtung, Kopf- und Fußzeilen, Dokumenteigenschaften. Ohne Qt."""
from __future__ import annotations

import dataclasses

from lunivo_writer.modelle.seite import PageSettings

from lunivo_writer.core.document.dokument import ABSCHNITT_BEGINN, Absatz, Abschnitt, Position
from .verlauf import BearbeitungsFehler, schritt

KOPF_FUSS = ("header", "footer", "first_header", "first_footer", "even_header", "even_footer")
_SEITENFELDER = {f.name for f in dataclasses.fields(PageSettings)}


class AbschnittTeil:
    def _abschnitt(self, index: int) -> Abschnitt:
        if not 0 <= index < len(self.dokument.abschnitte):
            raise BearbeitungsFehler(f"Kein Abschnitt {index}")
        return self.dokument.abschnitte[index]

    def abschnitt_index(self, block_id: int) -> int:
        """Der Abschnitt (Index), in dem der Absatz oder die Tabelle steht."""
        try:
            return self.dokument.abschnitte.index(self.dokument.abschnitt_von(block_id))
        except KeyError as e:
            raise BearbeitungsFehler(str(e)) from None

    @schritt("Abschnittswechsel", "abschnitt")
    def abschnitt_einfuegen(self, pos: Position | None = None, beginn: str = "naechste", seite: PageSettings | None = None) -> int:
        """Beginnt an der Stelle einen neuen Abschnitt (nur im Fließtext, nicht in einer Tabelle). Der neue Abschnitt übernimmt die
        Seiteneinrichtung des bisherigen, wenn keine angegeben ist. Gibt den Index des neuen Abschnitts zurück."""
        if beginn not in ABSCHNITT_BEGINN:
            raise BearbeitungsFehler(f"Unbekannter Abschnittsbeginn: {beginn}")
        pos = self._pruefe_position(self.auswahl.kopf if pos is None else pos)
        besitzer, bloecke, i, _a = self.dokument.finde(pos.absatz_id)
        if not isinstance(besitzer, Abschnitt):
            raise BearbeitungsFehler("In einer Tabelle kann kein Abschnitt beginnen")
        if pos.versatz > 0 or i == 0:
            ziel = self._teilen(pos)
            i += 1
        else:
            ziel = pos
        if i > 0 and not isinstance(bloecke[i - 1], Absatz):      # der Abschnitt davor endet immer mit einem Absatz
            self._liste(bloecke, i, 0, [Absatz(self._id())])
            i += 1
        n = self.dokument.abschnitte.index(besitzer)
        neu = Abschnitt(self._id(), list(bloecke[i:]), (seite or besitzer.seite).copy(), beginn)
        self._liste(bloecke, i, len(bloecke) - i)
        self._liste(self.dokument.abschnitte, n + 1, 0, [neu])
        self._beruehrt(*(b.id for b in neu.bloecke))
        self._setze(ziel)
        return n + 1

    @schritt("Abschnittswechsel", "abschnitt")
    def abschnitt_vor_einfuegen(self, block_id: int, beginn: str = "naechste", seite: PageSettings | None = None) -> int:
        """Beginnt einen neuen Abschnitt unmittelbar vor dem Block (Absatz, Tabelle oder Rahmen) im Haupttext — der Block davor beschließt
        den bisherigen. Gibt den Index des neuen Abschnitts zurück."""
        if beginn not in ABSCHNITT_BEGINN:
            raise BearbeitungsFehler(f"Unbekannter Abschnittsbeginn: {beginn}")
        f = self.dokument.finde(block_id)
        if f is None:
            raise BearbeitungsFehler(f"Kein Block mit der Id {block_id}")
        besitzer, bloecke, i, _b = f
        if not isinstance(besitzer, Abschnitt) or i == 0:
            raise BearbeitungsFehler("Ein Abschnitt beginnt nur zwischen zwei Blöcken des Haupttexts")
        n = self.dokument.abschnitte.index(besitzer)
        neu = Abschnitt(self._id(), list(bloecke[i:]), (seite or besitzer.seite).copy(), beginn)
        self._liste(bloecke, i, len(bloecke) - i)
        self._liste(self.dokument.abschnitte, n + 1, 0, [neu])
        self._beruehrt(*(b.id for b in neu.bloecke))
        return n + 1

    @schritt("Abschnittswechsel entfernen", "abschnitt")
    def abschnitt_entfernen(self, index: int, behalte: str = "vorher") -> None:
        """Hebt den Wechsel vor dem Abschnitt ``index`` auf: Sein Text gehört danach zum Abschnitt davor. ``behalte`` bestimmt,
        wessen Seiteneinrichtung gilt (``vorher`` oder ``nachher``)."""
        if index < 1:
            raise BearbeitungsFehler("Vor dem ersten Abschnitt gibt es keinen Wechsel")
        hinten, vorn = self._abschnitt(index), self._abschnitt(index - 1)
        if behalte not in ("vorher", "nachher"):
            raise BearbeitungsFehler(f"Unbekannte Angabe: {behalte}")
        if behalte == "nachher":
            self._attr(vorn, "seite", hinten.seite)
        self._beruehrt(*(b.id for b in hinten.bloecke))
        self._liste(vorn.bloecke, len(vorn.bloecke), 0, hinten.bloecke)
        self._liste(self.dokument.abschnitte, index, 1)

    @schritt("Abschnittsbeginn", "abschnitt")
    def abschnitt_beginn_setzen(self, index: int, beginn: str) -> None:
        if beginn not in ABSCHNITT_BEGINN:
            raise BearbeitungsFehler(f"Unbekannter Abschnittsbeginn: {beginn}")
        self._attr(self._abschnitt(index), "beginn", beginn)

    # ---- Seiteneinrichtung -------------------------------------------------------------------------------------------------
    @schritt("Seite einrichten", "seite")
    def seite_setzen(self, index: int | None = None, einrichtung: PageSettings | None = None, **felder) -> None:
        """Ändert die Seiteneinrichtung eines Abschnitts (``index``; ``None``: aller Abschnitte) — entweder ganz (``einrichtung``)
        oder einzelne Felder von ``PageSettings`` (Papier, Ränder, Spalten, Seitenfarbe, Rahmen, Wasserzeichen, Zeilennummern,
        Seitenzahlformat …)."""
        fremd = set(felder) - _SEITENFELDER
        if fremd:
            raise BearbeitungsFehler(f"Unbekanntes Feld der Seiteneinrichtung: {', '.join(sorted(fremd))}")
        ziele = self.dokument.abschnitte if index is None else [self._abschnitt(index)]
        for abschnitt in ziele:
            neu = (einrichtung or abschnitt.seite).copy()
            for name, wert in felder.items():
                setattr(neu, name, wert)
            for name in ("width_mm", "height_mm"):
                if getattr(neu, name) <= 0:
                    raise BearbeitungsFehler("Das Papier braucht eine Breite und eine Höhe")
            if neu.margin_left_mm + neu.margin_right_mm >= neu.width_mm or neu.margin_top_mm + neu.margin_bottom_mm >= neu.height_mm:
                raise BearbeitungsFehler("Die Ränder lassen keinen Platz für Text")
            if int(neu.spalten) < 1:
                raise BearbeitungsFehler("Eine Seite hat mindestens eine Spalte")
            if neu != abschnitt.seite:
                self._attr(abschnitt, "seite", neu)

    @schritt("Seite einrichten", "seite")
    def seite_ersetzen(self, index: int, einrichtung: PageSettings, ressourcen: dict | None = None) -> None:
        """Setzt die Seiteneinrichtung eines Abschnitts ganz; ``ressourcen`` sind die Bilddaten, auf die sie (Kopf-/Fußzeilenbilder)
        verweist."""
        for name, daten in (ressourcen or {}).items():
            if self.dokument.ressourcen.get(name) != daten:
                self._dict(self.dokument.ressourcen, name, daten)
        self.seite_setzen(index, einrichtung)

    @schritt("Kopf- und Fußzeile", "seite")
    def kopf_fuss_setzen(self, index: int | None, welche: str, text: str | None = None, align: str | None = None,
                         fmt: dict | None = None) -> None:
        """Setzt Text, Ausrichtung oder Format einer Kopf-/Fußzeile (``welche``: header, footer, first_header, first_footer,
        even_header, even_footer). ``index`` ``None``: in allen Abschnitten."""
        if welche not in KOPF_FUSS:
            raise BearbeitungsFehler(f"Unbekannte Kopf-/Fußzeile: {welche}")
        ziele = self.dokument.abschnitte if index is None else [self._abschnitt(index)]
        for abschnitt in ziele:
            alt = getattr(abschnitt.seite, welche)
            neu = alt.kopie(text, align)
            if fmt is not None:
                neu.fmt = dict(fmt)
            if text is not None and text != alt.text:
                neu.runs = []                                    # eigene Textstücke gelten nur zum alten Text
            if neu != alt:
                seite = abschnitt.seite.copy()
                setattr(seite, welche, neu)
                self._attr(abschnitt, "seite", seite)

    # ---- Dokumenteigenschaften ------------------------------------------------------------------------------------------------
    @schritt("Dokumenteigenschaft", "meta")
    def eigenschaft_setzen(self, name: str, wert=None) -> None:
        """Titel, Autor, Sprache, Zitierweise, Kennwort … — ``None`` entfernt die Eigenschaft."""
        if wert is None:
            if name in self.dokument.eigenschaften:
                self._dict(self.dokument.eigenschaften, name)
        elif self.dokument.eigenschaften.get(name, self) != wert:
            self._dict(self.dokument.eigenschaften, name, wert)
