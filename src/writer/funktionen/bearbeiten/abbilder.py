"""Abbilder des Dokuments für die Oberfläche: Absatz, Tabelle, Objekt, Liste und Abfragen über das ganze Dokument als eigene Kopien
(gleiche Feldnamen wie im Dokumentmodell). Wer ein Abbild ändert, ändert das Dokument nicht."""
from __future__ import annotations

import dataclasses
from types import MappingProxyType

from framework.befehle import bearbeiten as _befehle
from writer.werte import Bereich, Stelle, eigene_kopie


def _eigen(wert):
    """Das Abbild mit eigenen, veränderbaren Kopien seiner Wörterbücher und Listen."""
    if wert is None:
        return None
    if dataclasses.is_dataclass(wert):
        return dataclasses.replace(wert, **{f.name: eigene_kopie(getattr(wert, f.name)) for f in dataclasses.fields(wert)
                                            if isinstance(getattr(wert, f.name), MappingProxyType)})
    if type(wert) is tuple:
        return tuple(_eigen(v) for v in wert)
    return eigene_kopie(wert)


def dok_absatz(kennung, absatz_id):
    return _eigen(_befehle.abbild_absatz(kennung, absatz_id))


def dok_absatz_an_marke(kennung):
    return _eigen(_befehle.abbild_absatz_an_marke(kennung))


def dok_absatzlaengen(kennung):
    """(Id, Länge) aller Absätze in Dokumentreihenfolge."""
    return _eigen(_befehle.abbild_absatzlaengen(kennung))


def dok_letzter_absatz(kennung):
    """Die Id des letzten Absatzes des Dokuments."""
    return _eigen(_befehle.abbild_letzter_absatz(kennung))


def dok_verwendete_vorlagen(kennung):
    """Die Namen der Formatvorlagen, die Absätze des Dokuments tragen."""
    return _eigen(_befehle.abbild_verwendete_vorlagen(kennung))


def dok_sortierbare_absaetze(kennung):
    return _eigen(_befehle.abbild_sortierbare_absaetze(kennung))


def dok_dokumenttext(kennung):
    """Der Text des Dokuments, Absätze durch Zeilenwechsel getrennt."""
    return _eigen(_befehle.abbild_dokumenttext(kennung))


def dok_standardformat(kennung):
    """Das Grundformat des Dokuments (Schrift, Größe …)."""
    return _eigen(_befehle.abbild_standardformat(kennung))


def dok_vorlage_vorhanden(kennung, name):
    return _eigen(_befehle.abbild_vorlage_vorhanden(kennung, name))


def dok_bereiche_mit(kennung, schluessel):
    """Zusammenhängende Bereiche (je Absatz), deren Zeichenformat ``schluessel`` trägt; ein Bereich endet, wo sich dessen Wert ändert."""
    return [Bereich(Stelle(*a), Stelle(*k)) for a, k in _befehle.abbild_bereiche_mit(kennung, schluessel)]


def dok_aenderungsbereiche(kennung):
    """Bereiche nachverfolgter Änderungen; ein Bereich endet, wo Art, Bearbeiter oder Zeit wechseln."""
    return [Bereich(Stelle(*a), Stelle(*k)) for a, k in _befehle.abbild_aenderungsbereiche(kennung)]


def dok_notenbereiche(kennung):
    """Die Stellen der Notenzeichen im Text."""
    return [Bereich(Stelle(*a), Stelle(*k)) for a, k in _befehle.abbild_notenbereiche(kennung)]


def dok_tabelle(kennung, tabellen_id):
    return _eigen(_befehle.abbild_tabelle(kennung, tabellen_id))


def dok_tabelle_von(kennung, absatz_id):
    """(Tabelle, Zeile, Spalte) der innersten Zelle, in der der Absatz steht – ``None`` im Fließtext."""
    return _eigen(_befehle.abbild_tabelle_von(kennung, absatz_id))


def dok_zellen_im_bereich(kennung):
    """(Tabellen-Id, Zellen) der Zellen, die die Auswahl in einer Tabelle überstreicht – ``None`` außerhalb."""
    return _eigen(_befehle.abbild_zellen_im_bereich(kennung))


def dok_objekt(kennung, objekt_id):
    """Das frei positionierte Objekt mit der Id oder ``None``."""
    return _eigen(_befehle.abbild_objekt(kennung, objekt_id))


def dok_objekte(kennung):
    """Alle frei positionierten Objekte des Dokuments."""
    return _eigen(_befehle.abbild_objekte(kennung))


def dok_inline(kennung, objekt_id):
    """Das Objekt im Text mit der Id oder ``None``."""
    return _eigen(_befehle.abbild_inline(kennung, objekt_id))


def dok_objekt_position(kennung, objekt_id):
    """Die Textstelle vor einem Objekt im Text; bei einem freien Objekt der Anfang seines Ankerabsatzes."""
    p = _befehle.abbild_objekt_position(kennung, objekt_id)
    return None if p is None else Stelle(*p)


def dok_ressource(kennung, name):
    """Die Bilddaten einer Ressource des Dokuments."""
    return _eigen(_befehle.abbild_ressource(kennung, name))


def dok_liste(kennung, liste_id):
    return _eigen(_befehle.abbild_liste(kennung, liste_id))


def dok_noten(kennung):
    """Art der Note → (Id → Text)."""
    return _eigen(_befehle.abbild_noten(kennung))


def dok_kommentare(kennung):
    """Id des Kommentars → Bearbeiter, Initialen, Zeit, Text und ob er erledigt ist."""
    return _eigen(_befehle.abbild_kommentare(kennung))


def dok_quellen(kennung):
    return _eigen(_befehle.abbild_quellen(kennung))


def dok_eigenschaft(kennung, name):
    """Eine Eigenschaft des Dokuments (zum Beispiel ``zitierweise``) oder ``None``."""
    return _eigen(_befehle.abbild_eigenschaft(kennung, name))


def dok_abschnitt_index(kennung, block_id):
    """Der Abschnitt (Index), in dem der Absatz oder die Tabelle steht."""
    return _eigen(_befehle.abbild_abschnitt_index(kennung, block_id))


def dok_abschnitte_anzahl(kennung):
    return _eigen(_befehle.abbild_abschnitte_anzahl(kennung))


def dok_abschnitt_beginn(kennung, index):
    return _eigen(_befehle.abbild_abschnitt_beginn(kennung, index))


def dok_abschnitt_erster_absatz(kennung, index):
    """Die Id des ersten Absatzes des Abschnitts; ``None``, wenn es den Abschnitt nicht gibt oder er keinen Absatz hat."""
    return _eigen(_befehle.abbild_abschnitt_erster_absatz(kennung, index))
