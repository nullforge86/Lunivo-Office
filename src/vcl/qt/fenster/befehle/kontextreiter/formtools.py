"""Befehle zu Formen als freie Objekte (Zeichentools): Formstil-Raster, Füllungs-Palette, Anpassungsgriff, Form tauschen, Punkte bearbeiten.

Wirken auf die gewählte freie Form (``editor/objekte/frei_objekt.py``, Art ``form``). Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""
from __future__ import annotations

from PySide6.QtCore import QRectF

from vcl.qt.fenster.befehle.hilfen import _farbfeld
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine import FarbPalette, weitere_farben
from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
from writer.anbindung import formen_daten as _formen_daten


class FormToolsBefehle:
    def _form(self) -> dict | None:
        from vcl.qt.rendering import formen as FO
        return FO.daten_lesen(self.ed, "form") if self.ed else None

    def _form_hinweis(self) -> bool:
        self.w.lbl_msg.setText("Bitte zuerst eine Form auswählen.")
        return False

    # ---- Formstile --------------------------------------------------------------------------------------------------------------
    def formstileRaster(self, k=None) -> list[list[dict]]:
        """Daten der Galerie „Formstile“: 6 Zeilen × 7 Spalten (``editor/objekte/formen_stile.formstile_raster``)."""
        from vcl.qt.rendering import formen as S
        return S.formstile_raster()

    def formStilRaster(self, k=None, zeile=0, spalte=0):
        """Stil (Zeile, Spalte) des Rasters auf die gewählte Form: Füllung, Verlaufsart, Linie, Strichbreite und Effekt."""
        from vcl.qt.rendering import formen as S
        from vcl.qt.rendering import formen as FO
        if self._form() is None:
            return self._form_hinweis()
        w = S.formstil(int(zeile), int(spalte))
        ok = FO.frei_objekt_aendern(self.ed, "form", form_fuell=w["fuell"], fuell_art=w["fuell_art"] or None, form_linie=w["linie"], form_strich=w["strich"],
                        form_effekt=w["effekt"])
        self.w.band.aktualisieren()
        return ok

    def zeichenFuellungDaten(self, k=None) -> dict:
        """Daten des Füllungs-Popups aus dem Baustein ``oberflaeche/baukasten/basis/farben.py``: {"thema": Zeilen × 10 Spalten, "standard": [Farben],
        "verlauf": [Farben] (jede als Verlauf), "keine": True}. Die Auswahl setzen ``zeichenFuellung``-Wege des Popups (``FreiMenue.fuell``)."""
        from vcl.qt.widgets.bausteine.farben import farben as F
        return {"thema": F.thema_raster(), "standard": list(F.STANDARD_FARBEN), "verlauf": list(F.STANDARD_FARBEN), "keine": True}

    # ---- Anpassungsgriff und Formwechsel -------------------------------------------------------------------------------------------
    def formAnpassen(self, k=None, wert=0.0, index=0):
        """Parameter ``index`` des Anpassungsgriffs der gewählten Form auf ``wert`` setzen (``formen.anpass_setzen``)."""
        from vcl.qt.rendering import formen as F
        if self._form() is None:
            return self._form_hinweis()
        return F.anpass_setzen(self.ed, float(wert), int(index))

    def kann_formAnpassen(self) -> bool:
        from vcl.qt.rendering import formen as F
        d = self._form()
        return bool(d) and bool(F.anpass_griffe(d.get("form", "Rechteck"), QRectF(0, 0, 1, 1)))

    def formAendern(self, k=None, name=None):
        """„Form bearbeiten ▸ Form ändern“: die gewählte Form durch ``name`` (Katalogname) ersetzen; Größe, Füllung und Kontur bleiben."""
        from vcl.qt.rendering import formen as F
        if self._form() is None:
            return self._form_hinweis()
        from vcl.qt.widgets.dokumentansicht.bearbeitung import freiform_bedienung as FP
        ok = F.form_wechseln(self.ed, name)
        if ok and FP.aktiv(self.ed):
            FP.beenden(self.ed)                                           # eine andere Form hat keine eigenen Punkte mehr
        return ok

    def formPunkteBearbeiten(self, k=None):
        """„Punkte bearbeiten“: die gewählte Form wird zur Freiform (``editor/objekte/freiform.py``, Punktliste in ``daten["punkte"]``) und zeigt ihre
        Punkte zum Ziehen; Rechtsklick/Entf löscht einen Punkt, Doppelklick auf eine Kante fügt einen ein, Esc beendet."""
        if self._form() is None:
            return self._form_hinweis()
        from vcl.qt.widgets.dokumentansicht.bearbeitung import freiform_bedienung as FP
        ok = FP.starten(self.ed)
        if ok:
            self.w.statusBar().showMessage("Punkte ziehen · Rechtsklick oder Entf löscht einen Punkt · Doppelklick auf eine Kante fügt einen ein · Esc beendet.", 8000)
        return ok

    def kann_formPunkteBearbeiten(self) -> bool:
        return self._form() is not None

    # ---- Form-Menüs, Vorlagen, Text in der Form, Gruppieren (aus dem Kontext-Reiter) ---------------------------------------------------
    # ---- Form- und WordArt-Tools --------------------------------------------------------------------------------------------
    FARBEN = Farbe.FORMFARBEN

    def _form_farbe(self, feld: str, titel: str):
        c = weitere_farben(self.w, Farbe.AKZENT_DUNKEL, titel)
        if c is not None:
            self._form_aendern(**{feld: c.name()})

    def _form_aendern(self, **kw):
        from vcl.qt.rendering import formen
        if not (self.ed and formen.formen_aendern(self.ed, **kw)):
            self.w.lbl_msg.setText("Bitte zuerst eine Form auswählen (Schreibmarke vor der Form oder Form markieren).")

    def menue_formFuellung(self):
        m = FarbPalette(self.w, keine_text="Keine Füllung", start=Farbe.AKZENT_DUNKEL, titel="Füllfarbe")
        m.gewaehlt.connect(lambda c: self._form_aendern(fuell=c.name() if c is not None else ""))
        return m

    def menue_formKontur(self):
        m = FarbPalette(self.w, keine_text=None, start=Farbe.AKZENT_DUNKEL, titel="Linienfarbe")
        m.gewaehlt.connect(lambda c: self._form_aendern(linie=c.name()))
        m.addSeparator()
        st = m.untermenue("Linienstärke")
        for w in (0.5, 1.0, 2.0, 3.0, 5.0, 8.0):
            st.eintrag(f"{w:g} pt".replace(".", ","), lambda w=w: self._form_aendern(strich=w))
        return m

    def menue_formVorlagen(self):
        from vcl.qt.rendering.formen import formen
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n, fu, li, _st in _formen_daten.vorlagen():
            m.eintrag(n, lambda n=n: self._form_vorlage(n), symbol=_farbfeld(fu or Farbe.WEISS))
        return m

    def _form_vorlage(self, name):
        from vcl.qt.rendering import formen
        if not (self.ed and formen.vorlage(self.ed, name)):
            self.w.lbl_msg.setText("Bitte zuerst eine Form auswählen.")

    def formText(self, k=None):
        from vcl.qt.rendering import formen
        frei = formen.frei_daten(self.ed) if self.ed else None            # als freies Objekt gewählte Form
        if frei is not None:
            akt = frei.get("text", "")
        else:
            e, f = self._bild()
            if f is None:
                return
            akt = (e.inline_daten("form") or {}).get("text", "")
        t, ok = EingabeFenster.getText(self.w, "Text in der Form", "Text:", text=akt)
        if ok:
            self._form_aendern(text=t)

    def gruppieren(self, k=None):
        from vcl.qt.rendering import formen
        if self.ed:
            r = formen.gruppieren(self.ed)
            self.w.lbl_msg.setText(r or "Formen gruppiert.")

    def gruppeAufheben(self, k=None):
        from vcl.qt.rendering import formen
        if self.ed:
            r = formen.gruppe_aufheben(self.ed)
            self.w.lbl_msg.setText(r or "Gruppierung aufgehoben.")
