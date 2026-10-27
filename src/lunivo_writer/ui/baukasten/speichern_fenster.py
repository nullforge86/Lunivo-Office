"""Das eine Speichern-Fenster: Orte links, Ordnerinhalt rechts, unten Dateiname und Dateityp.

Aufbau nach dem Vorbild, das der Eigentümer vorgegeben hat (Bildschirmfoto „Speichern unter“): Titel und Orte (Persönlicher
Ordner, Schreibtisch, Dokumente, Andere Orte) links; oben Zurück, Vor, Hoch, Pfadleiste aus Knöpfen, Neuer Ordner, Liste/Kacheln;
in der Mitte die Dateien des Ordners (Name, Geändert, Typ, Größe), gefiltert nach dem gewählten Dateityp; unten „Dateiname“ mit
„Speichern“ und „Dateityp“ mit „Abbrechen“. Lunivos eigenes Fenster, nicht das des Desktops — so ist der Dateityp immer sichtbar.

Der Baustein liefert nur den Pfad und die Endung (``speicherort_waehlen``); was gespeichert wird, entscheidet der Aufrufer.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QDir, QModelIndex, QSize, QStandardPaths, QStorageInfo, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog, QFileSystemModel, QFrame, QGridLayout, QHBoxLayout,
                               QInputDialog, QLabel, QListView, QListWidget, QListWidgetItem, QMessageBox, QPushButton,
                               QStackedWidget, QStyle, QToolButton, QTreeView, QVBoxLayout, QWidget)

from lunivo_writer.core.farben import Farbe

STIL = """
QWidget#sfLinks { background: palette(window); border-right: 1px solid palette(midlight); }
QLabel#sfTitel { font-size: 17pt; font-weight: 600; padding: 4px 6px 14px 6px; }
QListWidget#sfOrte { background: transparent; border: none; outline: none; }
QListWidget#sfOrte::item { padding: 9px 10px; border-radius: 6px; }
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


def _theme(name: str, ersatz: QStyle.StandardPixmap) -> QIcon:
    """Symbol aus dem Icon-Theme des Systems (Mint-Y, Papirus …), sonst das passende Standardsymbol von Qt."""
    ic = QIcon.fromTheme(name)
    return ic if not ic.isNull() else QApplication.style().standardIcon(ersatz)


def _ordner(art) -> str:
    p = QStandardPaths.writableLocation(art)
    return p if p and os.path.isdir(p) else ""


