"""Änderungsrahmen: Jede Dokumentänderung, die das Framework ausführt, läuft hier durch.

Ablauf: Schreibschutz prüfen → Bearbeiter und Zeit für nachverfolgte Änderungen setzen → die Arbeit auf der Bearbeitungssitzung ausführen
(Rückgängig-Schritte bildet der Kern selbst) → ``dokument_geaendert`` melden. Die Oberfläche zeichnet auf diese Meldung hin neu; sie führt die
Änderung nicht selbst aus und bekommt keine Sitzung in die Hand."""
from __future__ import annotations

import datetime
from collections.abc import Callable

from core.bearbeitung import BearbeitungsFehler, Kontext
from framework.ereignisse import melder
from framework.schnittstellen.datentypen import Art, Ereignis
from framework.sitzungen import sitzung as _steuerung

GEAENDERT = "dokument_geaendert"
AUSWAHL = "auswahl_geaendert"                 # nur die Auswahl wurde gesetzt (Sprung): die Oberfläche zeigt die Stelle


def ausfuehren(kennung: int, arbeit: Callable[..., int]) -> int | None:
    """Führt ``arbeit(sitzung)`` für das Dokument ``kennung`` aus. → Ergebnis der Arbeit; ``None``, wenn das Dokument fehlt, schreibgeschützt ist
    oder der Kern die Änderung ablehnt."""
    satz = _steuerung._sitzungen.get(kennung)
    if satz is None or satz.nur_lesen:
        return None
    s = satz.sitzung
    s.autor = satz.bearbeiter
    s.datum = datetime.datetime.now().replace(microsecond=0).isoformat()
    try:
        ergebnis = arbeit(s)
    except BearbeitungsFehler:
        return None
    melder.melden(Ereignis(Art.GEAENDERT, GEAENDERT, {"kennung": kennung}))
    return ergebnis


def lesen(kennung: int, abfrage: Callable[..., int]) -> int | None:
    """``abfrage(sitzung)`` ohne Änderung des Dokuments; ``None``, wenn es das Dokument nicht gibt."""
    satz = _steuerung._sitzungen.get(kennung)
    return None if satz is None else abfrage(satz.sitzung)


def bewegen(kennung: int, arbeit: Callable[..., int]) -> int | None:
    """``arbeit(sitzung)`` setzt nur die Auswahl (Sprung); danach ``auswahl_geaendert`` melden. Auch bei Schreibschutz erlaubt."""
    satz = _steuerung._sitzungen.get(kennung)
    if satz is None:
        return None
    ergebnis = arbeit(satz.sitzung)
    if ergebnis:
        melder.melden(Ereignis(Art.GEAENDERT, AUSWAHL, {"kennung": kennung}))
    return ergebnis


def im_kontext_lesen(kennung: int, abfrage: Callable[..., int]) -> int | None:
    """``abfrage(kontext)`` mit dem Kontext des Dokuments (Layout mit den Optionen der Ansicht); ``None``, wenn es das Dokument nicht gibt."""
    satz = _steuerung._sitzungen.get(kennung)
    return None if satz is None else abfrage(Kontext(satz.sitzung, satz.layout_optionen))


def im_kontext_bewegen(kennung: int, arbeit: Callable[..., int]) -> int | None:
    """``arbeit(kontext)`` setzt nur die Auswahl; hat sie das getan, ``auswahl_geaendert`` melden. Auch bei Schreibschutz erlaubt."""
    satz = _steuerung._sitzungen.get(kennung)
    if satz is None:
        return None
    k = Kontext(satz.sitzung, satz.layout_optionen)
    ergebnis = arbeit(k)
    if k.bewegt:
        melder.melden(Ereignis(Art.GEAENDERT, AUSWAHL, {"kennung": kennung}))
    return ergebnis
