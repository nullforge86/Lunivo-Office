"""Baustein „Zwischenablage und Bearbeiten“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen."""
from __future__ import annotations

from writer.werkzeugleisten.bearbeiten.band.anschluss import BearbeitenAnschluss
from vcl.qt.widgets.ribbon.bearbeiten.aktionen.auswahl_aktionen import AuswahlAktionen
from vcl.qt.widgets.ribbon.bearbeiten.aktionen.klappen import BearbeitenKlappen
from writer.werkzeugleisten.bearbeiten.aktionen.such_aktionen import SuchAktionen
from vcl.qt.widgets.ribbon.bearbeiten.aktionen.zwischenablage_aktionen import ZwischenablageAktionen


class BearbeitenBandBefehle(ZwischenablageAktionen, AuswahlAktionen, SuchAktionen, BearbeitenKlappen, BearbeitenAnschluss):
    pass
