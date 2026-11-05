"""Kleine Dialoge: Seite einrichten, Absatz, Kopf-/Fußzeile, Tabelle, Suchen/Ersetzen."""
from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QLabel, QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from lunivo_writer.models.page import PAPER_MM, HeaderFooter, PageSettings
from lunivo_writer.ui.baukasten.mass_feld import EINHEITEN, MassSpin as _MassSpin, einheit, set_einheit, spin as _spin  # noqa: F401


from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter, abschnittstitel
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste, knopfzeile
from lunivo_writer.ui.baukasten.mass import RAND_KEIN
def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


class PageSetupDialog(PanelFaehig, QDialog):
    def __init__(self, page: PageSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seite einrichten")
        self.page = page.copy()
        inhalt = QWidget(); form = FormularGitter(inhalt)
        self.paper = QComboBox(); self.paper.addItems(list(PAPER_MM) + ["Benutzerdefiniert"])
        self.paper.setCurrentText(page.paper_name())
        self.orient = QComboBox(); self.orient.addItems(["Hochformat", "Querformat"])
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
        self.spalten_linie = QCheckBox("Linie zwischen den Spalten"); self.spalten_linie.setChecked(page.spalten_linie)
        form.reihe(("Spalten", self.spalten), ("Abstand der Spalten", self.spalten_abstand))
        form.breit(self.spalten_linie)
        bb = knopfzeile(self)
        lay = QVBoxLayout(self); lay.addWidget(inhalt); lay.addWidget(bb)

    def result_page(self) -> PageSettings:
        p = self.page
        if self.paper.currentText() in PAPER_MM:
            p.width_mm, p.height_mm = sorted(PAPER_MM[self.paper.currentText()])
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
        self.align = QComboBox(); self.align.addItems(["Links", "Zentriert", "Rechts", "Außen", "Innen"])
        self.align.setCurrentIndex({"left": 0, "center": 1, "right": 2, "aussen": 3, "innen": 4}.get(hf.align, 1))
        b = QPushButton("Seitenzahl einfügen")
        b.clicked.connect(lambda: self.text.insertPlainText("{PAGE}"))
        lay = QVBoxLayout(self)
        lay.addWidget(self.text)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        g.zeile("Ausrichtung", self.align); g.breit(b)
        lay.addWidget(inhalt)
        bb = knopfzeile(self)
        lay.addWidget(bb)

    def value(self) -> HeaderFooter:
        return HeaderFooter(self.text.toPlainText().strip("\n"),
                            ["left", "center", "right", "aussen", "innen"][self.align.currentIndex()])


class TableDialog(PanelFaehig, QDialog):
    """„Tabelle einfügen“ wie in der Vorlage: Tabellengröße, Einstellung für optimale Breite, Abmessungen für neue Tabellen speichern.
    ``vorgabe``: (Spalten, Zeilen) aus den Einstellungen; ``speichern.isChecked()`` sagt dem Aufrufer, ob er sie merken soll."""

    def __init__(self, parent=None, vorgabe: tuple[int, int] = (5, 2)):
        from PySide6.QtWidgets import QButtonGroup, QRadioButton
        super().__init__(parent)
        self.setWindowTitle("Tabelle einfügen")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Tabellengröße"))
        self.cols = QSpinBox(); self.cols.setRange(1, 63); self.cols.setValue(vorgabe[0])
        self.rows = QSpinBox(); self.rows.setRange(1, 500); self.rows.setValue(vorgabe[1])
        gi = QWidget(); g = FormularGitter(gi)
        for feld in (self.cols, self.rows):
            pass
        g.reihe((_titel("Spaltenan&zahl:", self.cols), self.cols), (_titel("Zeilenan&zahl:", self.rows), self.rows))
        lay.addWidget(gi)
        lay.addWidget(QLabel("Einstellung für optimale Breite"))
        self.fest = QRadioButton("Feste Spalten&breite:")
        self.auto = QRadioButton("Spaltenbreite automatisch anpassen (&S)"); self.auto.setChecked(True)
        gruppe = QButtonGroup(self); gruppe.addButton(self.fest); gruppe.addButton(self.auto)
        self.breite = _spin(30.0, 2.0, 500.0)
        self.breite.setAccessibleName("Feste Spaltenbreite")
        zi = QWidget(); z = FormularGitter(zi)
        z.reihe(("", self.fest), ("", self.breite)); z.breit(self.auto)
        lay.addWidget(zi)
        self.fest.toggled.connect(self.breite.setEnabled); self.breite.setEnabled(False)
        self.speichern = UmbruchSchalter("Ab&messungen für neue Tabellen speichern")
        lay.addWidget(self.speichern)
        lay.addStretch(1)
        lay.addWidget(knopfzeile(self))

    def spaltenbreite_px(self) -> float | None:
        """Feste Breite jeder Spalte in Bildpunkten; None: automatisch (Seitenbreite)."""
        return self.breite.value() * 96 / 25.4 if self.fest.isChecked() else None


class BildGroesseDialog(PanelFaehig, QDialog):
    def __init__(self, breite_px: float, hoehe_px: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bildgröße")
        self.verh = (hoehe_px / breite_px) if breite_px else 1.0
        self.b = _spin(breite_px * 25.4 / 96, 1, 2000)
        self.h = _spin(hoehe_px * 25.4 / 96, 1, 2000)
        self.fest = QCheckBox("Seitenverhältnis beibehalten"); self.fest.setChecked(True)
        self._sperre = False
        self.b.valueChanged.connect(self._b)
        self.h.valueChanged.connect(self._h)
        inhalt = QWidget(); form = FormularGitter(inhalt)
        form.reihe(("Breite", self.b), ("Höhe", self.h)); form.breit(self.fest)
        bb = knopfzeile(self)
        lay = QVBoxLayout(self); lay.addWidget(inhalt); lay.addWidget(bb)

    def _b(self, v):
        if self.fest.isChecked() and not self._sperre:
            self._sperre = True; self.h.setValue(v * self.verh); self._sperre = False

    def _h(self, v):
        if self.fest.isChecked() and not self._sperre and self.verh:
            self._sperre = True; self.b.setValue(v / self.verh); self._sperre = False

    def breite_px(self): return self.b.value() * 96 / 25.4
    def hoehe_px(self): return self.h.value() * 96 / 25.4


class ZoomDialog(PanelFaehig, QDialog):
    """Ansicht ▸ Zoom: feste Stufen, Seitenbreite, ganze Seite oder eigener Wert."""
    STUFEN = (200, 150, 100, 75, 50, 25)

    def __init__(self, parent, aktuell: float):
        super().__init__(parent)
        from PySide6.QtWidgets import QButtonGroup, QRadioButton, QSpinBox
        self.setWindowTitle("Zoom")
        lay = QVBoxLayout(self)
        raster = QWidget(); fl = FlussLayout(10); raster.setLayout(fl); fl.setContentsMargins(*RAND_KEIN)
        self.gruppe = QButtonGroup(self)
        self._art: dict[int, tuple[str, float]] = {}
        eintraege = [(f"{n} %", ("wert", n / 100)) for n in self.STUFEN] + \
                    [("Seitenbreite", ("breite", 0)), ("Ganze Seite", ("seite", 0))]
        for i, (text, art) in enumerate(eintraege):
            r = QRadioButton(text)
            self.gruppe.addButton(r, i)
            self._art[i] = art
            fl.addWidget(r)
            if art[0] == "wert" and abs(art[1] - aktuell) < 0.005:
                r.setChecked(True)
        eigen = QRadioButton("Eigener Wert:")
        self.gruppe.addButton(eigen, 100)
        self.spin = QSpinBox(); self.spin.setRange(10, 500); self.spin.setSuffix(" %")
        self.spin.setValue(int(round(aktuell * 100)))
        self.spin.valueChanged.connect(lambda _: eigen.setChecked(True))
        lay.addWidget(raster)
        ei = QWidget(); zeile = FormularGitter(ei); zeile.reihe(("", eigen), ("", self.spin))
        lay.addWidget(ei)
        if self.gruppe.checkedId() < 0:
            eigen.setChecked(True)
        bb = knopfzeile(self)
        lay.addWidget(bb)

    def ergebnis(self) -> tuple[str, float]:
        i = self.gruppe.checkedId()
        if i == 100 or i not in self._art:
            return "wert", self.spin.value() / 100
        return self._art[i]


from lunivo_writer.ui.dialogs.wasserzeichen_fenster import WasserzeichenDialog  # noqa: E402,F401  (früher hier)


class TabellenEigenschaftenDialog(PanelFaehig, QDialog):
    """„Tabelleneigenschaften“ (Reiter „Tabelle“ und „Spalte und Zelle“). Ändert die Tabelle nicht selbst; der Aufrufer liest ``werte()``
    (Format wie ``editor.tabelleneigenschaften.lesen``) oder die alten Felder breite/ausr/rand/pad/kopf.

    ``werte`` (optional) überschreibt die Einzelargumente; fehlende Schlüssel stammen aus ``VORGABE``."""
    AUSRICHTUNGEN = ("Links", "Zentriert", "Rechts")
    _AUSR = ("links", "mitte", "rechts")
    _PT_MM = 25.4 / 72
    _PX_MM = 25.4 / 96

    def __init__(self, parent, breite_prozent: int = 100, ausrichtung: int = 0, rand: float = 1.0, abstand: float = 4.0,
                 kopfzeile: bool = False, *, werte: dict | None = None):
        super().__init__(parent)
        from lunivo_writer.editor.tabelleneigenschaften import VORGABE
        from lunivo_writer.ui.baukasten.formular_gitter import AngepassteReiter, FormularGitter, UmbruchSchalter, abschnittstitel
        from lunivo_writer.ui.baukasten.mass_feld import EinheitFeld
        self.setWindowTitle("Tabelleneigenschaften")
        v = QVBoxLayout(self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        # ---- Tabelle
        s = QWidget(); g = FormularGitter(s)
        self.art = QComboBox()
        for k, n in (("auto", "Automatisch"), ("prozent", "Prozent des Textbereichs"), ("fest", "Feste Breite")):
            self.art.addItem(n, k)
        self.breite = QSpinBox(); self.breite.setRange(10, 100); self.breite.setSuffix(" %")
        self.fest = EinheitFeld(0.0, 5.0, 1000.0, ("mm", "cm", "in"), "cm")
        self.ausr = QComboBox(); self.ausr.addItems(self.AUSRICHTUNGEN)
        g.zeile("Breite", self.art)
        g.reihe(("Prozent", self.breite), ("Feste Breite", self.fest))
        g.zeile("Ausrichtung", self.ausr)
        g.breit(abschnittstitel("Zellen"))
        self.rand = QDoubleSpinBox(); self.rand.setRange(0, 15); self.rand.setDecimals(3); self.rand.setSingleStep(0.25); self.rand.setSuffix(" pt")
        self.pad = QDoubleSpinBox(); self.pad.setRange(0, 100); self.pad.setDecimals(3); self.pad.setSuffix(" px")
        self.abstand = EinheitFeld(0.0, 0.0, 50.0, ("mm", "cm", "pt"), "mm")
        g.reihe(("Rahmenstärke", self.rand), ("Innenabstand", self.pad))
        g.zeile("Zellenabstand", self.abstand)
        self.kopf = UmbruchSchalter("Erste Zeile ist Kopfzeile (wiederholt sich auf jeder Seite)"); self.kopf.setChecked(kopfzeile)
        g.breit(self.kopf)
        self.reiter.addTab(s, "Tabelle")
        # ---- Spalte und Zelle (die der Schreibmarke)
        z = QWidget(); zg = FormularGitter(z)
        self.sp_fest = UmbruchSchalter("Bevorzugte Breite der Spalte"); self.spalte = EinheitFeld(0.0, 5.0, 1000.0, ("mm", "cm", "in"), "cm")
        zg.breit(abschnittstitel("Spalte")); zg.breit(self.sp_fest); zg.zeile("Breite", self.spalte)
        zg.breit(abschnittstitel("Zelle"))
        self.senkrecht = QComboBox()
        for k, n in (("oben", "Oben"), ("mitte", "Mittig"), ("unten", "Unten")):
            self.senkrecht.addItem(n, k)
        zg.zeile("Senkrechte Ausrichtung", self.senkrecht)
        self.reiter.addTab(z, "Spalte und Zelle")
        fussleiste(self, v)
        # ---- Startwerte
        w = {**VORGABE, "breite": float(breite_prozent), "ausr": self._AUSR[max(0, min(2, ausrichtung))],
             "rahmen": rand * self._PT_MM, "innen": abstand * self._PX_MM, **(werte or {})}
        self.setze(w)
        self.art.currentIndexChanged.connect(self._sichtbar); self._sichtbar()

    def setze(self, w: dict) -> None:
        a = w.get("breite_art", "prozent")
        self.art.setCurrentIndex(max(0, self.art.findData(a)))
        if a == "prozent":
            self.breite.setValue(int(round(w["breite"])))
        elif a == "fest":
            self.fest.setValue(w["breite"])
        self.ausr.setCurrentIndex(max(0, self._AUSR.index(w["ausr"]) if w["ausr"] in self._AUSR else 0))
        self.rand.setValue(w["rahmen"] / self._PT_MM); self.pad.setValue(w["innen"] / self._PX_MM)
        self.abstand.setValue(w["abstand"])
        self.sp_fest.setChecked(bool(w["spalte_fest"])); self.spalte.setValue(w["spalte"] or 30.0)
        self.senkrecht.setCurrentIndex(max(0, self.senkrecht.findData(w["senkrecht"])))

    def _sichtbar(self, *_) -> None:
        a = self.art.currentData()
        self.breite.setEnabled(a == "prozent"); self.fest.setEnabled(a == "fest")

    def werte(self) -> dict:
        a = self.art.currentData()
        return {"breite_art": a, "breite": float(self.breite.value()) if a == "prozent" else self.fest.value() if a == "fest" else 0.0,
                "ausr": self._AUSR[self.ausr.currentIndex()], "innen": self.pad.value() * self._PX_MM,
                "abstand": self.abstand.value(), "rahmen": self.rand.value() * self._PT_MM,
                "spalte_fest": self.sp_fest.isChecked(), "spalte": self.spalte.value(), "senkrecht": self.senkrecht.currentData()}


class BildZuschneidenDialog(PanelFaehig, QDialog):
    """„Bild zuschneiden“: wie viele Bildpunkte links, oben, rechts und unten abgeschnitten werden."""

    def __init__(self, parent):
        super().__init__(parent)
        from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter
        self.setWindowTitle("Bild zuschneiden")
        v = QVBoxLayout(self)
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
