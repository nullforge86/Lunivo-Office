"""Dropdowns in den Köpfen von „FÜLLUNG“ und „LINIE“ des Diagramm-Panels (Vorlage): Mixin vor ``ObjektFormatPanel``.

``_kopf_menues_bauen()`` hängt je ein ``KopfDropdown`` rechts in den Kopf von ``a_fuell`` und ``a_kontur`` (nach dem Aufbau der Seite aufzurufen). Die Wahl im
Popup setzt dieselben Felder wie die Wahl im Abschnitt (Füllart, Farbe, Muster, Struktur, Strichtyp, Kombinierter Typ, Breite) und ruft ``_neu()``; das Feld im
Kopf zeigt das aktuelle Ergebnis und wird in ``_felder_zeigen`` nachgeführt (nach jeder Änderung und nach ``setze``).
Mit ``KOPF_MENUES = False`` in der Panelklasse ist das Verhalten abgeschaltet (SmartArt).

Schlüssel der Füllung: ``farbe:#hex``, ``graduell:#hex`` (Grundfarbe), ``muster:key``, ``textur:key``, ``""`` = keine; der Linie ``strichtyp|form|breite_pt``, ``""`` = keine.
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QIcon

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.dropdown.fuell_voreinstellungen import fuell_bild, fuell_menue, graduell_paar
from lunivo_writer.ui.baukasten.dropdown.kopf_dropdown import KopfDropdown
from lunivo_writer.ui.baukasten.dropdown.linien_voreinstellungen import linien_bild, linien_menue, linien_schluessel


def _hex(farbe: str | None) -> str:
    return QColor(farbe).name() if farbe else ""


class KopfMenueMixin:
    KOPF_MENUES = True

    def _kopf_menues_bauen(self) -> None:
        if not self.KOPF_MENUES:
            return
        self.kopf_fuell = KopfDropdown(lambda p: fuell_menue(p, self._fuell_schluessel()))
        self.kopf_fuell.gewaehlt.connect(self._fuell_voreinstellung); self.kopf_fuell.an(self.a_fuell)
        self.kopf_fuell.setAccessibleName("Füllung wählen"); self.kopf_fuell.setToolTip("Füllung wählen")
        self.kopf_linie = KopfDropdown(lambda p: linien_menue(p, self._linien_schluessel()))
        self.kopf_linie.gewaehlt.connect(self._linien_voreinstellung); self.kopf_linie.an(self.a_kontur)
        self.kopf_linie.setAccessibleName("Linie wählen"); self.kopf_linie.setToolTip("Linie wählen")
        self._kopf_aktualisieren()

    # ---- Wahl im Popup → Felder des Abschnitts -------------------------------------------------------------------------------
    def _fuell_voreinstellung(self, schluessel: str) -> None:
        art, _, wert = schluessel.partition(":")
        if not schluessel:
            self.fuellung_waehlen("keine")
        elif art == "farbe":
            self.farbe.setFarbe(wert); self.fuellung_waehlen("farbe")
        elif art == "graduell":
            self.v1.setFarbe(graduell_paar(wert)[0]); self.v2.setFarbe(graduell_paar(wert)[1]); self.fuellung_waehlen("verlauf")
        elif art == "muster":
            self.muster.setCurrentIndex(max(0, self.muster.findData(wert))); self.fuellung_waehlen("muster")
        elif art == "textur":
            self.textur.setCurrentIndex(max(0, self.textur.findData(wert))); self.fuellung_waehlen("textur")
        self._neu()

    def _linien_voreinstellung(self, schluessel: str) -> None:
        if not schluessel:
            self.k_keine.setChecked(True)
        else:
            art, form, breite = schluessel.split("|")
            self.k_art.setCurrentIndex(max(0, self.k_art.findData(art)))
            self.l_kombi.setze(form); self._k_breite_setzen(float(breite))
            self.k_linie.setChecked(True)
        self._neu()

    # ---- aktuelles Ergebnis ----------------------------------------------------------------------------------------------------
    def _fuell_spec(self) -> dict:
        if self.r_auto.isChecked():
            return {}
        if self.r_keine.isChecked():
            return {"art": "keine"}
        if self.r_verlauf.isChecked():
            return {"art": "graduell", "dunkel": self.v1.farbe, "hell": self.v2.farbe}
        if self.r_textur.isChecked():
            return {"art": "textur", "key": self.textur.currentData()}
        if self.r_muster.isChecked():
            return {"art": "muster", "key": self.muster.currentData(), "farbe": self.m_farbe.farbe}
        return {"art": "farbe", "farbe": self.farbe.farbe}

    def _fuell_schluessel(self) -> str:
        s = self._fuell_spec()
        art = s.get("art")
        return {"farbe": f"farbe:{_hex(s.get('farbe'))}", "graduell": f"graduell:{_hex(s.get('dunkel'))}", "muster": f"muster:{s.get('key')}",
                "textur": f"textur:{s.get('key')}"}.get(art, "")

    def _linien_spec(self) -> dict:
        if self.k_keine.isChecked():
            return {"art": "keine"}
        farbe = (self.kv1.farbe if self.k_verlauf.isChecked() else self.k_farbe.farbe) or Farbe.GRAU
        auto = self.k_auto.isChecked()
        return {"art": "einfach" if auto else self.k_art.currentData(), "form": "einfach" if auto else self.l_kombi.aktuell(),
                "breite": 0.75 if auto else self._k_breite(), "farbe": farbe}

    def _linien_schluessel(self) -> str:
        if not self.k_linie.isChecked():
            return ""
        s = self._linien_spec()
        return linien_schluessel(s["art"], s["form"], s["breite"])

    def _kopf_aktualisieren(self) -> None:
        if not getattr(self, "kopf_fuell", None):
            return
        self.kopf_fuell.setSymbol(QIcon(fuell_bild(self._fuell_spec(), KopfDropdown.SYMBOL)))
        self.kopf_linie.setSymbol(QIcon(linien_bild(self._linien_spec(), KopfDropdown.SYMBOL)))

    def _felder_zeigen(self) -> None:
        super()._felder_zeigen()
        self._kopf_aktualisieren()
