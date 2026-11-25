from __future__ import annotations
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from writer.anbindung import listen as L
from writer.anbindung import mehrstufig as M
from vcl.qt.widgets.dialoge.dokument.liste_dialog_hilfen import _KACHEL, _gl_bild


def kachel_bild(spec: dict | None, groesse: QSize) -> QIcon:
    """Dieselbe Kachel wie im Fenster „Nummerierung und Aufzählungszeichen“, verkleinert für die Auswahl im Band."""
    pm = _gl_bild(spec).pixmap(_KACHEL).scaled(groesse, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return QIcon(pm)


def aufzaehlungen() -> list:
    """Die Aufzählungsarten der Auswahl: Punkt, Quadrat und die Zeichen ◆ ✤ ➤ ✓ ✧ (wie im Fenster)."""
    return [L.liste("disc"), L.liste("square")] + [M.aufzaehlung(g) for g in M.glyphen()]


def nummerierungen() -> list:
    return [L.liste(*n) for n in L.nummerierungen()]
