"""Fenster „Optionen für Kopf- und Fußzeile“ (Seitenleistenfenster): Erste Seite anders; Gerade und ungerade Seiten unterschiedlich. Nur Darstellung."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QWidget

from lunivo_writer.farmwork.funktionen.kopffuss.typen import KopfFussOptionen
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import fussleiste
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import ausfuehren
from lunivo_writer.oberflaeche.baukasten.geruest.rollen import spalte
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig


class _Fenster(PanelFaehig, QDialog):
    pass


def optionen_fragen(eltern, optionen: KopfFussOptionen) -> tuple[bool, bool] | None:
    """Zeigt das Fenster; gibt (erste Seite anders, gerade/ungerade) zurück oder ``None``, wenn es abgebrochen wurde."""
    d = _Fenster(eltern)
    d.setWindowTitle("Optionen für Kopf- und Fußzeile")
    v = spalte("fenster", d)
    erste = UmbruchSchalter("Erste Seite anders")
    erste.setChecked(optionen.erste_seite_anders)
    gerade_ungerade = UmbruchSchalter("Gerade und ungerade Seiten sind unterschiedlich")
    gerade_ungerade.setChecked(optionen.gerade_ungerade)
    feld = QWidget()
    gitter = FormularGitter(feld)
    gitter.breit(abschnittstitel("Seiten"))
    gitter.breit(erste)
    gitter.breit(gerade_ungerade)
    v.addWidget(feld)
    v.addStretch(1)
    fussleiste(d, v)
    if ausfuehren(d):
        return erste.isChecked(), gerade_ungerade.isChecked()
    return None
