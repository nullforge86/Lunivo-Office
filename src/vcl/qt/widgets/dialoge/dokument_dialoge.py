from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QPlainTextEdit, QSpinBox, QWidget
from core.dokument.abschnitte.seite import HeaderFooter, PageSettings
from writer.anbindung.seite import paper_mm
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import spin as _spin
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste, knopfzeile
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld


class PageSetupDialog(PanelFaehig, QDialog):
    def __init__(self, page: PageSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seite einrichten")
        self.page = page.copy()
        inhalt = QWidget(); form = FormularGitter(inhalt)
        self.paper = Auswahlfeld(); self.paper.addItems(list(paper_mm()) + ["Benutzerdefiniert"])
        self.paper.setCurrentText(page.paper_name())
        self.orient = Auswahlfeld(); self.orient.addItems(["Hochformat", "Querformat"])
        self.orient.setCurrentIndex(1 if page.landscape else 0)
        self.top = _spin(page.margin_top_mm); self.bottom = _spin(page.margin_bottom_mm)
        self.left = _spin(page.margin_left_mm); self.right = _spin(page.margin_right_mm)
        form.reihe(("Papierformat", self.paper), ("Ausrichtung", self.orient))
        form.breit(abschnittstitel("Ränder"))
        form.reihe(("Oben", self.top), ("Unten", self.bottom))
        form.reihe(("Links", self.left), ("Rechts", self.right))
        form.breit(abschnittstitel("Spalten"))
        self.spalten = QSpinBox(); self.spalten.setRange(1, 4); self.spalten.setValue(max(1, int(page.spalten)))
        self.spalten_abstand = _spin(page.spalten_abstand_mm, 2, 40)
        self.spalten_linie = haken("standard", "Linie zwischen den Spalten", an=page.spalten_linie)
        form.reihe(("Spalten", self.spalten), ("Abstand der Spalten", self.spalten_abstand))
        form.breit(self.spalten_linie)
        bb = knopfzeile(self)
        lay = _spalte("standard", self); lay.addWidget(inhalt); lay.addWidget(bb)

    def result_page(self) -> PageSettings:
        p = self.page
        if self.paper.currentText() in paper_mm():
            p.width_mm, p.height_mm = sorted(paper_mm()[self.paper.currentText()])
        else:
            p.width_mm, p.height_mm = sorted((p.width_mm, p.height_mm))
        p.set_orientation(self.orient.currentIndex() == 1)
        p.margin_top_mm, p.margin_bottom_mm = self.top.value(), self.bottom.value()
        p.margin_left_mm, p.margin_right_mm = self.left.value(), self.right.value()
        p.spalten, p.spalten_abstand_mm, p.spalten_linie = self.spalten.value(), self.spalten_abstand.value(), self.spalten_linie.isChecked()
        return p

    def accept(self) -> None:
        p = self.result_page()
        if p.margin_left_mm + p.margin_right_mm >= p.width_mm - 20 or \
                p.margin_top_mm + p.margin_bottom_mm >= p.height_mm - 20:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Seite einrichten", "Die Ränder lassen zu wenig Platz für Text.")
            return
        super().accept()


class HeaderFooterDialog(PanelFaehig, QDialog):
    def __init__(self, title: str, hf: HeaderFooter, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.text = QPlainTextEdit(hf.text)
        self.text.setPlaceholderText("Text eingeben. {PAGE} = Seitenzahl, {PAGES} = Seitenanzahl")
        self.align = Auswahlfeld(); self.align.addItems(["Links", "Zentriert", "Rechts", "Außen", "Innen"])
        self.align.setCurrentIndex({"left": 0, "center": 1, "right": 2, "aussen": 3, "innen": 4}.get(hf.align, 1))
        b = knopf("standard", "Seitenzahl einfügen")
        b.clicked.connect(lambda: self.text.insertPlainText("{PAGE}"))
        lay = _spalte("standard", self)
        lay.addWidget(self.text)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        g.zeile("Ausrichtung", self.align); g.breit(b)
        lay.addWidget(inhalt)
        bb = knopfzeile(self)
        lay.addWidget(bb)

    def value(self) -> HeaderFooter:
        return HeaderFooter(self.text.toPlainText().strip("\n"),
                            ["left", "center", "right", "aussen", "innen"][self.align.currentIndex()])


class BildZuschneidenDialog(PanelFaehig, QDialog):
    """„Bild zuschneiden“: wie viele Bildpunkte links, oben, rechts und unten abgeschnitten werden."""

    def __init__(self, parent):
        super().__init__(parent)
        from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
        self.setWindowTitle("Bild zuschneiden")
        v = _spalte("standard", self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        self.felder: dict[str, QSpinBox] = {}
        for name in ("Links", "Oben", "Rechts", "Unten"):
            w = QSpinBox(); w.setRange(0, 5000); w.setSuffix(" px"); self.felder[name] = w
        g.reihe(("Links abschneiden", self.felder["Links"]), ("Oben abschneiden", self.felder["Oben"]),
                ("Rechts abschneiden", self.felder["Rechts"]), ("Unten abschneiden", self.felder["Unten"]))
        v.addWidget(inhalt)
        fussleiste(self, v)

    def werte(self) -> tuple[int, int, int, int]:
        """(links, oben, rechts, unten) in Bildpunkten."""
        f = self.felder
        return f["Links"].value(), f["Oben"].value(), f["Rechts"].value(), f["Unten"].value()
