"""Baustein „Kopf- und Fußzeile“ für ``Befehle`` (siehe ``framework/befehle_alt/befehlsliste.py``): setzt die feinen Teile zusammen.

Anschluss ans Framework, Ereignisse, Aktionen, Zustände, Klappen und Felder stehen je in einer eigenen Datei dieses Ordners."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.kopffuss.aktionen import KopfFussAktionen
from lunivo_writer.oberflaeche.funktionen.kopffuss.anschluss import KopfFussAnschluss
from lunivo_writer.oberflaeche.funktionen.kopffuss.ereignisse import KopfFussEreignisse
from lunivo_writer.oberflaeche.funktionen.kopffuss.felder import KopfFussFelder
from lunivo_writer.oberflaeche.funktionen.kopffuss.klappen import KopfFussKlappen
from lunivo_writer.oberflaeche.funktionen.kopffuss.zustaende import KopfFussZustaende


class KopfFussBandBefehle(KopfFussAktionen, KopfFussZustaende, KopfFussKlappen, KopfFussFelder, KopfFussEreignisse, KopfFussAnschluss):
    pass
