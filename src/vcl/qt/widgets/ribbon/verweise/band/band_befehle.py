"""Baustein „Verweise“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen.

Anschluss ans Farmwork, Aktionen und Klappen stehen je in einer eigenen Datei dieses Ordners, jeder Dialog in seiner eigenen."""
from __future__ import annotations

from vcl.qt.widgets.ribbon.verweise.aktionen.aktionen import VerweiseAktionen
from writer.referenzwerkzeuge.band.anschluss import VerweiseAnschluss
from vcl.qt.widgets.ribbon.verweise.aktionen.klappen import VerweiseKlappen


class VerweiseBandBefehle(VerweiseAktionen, VerweiseKlappen, VerweiseAnschluss):
    pass
