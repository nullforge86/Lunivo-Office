"""Das eine Speichern-Fenster: Orte links, Ordnerinhalt rechts, unten Dateiname und Dateityp.

Aufbau nach dem Vorbild, das der Eigentümer vorgegeben hat (Bildschirmfoto „Speichern unter“): Titel und Orte (Persönlicher
Ordner, Schreibtisch, Dokumente, Andere Orte) links; oben Zurück, Vor, Hoch, Pfadleiste aus Knöpfen, Neuer Ordner, Liste/Kacheln;
in der Mitte die Dateien des Ordners (Name, Geändert, Typ, Größe), gefiltert nach dem gewählten Dateityp; unten „Dateiname“ mit
„Speichern“ und „Dateityp“ mit „Abbrechen“. Lunivos eigenes Fenster, nicht das des Desktops — so ist der Dateityp immer sichtbar.

Der Baustein liefert nur den Pfad und die Endung (``speicherort_waehlen``); was gespeichert wird, entscheidet der Aufrufer.
"""
from __future__ import annotations

import os
import re

from PySide6.QtCore import QDir, QFileInfo, QModelIndex, QSize, QStandardPaths, QStorageInfo, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDialog, QFileIconProvider, QFileSystemModel, QFrame, QGridLayout,
                               QHBoxLayout, QHeaderView,
                               QLabel, QLineEdit, QListView, QListWidget, QListWidgetItem, QMessageBox, QPushButton,
                               QStackedWidget, QToolButton, QTreeView, QVBoxLayout, QWidget)

from lunivo_writer.core.farben import Farbe

STIL = """
QWidget#sfLinks { background: palette(window); border-right: 1px solid palette(midlight); }
QLabel#sfTitel { font-size: 17pt; font-weight: 600; padding: 4px 6px 14px 6px; }
QListWidget#sfOrte { background: transparent; border: none; outline: none; }
QListWidget#sfOrte { font-size: 11pt; }
QListWidget#sfOrte::item { padding-left: 10px; border-radius: 6px; }
QListWidget#sfOrte::item:selected { background: palette(midlight); color: palette(highlight); }
QListWidget#sfOrte::item:hover:!selected { background: palette(midlight); }
QFrame#sfPfad { border: 1px solid palette(mid); border-radius: 4px; }
QFrame#sfPfad QToolButton { border: none; padding: 2px 4px; }
QFrame#sfPfad QToolButton:hover { background: palette(midlight); border-radius: 3px; }
QPushButton#sfSpeichern { background: %(akzent)s; color: white; border: none; border-radius: 4px; padding: 6px 28px; font-weight: 600; }
QPushButton#sfSpeichern:hover { background: %(akzent_d)s; }
QTreeView#sfListe::item { padding: 4px 2px; }
QPushButton#sfSpeichern:disabled { background: palette(mid); }
""" % {"akzent": Farbe.AKZENT, "akzent_d": Farbe.AKZENT_DUNKEL}


# Liniensymbole im Stil der übrigen Lunivo-Symbole (Pfade nach Lucide, ISC-Lizenz, siehe assets/icons/LIZENZ-LUCIDE.txt):
# gleich stark, in der Schriftfarbe der Palette — auf hellem und dunklem Grund gut zu erkennen.
_PFADE = {
    "haus": "M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8 M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9"
            "a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
    "bildschirm": "M4 3h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z M8 21h8 M12 17v4",
    "dokumente": "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z M14 2v4a2 2 0 0 0 2 2h4 M10 9H8 M16 13H8 M16 17H8",
    "laufwerk": "M22 12H2 M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"
                " M6 16h.01 M10 16h.01",
    "mehr": "M12 12h.01 M19 12h.01 M5 12h.01 M12 2a10 10 0 1 0 0 20a10 10 0 1 0 0-20z",
    "links": "M12 19l-7-7 7-7 M19 12H5",
    "rechts": "M5 12h14 M12 5l7 7-7 7",
    "hoch": "M12 19V5 M5 12l7-7 7 7",
    "ordner_neu": "M12 10v6 M9 13h6 M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13"
                  "a2 2 0 0 0 2 2Z",
    "ordner": "M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z",
    "datei": "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z M14 2v4a2 2 0 0 0 2 2h4",
    "liste": "M8 6h13 M8 12h13 M8 18h13 M3 6h.01 M3 12h.01 M3 18h.01",
    "kacheln": "M4 3h5a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z M15 3h5a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1h-5a1 1 0 0 1-1-1V4"
               "a1 1 0 0 1 1-1z M15 14h5a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1h-5a1 1 0 0 1-1-1v-5a1 1 0 0 1 1-1z M4 14h5a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1"
               "H4a1 1 0 0 1-1-1v-5a1 1 0 0 1 1-1z",
}


