"""Beschriftungen, Textmarken, Querverweise, Stichwörter und Zitate — Funktionen am Editor (``KernEditor``).

Alles wirkt über die Bearbeitungssitzung auf das Dokumentmodell; Stellen im Text sind Zeichenstellen des Rohtextes (Absätze durch ein Zeichen getrennt,
wie ``textCursor().position()``).
"""
from __future__ import annotations

import re

from lunivo_writer.core.document.dokument import Auswahl, Lauf, Position
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene
from lunivo_writer.core.document.listen import listenmarken, nummer_text
from lunivo_writer.core.editing.suche import offset_zu_position, position_zu_offset
from lunivo_writer.editor.dokument.literatur import zitat

# ---- Beschriftungen ---------------------------------------------------------------------------------------
# Zahlschreibweise der Beschriftung (editor/text/zahlformat.py) ↔ Zahlenart des Modells ↔ Schalter des Felds SEQ
SEQ_FORMAT = {"arabisch": "ARABIC", "gross": "ALPHABETIC", "klein": "alphabetic", "roemisch": "ROMAN", "roemisch_klein": "roman"}
ZAHLENART = {"arabisch": "dezimal", "gross": "gross", "klein": "klein", "roemisch": "roem_gross", "roemisch_klein": "roem_klein"}


def seq_format(anweisung: str) -> str:
    """Zahlschreibweise aus einer Feldanweisung ``SEQ Abbildung \\* ROMAN`` (Vorgabe arabisch)."""
    m = re.search(r"\\\*\s*(\w+)", anweisung)
    if m:
        for k, v in SEQ_FORMAT.items():
            if v == m.group(1):
                return k
    return "arabisch"


def _seq_lauf(a):
    """(Versatz, Lauf) des SEQ-Feldes eines Absatzes, sonst ``None``."""
    versatz = 0
    for x in a.inhalte:
        n = len(x.text) if isinstance(x, Lauf) else 1
        if isinstance(x, Lauf) and str(x.format.get("feld", "")).upper().startswith("SEQ"):
            return versatz, x
        versatz += n
    return None


def beschriftungen_liste(ed) -> list[dict]:
    """[{label, text, pos, block}] — die Beschriftungsabsätze in Dokumentreihenfolge (``pos``: Stelle im Rohtext, ``block``: Id des Absatzes)."""
    d = ed.sitzung.dokument
    aus, n = [], 0
    for a in d.absaetze():
        if a.format.get("beschriftung") and a.text().strip():
            aus.append({"label": a.format["beschriftung"], "text": a.text().strip(), "pos": n, "block": a.id})
        n += a.laenge + 1
    return aus


def naechste_nummer(ed, label: str, zahl: str = "arabisch") -> str:
    """Nummer, die eine neue Beschriftung ``label`` an der Schreibmarke bekäme (für die Anzeige im Fenster)."""
    pos = ed.textCursor().position()
    n = 1 + sum(1 for k in beschriftungen_liste(ed) if k["label"] == label and k["pos"] < pos)
    return nummer_text(ZAHLENART.get(zahl, "dezimal"), n)


def beschriftung_einfuegen(ed, label: str, text: str, oben: bool = False, *, nach: str | None = None,
                           ohne_bezeichnung: bool = False, zahl: str = "arabisch") -> None:
    """Beschriftung „Abbildung 1: Text“ unter (``oben``: über) dem Objekt oder Absatz. ``nach`` ersetzt „: Text“ durch genau diesen
    Text hinter der Nummer, ``ohne_bezeichnung`` lässt „Abbildung “ weg, ``zahl`` ist die Schreibweise der Nummer."""
    s = ed.sitzung
    t = ed.tabelle_an_marke()
    if t is not None:
        block = t.id
    else:
        block = s.auswahl.kopf.absatz_id
    schluss = nach if nach is not None else (": " + text if text else "")

    def f(sitz):
        with sitz.gruppe("Beschriftung"):
            neu = sitz.beschriftung_einfuegen(label, "", block, davor=oben, zahlenart=ZAHLENART.get(zahl, "dezimal"))
            a = sitz._absatz(neu)
            if ohne_bezeichnung:                                    # „Abbildung “ vor der Nummer weglassen
                sitz.loeschen(Auswahl(Position(neu, 0), Position(neu, len(label) + 1)))
            if schluss:
                sitz.text_einfuegen(schluss, Position(neu, sitz._absatz(neu).laenge))
            sitz.absatzformat_anwenden({"abstand_vor": 4 / 0.75, "abstand_nach": 8 / 0.75}, absatz_ids=[neu])
            sitz.zeichenformat_anwenden({"kursiv": True, "groesse_pt": 9.0, "farbe": "#44546a"}, Auswahl(Position(neu, 0), Position(neu, sitz._absatz(neu).laenge)))
            sitz.setze_auswahl(Position(neu, sitz._absatz(neu).laenge))
    ed.ansicht._aendern(f)


