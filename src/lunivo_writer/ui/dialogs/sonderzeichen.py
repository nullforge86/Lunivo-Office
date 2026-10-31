"""Das Fenster „Symbol“ (Einfügen › Symbol › Weitere Symbole …) in der Seitenleiste, nach der Vorlage mit drei Reitern:

    Symbole                    Schriftart, Zeichenraster, „Zuletzt verwendete Symbole“, Zeichencode und „Von“ (Dezimal oder Hex)
    Sonderzeichen              Liste „Zeichen:“ mit Zeichen und Name
    Benutzerdefinierte Symbole Liste der Klappe: Haken, Tastenkombination, Nach oben/unten, Entfernen, Zurücksetzen

    d = SonderzeichenDialog(parent, einfuegen, SymbolDaten(settings, standard, anzahl))
    d.exec()                                   # „Einfügen“ ruft ``einfuegen(zeichen)`` und schließt das Fenster nicht

``SymbolDaten`` ist die eine Datenbasis für dieses Fenster und die Klappe „Symbol“ (``core/befehle/einfuegen.py``): zuletzt verwendete
Symbole, die benutzerdefinierte Liste (mit Haken) und deren Tastenkombinationen, alles als JSON ohne Markup in den Einstellungen.
Das Fenster fügt selbst nichts ein; der Aufrufer bekommt das Zeichen.
"""
from __future__ import annotations

import json
from typing import Callable

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QFontMetrics, QKeySequence, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDialog, QFrame, QHeaderView, QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import AngepassteReiter, FlussLayout, FormularGitter, abschnittstitel
from lunivo_writer.ui.baukasten.tasten_dialog import TastenDialog
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

KEY_ZULETZT = "einfuegen/symbole_zuletzt"
KEY_BENUTZER = "einfuegen/symbole_benutzer"
KEY_TASTEN = "einfuegen/symbole_tasten"

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
ZELLE = 30


class SymbolDaten:
    """Zuletzt verwendet, benutzerdefinierte Symbole (Zeichen, Haken) und Tastenkombinationen — in den Einstellungen (``get``/``set``)."""

    def __init__(self, einstellungen=None, standard: tuple = (), anzahl: int = 24):
        self.e = einstellungen if einstellungen is not None else _Speicher()
        self.standard, self.anzahl = tuple(standard), anzahl

    def _lesen(self, key: str, leer):
        try:
            wert = json.loads(str(self.e.get(key, "") or ""))
        except ValueError:
            return leer
        return wert if isinstance(wert, type(leer)) else leer

    def zuletzt(self) -> list[str]:
        return [z for z in self._lesen(KEY_ZULETZT, []) if isinstance(z, str) and z]

    def merken(self, z: str) -> None:
        liste = [z] + [x for x in self.zuletzt() if x != z]
        self.e.set(KEY_ZULETZT, json.dumps(liste[:self.anzahl], ensure_ascii=False))

    def benutzer(self) -> list[tuple[str, bool]]:
        """Die Liste „Benutzerdefinierte Symbole“ in ihrer Reihenfolge, je Zeichen mit Haken (``True``: in der Klappe zu sehen)."""
        if not str(self.e.get(KEY_BENUTZER, "") or ""):
            return [(z, True) for z in self.standard]
        return [(p[0], bool(p[1])) for p in self._lesen(KEY_BENUTZER, []) if isinstance(p, list) and len(p) == 2 and isinstance(p[0], str) and p[0]]

    def setze_benutzer(self, liste: list[tuple[str, bool]]) -> None:
        self.e.set(KEY_BENUTZER, json.dumps([[z, an] for z, an in liste], ensure_ascii=False) if liste else "[]")

    def sichtbar(self) -> list[str]:
        return [z for z, an in self.benutzer() if an]

    def zuruecksetzen(self) -> None:
        self.e.set(KEY_BENUTZER, ""); self.e.set(KEY_TASTEN, "")

    def tasten(self) -> dict[str, str]:
        return {z: t for z, t in self._lesen(KEY_TASTEN, {}).items() if isinstance(z, str) and isinstance(t, str) and t}

    def setze_tasten(self, tasten: dict[str, str]) -> None:
        self.e.set(KEY_TASTEN, json.dumps({z: t for z, t in tasten.items() if t}, ensure_ascii=False))


class _Speicher:
    def __init__(self):
        self.d: dict = {}

    def get(self, key, default=None):
        return self.d.get(key, default)

    def set(self, key, wert) -> None:
        self.d[key] = wert


