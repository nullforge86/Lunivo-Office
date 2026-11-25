"""Baustein „Kopf- und Fußzeile“ für ``Befehle`` (siehe ``framework/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen.

Anschluss ans Framework, Ereignisse, Aktionen, Zustände, Klappen und Felder stehen je in einer eigenen Datei dieses Ordners."""
from __future__ import annotations

from vcl.qt.widgets.ribbon.kopffuss.aktionen.aktionen import KopfFussAktionen
from writer.werkzeugleisten.kopffuss.band.anschluss import KopfFussAnschluss
from writer.werkzeugleisten.kopffuss.aktionen.ereignisse import KopfFussEreignisse
from vcl.qt.widgets.ribbon.kopffuss.felder.felder import KopfFussFelder
from vcl.qt.widgets.ribbon.kopffuss.aktionen.klappen import KopfFussKlappen
from writer.werkzeugleisten.kopffuss.aktionen.zustaende import KopfFussZustaende


class KopfFussBandBefehle(KopfFussAktionen, KopfFussZustaende, KopfFussKlappen, KopfFussFelder, KopfFussEreignisse, KopfFussAnschluss):
    pass
