from __future__ import annotations
from core.objekte.textfelder.modell.formular_daten import DATUMSFORMAT, _ersetzen, _ist_leer, _klick_kasten, _klick_knopf, feld_an, wert_von


class _Eingabe:
    """Wer fragt den Benutzer nach Datum oder Text eines Formularfeldes? Die Oberfläche setzt ``eingabe_anbieter`` beim Start auf ihr
    ``EingabeFenster``; der Editor kennt die Oberfläche nicht. Ohne Anbieter fragt das Standardfenster von Qt."""

    @staticmethod
    def getDatum(eltern, titel, frage="Datum:", datum=None):
        from PySide6.QtCore import QDate
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(eltern, titel, frage, text=(datum or QDate.currentDate()).toString(DATUMSFORMAT))
        tag = QDate.fromString(text, DATUMSFORMAT)
        return (tag if tag.isValid() else QDate.currentDate()), ok and tag.isValid()

    @staticmethod
    def getText(eltern, titel, frage, text="", kennwort=False):
        from PySide6.QtWidgets import QInputDialog
        return QInputDialog.getText(eltern, titel, frage, text=text)

    @staticmethod
    def zeigeAuswahl(eltern, optionen, global_pos, gewaehlt) -> None:
        """Liste der Möglichkeiten an ``global_pos``; ein Eintrag ruft ``gewaehlt(eintrag)``."""
        from PySide6.QtWidgets import QInputDialog
        if not optionen:
            return
        wahl, ok = QInputDialog.getItem(eltern, "Auswahl", "Auswahl:", list(optionen), 0, False)
        if ok:
            gewaehlt(wahl)


eingabe_anbieter = _Eingabe


def _klick_auswahl(ed, v: int, e: int, m: dict, fenster) -> None:
    from PySide6.QtGui import QCursor
    eingabe_anbieter.zeigeAuswahl(ed.widget(), m.get("optionen") or [], QCursor.pos(), lambda o: _ersetzen(ed, v, e, m, o))


def _klick_datum(ed, v: int, e: int, m: dict, fenster) -> None:
    from PySide6.QtCore import QDate
    aktuell = QDate.fromString(wert_von(ed, v, e), DATUMSFORMAT)
    tag, ok = eingabe_anbieter.getDatum(fenster or ed.widget().window(), m.get("name") or "Datum", "Datum:", aktuell)
    if ok:
        _ersetzen(ed, v, e, m, tag.toString(DATUMSFORMAT))


def _klick_text(ed, v: int, e: int, m: dict, fenster) -> None:
    alt = "" if _ist_leer(ed, v) else wert_von(ed, v, e)
    t, ok = eingabe_anbieter.getText(fenster or ed.widget().window(), m.get("name") or "Textfeld", m.get("name") or "Wert:", text=alt)
    if not ok:
        return
    if t:
        _ersetzen(ed, v, e, m, t)
    else:                                                  # geleert: das Feld zeigt wieder seinen Platzhalter
        _ersetzen(ed, v, e, m, m.get("platzhalter") or "Text eingeben", leer=True)


# Art des Feldes → was ein Klick darauf tut
_KLICK = {"kasten": _klick_kasten, "auswahl": _klick_auswahl, "datum": _klick_datum, "text": _klick_text, "knopf": _klick_knopf}


def klick(ed, pos: int, fenster=None) -> bool:
    """Klick in ein Feld: Kontrollkästchen wechselt, Auswahl zeigt die Liste, Text und Datum fragen nach dem Wert, die Schaltfläche löst
    ihre Aktion aus. → True, wenn der Klick ein Feld getroffen hat."""
    treffer = feld_an(ed.sitzung.dokument, pos)
    if treffer is None:
        return False
    v, e, m = treffer
    tun = _KLICK.get(m["art"])
    if tun is not None:
        tun(ed, v, e, m, fenster)
    return True
