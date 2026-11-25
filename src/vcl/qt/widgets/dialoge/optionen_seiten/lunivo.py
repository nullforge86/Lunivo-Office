"""Optionen: KI, Gedächtnis, Erweitert."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein

from core.formatierung.schrift import standard_datenbank
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft, rolle as _rolle

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from vcl.qt.widgets.bausteine.skalierung.daten import text as _t

import json
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QWidget
from vcl.qt.widgets.bausteine.schrift.beschriftung import text_label
from writer.funktionen import ki as KD
from framework.dokumentverwaltung.dokumentpflege import vorlesen
from system.plattform import pfade
from core.korrektur.woerterbuecher.vorhersage import EMPFAENGER
from vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam import LESESCHRIFTEN, _Seite
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_ENG, ABSTAND_NORMAL, BREITE_KNOPF_KLEIN, HOEHE_VORSCHAU_KLEIN, PADDING_PLAKETTE, PADDING_STARTKNOPF_LINK, RADIUS_KLEIN, RAND_KARTE_ZEILE, RAND_KEIN, RAND_ZEILE, RAND_ZEILE_ENG, SCHRIFT_HINWEIS, SCHRIFT_LISTE, SCHRIFT_KLEIN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld


class LunivoSeiten:
    """Optionen: KI, Gedächtnis, Erweitert. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``)."""


    # ================= Nur bei Lunivo =================
    def _ki(self, titel):
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        p = _Seite(self.w, titel)
        k = self.w.ki.konfig
        geaendert = self.w.ki.geaendert
        f = p.gruppe(_t("optionen.lunivo.pruefung_und_ki"))
        f.addRow(text_label(_t("optionen.lunivo.ki_konfiguration"), umbruch=False))
        combos: dict[str, QComboBox] = {}

        def standard_name() -> str:
            mid = k["modell"]
            if not mid:
                return "(keines)"
            for m in k.alle_modelle():
                if m["id"] == mid:
                    return m["name"]
            return mid[len(KD.ollama_marke()):] if mid.startswith(KD.ollama_marke()) else mid

        from vcl.qt.widgets.dialoge.ki.ki_dialoge import modell_felder_fuellen

        def aufgaben_fuellen():
            for aufgabe, c in combos.items():
                modell_felder_fuellen(c, k, aufgabe, standard=_t("optionen.lunivo.standard_0").format(standard_name()))
        for aufgabe, name in KD.aufgaben():
            c = Auswahlfeld()
            combos[aufgabe] = c
            c.currentIndexChanged.connect(lambda _i, a=aufgabe, c=c: (k.aufgabe_setzen(a, c.currentData() or ""), geaendert.emit()))
            f.addRow(name, c)
        mb = knopf("standard", _t("optionen.lunivo.ki_modelle_bearbeiten"), ohne_rand=True, hand=True)
        mb.setProperty("akzentSchrift", True); _rolle(mb, "link_links")
        f.addRow(mb)

        schluessel = zeilenfeld("frei", k["apiKey"], platzhalter="sk-ant-…", passwort=True)
        schluessel.setProperty("optName", _t("optionen.lunivo.api_schluessel"))
        f.addRow(_t("optionen.lunivo.api_schluessel"), schluessel)
        hinweis = QLabel(); _rolle(hinweis, "hinweis"); hinweis.setWordWrap(True)
        f.addRow(hinweis)
        zeile = QWidget(); h = _reihe("standard", zeile)
        zeigen = knopf("standard", _t("optionen.lunivo.anzeigen"), umschaltbar=True)
        kopie = knopf("standard", _t("optionen.lunivo.kopieren"))
        loeschen = knopf("standard", _t("optionen.lunivo.schluessel_loeschen"))
        erstellen = knopf("standard", _t("optionen.lunivo.schluessel_erstellen"), ohne_rand=True, hand=True)
        erstellen.setProperty("akzentSchrift", True); _rolle(erstellen, "link")
        for b in (zeigen, kopie, loeschen, erstellen):
            h.addWidget(b)
        h.addStretch(1)
        f.addRow(zeile)

        def schluessel_stand():
            hinweis.setText(_t("optionen.lunivo.gespeichert_in") + k.pfad + _t("optionen.lunivo.nur_fuer_dich_lesbar_bei_nutzung_von_cla") if k["apiKey"] else
                            _t("optionen.lunivo.kein_schluessel_fuer_das_modell_auf_dies"))
            for b in (zeigen, kopie, loeschen):
                b.setEnabled(bool(schluessel.text().strip()))
        schluessel.editingFinished.connect(lambda: (k.setze("apiKey", schluessel.text().strip()), schluessel_stand(), geaendert.emit()))
        schluessel.textChanged.connect(lambda _t: [b.setEnabled(bool(schluessel.text().strip())) for b in (zeigen, kopie, loeschen)])
        zeigen.toggled.connect(lambda an: (schluessel.setEchoMode(QLineEdit.Normal if an else QLineEdit.Password),
                                           zeigen.setText(_t("optionen.lunivo.verbergen") if an else _t("optionen.lunivo.anzeigen"))))
        kopie.clicked.connect(lambda: QApplication.clipboard().setText(schluessel.text().strip()))

        def loesche():
            if QMessageBox.question(self, _t("optionen.lunivo.schluessel_loeschen"), _t("optionen.lunivo.den_gespeicherten_schluessel_wirklich_lo")) == QMessageBox.Yes:
                schluessel.clear(); k.setze("apiKey", ""); schluessel_stand(); geaendert.emit()
        loeschen.clicked.connect(loesche)
        erstellen.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://console.anthropic.com/settings/keys")))

        modell = Auswahlfeld()
        f.addRow(_t("optionen.lunivo.ki_modell"), modell)

        def modell_fuellen():
            modell.blockSignals(True); modell.clear()
            modell.addItem("(keines)", "")
            for mid, name in KD.modelle_fest():
                modell.addItem(name, mid)
            for m in self.w.ki.ki.ollama_modelle():
                modell.addItem(_t("optionen.lunivo.auf_diesem_rechner_0").format(m), KD.ollama_marke() + m)
            for a in k["anbieter"]:
                modell.addItem(f"{a['name']} ({a['modell']})", KD.eigen_marke() + a["id"])
            modell.setCurrentIndex(max(0, modell.findData(k["modell"])))
            modell.blockSignals(False)
        modell.currentIndexChanged.connect(lambda _i: (k.setze("modell", modell.currentData()), aufgaben_fuellen(), geaendert.emit()))

        anb = QWidget(); av = _spalte("zeile", anb)
        anb.setProperty("optName", _t("optionen.lunivo.eigene_anbieter"))
        f.addRow(QLabel(_t("optionen.lunivo.eigene_anbieter")))
        f.addRow(anb)
        neuer = knopf("standard", _t("optionen.lunivo.anbieter_hinzufuegen"))
        f.addRow(neuer)

        def anbieter_fuellen():
            while av.count():
                it = av.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
            if not k["anbieter"]:
                av.addWidget(QLabel(_t("optionen.lunivo.noch_keiner_angelegt_ollama_openai_openr")))
            for a in k["anbieter"]:
                z = QWidget(); zh = _reihe("standard", z)
                teile = [a["modell"], _t("optionen.lunivo.lokaler_anbieter") if KD.ist_lokale_url(a["url"]) else _t("optionen.lunivo.ueber_das_internet")]
                zh.addWidget(QLabel(f"{a['name']}  ·  {' · '.join(t for t in teile if t)}"), 1)
                eb = knopf("standard", _t("optionen.lunivo.entfernen"))
                eb.clicked.connect(lambda _=False, i=a["id"]: (k.anbieter_entfernen(i), alles_neu(), geaendert.emit()))
                zh.addWidget(eb)
                av.addWidget(z)

        def alles_neu():
            aufgaben_fuellen(); modell_fuellen(); anbieter_fuellen()

        def anbieter_neu():
            from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
            from vcl.qt.widgets.dialoge.ki.ki_dialoge import KIEinstellungenDialog
            ausfuehren(KIEinstellungenDialog(self.w, 0))
            alles_neu(); geaendert.emit()

        def modelle_bearbeiten():
            from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
            from vcl.qt.widgets.dialoge.ki.ki_dialoge import KIEinstellungenDialog
            ausfuehren(KIEinstellungenDialog(self.w, 0))
            alles_neu(); geaendert.emit()
        neuer.clicked.connect(anbieter_neu)
        mb.clicked.connect(modelle_bearbeiten)

        f.addRow(QLabel(_t("optionen.lunivo.assistenten")))
        from vcl.qt.widgets.bausteine.interaktion.felder.assistenten_liste import AssistentenListe
        ass = AssistentenListe(self.w); ass.setProperty("optName", _t("optionen.lunivo.assistenten"))
        f.addRow(ass)

        wen = Auswahlfeld(); wen.addItems(EMPFAENGER)
        wen.setCurrentText(self.w.assistant.thema)
        wen.currentTextChanged.connect(self.w.assistant.setze_thema)
        self.w.assistant.themaGeaendert.connect(lambda t: wen.currentText() != t and (wen.blockSignals(True), wen.setCurrentText(t), wen.blockSignals(False)))
        f.addRow(_t("optionen.lunivo.fuer_wen_der_text_ist"), wen)

        verbrauch = QWidget(); vh = _reihe("zeile", verbrauch)
        vh.addWidget(QLabel(_t("optionen.lunivo.verbrauch")))
        vh.addWidget(QLabel(_t("optionen.lunivo.noch_nichts_verbraucht") if not k["kosten"] else _t("optionen.lunivo.bisherige_kosten_0").format(KD.als_geld(k['kosten']))))
        auf = knopf("standard", _t("optionen.lunivo.guthaben_aufladen"), ohne_rand=True, hand=True)
        auf.setProperty("akzentSchrift", True); _rolle(auf, "link")
        auf.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://console.anthropic.com/settings/billing")))
        vh.addWidget(auf); vh.addStretch(1)
        f.addRow(verbrauch)
        alles_neu(); schluessel_stand()
        verbindung = self.w.ki.geaendert.connect(lambda: (aufgaben_fuellen(), modell_fuellen(), anbieter_fuellen()))
        p.destroyed.connect(lambda *_: self.w.ki.geaendert.disconnect(verbindung))       # sonst greift die Verbindung nach dem Schließen der Seite auf gelöschte Felder
        p.abschluss()
        return p


    def _gedaechtnis(self, titel):
        from PySide6.QtWidgets import QListWidget
        from vcl.qt.widgets.dialoge.dokument.speichern_fenster import Dateifenster
        p = _Seite(self.w, titel)
        g = self.w.assistant.gelernt
        f = p.gruppe(_t("optionen.lunivo.gelernte_schreibweisen"))
        zeile = QWidget(); h = _reihe("zeile", zeile)
        lab = QLabel(); _rolle(lab, "text")
        vergessen = knopf("standard", "vergessen")
        h.addWidget(lab, 1); h.addWidget(vergessen)
        f.addRow(zeile)
        zeile.setProperty("optName", _t("optionen.lunivo.gelernte_schreibweisen"))
        liste = QListWidget(); liste.setMinimumHeight(HOEHE_VORSCHAU_KLEIN); liste.setAccessibleName(_t("optionen.lunivo.gelernte_schreibweisen"))

        def fuellen():
            d = g.daten
            lab.setText(_t("optionen.lunivo.0_eigene_schreibweisen_1_woerter_in_ruhe").format(len(d['woerter']), len(d['inRuhe'])))
            liste.clear()
            for alt, neu in sorted(d["woerter"].items()):
                liste.addItem(f"{alt} → {neu}")
            for w_ in sorted(d["inRuhe"]):
                liste.addItem(_t("optionen.lunivo.0_in_ruhe_lassen").format(w_))
            vergessen.setEnabled(bool(d["woerter"] or d["inRuhe"] or d["gezeigt"] or d["ki"]))
        f.addRow(liste)
        eb = knopf("standard", _t("optionen.lunivo.markierten_eintrag_entfernen"))

        def eintrag_weg():
            it = liste.currentItem()
            if not it:
                return
            t = it.text()
            if " → " in t:
                g.daten["woerter"].pop(t.split(" → ")[0], None)
            else:
                g.daten["inRuhe"].pop(t.replace(_t("optionen.lunivo.in_ruhe_lassen"), ""), None)
            g.speichern(); fuellen(); self.w.assistant.pruefen(voll=True)
        eb.clicked.connect(eintrag_weg)

        def weg():
            if QMessageBox.question(self, _t("optionen.lunivo.vergessen"), _t("optionen.lunivo.wirklich_alles_gelernte_loeschen")) == QMessageBox.Yes:
                g.vergessen(); fuellen(); self.w.assistant.pruefen(voll=True)
        vergessen.clicked.connect(weg)

        def sichern():
            pfad, _ = Dateifenster.getSaveFileName(self, _t("optionen.lunivo.gelerntes_sichern"), "gelernt.json", _t("optionen.lunivo.json_json"))
            if pfad:
                try:
                    with open(pfad, "w", encoding="utf-8") as fh:
                        json.dump(g.daten, fh, ensure_ascii=False, indent=1)
                except OSError as ex:
                    QMessageBox.warning(self, _t("optionen.lunivo.sichern"), _t("optionen.lunivo.die_sicherung_wurde_nicht_angelegt_grund").format(ex))

        def einspielen():
            pfad, _ = Dateifenster.getOpenFileName(self, _t("optionen.lunivo.gelerntes_einspielen"), "", _t("optionen.lunivo.json_json"))
            if not pfad:
                return
            try:
                with open(pfad, encoding="utf-8") as fh:
                    neu = json.load(fh)
                for key in g.daten:
                    if isinstance(neu.get(key), dict):
                        g.daten[key].update(neu[key])
            except (OSError, ValueError) as ex:
                QMessageBox.warning(self, _t("optionen.lunivo.einspielen"), _t("optionen.lunivo.die_datei_wurde_nicht_eingespielt_pruefe").format(ex))
                return
            g.speichern(); fuellen(); self.w.assistant.pruefen(voll=True)
        z2 = QWidget(); h2 = _reihe("zeile", z2)
        b1 = knopf("standard", _t("optionen.lunivo.sichern")); b2 = knopf("standard", _t("optionen.lunivo.einspielen"))
        b1.clicked.connect(sichern); b2.clicked.connect(einspielen)
        h2.addWidget(b1); h2.addWidget(b2); h2.addWidget(eb); h2.addStretch(1)
        f.addRow(z2)
        fuellen()
        p.hinweis(_t("optionen.lunivo.das_gedaechtnis_liegt_als_datei_auf_dies"))
        p.abschluss()
        return p


    def _erweitert(self, titel):
        from framework.dokumentverwaltung.integrationen import languagetool
        from framework.befehle.datei.orte import data_dir
        p = _Seite(self.w, titel)

        def groesse(pfad) -> str:
            gesamt = 0
            if pfad and os.path.exists(pfad):
                if os.path.isfile(pfad):
                    gesamt = os.path.getsize(pfad)
                for wurzel, _d, dateien in os.walk(pfad):
                    for n in dateien:
                        try:
                            gesamt += os.path.getsize(os.path.join(wurzel, n))
                        except OSError:
                            pass
            mb = gesamt / 1048576
            return "" if not gesamt else (_t("optionen.lunivo.0_0f_mb").format(mb) if mb >= 10 else _t("optionen.lunivo.0_1f_mb").format(mb).replace(".", ","))

        lt = languagetool.jar_finden()
        _prog, piper = vorlesen.piper_programm()
        stimmen = vorlesen.piper_stimmen() if piper else []
        schriften = [n for n in LESESCHRIFTEN if standard_datenbank.hat_familie(n)]
        schr_ordner = pfade.schriften_dir()
        karten = [
            ("LanguageTool", _t("optionen.lunivo.gruendlich_pruefen_grammatik_ueber_die_e"), bool(lt), languagetool.ordner(), _t("optionen.lunivo.holen")),
            (_t("optionen.lunivo.stimmen_zum_vorlesen_0").format(len(stimmen)), _t("optionen.lunivo.aufgenommene_stimmen_statt_der_blecherne"), bool(stimmen), piper, "stimme-holen.sh"),
            (_t("optionen.lunivo.schriften_zum_leichteren_lesen_0").format(len(schriften)), ", ".join(schriften) or _t("optionen.lunivo.opendyslexic_lexend_atkinson_hyperlegibl"),
             bool(schriften), schr_ordner, "schrift-holen.sh"),
        ]
        f = p.gruppe(_t("optionen.lunivo.was_zusaetzlich_geholt_wurde"))
        for name, beschr, da, pfad, fehlt in karten:
            k = rahmen_baustein("flach", name="optSchriftkarte")
            h = _reihe("karte", k)
            badge = QLabel("DA" if da else "—")
            badge.setAlignment(Qt.AlignCenter); badge.setFixedWidth(BREITE_KNOPF_KLEIN)
            _rolle(badge, "plakette", status="an" if da else "aus")
            h.addWidget(badge, 0, Qt.AlignTop)
            v = _spalte("eng")
            v.addWidget(text_label(name, fett=True, umbruch=False))
            b = QLabel(beschr if da else _t("optionen.lunivo.0_nicht_vorhanden_1").format(beschr, fehlt))
            b.setWordWrap(True); _rolle(b, "kursiv")
            v.addWidget(b)
            h.addLayout(v, 1)
            gr = QLabel(groesse(pfad) if da else ""); _rolle(gr, "hinweis")
            h.addWidget(gr, 0, Qt.AlignTop)
            f.addRow(k)
        f = p.gruppe(_t("optionen.lunivo.daten"))
        p.zeile(f, data_dir())
        p.abschluss()
        return p
