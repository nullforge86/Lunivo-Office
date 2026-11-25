"""Optionen: Leichter lesen, Sprache."""
from __future__ import annotations

from lunivo_writer.core.schrift import standard_datenbank
from lunivo_writer.oberflaeche.baukasten.basis.darstellung import eigenschaft, farbflaeche, rolle as _rolle

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte

from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t

from lunivo_writer.oberflaeche.baukasten.geruest.module import anmelden

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QFrame, QLabel, QRadioButton, QPushButton, QWidget
from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import text_label
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen import lesestufen as LS
from lunivo_writer.dienste.dokumentpflege import vorlesen
from lunivo_writer.oberflaeche.dialoge.lesen_hilfe.lesehilfe_dialog import PAPIERTOENE
from lunivo_writer.farmwork.datentypen.farben import Farbe
from lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam import LESESCHRIFTEN, _Seite
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_GROSS, ABSTAND_SPALTEN, PADDING_LESEN_VORSCHAU, RADIUS_FELD, RAND_ZEILE, SCHRIFT_HINWEIS


anmelden("optionen", "lesen", "optionen.seite.lesen", "_lesehilfe", 10)

class LesenSeiten:
    """Optionen: Leichter lesen, Sprache. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``)."""


    # ================= Leichter lesen =================
    def _lesehilfe(self, titel):
        p = _Seite(self.w, titel)
        refs: dict = {}
        stufen = LS.STUFEN
        proben = (_t("optionen.lesen.sehr_geehrte_damen_und_herren_hiermit_ku"),
                  _t("optionen.lesen.bitte_bestaetigen_sie_mir_den_eingang_un"),
                  _t("optionen.lesen.mit_freundlichen_gruessen"))

        def anwenden(_=None):
            self.w.lesehilfe_anwenden()
            vorschau_neu()

        def vorschau_neu():
            lab = refs.get("vorschau")
            if lab is None:
                return
            px_b, px_w = float(p.s.get("lesehilfe/buchstaben", 0)), float(p.s.get("lesehilfe/wort", 0))
            fnt = lab.font(); fnt.setLetterSpacing(QFont.AbsoluteSpacing, px_b); fnt.setWordSpacing(px_w); lab.setFont(fnt)
            _rolle(lab, "papiervorschau")
            farbflaeche(lab, PAPIERTOENE.get(str(p.s.get('lesehilfe/papier', _t("optionen.lesen.weiss"))), Farbe.WEISS), Farbe.SYMBOL)

        # ---- Lesestufe: drei Voreinstellungen, die die Einstellungen darunter setzen
        f = p.gruppe(_t("optionen.lesen.lesestufe"))
        karte = QWidget()
        kv = _spalte("zeile", karte)
        kv.addWidget(QLabel(_t("optionen.lesen.wie_leicht_soll_es_zu_lesen_sein")))
        spalten = _spalte("inhalt")                                    # Lesestufe und Vorschau stehen untereinander über die volle Breite
        links = _spalte("standard")
        links.addWidget(text_label(_t("optionen.lesen.lesestufe"), fett=True, umbruch=False))
        gruppe = QButtonGroup(karte)
        aktuell = LS.aktuell(p.s)
        erlaeutert = text_label(" ".join(stufen[aktuell]["text"] if aktuell else LS.EIGENE))
        _rolle(erlaeutert, "hinweis")
        for name in stufen:
            r = QRadioButton(name)
            r.setProperty("optName", _t("optionen.lesen.lesestufe"))
            r.setChecked(name == aktuell)
            gruppe.addButton(r)
            links.addWidget(r)
            r.toggled.connect(lambda an, n=name: an and waehle_stufe(n))
        links.addStretch(1)
        rechts = _spalte("standard")
        rechts.addWidget(text_label(_t("optionen.lesen.vorschau"), fett=True, umbruch=False))
        vorschau = QLabel("\n\n".join(proben)); vorschau.setWordWrap(True); vorschau.setObjectName("optVorschau")
        refs["vorschau"] = vorschau
        rechts.addWidget(vorschau); rechts.addWidget(erlaeutert)
        spalten.addLayout(links); spalten.addLayout(rechts)
        kv.addLayout(spalten)
        f.addRow(karte)

        def waehle_stufe(name):
            st = stufen[name]
            p.s.set("lesehilfe/stufe", name)
            refs["papier"].setCurrentText(st["papier"])
            refs["buch"].setCurrentIndex(refs["buch"].findData(st["buchstaben"]))
            refs["wort"].setCurrentIndex(refs["wort"].findData(st["wort"]))
            refs["luft"].setCurrentIndex(refs["luft"].findData(st["luft"]))
            refs["groesser"].setCurrentIndex(refs["groesser"].findData(st["groesser"]))
            refs["zurueck"].setCurrentIndex(refs["zurueck"].findData(st["zurueck"]))
            erlaeutert.setText(" ".join(st["text"]))
            anwenden()

        f = p.gruppe(_t("optionen.lesen.leichter_lesen"))
        refs["papier"] = p.auswahl(f, "lesehilfe/papier", _t("optionen.lesen.papierton"), list(PAPIERTOENE), _t("optionen.lesen.weiss"), anwenden)
        refs["buch"] = p.stufen(f, "lesehilfe/buchstaben", _t("optionen.lesen.buchstabenabstand"),
                                LS.BUCHSTABEN, 0.0, anwenden)
        refs["wort"] = p.stufen(f, "lesehilfe/wort", _t("optionen.lesen.wortabstand"),
                                LS.WORT, 0.0, anwenden)
        refs["luft"] = p.stufen(f, "lesehilfe/zeilenluft", _t("optionen.lesen.zeilenluft"), LS.ZEILENLUFT, 1.0, anwenden)
        f = p.gruppe(_t("optionen.lesen.beim_schreiben"))
        refs["fokus"] = p.haken(f, "lesehilfe/zeilenfokus", _t("optionen.lesen.zeilenfokus"), False, lambda on: self.w.lesehilfe_anwenden())
        refs["groesser"] = p.wahl(f, "lesehilfe/groesser", _t("optionen.lesen.absatz_beim_schreiben"),
                                  LS.GROESSER, "keine", anwenden)
        refs["zurueck"] = p.wahl(f, "lesehilfe/zurueck", _t("optionen.lesen.uebriger_text"),
                                 LS.ZURUECK, "keine", anwenden)
        f = p.gruppe(_t("optionen.lesen.vorlesen"))
        p.aktion(_t("optionen.lesen.den_text_hoeren"), _t("optionen.lesen.stimme_und_tempo"), lambda: self.w.befehle.stimmeWaehlen())
        if not vorlesen.verfuegbar():
            p.hinweis(_t("optionen.lesen.es_ist_keine_sprachausgabe_eingerichtet"))
        e = p.mehr()
        f = p.unter(e, _t("optionen.lesen.silben_farbig_lesehilfe_fuer_legasthenie"))
        p.haken(f, "lesehilfe/silben/an", _t("optionen.lesen.silben_farbig_anzeigen"), False, lambda _: self.w.silbenfarben_anwenden())
        b = QPushButton(_t("optionen.lesen.farben_darstellung_und_mindestlaenge_ein"))
        b.clicked.connect(lambda: self.w.befehle.silbenEinstellen())
        f.addRow(b)
        f = p.unter(e, _t("optionen.lesen.silbentrennung"))
        p.auswahl(f, "silben/sprache", _t("optionen.lesen.sprache_der_silbentrennung"), ["de_DE", "de_AT", "de_CH", "en_US", "en_GB", "fr", "es", "it", "nl_NL", "pl_PL", "tr_TR"], "de_DE")
        self._lese_schriften(p, e)
        vorschau_neu()
        p.abschluss()
        return p


    def _silbentrennung_haken(self, p, f):
        """Haken „Silbentrennung“: gilt für das Dokument, das gerade offen ist (derselbe Schalter wie im Reiter Schreibhilfe)."""
        c = QCheckBox(_t("optionen.lesen.silbentrennung"))
        c.setProperty("optName", _t("optionen.lesen.silbentrennung"))
        c.setChecked(bool(self.w.befehle.an_silbentrennung()))
        c.toggled.connect(lambda on: on != bool(self.w.befehle.an_silbentrennung()) and self.w.befehle.silbentrennung())
        f.addRow(c)
        return c


    def _lese_schriften(self, p, e):
        """Die drei Schriften zum leichteren Lesen mit Probe; sagt, ob sie da sind."""
        f = p.unter(e, _t("optionen.lesen.schriften_zum_leichteren_lesen"))
        vorhanden = {n.lower() for n in standard_datenbank.familien()}
        beschreibung = {"OpenDyslexic": _t("optionen.lesen.die_buchstaben_sind_unten_schwerer_sie_k"),
                        "Lexend": _t("optionen.lesen.weitere_abstaende_ruhigeres_zeilenbild"),
                        _t("optionen.lesen.atkinson_hyperlegible"): _t("optionen.lesen.unterscheidet_zeichen_wie_i_l_und_1")}
        reihe = QWidget(); rh = _reihe("zeile", reihe)
        for n in LESESCHRIFTEN:
            k = QFrame(); k.setObjectName("optSchriftkarte")
            kv = _spalte("standard", k)
            name = QLabel(n)
            if n.lower() in vorhanden:
                fnt = QFont(n); fnt.setPointSizeF(13); name.setFont(fnt)
            kv.addWidget(name)
            t = text_label(beschreibung.get(n, "") + ("" if n.lower() in vorhanden else _t("optionen.lesen.fehlt_skripte_schrift_holen_sh_holt_sie")))
            _rolle(t, "hinweis")
            kv.addWidget(t)
            rh.addWidget(k, 1)
        reihe.setProperty("optName", _t("optionen.lesen.schriften_zum_leichteren_lesen"))
        f.addRow(reihe)


    def _uebersetzung_oeffnen(self) -> None:
        from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import ausfuehren
        from lunivo_writer.oberflaeche.dialoge.ki.ki_dialoge import KIEinstellungenDialog
        ausfuehren(KIEinstellungenDialog(self.w, 2))
        self.w.ki.geaendert.emit()
