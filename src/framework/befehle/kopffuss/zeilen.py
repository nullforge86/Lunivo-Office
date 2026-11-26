"""Kopf- und Fußzeile eines Abschnitts als Text mit Ausrichtung setzen (Fenster „Kopf- und Fußzeile“) und die Seitenzahl in die Fußzeile
einfügen – anhand der Kennung des Dokuments und der Nummer des Abschnitts."""
from __future__ import annotations

from framework.sitzungen import sitzung as _steuerung

ZEILEN = ("header", "footer", "first_header", "first_footer")


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _ersetzen(s, abschnitt: int, seite) -> bool:
    from core.bearbeitung import BearbeitungsFehler
    try:
        s.seite_ersetzen(abschnitt, seite)
    except BearbeitungsFehler:
        return False
    return True


def zeile_setzen(kennung: int, abschnitt: int, zeile: str, text: str, ausrichtung: str) -> bool:
    """Die Zeile (einer der Namen aus ``ZEILEN``) des Abschnitts durch Text mit Ausrichtung ersetzen; ``False``, wenn der Kern ablehnt."""
    from core.dokument.abschnitte import HeaderFooter
    if zeile not in ZEILEN:
        raise ValueError(zeile)
    s = _sitzung(kennung)
    seite = s.dokument.abschnitte[abschnitt].seite.copy()
    setattr(seite, zeile, HeaderFooter(text, ausrichtung))
    return _ersetzen(s, abschnitt, seite)


def seitenzahl_einfuegen(kennung: int, abschnitt: int) -> bool:
    """Die Seitenzahl in die Fußzeile des Abschnitts setzen: eine leere Fußzeile bekommt sie mittig, sonst wird sie angehängt."""
    from core.dokument.abschnitte import HeaderFooter
    s = _sitzung(kennung)
    seite = s.dokument.abschnitte[abschnitt].seite.copy()
    if seite.footer.is_empty():
        seite.footer = HeaderFooter("{PAGE}", "center")
    elif "{PAGE}" not in seite.footer.text:
        seite.footer.text += " {PAGE}"
    return _ersetzen(s, abschnitt, seite)
