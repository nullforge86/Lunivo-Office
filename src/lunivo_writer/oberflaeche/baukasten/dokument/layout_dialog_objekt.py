"""Das Fenster „Layout“ eines Bildes oder freien Objekts nach der Vorlage (Fotos „Im Textfluss“ und „SmartArt“).

    d = layout_dialog_fuer(art)(parent, werte)            # art: "smartart", "form", "bild" … oder None (Bild im Text)
    if d.exec(): neu = d.werte()

Baut auf ``LayoutDialog`` (layout_dialog.py, unverändert) auf und ändert nur das Aussehen:
- Reiter „Position“ ist bei „Im Textfluss“ ganz grau (Felder, Optionen);
- „Relativ“ bei Höhe und Breite ist wie in der Vorlage immer grau;
- Abstand zum Text steht in der Reihenfolge Oben, Unten, Links, Rechts;
- bei SmartArt sind Drehung, „Relativ zur Originalbildgröße“ und „Zurücksetzen“ gesperrt und die Originalgröße leer.
"""
from __future__ import annotations

from functools import partial

from PySide6.QtWidgets import QGroupBox, QPushButton

from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import gruppe, FormularGitter
from lunivo_writer.oberflaeche.baukasten.dokument.layout_dialog import LayoutDialog
from lunivo_writer.oberflaeche.baukasten.basis.mass import RAND_DIALOG_GRUPPE

OHNE_ORIGINAL = ("smartart",)                           # Arten ohne Originalgröße (Drehung, Original-Skalierung, Zurücksetzen gesperrt)


class LayoutDialogObjekt(LayoutDialog):
    def __init__(self, parent=None, werte: dict | None = None, art: str | None = None):
        self._art = art
        super().__init__(parent, werte)
        self._abstand_ordnen()
        self._relativ_sperren()
        if art in OHNE_ORIGINAL:
            self._ohne_original()
        self._pruefen()

    # ---- Reiter Position: bei „Im Textfluss“ alles grau ----------------------------------------------------------------------
    def _pruefen(self) -> None:
        super()._pruefen()
        if not hasattr(self, "h"):
            return
        an = self.kacheln.aktuell() != "textfluss"
        for box in (self.h["box"], self.v["box"], self.mit_text.parentWidget()):
            box.setEnabled(an)

    # ---- Reiter Textumbruch: Oben, Unten, Links, Rechts -----------------------------------------------------------------------
    def _abstand_ordnen(self) -> None:
        alt = self._abstand_box
        seite = alt.parentWidget()
        neu = gruppe(alt.title()); g = FormularGitter(neu); g.setContentsMargins(*RAND_DIALOG_GRUPPE)
        for schl, text in (("oben", "Oben"), ("unten", "Unten"), ("links", "Links"), ("rechts", "Rechts")):
            g.zeile(text + ":", self.abstand[schl])
        seite.layout().replaceWidget(alt, neu)
        alt.hide(); alt.setParent(None); alt.deleteLater()
        self._abstand_box = neu
        neu.setEnabled(self.kacheln.aktuell() in ("quadrat", "passend", "transparent"))

    # ---- Reiter Größe ---------------------------------------------------------------------------------------------------------
    def _relativ_sperren(self) -> None:
        for m in (self.hoehe, self.breite):
            m["r_abs"].setChecked(True)
            for k in ("r_rel", "proz", "bezug"):
                m[k].setEnabled(False)
            m["r_rel"].setEnabled(False)

    def _ohne_original(self) -> None:
        self.skal_original.setChecked(False)
        for x in (self.drehung, self.skal_original):
            x.setEnabled(False)
        for b in self.findChildren(QPushButton):
            if b.text() == "Zurücksetzen":
                b.setEnabled(False)
        self.orig_text.setText("")

    def _orig_anzeigen(self) -> None:
        if getattr(self, "_art", None) in OHNE_ORIGINAL:
            self.orig_text.setText("")
        else:
            super()._orig_anzeigen()


def layout_dialog_fuer(art: str | None):
    """Der Fensterbau für die Objektart: ``layout_dialog_fuer(art)(parent, werte)``."""
    return partial(LayoutDialogObjekt, art=art)
