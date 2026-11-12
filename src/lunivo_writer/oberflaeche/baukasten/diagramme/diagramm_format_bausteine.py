"""Gemeinsame Kleinbausteine der Diagramm-Formatierung (Seitenleiste): Auswahllisten, Zeichner für Strichart und Kombinierten Typ, ``_AutoWert``.

Genutzt von ``diagramm_format_panel.py`` (Diagramm-Teile), ``diagramm_format_werte.py`` (Werte lesen/setzen) und ``diagramm_text_panel.py`` (Textoptionen)."""
from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QPainterPath
from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout, QWidget
from lunivo_writer.editor.diagramme import diagramm_format as F
from lunivo_writer.oberflaeche.baukasten.basis.linien import Linie
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.strich_auswahl import StrichAuswahl
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_NORMAL, RAND_KEIN
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld

TEXT_TEILE = ("diagrammbereich", "titel", "legende", "achse_horizontal", "achse_vertikal", "datenbeschriftung")
LEGENDEN_LAGEN = (("oben", "Oben"), ("unten", "Unten"), ("links", "Links"), ("rechts", "Rechts"))
RICHTUNGEN = (("waagerecht", "Waagerecht"), ("dreh90", "Um 90° drehen"), ("dreh270", "Um 270° drehen"), ("gestapelt", "Gestapelt"))
ABSCHLUSS = (("flach", "Flach"), ("rund", "Rund"), ("quadrat", "Quadratisch"))
VERKNUEPFUNG = (("rund", "Rund"), ("schraeg", "Abgeschrägt"), ("spitz", "Spitz"))
_OHNE = object()                                       # „Bildfüllung ohne Bild“: die Füllung bleibt, wie sie ist


def _optionen_name(teil: str) -> str:
    if teil.startswith("reihe_"):
        return "Reihe Optionen"
    if teil.startswith("legendeneintrag_"):
        return "Legendeneintrag Optionen"
    return {"titel": "Titel Optionen", "legende": "Legende Optionen", "achse_horizontal": "Achse Optionen", "achse_vertikal": "Achse Optionen",
            "zeichnungsbereich": "Zeichnungsbereich Optionen", "datenbeschriftung": "Datenbeschriftung Optionen"}.get(teil, "Diagramm Optionen")


def _text_teil(teil: str) -> bool:
    return teil in TEXT_TEILE or teil.startswith("legendeneintrag_")


def _combo(eintraege) -> QComboBox:
    c = Auswahlfeld()
    for k, n in eintraege:
        c.addItem(n, k)
    return c


def _strich_zeichner(art: str):
    """Zeichner für ``StrichAuswahl``: ein Strich der Strichart ``art`` über die Breite (schwarz)."""
    def z(p, r, farbe):
        pen = F.stift({"art": art, "breite": 1.6, "farbe": farbe.name()}); pen.setColor(farbe); p.setPen(pen)
        p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))
    return z


def _kombi_zeichner(form: str):
    """Zeichner für ``StrichAuswahl``: eine Linie des kombinierten Typs ``form`` (Flächen aus ``textfx._kontur_pfade``)."""
    def z(p, r, farbe):
        from lunivo_writer.editor.text import textfx as X
        pf = QPainterPath(); pf.moveTo(r.left(), r.center().y()); pf.lineTo(r.right(), r.center().y())
        p.setPen(Qt.NoPen); p.setBrush(farbe)
        for fl in X._kontur_pfade(pf, 3.0, form):
            p.drawPath(fl)
    return z


def _still(x, wert, setter: str = "setValue") -> None:
    x.blockSignals(True); getattr(x, setter)(wert); x.blockSignals(False)


class _AutoWert(QWidget):
    """Eine Zahl, die „Automatisch“ sein kann (Minimum, Maximum, Hauptintervall der Achse): Haken + Feld. ``wert()`` ist None bei Automatisch."""
    geaendert = Signal()

    def __init__(self, vorgabe: float = 0.0):
        super().__init__()
        h = QHBoxLayout(self); h.setContentsMargins(*RAND_KEIN); h.setSpacing(ABSTAND_NORMAL)
        self.auto = QCheckBox("Auto"); self.auto.setChecked(True)
        self.feld = QDoubleSpinBox(); self.feld.setRange(-1e9, 1e9); self.feld.setDecimals(2); self.feld.setValue(vorgabe); self.feld.setEnabled(False)
        self.feld.setMinimumWidth(0)
        h.addWidget(self.auto); h.addWidget(self.feld, 1)
        self.auto.toggled.connect(lambda an: (self.feld.setEnabled(not an), self.geaendert.emit()))
        self.feld.valueChanged.connect(lambda *_: self.geaendert.emit())

    def wert(self) -> float | None:
        return None if self.auto.isChecked() else self.feld.value()

    def setze(self, w: float | None) -> None:
        for x in (self.auto, self.feld):
            x.blockSignals(True)
        self.auto.setChecked(w is None); self.feld.setEnabled(w is not None)
        if w is not None:
            self.feld.setValue(float(w))
        for x in (self.auto, self.feld):
            x.blockSignals(False)
