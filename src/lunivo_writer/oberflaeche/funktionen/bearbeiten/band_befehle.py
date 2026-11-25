"""Baustein „Zwischenablage und Bearbeiten“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.bearbeiten.anschluss import BearbeitenAnschluss
from lunivo_writer.oberflaeche.funktionen.bearbeiten.auswahl_aktionen import AuswahlAktionen
from lunivo_writer.oberflaeche.funktionen.bearbeiten.klappen import BearbeitenKlappen
from lunivo_writer.oberflaeche.funktionen.bearbeiten.such_aktionen import SuchAktionen
from lunivo_writer.oberflaeche.funktionen.bearbeiten.zwischenablage_aktionen import ZwischenablageAktionen


class BearbeitenBandBefehle(ZwischenablageAktionen, AuswahlAktionen, SuchAktionen, BearbeitenKlappen, BearbeitenAnschluss):
    pass
