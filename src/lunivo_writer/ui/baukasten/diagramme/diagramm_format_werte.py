"""Werte von ``DiagrammFormatPanel`` (Seitenleiste „Diagramm formatieren“): ``werte()`` lesen, ``setze()`` füllen, Teil einrichten.

Mixin zu ``diagramm_format_panel.DiagrammFormatPanel`` und steht dort vor den Panel-Basen (``super()`` führt weiter zu ``ObjektFormatPanel``)."""
from __future__ import annotations

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.diagramme import diagramm_format as F
from lunivo_writer.ui.baukasten.basis.linien import Linie
from lunivo_writer.ui.baukasten.diagramme.diagramm_format_bausteine import _OHNE, _optionen_name, _text_teil, _still


class DiagrammFormatWerteMixin:
    """Werte des Panels lesen und setzen (Füllung, Linie, Optionen, Teil einrichten); ``DiagrammFormatPanel`` baut nur die Oberfläche."""

    def werte(self) -> dict:
        """Füllung, Linie und Effekte im Format des Teilformats (``None`` = entfernen)."""
        out: dict = {}
        fu = self._fuell_wert()
        if fu is not _OHNE:
            out["fuell"] = fu
        out["linie"] = self._linie_wert()
        fx = self._werte_effekte()
        for k in F.FX_SCHLUESSEL:
            out[k] = fx.get(k)
        return out

    def _fuell_wert(self):
        if self.r_auto.isChecked():
            return None
        if self.r_keine.isChecked():
            return ""
        tr = int(self.f_trans.value())
        d = self._fuell_art(tr)
        if d is _OHNE or isinstance(d, str):                                # kein Bild / einfarbig ohne Transparenz
            return d
        if tr:
            d["transparenz"] = tr
        return d

    def _fuell_art(self, tr: int):
        """Die Füllung der gewählten Art: Angaben, ``_OHNE`` (Bildfüllung ohne Bild) oder die Farbe (einfarbig ohne Transparenz)."""
        if self.r_verlauf.isChecked():
            d = {"art": "graduell", "dunkel": self.v1.farbe or Farbe.BLAU_DUNKEL, "hell": self.v2.farbe or Farbe.WEISS, "winkel": self.v_winkel.value()}
            d["farbe"] = d["dunkel"]
            return d
        if self.r_textur.isChecked() and self._bild_modus:
            return self._bild_fuellung()
        if self.r_textur.isChecked():
            return {"art": "textur", "key": self.textur.currentData()}
        if self.r_muster.isChecked():
            return {"art": "muster", "key": self.muster.currentData(), "farbe": self.m_farbe.farbe or Farbe.TINTE, "grund": Farbe.WEISS}
        if self.r_bild.isChecked():
            return self._bild_fuellung()
        c = self.farbe.farbe or Farbe.BLAU
        return c if not tr else {"art": "farbe", "farbe": c}

    def _bild_fuellung(self):
        return {"art": "bild", "bild_b64": self._bild_b64} if self._bild_b64 else _OHNE

    def _linie_wert(self) -> dict | None:
        if self.k_auto.isChecked():
            return None
        voll = {"keine": None, "farbe": None, "breite": None, "art": None, "transparenz": None, "kombiniert": None, "abschluss": None, "verknuepfung": None,
                "rund": None, "verlauf": None, "pfeil_anfang": None, "pfeil_ende": None, "pfeil_groesse": None,
                "pfeil_groesse_anfang": None, "pfeil_groesse_ende": None}
        if self.k_keine.isChecked():
            return {**voll, "keine": True}
        kombi, abschluss, verknuepfung = self.l_kombi.aktuell(), self.l_abschluss.currentData(), self.l_verknuepfung.currentData()
        voll.update(farbe=self.k_farbe.farbe or Farbe.GRAU, breite=self._k_breite(), art=self.k_art.currentData() or "einfach",
                    transparenz=int(self.k_trans.value()) or None, kombiniert=kombi if kombi != "einfach" else None,
                    abschluss=abschluss if abschluss != "flach" else None, verknuepfung=verknuepfung if verknuepfung != "rund" else None,
                    rund=True if self.l_rund.isChecked() else None)
        if self.k_verlauf.isChecked():
            voll["verlauf"] = {"farbe1": self.kv1.farbe or Farbe.ROT, "farbe2": self.kv2.farbe or Farbe.BLAU_DUNKEL, "winkel": self.kv_winkel.value()}
        if self._linienreihe:
            voll.update(self._pfeil_werte())
        return voll

    def _pfeil_werte(self) -> dict:
        """Pfeile am Anfang und Ende der Linienreihe; die Vorgabe („keiner“, Größe 1) gilt als nicht gesetzt (None)."""
        def wert(c, vorgabe):
            return c.currentData() if c.currentData() != vorgabe else None
        return {"pfeil_anfang": wert(self.p_anfang, "keiner"), "pfeil_ende": wert(self.p_ende, "keiner"),
                "pfeil_groesse_anfang": wert(self.p_groesse_anfang, 1.0), "pfeil_groesse_ende": wert(self.p_groesse_ende, 1.0)}

    # ---- Füllen ----------------------------------------------------------------------------------------------------------------------
    def _setze(self, w: dict) -> None:
        fmt = w.get("format") or {}
        super()._setze({**F.fx_normal(fmt), "_fmt": fmt})

    def _setze_fuellung(self, w: dict) -> None:
        fmt = w.get("_fmt") or {}
        fu, li = fmt.get("fuell"), fmt.get("linie")
        d = F.fuell_dict(fu)
        art = d.get("art", "farbe") if d else None
        radios = (self.r_keine, self.r_farbe, self.r_verlauf, self.r_textur, self.r_muster, self.r_bild, self.r_auto, self.k_keine, self.k_linie, self.k_verlauf, self.k_auto)
        for x in radios:
            x.blockSignals(True)
        self.r_auto.setChecked(fu is None); self.r_keine.setChecked(fu == "" or art == "keine"); self.r_farbe.setChecked(art == "farbe")
        self.r_verlauf.setChecked(art in ("graduell", "verlauf")); self.r_textur.setChecked(art in ("textur", "bild")); self.r_muster.setChecked(art == "muster")
        self.r_bild.setChecked(False); self._bild_modus = art == "bild"
        verlauf = bool(li and li.get("verlauf"))
        keine = F.linie_keine(li)
        self.k_auto.setChecked(not li); self.k_keine.setChecked(keine); self.k_verlauf.setChecked(bool(li) and not keine and verlauf)
        self.k_linie.setChecked(bool(li) and not keine and not verlauf)
        for x in radios:
            x.blockSignals(False)
        self._bild_b64 = (d or {}).get("bild_b64", "") if art == "bild" else ""
        self._setze_fuellfarben(art, d or {})
        self._setze_linienfelder(li or {})
        self._felder_zeigen()

    def _setze_fuellfarben(self, art: str, d: dict) -> None:
        self.farbe.setFarbe("")                                             # leere Farbe = „Automatisch“ (wie überall: gesetzte Farben zeigen ihre Hex-Zahl)
        if art == "farbe":
            self.farbe.setFarbe(d.get("farbe", Farbe.BLAU))
        elif art in ("graduell", "verlauf"):
            self.v1.setFarbe(d.get("dunkel", d.get("farbe", Farbe.BLAU_DUNKEL))); self.v2.setFarbe(d.get("hell", Farbe.BLAU_HELL))
        elif art == "textur":
            self.textur.setCurrentIndex(max(0, self.textur.findData(d.get("key"))))
        elif art == "muster":
            self.muster.setCurrentIndex(max(0, self.muster.findData(d.get("key")))); self.m_farbe.setFarbe(d.get("farbe", Farbe.TINTE))
        self.f_trans.setValue(float(d.get("transparenz", 0))); self.v_winkel.setValue(float(d.get("winkel", 90)))

    def _setze_linienfelder(self, li: dict) -> None:
        self.k_farbe.keine_text = "Automatisch"
        _still(self.k_wahl, Linie(li.get("farbe", ""), float(li.get("breite", 1.0)), F.strich_schluessel(li.get("art"))), "setLinie")
        self.s_art.setze(F.strich_schluessel(li.get("art"))); _still(self.s_breite, float(li.get("breite", 1.0 if li else 0.75)))      # still: sonst wählt die Änderung „Durchgezogene Linie“
        self.k_trans.setValue(float(li.get("transparenz", 0)))
        self.l_kombi.setze(li.get("kombiniert", "einfach"))
        for c, k, vorgabe in ((self.l_abschluss, "abschluss", "flach"), (self.l_verknuepfung, "verknuepfung", "rund"),
                              (self.p_anfang, "pfeil_anfang", "keiner"), (self.p_ende, "pfeil_ende", "keiner")):
            _still(c, max(0, c.findData(li.get(k, vorgabe))), "setCurrentIndex")
        _still(self.l_rund, bool(li.get("rund")), "setChecked")
        for c, k in ((self.p_groesse_anfang, "pfeil_groesse_anfang"), (self.p_groesse_ende, "pfeil_groesse_ende")):
            _still(c, max(0, c.findData(float(li.get(k, li.get("pfeil_groesse", 1.0))))), "setCurrentIndex")
        v = li.get("verlauf") or {}
        self.kv1.setFarbe(v.get("farbe1", Farbe.ROT)); self.kv2.setFarbe(v.get("farbe2", Farbe.BLAU_DUNKEL)); self.kv_winkel.setValue(float(v.get("winkel", 0)))

    def setze(self, werte: dict) -> None:
        """Die Felder mit dem Format des Teils füllen; meldet nichts."""
        if not self._fertig:
            super().setze(werte)
            return
        alt, self._stumm = self._stumm, True
        try:
            self._teil = werte.get("teil") or "diagrammbereich"
            self._teile_zeigen(werte)
            self._teil_einrichten(werte)
            super().setze(werte)
            f = werte.get("format") or {}
            self.text_panel.setze({"text": f.get("text") or {}, "teil": self._teil})
            if getattr(self.text_panel, "FOTO", False):               # Ränder usw. nur außer beim Titel (Vorlage: dort grau); „Text nicht drehen“ nur beim gedrehten Diagramm
                self.text_panel.a_feld.freigeben(self._teil != "titel", bool((werte.get("objekt") or {}).get("dreh")))
            self._setze_optionen(werte, f)
        finally:
            self._stumm = alt

    def _teile_zeigen(self, werte: dict) -> None:
        """Die Liste „Teil“ mit den Teilen des Diagramms (``werte["teile"]``, sonst nur der gewählte) und dem gewählten Eintrag."""
        teile = list(werte.get("teile") or [(self._teil, werte.get("name") or "Diagrammbereich")])
        self.teil_wahl.setze(teile, self._teil)

    def _hauptreiter_einrichten(self, teil: str) -> None:
        """Die zwei Hauptreiter „<Teil>optionen“ und „Textoptionen“: Name, was wählbar ist, welcher offen steht."""
        self.optionen.setTabText(0, _optionen_name(teil))
        text_ok = _text_teil(teil)
        self.optionen.setTabEnabled(1, text_ok)
        self.optionen.setTabEnabled(0, teil != "datenbeschriftung")
        if (not text_ok and self.optionen.currentIndex() == 1) or (teil == "datenbeschriftung" and self.optionen.currentIndex() == 0):
            self.optionen_waehlen(1 if teil == "datenbeschriftung" else 0)

    def _teil_einrichten(self, werte: dict) -> None:
        teil = self._teil
        self._hauptreiter_einrichten(teil)
        legende, achse, reihe, bereich = teil == "legende", teil.startswith("achse_"), teil.startswith("reihe_"), teil == "diagrammbereich"
        self.reiter.setTabVisible(2, legende or achse or reihe)
        self.reiter.setTabText(2, "Legendenoptionen" if legende else "Achsenoptionen" if achse else "Reihenoptionen")
        self._reiter_kurz()
        self.reiter.setTabVisible(3, bereich)
        self._luecke_an = reihe and bool(werte.get("saeulen"))
        for a, an in ((self.a_legende, legende), (self.a_achse, achse), (self.a_reihe, self._luecke_an),
                      (self.a_reihe_linie, reihe and bool(werte.get("linienreihe")))):
            a.setVisible(an)
        self._pfeile_freigeben(reihe and bool(werte.get("linienreihe")))
        for x in self._wert_zeilen:                                         # Minimum, Maximum, Hauptintervall: nur die Wertachse
            x.setEnabled(bool(werte.get("wertachse", True)))

    def _setze_optionen(self, werte: dict, f: dict) -> None:
        o = werte.get("objekt") or {}
        _still(self.o_lage, max(0, self.o_lage.findData(o.get("legende_pos", "unten"))), "setCurrentIndex")
        a = f.get("achse") or {}
        self.o_min.setze(a.get("min")); self.o_max.setze(a.get("max")); self.o_intervall.setze(a.get("intervall"))
        self.o_neben.setze(a.get("neben")); _still(self.o_format, a.get("format") or "", "setText")
        _still(self.o_umkehren, bool(a.get("umkehren")), "setChecked")
        _still(self.o_beschr, max(0, self.o_beschr.findData(a.get("beschriftung", "neben"))), "setCurrentIndex")
        r = f.get("reihe") or {}
        _still(self.o_luecke, float(r.get("luecke", 100))); _still(self.o_glatt, bool(r.get("glatt")), "setChecked"); _still(self.o_punkte, bool(r.get("punkte")), "setChecked")
        self.a_alt.setze(werte.get("alt_titel") or "", werte.get("alt_beschreibung") or "")
