"""Optionen: Schreiben, Speichern, Drucken und PDF."""
from __future__ import annotations

from lunivo_writer.core.schrift import standard_datenbank
from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t

from lunivo_writer.oberflaeche.baukasten.geruest.module import anmelden

import os
from PySide6.QtWidgets import QComboBox, QLineEdit, QMessageBox, QPushButton, QSpinBox
from lunivo_writer.korrektur import autokorrektur
from lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam import _Seite
from lunivo_writer.oberflaeche.baukasten.basis.mass import HOEHE_FELD
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld


anmelden("optionen", "schreiben", "optionen.seite.schreiben", "_schreiben", 30)
anmelden("optionen", "speichern", "optionen.seite.speichern", "_speichern", 40)
anmelden("optionen", "drucken", "optionen.seite.drucken", "_drucken", 50)

class DateiSeiten:
    """Optionen: Schreiben, Speichern, Drucken und PDF. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``)."""


    def _schreiben(self, titel):
        """Schrift für neuen Text, Prüfung, AutoKorrektur; im Einzelnen eingeklappt (alle AutoKorrektur-Fälle bleiben erhalten)."""
        p = _Seite(self.w, titel)
        f = p.gruppe(_t("optionen.datei.schrift_fuer_neuen_text"))
        fam = Auswahlfeld(); fam.setEditable(True)
        fam.addItems(standard_datenbank.familien())
        fam.setCurrentText(p.s.get("standard/schrift", "Liberation Sans"))
        fam.currentTextChanged.connect(lambda t: p.s.set("standard/schrift", t))
        fam.setAccessibleName(_t("optionen.datei.schrift_fuer_neuen_text"))
        f.addRow(_t("optionen.datei.schrift"), fam)
        p.zahl(f, "standard/groesse", _t("optionen.datei.groesse"), 6, 72, 11, _t("optionen.datei.pt"), 1)
        f = p.gruppe(_t("optionen.datei.pruefen"))
        p.haken(f, "schreibhilfe/wellen", _t("optionen.datei.rechtschreibung_waehrend_der_eingabe_pru"), True, lambda on: self.w.assistant.setze("wellen", on))
        p.haken(f, "rsGrammatik", _t("optionen.datei.grammatik_mitpruefen"), True, lambda _: self.w.assistant.pruefen(voll=True))
        self._silbentrennung_haken(p, f)
        p.aktion(_t("optionen.datei.sprache_fuer_die_pruefung_und_uebersetze"), _t("optionen.datei.ki_einstellungen_sprache"), self._uebersetzung_oeffnen)
        f = p.gruppe(_t("optionen.datei.autokorrektur"))
        p.haken(f, "schreibhilfe/autokorr", _t("optionen.datei.autokorrektur"), True, lambda on: self.w.assistant.setze("autokorr", on))
        p.haken(f, "schreibhilfe/vorhersage", _t("optionen.datei.wortvorhersage"), True, lambda on: self.w.assistant.setze("vorhersage", on))
        e = p.mehr()
        f = p.unter(e, _t("optionen.datei.autokorrektur_gross_und_kleinschreibung"))
        for name in ("akSatzGross", "akWochentage", "akFeststelltaste", "akOrdnungszahlen"):
            std, text = autokorrektur.SCHALTER[name]
            p.haken(f, "schreibhilfe/" + name, text, std)
        f = p.unter(e, _t("optionen.datei.autokorrektur_zeichen"))
        for name in ("akAnfuehrung", "akGedankenstrich", "akAuslassung"):
            std, text = autokorrektur.SCHALTER[name]
            p.haken(f, "schreibhilfe/" + name, text, std)
        p.haken(f, "schreibhilfe/akPfade", _t("optionen.datei.internet_und_netzwerkpfade_durch_hyperli"), True)
        f = p.unter(e, _t("optionen.datei.autokorrektur_einzuege_und_leerzeichen"))
        p.haken(f, "schreibhilfe/akErstzeile", _t("optionen.datei.leerzeichen_am_absatzanfang_mit_erstzeil"), False)
        p.haken(f, "schreibhilfe/akRechtsLeer", _t("optionen.datei.leerzeichenformat_am_ende_rechtsbuendige"), False)
        p.haken(f, "schreibhilfe/akZentriert", _t("optionen.datei.bei_zentriertem_ausrichten_erstzeilenein"), True)
        p.haken(f, "schreibhilfe/akTabEinzug", _t("optionen.datei.tabulator_und_ruecktaste_setzen_den_einz"), True)
        f = p.unter(e, _t("optionen.datei.pruefung_im_einzelnen"))
        p.haken(f, "schreibhilfe/vorschlaege", _t("optionen.datei.immer_korrekturvorschlaege_unterbreiten"), True)
        p.haken(f, "rsGrossIgnorieren", _t("optionen.datei.woerter_in_grossbuchstaben_ignorieren"), True, lambda _: self.w.assistant.pruefen(voll=True))
        p.haken(f, "rsZahlenIgnorieren", _t("optionen.datei.woerter_mit_zahlen_ignorieren"), True, lambda _: self.w.assistant.pruefen(voll=True))
        p.haken(f, "rsPfadeIgnorieren", _t("optionen.datei.internet_und_netzwerkpfade_ignorieren"), True, lambda _: self.w.assistant.pruefen(voll=True))
        p.aktion(_t("optionen.datei.weggewinkte_funde_wieder_anzeigen"), _t("optionen.datei.wieder_anzeigen"),
                 lambda: (self.w.assistant._weg.clear(), self.w.assistant.pruefen(voll=True)))
        p.aktion(_t("optionen.datei.gruendlich_pruefen"), _t("optionen.datei.gruendlich_pruefen_2"), lambda: self.w.befehle.tun("gruendlichPruefen"))
        f = p.unter(e, _t("optionen.datei.autoformat"))
        p.haken(f, "autoformat/liste", _t("optionen.datei.automatisch_nummerierte_listen"), True)
        p.haken(f, "autoformat/punkte", _t("optionen.datei.aufzaehlungen_erkennen"), True)
        p.haken(f, "schreibhilfe/akKreiszahl", _t("optionen.datei.zahl_automatisch_im_kreis"), False)
        f = p.unter(e, _t("optionen.datei.bearbeiten_und_einfuegen"))
        p.haken(f, "bearbeiten/wortweise", _t("optionen.datei.wortweise_markieren"), True)
        p.haken(f, "bearbeiten/ziehen", _t("optionen.datei.text_mit_der_maus_verschieben"), True, lambda _: self.w.lesehilfe_anwenden())
        p.haken(f, "bearbeiten/tippen_ersetzt", _t("optionen.datei.tippen_ersetzt_die_auswahl"), False)
        p.haken(f, "bearbeiten/einfuegen_schaltflaeche", _t("optionen.datei.schaltflaeche_nach_dem_einfuegen"), True)
        p.haken(f, "bearbeiten/mittlere_taste", _t("optionen.datei.mittlere_maustaste_fuegt_ein"), True)
        from lunivo_writer.oberflaeche.dokument.bearbeitung.kern_editor import EINFUEGE_MODI
        p.wahl(f, "bearbeiten/einfuegen_standard", _t("optionen.datei.standardeinfuegeformat"), [(m, m) for m in EINFUEGE_MODI], EINFUEGE_MODI[0])
        f = p.unter(e, _t("optionen.datei.eigenes_woerterbuch_und_gelernte_schreib"))
        f.addRow(self._gedaechtnis(""))
        p.abschluss()
        return p


    def _speichern(self, titel):
        p = _Seite(self.w, titel)
        f = p.gruppe(_t("optionen.datei.speichern"))
        p.wahl(f, "speichern/standard", _t("optionen.datei.dateien_als_standard_speichern"), [(_t("optionen.datei.docx_dokument_docx"), ".docx"), (_t("optionen.datei.textdatei_txt"), ".txt")], ".docx")
        p.pfad(f, "speichern/ordner", _t("optionen.datei.ordner_zum_speichern"), _t("optionen.datei.zuletzt_benutzter_ordner"))
        from lunivo_writer.oberflaeche.dialoge import dokument_dialoge as _d
        p.wahl(f, "ui/masseinheit", _t("optionen.datei.masseinheit"), [(n, n) for n in _d.EINHEITEN], _t("optionen.datei.millimeter"), _d.set_einheit)
        f = p.gruppe(_t("optionen.datei.sicherung"))
        p.wahl(f, "sicherung/aktiv", _t("optionen.datei.wann_gesichert_wird"), [(_t("optionen.datei.laufend_nach_jeder_aenderung"), True), (_t("optionen.datei.nie"), False)], True)
        minuten = QSpinBox(); minuten.setRange(1, 120); minuten.setSuffix(_t("optionen.datei.min")); minuten.setMinimumHeight(HOEHE_FELD)
        minuten.setValue(max(1, p.s.get_int("autosave_seconds", 60) // 60))

        def neu(m):
            p.s.set("autosave_seconds", m * 60)
            self.w.autosave.start(m * 60 * 1000)
        minuten.valueChanged.connect(neu)
        f.addRow(_t("optionen.datei.abstand_minuten"), minuten)
        e = p.mehr()
        f = p.unter(e, _t("optionen.datei.weiteres_zum_speichern"))
        p.haken(f, "start/letztes_oeffnen", _t("optionen.datei.beim_start_das_zuletzt_geschriebene_doku"), False)
        p.haken(f, "speichern/bilder_nicht_komprimieren", _t("optionen.datei.bilder_in_der_datei_nicht_komprimieren"), True)
        p.wahl(f, "ausgabe/ppi", _t("optionen.datei.standard_ausgabeziel"),
               [(t, t) for t in (_t("optionen.datei.96_ppi_bildschirm"), _t("optionen.datei.150_ppi_web_entwurf"), _t("optionen.datei.220_ppi_druck"), _t("optionen.datei.330_ppi_hohe_qualitaet"))],
               _t("optionen.datei.150_ppi_web_entwurf"))
        p.pfad(f, "vorlagen/ordner", _t("optionen.datei.eigene_vorlagen"), "~/Vorlagen")
        f = p.unter(e, _t("optionen.datei.zwischenstaende"))
        p.zahl(f, "sicherung/tage", _t("optionen.datei.aufbewahren_tage"), 1, 365, 7, _t("optionen.datei.tage"))
        p.aktion(_t("optionen.datei.zwischenstaende_loeschen"), _t("optionen.datei.zwischenstaende_loeschen"), self._zwischenstaende_loeschen)
        p.aktion(_t("optionen.datei.vorfassungen_gespeicherter_dokumente_je"), _t("optionen.datei.sicherungskopien_oeffnen"),
                 self._sicherungskopien_oeffnen)
        f = p.unter(e, _t("optionen.datei.gedaechtnis_und_woerterbuch_sichern"))
        p.aktion(_t("optionen.datei.sichern_und_zurueckholen"), _t("optionen.datei.sichern"), self._daten_sichern)
        zb = QPushButton(_t("optionen.datei.einspielen")); zb.clicked.connect(self._daten_zurueckholen)
        f.addRow(zb)
        ort = QLineEdit(p.s.datei()); ort.setReadOnly(True); ort.setAccessibleName(_t("optionen.datei.ort_der_einstellungsdatei"))
        f.addRow(_t("optionen.datei.einstellungsdatei"), ort)
        f = p.unter(e, _t("optionen.datei.dokument_schuetzen_und_aenderungen"))
        p.aktion(_t("optionen.datei.kennwort_bearbeitung_sperren_datenschutz"), _t("optionen.datei.kennwort_und_datenschutz"), lambda: self._anpassen("sicherheit"))
        p.aktion(_t("optionen.datei.aenderungen_verfolgen_markup_farben_spre"), _t("optionen.datei.aenderungen_verfolgen"), lambda: self._anpassen("verfolgen"))
        p.abschluss()
        return p


    def _zwischenstaende_loeschen(self):
        import shutil
        from lunivo_writer.dienste.dokumentpflege import wiederherstellung
        ordner = wiederherstellung.recovery_dir()
        if QMessageBox.question(self, _t("optionen.datei.zwischenstaende_loeschen"), _t("optionen.datei.alle_gesicherten_zwischenstaende_in_0_wi").format(ordner)) != QMessageBox.Yes:
            return
        n = 0
        for name in os.listdir(ordner) if os.path.isdir(ordner) else []:
            pfad = os.path.join(ordner, name)
            try:
                shutil.rmtree(pfad) if os.path.isdir(pfad) else os.remove(pfad)
                n += 1
            except OSError:
                pass
        QMessageBox.information(self, _t("optionen.datei.zwischenstaende_loeschen"), _t("optionen.datei.0_zwischenstaende_geloescht").format(n))


    def _sicherungskopien_oeffnen(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        from lunivo_writer.dienste.dateizugriff import sicher_schreiben
        ordner = sicher_schreiben.sicherungs_ordner()
        os.makedirs(ordner, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(ordner))


    def _daten_sichern(self):
        import zipfile
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
        from lunivo_writer.farmwork.funktionen.datei.orte import data_dir
        pfad, _ = Dateifenster.getSaveFileName(self, _t("optionen.datei.sichern_2"), "lunivo-sicherung.zip", _t("optionen.datei.zip_zip"))
        if not pfad:
            return
        with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED) as z:
            for n in ("gelernt.json",):
                f = os.path.join(data_dir(), n)
                if os.path.exists(f):
                    z.write(f, n)
        QMessageBox.information(self, _t("optionen.datei.sichern_2"), _t("optionen.datei.gesichert") + pfad)


    def _daten_zurueckholen(self):
        import zipfile
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
        from lunivo_writer.farmwork.funktionen.datei.orte import data_dir
        pfad, _ = Dateifenster.getOpenFileName(self, _t("optionen.datei.zurueckholen"), "", _t("optionen.datei.zip_zip"))
        if not pfad:
            return
        try:
            with zipfile.ZipFile(pfad) as z:
                if "gelernt.json" in z.namelist():
                    z.extract("gelernt.json", data_dir())
            self.w.assistant.gelernt.laden(); self.w.assistant.pruefen(voll=True)
        except (OSError, zipfile.BadZipFile) as ex:
            QMessageBox.warning(self, _t("optionen.datei.zurueckholen"), _t("optionen.datei.der_zwischenstand_wurde_nicht_zurueckgeh").format(ex))
            return
        QMessageBox.information(self, _t("optionen.datei.zurueckholen"), _t("optionen.datei.zurueckgeholt"))


    def _drucken(self, titel):
        """Drucken und PDF auf einer Seite: das Häufige sichtbar, der Rest eingeklappt."""
        p = _Seite(self.w, titel)
        f = p.gruppe(_t("optionen.datei.drucken"))
        p.haken(f, "drucken/hoch", _t("optionen.datei.hohe_qualitaet"), True)
        p.haken(f, "drucken/hintergrund", _t("optionen.datei.hintergrundfarben_und_bilder_drucken"), True)
        f = p.gruppe("PDF")
        p.haken(f, "pdf/oeffnen", _t("optionen.datei.pdf_nach_dem_export_oeffnen"), False)
        p.haken(f, "pdf/lz_ueberschriften", _t("optionen.datei.ueberschriften_als_lesezeichen"), False)
        e = p.mehr()
        f = p.unter(e, _t("optionen.datei.drucken_im_einzelnen"))
        p.wahl(f, "drucken/vorgabe", _t("optionen.datei.womit_das_druckfenster_aufgeht"), [(_t("optionen.datei.alle_seiten"), _t("optionen.datei.alle_seiten")), (_t("optionen.datei.aktuelle_seite"), _t("optionen.datei.aktuelle_seite"))], _t("optionen.datei.alle_seiten"))
        p.haken(f, "drucken/umgekehrt", _t("optionen.datei.umgekehrte_reihenfolge"), False)
        p.haken(f, "drucken/zeichnungen", _t("optionen.datei.zeichnungsobjekte_drucken"), True)
        p.haken(f, "drucken/leere", _t("optionen.datei.leere_seiten_mitdrucken"), True)
        p.haken(f, "drucken/felder", _t("optionen.datei.felder_vor_dem_drucken_aktualisieren"), True)
        p.wahl(f, "drucken/versteckt", _t("optionen.datei.ausgeblendeter_text"), [(_t("optionen.datei.ausgeblendeten_text_nicht_drucken"), False), (_t("optionen.datei.ausgeblendeten_text_drucken"), True)], False)
        f = p.unter(e, _t("optionen.datei.pdf_im_einzelnen"))
        p.haken(f, "pdf/kommentare", _t("optionen.datei.kommentare_als_pdf_notizen_mitnehmen"), False)
        p.haken(f, "pdf/eigenschaften", _t("optionen.datei.dokumenteigenschaften_autor_in_das_pdf_u"), True)
        p.haken(f, "pdf/lz_textmarken", _t("optionen.datei.textmarken_uebernehmen"), False)
        p.hinweis(_t("optionen.datei.gedruckt_wird_ueber_das_druckfenster_des"))
        p.abschluss()
        return p
