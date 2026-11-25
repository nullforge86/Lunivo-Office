"""Baustein „Zwischenablage und Bearbeiten“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.bearbeiten.band.anschluss import BearbeitenAnschluss
from lunivo_writer.oberflaeche.funktionen.bearbeiten.aktionen.auswahl_aktionen import AuswahlAktionen
from lunivo_writer.oberflaeche.funktionen.bearbeiten.aktionen.klappen import BearbeitenKlappen
from lunivo_writer.oberflaeche.funktionen.bearbeiten.aktionen.such_aktionen import SuchAktionen
from lunivo_writer.oberflaeche.funktionen.bearbeiten.aktionen.zwischenablage_aktionen import ZwischenablageAktionen


class BearbeitenBandBefehle(ZwischenablageAktionen, AuswahlAktionen, SuchAktionen, BearbeitenKlappen, BearbeitenAnschluss):
    pass
