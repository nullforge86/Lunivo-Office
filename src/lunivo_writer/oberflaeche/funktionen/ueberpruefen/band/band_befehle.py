"""Baustein „Überprüfen“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): Kommentare, Noten, Änderungen, Markup, Anzeige und Schutz.

Anschluss ans Farmwork, Aktionen, Zustände, Klappen und Felder stehen je in einer eigenen Datei dieses Ordners, jeder Dialog in seiner eigenen."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.aenderungs_aktionen import AenderungsAktionen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.band.anschluss import UeberpruefenAnschluss
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.anzeige_aktionen import AnzeigeAktionen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.felder.felder import UeberpruefenFelder
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.klappen_markup import MarkupKlappen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.klappen_pruefen import PruefenKlappen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.kommentar_aktionen import KommentarAktionen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.noten_aktionen import NotenAktionen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.schutz_aktionen import SchutzAktionen
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.aktionen.zustaende import UeberpruefenZustaende


class UeberpruefenBandBefehle(KommentarAktionen, AenderungsAktionen, NotenAktionen, AnzeigeAktionen, SchutzAktionen, UeberpruefenZustaende,
                              PruefenKlappen, MarkupKlappen, UeberpruefenFelder, UeberpruefenAnschluss):
    pass
