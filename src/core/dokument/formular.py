"""Formularfelder (Inhaltssteuerelemente): Textfeld, Auswahlliste, Datum, Kontrollkästchen, Schaltfläche.

Ein Feld ist ein Textstück mit dem Zeichenformat ``formular`` (JSON: Art, Name, Optionen …); sein Text ist der eingegebene Wert. In DOCX werden
Felder als Inhaltssteuerelemente (`w:sdt`) gespeichert und wieder gelesen. „Nur Formulardaten drucken“ druckt nur die Feldinhalte (für
vorgedruckte Formulare); der übrige Text, Bilder und Seitenschmuck fehlen im Ausdruck.
"""
from __future__ import annotations

import json

from PySide6.QtCore import Qt

from core.dokument.dokument import Position



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
from core.formatierung.farben.farben import Farbe
ARTEN = ("text", "auswahl", "datum", "kasten", "knopf")
KASTEN_LEER, KASTEN_VOLL = "☐", "☒"
AKTIONEN = ["Keine", "Drucken", "Als PDF exportieren", "Felder zurücksetzen"]
DATUMSFORMAT = "dd.MM.yyyy"
PLATZHALTER_FARBE = Farbe.GRAU


def meta(art: str, name: str = "", **kw) -> dict:
    m = {"art": art, "name": name}
    m.update({k: v for k, v in kw.items() if v not in (None, "")})
    return m


def meta_text(m: dict) -> str:
    return json.dumps(m, ensure_ascii=False, separators=(",", ":"))


def meta_lesen(s: str) -> dict | None:
    try:
        m = json.loads(s)
        return m if isinstance(m, dict) and m.get("art") in ARTEN else None
    except (TypeError, ValueError):
        return None


_PLATZHALTER = {"auswahl": "Auswahl treffen", "datum": "Datum wählen"}      # Vorgabe je Art; sonst „Text eingeben“


def _anzeige(m: dict, wert: str | None) -> tuple[str, bool]:
    """(Text des Feldes, zeigt nur den Platzhalter) für ein neues Feld mit dem Wert ``wert``."""
    art = m["art"]
    if art == "kasten":
        return (KASTEN_VOLL if wert == "1" else KASTEN_LEER), False
    if art == "knopf":
        return f"  {m.get('aufschrift') or 'Schaltfläche'}  ", False
    vorgabe = _PLATZHALTER.get(art, "Text eingeben")
    if art == "auswahl" and wert is None and m.get("optionen") and not m.get("platzhalter"):
        return vorgabe, True
    return (wert or m.get("platzhalter") or vorgabe), not wert


def einfuegen(ed, m: dict, wert: str | None = None) -> None:
    """Feld an der Schreibmarke (oder anstelle der Markierung) einfügen."""
    text, leer = _anzeige(m, wert)

    def f(s):
        with s.gruppe("Formularfeld"):
            s.text_einfuegen(text, format=_zeichenformat(m, leer))
            s.tippformat = {}                              # was danach getippt wird, gehört nicht mehr zum Feld
    ed.ansicht._aendern(f)


def _zeichenformat(m: dict, leer: bool = False) -> dict:
    """Das Zeichenformat eines Feldes im Dokumentmodell (``formular``: die Daten als Text)."""
    m = {k: v for k, v in m.items() if k != "leer"}
    fmt = {"formular": meta_text(dict(m, leer=True) if leer else m)}
    if leer:
        fmt["farbe"] = PLATZHALTER_FARBE
    if m["art"] == "knopf":
        fmt.update(fett=True, marker="#dee2e6")
    if m["art"] == "kasten":
        fmt["groesse_pt"] = 14.0
    return fmt


def bereiche(dok) -> list[tuple[int, int, dict]]:
    """[(von, bis, Feld-Daten)] aller Felder (Stellen im Rohtext); zusammenhängende Stücke mit gleichen Daten sind ein Feld."""
    out: list[list] = []
    n = 0
    for a in dok.absaetze():
        versatz = 0
        for x in a.inhalte:
            laenge = len(x.text) if hasattr(x, "text") else 1
            roh = x.format.get("formular")
            if roh:
                s = roh if isinstance(roh, str) else meta_text(roh)
                v, e = n + versatz, n + versatz + laenge
                if out and out[-1][1] == v and out[-1][2] == s:
                    out[-1][1] = e
                else:
                    out.append([v, e, s])
            versatz += laenge
        n += a.laenge + 1
    res = []
    for v, e, s in out:
        m = meta_lesen(s)
        if m:
            res.append((v, e, m))
    return res


