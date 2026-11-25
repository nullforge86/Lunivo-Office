"""Optionen: Menüband, Schnellzugriff, Sicherheit."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken as haken_baustein
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf

from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft, rolle as _rolle

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import anwenden, raender, reihe as _reihe, spalte as _spalte

from vcl.qt.widgets.bausteine.skalierung.daten import text as _t

import json
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QWidget
from vcl.qt.widgets.bausteine.schrift.beschriftung import md_label
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import UmbruchSchalter, FormularGitter, tabellen_gitter
from vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam import _Seite
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_GROSS, ABSTAND_MITTEL, ABSTAND_NORMAL, ABSTAND_SPALTE, BREITE_KNOPF_PFEIL, HOEHE_LISTE_BEFEHLE, ICON_GROSS, RAND_KEIN, RAND_OBEN_KLEIN, RAND_OBEN_SEITE, RAND_ZEILE
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.menues.dropdown.dropdown_knopf import DropdownTaste


class BefehleSeiten:
    """Optionen: Menüband, Schnellzugriff, Sicherheit. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``)."""


    def _zwei_listen(self, p, links_kopf: str, rechts_kopf: str, hinzu: str, weg: str, kategorie: str):
        """Gerüst der Vorlage: links „Befehle auswählen“ (Auswahl, Suche, Liste), in der Mitte Hinzufügen/Entfernen, rechts die Liste
        der aktuellen Einträge mit Pfeilen. Gibt (links, rechts, suche, b_hinzu, b_weg, auf, ab, unten) zurück."""
        w = QWidget(); g = tabellen_gitter(w, rand=RAND_OBEN_SEITE, waagerecht=ABSTAND_SPALTE, senkrecht=ABSTAND_NORMAL)       # Zwei-Listen-Gerüst: Spalten mit festen Aufgaben, Listen über mehrere Zeilen
        g.setColumnStretch(0, 5); g.setColumnStretch(2, 5)
        g.addWidget(QLabel(links_kopf), 0, 0)
        kopf = _reihe("standard")
        auswahl = Auswahlfeld(); auswahl.addItem(kategorie)
        suche = zeilenfeld("frei", platzhalter=_t("optionen.befehle.befehl_suchen")); suche.setClearButtonEnabled(True)
        kopf.addWidget(auswahl, 1); kopf.addWidget(suche, 1)
        g.addLayout(kopf, 1, 0)
        links = QListWidget(); links.setMinimumHeight(HOEHE_LISTE_BEFEHLE); links.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
        g.addWidget(links, 2, 0)
        mitte = _spalte("standard"); mitte.addStretch(1)
        b_hinzu = knopf("standard", hinzu); b_weg = knopf("standard", weg)
        mitte.addWidget(b_hinzu); mitte.addWidget(b_weg); mitte.addStretch(1)
        g.addLayout(mitte, 2, 1)
        g.addWidget(QLabel(rechts_kopf), 0, 2)
        rechts = QListWidget(); rechts.setMinimumHeight(HOEHE_LISTE_BEFEHLE); rechts.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
        pf = _spalte("standard")
        auf = knopf("standard", "▲"); ab = knopf("standard", "▼")
        for b in (auf, ab):
            _rolle(b, "symbol")
        pf.addStretch(1); pf.addWidget(auf); pf.addWidget(ab); pf.addStretch(1)
        rz = _reihe("standard"); rz.addWidget(rechts, 1); rz.addLayout(pf)
        g.addLayout(rz, 1, 2, 2, 1)
        unten = _reihe("oben")
        g.addLayout(unten, 3, 0, 1, 3)
        p.lay.addWidget(w)
        return links, rechts, suche, b_hinzu, b_weg, auf, ab, unten


    @staticmethod
    def _schieben(liste: QListWidget, d: int) -> None:
        i = liste.currentRow(); j = i + d
        if i < 0 or not 0 <= j < liste.count():
            return
        it = liste.takeItem(i)
        liste.insertItem(j, it)
        liste.setCurrentRow(j)


    def _menueband(self, titel):
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge import IMMER
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge_hilfen import lade_json
        from writer.werkzeugleisten.plan import plan
        from vcl.qt.widgets.ribbon.band_leiste import STANDARD_VERSTECKT
        p = _Seite(self.w, titel)
        links, rechts, suche, b_hinzu, b_weg, auf, ab, unten = self._zwei_listen(
            p, _t("optionen.befehle.register_die_ausgeblendet_sind"), _t("optionen.befehle.menueband_anpassen"), _t("optionen.befehle.hinzufuegen"), _t("optionen.befehle.entfernen"), _t("optionen.befehle.ausgeblendete_register"))
        namen = [r["name"] for r in plan(self.w.band.daten) if not r.get("kontext") and r["name"] not in IMMER]
        cfg = lade_json(self.w.settings, "ui/register_plan", {})
        reihenfolge = [n for n in cfg.get("reihenfolge", []) if n in namen] + [n for n in namen if n not in cfg.get("reihenfolge", [])]
        versteckt = set(cfg["versteckt"] if "versteckt" in cfg else STANDARD_VERSTECKT)
        for n in reihenfolge:
            (links if n in versteckt else rechts).addItem(n)

        def speichern():
            sichtbar = [rechts.item(i).text() for i in range(rechts.count())]
            weg = [links.item(i).text() for i in range(links.count())]
            self.w.settings.set("ui/register_plan", json.dumps({"reihenfolge": sichtbar + weg, "versteckt": weg}))
            self._band_merken()

        def verschiebe(von, nach):
            it = von.currentItem()
            if it is None or (nach is links and it.text() in IMMER):
                return
            if nach is links and rechts.count() <= 1 and von is rechts:
                return                                           # mindestens ein Register bleibt
            von.takeItem(von.row(it)); nach.addItem(it); nach.setCurrentItem(it)
            speichern()
        b_hinzu.clicked.connect(lambda: verschiebe(links, rechts))
        b_weg.clicked.connect(lambda: verschiebe(rechts, links))
        links.itemDoubleClicked.connect(lambda _i: verschiebe(links, rechts))
        auf.clicked.connect(lambda: (self._schieben(rechts, -1), speichern()))
        ab.clicked.connect(lambda: (self._schieben(rechts, 1), speichern()))
        suche.textChanged.connect(lambda t: [links.item(i).setHidden(t.lower() not in links.item(i).text().lower())
                                             for i in range(links.count())])
        from PySide6.QtWidgets import QMenu
        unten.addWidget(QLabel(_t("optionen.befehle.tastenkombinationen")))
        tk = knopf("standard", _t("optionen.befehle.anzeigen"))
        tk.clicked.connect(lambda: __import__("vcl.qt.widgets.dialoge.lesen_hilfe.hilfe_dialoge", fromlist=["x"]).tastenkuerzel(self.w).exec())
        unten.addWidget(tk); unten.addStretch(1)
        unten.addWidget(QLabel(_t("optionen.befehle.anpassungen")))
        zr = DropdownTaste(_t("optionen.befehle.zuruecksetzen"))
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe(zr)
        m.eintrag(_t("optionen.befehle.nur_das_menueband"), lambda: (self.w.settings.remove("ui/register_plan"), self._band_merken(), self._band_jetzt()))
        m.eintrag(_t("optionen.befehle.alle_anpassungen_register_schnellzugriff"), self.w.befehle.vorlagenZurueck)
        zr.menue_setzen(m)
        unten.addWidget(zr)
        f = p.gruppe(_t("optionen.befehle.aussehen"))
        for text, fn in ((_t("optionen.befehle.benutzeroberflaeche_waehlen"), self.w.befehle.benutzeroberflaeche),
                         (_t("optionen.befehle.symbole_austauschen"), self.w.befehle.symbolTauschen)):
            b = knopf("standard", text, aktion=fn); f.addRow(b)
        p.abschluss()
        return p


    def _schnellzugriff(self, titel):
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge_hilfen import lade_json
        from vcl.qt.widgets.ribbon.band_leiste import RegisterBand
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        p = _Seite(self.w, titel)
        links, rechts, suche, b_hinzu, b_weg, auf, ab, unten = self._zwei_listen(
            p, _t("optionen.befehle.befehle_auswaehlen"), _t("optionen.befehle.derzeit_angezeigte_optionen"), _t("optionen.befehle.hinzufuegen_pfeil"), _t("optionen.befehle.entfernen_pfeil"), _t("optionen.befehle.haeufig_verwendete_befehle"))
        alle = {aktion: (sym, name) for sym, name, aktion in RegisterBand.SCHNELL_ALLE}
        vorgabe = [a for _s, _n, a in RegisterBand.SCHNELL]

        def eintrag(aktion):
            sym, name = alle[aktion]
            it = QListWidgetItem(symbole.icon(sym, ICON_GROSS), name)
            it.setData(Qt.UserRole, aktion)
            return it

        def fuellen(aktuell):
            links.clear(); rechts.clear()
            for a in aktuell:
                if a in alle:
                    rechts.addItem(eintrag(a))
            for a in alle:
                if a not in aktuell:
                    links.addItem(eintrag(a))
        fuellen(lade_json(self.w.settings, "ui/schnellzugriff", None) or vorgabe)

        def speichern():
            self.w.settings.set("ui/schnellzugriff", json.dumps([rechts.item(i).data(Qt.UserRole) for i in range(rechts.count())]))
            self._band_merken()

        def verschiebe(von, nach):
            it = von.currentItem()
            if it is None:
                return
            von.takeItem(von.row(it)); nach.addItem(it); nach.setCurrentItem(it)
            speichern()
        b_hinzu.clicked.connect(lambda: verschiebe(links, rechts))
        b_weg.clicked.connect(lambda: verschiebe(rechts, links))
        links.itemDoubleClicked.connect(lambda _i: verschiebe(links, rechts))
        rechts.itemDoubleClicked.connect(lambda _i: verschiebe(rechts, links))
        auf.clicked.connect(lambda: (self._schieben(rechts, -1), speichern()))
        ab.clicked.connect(lambda: (self._schieben(rechts, 1), speichern()))
        suche.textChanged.connect(lambda t: [links.item(i).setHidden(t.lower() not in links.item(i).text().lower())
                                             for i in range(links.count())])
        unten.addStretch(1)
        zr = knopf("standard", _t("optionen.befehle.zuruecksetzen_2"))
        zr.clicked.connect(lambda: (self.w.settings.remove("ui/schnellzugriff"), fuellen(vorgabe), self._band_merken()))
        unten.addWidget(zr)
        p.abschluss()
        return p


    def _sicherheit(self, titel):
        p = _Seite(self.w, titel)
        t = self.w.current_tab()
        f = p.gruppe(_t("optionen.befehle.kennwortschutz"))
        w = QWidget(); g = FormularGitter(w); raender(g, "zeile")
        g.beschriftung_voll = True; g.beschriftungsabstand = ABSTAND_GROSS; g.einspaltig = True
        k1 = zeilenfeld("frei", platzhalter=_t("optionen.befehle.kennwort"), passwort=True)
        k2 = zeilenfeld("frei", platzhalter=_t("optionen.befehle.kennwort_erneut_eingeben"), passwort=True)
        zk = _reihe("inhalt"); zk.addWidget(k1, 1); zk.addWidget(k2, 1)
        g.zeile(_t("optionen.befehle.dokumentkennwort"), zk)
        f.addRow(w)
        w.setProperty("optName", _t("optionen.befehle.dokumentkennwort"))
        stand = QLabel(); stand.setWordWrap(True)
        setzen = knopf("standard", _t("optionen.befehle.kennwort_setzen")); weg = knopf("standard", _t("optionen.befehle.kennwort_entfernen"))
        zeile = QWidget(); h = _reihe("standard", zeile)
        h.addWidget(setzen); h.addWidget(weg); h.addStretch(1)
        f.addRow(zeile)
        f.addRow(stand)

        def zeige(meldung: str = ""):
            if not t:
                stand.setText(_t("optionen.befehle.kein_dokument_geoeffnet_das_kennwort_geh"))
            elif meldung:
                stand.setText(meldung)
            else:
                stand.setText(_t("optionen.befehle.das_dokument_wird_beim_speichern_verschl") if t.meta.get("kennwort")
                              else _t("optionen.befehle.ohne_kennwort_die_datei_ist_im_klartext"))
        for c in (k1, k2, setzen, weg):
            c.setEnabled(t is not None)

        def setze():
            if not k1.text():
                zeige(_t("optionen.befehle.bitte_ein_kennwort_eingeben")); return
            if k1.text() != k2.text():
                zeige(_t("optionen.befehle.die_beiden_eingaben_stimmen_nicht_uebere")); return
            t.meta["kennwort"] = k1.text()
            t.editor.document().setModified(True)
            k1.clear(); k2.clear()
            zeige(_t("optionen.befehle.gesetzt_das_dokument_wird_ab_dem_naechst"))
        setzen.clicked.connect(setze)
        weg.clicked.connect(lambda: (t.meta.pop("kennwort", None), t.editor.document().setModified(True), k1.clear(), k2.clear(),
                                     zeige(_t("optionen.befehle.entfernt_gilt_ab_dem_naechsten_speichern"))))
        zeige()
        warn = md_label(_t("optionen.befehle.ein_vergessenes_kennwort_kann_niemand_wi"))
        warn.setWordWrap(True); _rolle(warn, "text")
        f.addRow(warn)
        sperre = haken_baustein("standard", _t("optionen.befehle.bearbeitung_sperren"))
        sperre.setChecked(bool(t and getattr(t, "gesperrt", False))); sperre.setEnabled(t is not None)
        sperre.toggled.connect(lambda on: t and on != bool(getattr(t, "gesperrt", False)) and self.w.toggle_sperre())
        f.addRow(sperre)
        f = p.gruppe(_t("optionen.befehle.datenschutz"))
        p.haken(f, "sicherheit/markup_oeffnen", _t("optionen.befehle.ausgeblendete_markups_beim_oeffnen_anzei"), True)
        p.haken(f, "sicherheit/personendaten_weg", _t("optionen.befehle.beim_speichern_persoenliche_daten_entfer"), False)
        p.abschluss()
        return p


    def _verfolgen(self, titel):
        p = _Seite(self.w, titel)
        f = p.gruppe(_t("optionen.befehle.aenderungen_verfolgen"))
        b = UmbruchSchalter(_t("optionen.befehle.aenderungen_im_aktuellen_dokument_verfol"))
        e = self.w.current_editor()
        b.setChecked(bool(e and e.verfolgen)); b.setEnabled(e is not None)
        b.toggled.connect(lambda on: self.w.current_editor() and self.w.current_editor().set_verfolgen(on))
        f.addRow(b)
        m = UmbruchSchalter(_t("optionen.befehle.markup_anzeigen_kommentare_einfuegungen"))
        m.setChecked(bool(e.markup) if e else True); m.setEnabled(e is not None)
        m.toggled.connect(lambda on: self.w.current_editor() and self.w.current_editor().set_markup(on))
        f.addRow(m)
        from writer.funktionen.ansicht import sprechblasen as SB
        kat = SB.katalog()
        from vcl.qt.widgets.bausteine.farben.farben import FESTE_FARBEN
        from vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor import DEL_STILE, INS_STILE
        neu = lambda _=None: self.w.markup_neu()                                               # noqa: E731
        f = p.gruppe(_t("optionen.befehle.markup"))
        p.auswahl(f, "aenderungen/ins_stil", _t("optionen.befehle.einfuegungen"), INS_STILE, _t("optionen.befehle.unterstrichen"), neu)
        p.auswahl(f, "aenderungen/del_stil", _t("optionen.befehle.loeschvorgaenge"), DEL_STILE, _t("optionen.befehle.durchgestrichen"), neu)
        p.auswahl(f, "aenderungen/balken", _t("optionen.befehle.geaenderte_zeilen_balken_im_rand"), ["links", "rechts", "außen", "keine"], "links", neu)
        p.auswahl(f, "aenderungen/farbe", _t("optionen.befehle.farbe"), [_t("optionen.befehle.nach_autor")] + list(FESTE_FARBEN), _t("optionen.befehle.nach_autor"), neu)
        f = p.gruppe(_t("optionen.befehle.sprechblasen"))
        p.auswahl(f, "sprechblasen/verwenden", _t("optionen.befehle.sprechblasen_verwenden"), kat.verwenden, kat.standard.verwenden, neu)
        p.haken(f, "sprechblasen/empfohlen", _t("optionen.befehle.empfohlene_breite_verwenden_60_mm"), True, neu)
        p.zahl(f, "sprechblasen/breite_mm", _t("optionen.befehle.bevorzugte_breite"), 30, 120, 60, _t("optionen.befehle.mm"), 1, neu)
        p.auswahl(f, "sprechblasen/rand", _t("optionen.befehle.seitenrand"), kat.rand,_t("optionen.befehle.rechts"), neu)
        p.haken(f, "sprechblasen/linien", _t("optionen.befehle.verbindungslinien_zum_text_anzeigen"), True, neu)
        f = p.gruppe(_t("optionen.befehle.drucken_mit_sprechblasen"))
        p.haken(f, "sprechblasen/drucken", _t("optionen.befehle.sprechblasen_mitdrucken_und_exportieren"), False)
        p.auswahl(f, "sprechblasen/ausrichtung", _t("optionen.befehle.papierausrichtung"), kat.ausrichtung,_t("optionen.befehle.automatisch"))
        p.hinweis(_t("optionen.befehle.einfuegungen_und_loeschungen_stehen_in_e"))
        p.abschluss()
        return p
