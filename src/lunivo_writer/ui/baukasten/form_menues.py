"""Menüs und Galerie des Reiters „Zeichentools“ für Formen: „Form bearbeiten“ und die Stilgalerie „Abc“ (nur Aussehen; jede Wahl ruft einen Befehl).

``form_bearbeiten_menue(b)``  Form ändern ▸ (die Formen des Katalogs nach Gruppen, Wahl ``formAendern``) · Punkte bearbeiten (``formPunkteBearbeiten``: Freiform, siehe ``editor/freiform.py``)
``formstile_galerie(b)``      sechs Kacheln „Abc“ im Band; der Pfeil öffnet das Raster 6 × 7 (``objekt_menues.formstile``), Wahl ``formStilRaster``
``KLAPPEN`` / ``GALERIEN``    melden sie dem Band (``bild_diagramm_menues.py``)
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap

from lunivo_writer.ui.baukasten.menue_liste import MenueListe

# Welche sechs Stile die Kacheln im Band zeigen: (Zeile, Spalte) des Rasters
BAND_STILE = ((1, 0), (0, 1), (1, 1), (1, 2), (1, 3), (1, 4))


def form_bearbeiten_menue(b) -> MenueListe:
    from lunivo_writer.editor import formen_katalog as K
    from lunivo_writer.ui.baukasten.bild_diagramm_menues import _form_bild
    m = MenueListe()
    aendern = m.untermenue("Form ändern")
    for kat, formen in K.KATEGORIEN:
        sub = aendern.untermenue(kat)
        for name in formen:
            sub.eintrag(name, lambda n=name: b.formAendern(None, n), symbol=_form_bild(name))
    m.eintrag("Punkte bearbeiten", lambda: b.formPunkteBearbeiten(),
              tip="Die Punkte der Form ziehen; Rechtsklick löscht einen Punkt, Doppelklick auf eine Kante fügt einen ein")
    return m


def formstile_galerie(b) -> dict:
    from lunivo_writer.ui.baukasten.objekt_menues import formstil_zeichner, formstile
    from lunivo_writer.ui.baukasten.raster_auswahl import _symbol
    kacheln = []
    for z, s in BAND_STILE:
        pm = _symbol(formstil_zeichner(f"z{z}{s}"), QSize(50, 34)).pixmap(QSize(50, 34))
        kacheln.append((f"Formstil {z + 1}/{s + 1}", pm, lambda z=z, s=s: b.formStilRaster(None, z, s)))
    from lunivo_writer.ui.document.freie_bilder_bedienung import FreieBilderMixin as F
    return {"kacheln": kacheln, "menue": F.frei_formstile_menue(None, None, lambda: b.ed), "name": "Formstile"}


def linien_galerie(b) -> dict:
    """Linien und Pfeile als Kacheln im Band (zwei Reihen, ``zeilen`` der Gruppe); Klick fügt die Linie ein (``formEinfuegen``).
    Der Pfeil daneben öffnet das Raster der Gruppe „Linie“ des Formenkatalogs."""
    from PySide6.QtCore import QRectF as R
    from PySide6.QtGui import QColor, QPen
    from lunivo_writer.core.farben import Farbe
    from lunivo_writer.editor import formen_katalog as K
    from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, _symbol
    namen = list(dict(K.KATEGORIEN)["Linie"])

    def zeichner(name):
        def zeichne(p, r):
            p.setPen(QPen(QColor(Farbe.AKZENT), 1.5)); p.setBrush(Qt.NoBrush)
            p.drawPath(K.pfad(name, R(r).adjusted(3, 3, -3, -3)))
        return zeichne
    kacheln = [(n, _symbol(zeichner(n), QSize(26, 22)).pixmap(QSize(26, 22)), lambda n=n: b.formEinfuegen(None, n)) for n in namen]
    menue = RasterAuswahl(getattr(b, "w", None), titel="Linien", spalten=5, groesse=QSize(26, 22))
    for n in namen:
        menue.kachel(n, n, zeichner(n)).setCheckable(False)
    menue.gewaehlt.connect(lambda n: b.formEinfuegen(None, n))
    return {"kacheln": kacheln, "menue": menue, "name": "Linien"}


KLAPPEN = {"formBearbeiten": form_bearbeiten_menue}
GALERIEN = {"zeichenFormstile": formstile_galerie, "zeichenLinien": linien_galerie}
