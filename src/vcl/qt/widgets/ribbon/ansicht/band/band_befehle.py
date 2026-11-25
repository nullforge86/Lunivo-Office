"""Baustein „Ansicht, Fenster, Zoom“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen.

Anschluss ans Farmwork und die Aktionen (Hilfe, Oberfläche, Fenster, Layout, Zoom, Lesen) stehen je in einer eigenen Datei dieses Ordners."""
from __future__ import annotations

from writer.werkzeugleisten.ansicht.band.anschluss import AnsichtAnschluss
from writer.werkzeugleisten.ansicht.aktionen.fenster_aktionen import FensterAktionen
from vcl.qt.widgets.ribbon.ansicht.aktionen.hilfe_aktionen import HilfeAktionen
from writer.werkzeugleisten.ansicht.aktionen.layout_aktionen import LayoutAktionen
from writer.werkzeugleisten.ansicht.aktionen.lesen_aktionen import LesenAktionen
from vcl.qt.widgets.ribbon.ansicht.aktionen.oberflaeche_aktionen import OberflaecheAktionen
from vcl.qt.widgets.ribbon.ansicht.aktionen.zoom_aktionen import ZoomAktionen


class AnsichtBandBefehle(HilfeAktionen, OberflaecheAktionen, FensterAktionen, LayoutAktionen, ZoomAktionen, LesenAktionen, AnsichtAnschluss):
    pass
