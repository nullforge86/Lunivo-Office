"""„Gehe zu“: Sprungziele im Dokument — Seite, Zeile (Absatz), Überschrift, Textmarke, Kommentar, Fußnote, Endnote, Tabelle, Bild,
Beschriftung, Abschnitt. Die Oberfläche ist der Reiter „Gehe zu“ im Feld „Suchen und ersetzen“ (oberflaeche/dokument/dokumentfenster/suchen_feld.py).

Alle Stellen sind Zeichenstellen im Rohtext (Absätze durch ein Zeichen getrennt, wie ``textCursor().position()``)."""
from __future__ import annotations

from core.bearbeitung import Kontext

from core.dokument.dokument import InlineObjekt, Tabelle
from core.suche.textsuche.suche import position_zu_offset
from core.verzeichnisse.abbildungsverzeichnis import beschriftung
from core.referenzen.querverweise import querverweis
from core.referenzen.querverweise import textmarke

NUMMERN = ("Seite", "Zeile")                                    # man gibt eine Zahl ein
LISTEN = ("Überschrift", "Textmarke", "Beschriftung", "Kommentar", "Fußnote", "Endnote", "Tabelle", "Bild", "Abschnitt")
ARTEN = NUMMERN + LISTEN


def _kurz(t: str, n: int = 60) -> str:
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1] + "…"


def _stellen(dok) -> dict:
    """Absatz-Id → Stelle des Absatzanfangs im Rohtext."""
    aus, n = {}, 0
    for a in dok.absaetze():
        aus[a.id] = n
        n += a.laenge + 1
    return aus


def _seitenzahl(ed) -> int:
    return max(1, len(ed.ansicht.ergebnis().seiten))


def maximum(ed, art: str) -> int:
    """Obergrenze für Seite und Zeile."""
    return _seitenzahl(ed) if art == "Seite" else max(1, sum(1 for _ in ed.sitzung.dokument.absaetze()))


def seitenstart(ed, n: int) -> int:
    """Stelle des ersten Textes auf der Seite ``n`` (ab 1); hat die Seite keinen Text, der Anfang der nächsten mit Text."""
    erg = ed.ansicht.ergebnis()
    stellen = _stellen(ed.sitzung.dokument)
    for seite in erg.seiten[max(0, min(n, len(erg.seiten)) - 1):]:
        for p in seite.plaetze:
            if p.art == "zeile" and not p.kopie and p.block_id in stellen:
                return stellen[p.block_id]
    return 0


def zeilenstart(ed, n: int) -> int:
    absaetze = list(ed.sitzung.dokument.absaetze())
    return _stellen(ed.sitzung.dokument)[absaetze[max(0, min(n, len(absaetze)) - 1)].id]


def _ziele_ueberschrift(ed):
    return [(z["text"], z["pos"]) for z in querverweis.querverweis_ziele(Kontext(ed.sitzung)) if z["art"] == "Überschrift"]


def _ziele_textmarke(ed):
    return [(d["name"], d["von"]) for d in textmarke.lesezeichen_liste(Kontext(ed.sitzung), versteckte=False)]


def _ziele_beschriftung(ed):
    return [(f"{k['label']}: {_kurz(k['text'])}", k["pos"]) for k in beschriftung.beschriftungen_liste(Kontext(ed.sitzung))]


def _ziele_kommentar(ed):
    gesehen: dict[int, int] = {}
    for b in ed.kommentar_bereiche():
        gesehen.setdefault(int(b["wert"]), b["von"])
    k = ed.kommentare or {}
    return [(f"Kommentar {i}: {_kurz((k.get(kid) or {}).get('text', ''))}".rstrip(": "), pos) for i, (kid, pos) in enumerate(sorted(gesehen.items(), key=lambda x: x[1]), start=1)]


def _ziele_note(art: str):
    kenn = "f" if art == "Fußnote" else "e"

    def _liste(ed):
        return [(f"{art} {i}", n["von"]) for i, n in enumerate((n for n in ed.noten_stellen() if n["art"] == kenn), start=1)]
    return _liste


def _tabellen(bloecke, stellen):
    """(Tabelle, Stelle des Tabellenanfangs) aller Tabellen in Dokumentreihenfolge (auch geschachtelte)."""
    for b in bloecke:
        if isinstance(b, Tabelle):
            erster = next((x for zeile in b.zellen for z in zeile for x in z.bloecke if hasattr(x, "inhalte")), None)
            if erster is not None:
                yield b, stellen.get(erster.id, 0)
            for zeile in b.zellen:
                for z in zeile:
                    yield from _tabellen(z.bloecke, stellen)


def _ziele_tabelle(ed):
    dok = ed.sitzung.dokument
    stellen = _stellen(dok)
    alle = sorted((p, t) for a in dok.abschnitte for t, p in _tabellen(a.bloecke, stellen))
    return [(f"Tabelle {i}: {t.zeilen} × {t.spalten}", p) for i, (p, t) in enumerate(alle, start=1)]


