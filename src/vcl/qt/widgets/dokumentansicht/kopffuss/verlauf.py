"""Rückgängig und Wiederholen beim Bearbeiten von Kopf- und Fußzeile auf dem Blatt (Schnellzugriff oben, Start-Leiste): getippter Text im Feld und
Format/Ausrichtung der Zeile in einer gemeinsamen Reihenfolge.

Ein Schritt ist entweder ``("text", Zone)`` – ein Tippschritt des Feldes – oder ``("zeile", Zone, vorher, nachher)`` – Format und Ausrichtung
der Zeile vor und nach der Änderung."""
from __future__ import annotations

TEXT, ZEILE = "text", "zeile"


class VerlaufTeil:
    """Baustein des ``KopfFussBearbeiter``: die Schritte der Bearbeitung."""

    def _verlauf_beginnen(self) -> None:
        self._verlauf, self._wieder = [], []

    def _textschritte_verwerfen(self) -> None:
        """Der Text der Felder wurde neu gesetzt: ihre Tippschritte gibt es nicht mehr."""
        self._verlauf = [a for a in self._verlauf if a[0] != TEXT]
        self._wieder = [a for a in self._wieder if a[0] != TEXT]

    def _stand(self) -> tuple:
        zeile = self.hf()
        return (self.zone, dict(zeile.fmt), zeile.align)

    def _merken(self, vorher: tuple) -> None:
        nachher = self._stand()
        if nachher != vorher:
            self._verlauf.append((ZEILE, vorher[0], vorher, nachher))
            self._wieder.clear()

    def _text_gemerkt(self, zone: str) -> None:
        if self.aktiv and not self._laedt:
            self._verlauf.append((TEXT, zone))
            self._wieder.clear()

    def _stand_setzen(self, stand: tuple) -> None:
        zone, fmt, ausrichtung = stand
        alt, self.zone = self.zone, zone
        feldname = self._feldname(zone)

        def setze(seite) -> None:
            zeile = getattr(seite, feldname).kopie(align=ausrichtung)
            zeile.fmt = dict(fmt)
            setattr(seite, feldname, zeile)
        self.aendern(setze, neu_laden=False)
        self._zeile_ausrichten()
        self._basis_anwenden(zone)
        self.zone = alt

    @staticmethod
    def _text_schritt(feld, rueck: bool) -> None:
        """Rückgängig/Wiederholen im Feld, bis sich der Text ändert (Schriftschritte, die das Feld dazwischen merkt, zählen nicht)."""
        vor = feld.toPlainText()
        dokument = feld.document()
        while dokument.isUndoAvailable() if rueck else dokument.isRedoAvailable():
            feld.undo() if rueck else feld.redo()
            if feld.toPlainText() != vor:
                break

    def rueckgaengig(self) -> None:
        self.speichern()
        if not self._verlauf:
            return
        schritt = self._verlauf.pop()
        if schritt[0] == TEXT:
            self._text_schritt(self.felder[schritt[1]], rueck=True)
        else:
            self._stand_setzen(schritt[2])
        self._wieder.append(schritt)

    def wiederholen(self) -> None:
        if not self._wieder:
            return
        schritt = self._wieder.pop()
        if schritt[0] == TEXT:
            self._text_schritt(self.felder[schritt[1]], rueck=False)
        else:
            self._stand_setzen(schritt[3])
        self._verlauf.append(schritt)
