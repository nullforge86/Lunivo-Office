"""Sonderzeichen dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.sonderzeichen`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from core.formatierung.schrift import standard_datenbank
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from typing import Callable
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QFontMetrics, QKeySequence
from PySide6.QtWidgets import QAbstractItemView, QApplication, QDialog, QHeaderView, QLabel, QScrollArea, QSizePolicy, QTreeWidget, QTreeWidgetItem, QWidget
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.angepasste_reiter import AngepassteReiter
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_SONDERZEICHEN_PX, SONDERZEICHEN_KOPF_ZEILEN, SONDERZEICHEN_SONDER_ZEILEN, SONDERZEICHEN_ZELLEN_REIHEN
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_FELD_ZEICHENCODE, BREITE_ZEILENHINWEIS, GROESSE_FENSTER_SONDERZEICHEN, HOEHE_ZEILE_SONDER, ZUGABE_LISTE_KOPF, ZUGABE_LISTE_SONDER, ZUGABE_RAHMEN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_ZEICHEN_MITTEL
from vcl.qt.widgets.dialoge.einfuegen.sonderzeichen_hilfen import SymbolDaten, ZELLE, _TastenFenster
from vcl.qt.widgets.dialoge.einfuegen.zeichenraster import Zeichenraster


# Zeichen und Name wie in der Vorlage (die Bildlaufleiste dort zeigt genau einen Eintrag mehr: das schließende einfache Anführungszeichen); ein Leerzeichen-Zeichen steht dort ohne Bild (leer), das geschützte Leerzeichen als „°“.
SONDERZEICHEN = (
    ("—", "Geviertstrich", "—"), ("–", "Halbgeviertstrich", "–"), ("", "Geviertabstand", " "),
    ("", "Halbgeviertabstand", " "), ("°", "Geschützte Leerzeichen", " "), ("©", "Copyright", "©"),
    ("®", "Registriert", "®"), ("™", "Markenzeichen", "™"), ("§", "Abschnitt", "§"),
    ("¶", "Absatz", "¶"), ("…", "Ellipse", "…"), ("‘", "Einfaches Anführungszeichen", "‘"),
    ("’", "Einfaches Anführungszeichen, rechts", "’"),
)


VON = (("Symbol(DEC)", 10), ("Unicode(HEX)", 16))


NORMAL = "(Normaler Text)"


class SonderzeichenDialog(PanelFaehig, QDialog):
    def __init__(self, parent, einfuegen: Callable[[str], None], daten: SymbolDaten | None = None, *, bei_tasten: Callable | None = None):
        super().__init__(parent)
        self.setWindowTitle("Symbol")
        self.resize(*GROESSE_FENSTER_SONDERZEICHEN)
        self.einfuegen = einfuegen
        self.daten = daten or SymbolDaten()
        self._bei_tasten = bei_tasten
        self._code: int | None = None
        self._sprung = False
        self._cache: dict[str, list[int]] = {}
        v = _spalte("standard", self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        self.reiter.addTab(self._symbole(), "Symbole")
        self.reiter.addTab(self._sonderzeichen(), "Sonderzeichen")
        self.reiter.addTab(self._benutzer(), "Benutzerdefinierte Symbole")
        self.bei_benutzer = knopf("standard", "Einfügen bei benutzerdefinierten Symbolen")
        self.bei_benutzer.clicked.connect(self._zu_benutzer)
        self.ok = fussleiste(self, v, self.bei_benutzer, bei_ok=self._einfuegen, ok_text="Einfügen", abbrechen_text="Abbrechen")
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import Knopfzeile
        self.abbrechen = self.findChild(Knopfzeile).abbrechen
        self.reiter.currentChanged.connect(self._reiter)
        self._schrift_neu()
        self._benutzer_fuellen()
        self._reiter(0)

    # ---- Reiter „Symbole“
    def _symbole(self) -> QWidget:
        s = QWidget(); g = FormularGitter(s)
        self.schrift = Auswahlfeld(); self.schrift.addItem(NORMAL)
        self.schrift.addItems(standard_datenbank.familien())
        self.schrift.zeichen(DROPDOWN_ZEICHEN_MITTEL)
        self.schrift.currentIndexChanged.connect(self._schrift_neu)
        g.zeile("&Schriftart:", self.schrift)
        self.raster = Zeichenraster()
        self.rollen = QScrollArea(); self.rollen.setWidgetResizable(True); self.rollen.setWidget(self.raster)
        self.rollen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.rollen.setFixedHeight(ZELLE * SONDERZEICHEN_ZELLEN_REIHEN + ZUGABE_RAHMEN)
        self.rollen.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed); self.rollen.setMinimumWidth(0)
        self.raster.gewaehlt.connect(self._gewaehlt); self.raster.gewaehlt_doppelt.connect(lambda cp: (self._gewaehlt(cp), self._einfuegen()))
        g.breit(self.rollen)
        g.breit(abschnittstitel("Zuletzt verwendete Symbole"))
        self.zuletzt = Zeichenraster()
        self.zuletzt.setze([ord(z) for z in self.daten.zuletzt() if len(z) == 1], QApplication.font())
        self.zuletzt.gewaehlt.connect(self._gewaehlt); self.zuletzt.gewaehlt_doppelt.connect(lambda cp: (self._gewaehlt(cp), self._einfuegen()))
        g.breit(self.zuletzt)
        self.zeichencode = zeilenfeld("frei"); self.zeichencode.setMaximumWidth(BREITE_FELD_ZEICHENCODE)
        self.zeichencode.textEdited.connect(self._code_getippt)
        self.von = Auswahlfeld()
        for name, basis in VON:
            self.von.addItem(name, basis)
        self.von.currentIndexChanged.connect(lambda *_: self._code_zeigen())
        g.reihe(("Zeichencode:", self.zeichencode), ("Von:", self.von), gewichte=(1, 2))
        return s

    def _schrift_neu(self, *_) -> None:
        name = self.schrift.currentText()
        if name not in self._cache:
            f = QFont(QApplication.font()) if name == NORMAL else QFont(name)
            f.setPixelSize(SCHRIFT_SONDERZEICHEN_PX)
            fm = QFontMetrics(f)
            self._cache[name] = [cp for cp in range(32, 0x10000) if not 0x7F <= cp <= 0x9F and not 0xD800 <= cp <= 0xDFFF and fm.inFontUcs4(cp)]
        f = QFont(QApplication.font()) if name == NORMAL else QFont(name)
        for r in (self.raster, self.zuletzt):
            r._schrift = QFont(f); r._schrift.setPixelSize(SCHRIFT_SONDERZEICHEN_PX)
        self.raster.setze(self._cache[name], f)
        if self._code is None and self.raster.zeichen():
            self._code = self.raster.zeichen()[0]
        self.raster.waehle(self._code)
        self._code_zeigen()

    def _gewaehlt(self, cp: int) -> None:
        self._code = cp
        self.raster.waehle(cp)
        self._code_zeigen()
        self._knoepfe()
        i = self.raster.zeichen().index(cp) if cp in self.raster.zeichen() else -1
        if i >= 0:
            r = self.raster.zelle_von(i)
            self.rollen.ensureVisible(r.center().x(), r.center().y(), 0, ZELLE)

    def _code_zeigen(self) -> None:
        basis = self.von.currentData() or 10
        self.zeichencode.setText("" if self._code is None else (f"{self._code:X}" if basis == 16 else str(self._code)))

    def _code_getippt(self, text: str) -> None:
        try:
            cp = int(text.strip(), self.von.currentData() or 10)
        except ValueError:
            return
        if 0 < cp < 0x110000 and not 0xD800 <= cp <= 0xDFFF:
            self._code = cp
            self.raster.waehle(cp)
            self._knoepfe()
            i = self.raster.zeichen().index(cp) if cp in self.raster.zeichen() else -1
            if i >= 0:
                r = self.raster.zelle_von(i)
                self.rollen.ensureVisible(r.center().x(), r.center().y(), 0, ZELLE)

    # ---- Reiter „Sonderzeichen“
    def _sonderzeichen(self) -> QWidget:
        s = QWidget(); g = FormularGitter(s)
        self.sonder = QTreeWidget(); self.sonder.setColumnCount(2); self.sonder.setHeaderHidden(True); self.sonder.setRootIsDecorated(False)
        self.sonder.setUniformRowHeights(True); self.sonder.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sonder.setFixedHeight(SONDERZEICHEN_SONDER_ZEILEN * HOEHE_ZEILE_SONDER + ZUGABE_LISTE_SONDER); self.sonder.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.sonder.header().setSectionResizeMode(0, QHeaderView.Fixed); self.sonder.setColumnWidth(0, 56)
        self.sonder.header().setStretchLastSection(True)
        for anzeige, name, zeichen in SONDERZEICHEN:
            it = QTreeWidgetItem([anzeige, name]); it.setData(0, Qt.UserRole, zeichen)
            it.setTextAlignment(0, Qt.AlignCenter); it.setSizeHint(0, QSize(BREITE_ZEILENHINWEIS, HOEHE_ZEILE_SONDER)); it.setToolTip(1, name)
            self.sonder.addTopLevelItem(it)
        self.sonder.setCurrentItem(self.sonder.topLevelItem(0))
        self.sonder.currentItemChanged.connect(lambda *_: self._knoepfe())
        self.sonder.itemDoubleClicked.connect(lambda *_: self._einfuegen())
        self.sonder_titel = QLabel("&Zeichen:"); self.sonder_titel.setBuddy(self.sonder)
        g.breit(self.sonder_titel); g.breit(self.sonder)
        return s

    # ---- Reiter „Benutzerdefinierte Symbole“
    def _benutzer(self) -> QWidget:
        s = QWidget(); g = FormularGitter(s)
        self.liste = QTreeWidget(); self.liste.setColumnCount(2); self.liste.setRootIsDecorated(False); self.liste.setUniformRowHeights(True)
        self.liste.setHeaderLabels(["Benutzerdefinierte Symbole:", "Tastenkombinationen:"]); self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.liste.setSelectionMode(QAbstractItemView.SingleSelection)
        self.liste.setFixedHeight(SONDERZEICHEN_KOPF_ZEILEN * HOEHE_ZEILE_SONDER + ZUGABE_LISTE_KOPF); self.liste.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        kopf = self.liste.header(); kopf.setStretchLastSection(True); kopf.setSectionResizeMode(0, QHeaderView.Fixed)
        kopf.setTextElideMode(Qt.ElideRight)
        self.liste.itemChanged.connect(self._haken); self.liste.currentItemChanged.connect(lambda *_: self._liste_knoepfe())
        g.breit(self.liste)
        g.breit(abschnittstitel("Tastenkombinationen"))
        self.taste = zeilenfeld("frei", "Keine", nur_lesen=True)
        self.taste_setzen = knopf("standard", "Tastenkombinationen &festlegen", aktion=self._taste_festlegen)
        g.breit(self.taste); g.breit(self.taste_setzen)
        self.runter, self.hoch = knopf("standard", "Nach &unten"), knopf("standard", "Nach o&ben")
        self.entfernen, self.zurueck = knopf("standard", "&Entfernen"), knopf("standard", "Symbolleiste &zurücksetzen")
        self.runter.clicked.connect(lambda: self._verschieben(1)); self.hoch.clicked.connect(lambda: self._verschieben(-1))
        self.entfernen.clicked.connect(self._entfernen); self.zurueck.clicked.connect(self._zuruecksetzen)
        for paar in ((self.runter, self.hoch), (self.entfernen, self.zurueck)):
            f = FlussLayout(6)
            for k in paar:
                f.addWidget(k)
            g.breit(f)
        return s

    def _breiten(self) -> None:
        self.liste.setColumnWidth(0, max(60, int(self.liste.viewport().width() * 0.45)))

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._breiten()

    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        self._breiten()

    def _benutzer_fuellen(self, wahl: int | None = None) -> None:
        tasten = self.daten.tasten()
        self.liste.blockSignals(True)
        self.liste.clear()
        for z, an in self.daten.benutzer():
            it = QTreeWidgetItem([z, tasten.get(z, "")])
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable); it.setCheckState(0, Qt.Checked if an else Qt.Unchecked)
            it.setData(0, Qt.UserRole, z); it.setSizeHint(0, QSize(BREITE_ZEILENHINWEIS, HOEHE_ZEILE_SONDER))
            self.liste.addTopLevelItem(it)
        self.liste.blockSignals(False)
        n = self.liste.topLevelItemCount()
        if n:
            self.liste.setCurrentItem(self.liste.topLevelItem(min(n - 1, wahl if wahl is not None else 0)))
        self._liste_knoepfe()

    def _liste_aus_widget(self) -> list[tuple[str, bool]]:
        return [(it.data(0, Qt.UserRole), it.checkState(0) == Qt.Checked)
                for it in (self.liste.topLevelItem(i) for i in range(self.liste.topLevelItemCount()))]

    def _liste_knoepfe(self) -> None:
        i = self.liste.indexOfTopLevelItem(self.liste.currentItem()) if self.liste.currentItem() else -1
        n = self.liste.topLevelItemCount()
        self.hoch.setEnabled(i > 0); self.runter.setEnabled(0 <= i < n - 1)
        self.entfernen.setEnabled(i >= 0); self.taste_setzen.setEnabled(i >= 0)
        z = self.liste.currentItem().data(0, Qt.UserRole) if i >= 0 else None
        self.taste.setText(self.daten.tasten().get(z, "") or "Keine")
        self._knoepfe()

    def _haken(self, *_) -> None:
        self.daten.setze_benutzer(self._liste_aus_widget())

    def _verschieben(self, schritt: int) -> None:
        i = self.liste.indexOfTopLevelItem(self.liste.currentItem())
        liste = self._liste_aus_widget()
        j = i + schritt
        if i < 0 or not 0 <= j < len(liste):
            return
        liste[i], liste[j] = liste[j], liste[i]
        self.daten.setze_benutzer(liste)
        self._benutzer_fuellen(j)

    def _entfernen(self) -> None:
        i = self.liste.indexOfTopLevelItem(self.liste.currentItem())
        liste = self._liste_aus_widget()
        if i < 0:
            return
        z = liste.pop(i)[0]
        self.daten.setze_benutzer(liste)
        tasten = self.daten.tasten(); tasten.pop(z, None); self.daten.setze_tasten(tasten)
        self._benutzer_fuellen(i if i < len(liste) else len(liste) - 1)
        self._tasten_melden()

    def _zuruecksetzen(self) -> None:
        self.daten.zuruecksetzen()
        self._benutzer_fuellen()
        self._tasten_melden()

    def _taste_festlegen(self) -> None:
        it = self.liste.currentItem()
        if it is None:
            return
        z = it.data(0, Qt.UserRole)
        tasten = self.daten.tasten()

        def belegt(t: str):
            return next((f"„{a}“" for a, b in tasten.items() if a != z and QKeySequence(b) == QKeySequence(t)), None)
        d = _TastenFenster(self, tasten.get(z, ""), belegt=belegt)
        d.setWindowTitle(f"Tastenkombination für „{z}“")
        if d.exec():
            tasten[z] = d.taste()
            self.daten.setze_tasten(tasten)
            self._benutzer_fuellen(self.liste.indexOfTopLevelItem(it))
            self._tasten_melden()

    def _tasten_melden(self) -> None:
        if self._bei_tasten:
            self._bei_tasten()

    # ---- Knöpfe unten
    def zeichen_jetzt(self) -> str:
        """Das Zeichen, das „Einfügen“ gerade einfügt: je nach Reiter aus Raster, Sonderzeichen oder benutzerdefinierter Liste."""
        r = self.reiter.currentIndex()
        if r == 0:
            return chr(self._code) if self._code else ""
        it = self.sonder.currentItem() if r == 1 else self.liste.currentItem()
        return (it.data(0, Qt.UserRole) or "") if it is not None else ""

    def _reiter(self, i: int) -> None:
        self.abbrechen.setText("Schließen" if i == 2 else "Abbrechen")
        self._knoepfe()

    def _knoepfe(self) -> None:
        i = self.reiter.currentIndex()
        self.bei_benutzer.setEnabled(i != 2 and bool(self.zeichen_jetzt()))
        self.ok.setEnabled(bool(self.zeichen_jetzt()))

    def _einfuegen(self) -> None:
        z = self.zeichen_jetzt()
        if not z:
            return
        self.einfuegen(z)
        self.daten.merken(z)
        self.zuletzt.setze([ord(c) for c in self.daten.zuletzt() if len(c) == 1])

    def _zu_benutzer(self) -> None:
        z = self.zeichen_jetzt()
        liste = self.daten.benutzer()
        if z and z not in [a for a, _ in liste]:
            self.daten.setze_benutzer(liste + [(z, True)])
            self._benutzer_fuellen(self.liste.currentIndex().row() if self.liste.currentItem() else None)