def _objekte(ed, nur_art: str | None = None) -> list:
    """[(Stelle, Art)] aller Objekte (im Text und frei positioniert) in Dokumentreihenfolge."""
    dok = ed.sitzung.dokument
    stellen = _stellen(dok)
    aus = []
    for a in dok.absaetze():
        versatz = 0
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                aus.append((stellen[a.id] + versatz, x.art))
                versatz += 1
            else:
                versatz += len(x.text)
    aus += [(stellen.get(o.anker, 0), o.art) for o in dok.objekte.values()]
    return sorted(p for p in aus if nur_art is None or p[1] == nur_art)


def _ziele_bild(ed):
    return [(f"Bild {i}", p) for i, (p, _a) in enumerate(_objekte(ed, "bild"), start=1)]


def _ziele_abschnitt(ed):
    dok = ed.sitzung.dokument
    stellen = _stellen(dok)
    aus = []
    for i, ab in enumerate(dok.abschnitte):
        erster = next((b for b in ab.bloecke if hasattr(b, "inhalte")), None)
        aus.append((f"Abschnitt {i + 1}" + (f" ({ab.beginn})" if i else ""), stellen.get(erster.id, 0) if erster is not None else 0))
    return aus


_ZIELE = {"Überschrift": _ziele_ueberschrift, "Textmarke": _ziele_textmarke, "Beschriftung": _ziele_beschriftung,
          "Kommentar": _ziele_kommentar, "Fußnote": _ziele_note("Fußnote"), "Endnote": _ziele_note("Endnote"),
          "Tabelle": _ziele_tabelle, "Bild": _ziele_bild, "Abschnitt": _ziele_abschnitt}


def ziele(ed, art: str) -> list[tuple[str, int]]:
    """[(Beschriftung, Position)] für die Listen-Arten."""
    liste = _ZIELE.get(art)
    return liste(ed) if liste else []


def springen(ed, pos: int) -> None:
    ed.select_range(pos, pos)
    ed.ensureCursorVisible()
    ed.setFocus()


# ---- „Gehe zu“ in der linken Seitenleiste (Reiter des Feldes „Suchen und ersetzen“), Elemente wie in der Vorlage -----------------------------
ELEMENTE = ("Seite", "Abschnitt", "Zeile", "Textmarke", "Kommentar", "Fußnote", "Endnote", "Feld", "Tabelle", "Grafik", "Formel", "Objekt",
            "Überschrift")
EINGABE = {"Seite": "Seitenzahl eingeben:", "Abschnitt": "Abschnittsnummer eingeben:", "Zeile": "Zeilennummer eingeben:",
           "Textmarke": "Textmarkenname eingeben:", "Kommentar": "Kommentarnummer eingeben:", "Fußnote": "Fußnotennummer eingeben:",
           "Endnote": "Endnotennummer eingeben:", "Feld": "Feldnummer eingeben:", "Tabelle": "Tabellennummer eingeben:",
           "Grafik": "Grafiknummer eingeben:", "Formel": "Formelnummer eingeben:", "Objekt": "Objektnummer eingeben:",
           "Überschrift": "Überschriftnummer eingeben:"}


def positionen(ed, element: str) -> list[int]:
    """Die Anfänge aller Elemente einer Art, der Reihe nach."""
    dok = ed.sitzung.dokument
    if element == "Seite":
        return [seitenstart(ed, n) for n in range(1, _seitenzahl(ed) + 1)]
    if element == "Zeile":
        stellen = _stellen(dok)
        return [stellen[a.id] for a in dok.absaetze()]
    if element == "Feld":
        return sorted({position_zu_offset(dok, f.anker) for f in ed.sitzung.bereiche(lambda f: "feld" in f)})
    if element == "Formel":
        return [p for p, _a in _objekte(ed, "formel")]
    if element == "Objekt":
        return [p for p, _a in _objekte(ed)]
    return sorted({p for _t, p in ziele(ed, "Bild" if element == "Grafik" else element)})


def _ziel_index_leer(alle: list[int], element: str, i: int, hier: int, richtung: int) -> int:
    """Index für „Weiter“/„Zurück“ ohne Eingabe."""
    if element == "Seite":
        return i + richtung
    if richtung > 0:
        return next((k for k, p in enumerate(alle) if p > hier), len(alle))
    return max((k for k, p in enumerate(alle) if p < hier), default=-1)


def ziel(ed, element: str, eingabe: str = "", richtung: int = 1) -> int | None:
    """Wohin „Weiter“ (``richtung`` 1) oder „Zurück“ (-1) springt. ``eingabe``: leer = nächstes/voriges Element, „4“ = das vierte,
    „+2“/„-2“ = zwei weiter/zurück; bei Textmarken auch der Name."""
    alle = positionen(ed, element)
    if not alle:
        return None
    hier = ed.textCursor().position()
    i = max((k for k, p in enumerate(alle) if p <= hier), default=-1)          # das Element, in dem die Schreibmarke steht
    if element == "Seite":
        i = max(0, min(len(alle), ed.current_page()) - 1)
    t = (eingabe or "").strip().replace("–", "-")
    if not t:
        n = _ziel_index_leer(alle, element, i, hier, richtung)
    elif t[0] in "+-" and t[1:].isdigit():
        n = i + int(t)
    elif t.isdigit():
        n = int(t) - 1
    elif element == "Textmarke":
        treffer = [p for name, p in ziele(ed, "Textmarke") if name.casefold() == t.casefold()]
        return treffer[0] if treffer else None
    else:
        return None
    return alle[n] if 0 <= n < len(alle) else None
