"""Kleine Fenster des Reiters Einfügen nach den WPS-Vorlagen: „Zahl“, „Felder“, „Text in Tabelle umwandeln“, „Tabelle in Text konvertieren“.

    d = ZahlDialog(parent)                 # if d.exec(): d.ergebnis() → "XIV"
    d = FelderDialog(parent, kontext)      # if d.exec(): d.feld() → (Anweisung, Ergebnis)
    d = TrennerDialog(parent, zu_tabelle=True, texte=[…])   # if d.exec(): d.trenner(), d.spalten()

Die Fenster ändern das Dokument nicht; der Aufrufer (``Befehle``) fügt das Ergebnis ein.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QRadioButton, QSpinBox,
    QVBoxLayout,
)

from lunivo_writer.editor import felder as F
from lunivo_writer.editor import tabelle_text as TT
from lunivo_writer.editor import zahlformat as Z
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


class ZahlDialog(QDialog):
    """Feld „Zahl“, darunter die Liste „Zahlentyp“ (wie die Vorlage „Zahl“)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zahl")
        v = QVBoxLayout(self)
        self.zahl = QLineEdit(); self.zahl.setMinimumHeight(34); self.zahl.setAccessibleName("Zahl")
        v.addWidget(_titel("&Zahl", self.zahl)); v.addWidget(self.zahl)
        self.typ = QListWidget(); self.typ.setAccessibleName("Zahlentyp")
        for k, t in Z.TYPEN:
            it = QListWidgetItem(t); it.setData(Qt.UserRole, k); self.typ.addItem(it)
        self.typ.setCurrentRow(0)
        self.typ.setMinimumHeight(self.typ.sizeHintForRow(0) * 5 + 8)
        v.addWidget(_titel("Zahlen&typ", self.typ)); v.addWidget(self.typ)
        self.hinweis = QLabel(""); self.hinweis.setStyleSheet("color: palette(mid);"); self.hinweis.setWordWrap(True)
        v.addWidget(self.hinweis)
        self.ok = fussleiste(self, v, bei_ok=self._pruefen)
        self.typ.itemDoubleClicked.connect(lambda _i: self._pruefen())
        self.zahl.textChanged.connect(lambda _t: self.hinweis.setText(""))
        self.resize(300, 0)

    def ergebnis(self) -> str:
        """Die Zahl im gewählten Typ; ``ValueError`` bei falscher Eingabe."""
        text = self.zahl.text().strip().replace(".", "")
        if not text.isdigit():
            raise ValueError("Bitte eine ganze Zahl eingeben.")
        return Z.zahl_text(int(text), self.typ.currentItem().data(Qt.UserRole))

    def _pruefen(self) -> None:
        try:
            self.ergebnis()
        except ValueError as e:
            self.hinweis.setText(str(e)); self.zahl.setFocus()
            return
        self.accept()