def _symbol(name: str, px: int = 20) -> QIcon:
    from lunivo_writer.ui.widgets import icons
    return icons.icon_aus_pfad(_PFADE[name], px)


class _Symbole(QFileIconProvider):
    """Ordner und Dateien in der Liste mit denselben Liniensymbolen wie der Rest des Fensters."""

    def __init__(self):
        super().__init__()
        self._ordner, self._datei = _symbol("ordner", 18), _symbol("datei", 18)

    def icon(self, info):
        if isinstance(info, QFileInfo):
            return self._ordner if info.isDir() else self._datei
        return self._ordner


def _ordner(art) -> str:
    p = QStandardPaths.writableLocation(art)
    return p if p and os.path.isdir(p) else ""


class SpeichernFenster(QDialog):
    """``typen``: Liste (Endung, Filtertext) wie („.docx“, „Word-Dokument (*.docx)“). ``ergebnis()`` → (Pfad, Endung).
    Ohne ``typen`` wählt das Fenster einen Ordner (siehe ``ordner_waehlen``); mit ``oeffnen=True`` eine vorhandene Datei
    (siehe ``datei_waehlen``), dann sind ``typen`` Paare (Muster-Liste, Beschriftung)."""

    def __init__(self, parent, titel: str, startpfad: str, typen: list[tuple], vorwahl: str, oeffnen: bool = False,
                 mehrere: bool = False):
        super().__init__(parent)
        self.setWindowTitle(titel)
        self.setObjectName("speichernFenster")
        self.setStyleSheet(STIL)
        self.resize(1040, 660)
        self.typen = list(typen)
        self.nur_ordner = not self.typen
        self.oeffnen = oeffnen
        self._muster = [list(e) if oeffnen else [f"*{e}"] for e, _f in self.typen]
        self._dateien: list[str] = []
        self._zurueck: list[str] = []
        self._vor: list[str] = []
        self._ergebnis: tuple[str, str] | None = None

        ordner, name = os.path.split(startpfad)
        if not ordner or not os.path.isdir(ordner):
            ordner = _ordner(QStandardPaths.DocumentsLocation) or QDir.homePath()

        haupt = QHBoxLayout(self)
        haupt.setContentsMargins(0, 0, 0, 0)
        haupt.setSpacing(0)

        # ---- links: Titel und Orte -------------------------------------------------------------------------------------
        links = QWidget(); links.setObjectName("sfLinks"); links.setFixedWidth(250)
        lv = QVBoxLayout(links); lv.setContentsMargins(18, 22, 12, 12)
        t = QLabel(titel); t.setObjectName("sfTitel"); t.setWordWrap(True)
        lv.addWidget(t)
        self.orte = QListWidget(); self.orte.setObjectName("sfOrte"); self.orte.setIconSize(QSize(20, 20))
        self.orte.setSpacing(2)
        self.orte.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.orte.setTextElideMode(Qt.ElideMiddle)
        for text, pfad, ic in (("Persönlicher Ordner", QDir.homePath(), _symbol("haus")),
                               ("Schreibtisch", _ordner(QStandardPaths.DesktopLocation), _symbol("bildschirm")),
                               ("Dokumente", _ordner(QStandardPaths.DocumentsLocation), _symbol("dokumente"))):
            if pfad:
                self._ort(text, pfad, ic)
        for vol in QStorageInfo.mountedVolumes():                   # eingehängte Laufwerke (USB-Stick, zweite Platte)
            wurzel = vol.rootPath()
            if vol.isValid() and vol.isReady() and wurzel.startswith(("/media/", "/run/media/")):
                self._ort(os.path.basename(wurzel) or vol.displayName(), wurzel, _symbol("laufwerk"))
        self._ort("Andere Orte", "/", _symbol("mehr"))
        self.orte.itemClicked.connect(lambda it: self.gehe_zu(it.data(Qt.UserRole)))
        lv.addWidget(self.orte, 1)
        haupt.addWidget(links)

        # ---- rechts: Leiste, Dateien, Name und Typ ---------------------------------------------------------------------
        rechts = QWidget()
        rv = QVBoxLayout(rechts); rv.setContentsMargins(16, 14, 16, 16); rv.setSpacing(10)
        leiste = QHBoxLayout(); leiste.setSpacing(4)
        self.k_zurueck = self._knopf(_symbol("links"), "Zurück", self.zurueck)
        self.k_vor = self._knopf(_symbol("rechts"), "Vor", self.vor)
        self.k_hoch = self._knopf(_symbol("hoch"), "Übergeordneter Ordner", self.hoch)
        for k in (self.k_zurueck, self.k_vor, self.k_hoch):
            leiste.addWidget(k)
        self.pfad_leiste = QFrame(); self.pfad_leiste.setObjectName("sfPfad"); self.pfad_leiste.setMinimumHeight(36)
        self.pfad_layout = QHBoxLayout(self.pfad_leiste); self.pfad_layout.setContentsMargins(4, 1, 4, 1); self.pfad_layout.setSpacing(0)
        leiste.addWidget(self.pfad_leiste, 1)
        leiste.addSpacing(8)
        leiste.addWidget(self._knopf(_symbol("ordner_neu"), "Neuer Ordner", self.neuer_ordner))
        self.k_liste = self._knopf(_symbol("liste"), "Liste", lambda: self.ansicht(0), pruefbar=True)
        self.k_kacheln = self._knopf(_symbol("kacheln"), "Kacheln", lambda: self.ansicht(1), pruefbar=True)
        leiste.addWidget(self.k_liste); leiste.addWidget(self.k_kacheln)
        rv.addLayout(leiste)

        self.modell = QFileSystemModel(self)
        self._symbole = _Symbole()
        self.modell.setIconProvider(self._symbole)
        self.modell.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.modell.setNameFilterDisables(False)
        self.modell.setRootPath("")
        self.liste = QTreeView(); self.liste.setObjectName("sfListe"); self.liste.setModel(self.modell)
        self.liste.setRootIsDecorated(False); self.liste.setItemsExpandable(False); self.liste.setUniformRowHeights(True)
        self.liste.setSortingEnabled(True); self.liste.sortByColumn(0, Qt.AscendingOrder)
        self.liste.setSelectionMode(QAbstractItemView.SingleSelection)
        kopf = self.liste.header()
        kopf.moveSection(kopf.visualIndex(3), 1)                    # Name, Geändert, Typ, Größe (wie im Vorbild)
        kopf.moveSection(kopf.visualIndex(2), 2)
        kopf.setStretchLastSection(False)
        kopf.setSectionResizeMode(0, QHeaderView.Stretch)                # der Name bekommt den Platz, die übrigen Spalten bleiben ganz
        for spalte, breite in ((3, 150), (2, 170), (1, 100)):
            kopf.setSectionResizeMode(spalte, QHeaderView.Interactive)
            kopf.resizeSection(spalte, breite)
        self.liste.setIconSize(QSize(18, 18))
        self.kacheln = QListView(); self.kacheln.setModel(self.modell)
        self.kacheln.setViewMode(QListView.IconMode); self.kacheln.setResizeMode(QListView.Adjust)
        self.kacheln.setGridSize(QSize(110, 90)); self.kacheln.setIconSize(QSize(40, 40)); self.kacheln.setWordWrap(True)
        self.ansichten = QStackedWidget(); self.ansichten.addWidget(self.liste); self.ansichten.addWidget(self.kacheln)
        for v in (self.liste, self.kacheln):
            v.clicked.connect(self._angeklickt)
            v.doubleClicked.connect(self._doppelklick)
        rv.addWidget(self.ansichten, 1)

        unten = QGridLayout(); unten.setHorizontalSpacing(10); unten.setVerticalSpacing(10)
        self.name = QComboBox(); self.name.setEditable(True); self.name.setInsertPolicy(QComboBox.NoInsert)
        self.name.setEditText(name)
        self.typ = QComboBox()
        for endung, filtertext in self.typen:
            self.typ.addItem(filtertext, None if oeffnen else endung)
        self.typ.setCurrentIndex(max(0, next((i for i, (e, _f) in enumerate(self.typen) if e == vorwahl), 0)))
        self.k_speichern = QPushButton("&Speichern"); self.k_speichern.setObjectName("sfSpeichern"); self.k_speichern.setDefault(True)
        self.k_abbrechen = QPushButton("Abbrechen")
        for k in (self.k_speichern, self.k_abbrechen):
            k.setMinimumWidth(120)
        for feld in (self.name, self.typ, self.k_speichern, self.k_abbrechen):
            feld.setMinimumHeight(36)                                 # Felder in der Höhe des Vorbilds, nicht schmal
        l1 = QLabel("Datei&name:"); l1.setBuddy(self.name)
        l2 = QLabel("Datei&typ:"); l2.setBuddy(self.typ)
        unten.addWidget(l1, 0, 0); unten.addWidget(self.name, 0, 1); unten.addWidget(self.k_speichern, 0, 2)
        unten.addWidget(l2, 1, 0); unten.addWidget(self.typ, 1, 1); unten.addWidget(self.k_abbrechen, 1, 2)
        unten.setColumnStretch(1, 1)
        rv.addLayout(unten)
        if oeffnen:
            self.k_speichern.setText("Ö&ffnen")
            if mehrere:
                for ansicht in (self.liste, self.kacheln):
                    ansicht.setSelectionMode(QAbstractItemView.ExtendedSelection)
                    ansicht.selectionModel().selectionChanged.connect(self._auswahl_geaendert)
        if self.nur_ordner:                                         # Ordner wählen: kein Dateityp, der Ordner steht im Namensfeld
            l1.setText("&Ordner:"); l2.hide(); self.typ.hide()
            self.k_speichern.setText("&Auswählen")
            self.modell.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        haupt.addWidget(rechts, 1)

        self.k_speichern.clicked.connect(self.speichern)
        self.k_abbrechen.clicked.connect(self.reject)
        self.typ.currentIndexChanged.connect(self._typ_gewechselt)
        self.name.lineEdit().textChanged.connect(lambda s: self.k_speichern.setEnabled(bool(s.strip())))
        self.k_speichern.setEnabled(bool(name.strip()))

        self.ordner = ""
        self._filter_setzen()
        self.ansicht(0)
        self.gehe_zu(ordner, merken=False)
        self.name.lineEdit().setFocus()
        stamm = os.path.splitext(name)[0]
        self.name.lineEdit().setSelection(0, len(stamm))

    # ---- Bausteine ---------------------------------------------------------------------------------------------------------
    def _ort(self, text: str, pfad: str, ic: QIcon) -> None:
        it = QListWidgetItem(ic, "  " + text)
        it.setSizeHint(QSize(0, 40))                              # feste Zeilenhöhe: nichts überlappt, egal welches Thema
        it.setData(Qt.UserRole, pfad)
        it.setToolTip(pfad)
        self.orte.addItem(it)

    def _knopf(self, ic: QIcon, tipp: str, aktion, pruefbar: bool = False) -> QToolButton:
        k = QToolButton(); k.setIcon(ic); k.setToolTip(tipp); k.setAutoRaise(True); k.setIconSize(QSize(20, 20))
        k.setFixedSize(36, 34); k.setCheckable(pruefbar)
        if ic.isNull():
            k.setText(tipp[:1])
        k.clicked.connect(lambda _=False: aktion())
        return k

    @property
    def endung(self) -> str:
        return self.typ.currentData() or ""

    # ---- Navigation --------------------------------------------------------------------------------------------------------
    def gehe_zu(self, pfad: str, merken: bool = True) -> None:
        pfad = os.path.abspath(os.path.expanduser(pfad))
        if not os.path.isdir(pfad):
            return
        if merken and self.ordner and pfad != self.ordner:
            self._zurueck.append(self.ordner)
            self._vor.clear()
        self.ordner = pfad
        wurzel = self.modell.index(pfad)
        self.liste.setRootIndex(wurzel)
        self.kacheln.setRootIndex(wurzel)
        self._pfad_zeigen()
        self.k_zurueck.setEnabled(bool(self._zurueck))
        self.k_vor.setEnabled(bool(self._vor))
        self.k_hoch.setEnabled(pfad != os.path.dirname(pfad))
        if self.nur_ordner:
            self.name.setEditText(pfad)
        for i in range(self.orte.count()):
            it = self.orte.item(i)
            it.setSelected(it.data(Qt.UserRole) == pfad)

    def zurueck(self) -> None:
        if self._zurueck:
            self._vor.append(self.ordner)
            ziel = self._zurueck.pop()
            self.gehe_zu(ziel, merken=False)

    def vor(self) -> None:
        if self._vor:
            self._zurueck.append(self.ordner)
            self.gehe_zu(self._vor.pop(), merken=False)

    def hoch(self) -> None:
        self.gehe_zu(os.path.dirname(self.ordner))

    def _pfad_zeigen(self) -> None:
        while self.pfad_layout.count():
            w = self.pfad_layout.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        teile = [p for p in self.ordner.split(os.sep) if p]
        stufen = [(os.sep, os.sep)]
        for i, t in enumerate(teile):
            stufen.append((t, os.sep + os.sep.join(teile[: i + 1])))
        for i, (text, ziel) in enumerate(stufen):
            k = QToolButton(); k.setText(text); k.setAutoRaise(True); k.setToolTip(ziel)
            k.clicked.connect(lambda _=False, z=ziel: self.gehe_zu(z))
            self.pfad_layout.addWidget(k)
            if 0 < i < len(stufen) - 1 or (i == 0 and len(stufen) > 1):
                pfeil = QLabel("›"); pfeil.setContentsMargins(2, 0, 2, 0)
                self.pfad_layout.addWidget(pfeil)
        self.pfad_layout.addStretch(1)

    def ansicht(self, nr: int) -> None:
        self.ansichten.setCurrentIndex(nr)
        self.k_liste.setChecked(nr == 0)
        self.k_kacheln.setChecked(nr == 1)

    def neuer_ordner(self) -> None:
        name = _ordner_name_fragen(self)
        if not name:
            return
        if os.sep in name or name in (".", ".."):
            QMessageBox.warning(self, "Neuer Ordner", "Der Name darf keinen Schrägstrich enthalten.")
            return
        try:
            os.mkdir(os.path.join(self.ordner, name))
        except OSError as e:
            QMessageBox.warning(self, "Neuer Ordner", f"Der Ordner konnte nicht angelegt werden: {e.strerror or e}")
            return
        self.gehe_zu(os.path.join(self.ordner, name))

    # ---- Dateien -----------------------------------------------------------------------------------------------------------
    def _filter_setzen(self) -> None:
        if self.nur_ordner:
            return
        muster = self._muster[self.typ.currentIndex()] if 0 <= self.typ.currentIndex() < len(self._muster) else []
        self.modell.setNameFilters([] if "*" in muster else muster)

    def _typ_gewechselt(self) -> None:
        self._filter_setzen()
        if self.oeffnen:
            return
        text = self.name.currentText().strip()
        stamm, alte = os.path.splitext(text)
        if text and alte.lower() in {e for e, _f in self.typen}:
            self.name.setEditText(stamm + self.endung)

    def _angeklickt(self, idx: QModelIndex) -> None:
        if self.nur_ordner:
            self.name.setEditText(self.modell.filePath(idx))
        elif not self.modell.isDir(idx):
            self.name.setEditText(self.modell.fileName(idx))

    def _auswahl_geaendert(self, *_a) -> None:
        ansicht = self.ansichten.currentWidget()
        namen = [self.modell.fileName(i) for i in ansicht.selectionModel().selectedRows() if not self.modell.isDir(i)]
        if len(namen) > 1:
            self.name.setEditText(" ".join(f"\"{n}\"" for n in namen))

    def _doppelklick(self, idx: QModelIndex) -> None:
        if self.modell.isDir(idx):
            self.gehe_zu(self.modell.filePath(idx))
        else:
            self.name.setEditText(self.modell.fileName(idx))
            self.speichern()

    def zielpfad(self) -> str:
        """Pfad aus Ordner und Dateiname; die Endung des gewählten Dateityps gilt (eine andere bekannte wird ersetzt)."""
        text = os.path.expanduser(self.name.currentText().strip())
        pfad = text if os.path.isabs(text) else os.path.join(self.ordner, text)
        stamm, alte = os.path.splitext(pfad)
        bekannt = {e for e, _f in self.typen}
        if alte.lower() in bekannt:
            pfad = stamm
        return pfad + self.endung

    def speichern(self) -> None:
        text = self.name.currentText().strip()
        if not text:
            return
        if self.oeffnen:
            namen = re.findall(r'"([^"]+)"', text) or [text]
            pfade = [os.path.join(self.ordner, os.path.expanduser(n)) if not os.path.isabs(os.path.expanduser(n)) else os.path.expanduser(n)
                     for n in namen]
            if len(pfade) == 1 and os.path.isdir(pfade[0]):
                self.gehe_zu(pfade[0]); self.name.setEditText("")
                return
            fehlt = [p for p in pfade if not os.path.isfile(p)]
            if fehlt:
                QMessageBox.warning(self, self.windowTitle(), f"„{os.path.basename(fehlt[0])}“ gibt es in diesem Ordner nicht.")
                return
            self._dateien = pfade
            self._ergebnis = (pfade[0], "")
            self.accept()
            return
        if self.nur_ordner:
            ziel = os.path.expanduser(text) if os.path.isabs(os.path.expanduser(text)) else os.path.join(self.ordner, text)
            if not os.path.isdir(ziel):
                QMessageBox.warning(self, self.windowTitle(), f"Den Ordner „{ziel}“ gibt es nicht.")
                return
            self._ergebnis = (os.path.abspath(ziel), "")
            self.accept()
            return
        ziel = os.path.join(self.ordner, os.path.expanduser(text)) if not os.path.isabs(text) else text
        if os.path.isdir(ziel):                                     # Ordnername eingegeben: hineingehen
            self.gehe_zu(ziel)
            self.name.setEditText("")
            return
        pfad = self.zielpfad()
        if not os.path.isdir(os.path.dirname(pfad)):
            QMessageBox.warning(self, self.windowTitle(), f"Den Ordner „{os.path.dirname(pfad)}“ gibt es nicht.")
            return
        if os.path.exists(pfad):
            frage = QMessageBox(QMessageBox.Question, self.windowTitle(),
                                f"„{os.path.basename(pfad)}“ gibt es schon. Ersetzen?\n\nDie bisherige Fassung kommt in die Sicherungskopien.",
                                QMessageBox.Cancel, self)
            ersetzen = frage.addButton("Ersetzen", QMessageBox.AcceptRole)
            frage.setDefaultButton(QMessageBox.Cancel)
            frage.exec()
            if frage.clickedButton() is not ersetzen:
                return
        self._ergebnis = (pfad, self.endung)
        self.accept()

    def ergebnis(self) -> tuple[str, str] | None:
        return self._ergebnis

    def dateien(self) -> list[str]:
        return list(self._dateien)