def beschriftungen_nummerieren(ed) -> None:
    ed.ansicht._aendern(lambda s: s.beschriftungen_nummerieren())


# ---- Textmarken ------------------------------------------------------------------------------------------------
def lesezeichen_liste(ed, versteckte: bool = True) -> list[dict]:
    """[{name, von, bis}] — Textmarken mit ihren Stellen im Rohtext. ``versteckte=False`` lässt die Marken weg, die mit „_“ beginnen
    (z. B. „_Toc…“ des Inhaltsverzeichnisses)."""
    d = ed.sitzung.dokument
    aus = [{"name": n, "von": position_zu_offset(d, a.anker), "bis": position_zu_offset(d, a.kopf)} for n, a in ed.sitzung.textmarken().items()]
    return sorted((x for x in aus if versteckte or not x["name"].startswith("_")), key=lambda x: x["von"])


_NAME = re.compile(r"^[A-Za-zÄÖÜäöüß][A-Za-z0-9ÄÖÜäöüß_]{0,39}$")


def lesezeichen_name_gueltig(name: str) -> bool:
    return bool(_NAME.match(name))


def lesezeichen_setzen(ed, name: str) -> bool:
    """Setzt die Textmarke auf die Auswahl (ohne Auswahl: auf das Wort an der Schreibmarke); eine gleichnamige wird versetzt."""
    s = ed.sitzung
    if s.auswahl.leer and not s._absatz(s.auswahl.kopf.absatz_id).text():
        return False
    return ed.ansicht._aendern(lambda sitz: sitz.textmarke_setzen(name))


def lesezeichen_loeschen(ed, name: str) -> None:
    ed.ansicht._aendern(lambda s: s.textmarke_loeschen(name))


def lesezeichen_gehe(ed, name: str) -> bool:
    for d in lesezeichen_liste(ed):
        if d["name"] == name:
            ed.select_range(d["von"], d["bis"])
            ed.ensureCursorVisible()
            return True
    return False


def intern_springen(ed, href: str) -> bool:
    return href.startswith("#") and lesezeichen_gehe(ed, href[1:])


