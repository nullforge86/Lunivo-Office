"""Befehle zu Formen als freie Objekte (Zeichentools): Formstil-Raster, Füllungs-Palette, Anpassungsgriff, Form tauschen, Punkte bearbeiten.

Wirken auf die gewählte freie Form (``editor/frei_objekt.py``, Art ``form``). Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""
from __future__ import annotations

from PySide6.QtCore import QRectF


class FormToolsBefehle:
    def _form(self) -> dict | None:
        from lunivo_writer.editor import frei_objekt as FO
        return FO.daten_lesen(self.ed, "form") if self.ed else None

    def _form_hinweis(self) -> bool:
        self.w.lbl_msg.setText("Bitte zuerst eine Form auswählen.")
        return False

    # ---- Formstile --------------------------------------------------------------------------------------------------------------
    def formstileRaster(self, k=None) -> list[list[dict]]:
        """Daten der Galerie „Formstile“: 6 Zeilen × 7 Spalten (``editor/formen_stile.formstile_raster``)."""
        from lunivo_writer.editor import formen_stile as S
        return S.formstile_raster()

    def formStilRaster(self, k=None, zeile=0, spalte=0):
        """Stil (Zeile, Spalte) des Rasters auf die gewählte Form: Füllung, Verlaufsart, Linie, Strichbreite und Effekt."""
        from lunivo_writer.editor import formen_stile as S
        from lunivo_writer.editor import frei_objekt as FO
        if self._form() is None:
            return self._form_hinweis()
        w = S.formstil(int(zeile), int(spalte))
        ok = FO.aendern(self.ed, "form", form_fuell=w["fuell"], fuell_art=w["fuell_art"] or None, form_linie=w["linie"], form_strich=w["strich"],
                        form_effekt=w["effekt"])
        self.w.band.aktualisieren()
        return ok

    def zeichenFuellungDaten(self, k=None) -> dict:
        """Daten des Füllungs-Popups aus dem Baustein ``ui/baukasten/farben.py``: {"thema": Zeilen × 10 Spalten, "standard": [Farben],
        "verlauf": [Farben] (jede als Verlauf), "keine": True}. Die Auswahl setzen ``zeichenFuellung``-Wege des Popups (``FreiMenue.fuell``)."""
        from lunivo_writer.ui.baukasten import farben as F
        return {"thema": F.thema_raster(), "standard": list(F.STANDARD_FARBEN), "verlauf": list(F.STANDARD_FARBEN), "keine": True}

    # ---- Anpassungsgriff und Formwechsel -------------------------------------------------------------------------------------------
    def formAnpassen(self, k=None, wert=0.0, index=0):
        """Parameter ``index`` des Anpassungsgriffs der gewählten Form auf ``wert`` setzen (``formen.anpass_setzen``)."""
        from lunivo_writer.editor import formen as F
        if self._form() is None:
            return self._form_hinweis()
        return F.anpass_setzen(self.ed, float(wert), int(index))

    def kann_formAnpassen(self) -> bool:
        from lunivo_writer.editor import formen as F
        d = self._form()
        return bool(d) and bool(F.anpass_griffe(d.get("form", "Rechteck"), QRectF(0, 0, 1, 1)))

    def formAendern(self, k=None, name=None):
        """„Form bearbeiten ▸ Form ändern“: die gewählte Form durch ``name`` (Katalogname) ersetzen; Größe, Füllung und Kontur bleiben."""
        from lunivo_writer.editor import formen as F
        if self._form() is None:
            return self._form_hinweis()
        from lunivo_writer.ui.document import freiform_bedienung as FP
        ok = F.form_wechseln(self.ed, name)
        if ok and FP.aktiv(self.ed):
            FP.beenden(self.ed)                                           # eine andere Form hat keine eigenen Punkte mehr
        return ok

    def formPunkteBearbeiten(self, k=None):
        """„Punkte bearbeiten“: die gewählte Form wird zur Freiform (``editor/freiform.py``, Punktliste in ``daten["punkte"]``) und zeigt ihre
        Punkte zum Ziehen; Rechtsklick/Entf löscht einen Punkt, Doppelklick auf eine Kante fügt einen ein, Esc beendet."""
        if self._form() is None:
            return self._form_hinweis()
        from lunivo_writer.ui.document import freiform_bedienung as FP
        ok = FP.starten(self.ed)
        if ok:
            self.w.statusBar().showMessage("Punkte ziehen · Rechtsklick oder Entf löscht einen Punkt · Doppelklick auf eine Kante fügt einen ein · Esc beendet.", 8000)
        return ok

    def kann_formPunkteBearbeiten(self) -> bool:
        return self._form() is not None