def speicherort_waehlen(parent, titel: str, startpfad: str, typen: list[tuple[str, str]], vorwahl: str) -> tuple[str, str] | None:
    """Öffnet das Speichern-Fenster. → (Pfad mit Endung, Endung) oder None bei Abbruch."""
    f = SpeichernFenster(parent, titel, startpfad, typen, vorwahl)
    return f.ergebnis() if f.exec() == QDialog.Accepted else None


def ordner_waehlen(parent, titel: str, startordner: str) -> str | None:
    """Dasselbe Fenster zum Wählen eines Ordners. → Ordner oder None bei Abbruch."""
    f = SpeichernFenster(parent, titel, os.path.join(startordner, ""), [], "")
    return f.ergebnis()[0] if f.exec() == QDialog.Accepted else None


def datei_waehlen(parent, titel: str, start: str, filter_text: str, mehrere: bool = False) -> list[str]:
    """Dasselbe Fenster zum Öffnen. ``filter_text`` im Qt-Stil („Dokumente (*.docx *.odt);;Alle Dateien (*)“).
    → die gewählten Dateien (leer bei Abbruch)."""
    typen = []
    for teil in filter_text.split(";;"):
        m = re.match(r"\s*(.*?)\s*\(([^)]*)\)\s*$", teil)
        if m:
            typen.append((m.group(2).split(), teil.strip()))
    if not typen:
        typen = [(["*"], "Alle Dateien (*)")]
    start = os.path.expanduser(start or "~")
    startpfad = os.path.join(start, "") if os.path.isdir(start) else start
    f = SpeichernFenster(parent, titel, startpfad, typen, "", oeffnen=True, mehrere=mehrere)
    return f.dateien() if f.exec() == QDialog.Accepted else []


