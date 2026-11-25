"""Formular daten: aus ``vcl.qt.rendering.textfelder.formular`` herausgelöst."""
from __future__ import annotations
import json
from core.dokument.dokument import Position
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


def einfuegen(s, m: dict, wert: str | None = None) -> None:
    """Feld an der Schreibmarke (oder anstelle der Markierung) der Sitzung ``s`` einfügen."""
    text, leer = _anzeige(m, wert)
    with s.gruppe("Formularfeld"):
        s.text_einfuegen(text, format=_zeichenformat(m, leer))
        s.tippformat = {}                                  # was danach getippt wird, gehört nicht mehr zum Feld


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


def _auswahl(s, v: int, e: int):
    from core.dokument.dokument import Auswahl
    from core.suche.textsuche.suche import offset_zu_position
    d = s.dokument
    return Auswahl(offset_zu_position(d, v), offset_zu_position(d, e))


def ersetzen(s, v: int, e: int, m: dict, text: str, leer: bool = False) -> None:
    """Den Text des Feldes (Stellen ``v`` bis ``e``) in der Sitzung ``s`` ersetzen."""
    s.ersetzen(text, _auswahl(s, v, e), format=_zeichenformat(m, leer))


def wert_von(s, v: int, e: int) -> str:
    return s.text(_auswahl(s, v, e))


def kasten_umschalten(s, v: int, e: int, m: dict) -> None:
    """Das Kontrollkästchen wechselt zwischen leer und angekreuzt."""
    voll = wert_von(s, v, e) == KASTEN_VOLL
    ersetzen(s, v, e, m, KASTEN_LEER if voll else KASTEN_VOLL)


def ist_leer(s, pos: int) -> bool:
    treffer = feld_an(s.dokument, pos)
    return bool(treffer and treffer[2].get("leer"))


def alle_zuruecksetzen(s) -> int:
    """Alle Felder der Sitzung ``s`` auf ihren Anfangswert (Platzhalter, leeres Kästchen) zurücksetzen. → Zahl der zurückgesetzten Felder."""
    zaehler = 0
    with s.gruppe("Felder zurücksetzen"):
        for v, e, m in reversed(bereiche(s.dokument)):
            if m["art"] == "kasten":
                s.ersetzen(KASTEN_LEER, _auswahl(s, v, e), format=_zeichenformat(m))
            elif m["art"] in ("text", "auswahl", "datum"):
                ph = m.get("platzhalter") or {"text": "Text eingeben", "auswahl": "Auswahl treffen", "datum": "Datum wählen"}[m["art"]]
                s.ersetzen(ph, _auswahl(s, v, e), format=_zeichenformat(m, True))
            else:
                continue
            zaehler += 1
    return zaehler


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
