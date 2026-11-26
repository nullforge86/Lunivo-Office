"""Bilder in Kopf- und Fußzeile: ein Bild aus einer Datei frei platziert in die Zeile legen, die gerade bearbeitet wird.

Das Bild wird ein freies Objekt des Dokuments, das auf jedem Blatt des Abschnitts steht (Befehl über ``writer``). Nach dem Einfügen endet die
Textbearbeitung und das Bild ist ausgewählt: Verschieben, Größe ändern und Löschen gehen wie bei jedem frei platzierten Bild."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

from writer.funktionen import bearbeiten as _bearbeiten
from writer.funktionen.kopffuss import blatttexte as T
from writer.werte import mm_zu_px
from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_BILD_HOEHE_MM


class BildAktionenTeil:
    """Baustein des ``KopfFussBearbeiter``: Bilder der Zeile."""

    def bild_einfuegen(self, pfad: str) -> bool:
        """Das Bild der Datei in die aktive Zeile legen (höchstens ``KOPFFUSS_BILD_HOEHE_MM`` hoch, Seitenverhältnis bleibt). ``False``: kein lesbares Bild."""
        try:
            with open(pfad, "rb") as datei:
                roh = datei.read()
        except OSError:
            return False
        bild = QImage()
        if not bild.loadFromData(roh):
            return False
        breite, hoehe = float(bild.width()), float(bild.height())
        hoechstens = mm_zu_px(KOPFFUSS_BILD_HOEHE_MM)
        if hoehe > hoechstens:
            breite, hoehe = breite * hoechstens / hoehe, hoechstens
        self.speichern()
        ed = self.ed
        abschnitt, zone = ed.abschnitt_nr(), self.zone
        ergebnis = []

        def befehl() -> bool:
            ergebnis.append(_bearbeiten.kopffuss_bild_einfuegen(ed.kennung, abschnitt, zone, breite, hoehe, roh))
            return ergebnis[0] is not None
        if not ed.ansicht._befehl(befehl) or ergebnis[0] is None:
            return False
        ed.pageApplied.emit()
        self.beende()                                           # das Bild liegt auf dem Blatt: jetzt ist es zu sehen und lässt sich fassen
        ed.ansicht.gewaehltes_objekt = ergebnis[0]
        ed.ansicht.update()
        ed.freiAuswahlGeaendert.emit()
        return True

    # ---- Bilder über den Feldern zeigen ------------------------------------------------------------------------------------------------------
    def _bilder_zeigen(self) -> None:
        """Solange die Zeile bearbeitet wird, liegen die Textfelder über dem Blatt: die Bilder der Kopf- und Fußzeile werden deshalb als Abbild
        über die Felder gelegt (nur zum Ansehen; gefasst werden sie nach dem Beenden der Textbearbeitung)."""
        ed = self.ed
        blatt = ed.ansicht.blatt(self.blatt)
        stand = (ed.revision, ed.zoom, self.blatt, blatt.left(), blatt.top())
        if stand == self._abbild_stand:                         # nichts hat sich geändert: die Abbilder liegen schon richtig
            return
        self._abbild_stand = stand
        orte = ed.ansicht.ergebnis().objekte
        gezeigt = set()
        for zone in T.ZONEN:
            for oid in self.bilder(zone):
                ort, objekt = orte.get(oid), _bearbeiten.dok_objekt(ed.kennung, oid)
                bild = ed.objekt_bild(objekt) if objekt is not None and ort is not None else None
                if bild is None:
                    continue
                abbild = self._abbilder.get(oid)
                if abbild is None:
                    abbild = self._abbilder[oid] = QLabel(ed.viewport())
                    abbild.setAttribute(Qt.WA_TransparentForMouseEvents)
                    abbild.setScaledContents(True)
                abbild.setPixmap(QPixmap.fromImage(bild))
                r = ort[1]
                abbild.setGeometry(round(blatt.left() + r.x * ed.zoom), round(blatt.top() + r.y * ed.zoom), round(r.width * ed.zoom), round(r.height * ed.zoom))
                abbild.show()
                abbild.raise_()
                gezeigt.add(oid)
        for oid, abbild in self._abbilder.items():
            if oid not in gezeigt:
                abbild.hide()

    def _bilder_verbergen(self) -> None:
        self._abbild_stand = None
        for abbild in self._abbilder.values():
            abbild.hide()

    def bilder(self, zone: str | None = None) -> tuple[int, ...]:
        """Die Ids der Bilder in der Kopf- bzw. Fußzeile des Abschnitts an der Schreibmarke."""
        return _bearbeiten.kopffuss_bilder(self.ed.kennung, self.ed.abschnitt_nr(), zone or self.zone)
