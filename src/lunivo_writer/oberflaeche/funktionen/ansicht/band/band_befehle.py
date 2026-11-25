"""Baustein „Ansicht, Fenster, Zoom“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen.

Anschluss ans Farmwork und die Aktionen (Hilfe, Oberfläche, Fenster, Layout, Zoom, Lesen) stehen je in einer eigenen Datei dieses Ordners."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.ansicht.band.anschluss import AnsichtAnschluss
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen.fenster_aktionen import FensterAktionen
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen.hilfe_aktionen import HilfeAktionen
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen.layout_aktionen import LayoutAktionen
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen.lesen_aktionen import LesenAktionen
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen.oberflaeche_aktionen import OberflaecheAktionen
from lunivo_writer.oberflaeche.funktionen.ansicht.aktionen.zoom_aktionen import ZoomAktionen


class AnsichtBandBefehle(HilfeAktionen, OberflaecheAktionen, FensterAktionen, LayoutAktionen, ZoomAktionen, LesenAktionen, AnsichtAnschluss):
    pass
