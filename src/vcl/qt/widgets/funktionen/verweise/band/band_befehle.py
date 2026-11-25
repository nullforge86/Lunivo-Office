"""Baustein „Verweise“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen.

Anschluss ans Farmwork, Aktionen und Klappen stehen je in einer eigenen Datei dieses Ordners, jeder Dialog in seiner eigenen."""
from __future__ import annotations

from vcl.qt.widgets.funktionen.verweise.aktionen.aktionen import VerweiseAktionen
from writer.funktionen.verweise.band.anschluss import VerweiseAnschluss
from vcl.qt.widgets.funktionen.verweise.aktionen.klappen import VerweiseKlappen


class VerweiseBandBefehle(VerweiseAktionen, VerweiseKlappen, VerweiseAnschluss):
    pass