class SpeichernFenster(QDialog):
    """``typen``: Liste (Endung, Filtertext) wie („.docx“, „Word-Dokument (*.docx)“). ``ergebnis()`` → (Pfad, Endung)."""

    def __init__(self, parent, titel: str, startpfad: str, typen: list[tuple[str, str]], vorwahl: str):
        super().__init__(parent)
        self.setWindowTitle(titel)
        self.setObjectName("speichernFenster")
        self.setStyleSheet(STIL)
        self.resize(1040, 660)
        self.typen = list(typen)
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
        self.orte = QListWidget(); self.orte.setObjectName("sfOrte"); self.orte.setIconSize(QSize(18, 18))
        self.orte.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.orte.setTextElideMode(Qt.ElideMiddle)
        for text, pfad, ic in (("Persönlicher Ordner", QDir.homePath(), _theme("user-home", QStyle.SP_DirHomeIcon)),
                               ("Schreibtisch", _ordner(QStandardPaths.DesktopLocation), _theme("user-desktop", QStyle.SP_DesktopIcon)),
                               ("Dokumente", _ordner(QStandardPaths.DocumentsLocation), _theme("folder-documents", QStyle.SP_DirIcon))):
            if pfad:
                self._ort(text, pfad, ic)
        for vol in QStorageInfo.mountedVolumes():                   # eingehängte Laufwerke (USB-Stick, zweite Platte)
            wurzel = vol.rootPath()
            if vol.isValid() and vol.isReady() and wurzel.startswith(("/media/", "/run/media/")):
                self._ort(os.path.basename(wurzel) or vol.displayName(), wurzel, _theme("drive-removable-media", QStyle.SP_DriveHDIcon))
        self._ort("Rechner", "/", _theme("computer", QStyle.SP_ComputerIcon))
        self.orte.itemClicked.connect(lambda it: self.gehe_zu(it.data(Qt.UserRole)))
        lv.addWidget(self.orte, 1)
        haupt.addWidget(links)

        # ---- rechts: Leiste, Dateien, Name und Typ ---------------------------------------------------------------------
        rechts = QWidget()
        rv = QVBoxLayout(rechts); rv.setContentsMargins(16, 14, 16, 16); rv.setSpacing(10)
        leiste = QHBoxLayout(); leiste.setSpacing(4)
        self.k_zurueck = self._knopf(_theme("go-previous", QStyle.SP_ArrowBack), "Zurück", self.zurueck)
        self.k_vor = self._knopf(_theme("go-next", QStyle.SP_ArrowForward), "Vor", self.vor)
        self.k_hoch = self._knopf(_theme("go-up", QStyle.SP_FileDialogToParent), "Übergeordneter Ordner", self.hoch)
        for k in (self.k_zurueck, self.k_vor, self.k_hoch):
            leiste.addWidget(k)
        self.pfad_leiste = QFrame(); self.pfad_leiste.setObjectName("sfPfad")
        self.pfad_layout = QHBoxLayout(self.pfad_leiste); self.pfad_layout.setContentsMargins(4, 1, 4, 1); self.pfad_layout.setSpacing(0)
        leiste.addWidget(self.pfad_leiste, 1)
        leiste.addSpacing(8)
        leiste.addWidget(self._knopf(_theme("folder-new", QStyle.SP_FileDialogNewFolder), "Neuer Ordner", self.neuer_ordner))
        self.k_liste = self._knopf(_theme("view-list-details", QStyle.SP_FileDialogDetailedView), "Liste", lambda: self.ansicht(0),
                                   pruefbar=True)
        self.k_kacheln = self._knopf(_theme("view-list-icons", QStyle.SP_FileDialogListView), "Kacheln", lambda: self.ansicht(1),
                                     pruefbar=True)
        leiste.addWidget(self.k_liste); leiste.addWidget(self.k_kacheln)
        rv.addLayout(leiste)

        self.modell = QFileSystemModel(self)
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
        kopf.resizeSection(0, 360); kopf.resizeSection(3, 150); kopf.resizeSection(2, 170)
        kopf.setStretchLastSection(True)
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
            self.typ.addItem(filtertext, endung)
        self.typ.setCurrentIndex(max(0, next((i for i, (e, _f) in enumerate(self.typen) if e == vorwahl), 0)))
        self.k_speichern = QPushButton("&Speichern"); self.k_speichern.setObjectName("sfSpeichern"); self.k_speichern.setDefault(True)
        self.k_abbrechen = QPushButton("Abbrechen")
        for k in (self.k_speichern, self.k_abbrechen):
            k.setMinimumWidth(110)
        l1 = QLabel("Datei&name:"); l1.setBuddy(self.name)
        l2 = QLabel("Datei&typ:"); l2.setBuddy(self.typ)
        unten.addWidget(l1, 0, 0); unten.addWidget(self.name, 0, 1); unten.addWidget(self.k_speichern, 0, 2)
        unten.addWidget(l2, 1, 0); unten.addWidget(self.typ, 1, 1); unten.addWidget(self.k_abbrechen, 1, 2)
        unten.setColumnStretch(1, 1)
        rv.addLayout(unten)
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
        it = QListWidgetItem(ic, text)
        it.setData(Qt.UserRole, pfad)
        it.setToolTip(pfad)
        self.orte.addItem(it)

    def _knopf(self, ic: QIcon, tipp: str, aktion, pruefbar: bool = False) -> QToolButton:
        k = QToolButton(); k.setIcon(ic); k.setToolTip(tipp); k.setAutoRaise(True); k.setIconSize(QSize(18, 18))
        k.setFixedSize(32, 30); k.setCheckable(pruefbar)
        if ic.isNull():
            k.setText(tipp[:1])
        k.clicked.connect(lambda _=False: aktion())
        return k

    @property
    def endung(self) -> str:
        return self.typ.currentData()

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
        name, ok = QInputDialog.getText(self, "Neuer Ordner", "Name des Ordners:", text="Neuer Ordner")
        name = name.strip()
        if not ok or not name:
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
        self.modell.setNameFilters([f"*{self.endung}"] if self.endung else [])

    def _typ_gewechselt(self) -> None:
        self._filter_setzen()
        text = self.name.currentText().strip()
        stamm, alte = os.path.splitext(text)
        if text and alte.lower() in {e for e, _f in self.typen}:
            self.name.setEditText(stamm + self.endung)

    def _angeklickt(self, idx: QModelIndex) -> None:
        if not self.modell.isDir(idx):
            self.name.setEditText(self.modell.fileName(idx))

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


def speicherort_waehlen(parent, titel: str, startpfad: str, typen: list[tuple[str, str]], vorwahl: str) -> tuple[str, str] | None:
    """Öffnet das Speichern-Fenster. → (Pfad mit Endung, Endung) oder None bei Abbruch."""
    f = SpeichernFenster(parent, titel, startpfad, typen, vorwahl)
    return f.ergebnis() if f.exec() == QDialog.Accepted else None
