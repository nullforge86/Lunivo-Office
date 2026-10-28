"""Fenster des Reiters Verweise nach den WPS-Vorlagen: „Inhaltsverzeichnis“, „Indexeintrag festlegen“, „Beschriftung“ (mit
„Beschriftungsnummerierung“) und „Querverweis“.

    d = InhaltsverzeichnisDialog(parent, {"fuell": "punkt", "ebenen": 3, …})   # if d.exec(): d.ergebnis() → dict
    d = IndexeintragDialog(parent, "Apfel", ["Marke1"], auswahl=True)          # d.markieren(Eintrag, alle) bei jedem Klick
    d = BeschriftungDialog(parent, eigene, naechste, objekt=True)              # if d.exec(): d.ergebnis(), d.eigene
    d = QuerverweisDialog(parent, ziele)                                        # d.einfuegen(ziel, wie, link, oben_unten)

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


class NummerierungDialog(QDialog):
    """„Beschriftungsnummerierung“: Schreibweise der Nummer. Kapitelnummern kennt Lunivo noch nicht (grau)."""

    def __init__(self, parent=None, zahl: str = "arabisch"):
        super().__init__(parent)
        from lunivo_writer.editor import zahlformat as Z
        from lunivo_writer.editor.verweise import SEQ_FORMAT
        self.setWindowTitle("Beschriftungsnummerierung")
        v = QVBoxLayout(self)
        self.format = QComboBox(); self.format.setMinimumHeight(34); self.format.setAccessibleName("Format")
        for k, t in Z.TYPEN:
            if k in SEQ_FORMAT:
                self.format.addItem(t, k)
        self.format.setCurrentIndex(max(0, self.format.findData(zahl)))
        z = QHBoxLayout(); z.addWidget(_titel("&Format:", self.format)); z.addWidget(self.format, 1); v.addLayout(z)
        kapitel = QCheckBox("&Kapitelnummer einbeziehen"); kapitel.setEnabled(False); v.addWidget(kapitel)
        fussleiste(self, v)

    def zahl(self) -> str:
        return self.format.currentData()


class BeschriftungDialog(QDialog):
    """„Beschriftung“ wie die Vorlage: Feld mit „Tabelle 1“ zum Weiterschreiben, Bezeichnung, Position (nur bei markiertem Objekt),
    „Bezeichnung nicht in der Beschriftung verwenden“, Neues Etikett / Bezeichnung löschen / Nummerierung.

    ``naechste(label, zahl)`` liefert die Nummer der neuen Beschriftung. ``ergebnis()`` → label, nach, oben, ohne, zahl; ``eigene``
    ist die (geänderte) Liste eigener Bezeichnungen, die der Aufrufer sich merkt."""

    def __init__(self, parent=None, eigene: list[str] | None = None, naechste=None, objekt: bool = False, label: str = "Abbildung"):
        super().__init__(parent)
        from lunivo_writer.editor.zusatz import BESCHRIFTUNGEN
        self.setWindowTitle("Beschriftung")
        self._naechste = naechste or (lambda _l, _z: "1")
        self.eigene = list(eigene or [])
        self.zahl = "arabisch"
        self._vorne = ""
        v = QVBoxLayout(self)
        self.text = QLineEdit(); self.text.setMinimumHeight(34); self.text.setMinimumWidth(380); self.text.setAccessibleName("Beschriftung")
        v.addWidget(_titel("&Beschriftung:", self.text)); v.addWidget(self.text)
        g = QGridLayout(); g.setHorizontalSpacing(10)
        self.label = QComboBox(); self.label.setMinimumHeight(34); self.label.setAccessibleName("Bezeichnung")
        self.label.addItems(list(BESCHRIFTUNGEN) + [x for x in self.eigene if x not in BESCHRIFTUNGEN])
        self.label.setCurrentText(label)
        self.pos = QComboBox(); self.pos.addItems(["Unter dem ausgewählten Element", "Über dem ausgewählten Element"])
        self.pos.setMinimumHeight(34); self.pos.setEnabled(objekt); self.pos.setAccessibleName("Position")
        g.addWidget(_titel("B&ezeichnung:", self.label), 0, 0); g.addWidget(self.label, 0, 1)
        g.addWidget(_titel("&Position:", self.pos), 1, 0); g.addWidget(self.pos, 1, 1)
        g.setColumnStretch(1, 1)
        v.addLayout(g)
        self.ohne = QCheckBox("Be&zeichnung nicht in der Beschriftung verwenden"); v.addWidget(self.ohne)
        z = QHBoxLayout()
        self.neu, self.loeschen, self.nummerierung = QPushButton("Neues &Etikett…"), QPushButton("Bezeichnung &löschen"), QPushButton("N&ummerierung…")
        for k in (self.neu, self.loeschen, self.nummerierung):
            k.setMinimumHeight(36); z.addWidget(k)
        v.addLayout(z)
        fussleiste(self, v)
        self.neu.clicked.connect(self._neu); self.loeschen.clicked.connect(self._loeschen); self.nummerierung.clicked.connect(self._nummerierung)
        self.label.currentTextChanged.connect(lambda _t: self._vorspann())
        self.ohne.toggled.connect(lambda _a: self._vorspann())
        self._vorspann()

    def _vorspann(self) -> None:
        """Den Anfang „Tabelle 1“ im Feld erneuern, Geschriebenes dahinter behalten."""
        rest = self.text.text()[len(self._vorne):] if self.text.text().startswith(self._vorne) else ""
        nr = self._naechste(self.label.currentText(), self.zahl)
        self._vorne = nr if self.ohne.isChecked() else f"{self.label.currentText()} {nr}"
        self.text.setText(self._vorne + rest)
        from lunivo_writer.editor.zusatz import BESCHRIFTUNGEN
        self.loeschen.setEnabled(self.label.currentText() not in BESCHRIFTUNGEN)

    def _neu(self) -> None:
        from PySide6.QtWidgets import QInputDialog
        t, ok = QInputDialog.getText(self, "Neue Bezeichnung", "&Bezeichnung:")
        t = " ".join(t.split())
        if ok and t:
            if self.label.findText(t) < 0:
                self.label.addItem(t); self.eigene.append(t)
            self.label.setCurrentText(t)

    def _loeschen(self) -> None:
        t = self.label.currentText()
        if t in self.eigene:
            self.eigene.remove(t)
            self.label.removeItem(self.label.currentIndex())

    def _nummerierung(self) -> None:
        d = NummerierungDialog(self, self.zahl)
        if d.exec():
            self.zahl = d.zahl()
            self._vorspann()

    def ergebnis(self) -> dict:
        t = self.text.text()
        nach = t[len(self._vorne):] if t.startswith(self._vorne) else (": " + t.strip() if t.strip() else "")
        return {"label": self.label.currentText(), "nach": nach, "oben": self.pos.isEnabled() and self.pos.currentIndex() == 1,
                "ohne": self.ohne.isChecked(), "zahl": self.zahl}


class QuerverweisDialog(QDialog):
    """„Querverweis“ wie die Vorlage: Verweistyp, Verweisen auf, „Als Hyperlink einfügen“, „Oben/unten einschließen“, die Liste
    „Für welche …“; „Einfügen“ meldet ``einfuegen(ziel, wie, link, oben_unten)`` und lässt das Fenster offen, „Abbrechen“ wird
    danach zu „Schließen“."""

    einfuegen = Signal(dict, str, bool, bool)

    _FUER = {"Nummeriertes Element": "Für welches nummerierte Element:", "Überschrift": "Für welche Überschrift:",
             "Textmarke": "Für welche Textmarke:", "Fußnote": "Für welche Fußnote:", "Endnote": "Für welche Endnote:"}

    def __init__(self, parent=None, ziele: list[dict] | None = None):
        super().__init__(parent)
        from PySide6.QtWidgets import QListWidget, QListWidgetItem
        from lunivo_writer.editor import verweise as VW
        self._QListWidgetItem = QListWidgetItem
        self.ziele = list(ziele or [])
        self.setWindowTitle("Querverweis")
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(10)
        self.art = QComboBox(); self.art.addItems(VW.VERWEISTYPEN); self.art.setMinimumHeight(34); self.art.setAccessibleName("Verweistyp")
        self.auf = QComboBox(); self.auf.setMinimumHeight(34); self.auf.setMinimumWidth(200); self.auf.setAccessibleName("Verweisen auf")
        g.addWidget(_titel("&Verweistyp:", self.art), 0, 0); g.addWidget(_titel("Verweisen &auf:", self.auf), 0, 1)
        g.addWidget(self.art, 1, 0); g.addWidget(self.auf, 1, 1)
        self.link = QCheckBox("Als &Hyperlink einfügen"); self.link.setChecked(True)
        self.oben_unten = QCheckBox("Oben/unten einschließen (&O)")
        g.addWidget(self.link, 2, 0); g.addWidget(self.oben_unten, 2, 1)
        v.addLayout(g)
        self.liste = QListWidget(); self.liste.setMinimumHeight(190); self.liste.setAccessibleName("Ziel")
        self.fuer = _titel("", self.liste)
        v.addWidget(self.fuer); v.addWidget(self.liste, 1)
        self.zeile = knopfzeile(self, ok_text="Einfügen", bei_ok=self._melden)
        v.addWidget(self.zeile)
        self.art.currentTextChanged.connect(self._art_gewaehlt)
        self.auf.currentIndexChanged.connect(lambda _i: self._auffrischen())
        self.liste.currentRowChanged.connect(lambda _i: self._auffrischen())
        self.liste.itemDoubleClicked.connect(lambda _it: self._melden())
        self._art_gewaehlt(self.art.currentText())

    def _art_gewaehlt(self, art: str) -> None:
        from lunivo_writer.editor import verweise as VW
        self.auf.clear()
        for k, t in VW.verweisen_auf(art):
            self.auf.addItem(t, k)
        self.fuer.setText(self._FUER.get(art, f"Für welche Beschriftung „{art}“:"))
        self.liste.clear()
        for z in self.ziele:
            if z["art"] == art:
                it = self._QListWidgetItem(z["text"][:90]); it.setData(Qt.UserRole, z); self.liste.addItem(it)
        self._auffrischen()

    def _auffrischen(self) -> None:
        self.oben_unten.setEnabled(self.auf.currentData() in ("seite", "nummer"))
        self.zeile.ok.setEnabled(self.liste.currentItem() is not None)

    def ergebnis(self):
        it = self.liste.currentItem()
        return (it.data(Qt.UserRole) if it else None), self.auf.currentData()

    def _melden(self) -> None:
        ziel, wie = self.ergebnis()
        if ziel is None:
            return
        self.einfuegen.emit(ziel, wie, self.link.isChecked(), self.oben_unten.isEnabled() and self.oben_unten.isChecked())
        self.zeile.abbrechen.setText("Schließen")
