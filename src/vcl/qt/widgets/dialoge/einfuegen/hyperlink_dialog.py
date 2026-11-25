"""Hyperlink dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QDialog, QListWidget, QWidget
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf, werkzeugknopf
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_KNOPF_QUADRAT, GROESSE_RASTER_DATEIEN, HOEHE_KNOPF_HOCH, HOEHE_LISTE_MITTEL, ICON_GROSS, ICON_LISTE
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster_hilfen import _titel


class HyperlinkDialog(PanelFaehig, QDialog):
    """„Hyperlink“ wie in der Vorlage: links „Link zu“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse), oben „Anzuzeigender Text“
    und „QuickInfo …“, darunter je Ziel eine Seite. Das Fenster fügt nichts ein; ``ergebnis()`` liefert, was der Aufrufer braucht.

        d = HyperlinkDialog(parent, text="markierter Text", ziele=verweise.querverweis_ziele(ed), ordner=..., adressen=[...])
        if d.exec(): d.ergebnis()   # {"art": "datei"|"dokument"|"mail", "href" | "ziel", "text", "tipp"}
    """

    def __init__(self, parent=None, *, text: str = "", ziele: list[dict] | None = None, ordner: str = "", adressen: list[str] | None = None):
        super().__init__(parent)
        import os
        from PySide6.QtCore import QDir, QSize
        from PySide6.QtWidgets import (
            QFileSystemModel, QInputDialog, QListView, QPushButton, QStackedWidget, QToolButton, QTreeWidget, QTreeWidgetItem, QWidget,
        )
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        self._os, self._QInputDialog = os, QInputDialog
        self.setWindowTitle("Hyperlink")
        self.tipp = ""
        rechts = _spalte("standard", self)
        z = FormularGitter()                                                   # passt sich der Breite an (Seitenleiste: untereinander)
        z.breit(abschnittstitel("Link zu"))
        self.arten = QButtonGroup(self)
        fl = FlussLayout(6)                                                    # die drei Ziele, bei Platzmangel untereinander
        for i, (sym, name) in enumerate((("kette", "&Datei oder Webseite"), ("textmarke", "Aktuelles D&okument"),
                                         ("briefumschlag", "E-Mail-Adre&sse"))):
            b = werkzeugknopf("band_menue", name, symbol=sym, symbolgroesse=ICON_LISTE, symbol_einpassen=True, umschaltbar=True)
            b.setMinimumHeight(HOEHE_KNOPF_HOCH)
            self.arten.addButton(b, i); fl.addWidget(b)
        z.breit(fl)
        self.text = zeilenfeld("standard", text)
        quick = knopf("klein", "&QuickInfo …", aktion=self._quickinfo)
        z.zeile(_titel("Anzuzeigender &Text:", self.text), self.text); z.breit(quick)
        rechts.addLayout(z)
        self.seiten = QStackedWidget(); rechts.addWidget(self.seiten, 1)
        # Seite 1: Datei oder Webseite
        s1 = QWidget(); v1 = _spalte("standard", s1)
        oz = _reihe("standard")
        self.ordner = Auswahlfeld(); self.ordner.setEditable(True); self.ordner.setAccessibleName("Ordner")
        start = ordner if ordner and os.path.isdir(ordner) else QDir.homePath()
        for p in dict.fromkeys([start, QDir.homePath()] + [os.path.join(QDir.homePath(), n) for n in ("Schreibtisch", "Desktop", "Dokumente")]):
            if os.path.isdir(p):
                self.ordner.addItem(symbole.icon("oeffnen", ICON_GROSS), p)
        hoch = werkzeugknopf("fest", symbol="trefferHoch", symbolgroesse="gross", tooltip="Übergeordneter Ordner", name="Übergeordneter Ordner",
                             groesse=GROESSE_KNOPF_QUADRAT, flach=False)
        oz.addWidget(self.ordner, 1); oz.addWidget(hoch); v1.addLayout(oz)
        self.modell = QFileSystemModel(self); self.modell.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.dateien = QListView(); self.dateien.setModel(self.modell); self.dateien.setViewMode(QListView.ListMode)
        self.dateien.setFlow(QListView.TopToBottom); self.dateien.setWrapping(True); self.dateien.setResizeMode(QListView.Adjust)
        self.dateien.setGridSize(QSize(*GROESSE_RASTER_DATEIEN)); self.dateien.setUniformItemSizes(True); self.dateien.setMinimumHeight(HOEHE_LISTE_MITTEL)
        self.dateien.setAccessibleName("Dateien")
        v1.addWidget(self.dateien, 1)
        az = FormularGitter()
        self.adresse = zeilenfeld("standard", platzhalter="https://… oder Pfad einer Datei")
        marken = knopf("klein", "&Lesezeichen …", aktiv=False)
        marken.setToolTip("Sprungziele in fremden Dateien kann Lunivo noch nicht auslesen.")
        az.zeile(_titel("Adr&esse:", self.adresse), self.adresse); az.breit(marken)
        v1.addLayout(az)
        self.seiten.addWidget(s1)
        # Seite 2: Aktuelles Dokument
        s2 = QWidget(); v2 = _spalte("standard", s2)
        self.stellen = QTreeWidget(); self.stellen.setHeaderHidden(True); self.stellen.setAccessibleName("Stelle im Dokument")
        v2.addWidget(_titel("&Wählen Sie eine Stelle im Dokument:", self.stellen)); v2.addWidget(self.stellen, 1)
        anfang = QTreeWidgetItem(["Anfang des Dokuments"]); anfang.setData(0, Qt.UserRole, {"art": "Anfang", "block": 0, "text": ""})
        self.stellen.addTopLevelItem(anfang)
        gruppen = {}
        for z_ in ziele or []:
            art = "Überschriften" if z_["art"] == "Überschrift" else "Textmarken" if z_["art"] == "Textmarke" else None
            if art is None:
                continue
            if art not in gruppen:
                gruppen[art] = QTreeWidgetItem([art]); gruppen[art].setFlags(Qt.ItemIsEnabled); self.stellen.addTopLevelItem(gruppen[art])
            it = QTreeWidgetItem([z_["text"]]); it.setData(0, Qt.UserRole, z_); gruppen[art].addChild(it)
        self.stellen.expandAll(); self.stellen.setCurrentItem(anfang)
        self.seiten.addWidget(s2)
        # Seite 3: E-Mail-Adresse
        s3 = QWidget(); v3 = _spalte("standard", s3); g3 = FormularGitter(); v3.addLayout(g3, 1)
        self.mail = zeilenfeld("standard"); self.betreff = zeilenfeld("standard")
        self.zuletzt = QListWidget(); self.zuletzt.addItems(adressen or []); self.zuletzt.setAccessibleName("Zuletzt verwendete E-Mail-Adressen")
        g3.zeile(_titel("E-&Mail-Adresse:", self.mail), self.mail)
        g3.zeile(_titel("&Betreff:", self.betreff), self.betreff)
        g3.zeile(_titel("&Zuletzt verwendete E-Mail-Adressen:", self.zuletzt), self.zuletzt)
        self.seiten.addWidget(s3)
        self.ok = fussleiste(self, rechts)
        # Verbindungen
        self.arten.idClicked.connect(lambda i: (self.seiten.setCurrentIndex(i), self._pruefen()))
        self.ordner.currentTextChanged.connect(self._ordner_zeigen)
        hoch.clicked.connect(lambda: self._ordner_setzen(os.path.dirname(self.ordner.currentText().rstrip(os.sep)) or os.sep))
        self.dateien.clicked.connect(lambda i: self.adresse.setText(self.modell.filePath(i)))
        self.dateien.doubleClicked.connect(self._doppelklick)
        self.zuletzt.currentTextChanged.connect(self.mail.setText)
        for f in (self.adresse, self.mail):
            f.textChanged.connect(lambda _t: self._pruefen())
        self.stellen.currentItemChanged.connect(lambda *_: self._pruefen())
        self.arten.button(0).setChecked(True)
        self._ordner_zeigen(self.ordner.currentText())
        self._pruefen()

    def _ordner_setzen(self, pfad: str) -> None:
        if self.ordner.findText(pfad) < 0:
            self.ordner.addItem(pfad)
        self.ordner.setCurrentText(pfad)

    def _ordner_zeigen(self, pfad: str) -> None:
        if self._os.path.isdir(pfad):
            self.dateien.setRootIndex(self.modell.setRootPath(pfad))

    def _doppelklick(self, i) -> None:
        pfad = self.modell.filePath(i)
        if self.modell.isDir(i):
            self._ordner_setzen(pfad)
        else:
            self.adresse.setText(pfad); self._pruefen()
            if self.ok.isEnabled():
                self.accept()

    def _quickinfo(self) -> None:
        t, ok = self._QInputDialog.getText(self, "QuickInfo für Hyperlink", "QuickInfo-Text:", text=self.tipp)
        if ok:
            self.tipp = t.strip()

    def art_waehlen(self, i: int) -> None:
        self.arten.button(i).setChecked(True); self.seiten.setCurrentIndex(i); self._pruefen()

    def _pruefen(self) -> None:
        i = self.arten.checkedId()
        if i == 0:
            gut = bool(self.adresse.text().strip())
        elif i == 1:
            it = self.stellen.currentItem()
            gut = it is not None and it.data(0, Qt.UserRole) is not None
        else:
            gut = "@" in self.mail.text()
        self.ok.setEnabled(gut)

    @staticmethod
    def adresse_zu_href(adresse: str) -> str:
        """Eingabe → Linkziel: Dateipfad → file://…, „www.…“ → https://…, sonst unverändert."""
        import os
        from PySide6.QtCore import QUrl
        a = adresse.strip()
        if a.startswith(("/", "~")):
            return QUrl.fromLocalFile(os.path.expanduser(a)).toString()
        if "://" not in a and not a.startswith(("mailto:", "#")) and "." in a and " " not in a:
            return "https://" + a
        return a

    def ergebnis(self) -> dict:
        from PySide6.QtCore import QUrl, QUrlQuery
        i = self.arten.checkedId()
        r = {"text": self.text.text().strip(), "tipp": self.tipp}
        if i == 1:
            r.update(art="dokument", ziel=self.stellen.currentItem().data(0, Qt.UserRole))
            r["text"] = r["text"] or r["ziel"].get("text") or "Anfang des Dokuments"
        elif i == 2:
            u = QUrl("mailto:" + self.mail.text().strip())
            if self.betreff.text().strip():
                q = QUrlQuery(); q.addQueryItem("subject", self.betreff.text().strip()); u.setQuery(q)
            r.update(art="mail", href=u.toString(), adresse=self.mail.text().strip())
            r["text"] = r["text"] or self.mail.text().strip()
        else:
            r.update(art="datei", href=self.adresse_zu_href(self.adresse.text()))
            r["text"] = r["text"] or self.adresse.text().strip()
        return r
