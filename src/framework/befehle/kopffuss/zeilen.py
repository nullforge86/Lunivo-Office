"""Kopf- und Fußzeile eines Abschnitts als Text mit Ausrichtung setzen (Fenster „Kopf- und Fußzeile“) und die Seitenzahl in die Fußzeile
einfügen – anhand der Kennung des Dokuments und der Nummer des Abschnitts."""
from __future__ import annotations

from framework.befehle.kopffuss.typen import BlattZeilen
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


def blatt_zeilen(kennung: int, abschnitt: int, blatt: int) -> BlattZeilen:
    """Die Kopf- und Fußzeile, die das Blatt ``blatt`` (ab 0) mit der Einrichtung des Abschnitts trägt (erste Seite anders, gerade Seiten anders),
    seine angezeigte Seitenzahl und die wirksame Ausrichtung („außen“ und „innen“ aufgelöst) – für das Bearbeiten direkt auf der Seite."""
    import core.dokument.kopf_fusszeilen as _k
    abschnitte = _sitzung(kennung).dokument.abschnitte
    seite = abschnitte[max(0, min(abschnitt, len(abschnitte) - 1))].seite
    nummer = _k.erste_nummer(seite) + max(0, blatt)
    art = seite.kopf_fuss_art(max(0, blatt) + 1, nummer)
    kopf, fuss = (art + "_" if art else "") + "header", (art + "_" if art else "") + "footer"
    return BlattZeilen(kopf, fuss, _k.nummer(nummer, seite), _k.ausrichtung(getattr(seite, kopf).align, max(0, blatt) + 1),
                       _k.ausrichtung(getattr(seite, fuss).align, max(0, blatt) + 1), art)


def seitenzahl_loeschen(kennung: int, abschnitt: int, art: str, blatt: int) -> bool | None:
    """Seitenzahl entfernen: ``art`` „dokument“ (alle Abschnitte), „abschnitt“, „aktuelle“ (nur Blatt ``blatt``, ab 0), „auf“ (bis einschließlich)
    oder „von“ (ab dem Blatt). ``True``: geändert; ``False``: es gab keine Seitenzahl oder der Kern lehnt ab; ``None``: so nicht darstellbar."""
    import core.dokument.kopf_fusszeilen as _k
    s = _sitzung(kennung)
    if art == "dokument":
        gab = False
        with s.gruppe("Seitenzahl löschen"):
            for index, eintrag in enumerate(s.dokument.abschnitte):
                seite = eintrag.seite.copy()
                if _k.seitenzahlen_entfernen(seite):
                    gab = _ersetzen(s, index, seite) or gab
        return gab
    seite = s.dokument.abschnitte[abschnitt].seite.copy()
    ergebnis = _k.seitenzahl_loeschen_bereich(seite, art, blatt)
    if ergebnis:
        return _ersetzen(s, abschnitt, seite)
    return ergebnis


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
