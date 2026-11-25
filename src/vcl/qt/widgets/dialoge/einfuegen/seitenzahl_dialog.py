"""Seitenzahl dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QButtonGroup, QComboBox, QDialog, QLabel, QSpinBox
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_KNOPF
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster_hilfen import _titel


class SeitenzahlDialog(PanelFaehig, QDialog):
    """„Seitenzahl einfügen“ wie in der Vorlage: Format und Position, Kapitelnummer einbeziehen (Formatvorlage, Trennzeichen, Beispiele),
    Seitennummerierung (fortsetzen oder beginnen mit) und „Übernehmen für“ (gesamtes Dokument, von aktueller Seite, aktueller Abschnitt).

        d = SeitenzahlDialog(parent, page)     # page: Einrichtung des aktuellen Abschnitts (Vorbelegung)
        if d.exec(): d.werte()   # {"ort", "ausrichtung", "muster", "format", "start", "kapitel": (Ebene, Zeichen), "bereich"}
    """

    BEREICHE = (("dokument", "Gesamtes &Dokument"), ("seite", "Von aktueller Seite (&p)"), ("abschnitt", "Aktueller Abschnit&t"))

    def __init__(self, parent=None, page=None):
        super().__init__(parent)
        from core.dokument.kopf_fusszeilen import seitenzahl as SZ
        self.setWindowTitle("Seitenzahl einfügen")
        v = _spalte("standard", self)
        g = FormularGitter()                                                # passt sich der Breite an (Seitenleiste), nichts wird abgeschnitten
        self.muster = Auswahlfeld(); self.position = Auswahlfeld()
        for muster, fmt, t in SZ.MUSTER:
            self.muster.addItem(t, (muster, fmt))
        for ort, ausr, t in SZ.POSITIONEN:
            self.position.addItem(t, (ort, ausr))
        self.position.setCurrentIndex(6)                                    # „Unten zentriert“
        for text, feld in (("&Format:", self.muster), ("Position (&s):", self.position)):
            feld.setMinimumHeight(HOEHE_KNOPF)
            g.zeile(_titel(text, feld), feld)
        self.kapitel = UmbruchSchalter("&Kapitelnummer einbeziehen"); g.breit(self.kapitel)
        self.ebene = Auswahlfeld(); self.trenner = Auswahlfeld()
        for n in range(1, 10):
            self.ebene.addItem(f"Überschrift {n}", n)
        for z, t, _docx in SZ.TRENNER:
            self.trenner.addItem(t, z)
        self.beispiel = QLabel()
        self._kapitel_teile = []
        for text, feld in (("Kapitel beginnt mit Formatvorlage (&C):", self.ebene), ("Trennzeichen &verwenden:", self.trenner),
                           ("Beispiele:", self.beispiel)):
            if isinstance(feld, QComboBox):
                feld.setMinimumHeight(HOEHE_KNOPF)
            t = _titel(text, feld)
            g.zeile(t, feld)
            self._kapitel_teile += [t, feld]
        g.breit(abschnittstitel("Seitennummerierung"))
        self.fortsetzen = option("standard", "Fortsetzen vom vorherigen Abschnitt (&o)"); self.beginnen = option("standard", "&Beginnen mit:")
        self.start = QSpinBox(); self.start.setRange(1, 9999); self.start.setMinimumHeight(HOEHE_KNOPF)
        self.start.setAccessibleName("Beginnen mit")
        g.breit(self.fortsetzen)
        z = FlussLayout(6); z.addWidget(self.beginnen); z.addWidget(self.start); g.breit(z)
        g.breit(abschnittstitel("Übernehmen für"))
        self.bereich = QButtonGroup(self)
        u = FlussLayout(10)
        for i, (_k, t) in enumerate(self.BEREICHE):
            r = option("standard", t, gruppe=self.bereich, nummer=i); u.addWidget(r)
        g.breit(u)
        v.addLayout(g)
        v.addStretch(1)
        self.bereich.button(0).setChecked(True)
        fussleiste(self, v)
        if page is not None:                                                  # Vorbelegung aus der Einrichtung
            for i, (_m, fmt, _t) in enumerate(SZ.MUSTER):
                if fmt == page.seiten_format:
                    self.muster.setCurrentIndex(i); break
            self.kapitel.setChecked(bool(page.kapitel_ebene))
            self.ebene.setCurrentIndex(max(0, (page.kapitel_ebene or 1) - 1))
            self.trenner.setCurrentIndex(max(0, self.trenner.findData(page.kapitel_trenner)))
            if page.seiten_start > 0:
                self.beginnen.setChecked(True); self.start.setValue(page.seiten_start)
        if not self.beginnen.isChecked():
            self.fortsetzen.setChecked(True)
        self.kapitel.toggled.connect(self._zustand); self.beginnen.toggled.connect(self._zustand)
        self.trenner.currentIndexChanged.connect(self._zustand)
        self._zustand()

    def _zustand(self, *_a) -> None:
        for w in self._kapitel_teile:
            w.setEnabled(self.kapitel.isChecked())
        tr = self.trenner.currentData()
        self.beispiel.setText(f"1{tr}1, 1{tr}A")
        self.start.setEnabled(self.beginnen.isChecked())

    def werte(self) -> dict:
        muster, fmt = self.muster.currentData()
        ort, ausr = self.position.currentData()
        return {"ort": ort, "ausrichtung": ausr, "muster": muster, "format": fmt,
                "start": self.start.value() if self.beginnen.isChecked() else 0,
                "kapitel": (self.ebene.currentData() if self.kapitel.isChecked() else 0, self.trenner.currentData()),
                "bereich": self.BEREICHE[self.bereich.checkedId()][0]}
