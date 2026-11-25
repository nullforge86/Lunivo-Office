"""Baustein „Überprüfen“ für ``Befehle`` (siehe ``farmwork/befehle_alt/befehlsliste.py``): Kommentare, Noten, Änderungen, Markup, Anzeige und Schutz.

Anschluss ans Farmwork, Aktionen, Zustände, Klappen und Felder stehen je in einer eigenen Datei dieses Ordners, jeder Dialog in seiner eigenen."""
from __future__ import annotations

from writer.ueberpruefung.aktionen.aenderungs_aktionen import AenderungsAktionen
from vcl.qt.widgets.ribbon.ueberpruefen.band.anschluss import UeberpruefenAnschluss
from writer.ueberpruefung.aktionen.anzeige_aktionen import AnzeigeAktionen
from vcl.qt.widgets.ribbon.ueberpruefen.felder.felder import UeberpruefenFelder
from vcl.qt.widgets.ribbon.ueberpruefen.aktionen.klappen_markup import MarkupKlappen
from vcl.qt.widgets.ribbon.ueberpruefen.aktionen.klappen_pruefen import PruefenKlappen
from vcl.qt.widgets.ribbon.ueberpruefen.aktionen.kommentar_aktionen import KommentarAktionen
from writer.ueberpruefung.aktionen.noten_aktionen import NotenAktionen
from vcl.qt.widgets.ribbon.ueberpruefen.aktionen.schutz_aktionen import SchutzAktionen
from writer.ueberpruefung.aktionen.zustaende import UeberpruefenZustaende


class UeberpruefenBandBefehle(KommentarAktionen, AenderungsAktionen, NotenAktionen, AnzeigeAktionen, SchutzAktionen, UeberpruefenZustaende,
                              PruefenKlappen, MarkupKlappen, UeberpruefenFelder, UeberpruefenAnschluss):
    pass
