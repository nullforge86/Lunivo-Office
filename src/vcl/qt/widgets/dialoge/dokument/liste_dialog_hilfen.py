"""Liste dialog hilfen: aus ``vcl.qt.widgets.dialoge.dokument.liste_dialog`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QSpinBox, QWidget
from writer.anbindung import listen as L
from writer.anbindung import mehrstufig as _mehrstufig
from vcl.qt.widgets.bausteine.symbole.medien.listen_symbole import liste_zeichner
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_LISTENSTIL_KACHEL, RAND_KEIN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_ZEICHEN_KURZ
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_LISTE_BEISPIEL_PX, SCHRIFT_LISTE_KLEIN_PX
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter


_KACHEL = QSize(*GROESSE_LISTENSTIL_KACHEL) # die Kacheln füllen das Raster wie in der Vorlage: vier je Zeile, jede mit Rahmen


def _rahmen(p: QPainter, groesse: QSize) -> None:
    p.setPen(QColor(Farbe.GRAU_HELL)); p.setBrush(Qt.NoBrush); p.drawRect(0, 0, groesse.width() - 1, groesse.height() - 1)


def _bild(spec: dict | None, groesse: QSize = _KACHEL) -> QIcon:
    pm = QPixmap(groesse); pm.fill(QColor(Farbe.PAPIER))
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    r = QRectF(0, 0, groesse.width(), groesse.height())
    if spec is None:                                          # „Kein“: ein kleines Quadrat mit dem Wort darin
        q = QRectF(r.center().x() - 32, r.center().y() - 32, 64, 64)
        p.setPen(QColor(Farbe.GRAU)); p.drawRect(q)
        f = p.font(); f.setBold(True); p.setFont(f)
        p.setPen(QColor(Farbe.TINTE_DUNKEL)); p.drawText(q, Qt.AlignCenter, "Kein")
    else:
        liste_zeichner(L.marke(spec))(p, r.adjusted(0, 18, 0, -18))
    _rahmen(p, groesse)
    p.end()
    return QIcon(pm)


class _Zahlenformat(QWidget):
    """Zahlenformat, Zahlenart, Startzahl und „Schriftart …“ der Nummer — gemeinsam für „Nummerierung anpassen“ und „Gliederung anpassen“."""
    geaendert = Signal()

    def __init__(self, tipp: str, breit: bool = False):
        """``breit``: die Anordnung der Gliederung (Zahlenformat und Vorlage über die ganze Breite, „Beginnen mit“ in einer eigenen Zeile;
        „Schriftart …“ setzt der Aufrufer, z. B. neben die vorherige Ebene). Sonst die der einfachen Nummerierung."""
        super().__init__()
        g = FormularGitter(self); g.setContentsMargins(*RAND_KEIN)
        self.format = zeilenfeld("frei"); self.format.setToolTip(tipp)
        self.schrift = knopf("standard", "Schriftart …", aktion=self._schriftart)
        self.zeichen: dict = {}
        self.art = Auswahlfeld()
        for k, st in L.stile().items():
            if not st[1]:
                self.art.addItem(st[0], k)
        self.art.zeichen(DROPDOWN_ZEICHEN_KURZ)
        self.start = QSpinBox(); self.start.setRange(1, 9999)
        if breit:
            g.reihe(("Zahlenformat:", self.format))
            g.reihe(("Zahlenformatvorlage:", self.art), ("Beginnen mit:", self.start), gewichte=(5, 4))
        else:
            g.reihe(("Zahlenformat:", self.format))
            g.breit(self.schrift)
            g.reihe(("Zahlenformatvorlage:", self.art), ("Beginnen mit:", self.start), gewichte=(5, 4))
        self.format.textChanged.connect(lambda *_: self.geaendert.emit())
        self.art.currentIndexChanged.connect(lambda *_: self.geaendert.emit())
        self.start.valueChanged.connect(lambda *_: self.geaendert.emit())

    def setze(self, format: str, stil: str, start: int, zeichen: dict | None) -> None:
        for w in (self.format, self.art, self.start):
            w.blockSignals(True)
        self.format.setText(format); self.art.setCurrentIndex(max(0, self.art.findData(stil))); self.start.setValue(start)
        for w in (self.format, self.art, self.start):
            w.blockSignals(False)
        self.zeichen = dict(zeichen or {})

    def _schriftart(self) -> None:
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
        from vcl.qt.widgets.dialoge.formatierung.schriftart_dialog import ZEICHEN, SchriftartDialog
        d = SchriftartDialog(self, {**ZEICHEN, **(self.zeichen or {})}, umfang="vorlage")

        def fertig() -> None:
            self.zeichen = L.zeichen_filtern(d.werte())
            self.geaendert.emit()
        zeige_unter(self, d, fertig)


def _gl_bild(defn: dict | None, groesse: QSize = _KACHEL) -> QIcon:
    """Kachel einer Gliederung: die Ebenen 1 bis 3 mit ihren Nummern."""
    if defn is None:
        return _bild(None, groesse)
    if "ebenen" not in defn:
        return _bild(defn, groesse)
    pm = QPixmap(groesse); pm.fill(QColor(Farbe.PAPIER))
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    if _mehrstufig.ist_aufzaehlung(defn):                              # Aufzählung mit eigenem Zeichen: drei Zeilen mit dem Zeichen davor
        f = p.font(); f.setPixelSize(SCHRIFT_LISTE_BEISPIEL_PX); p.setFont(f)
        for i in range(3):
            y = groesse.height() / 2 - 24 + i * 24
            p.setPen(QColor(Farbe.TINTE)); p.drawText(QRectF(groesse.width() * 0.3, y - 10, 22, 20), Qt.AlignCenter, defn["ebenen"][0]["format"])
            p.setPen(QColor(Farbe.GRAU_HELL)); p.drawLine(int(groesse.width() * 0.3 + 30), int(y), int(groesse.width() * 0.3 + 90), int(y))
        _rahmen(p, groesse); p.end()
        return QIcon(pm)
    zaehler = [0] * _mehrstufig.ebenen()
    f = p.font(); f.setPixelSize(SCHRIFT_LISTE_KLEIN_PX); p.setFont(f)
    for i, n in enumerate((1, 2, 2, 3)):
        _mehrstufig.zaehlen(zaehler, defn, n)
        t = _mehrstufig.nummer_der_ebene(defn, zaehler, n)
        y = 22 + i * 24
        x = 14 + (n - 1) * 10
        p.setPen(QColor(Farbe.TINTE)); p.drawText(QRectF(x, y - 7, 40, 14), Qt.AlignVCenter | Qt.AlignLeft, t)
        p.setPen(QColor(Farbe.GRAU_HELL)); p.drawLine(int(x + 38), y, groesse.width() - 8, y)
    _rahmen(p, groesse)
    p.end()
    return QIcon(pm)
