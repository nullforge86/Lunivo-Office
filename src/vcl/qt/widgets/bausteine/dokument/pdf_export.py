"""Eingebettete, schrittweise PDF-Exportansicht für Lunivos Datei-Menü."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.bausteine.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.bausteine.haken.haken import haken
from vcl.qt.widgets.bausteine.bausteine.knopf.knopf import knopf as knopf_baustein, werkzeugknopf
from vcl.qt.widgets.bausteine.bausteine.option.option import option

from vcl.qt.widgets.bausteine.basis.darstellung import rolle as _rolle

from writer.baukasten.basis.mass import ABSTAND_BLOCK as _A_BLOCK, ABSTAND_GROSS as _A_GROSS, ABSTAND_MITTEL as _A_MITTEL

from vcl.qt.widgets.bausteine.geruest.rollen import anwenden, raender, reihe as _reihe, spalte as _spalte

from writer.baukasten.basis.daten import text as _t

import os
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QLabel, QLayout, QLineEdit, QMessageBox, QPushButton, QRadioButton, QSpinBox,
    QToolButton, QWidget,
)

from filter.pdf.pdf_export import DRUCK, PdfWahl, kennwort_fehler

from vcl.qt.widgets.bausteine.felder.formular_gitter import FELDHOEHE as FELD_H, FlussLayout, FormularGitter, abschnittstitel
from writer.baukasten.basis.mass import ABSTAND_EXPORT_ABSCHNITT, ABSTAND_KLEIN, ABSTAND_NORMAL, ABSTAND_ZEILE, RAND_EXPORT_ABSCHNITT, RAND_EXPORT_FENSTER, RAND_EXPORT_SCHUTZ, RAND_EXPORT_SEITENZEILE, RAND_EXPORT_WEITERE, RAND_KEIN, RAND_OBEN_SEITE, RAND_ZEILE
from vcl.qt.widgets.bausteine.dropdown.auswahlfeld import Auswahlfeld

RECHTE = [("aendern", _t("pdf.aendern_erlauben")), ("kopieren", _t("pdf.kopieren_erlauben")),
          ("kommentieren", _t("pdf.kommentare_hinzufuegen_erlauben"))]


def _abschnitt(titel: str, hilfe: str, layout=None) -> QWidget:
    w = QWidget()
    v = _spalte("abschnitt", w)
    kopf = abschnittstitel(titel)
    erklaerung = QLabel(hilfe); erklaerung.setWordWrap(True); erklaerung.setObjectName("bsHinweis")
    v.addWidget(kopf); v.addWidget(erklaerung)
    if layout is not None:
        v.addLayout(layout) if isinstance(layout, QLayout) else v.addWidget(layout)
    return w


def _einklappen(titel: str, beschreibung: str, inhalt: QWidget, offen: bool = False) -> tuple[QWidget, QToolButton]:
    w = QWidget(); v = _spalte("zeile", w)
    knopf = werkzeugknopf("standard", titel, umschaltbar=True, an=offen, flach=False)
    knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); knopf.setArrowType(Qt.DownArrow if offen else Qt.RightArrow)
    knopf.setAutoRaise(True); knopf.setMinimumHeight(FELD_H)
    knopf.setAccessibleName(titel); knopf.setAccessibleDescription(beschreibung)
    inhalt.setVisible(offen)
    knopf.toggled.connect(inhalt.setVisible)
    knopf.toggled.connect(lambda an: knopf.setArrowType(Qt.DownArrow if an else Qt.RightArrow))
    v.addWidget(knopf); v.addWidget(inhalt)
    return w, knopf


def _kennwort() -> QLineEdit:
    f = zeilenfeld("frei", passwort=True); f.setMinimumHeight(FELD_H)
    return f


class PdfExportAnsicht(QWidget):
    """PDF-Export als dauerhaft sichtbare zweite Menüspalte, keine separates Dialogfenster."""

    def __init__(self, parent, start: PdfWahl, seiten: int, aktuelle: int, markierung: bool,
                 exportieren: Callable[[PdfWahl], bool], zurueck: Callable[[], None]):
        super().__init__(parent)
        self._exportieren = exportieren
        self._zurueck = zurueck
        self._ersetzen_ok = ""
        self._wahl: PdfWahl | None = None
        self.optionen: dict[str, QCheckBox] = {}
        self.rechte: dict[str, QCheckBox] = {}

        root = _spalte("fenster", self)
        titel = QLabel(_t("pdf.pdf_exportieren")); titel.setObjectName("bsTitel")
        root.addWidget(titel)
        intro = QLabel(_t("pdf.waehle_speicherort_und_seiten_weitere_ei"))
        intro.setWordWrap(True); intro.setObjectName("bsHinweis"); root.addWidget(intro)

        self.pfad = zeilenfeld("frei", start.pfad); self.pfad.setMinimumHeight(FELD_H)
        self.pfad.setAccessibleName(_t("pdf.pdf_dateiname_und_speicherort"))
        self.pfad.setToolTip(_t("pdf.dateiname_und_speicherort_der_pdf_datei"))
        durch = knopf_baustein("standard", _t("pdf.durchsuchen"), aktion=self._durchsuchen)
        durch.setAccessibleDescription(_t("pdf.speicherort_fuer_die_pdf_datei_auswaehle"))
        datei_zeile = _reihe("standard"); datei_zeile.addWidget(self.pfad, 1); datei_zeile.addWidget(durch)
        root.addWidget(_abschnitt(_t("pdf.1_pdf_speichern"), _t("pdf.dateiname_und_speicherort"), datei_zeile))

        bereich_layout = _spalte("eng")
        self.b_alles = option("standard", _t("pdf.ganzes_dokument"))
        self.b_aktuell = option("standard", _t("pdf.aktuelle_seite_0").format(aktuelle))
        self.b_markierung = option("standard", _t("pdf.nur_die_markierung"))
        self.b_markierung.setEnabled(markierung)
        if not markierung:
            self.b_markierung.setToolTip(_t("pdf.diese_auswahl_ist_verfuegbar_sobald_text"))
        self.b_seiten = option("standard", _t("pdf.seitenbereich"))
        self._bereiche = {"alles": self.b_alles, "aktuell": self.b_aktuell, "markierung": self.b_markierung, "seiten": self.b_seiten}
        gruppe = QButtonGroup(self)
        for b in self._bereiche.values():
            gruppe.addButton(b); bereich_layout.addWidget(b)
        bereich = start.bereich if start.bereich != "markierung" or markierung else "alles"
        self._bereiche.get(bereich, self.b_alles).setChecked(True)
        seiten_zeile = _reihe("einzug")
        self.von, self.bis = QSpinBox(), QSpinBox()
        for feld, wert in ((self.von, start.von), (self.bis, start.bis)):
            feld.setRange(1, max(1, seiten)); feld.setValue(min(max(1, wert), max(1, seiten)))
            feld.setMinimumHeight(FELD_H)
        if start.bereich != "seiten":
            self.von.setValue(1); self.bis.setValue(max(1, seiten))
        self.l_von, self.l_bis = QLabel(_t("pdf.von_seite")), QLabel("bis")
        self.l_von.setBuddy(self.von); self.l_bis.setBuddy(self.bis)
        seiten_zeile.addWidget(self.l_von); seiten_zeile.addWidget(self.von); seiten_zeile.addWidget(self.l_bis)
        seiten_zeile.addWidget(self.bis); seiten_zeile.addStretch(1)
        bereich_layout.addLayout(seiten_zeile)
        self.b_seiten.toggled.connect(self._seiten_schalten)
        self._seiten_schalten(self.b_seiten.isChecked())
        root.addWidget(_abschnitt(_t("pdf.2_seiten_auswaehlen"), _t("pdf.lege_fest_welche_seiten_in_die_pdf_komme"), bereich_layout))

        inhalte = _spalte("eng")
        for key, text, tip in (
            ("hyperlinks", _t("pdf.links_beibehalten"), _t("pdf.anklickbare_links_im_dokument_funktionie")),
            ("kommentare", _t("pdf.kommentare_uebernehmen"), _t("pdf.kommentare_erscheinen_im_pdf_als_notizen")),
            ("ueberschriften", _t("pdf.ueberschriften_als_pdf_lesezeichen"), _t("pdf.erstellt_eine_klickbare_navigation_aus_d")),
        ):
            box = haken("standard", text, an=getattr(start, key), tooltip=tip, name=text)
            self.optionen[key] = box; inhalte.addWidget(box)
        root.addWidget(_abschnitt(_t("pdf.3_inhalte_uebernehmen"), _t("pdf.waehle_was_im_pdf_erhalten_bleiben_soll"), inhalte))

        weitere = QWidget(); av = _spalte("abschnitt", weitere)
        for key, text, tip in (
            ("eigenschaften", _t("pdf.dokumentinformationen_uebernehmen"), _t("pdf.titel_verfasser_und_weitere_dokumentanga")),
            ("textmarken", _t("pdf.textmarken_als_sprungziele"), _t("pdf.gesetzte_textmarken_werden_im_pdf_anklic")),
            ("notenlinks", _t("pdf.fuss_und_endnoten_verknuepfen"), _t("pdf.notenzeichen_fuehren_im_pdf_zur_jeweilig")),
            ("andere", _t("pdf.weitere_vorlagen_als_lesezeichen"), _t("pdf.zum_beispiel_titel_untertitel_oder_zitat")),
            ("eigene", _t("pdf.eigene_vorlagen_als_lesezeichen"), _t("pdf.benutzerdefinierte_formatvorlagen_in_der")),
        ):
            box = haken("standard", text, an=getattr(start, key), tooltip=tip, name=text)
            self.optionen[key] = box; av.addWidget(box)
        weitere_box, self.weitere_knopf = _einklappen(_t("pdf.weitere_exportoptionen"), _t("pdf.zusaetzliche_angaben_und_navigationsopti"), weitere)
        root.addWidget(weitere_box)

        self.schutz_inhalt = self._schutz(start)
        schutz_box, self.schutz_knopf = _einklappen(_t("pdf.4_schutz_und_berechtigungen"), _t("pdf.optionaler_kennwortschutz_und_einstellun"), self.schutz_inhalt)
        root.addWidget(schutz_box)

        self.meldung = QLabel(); self.meldung.setWordWrap(True); self.meldung.setObjectName("bsHinweis"); self.meldung.hide()
        root.addWidget(self.meldung)
        root.addStretch(1)

        fuss = FlussLayout(_A_MITTEL); raender(fuss, "oben")
        self.schliessen = haken("standard", _t("pdf.danach_zum_dokument_zurueck"))
        self.schliessen.setChecked(start.schliessen)
        self.schliessen.setToolTip(_t("pdf.kehrt_nach_erfolgreichem_export_zur_doku"))
        abbrechen = knopf_baustein("standard", _t("pdf.zurueck_zum_dokument"), rolle="aktion", aktion=self._zurueck)
        self.ok = knopf_baustein("standard", _t("pdf.pdf_exportieren"), objektname="optFertig", standard=True)
        self.ok.setCursor(Qt.PointingHandCursor); self.ok.clicked.connect(self._ok)
        fuss.addWidget(self.schliessen); fuss.addWidget(abbrechen); fuss.addWidget(self.ok)
        root.addLayout(fuss)

    def _schutz(self, s: PdfWahl) -> QWidget:
        bereich = QWidget()
        v = _spalte("abschnitt", bereich)
        self.verschluesseln = haken("standard", _t("pdf.pdf_mit_kennwort_schuetzen"))
        self.verschluesseln.setChecked(s.verschluesseln)
        self.verschluesseln.setToolTip(_t("pdf.schuetzt_den_zugriff_und_oder_legt_fest"))
        v.addWidget(self.verschluesseln)

        self.innen = QWidget(); g = FormularGitter(self.innen)
        self.rechte_kw, self.rechte_kw2 = _kennwort(), _kennwort()
        self.rechte_kw.setText(s.kennwort_rechte); self.rechte_kw2.setText(s.kennwort_rechte)
        g.reihe((_t("pdf.kennwort_fuer_berechtigungen"), self.rechte_kw), (_t("pdf.bestaetigung"), self.rechte_kw2))
        self.rechte_kw.setAccessibleName(_t("pdf.kennwort_fuer_berechtigungen")); self.rechte_kw2.setAccessibleName(_t("pdf.bestaetigung_des_berechtigungskennworts"))
        hinweis = QLabel(_t("pdf.mit_diesem_kennwort_koennen_empfaenger_d"))
        hinweis.setWordWrap(True); hinweis.setObjectName("bsHinweis"); g.breit(hinweis)

        self.rechte: dict[str, QCheckBox] = {}
        for key, label in RECHTE:
            box = haken("standard", label, an=getattr(s, key)); self.rechte[key] = box
            g.breit(box)
        self.druck = Auswahlfeld()
        for text, value in DRUCK:
            label = {_t("pdf.freier_druck"): _t("pdf.drucken"), _t("pdf.nur_niedrige_aufloesung"): _t("pdf.drucken_in_niedriger_aufloesung"),
                     _t("pdf.kein_druck"): _t("pdf.drucken_nicht_erlauben")}.get(text, text)
            self.druck.addItem(label, value)
        self.druck.setCurrentIndex(max(0, self.druck.findData(s.druck)))
        g.zeile(_t("pdf.drucken"), self.druck)

        oeffnen_titel = QLabel(_t("pdf.kennwort_zum_oeffnen_der_pdf_optional"))
        oeffnen_titel.setToolTip(_t("pdf.wer_dieses_kennwort_nicht_kennt_kann_die"))
        g.breit(oeffnen_titel)
        self.oeffnen_kw, self.oeffnen_kw2 = _kennwort(), _kennwort()
        self.oeffnen_kw.setText(s.kennwort_oeffnen); self.oeffnen_kw2.setText(s.kennwort_oeffnen)
        g.reihe((_t("pdf.kennwort"), self.oeffnen_kw), (_t("pdf.bestaetigung"), self.oeffnen_kw2))
        self.oeffnen_kw.setAccessibleName(_t("pdf.kennwort_zum_oeffnen_der_pdf")); self.oeffnen_kw2.setAccessibleName(_t("pdf.bestaetigung_des_kennworts_zum_oeffnen"))
        v.addWidget(self.innen)
        self.verschluesseln.toggled.connect(self.innen.setEnabled); self.innen.setEnabled(s.verschluesseln)
        return bereich

    def _seiten_schalten(self, an: bool) -> None:
        for feld in (self.von, self.bis, self.l_von, self.l_bis):
            feld.setEnabled(an)

    def _durchsuchen(self) -> None:
        from vcl.qt.widgets.bausteine.dokument.speichern_fenster import datei_speichern
        neu = datei_speichern(self, _t("pdf.pdf_datei_exportieren"), self.pfad.text().strip(), _t("pdf.pdf_dokument_pdf"))
        if neu:
            self.pfad.setText(neu); self._ersetzen_ok = neu

    def ergebnis(self) -> PdfWahl:
        bereich = next(key for key, button in self._bereiche.items() if button.isChecked())
        w = PdfWahl(pfad=os.path.expanduser(self.pfad.text().strip()), bereich=bereich, von=self.von.value(), bis=self.bis.value(),
                    verschluesseln=self.verschluesseln.isChecked(), kennwort_rechte=self.rechte_kw.text(),
                    kennwort_oeffnen=self.oeffnen_kw.text(), druck=self.druck.currentData(), schliessen=self.schliessen.isChecked())
        for key, box in {**self.optionen, **self.rechte}.items():
            setattr(w, key, box.isChecked())
        return w

    def _ok(self) -> None:
        w = self.ergebnis()
        fehler = ""
        if not w.pfad:
            fehler = _t("pdf.bitte_gib_einen_dateinamen_und_speichero")
        elif not os.path.isdir(os.path.dirname(w.pfad) or "."):
            fehler = _t("pdf.der_gewaehlte_ordner_0_ist_nicht_vorhand").format(os.path.dirname(w.pfad))
        if fehler:
            self.pfad.setFocus()
        elif w.verschluesseln:
            fehler = kennwort_fehler(w, self.rechte_kw2.text(), self.oeffnen_kw2.text())
            if fehler:
                self.schutz_knopf.setChecked(True)
                if fehler.startswith(_t("pdf.das_kennwort_fuer_die_berechtigungen")):
                    self.rechte_kw2.setFocus()
                else:
                    self.oeffnen_kw2.setFocus()
        if fehler:
            QMessageBox.warning(self, _t("pdf.pdf_export"), fehler)
            return
        if not w.pfad.lower().endswith(".pdf"):
            w.pfad += ".pdf"; self.pfad.setText(w.pfad)
        if os.path.exists(w.pfad) and w.pfad != self._ersetzen_ok and QMessageBox.question(
                self, _t("pdf.pdf_ersetzen"), _t("pdf.0_ist_schon_vorhanden_moechtest_du_die_d").format(os.path.basename(w.pfad)),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        if not self._exportieren(w):
            return
        self._wahl = w; self._ersetzen_ok = w.pfad
        if w.schliessen:
            self._zurueck()
        else:
            self.meldung.setText(_t("pdf.pdf_gespeichert_0").format(w.pfad))
            self.meldung.show()

    def wahl(self) -> PdfWahl | None:
        return self._wahl