class Zeichenraster(QWidget):
    """Zeichen in Zellen, die sich der Breite anpassen: Spaltenzahl = Breite / Zelle, Höhe folgt der Zahl der Zeilen (``heightForWidth``)."""
    gewaehlt = Signal(int)
    gewaehlt_doppelt = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zeichen: list[int] = []
        self._schrift = QFont(QApplication.font())
        self._aktuell = -1
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

    def setze(self, zeichen: list[int], schrift: QFont | None = None) -> None:
        self._zeichen = list(zeichen)
        if schrift is not None:
            self._schrift = QFont(schrift); self._schrift.setPixelSize(17)
        self._aktuell = -1
        self.updateGeometry(); self.update()

    def zeichen(self) -> list[int]:
        return self._zeichen

    def waehle(self, code: int | None) -> None:
        self._aktuell = self._zeichen.index(code) if code in self._zeichen else -1
        self.update()

    def spalten(self) -> int:
        return max(1, self.width() // ZELLE)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, breite: int) -> int:
        sp = max(1, breite // ZELLE)
        return max(1, -(-len(self._zeichen) // sp)) * ZELLE + 1

    def sizeHint(self) -> QSize:
        return QSize(ZELLE * 8 + 1, self.heightForWidth(ZELLE * 8))

    def minimumSizeHint(self) -> QSize:
        return QSize(ZELLE, ZELLE + 1)

    def zelle_von(self, i: int) -> QRect:
        sp = self.spalten()
        return QRect((i % sp) * ZELLE, (i // sp) * ZELLE, ZELLE, ZELLE)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        pal = self.palette()
        p.fillRect(self.rect(), pal.base())
        p.setFont(self._schrift)
        for i, cp in enumerate(self._zeichen):
            r = self.zelle_von(i)
            if i == self._aktuell:
                p.fillRect(r, pal.highlight() if self.hasFocus() else pal.midlight())
            p.setPen(QPen(pal.mid().color(), 1)); p.drawRect(r.adjusted(0, 0, -1, -1))
            p.setPen(pal.highlightedText().color() if i == self._aktuell and self.hasFocus() else pal.text().color())
            p.drawText(r, Qt.AlignCenter, chr(cp))
        p.end()

    def _index_bei(self, pos) -> int:
        i = (pos.y() // ZELLE) * self.spalten() + pos.x() // ZELLE
        return i if 0 <= i < len(self._zeichen) and pos.x() < self.spalten() * ZELLE else -1

    def mousePressEvent(self, ev) -> None:
        i = self._index_bei(ev.position().toPoint())
        if i >= 0:
            self._setze_index(i)
        self.setFocus(Qt.MouseFocusReason)

    def mouseDoubleClickEvent(self, ev) -> None:
        i = self._index_bei(ev.position().toPoint())
        if i >= 0:
            self.gewaehlt_doppelt.emit(self._zeichen[i])

    def _setze_index(self, i: int) -> None:
        self._aktuell = i
        self.update()
        self.gewaehlt.emit(self._zeichen[i])

    def keyPressEvent(self, ev) -> None:
        sp = self.spalten()
        schritt = {Qt.Key_Left: -1, Qt.Key_Right: 1, Qt.Key_Up: -sp, Qt.Key_Down: sp}.get(ev.key())
        if schritt is None or not self._zeichen:
            return super().keyPressEvent(ev)
        i = min(len(self._zeichen) - 1, max(0, (self._aktuell if self._aktuell >= 0 else 0) + (schritt if self._aktuell >= 0 else 0)))
        self._setze_index(i)

    def focusInEvent(self, ev) -> None:
        super().focusInEvent(ev); self.update()

    def focusOutEvent(self, ev) -> None:
        super().focusOutEvent(ev); self.update()


class _TastenFenster(PanelFaehig, TastenDialog):
    """„Tastenkombination“ als Seite über dem Fenster „Symbol“."""


class SonderzeichenDialog(PanelFaehig, QDialog):
    def __init__(self, parent, einfuegen: Callable[[str], None], daten: SymbolDaten | None = None, *, bei_tasten: Callable | None = None):
        super().__init__(parent)
        self.setWindowTitle("Symbol")
        self.resize(444, 560)
        self.einfuegen = einfuegen
        self.daten = daten or SymbolDaten()
        self._bei_tasten = bei_tasten
        self._code: int | None = None
        self._sprung = False
        self._cache: dict[str, list[int]] = {}
        v = QVBoxLayout(self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        self.reiter.tabBar().setElideMode(Qt.ElideNone); self.reiter.tabBar().setUsesScrollButtons(True)      # Namen bleiben ganz, bei Enge rollt die Leiste
        self.reiter.addTab(self._symbole(), "Symbole")
        self.reiter.addTab(self._sonderzeichen(), "Sonderzeichen")
        self.reiter.addTab(self._benutzer(), "Benutzerdefinierte Symbole")
        self.bei_benutzer = QPushButton("Einfügen bei benutzerdefinierten Symbolen")
        self.bei_benutzer.clicked.connect(self._zu_benutzer)
        self.ok = fussleiste(self, v, self.bei_benutzer, bei_ok=self._einfuegen, ok_text="Einfügen", abbrechen_text="Abbrechen")
        from lunivo_writer.ui.baukasten.dialog_rahmen import Knopfzeile
        self.abbrechen = self.findChild(Knopfzeile).abbrechen
        self.reiter.currentChanged.connect(self._reiter)
        self._schrift_neu()
        self._benutzer_fuellen()
        self._reiter(0)

    # ---- Reiter „Symbole“
    def _symbole(self) -> QWidget:
        s = QWidget(); g = FormularGitter(s)
        self.schrift = QComboBox(); self.schrift.addItem(NORMAL)
        self.schrift.addItems(QFontDatabase.families())
        self.schrift.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon); self.schrift.setMinimumContentsLength(8)
        self.schrift.currentIndexChanged.connect(self._schrift_neu)
        g.zeile("&Schriftart:", self.schrift)
        self.raster = Zeichenraster()
        self.rollen = QScrollArea(); self.rollen.setWidgetResizable(True); self.rollen.setWidget(self.raster)
        self.rollen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.rollen.setFixedHeight(ZELLE * 5 + 2)
        self.rollen.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed); self.rollen.setMinimumWidth(0)
        self.raster.gewaehlt.connect(self._gewaehlt); self.raster.gewaehlt_doppelt.connect(lambda cp: (self._gewaehlt(cp), self._einfuegen()))
        g.breit(self.rollen)
        g.breit(abschnittstitel("Zuletzt verwendete Symbole"))
        self.zuletzt = Zeichenraster()
        self.zuletzt.setze([ord(z) for z in self.daten.zuletzt() if len(z) == 1], QApplication.font())
        self.zuletzt.gewaehlt.connect(self._gewaehlt); self.zuletzt.gewaehlt_doppelt.connect(lambda cp: (self._gewaehlt(cp), self._einfuegen()))
        g.breit(self.zuletzt)
        self.zeichencode = QLineEdit(); self.zeichencode.setMaximumWidth(120)
        self.zeichencode.textEdited.connect(self._code_getippt)
        self.von = QComboBox()
        for name, basis in VON:
            self.von.addItem(name, basis)
        self.von.currentIndexChanged.connect(lambda *_: self._code_zeigen())
        g.reihe(("Zeichencode:", self.zeichencode), ("Von:", self.von), gewichte=(1, 2))
        return s

    def _schrift_neu(self, *_) -> None:
        name = self.schrift.currentText()
        if name not in self._cache:
            f = QFont(QApplication.font()) if name == NORMAL else QFont(name)
            f.setPixelSize(17)
            fm = QFontMetrics(f)
            self._cache[name] = [cp for cp in range(32, 0x10000) if not 0x7F <= cp <= 0x9F and not 0xD800 <= cp <= 0xDFFF and fm.inFontUcs4(cp)]
        f = QFont(QApplication.font()) if name == NORMAL else QFont(name)
        for r in (self.raster, self.zuletzt):
            r._schrift = QFont(f); r._schrift.setPixelSize(17)
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
        self.sonder.setFixedHeight(12 * 27 + 4); self.sonder.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.sonder.header().setSectionResizeMode(0, QHeaderView.Fixed); self.sonder.setColumnWidth(0, 56)
        self.sonder.header().setStretchLastSection(True)
        for anzeige, name, zeichen in SONDERZEICHEN:
            it = QTreeWidgetItem([anzeige, name]); it.setData(0, Qt.UserRole, zeichen)
            it.setTextAlignment(0, Qt.AlignCenter); it.setSizeHint(0, QSize(10, 27)); it.setToolTip(1, name)
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
        self.liste.setFixedHeight(8 * 27 + 24); self.liste.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        kopf = self.liste.header(); kopf.setStretchLastSection(True); kopf.setSectionResizeMode(0, QHeaderView.Fixed)
        kopf.setTextElideMode(Qt.ElideRight)
        self.liste.itemChanged.connect(self._haken); self.liste.currentItemChanged.connect(lambda *_: self._liste_knoepfe())
        g.breit(self.liste)
        g.breit(abschnittstitel("Tastenkombinationen"))
        self.taste = QLineEdit("Keine"); self.taste.setReadOnly(True)
        self.taste_setzen = QPushButton("Tastenkombinationen &festlegen"); self.taste_setzen.clicked.connect(self._taste_festlegen)
        g.breit(self.taste); g.breit(self.taste_setzen)
        self.runter, self.hoch = QPushButton("Nach &unten"), QPushButton("Nach o&ben")
        self.entfernen, self.zurueck = QPushButton("&Entfernen"), QPushButton("Symbolleiste &zurücksetzen")
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
            it.setData(0, Qt.UserRole, z); it.setSizeHint(0, QSize(10, 27))
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
