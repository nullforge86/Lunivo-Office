"""Baustein dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QListWidgetItem, QMessageBox
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from writer.anbindung import bausteine
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_EINFUEGEN_VORSCHAU_PT, SCHRIFT_GRUPPENKOPF_FAKTOR
from vcl.qt.widgets.bausteine.schrift.schriftarten import SERIF
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_EINFUEGEN_GROSS, HOEHE_BEREICH_MITTEL, HOEHE_LISTE_HOCH, RAND_ZEILE
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig


class BausteinDialog(PanelFaehig, QDialog):
    """Textbausteine: links die Liste (mitgelieferte und eigene), rechts die Vorschau; Name und Kürzel oben. „Aus Markierung …“ merkt den markierten Text
    samt Formatierung, „Einfügen“ setzt den Baustein an die Schreibmarke. Das Kürzel plus F3 setzt ihn direkt ein."""

    def __init__(self, parent, ed):
        super().__init__(parent)
        from PySide6.QtWidgets import QLineEdit, QTextBrowser
        self.ed = ed
        self.setWindowTitle("Textbausteine")
        self.resize(*GROESSE_FENSTER_EINFUEGEN_GROSS)
        v = _spalte("standard", self)
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
        from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
        felder = FormularGitter(); v.addLayout(felder)
        self.name = zeilenfeld("frei"); self.kuerzel = zeilenfeld("frei")
        felder.zeile("Name:", self.name)
        felder.zeile("Kürzel:", self.kuerzel)
        v.addWidget(abschnittstitel("Bausteine"))
        self.liste = QListWidget(); self.liste.itemDoubleClicked.connect(lambda _: self._einfuegen())
        self.liste.currentItemChanged.connect(lambda *_: self._zeigen())
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.liste.setWordWrap(True)
        self.liste.setTextElideMode(Qt.ElideNone); self.liste.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.liste.setMinimumHeight(HOEHE_LISTE_HOCH)
        v.addWidget(self.liste, 3)
        v.addWidget(abschnittstitel("Vorschau"))
        self.vorschau = QTextBrowser(); self.vorschau.setFont(QFont(SERIF, SCHRIFT_EINFUEGEN_VORSCHAU_PT))
        self.vorschau.document().setDocumentMargin(12); self.vorschau.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.vorschau.setMinimumHeight(HOEHE_BEREICH_MITTEL)
        v.addWidget(self.vorschau, 4)
        h = QLabel("Eigene kommen aus dem Markierten, die übrigen sind mitgeliefert. «So gesetzte Stellen» sind Lücken: Tab springt von einer zur nächsten, Tippen ersetzt sie.")
        h.setWordWrap(True); hinweis_stil(h, klein=True); h.setContentsMargins(*RAND_ZEILE)
        v.addWidget(h)
        self.aus_markierung = knopf("standard", "Aus Markierung …", aktion=self._neu)
        self.loeschen = knopf("standard", "Löschen", aktion=self._weg)
        self.einfuegen_knopf = fussleiste(self, v, self.aus_markierung, self.loeschen, nur_ok=True, ok_text="Einfügen", bei_ok=self._einfuegen)
        self._fuellen()

    def _fuellen(self, wahl: str | None = None) -> None:
        self.liste.clear()
        gruppen = (("Standard", bausteine.standard()), ("Eigene", bausteine.laden()))
        for titel, eintraege in gruppen:
            if not eintraege:
                continue
            kopf = QListWidgetItem(titel.upper()); kopf.setFlags(Qt.NoItemFlags)
            f = kopf.font(); f.setPointSizeF(f.pointSizeF() * SCHRIFT_GRUPPENKOPF_FAKTOR); kopf.setFont(f); self.liste.addItem(kopf)
            for b in eintraege:
                it = QListWidgetItem(b["name"]); it.setData(Qt.UserRole, b); self.liste.addItem(it)
                if wahl and b["name"] == wahl:
                    self.liste.setCurrentItem(it)
        if self.liste.currentItem() is None:
            for i in range(self.liste.count()):
                if self.liste.item(i).data(Qt.UserRole):
                    self.liste.setCurrentRow(i); break
        self._zeigen()

    def _aktuell(self) -> dict | None:
        it = self.liste.currentItem()
        return it.data(Qt.UserRole) if it else None

    def _zeigen(self) -> None:
        b = self._aktuell()
        self.einfuegen_knopf.setEnabled(b is not None)
        self.loeschen.setEnabled(bool(b) and not b.get("standard"))
        if b is None:
            self.vorschau.clear()
            return
        self.name.setText(b["name"]); self.kuerzel.setText(b.get("kuerzel", ""))
        self.vorschau.setPlainText(b.get("text", ""))

    def _neu(self) -> None:
        if self._bild is None:
            return
        pm = QPixmap.fromImage(self._bild)
        b = min(460, max(40, self.width() - 8))
        if pm.width() > b:
            pm = pm.scaledToWidth(b, Qt.SmoothTransformation)
        self.setPixmap(pm)

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._neu()


class BausteinDialog(PanelFaehig, QDialog):
    """Textbausteine: links die Liste (mitgelieferte und eigene), rechts die Vorschau; Name und Kürzel oben. „Aus Markierung …“ merkt den markierten Text
    samt Formatierung, „Einfügen“ setzt den Baustein an die Schreibmarke. Das Kürzel plus F3 setzt ihn direkt ein."""

    def __init__(self, parent, ed):
        super().__init__(parent)
        from PySide6.QtWidgets import QLineEdit, QTextBrowser
        self.ed = ed
        self.setWindowTitle("Textbausteine")
        self.resize(*GROESSE_FENSTER_EINFUEGEN_GROSS)
        v = _spalte("standard", self)
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
        from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
        felder = FormularGitter(); v.addLayout(felder)
        self.name = zeilenfeld("frei"); self.kuerzel = zeilenfeld("frei")
        felder.zeile("Name:", self.name)
        felder.zeile("Kürzel:", self.kuerzel)
        v.addWidget(abschnittstitel("Bausteine"))
        self.liste = QListWidget(); self.liste.itemDoubleClicked.connect(lambda _: self._einfuegen())
        self.liste.currentItemChanged.connect(lambda *_: self._zeigen())
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.liste.setWordWrap(True)
        self.liste.setTextElideMode(Qt.ElideNone); self.liste.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.liste.setMinimumHeight(HOEHE_LISTE_HOCH)
        v.addWidget(self.liste, 3)
        v.addWidget(abschnittstitel("Vorschau"))
        self.vorschau = QTextBrowser(); self.vorschau.setFont(QFont(SERIF, SCHRIFT_EINFUEGEN_VORSCHAU_PT))
        self.vorschau.document().setDocumentMargin(12); self.vorschau.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.vorschau.setMinimumHeight(HOEHE_BEREICH_MITTEL)
        v.addWidget(self.vorschau, 4)
        h = QLabel("Eigene kommen aus dem Markierten, die übrigen sind mitgeliefert. «So gesetzte Stellen» sind Lücken: Tab springt von einer zur nächsten, Tippen ersetzt sie.")
        h.setWordWrap(True); hinweis_stil(h, klein=True); h.setContentsMargins(*RAND_ZEILE)
        v.addWidget(h)
        self.aus_markierung = knopf("standard", "Aus Markierung …", aktion=self._neu)
        self.loeschen = knopf("standard", "Löschen", aktion=self._weg)
        self.einfuegen_knopf = fussleiste(self, v, self.aus_markierung, self.loeschen, nur_ok=True, ok_text="Einfügen", bei_ok=self._einfuegen)
        self._fuellen()

    def _fuellen(self, wahl: str | None = None) -> None:
        self.liste.clear()
        gruppen = (("Standard", bausteine.standard()), ("Eigene", bausteine.laden()))
        for titel, eintraege in gruppen:
            if not eintraege:
                continue
            kopf = QListWidgetItem(titel.upper()); kopf.setFlags(Qt.NoItemFlags)
            f = kopf.font(); f.setPointSizeF(f.pointSizeF() * SCHRIFT_GRUPPENKOPF_FAKTOR); kopf.setFont(f); self.liste.addItem(kopf)
            for b in eintraege:
                it = QListWidgetItem(b["name"]); it.setData(Qt.UserRole, b); self.liste.addItem(it)
                if wahl and b["name"] == wahl:
                    self.liste.setCurrentItem(it)
        if self.liste.currentItem() is None:
            for i in range(self.liste.count()):
                if self.liste.item(i).data(Qt.UserRole):
                    self.liste.setCurrentRow(i); break
        self._zeigen()

    def _aktuell(self) -> dict | None:
        it = self.liste.currentItem()
        return it.data(Qt.UserRole) if it else None

    def _zeigen(self) -> None:
        b = self._aktuell()
        self.einfuegen_knopf.setEnabled(b is not None)
        self.loeschen.setEnabled(bool(b) and not b.get("standard"))
        if b is None:
            self.vorschau.clear()
            return
        self.name.setText(b["name"]); self.kuerzel.setText(b.get("kuerzel", ""))
        if b.get("absaetze"):
            self._vorschau_fuellen(b["absaetze"])
        else:
            self.vorschau.setPlainText(b.get("text", ""))

    def _vorschau_fuellen(self, absaetze: list[dict]) -> None:
        """Die Vorschau (ein eigenes Anzeigefeld) mit den Absätzen eines mitgelieferten Bausteins füllen: ``{"runs": [{"t", "fett", "kursiv", …}], "ausr"}``."""
        from PySide6.QtGui import QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor
        self.vorschau.clear()
        c = QTextCursor(self.vorschau.document())
        for i, a in enumerate(absaetze):
            bf = QTextBlockFormat()
            bf.setAlignment({"mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight, "block": Qt.AlignJustify}.get(a.get("ausr"), Qt.AlignLeft))
            c.insertBlock(bf) if i else c.setBlockFormat(bf)
            for r in a.get("runs", []):
                cf = QTextCharFormat()
                cf.setFontWeight(QFont.Bold if r.get("fett") else QFont.Normal)
                cf.setFontItalic(bool(r.get("kursiv"))); cf.setFontUnderline(bool(r.get("unter"))); cf.setFontStrikeOut(bool(r.get("durch")))
                if r.get("farbe"):
                    cf.setForeground(QColor(r["farbe"]))
                if r.get("marker"):
                    cf.setBackground(QColor(r["marker"]))
                if r.get("pt"):
                    cf.setFontPointSize(float(r["pt"]))
                if r.get("schrift"):
                    cf.setFontFamilies([r["schrift"]])
                c.insertText(r.get("t", ""), cf)

    def _neu(self) -> None:
        from PySide6.QtWidgets import QInputDialog
        c = self.ed.textCursor()
        if not c.hasSelection():
            QMessageBox.information(self, "Textbaustein", "Bitte zuerst den Text markieren, der gemerkt werden soll.")
            return
        n = self.name.text().strip()
        if not n:
            n, ok = QInputDialog.getText(self, "Textbaustein", "Name des Bausteins:")
            if not ok or not n.strip():
                return
            n = n.strip()
        if any(b["name"] == n for b in bausteine.standard()):
            QMessageBox.information(self, "Textbaustein", "Dieser Name gehört zu einem mitgelieferten Baustein. Bitte einen anderen wählen.")
            return
        bausteine.hinzufuegen(self.ed.kennung, n, self.kuerzel.text())
        self._fuellen(n)

    def _weg(self) -> None:
        b = self._aktuell()
        if b and not b.get("standard"):
            bausteine.entfernen(b["name"]); self._fuellen()

    def _einfuegen(self) -> None:
        b = self._aktuell()
        if b:
            self.ed.ansicht._befehl(lambda: bausteine.einfuegen(self.ed.kennung, b)); self.accept()
