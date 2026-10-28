"""Fenster des Reiters Verweise nach den WPS-Vorlagen: „Inhaltsverzeichnis“ und „Indexeintrag festlegen“.

    d = InhaltsverzeichnisDialog(parent, {"fuell": "punkt", "ebenen": 3, …})   # if d.exec(): d.ergebnis() → dict
    d = IndexeintragDialog(parent, "Apfel", ["Marke1"], auswahl=True)          # d.markieren(Eintrag, alle) bei jedem Klick

Die Fenster ändern das Dokument nicht; der Aufrufer (``Befehle``) setzt das Ergebnis um.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFontMetricsF, QPainter
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton,
    QSpinBox, QVBoxLayout,
)

from lunivo_writer.editor import tabfuell
from lunivo_writer.editor.indexeintrag import Eintrag
from lunivo_writer.editor.verzeichnis import TOC_FUELL, TOC_VORGABE
from lunivo_writer.ui.baukasten.dialog_rahmen import VorschauFlaeche, fussleiste, knopfzeile

_FUELL_ANZEIGE = {"": "(ohne)", "punkt": "." * 24, "strich": "-" * 20, "linie": "_" * 18}


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


class InhaltsverzeichnisDialog(QDialog):
    """Links Füllzeichen, Ebenen anzeigen, Seitenzahlen anzeigen/rechtsbündig, Hyperlinks verwenden; rechts die Seitenansicht."""

    def __init__(self, parent=None, opt: dict | None = None):
        super().__init__(parent)
        o = {**TOC_VORGABE, **(opt or {})}
        self.setWindowTitle("Inhaltsverzeichnis")
        v = QVBoxLayout(self)
        box = QGroupBox("Inhaltsverzeichnis"); h = QHBoxLayout(box); h.setSpacing(12)
        links = QVBoxLayout()
        self.fuell = QComboBox(); self.fuell.setMinimumHeight(34); self.fuell.setMinimumWidth(190); self.fuell.setAccessibleName("Füllzeichen")
        for schl in TOC_FUELL:
            self.fuell.addItem(_FUELL_ANZEIGE[schl], schl)
        self.fuell.setCurrentIndex(max(0, self.fuell.findData(o["fuell"])))
        self.ebenen = QSpinBox(); self.ebenen.setRange(1, 9); self.ebenen.setValue(int(o["ebenen"])); self.ebenen.setMinimumHeight(34)
        self.ebenen.setAccessibleName("Ebenen anzeigen")
        self.seitenzahlen = QCheckBox("Seitenza&hlen anzeigen"); self.seitenzahlen.setChecked(bool(o["seitenzahlen"]))
        self.rechts = QCheckBox("Seitenzahlen &rechtsbündig"); self.rechts.setChecked(bool(o["rechts"]))
        self.links = QCheckBox("&Hyperlinks verwenden"); self.links.setChecked(bool(o["links"]))
        optionen = QPushButton("&Optionen…"); optionen.setMinimumHeight(36); optionen.setEnabled(False)   # Vorlagen den Ebenen zuordnen: fehlt noch
        links.addWidget(_titel("Füllzei&chen:", self.fuell)); links.addWidget(self.fuell)
        links.addWidget(_titel("&Ebenen anzeigen:", self.ebenen)); links.addWidget(self.ebenen)
        for w in (self.seitenzahlen, self.rechts, self.links):
            links.addWidget(w)
        z = QHBoxLayout(); z.addWidget(optionen); z.addStretch(1); links.addLayout(z)
        links.addStretch(1)
        h.addLayout(links)
        rechts = QVBoxLayout()
        rechts.addWidget(QLabel("Seitenansicht"))
        self.vorschau = VorschauFlaeche(self._male, 190); self.vorschau.setMinimumWidth(260)
        rechts.addWidget(self.vorschau, 1)
        h.addLayout(rechts, 1)
        v.addWidget(box)
        fussleiste(self, v)
        for w in (self.seitenzahlen, self.rechts, self.links):
            w.toggled.connect(self._auffrischen)
        self.fuell.currentIndexChanged.connect(self._auffrischen); self.ebenen.valueChanged.connect(self._auffrischen)
        self._auffrischen()

    def ergebnis(self) -> dict:
        return {"fuell": self.fuell.currentData() or "", "ebenen": self.ebenen.value(), "seitenzahlen": self.seitenzahlen.isChecked(),
                "rechts": self.rechts.isChecked(), "links": self.links.isChecked()}

    def _auffrischen(self, *_):
        self.rechts.setEnabled(self.seitenzahlen.isChecked())
        self.fuell.setEnabled(self.seitenzahlen.isChecked() and self.rechts.isChecked())
        self.vorschau.update()

    def _male(self, p: QPainter, r) -> None:
        o = self.ergebnis()
        f = p.font(); f.setPixelSize(13); p.setFont(f)
        fm = QFontMetricsF(f)
        p.setPen(QColor("#212529"))
        zeichen = tabfuell.FUELL.get(o["fuell"], ("", "", ""))[1] if o["rechts"] else ""
        y = r.top() + 2
        for i in range(min(o["ebenen"], 7)):
            x = r.left() + 10 * i
            text, zahl = f"Überschrift {i + 1}", str(1 + 2 * i)
            p.drawText(QRectF(x, y, r.right() - x, fm.height()), Qt.AlignLeft | Qt.AlignVCenter, text)
            if o["seitenzahlen"]:
                if o["rechts"]:
                    p.drawText(QRectF(r.left(), y, r.width(), fm.height()), Qt.AlignRight | Qt.AlignVCenter, zahl)
                    if zeichen:
                        von, bis = x + fm.horizontalAdvance(text) + 3, r.right() - fm.horizontalAdvance(zahl) - 3
                        n = max(0, int((bis - von) // fm.horizontalAdvance(zeichen)))
                        p.drawText(QRectF(von, y, bis - von, fm.height()), Qt.AlignLeft | Qt.AlignVCenter, zeichen * n)
                else:
                    p.drawText(QRectF(x + fm.horizontalAdvance(text + " "), y, r.width(), fm.height()), Qt.AlignLeft | Qt.AlignVCenter, zahl)
            y += fm.height() + 6


class IndexeintragDialog(QDialog):
    """Haupt- und Untereintrag mit Sortierung, Optionen (Querverweis „Siehe“, aktuelle Seite, Seitenbereich über eine Textmarke),
    Seitenzahlenformat fett/kursiv; „Markieren“, „Alles markieren“, „Schließen“. Meldet jeden Klick mit ``markieren``."""

    markieren = Signal(object, bool)

    def __init__(self, parent=None, vorschlag: str = "", marken: list[str] | None = None, auswahl: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Indexeintrag festlegen")
        v = QVBoxLayout(self)

        def feld(name, text=""):
            e = QLineEdit(text); e.setMinimumHeight(34); e.setMinimumWidth(130); e.setAccessibleName(name)
            return e
        index = QGroupBox("Index"); g = QGridLayout(index); g.setHorizontalSpacing(10)
        self.haupt, self.lesung = feld("Haupteintrag", vorschlag), feld("Sortieren als (Haupteintrag)")
        self.unter, self.lesung_unter = feld("Untereintrag"), feld("Sortieren als (Untereintrag)")
        g.addWidget(_titel("Haupteintrag (&e):", self.haupt), 0, 0); g.addWidget(self.haupt, 0, 1)
        g.addWidget(_titel("Sortieren als (&H):", self.lesung), 0, 2); g.addWidget(self.lesung, 0, 3)
        g.addWidget(_titel("Untereintrag (&S):", self.unter), 1, 0); g.addWidget(self.unter, 1, 1)
        g.addWidget(_titel("Sortieren als (&g):", self.lesung_unter), 1, 2); g.addWidget(self.lesung_unter, 1, 3)
        v.addWidget(index)

        opt = QGroupBox("Optionen"); og = QGridLayout(opt)
        self.art = QButtonGroup(self)
        self.r_siehe, self.r_seite, self.r_bereich = (QRadioButton("Querverweis (&r):"), QRadioButton("Aktuelle Seite (&p)"),
                                                      QRadioButton("Seitenbereich (&n)"))
        for i, r in enumerate((self.r_siehe, self.r_seite, self.r_bereich)):
            self.art.addButton(r, i)
        self.r_seite.setChecked(True)
        self.siehe = feld("Querverweis"); self.siehe.setPlaceholderText("Siehe")
        self.marke = QComboBox(); self.marke.addItems(marken or []); self.marke.setMinimumHeight(34); self.marke.setAccessibleName("Textmarke")
        self.marke_titel = _titel("Textmarke:", self.marke)
        og.addWidget(self.r_siehe, 0, 0); og.addWidget(self.siehe, 0, 1, 1, 2)
        og.addWidget(self.r_seite, 1, 0, 1, 3)
        og.addWidget(self.r_bereich, 2, 0, 1, 3)
        og.addWidget(self.marke_titel, 3, 0, Qt.AlignRight); og.addWidget(self.marke, 3, 1, 1, 2)
        og.setColumnStretch(2, 1)
        v.addWidget(opt)

        fmt = QGroupBox("Seitenzahlenformat"); fv = QVBoxLayout(fmt)
        self.fett, self.kursiv = QCheckBox("&Fett"), QCheckBox("&Kursiv")
        fv.addWidget(self.fett); fv.addWidget(self.kursiv)
        v.addWidget(fmt)

        self.knopf_markieren, self.knopf_alle = QPushButton("Markieren (&M)"), QPushButton("Alles markieren (&a)")
        self.knopf_alle.setEnabled(auswahl and bool(vorschlag))       # nur mit markiertem Text: jede Stelle mit demselben Text
        self.knopf_markieren.clicked.connect(lambda: self._melden(False))
        self.knopf_alle.clicked.connect(lambda: self._melden(True))
        zeile = knopfzeile(self, self.knopf_markieren, self.knopf_alle, schliessen=True)
        v.addWidget(zeile)
        self.knopf_markieren.setDefault(True); zeile.ok.setDefault(False)
        self.art.idToggled.connect(lambda _i, _an: self._auffrischen())
        self.haupt.textChanged.connect(lambda _t: self._auffrischen())
        self._auffrischen()

    def eintrag(self) -> Eintrag:
        return Eintrag(self.haupt.text().strip(), self.unter.text().strip(), self.lesung.text().strip(), self.lesung_unter.text().strip(),
                       siehe=self.siehe.text().strip() if self.r_siehe.isChecked() else "",
                       marke=self.marke.currentText() if self.r_bereich.isChecked() else "",
                       fett=self.fett.isChecked(), kursiv=self.kursiv.isChecked())

    def _melden(self, alle: bool) -> None:
        self.markieren.emit(self.eintrag(), alle)

    def _auffrischen(self) -> None:
        self.siehe.setEnabled(self.r_siehe.isChecked())
        bereich = self.r_bereich.isChecked() and self.marke.count() > 0
        self.marke.setEnabled(bereich); self.marke_titel.setEnabled(bereich)
        self.r_bereich.setEnabled(self.marke.count() > 0)
        self.knopf_markieren.setEnabled(bool(self.haupt.text().strip()))