class FelderDialog(QDialog):
    """Links die Feldnamen, rechts Beschreibung, Feldanweisung und Ergebnis."""

    def __init__(self, parent=None, kontext: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Felder")
        self.kontext = kontext or {}
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(12)
        self.liste = QListWidget(); self.liste.setAccessibleName("Feldnamen"); self.liste.addItems(list(F.FELDER))
        self.liste.setMinimumWidth(170)
        g.addWidget(_titel("&Feldnamen:", self.liste), 0, 0); g.addWidget(self.liste, 1, 0, 3, 1)
        self.beschreibung = QLabel(); self.beschreibung.setWordWrap(True)
        self.anweisung = QLineEdit(); self.anweisung.setReadOnly(True); self.anweisung.setMinimumHeight(34); self.anweisung.setMinimumWidth(240)
        self.ergebnis_text = QLineEdit(); self.ergebnis_text.setReadOnly(True); self.ergebnis_text.setMinimumHeight(34)
        g.addWidget(self.beschreibung, 1, 1)
        rechts = QVBoxLayout()
        rechts.addWidget(_titel("Feld&anweisung:", self.anweisung)); rechts.addWidget(self.anweisung)
        rechts.addWidget(_titel("&Ergebnis:", self.ergebnis_text)); rechts.addWidget(self.ergebnis_text); rechts.addStretch(1)
        g.addLayout(rechts, 2, 1)
        g.setColumnStretch(1, 1)
        v.addLayout(g)
        fussleiste(self, v)
        self.liste.currentTextChanged.connect(self._zeigen)
        self.liste.itemDoubleClicked.connect(lambda _i: self.accept())
        self.liste.setCurrentRow(0)
        self.resize(520, 300)

    def _zeigen(self, name: str) -> None:
        text, anweisung = F.FELDER.get(name, ("", ""))
        self.beschreibung.setText(text); self.anweisung.setText(anweisung); self.anweisung.setCursorPosition(0)
        self.ergebnis_text.setText(F.ergebnis(name, self.kontext)); self.ergebnis_text.setCursorPosition(0)

    def feld(self) -> tuple[str, str]:
        return self.anweisung.text(), self.ergebnis_text.text()


class TrennerDialog(QDialog):
    """„Text in Tabelle umwandeln“ (mit Spaltenzahl) oder „Tabelle in Text konvertieren“: woran getrennt wird."""

    def __init__(self, parent=None, *, zu_tabelle: bool = True, texte: list[str] | None = None):
        super().__init__(parent)
        self.zu_tabelle, self.texte = zu_tabelle, list(texte or [])
        self.setWindowTitle("Text in Tabelle umwandeln" if zu_tabelle else "Tabelle in Text konvertieren")
        v = QVBoxLayout(self)
        if zu_tabelle:
            g = QGridLayout()
            self._spalten = QSpinBox(); self._spalten.setRange(1, 63); self._spalten.setMinimumHeight(34); self._spalten.setMinimumWidth(90)
            self._zeilen = QLabel()
            g.addWidget(_titel("&Spaltenanzahl:", self._spalten), 0, 0); g.addWidget(self._spalten, 0, 1)
            g.addWidget(QLabel("Zeilenanzahl:"), 1, 0); g.addWidget(self._zeilen, 1, 1)
            g.setColumnStretch(2, 1)
            v.addLayout(g)
        t = QLabel("Text trennen bei" if zu_tabelle else "Zellen trennen durch"); f = t.font(); f.setBold(True); t.setFont(f)
        v.addWidget(t)
        self._gruppe = QButtonGroup(self)
        g = QGridLayout()
        for i, (_z, text) in enumerate(TT.TRENNER):
            r = QRadioButton(text); self._gruppe.addButton(r, i); g.addWidget(r, i // 3, i % 3)
        andere = QRadioButton("A&ndere:"); self._gruppe.addButton(andere, len(TT.TRENNER))
        self.andere = QLineEdit("-"); self.andere.setMaxLength(1); self.andere.setMaximumWidth(48); self.andere.setMinimumHeight(34)
        self.andere.setAlignment(Qt.AlignCenter); self.andere.setAccessibleName("Anderes Trennzeichen")
        z = QHBoxLayout(); z.addWidget(andere); z.addWidget(self.andere); z.addStretch(1)
        g.addLayout(z, 2, 0, 1, 3)
        v.addLayout(g)
        self.andere.textEdited.connect(lambda _t: andere.setChecked(True))
        vorgabe = "\t" if any("\t" in s for s in self.texte) or not zu_tabelle else "\n"
        self._gruppe.button([k for k, _t in TT.TRENNER].index(vorgabe)).setChecked(True)
        self._gruppe.idToggled.connect(lambda _i, an: an and self._zaehlen())
        self.andere.textChanged.connect(lambda _t: self._zaehlen())
        fussleiste(self, v)
        self._zaehlen()

    def trenner(self) -> str:
        i = self._gruppe.checkedId()
        return TT.TRENNER[i][0] if i < len(TT.TRENNER) else (self.andere.text() or "-")

    def spalten(self) -> int | None:
        return self._spalten.value() if self.zu_tabelle else None

    def _zaehlen(self) -> None:
        if not self.zu_tabelle:
            return
        z = TT.zellen(self.texte, self.trenner())
        self._spalten.setValue(max((len(r) for r in z), default=1))
        self._zeilen.setText(str(len(z)))


class SeitenzahlDialog(QDialog):
    """„Seitenzahl einfügen“: Position (Kopf-/Fußzeile), Ausrichtung und Schreibweise, mit kleinem Seitenbild."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from lunivo_writer.editor import seitenzahl as SZ
        from lunivo_writer.ui.baukasten.dialog_rahmen import VorschauFlaeche
        self.setWindowTitle("Seitenzahl einfügen")
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(12)
        self.muster = QComboBox(); self.ort = QComboBox(); self.ausrichtung = QComboBox()
        for k, t in SZ.MUSTER:
            self.muster.addItem(t, k)
        for k, t in (("kopf", "Kopfzeile"), ("fuss", "Fußzeile")):
            self.ort.addItem(t, k)
        for k, t in (("left", "Links"), ("center", "Mitte"), ("right", "Rechts")):
            self.ausrichtung.addItem(t, k)
        self.ort.setCurrentIndex(1); self.ausrichtung.setCurrentIndex(1)
        for i, (text, feld) in enumerate((("&Format:", self.muster), ("&Position:", self.ort), ("&Ausrichtung:", self.ausrichtung))):
            feld.setMinimumHeight(34); feld.setMinimumWidth(180)
            g.addWidget(_titel(text, feld), i, 0); g.addWidget(feld, i, 1)
        self.vorschau = VorschauFlaeche(self._male, 140, flaeche=False); self.vorschau.setFixedSize(110, 140)
        g.addWidget(self.vorschau, 0, 2, 4, 1)
        g.setRowStretch(3, 1)
        v.addLayout(g)
        fussleiste(self, v)
        for c in (self.muster, self.ort, self.ausrichtung):
            c.currentIndexChanged.connect(lambda _i: self.vorschau.update())

    def _male(self, p, r) -> None:
        from lunivo_writer.ui.baukasten.seiten_bildchen import seitenzahl_zeichner
        seitenzahl_zeichner(self.ort.currentData(), self.ausrichtung.currentData())(p, r)

    def werte(self) -> tuple[str, str, str]:
        return self.ort.currentData(), self.ausrichtung.currentData(), self.muster.currentData()


class HyperlinkDialog(QDialog):
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
        from lunivo_writer.ui.widgets import icons
        self._os, self._QInputDialog = os, QInputDialog
        self.setWindowTitle("Hyperlink")
        self.tipp = ""
        h = QHBoxLayout(self)
        from PySide6.QtWidgets import QFrame
        links = QVBoxLayout(); t = QLabel("Link zu:"); t.setAlignment(Qt.AlignCenter); links.addWidget(t)
        leiste = QFrame(); leiste.setFrameShape(QFrame.StyledPanel); leiste.setFixedWidth(164); lv = QVBoxLayout(leiste)
        lv.setContentsMargins(4, 4, 4, 4); lv.setSpacing(4)
        self.arten = QButtonGroup(self)
        for i, (sym, name) in enumerate((("kette", "&Datei oder Webseite"), ("textmarke", "Aktuelles D&okument"),
                                         ("briefumschlag", "E-Mail-Adre&sse"))):
            b = QToolButton(); b.setText(name); b.setIcon(icons.icon(sym, 24)); b.setIconSize(QSize(24, 24)); b.setCheckable(True)
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); b.setAutoRaise(True); b.setMinimumSize(152, 60)
            self.arten.addButton(b, i); lv.addWidget(b)
        lv.addStretch(1)
        links.addWidget(leiste, 1); h.addLayout(links)
        rechts = QVBoxLayout(); h.addLayout(rechts, 1)
        z = QHBoxLayout()
        self.text = QLineEdit(text); self.text.setMinimumHeight(34)
        quick = QPushButton("&QuickInfo …"); quick.setMinimumHeight(34); quick.clicked.connect(self._quickinfo)
        z.addWidget(_titel("Anzuzeigender &Text:", self.text)); z.addWidget(self.text, 1); z.addWidget(quick)
        rechts.addLayout(z)
        self.seiten = QStackedWidget(); rechts.addWidget(self.seiten, 1)
        # Seite 1: Datei oder Webseite
        s1 = QWidget(); v1 = QVBoxLayout(s1); v1.setContentsMargins(0, 0, 0, 0)
        oz = QHBoxLayout()
        self.ordner = QComboBox(); self.ordner.setEditable(True); self.ordner.setMinimumHeight(34); self.ordner.setAccessibleName("Ordner")
        start = ordner if ordner and os.path.isdir(ordner) else QDir.homePath()
        for p in dict.fromkeys([start, QDir.homePath()] + [os.path.join(QDir.homePath(), n) for n in ("Schreibtisch", "Desktop", "Dokumente")]):
            if os.path.isdir(p):
                self.ordner.addItem(icons.icon("oeffnen", 18), p)
        hoch = QToolButton(); hoch.setIcon(icons.icon("trefferHoch", 18)); hoch.setToolTip("Übergeordneter Ordner"); hoch.setFixedSize(34, 34)
        hoch.setAccessibleName("Übergeordneter Ordner")
        oz.addWidget(self.ordner, 1); oz.addWidget(hoch); v1.addLayout(oz)
        self.modell = QFileSystemModel(self); self.modell.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.dateien = QListView(); self.dateien.setModel(self.modell); self.dateien.setViewMode(QListView.ListMode)
        self.dateien.setFlow(QListView.TopToBottom); self.dateien.setWrapping(True); self.dateien.setResizeMode(QListView.Adjust)
        self.dateien.setGridSize(QSize(170, 26)); self.dateien.setUniformItemSizes(True); self.dateien.setMinimumSize(520, 240)
        self.dateien.setAccessibleName("Dateien")
        v1.addWidget(self.dateien, 1)
        az = QHBoxLayout()
        self.adresse = QLineEdit(); self.adresse.setMinimumHeight(34); self.adresse.setPlaceholderText("https://… oder Pfad einer Datei")
        marken = QPushButton("&Lesezeichen …"); marken.setMinimumHeight(34); marken.setEnabled(False)
        marken.setToolTip("Sprungziele in fremden Dateien kann Lunivo noch nicht auslesen.")
        az.addWidget(_titel("Adr&esse:", self.adresse)); az.addWidget(self.adresse, 1); az.addWidget(marken)
        v1.addLayout(az)
        self.seiten.addWidget(s1)
        # Seite 2: Aktuelles Dokument
        s2 = QWidget(); v2 = QVBoxLayout(s2); v2.setContentsMargins(0, 0, 0, 0)
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
        s3 = QWidget(); g3 = QGridLayout(s3); g3.setContentsMargins(0, 0, 0, 0)
        self.mail = QLineEdit(); self.mail.setMinimumHeight(34); self.betreff = QLineEdit(); self.betreff.setMinimumHeight(34)
        self.zuletzt = QListWidget(); self.zuletzt.addItems(adressen or []); self.zuletzt.setAccessibleName("Zuletzt verwendete E-Mail-Adressen")
        g3.addWidget(_titel("E-&Mail-Adresse:", self.mail), 0, 0); g3.addWidget(self.mail, 1, 0)
        g3.addWidget(_titel("&Betreff:", self.betreff), 2, 0); g3.addWidget(self.betreff, 3, 0)
        g3.addWidget(_titel("&Zuletzt verwendete E-Mail-Adressen:", self.zuletzt), 4, 0); g3.addWidget(self.zuletzt, 5, 0)
        g3.setRowStretch(5, 1)
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
        self.resize(820, 470)

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


class ObjektDialog(QDialog):
    """„Objekt einfügen“ wie in der Vorlage. „Neu“ (ein eingebettetes Office-Objekt anlegen) kann Lunivo nicht und bleibt grau;
    „Aus Datei erstellen“ fügt Text, Dokument oder Bild ein, mit „Als Symbol anzeigen“ ein Dateisymbol mit Link auf die Datei."""

    TYPEN = ("DOCX-Dokument", "ODT-Dokument", "XLSX-Tabelle", "PPTX-Präsentation")

    def __init__(self, parent=None, *, als_symbol: bool = False, ordner: str = ""):
        super().__init__(parent)
        from PySide6.QtWidgets import QCheckBox, QFrame, QPushButton
        self.setWindowTitle("Objekt einfügen")
        self._ordner = ordner
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(14)
        self.neu = QRadioButton("&Neu"); self.aus_datei = QRadioButton("&Aus Datei erstellen")
        self.neu.setEnabled(False); self.neu.setToolTip("Eingebettete Office-Objekte kann Lunivo nicht anlegen.")
        self.aus_datei.setChecked(True)
        links = QVBoxLayout(); links.addWidget(self.neu); links.addWidget(self.aus_datei); links.addStretch(1)
        g.addLayout(links, 0, 0)
        mitte = QVBoxLayout()
        self.typen = QListWidget(); self.typen.addItems(list(self.TYPEN)); self.typen.setEnabled(False); self.typen.setMaximumHeight(110)
        mitte.addWidget(_titel("Objekt&typ:", self.typen)); mitte.addWidget(self.typen)
        dz = QHBoxLayout()
        self.datei = QLineEdit(); self.datei.setMinimumHeight(34); self.datei.setAccessibleName("Datei")
        such = QPushButton("&Durchsuchen …"); such.setMinimumHeight(34); such.clicked.connect(self._suchen)
        dz.addWidget(self.datei, 1); dz.addWidget(such)
        mitte.addWidget(_titel("&Datei:", self.datei)); mitte.addLayout(dz)
        g.addLayout(mitte, 0, 1)
        self.symbol = QCheckBox("Als Sym&bol anzeigen"); self.symbol.setChecked(als_symbol)
        g.addWidget(self.symbol, 0, 2, Qt.AlignTop)
        g.setColumnStretch(1, 1)
        v.addLayout(g)
        v.addWidget(QLabel("Ergebnis"))
        kasten = QFrame(); kasten.setFrameShape(QFrame.StyledPanel); kh = QHBoxLayout(kasten)
        self.ergebnis_text = QLabel(); self.ergebnis_text.setWordWrap(True); kh.addWidget(self.ergebnis_text)
        v.addWidget(kasten)
        self.ok = fussleiste(self, v)
        self.datei.textChanged.connect(lambda _t: self._beschreiben()); self.symbol.toggled.connect(lambda _a: self._beschreiben())
        self._beschreiben()
        self.resize(640, 0)

    def _suchen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        pfade = datei_waehlen(self, "Datei für das Objekt wählen", self.datei.text() or self._ordner, "Alle Dateien (*)")
        if pfade:
            self.datei.setText(pfade[0])

    def art(self) -> str:
        """"symbol" | "bild" | "text" | "" (keine Datei)."""
        import os
        pfad = self.datei.text().strip()
        if not pfad or not os.path.isfile(pfad):
            return ""
        if self.symbol.isChecked():
            return "symbol"
        endung = os.path.splitext(pfad)[1].lower()
        if endung in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"):
            return "bild"
        if endung in (".docx", ".odt", ".rtf", ".txt", ".md"):
            return "text"
        return "symbol"

    def _beschreiben(self) -> None:
        import os
        a = self.art()
        name = os.path.basename(self.datei.text().strip())
        self.ok.setEnabled(bool(a))
        self.ergebnis_text.setText({
            "": "Wählen Sie eine Datei. Ihr Inhalt wird in das Dokument eingefügt.",
            "bild": f"Fügt das Bild „{name}“ in Ihr Dokument ein.",
            "text": f"Fügt den Inhalt von „{name}“ in Ihr Dokument ein (Text, Tabellen und Bilder).",
            "symbol": f"Fügt ein Symbol für „{name}“ ein. Ein Klick darauf öffnet die Datei."
                      + ("" if self.symbol.isChecked() else " (Den Inhalt dieser Dateiart kann Lunivo nicht einbetten.)"),
        }[a])
