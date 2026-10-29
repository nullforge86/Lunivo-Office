"""Das Fenster „Vergrößern“ (Lupe in der Schnellleiste am Bild): das Bild in seiner Auflösung ansehen, mit Regler und Mausrad zoomen.

    BildZoomFenster(parent, bild).exec()     # nur ansehen, ändert nichts; Zoom 100 % = ein Bildpunkt je Bildschirmpunkt

Gebaut wie die anderen Seitenleistenfenster (``PanelFaehig``, ``FormularGitter``): bei 300 px Breite ragt nichts heraus; die Ansicht rollt in beide
Richtungen. Der Regler ist der Baustein ``SchiebeFeld``."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QDialog, QFrame, QLabel, QScrollArea, QSizePolicy, QVBoxLayout

from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import abschnittstitel
from lunivo_writer.ui.baukasten.schiebe_feld import SchiebeFeld
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

ZOOM_MIN, ZOOM_MAX = 10, 400


class _Ansicht(QScrollArea):
    """Rollbereich, dessen Mausrad (mit oder ohne Strg) den Zoom ändert."""

    def __init__(self, bei_zoom):
        super().__init__()
        self._bei_zoom = bei_zoom
        self.setWidgetResizable(False); self.setAlignment(Qt.AlignCenter); self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding); self.setMinimumWidth(0)
        self.bild = QLabel(); self.bild.setAlignment(Qt.AlignCenter); self.setWidget(self.bild)

    def wheelEvent(self, e) -> None:
        if e.angleDelta().y():
            self._bei_zoom(10 if e.angleDelta().y() > 0 else -10)
            e.accept()
            return
        super().wheelEvent(e)


class BildZoomFenster(PanelFaehig, QDialog):
    def __init__(self, parent=None, bild: QImage | None = None, titel: str = "Vergrößern"):
        super().__init__(parent)
        self.setWindowTitle(titel)
        self._bild = bild if bild is not None and not bild.isNull() else QImage(1, 1, QImage.Format_ARGB32)
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(6)
        v.addWidget(abschnittstitel("Vergrößerung"))
        self.zoom = SchiebeFeld(ZOOM_MIN, ZOOM_MAX, " %", 10, 0, 100)
        self.zoom.setAccessibleName("Vergrößerung")
        v.addWidget(self.zoom)
        self.ansicht = _Ansicht(lambda s: self.zoom.setValue(self.zoom.value() + s, melden=True))
        self.ansicht.setMinimumHeight(260)
        v.addWidget(self.ansicht, 1)
        self.info = QLabel(f"Originalauflösung: {self._bild.width()} × {self._bild.height()} Bildpunkte"); self.info.setWordWrap(True)
        v.addWidget(self.info)
        fussleiste(self, v, nur_ok=True, ok_text="Schließen")
        self.zoom.valueChanged.connect(self.aktualisieren)
        self.aktualisieren()

    def aktualisieren(self, _w=None) -> None:
        """Das Bild im gewählten Maßstab zeigen."""
        f = self.zoom.value() / 100.0
        pm = QPixmap.fromImage(self._bild)
        if abs(f - 1.0) > 1e-6:
            pm = pm.scaled(QSize(max(1, round(pm.width() * f)), max(1, round(pm.height() * f))), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ansicht.bild.setPixmap(pm); self.ansicht.bild.resize(pm.size())