def feld_an(dok, pos: int):
    for v, e, m in bereiche(dok):
        if v <= pos <= e:
            return v, e, m
    return None


def _auswahl(ed, v: int, e: int):
    from core.dokument.dokument import Auswahl
    from core.suche.textsuche.suche import offset_zu_position
    d = ed.sitzung.dokument
    return Auswahl(offset_zu_position(d, v), offset_zu_position(d, e))


def _ersetzen(ed, v: int, e: int, m: dict, text: str, leer: bool = False) -> None:
    ed.ansicht._aendern(lambda s: s.ersetzen(text, _auswahl(ed, v, e), format=_zeichenformat(m, leer)))


def wert_von(ed, v: int, e: int) -> str:
    return ed.sitzung.text(_auswahl(ed, v, e))


def _klick_kasten(ed, v: int, e: int, m: dict, fenster) -> None:
    voll = wert_von(ed, v, e) == KASTEN_VOLL
    _ersetzen(ed, v, e, m, KASTEN_LEER if voll else KASTEN_VOLL)


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


def _klick_knopf(ed, v: int, e: int, m: dict, fenster) -> None:
    _knopf_aktion(ed, m, fenster or ed.fenster)


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


def _ist_leer(ed, pos: int) -> bool:
    treffer = feld_an(ed.sitzung.dokument, pos)
    return bool(treffer and treffer[2].get("leer"))


def _knopf_aktion(ed, m: dict, fenster) -> None:
    a = m.get("aktion", "Keine")
    if a == "Felder zurücksetzen":
        alle_zuruecksetzen(ed)
    elif a == "Drucken" and hasattr(fenster, "print_dialog"):
        fenster.print_dialog()
    elif a == "Als PDF exportieren" and hasattr(fenster, "export_pdf_dialog"):
        fenster.export_pdf_dialog()


def alle_zuruecksetzen(ed) -> int:
    """Alle Felder auf ihren Anfangswert (Platzhalter, leeres Kästchen) zurücksetzen."""
    zaehler = [0]

    def f(s):
        with s.gruppe("Felder zurücksetzen"):
            for v, e, m in reversed(bereiche(s.dokument)):
                if m["art"] == "kasten":
                    s.ersetzen(KASTEN_LEER, _auswahl(ed, v, e), format=_zeichenformat(m))
                elif m["art"] in ("text", "auswahl", "datum"):
                    ph = m.get("platzhalter") or {"text": "Text eingeben", "auswahl": "Auswahl treffen", "datum": "Datum wählen"}[m["art"]]
                    s.ersetzen(ph, _auswahl(ed, v, e), format=_zeichenformat(m, True))
                else:
                    continue
                zaehler[0] += 1
    ed.ansicht._aendern(f)
    return zaehler[0]


def daten(dok) -> list[tuple[str, str]]:
    """[(Name, Wert)] aller Felder mit Wert (ohne Platzhalter und Schaltflächen)."""
    from core.suche.textsuche.suche import roh_text
    text = roh_text(dok)
    out = []
    for v, e, m in bereiche(dok):
        if m["art"] == "knopf" or m.get("leer"):
            continue
        w = text[v:e]
        out.append((m.get("name") or m["art"], "ja" if (m["art"] == "kasten" and w == KASTEN_VOLL) else
                    ("" if m["art"] == "kasten" else w)))
    return out


def nur_formulardaten(dok) -> int:
    """„Nur Formulardaten drucken“ in der KOPIE ``dok``: Text außerhalb der Felder wird unsichtbar, Bilder entfallen. → Zahl der Felder."""
    from core.dokument.dokument import Auswahl
    from core.bearbeitung import Bearbeitungssitzung
    from core.suche.textsuche.suche import offset_zu_position
    s = Bearbeitungssitzung(dok)
    for oid in list(dok.objekte):
        s.objekt_entfernen(oid)
    felder = bereiche(dok)
    ende = sum(a.laenge + 1 for a in dok.absaetze()) - 1
    frei, pos = [], 0
    for v, e, _m in sorted(felder):
        if v > pos:
            frei.append((pos, v))
        pos = max(pos, e)
    frei.append((pos, max(pos, ende)))
    for v, e in reversed(frei):
        if e > v:
            for a, von, bis in s._stuecke(offset_zu_position(dok, v), offset_zu_position(dok, e)):
                s.zeichenformat_anwenden({"farbe": "#00000000", "marker": None, "unterstrichen": None}, Auswahl(Position(a.id, von), Position(a.id, bis)))
    return len(felder)