# ---- Querverweise -----------------------------------------------------------------------------------------------
# Verweistyp → was eingefügt werden kann („Verweisen auf“), in der Reihenfolge des Fensters
VERWEISTYPEN = ["Nummeriertes Element", "Überschrift", "Textmarke", "Fußnote", "Endnote", "Abbildung", "Tabelle", "Gleichung"]
VERWEISEN_AUF = {
    "Nummeriertes Element": [("seite", "Seitenzahl"), ("nummer", "Absatznummer"), ("text", "Absatztext"), ("obenunten", "Oben/unten")],
    "Überschrift": [("text", "Überschriftentext"), ("seite", "Seitenzahl"), ("nummer", "Überschriftennummer"), ("obenunten", "Oben/unten")],
    "Textmarke": [("text", "Textmarkeninhalt"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
    "Fußnote": [("nummer", "Fußnotennummer"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
    "Endnote": [("nummer", "Endnotennummer"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
}
_BESCHRIFTUNG_AUF = [("text", "Vollständige Beschriftung"), ("nummer", "Nur Bezeichnung und Nummer"), ("nur_text", "Nur Beschriftungstext"),
                     ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")]


def verweisen_auf(art: str) -> list[tuple[str, str]]:
    return VERWEISEN_AUF.get(art, _BESCHRIFTUNG_AUF)


_AUFZAEHLUNG = ("•", "◦", "▪", "–", "-")                 # Listenzeichen ohne Nummer: kein Ziel für einen Querverweis


def _ziele_absaetze(ed) -> list[dict]:
    """Überschriften und nummerierte Absätze."""
    d = ed.sitzung.dokument
    marken = listenmarken(d)
    z, n = [], 0
    for a in d.absaetze():
        text = a.text().strip()
        nummer = marken.get(a.id, "").strip()
        ort = {"pos": n, "block": a.id, "von": n, "bis": n + a.laenge, "nummer": nummer}
        if ueberschriftsebene(d, a) and text:
            z.append({"art": "Überschrift", "text": text, **ort})
        elif nummer and not nummer.startswith(_AUFZAEHLUNG) and text:
            z.append({"art": "Nummeriertes Element", "text": f"{nummer} {text}", **ort, "inhalt": text})
        n += a.laenge + 1
    return z


def _bezeichnung_nummer(a) -> str:
    """„Abbildung 2“ — der Text der Beschriftung bis einschließlich der Nummer."""
    f = _seq_lauf(a)
    return a.text()[:f[0] + len(f[1].text)].strip() if f else ""


def _beschriftungstext(a) -> str:
    """Der Text hinter der Nummer, ohne Doppelpunkt."""
    f = _seq_lauf(a)
    rest = a.text()[f[0] + len(f[1].text):] if f else a.text()
    return re.sub(r"^\s*[:.–-]?\s*", "", rest).strip()


def _ziele_beschriftungen(ed) -> list[dict]:
    d = ed.sitzung.dokument
    z = []
    for k in beschriftungen_liste(ed):
        a = ed.sitzung._absatz(k["block"])
        z.append({"art": k["label"], "text": k["text"], "pos": k["pos"], "block": a.id, "von": k["pos"], "bis": k["pos"] + a.laenge,
                  "nummer": _bezeichnung_nummer(a) or k["text"], "inhalt": _beschriftungstext(a)})
    return z


def _ziele_textmarken(ed) -> list[dict]:
    marken = lesezeichen_liste(ed, versteckte=False)
    text = ed.sitzung.text() if marken else ""
    return [{"art": "Textmarke", "text": d["name"], "pos": d["von"], "name": d["name"], "inhalt": text[d["von"]:d["bis"]].replace("\n", " ")} for d in marken]


def _ziele_noten(ed) -> list[dict]:
    """Fußnoten (1, 2, …) und Endnoten (i, ii, …) in Textreihenfolge."""
    z = []
    zaehler = {"f": 0, "e": 0}
    for n in ed.noten_stellen():
        zaehler[n["art"]] += 1
        nr = str(zaehler[n["art"]]) if n["art"] == "f" else nummer_text("roem_klein", zaehler[n["art"]])
        text = ((ed.noten or {}).get(n["art"], {}) or {}).get(n["id"], "")
        z.append({"art": "Fußnote" if n["art"] == "f" else "Endnote", "text": f"{nr} {text}".strip(), "pos": n["von"], "von": n["von"], "bis": n["bis"], "nummer": nr})
    return z


def querverweis_ziele(ed) -> list[dict]:
    """Mögliche Ziele: nummerierte Absätze, Überschriften, Textmarken, Fuß- und Endnoten, Beschriftungen.
    Jedes Ziel: art, text (Anzeige), pos, von/bis (Bereich für die Textmarke), nummer (wenn es eine hat)."""
    return _ziele_absaetze(ed) + _ziele_beschriftungen(ed) + _ziele_textmarken(ed) + _ziele_noten(ed)


def marke_sichern(ed, ziel: dict) -> str:
    """Name der Textmarke am Ziel. Fehlt eine, bekommt der Bereich des Ziels eine verborgene Textmarke „_Ref…“."""
    if "name" in ziel:
        return ziel["name"]
    von, bis = ziel["von"], ziel["bis"]
    if bis <= von:
        bis = von + 1
    vorhanden = set()
    for d in lesezeichen_liste(ed):
        vorhanden.add(d["name"])
        if d["von"] == von and d["bis"] == bis and d["name"].startswith(("_Ref", "Ziel_")):
            return d["name"]
    n = 1
    while f"_Ref{n:06d}" in vorhanden:
        n += 1
    name = f"_Ref{n:06d}"
    dok = ed.sitzung.dokument
    ed.ansicht._aendern(lambda s: s.textmarke_setzen(name, Auswahl(offset_zu_position(dok, von), offset_zu_position(dok, bis))))
    return name


def querverweis_text(ed, ziel: dict, wie: str, oben_unten: bool = False) -> str:
    from .verweise_fach_kern import querverweis_text_bilden
    seitenzahl = None
    if wie == "seite":
        seitenzahl = ed.seiten_von([ziel["pos"]])[0]
    return querverweis_text_bilden(ziel, wie, ed.textCursor().position(), seitenzahl, oben_unten)


def querverweis_einfuegen(ed, ziel: dict, wie: str, *, link: bool = True, oben_unten: bool = False) -> None:
    """Querverweis an der Schreibmarke (siehe ``querverweis_text``); ``link`` macht ihn zum internen Hyperlink (Strg+Klick)."""
    text = querverweis_text(ed, ziel, wie, oben_unten)
    name = marke_sichern(ed, ziel) if link else ""

    def f(s):
        with s.gruppe("Querverweis"):
            if name:
                s.querverweis_einfuegen(name, text)
            else:
                s.text_einfuegen(text)
            s.text_einfuegen(" ", format={})
    ed.ansicht._aendern(f)


# ---- Stichwörter -------------------------------------------------------------------------------------------------------
def index_eintragen(ed, e, alle: bool = False) -> int:
    """Indexeintrag ``e`` (``editor.dokument.indexeintrag.Eintrag``) an die Markierung setzen (ohne Markierung: das Wort an der
    Schreibmarke); ``alle`` markiert jede Stelle im Dokument mit demselben Text. Gibt die Zahl der markierten Stellen zurück."""
    s = ed.sitzung
    if not e.haupt:
        return 0
    start, ende = s._bereich_oder_wort(None)
    stellen = [Auswahl(start, ende)]
    if alle:
        such = s.text(Auswahl(start, ende))
        stellen = s.suche(such, gross_klein=True) or stellen
    zaehler = [0]

    def f(sitz):
        with sitz.gruppe("Indexeintrag"):
            for st in stellen:
                sitz.index_eintragen(e.text(), e.schalter(), st)
                zaehler[0] += 1
    ed.ansicht._aendern(f)
    return zaehler[0]


def index_markieren(ed, term: str) -> bool:
    s = ed.sitzung
    try:
        start, ende = s._bereich_oder_wort(None)
    except Exception:
        return False
    return ed.ansicht._aendern(lambda sitz: sitz.index_eintragen(term or sitz.text(Auswahl(start, ende)), "", Auswahl(start, ende)))


# ---- Zitate ----------------------------------------------------------------------------------------------------------------
def zitat_einfuegen(ed, q: dict) -> None:
    quellen = ed.quellen
    nr = 1 + [x["tag"] for x in quellen].index(q["tag"]) if q["tag"] in [x["tag"] for x in quellen] else 1
    text = zitat(q, ed.zitierweise, nr)

    def f(s):
        with s.gruppe("Zitat"):
            if not any(x.get("tag") == q["tag"] for x in s.dokument.quellen):
                s.quelle_setzen(q)
            s.zitat_einfuegen(q["tag"], text)
            s.text_einfuegen(" ", format={})
    ed.ansicht._aendern(f)


def quelle_tag(quellen: list[dict], q: dict) -> str:
    from .verweise_fach_kern import quelle_tag_bilden
    return quelle_tag_bilden(quellen, q)
