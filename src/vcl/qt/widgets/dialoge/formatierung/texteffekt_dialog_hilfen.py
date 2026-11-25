"""Texteffekt dialog hilfen: aus ``vcl.qt.widgets.dialoge.formatierung.texteffekt_dialog`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QScrollArea, QToolButton, QWidget
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FELDHOEHE, FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_FELD, RAND_TEXTEFFEKT_GITTER


FELDBREITE = 128                                                  # Breite der Feldspalte und der Menüs in den Abschnittsköpfen (Vorlage: alles rechtsbündig in einer Spalte)


def seitengitter(widget: QWidget) -> FormularGitter:
    """Das ``FormularGitter`` der Seitenleiste „Formatierung“: Beschriftungen links, alle Felder in einer gleich breiten Spalte rechts."""
    g = FormularGitter(widget)
    g.feldbreite = FELDBREITE
    return g


class _Pfeil(QToolButton):
    """Der Pfeil vor einer Abschnittsüberschrift: schaltet um wie ein Umschaltknopf (``setChecked``, ``toggled``), zeigt aber keinen Knopfrahmen."""
    toggled = Signal(bool)

    def __init__(self):
        super().__init__()
        self._an = False
        self.setAutoRaise(True); self.setArrowType(Qt.RightArrow)
        self.setMinimumHeight(HOEHE_FELD)                                                # Klickfläche: Höhe wie die Felder; die Breite bleibt, sonst ragt die Zeile bei 300 px heraus
        self.clicked.connect(self.toggle)

    def isChecked(self) -> bool:
        return self._an

    def setChecked(self, an: bool) -> None:
        if an != self._an:
            self._an = bool(an)
            self.setArrowType(Qt.DownArrow if self._an else Qt.RightArrow)
            self.toggled.emit(self._an)

    def toggle(self) -> None:
        self.setChecked(not self._an)


class Abschnitt(QWidget):
    """Aufklappbarer Abschnitt: Pfeil und Überschrift in Großbuchstaben links, optional ein Bedienelement rechts (z. B. die Voreinstellung)."""

    def __init__(self, titel: str, rechts: QWidget | None = None):
        super().__init__()
        v = _spalte("standard", self)
        kopf = _reihe("standard")
        self.knopf = _Pfeil()                                            # nur der Pfeil
        self.knopf.setAccessibleName(titel); self.knopf.setToolTip(titel)
        self.titel = abschnittstitel(titel)                              # die Überschrift wie überall (kleine graue Großbuchstaben); ein Klick klappt auf und zu
        self.titel.setCursor(Qt.PointingHandCursor); self.titel.mousePressEvent = lambda e: self.knopf.toggle()
        self.titel.setWordWrap(True)                                     # schmale Seitenleiste: der Titel bricht um, statt das Feld rechts über den Rand zu schieben
        kopf.addWidget(self.knopf); kopf.addWidget(self.titel); kopf.addStretch(1)
        v.addLayout(kopf)
        self.inhalt = QWidget(); self.gitter = seitengitter(self.inhalt); self.gitter.setContentsMargins(*RAND_TEXTEFFEKT_GITTER)
        v.addWidget(self.inhalt); self.inhalt.setVisible(False)
        self.knopf.toggled.connect(self._umschalten)
        if rechts is not None:
            self.kopffeld(rechts)

    def _umschalten(self, an: bool) -> None:
        self.knopf.setArrowType(Qt.DownArrow if an else Qt.RightArrow); self.inhalt.setVisible(an)
        self.updateGeometry()
        p = self.parentWidget()
        while p is not None and not isinstance(p, QScrollArea):         # der Rollbereich muss die neue Höhe der Seite kennen
            if p.layout() is not None:
                p.layout().invalidate()
            p = p.parentWidget()
        if p is not None:
            p.widget().adjustSize()

    def kopffeld(self, widget: QWidget, text: str = "") -> None:
        """Das Menü des Abschnitts (Voreinstellung, Farbe) rechts im Kopf, in der Breite der Feldspalte darunter."""
        widget.setFixedSize(FELDBREITE, FELDHOEHE)
        self.layout().itemAt(0).layout().addWidget(widget)

    def zeile(self, text: str, widget: QWidget) -> None:
        self.gitter.zeile(text, widget)

    def auswahl(self, *radios: QWidget) -> None:
        """Auswahlpunkte (Füllungsart, Linienart) ordentlich untereinander, eine je Zeile."""
        for r in radios:
            r.setProperty("einspaltig", True)                                  # nicht zu zweit nebeneinander ins Raster
            self.gitter.breit(r)

    def breit(self, widget: QWidget) -> None:
        self.gitter.breit(widget)
