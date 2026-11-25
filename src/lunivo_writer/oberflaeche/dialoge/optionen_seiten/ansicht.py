"""Optionen: Ansicht und Darstellung."""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.bausteine.haken.haken import haken
from lunivo_writer.oberflaeche.baukasten.bausteine.knopf.knopf import knopf
from lunivo_writer.oberflaeche.baukasten.bausteine.option.option import option

from lunivo_writer.oberflaeche.baukasten.basis.darstellung import eigenschaft, rolle as _rolle

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte

from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t

from lunivo_writer.oberflaeche.baukasten.geruest.module import anmelden

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QButtonGroup, QCheckBox, QLabel, QRadioButton, QPushButton, QSlider, QWidget
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import UmbruchSchalter
from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import text_label
from lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam import _Seite
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.basis.mass import SCHRIFT_ANSICHT_PROBE_PT
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_GROSS, ABSTAND_MITTEL, HOEHE_FELD, HOEHE_WAHLKARTE, ICON_NORMAL, RAND_ABSCHNITT, RAND_ZEILE_LOCKER, SCHRIFT_HINWEIS


anmelden("optionen", "anzeige", "optionen.seite.anzeige", "_ansicht", 20)

class AnsichtSeiten:
    """Optionen: Ansicht und Darstellung. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``)."""


    THEMEN = (("light", _t("optionen.ansicht.hell")), ("dark", _t("optionen.ansicht.dunkel")), ("mint", _t("optionen.ansicht.mint")), ("system", _t("optionen.ansicht.wie_das_system")))


    def _ansicht(self, titel):
        p = _Seite(self.w, titel)
        self._aussehen(p)
        f = p.gruppe(_t("optionen.ansicht.anzeigen"))
        p.haken(f, "ansicht/lineal", _t("optionen.ansicht.lineal"), False, lambda _: self.w.lineale_anwenden())
        p.haken(f, "ui/statusleiste", _t("optionen.ansicht.statusleiste"), True, lambda on: self.w.statusBar().setVisible(on))
        alle = UmbruchSchalter(_t("optionen.ansicht.absatzmarken_und_leerzeichen_zeigen"))
        alle.setProperty("optName", alle.text()); alle.setMinimumHeight(HOEHE_FELD)

        def alle_stand():
            alt = p.s.get_bool("ui/steuerzeichen", False)
            an = p.s.get_bool("ui/marken_absatz", alt) and p.s.get_bool("ui/marken_leer", alt)
            alle.blockSignals(True); alle.setChecked(an); alle.blockSignals(False)
        alle_stand()
        alle.toggled.connect(lambda on: (self.w.marken_setzen(on, on), alle_stand()))
        f.addRow(alle)
        f = p.gruppe(_t("optionen.ansicht.groesse_und_kontrast"))
        self._darstellung(p, f)
        e = p.mehr()
        f = p.unter(e, _t("optionen.ansicht.weitere_anzeige"))
        p.haken(f, "ansicht/lineal_hoch", _t("optionen.ansicht.vertikales_lineal"), False, lambda _: self.w.lineale_anwenden())
        p.schalter(f, _t("optionen.ansicht.navigationsbereich"), lambda: self.w.navigation.isVisible(), self.w.toggle_navigation)
        p.haken(f, "ui/marken", _t("optionen.ansicht.textbegrenzungen"), False, self.w.set_marken)
        p.schalter(f, _t("optionen.ansicht.gitternetzlinien"), lambda: bool(self.w.befehle.an_netzlinien()), lambda: self.w.befehle.netzlinien())
        p.haken(f, "ui/seitenleiste", _t("optionen.ansicht.seitenleiste_beim_start"), True)
        p.haken(f, "ui/leisten_text", _t("optionen.ansicht.namen_unter_den_symbolen_der_randleisten"), False, lambda _: self.w.ansicht_optionen_anwenden())
        p.haken(f, "ui/quickinfo", _t("optionen.ansicht.quickinfo"), True, lambda _: self.w.ansicht_optionen_anwenden())
        p.haken(f, "ui/live_vorschau", _t("optionen.ansicht.live_vorschau"), True, lambda _: self.w.vorschau.ende())
        p.haken(f, "ui/mini_auswahl", _t("optionen.ansicht.minisymbolleiste_bei_auswahl"), True)
        p.haken(f, "ui/absatz_symbol", _t("optionen.ansicht.absatz_layout_symbol_neben_dem_absatz"), True)
        p.haken(f, "ui/objektanker", _t("optionen.ansicht.objektanker"), True)
        p.haken(f, "ui/versteckt_zeigen", _t("optionen.ansicht.ausgeblendeter_text"), False, lambda _: self.w.versteckt_anwenden())
        f = p.unter(e, _t("optionen.ansicht.formatierungszeichen_einzeln"))
        absatz, leer = haken("standard", _t("optionen.ansicht.absatzmarken")), haken("standard", _t("optionen.ansicht.leerzeichen_und_tabstoppzeichen"))
        for c in (absatz, leer):
            c.setProperty("optName", c.text()); c.setMinimumHeight(HOEHE_FELD)

        def stand():
            alt = p.s.get_bool("ui/steuerzeichen", False)
            for c, k in ((absatz, "ui/marken_absatz"), (leer, "ui/marken_leer")):
                c.blockSignals(True); c.setChecked(p.s.get_bool(k, alt)); c.blockSignals(False)
            alle_stand()
        stand()
        absatz.toggled.connect(lambda on: (self.w.marken_setzen(absatz=on), stand()))
        leer.toggled.connect(lambda on: (self.w.marken_setzen(leer=on), stand()))
        for c in (absatz, leer):
            f.addRow(c)
        f = p.unter(e, _t("optionen.ansicht.menueband"))
        p.haken(f, "ui/band_doppelklick", _t("optionen.ansicht.doppelklick_blendet_das_band_aus"), True, lambda on: setattr(self.w.band, "einklappbar", on))
        p.haken(f, "ui/band_kompakt", _t("optionen.ansicht.kompaktes_menueband_niedrigere_gruppen_o"), True, lambda on: self.w.neu_bauen_band())
        p.haken(f, "ui/strg_klick_link", _t("optionen.ansicht.strg_klick_folgt_einem_verweis"), True)
        self._oberflaeche_wahl(p, f)
        p.aktion(_t("optionen.ansicht.menueband_anpassen"), _t("optionen.ansicht.menueband_anpassen_2"), lambda: self._anpassen("menueband"))
        p.aktion(_t("optionen.ansicht.symbolleiste_fuer_den_schnellzugriff"), _t("optionen.ansicht.schnellzugriff_anpassen"), lambda: self._anpassen("schnellzugriff"))
        p.abschluss()
        return p


    def _aussehen(self, p):
        """Hell, Dunkel, Mint oder wie das System: vier große Schaltflächen, genau eine ist gewählt (kein ausgegrauter Zusatzschalter)."""
        f = p.gruppe(_t("optionen.ansicht.aussehen"))
        zeile = QWidget(); h = _reihe("zeile", zeile)
        gruppe = QButtonGroup(zeile)
        knoepfe: dict[str, QPushButton] = {}
        for schl, name in self.THEMEN:
            b = knopf("standard", name, objektname="optWahl", umschaltbar=True)
            b.setAccessibleName(name); b.setAccessibleDescription(_t("optionen.ansicht.aussehen_des_programms"))
            b.setProperty("optName", _t("optionen.ansicht.hell_dunkel_aussehen"))
            gruppe.addButton(b); h.addWidget(b, 1)
            knoepfe[schl] = b

        def zeigen(_=None):
            jetzt = p.s.get("theme", "system")
            for schl, b in knoepfe.items():
                b.blockSignals(True); b.setChecked(schl == jetzt)
                aktiv = schl == jetzt
                b.setText(dict(self.THEMEN)[schl]); b.setIcon(symbole.icon("check", ICON_NORMAL) if aktiv else QIcon()); b.blockSignals(False)
        for schl, b in knoepfe.items():
            b.clicked.connect(lambda _c=False, k=schl: (self.w.set_theme(k), zeigen()))
        zeigen()
        self._aussehen_zeigen = zeigen
        zeile.setProperty("optName", _t("optionen.ansicht.hell_dunkel_aussehen"))
        f.addRow(zeile)


    def _oberflaeche_wahl(self, p, f):
        oberfl = QWidget(); ov = _spalte("abschnitt", oberfl); ov.addWidget(QLabel(_t("optionen.ansicht.benutzeroberflaeche")))
        gr = QButtonGroup(oberfl)
        beschreibung = text_label("", umbruch=True)
        _rolle(beschreibung, "hinweis")
        texte = {"symbolleisten": _t("optionen.ansicht.menueleiste_darunter_zwei_zeilen_symbole"),
                 "register": _t("optionen.ansicht.menueleiste_oben_darunter_reiter_start_e")}
        aktuell = p.s.get("ui/oberflaeche", "register")
        for schl, name in (("symbolleisten", _t("optionen.ansicht.symbolleisten")), ("register", _t("optionen.ansicht.in_registern"))):
            r = option("standard", name, an=schl == aktuell); r.setProperty("optName", _t("optionen.ansicht.benutzeroberflaeche")); r.setMinimumHeight(HOEHE_FELD)
            gr.addButton(r); ov.addWidget(r)
            r.toggled.connect(lambda an, k=schl: an and (beschreibung.setText(texte[k]),
                                                         self.w.oberflaeche_aendern(k, self.w.menubar_wanted if k == "register" else True)))
        beschreibung.setText(texte.get(aktuell, ""))
        ov.addWidget(beschreibung)
        oberfl.setProperty("optName", _t("optionen.ansicht.benutzeroberflaeche"))
        f.addRow(oberfl)


    def _darstellung(self, p, f):
        """Schrift größer/kleiner, Weicher Kontrast, Größe der Symbole, Schrift der Bedienung."""
        kopf = QWidget(); v = _spalte("abschnitt", kopf)
        v.addWidget(QLabel(_t("optionen.ansicht.schrift_im_text")))
        knoepfe = _reihe("standard")
        klein, gross = knopf("standard", _t("optionen.ansicht.a_kleiner")), knopf("standard", _t("optionen.ansicht.a_groesser"))
        for k in (klein, gross):
            k.setMinimumHeight(HOEHE_FELD); knoepfe.addWidget(k)
        knoepfe.addStretch(1)
        v.addLayout(knoepfe)
        zeile = _reihe("standard")
        probe = QLabel(_t("optionen.ansicht.so_gross_schreibst_du"))
        probe.setObjectName("optVorschau")
        stand = QLabel()
        _rolle(stand, "hinweis")
        zeile.addWidget(probe); zeile.addWidget(stand); zeile.addStretch(1)
        v.addLayout(zeile)

        def zoom_zeigen():
            e = self.w.current_editor()
            z = e.zoom if e is not None else 1.0
            fnt = probe.font(); fnt.setPointSizeF(SCHRIFT_ANSICHT_PROBE_PT * z); probe.setFont(fnt)
            stand.setText(_t("optionen.ansicht.schriftgroesse_0").format(round(z * 100)))

        def um(faktor):
            self.w.befehle._zoom_um(faktor)
            zoom_zeigen()
        klein.clicked.connect(lambda: um(1 / 1.1))
        gross.clicked.connect(lambda: um(1.1))
        zoom_zeigen()
        kopf.setProperty("optName", _t("optionen.ansicht.schrift_im_text"))
        f.addRow(kopf)
        p.haken(f, "ui/weich", _t("optionen.ansicht.weicher_kontrast"), False, lambda _: self.w.set_theme(self.w.settings.get("theme", "system")))
        p.wahl(f, "ui/icongroesse", _t("optionen.ansicht.groesse_der_symbole"), [(_t("optionen.ansicht.klein"), "klein"), (_t("optionen.ansicht.mittel"), "mittel"), (_t("optionen.ansicht.gross"), "gross")], "mittel",
               lambda _: self.w.ansicht_optionen_anwenden())
        regler = QWidget(); rv = _spalte("abschnitt", regler); rv.addWidget(QLabel(_t("optionen.ansicht.schrift_der_bedienung")))
        rh = _reihe("standard")
        sl = QSlider(Qt.Horizontal); sl.setRange(80, 140); sl.setSingleStep(5); sl.setPageStep(10); sl.setMinimumHeight(HOEHE_FELD)
        sl.setAccessibleName(_t("optionen.ansicht.schrift_der_bedienung_in_prozent"))
        sl.setValue(p.s.get_int("ui/bedien_prozent", 100))
        prozent = QLabel(f"{sl.value()} %"); _rolle(prozent, "text")

        def neu_wert(w):
            p.s.set("ui/bedien_prozent", w)
            prozent.setText(f"{w} %")
            if not sl.isSliderDown():
                self.w.ansicht_optionen_anwenden()
        sl.valueChanged.connect(neu_wert)
        sl.sliderReleased.connect(self.w.ansicht_optionen_anwenden)
        rh.addWidget(sl, 1); rh.addWidget(prozent)
        rv.addLayout(rh)
        regler.setProperty("optName", _t("optionen.ansicht.schrift_der_bedienung"))
        f.addRow(regler)
