from __future__ import annotations
from writer.funktionen.objekte import formular as FW
from writer.funktionen.objekte.formular import formular_datumsformat, Feldbeschreibung, meta  # noqa: F401  (Namen der Oberfläche)


# ---- Änderungen am Dokument: Befehle des Frameworks anhand der Kennung des Dokuments ------------------------------------------------------
def einfuegen(ed, m: Feldbeschreibung, wert: str | None = None) -> None:
    """Feld an der Schreibmarke (oder anstelle der Markierung) einfügen."""
    ed.ansicht._befehl(lambda: FW.einfuegen(ed.kennung, m, wert))


def alle_zuruecksetzen(ed) -> int:
    """Alle Felder auf ihren Anfangswert (Platzhalter, leeres Kästchen) zurücksetzen. → Zahl der zurückgesetzten Felder."""
    zahl = [0]

    def f() -> bool:
        zahl[0] = FW.alle_zuruecksetzen(ed.kennung)
        return True
    ed.ansicht._befehl(f)
    return zahl[0]


def nur_formulardaten(kennung: int) -> int:
    """„Nur Formulardaten drucken“ in der KOPIE hinter ``anschluss`` (Änderungs-Port). → Zahl der Felder."""
    return FW.nur_formulardaten(kennung)


def wert_von(ed, v: int, e: int) -> str:
    return FW.wert_von(ed.kennung, v, e)


def _ersetzen(ed, v: int, e: int, m: Feldbeschreibung, text: str, leer: bool = False) -> None:
    ed.ansicht._befehl(lambda: FW.ersetzen(ed.kennung, v, e, m, text, leer))


def _ist_leer(ed, pos: int) -> bool:
    return FW.ist_leer(ed.kennung, pos)


def _klick_kasten(ed, v: int, e: int, m: Feldbeschreibung, fenster) -> None:
    ed.ansicht._befehl(lambda: FW.kasten_umschalten(ed.kennung, v, e, m))


def _klick_knopf(ed, v: int, e: int, m: Feldbeschreibung, fenster) -> None:
    """Die Aktion der Schaltfläche: Felder zurücksetzen, Drucken oder als PDF exportieren."""
    fenster = fenster or ed.fenster
    a = m.aktion or "Keine"
    if a == FW.formular_aktion_zuruecksetzen():
        alle_zuruecksetzen(ed)
    elif a == FW.formular_aktion_drucken() and hasattr(fenster, "print_dialog"):
        fenster.print_dialog()
    elif a == FW.formular_aktion_pdf() and hasattr(fenster, "export_pdf_dialog"):
        fenster.export_pdf_dialog()


class _Eingabe:
    """Wer fragt den Benutzer nach Datum oder Text eines Formularfeldes? Die Oberfläche setzt ``eingabe_anbieter`` beim Start auf ihr
    ``EingabeFenster``; der Editor kennt die Oberfläche nicht. Ohne Anbieter fragt das Standardfenster von Qt."""

    @staticmethod
    def getDatum(eltern, titel, frage="Datum:", datum=None):
        from PySide6.QtCore import QDate
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(eltern, titel, frage, text=(datum or QDate.currentDate()).toString(formular_datumsformat()))
        tag = QDate.fromString(text, formular_datumsformat())
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


def _klick_auswahl(ed, v: int, e: int, m: Feldbeschreibung, fenster) -> None:
    from PySide6.QtGui import QCursor
    eingabe_anbieter.zeigeAuswahl(ed.widget(), m.optionen, QCursor.pos(), lambda o: _ersetzen(ed, v, e, m, o))


def _klick_datum(ed, v: int, e: int, m: Feldbeschreibung, fenster) -> None:
    from PySide6.QtCore import QDate
    aktuell = QDate.fromString(wert_von(ed, v, e), formular_datumsformat())
    tag, ok = eingabe_anbieter.getDatum(fenster or ed.widget().window(), m.name or "Datum", "Datum:", aktuell)
    if ok:
        _ersetzen(ed, v, e, m, tag.toString(formular_datumsformat()))


def _klick_text(ed, v: int, e: int, m: Feldbeschreibung, fenster) -> None:
    alt = "" if _ist_leer(ed, v) else wert_von(ed, v, e)
    t, ok = eingabe_anbieter.getText(fenster or ed.widget().window(), m.name or "Textfeld", m.name or "Wert:", text=alt)
    if not ok:
        return
    if t:
        _ersetzen(ed, v, e, m, t)
    else:                                                  # geleert: das Feld zeigt wieder seinen Platzhalter
        _ersetzen(ed, v, e, m, m.platzhalter or "Text eingeben", leer=True)


# Art des Feldes → was ein Klick darauf tut
_KLICK = {"kasten": _klick_kasten, "auswahl": _klick_auswahl, "datum": _klick_datum, "text": _klick_text, "knopf": _klick_knopf}


def klick(ed, pos: int, fenster=None) -> bool:
    """Klick in ein Feld: Kontrollkästchen wechselt, Auswahl zeigt die Liste, Text und Datum fragen nach dem Wert, die Schaltfläche löst
    ihre Aktion aus. → True, wenn der Klick ein Feld getroffen hat."""
    treffer = FW.feld_an(ed.kennung, pos)
    if treffer is None:
        return False
    m = treffer.feld
    tun = _KLICK.get(m.art)
    if tun is not None:
        tun(ed, treffer.von, treffer.bis, m, fenster)
    return True