def datei_speichern(parent, titel: str, startpfad: str, filter_text: str) -> str | None:
    """Speichern mit einem Filter im Qt-Stil („JSON (*.json)“) — für Lunivos eigene Dateien (Sicherungen, Gelerntes …)."""
    typen = []
    for teil in filter_text.split(";;"):
        m = re.match(r"\s*(.*?)\s*\(\*(\.[^ )]+)[^)]*\)\s*$", teil)
        if m:
            typen.append((m.group(2), teil.strip()))
    if not typen:
        return (speicherort_waehlen(parent, titel, startpfad, [("", "Alle Dateien (*)")], "") or (None,))[0]
    erg = speicherort_waehlen(parent, titel, os.path.expanduser(startpfad), typen, typen[0][0])
    return erg[0] if erg else None


class Dateifenster:
    """Dieselben Aufrufe wie ``QFileDialog.get…`` (Rückgabe wie dort), aber mit Lunivos eigenem Fenster.
    So bleibt jeder Aufruf eine Zeile, und überall erscheint dasselbe Fenster."""

    @staticmethod
    def getOpenFileName(parent, titel: str = "", start: str = "", filter_text: str = "Alle Dateien (*)", *_a, **_k):
        wahl = datei_waehlen(parent, titel or "Öffnen", start, filter_text)
        return (wahl[0], "") if wahl else ("", "")

    @staticmethod
    def getOpenFileNames(parent, titel: str = "", start: str = "", filter_text: str = "Alle Dateien (*)", *_a, **_k):
        return datei_waehlen(parent, titel or "Öffnen", start, filter_text, mehrere=True), ""

    @staticmethod
    def getSaveFileName(parent, titel: str = "", start: str = "", filter_text: str = "Alle Dateien (*)", *_a, **_k):
        return datei_speichern(parent, titel or "Speichern unter", start, filter_text) or "", ""

    @staticmethod
    def getExistingDirectory(parent, titel: str = "", start: str = "", *_a, **_k):
        return ordner_waehlen(parent, titel or "Ordner wählen", os.path.expanduser(start or "~")) or ""


