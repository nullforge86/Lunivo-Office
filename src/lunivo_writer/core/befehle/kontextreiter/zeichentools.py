"""Befehle: Kontext-Reiter „Zeichentools“ für frei positionierte Bilder und Formen: Ausrichten, Drehen, Ebene, Umbruch, Layout, Maße.

Ein Baustein von ``KontextBefehle`` (``core/befehle/kontextreiter/kontext.py``)."""
from __future__ import annotations

from PySide6.QtGui import QCursor
from lunivo_writer.core.befehle.hilfen import FreiMenue


class ZeichenToolsBefehle:
    # ---- Zeichentools (Kontext-Reiter für frei positionierte Bilder und Formen) --------------------------------------------------
    def _zeichen(self):
        """(Editor, Ziel) des markierten Bildes oder (Editor, None)."""
        from lunivo_writer.editor.objekte import bildlayout as BL
        e = self.ed
        return (e, BL.ziel(e)) if e else (None, None)

    def _zeichen_edit(self):
        return self.ed

    def menue_zeichenFormstile(self):
        return FreiMenue.formstile(self)

    def menue_zeichenFuellung(self):
        return FreiMenue.fuell(self)

    def menue_zeichenGliederung(self):
        return FreiMenue.kontur(self)

    def menue_zeichenAusrichten(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for schl, text in (("links", "Links ausrichten"), ("mitte", "Waagerecht zentrieren"), ("rechts", "Rechts ausrichten"),
                           ("oben", "Oben ausrichten"), ("mittig", "Senkrecht zentrieren"), ("unten", "Unten ausrichten")):
            m.eintrag(text, lambda s=schl: self.zeichenAusrichten(None, s))
        return m

    def menue_zeichenDrehen(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Um 90° nach rechts drehen", lambda: self.zeichenDrehen(None, 90))
        m.eintrag("Um 90° nach links drehen", lambda: self.zeichenDrehen(None, -90))
        m.eintrag("Drehung zurücksetzen", lambda: self.zeichenDrehen(None, 0))
        return m

    def menue_zeichenEbene(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Vor den Text", lambda: self.zeichenEbene(None, "vor"))
        m.eintrag("Hinter den Text", lambda: self.zeichenEbene(None, "hinter"))
        return m

    def zeichenEffekte(self, k=None):
        e, z = self._zeichen()
        if z is not None:
            e._frei_effekte()

    def zeichenFormatUebertragen(self, k=None):
        from lunivo_writer.editor.objekte import bildlayout as BL
        e, z = self._zeichen()
        merk = BL.format_merken(z)
        if merk is None:
            self.w.statusBar().showMessage("Format übertragen: erst ein freies Bild oder eine Form markieren.", 4000)
            return
        e._frei_format_merk = merk
        self.w.statusBar().showMessage("Jetzt das Bild anklicken, das dieses Format bekommen soll.", 6000)

    def zeichenAusrichten(self, k=None, wie="links"):
        from lunivo_writer.editor.objekte import bildlayout as BL
        e, z = self._zeichen()
        BL.ausrichten(e, z, wie)

    def zeichenDrehen(self, k=None, grad=90):
        from lunivo_writer.editor.objekte import bildlayout as BL
        e, z = self._zeichen()
        if z is not None and z[0] == "frei":
            BL.frei_aendern(e, z, dreh=0.0) if grad == 0 else BL.drehen(e, z, float(grad))

    def zeichenEbene(self, k=None, wo="vor"):
        from lunivo_writer.editor.objekte import bildlayout as BL
        e, z = self._zeichen()
        BL.ebene(e, z, wo == "vor")

    def zeichenVorn(self, k=None): self.zeichenEbene(None, "vor")

    def zeichenHinten(self, k=None): self.zeichenEbene(None, "hinter")

    def zeichenUmbruch(self, k=None):
        e, z = self._zeichen()
        if z is not None:
            e._frei_layout_popup(QCursor.pos())

    def zeichenLayout(self, k=None):
        e, z = self._zeichen()
        if z is not None:
            e.bild_layout_dialog()

    def zeichenMasse(self, breite_mm=None, hoehe_mm=None):
        from lunivo_writer.editor.objekte import bildlayout as BL
        e, z = self._zeichen()
        BL.masse_setzen(e, z, breite_mm, hoehe_mm)
