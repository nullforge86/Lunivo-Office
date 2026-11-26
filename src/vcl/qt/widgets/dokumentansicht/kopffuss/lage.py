"""Lage der Teile auf dem Blatt beim Bearbeiten von Kopf- und Fußzeile: Felder über Kopf- und Fußbereich, Linien, Etiketten, die Leiste neben
dem Etikett des aktiven Bereichs und das Absatz-Symbol links vom aktiven Feld. Alle Abstände sind benannte Maße des Baukastens."""
from __future__ import annotations

from PySide6.QtCore import QRect, QRectF
from PySide6.QtGui import QFont

from writer.funktionen.kopffuss import blatttexte as T
from writer.werte import mm_zu_px
from vcl.qt.widgets.bausteine.abstaende import (KOPFFUSS_ETIKETT_ABSTAND, KOPFFUSS_FELD_HOEHE_MM, KOPFFUSS_FUSS_VON_UNTEN_MM, KOPFFUSS_KOPF_OBEN_MM,
                                                KOPFFUSS_LEISTE_ABSTAND, KOPFFUSS_LINIE_ABSTAND, KOPFFUSS_LINIE_HOEHE, KOPFFUSS_SCHRIFT_PX,
                                                KOPFFUSS_SCHRIFT_PX_MIN)

def _oben(zone: str) -> bool:
    """Ob die Zone am oberen Blattrand liegt (die erste der beiden Zonen)."""
    return zone == T.ZONEN[0]


class LageTeil:
    """Baustein des ``KopfFussBearbeiter``: wo die Teile liegen."""

    def _rect(self, zone: str) -> QRectF:
        """Das Feld der Zone auf dem bearbeiteten Blatt, in den Koordinaten der Ansicht."""
        ed = self.ed
        zoom = ed.zoom
        b = ed._blatt(self.blatt)
        oben = ed.blatt_oben(self.blatt)
        hoehe = mm_zu_px(KOPFFUSS_FELD_HOEHE_MM) * zoom
        y = oben + mm_zu_px(KOPFFUSS_KOPF_OBEN_MM) * zoom if _oben(zone) else oben + b["H"] - mm_zu_px(KOPFFUSS_FUSS_VON_UNTEN_MM) * zoom
        return QRectF(b["x"] + b["ml"], y, b["cw"], hoehe)

    def _felder_legen(self) -> None:
        groesse = max(KOPFFUSS_SCHRIFT_PX_MIN, round(KOPFFUSS_SCHRIFT_PX * self.ed.zoom))
        alt, self._laedt = self._laedt, True                    # Lage und Schrift sind keine Änderung des Textes
        for z in T.ZONEN:
            g = self._rect(z).toRect()
            feld = self.felder[z]
            if feld.geometry() != g:
                feld.setGeometry(QRect(g))
            if getattr(feld, "schrift_px", None) != groesse:
                schrift = QFont(self.ed.ansicht.font())
                schrift.setPixelSize(groesse)
                feld.setFont(schrift)
                feld.schrift_px = groesse
            if getattr(feld, "zoom_basis", None) != self.ed.zoom:
                self._basis_anwenden(z)
        self._laedt = alt

    def _platzieren(self) -> None:
        if not self.aktiv:
            return
        blatt = self.ed.ansicht.blatt(self.blatt)
        self._felder_legen()
        for z in T.ZONEN:
            g = self.felder[z].geometry()
            linie_y = g.bottom() + KOPFFUSS_LINIE_ABSTAND if _oben(z) else g.top() - KOPFFUSS_LINIE_ABSTAND
            self.linien[z].setGeometry(round(blatt.left()), linie_y - KOPFFUSS_LINIE_HOEHE // 2, round(blatt.width()), KOPFFUSS_LINIE_HOEHE)
            etikett = self.etiketten[z]
            # oben: Etikett unter der Linie; unten: Etikett über der Linie
            y = linie_y + KOPFFUSS_ETIKETT_ABSTAND if _oben(z) else linie_y - etikett.height() - KOPFFUSS_ETIKETT_ABSTAND
            etikett.move(g.left(), max(0, y))
        self._leiste_legen(blatt)
        g = self.felder[self.zone].geometry()
        self.absatz.move(max(0, g.left() - self.absatz.width() - KOPFFUSS_ETIKETT_ABSTAND), g.top())
        self._bilder_zeigen()

    def _leiste_legen(self, blatt: QRectF) -> None:
        """Die Leiste neben das Etikett des aktiven Bereichs; passt sie dort nicht aufs Blatt, unter (oben) bzw. über (unten) das Etikett."""
        etikett = self.etiketten[self.zone].geometry()
        leiste = self.leiste
        leiste.adjustSize()
        rechts = round(blatt.right()) - KOPFFUSS_ETIKETT_ABSTAND
        x = etikett.right() + KOPFFUSS_LEISTE_ABSTAND
        if x + leiste.width() <= rechts:
            leiste.move(x, max(0, etikett.center().y() - leiste.height() // 2))
            return
        x = max(round(blatt.left()) + KOPFFUSS_ETIKETT_ABSTAND, min(etikett.left(), rechts - leiste.width()))
        y = etikett.bottom() + KOPFFUSS_ETIKETT_ABSTAND if _oben(self.zone) else etikett.top() - leiste.height() - KOPFFUSS_ETIKETT_ABSTAND
        leiste.move(x, max(0, y))

    def _ins_bild_holen(self) -> None:
        """Den aktiven Bereich in den sichtbaren Ausschnitt rollen (die Fußzeile liegt meist unterhalb des Fensters)."""
        eltern = self.ed.viewport().parentWidget()
        while eltern is not None and not hasattr(eltern, "ensureWidgetVisible"):
            eltern = eltern.parentWidget()
        if eltern is not None:
            eltern.ensureWidgetVisible(self.feld)

    def _zone_bei(self, pos) -> tuple[str, int] | None:
        """Der Kopf- oder Fußbereich unter einem Punkt der Ansicht: (Zone, Blatt) – der Streifen des Blattes über bzw. unter dem Text."""
        ed = self.ed
        blatt = max(0, int(ed._blatt_bei_y(pos.y())))
        if not ed.ansicht.blatt(blatt).contains(pos):
            return None
        merke, self.blatt = self.blatt, blatt
        bereiche = {z: self._rect(z) for z in T.ZONEN}
        self.blatt = merke
        for z, r in bereiche.items():
            if (pos.y() <= r.bottom() + KOPFFUSS_LINIE_ABSTAND) if _oben(z) else (pos.y() >= r.top() - KOPFFUSS_LINIE_ABSTAND):
                return z, blatt
        return None
