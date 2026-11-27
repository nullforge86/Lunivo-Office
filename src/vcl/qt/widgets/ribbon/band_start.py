"""Kompakte Arbeitsleiste des Reiters „Start“: eine Zeile aus den vorhandenen Knöpfen und Feldern.

Reicht die Breite nicht, wird die Leiste nicht höher und nicht gerollt: die Knöpfe am rechten Ende werden ausgeblendet und stehen dann im Menü „Mehr“.
Passt alles, ist „Mehr“ nicht zu sehen."""
from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.zustaende.geruest import reihe
from vcl.qt.widgets.ribbon.band_bausteine import _GruppenTrenner


class _Arbeitsleiste(QWidget):
    """Eine Zeile aus Teilen (Knopf, Feld, Trenner) und am Ende „Mehr“. Was nicht ganz hineinpasst, wird von rechts her ausgeblendet."""

    def __init__(self):
        super().__init__()
        self.zeile = reihe("leiste", self)
        self.teile: list[QWidget] = []
        self.mehr: QWidget | None = None
        self.mehr_immer = False                                # „Mehr“ enthält auch bei voller Breite Befehle

    def teil(self, w: QWidget) -> QWidget:
        self.teile.append(w)
        self.zeile.addWidget(w)
        return w

    def abschliessen(self, mehr: QWidget) -> None:
        self.mehr = mehr
        self.zeile.addWidget(mehr)
        self.zeile.addStretch(1)

    def minimumSizeHint(self) -> QSize:
        return QSize(self.mehr.sizeHint().width() if self.mehr is not None else 0, super().minimumSizeHint().height())

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self.verteilen()

    @staticmethod
    def _breite(w: QWidget) -> int:
        """Die Breite, die das Teil in der Zeile wirklich bekommt: sein Wunsch innerhalb seiner Mindest- und Höchstbreite."""
        return max(w.minimumWidth(), min(w.sizeHint().width(), w.maximumWidth()))

    def verteilen(self) -> None:
        """So viele Teile zeigen, wie neben „Mehr“ ganz hineinpassen; ab dem ersten, das nicht passt, sind alle weiteren verborgen."""
        if self.mehr is None:
            return
        rand, abstand = self.zeile.contentsMargins(), self.zeile.spacing()
        frei = self.width() - rand.left() - rand.right()
        alles = sum(self._breite(w) + abstand for w in self.teile) <= frei
        zeigen = self.mehr_immer or not alles              # „Mehr“ nur, wenn es etwas enthält
        if zeigen:
            frei -= self._breite(self.mehr)
        belegt, passt = 0, True
        for w in self.teile:
            belegt += self._breite(w) + abstand
            passt = passt and belegt <= frei
            w.setVisible(passt)
        self.mehr.setVisible(zeigen)


class BandStartBaustein:
    """Baut die Arbeitsleiste des Reiters „Start“ und hält das Menü „Mehr“ zum Sichtbaren passend."""

    def _start_bauen(self, zeile, r: dict) -> None:
        plan = r["arbeitsleiste"]
        leiste = _Arbeitsleiste()
        leiste.mehr_immer = plan["mehr_immer"]
        stil, font, groesse = self._formatfelder()
        felder = {"stil": stil, "font": font, "groesse": groesse}
        in_zeile = {e["feld"] for e in plan["zeile"] if e.get("feld")}
        for name in [n for n in felder if n not in in_zeile]:  # ein Feld, das die Zeile nicht zeigt, gibt es im Band nicht
            self.felder.pop(name).deleteLater()
        im_menue: list[tuple[QWidget, list[str]]] = []          # (Knopf der Zeile, Namen seiner Zeilen im Menü „Mehr“)
        for e in plan["zeile"]:
            if e.get("trenner"):
                leiste.teil(_GruppenTrenner())
            elif e.get("feld"):
                leiste.teil(felder[e["feld"]])
            else:
                im_menue.append((leiste.teil(self._knopf(e, False)), [z["name"] for z in e["im_menue"]]))
        mehr = self._knopf(plan["mehr"], False)
        menue = mehr.menu()
        menue.aboutToShow.connect(lambda: self._mehr_abgleichen(menue.actions(), im_menue))
        leiste.abschliessen(mehr)
        zeile.addWidget(leiste, 1)
        self.arbeitsleiste = leiste

    @staticmethod
    def _mehr_abgleichen(aktionen: list[QAction], im_menue: list[tuple[QWidget, list[str]]]) -> None:
        """Vor dem Öffnen von „Mehr“: die Zeilen eines Knopfes sind genau dann zu sehen, wenn der Knopf selbst ausgeblendet ist."""
        kopf = []                                              # die Zeilen der Leistenknöpfe stehen vor dem ersten Trenner
        for a in aktionen:
            if a.isSeparator():
                break
            kopf.append(a)
        verborgen = {name for w, namen in im_menue if w.isHidden() for name in namen}
        for a in kopf:
            a.setVisible(a.text().partition("\t")[0] in verborgen)
        if len(kopf) < len(aktionen):
            aktionen[len(kopf)].setVisible(bool(verborgen))    # der Trenner zwischen den ausgeblendeten und den übrigen Befehlen