def _ordner_name_fragen(parent) -> str:
    """Kleines Fenster „Neuer Ordner“ in der Größe der übrigen Felder (statt des winzigen Eingabefensters von Qt)."""
    d = QDialog(parent)
    d.setWindowTitle("Neuer Ordner")
    d.setStyleSheet(STIL)
    d.setMinimumWidth(440)
    v = QVBoxLayout(d); v.setContentsMargins(24, 20, 24, 20); v.setSpacing(10)
    feld = QLineEdit("Neuer Ordner"); feld.setMinimumHeight(36); feld.selectAll()
    l = QLabel("&Name des Ordners:"); l.setBuddy(feld)
    v.addWidget(l); v.addWidget(feld); v.addSpacing(10)
    knoepfe = QHBoxLayout(); knoepfe.addStretch(1)
    ok = QPushButton("&Anlegen"); ok.setObjectName("sfSpeichern"); ok.setDefault(True)
    ab = QPushButton("Abbrechen")
    for k in (ok, ab):
        k.setMinimumSize(120, 36); knoepfe.addWidget(k)
    v.addLayout(knoepfe)
    ok.clicked.connect(d.accept); ab.clicked.connect(d.reject)
    feld.textChanged.connect(lambda t: ok.setEnabled(bool(t.strip())))
    return feld.text().strip() if d.exec() == QDialog.Accepted else ""
