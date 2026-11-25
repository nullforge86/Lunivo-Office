"""„Gehe zu“: Sprungziele im Dokument — Seite, Zeile (Absatz), Überschrift, Textmarke, Kommentar, Fußnote, Endnote, Tabelle, Bild,
Beschriftung, Abschnitt. Die Oberfläche ist der Reiter „Gehe zu“ im Feld „Suchen und ersetzen“ (oberflaeche/dokument/dokumentfenster/suchen_feld.py).

Alle Stellen sind Zeichenstellen im Rohtext (Absätze durch ein Zeichen getrennt). ``k`` ist der ``Kontext`` des Dokuments."""
from __future__ import annotations

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


def _seitenzahl(k) -> int:
    return max(1, len(k.layout().seiten))


def maximum(k, art: str) -> int:
    """Obergrenze für Seite und Zeile."""
    return _seitenzahl(k) if art == "Seite" else max(1, sum(1 for _ in k.sitzung.dokument.absaetze()))


def seitenstart(k, n: int) -> int:
    """Stelle des ersten Textes auf der Seite ``n`` (ab 1); hat die Seite keinen Text, der Anfang der nächsten mit Text."""
    erg = k.layout()
    stellen = _stellen(k.sitzung.dokument)
    for seite in erg.seiten[max(0, min(n, len(erg.seiten)) - 1):]:
        for p in seite.plaetze:
            if p.art == "zeile" and not p.kopie and p.block_id in stellen:
                return stellen[p.block_id]
    return 0


def zeilenstart(k, n: int) -> int:
    absaetze = list(k.sitzung.dokument.absaetze())
    return _stellen(k.sitzung.dokument)[absaetze[max(0, min(n, len(absaetze)) - 1)].id]


def _ziele_ueberschrift(k):
    return [(z["text"], z["pos"]) for z in querverweis.querverweis_ziele(k) if z["art"] == "Überschrift"]


def _ziele_textmarke(k):
    return [(d["name"], d["von"]) for d in textmarke.lesezeichen_liste(k, versteckte=False)]


def _ziele_beschriftung(k):
    return [(f"{b['label']}: {_kurz(b['text'])}", b["pos"]) for b in beschriftung.beschriftungen_liste(k)]


def _ziele_kommentar(k):
    gesehen: dict[int, int] = {}
    for b in k.kommentar_bereiche():
        gesehen.setdefault(int(b["wert"]), b["von"])
    texte = k.kommentare
    return [(f"Kommentar {i}: {_kurz((texte.get(kid) or {}).get('text', ''))}".rstrip(": "), pos) for i, (kid, pos) in enumerate(sorted(gesehen.items(), key=lambda x: x[1]), start=1)]


def _ziele_note(art: str):
    kenn = "f" if art == "Fußnote" else "e"

    def _liste(k):
        return [(f"{art} {i}", n["von"]) for i, n in enumerate((n for n in k.noten_stellen() if n["art"] == kenn), start=1)]
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


def _ziele_tabelle(k):
    dok = k.sitzung.dokument
    stellen = _stellen(dok)
    alle = sorted((p, t) for a in dok.abschnitte for t, p in _tabellen(a.bloecke, stellen))
    return [(f"Tabelle {i}: {t.zeilen} × {t.spalten}", p) for i, (p, t) in enumerate(alle, start=1)]


def _objekte(k, nur_art: str | None = None) -> list:
    """[(Stelle, Art)] aller Objekte (im Text und frei positioniert) in Dokumentreihenfolge."""
    dok = k.sitzung.dokument
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


def _ziele_bild(k):
    return [(f"Bild {i}", p) for i, (p, _a) in enumerate(_objekte(k, "bild"), start=1)]


def _ziele_abschnitt(k):
    dok = k.sitzung.dokument
    stellen = _stellen(dok)
    aus = []
    for i, ab in enumerate(dok.abschnitte):
        erster = next((b for b in ab.bloecke if hasattr(b, "inhalte")), None)
        aus.append((f"Abschnitt {i + 1}" + (f" ({ab.beginn})" if i else ""), stellen.get(erster.id, 0) if erster is not None else 0))
    return aus


_ZIELE = {"Überschrift": _ziele_ueberschrift, "Textmarke": _ziele_textmarke, "Beschriftung": _ziele_beschriftung,
          "Kommentar": _ziele_kommentar, "Fußnote": _ziele_note("Fußnote"), "Endnote": _ziele_note("Endnote"),
          "Tabelle": _ziele_tabelle, "Bild": _ziele_bild, "Abschnitt": _ziele_abschnitt}


def ziele(k, art: str) -> list[tuple[str, int]]:
    """[(Beschriftung, Position)] für die Listen-Arten."""
    liste = _ZIELE.get(art)
    return liste(k) if liste else []


def springen(k, pos: int) -> int:
    """Setzt die Schreibmarke an ``pos``; die Oberfläche zeigt die Stelle auf die Meldung des Frameworks hin."""
    k.auswaehlen(pos, pos)
    return 1


# ---- „Gehe zu“ in der linken Seitenleiste (Reiter des Feldes „Suchen und ersetzen“), Elemente wie in der Vorlage -----------------------------
ELEMENTE = ("Seite", "Abschnitt", "Zeile", "Textmarke", "Kommentar", "Fußnote", "Endnote", "Feld", "Tabelle", "Grafik", "Formel", "Objekt",
            "Überschrift")
EINGABE = {"Seite": "Seitenzahl eingeben:", "Abschnitt": "Abschnittsnummer eingeben:", "Zeile": "Zeilennummer eingeben:",
           "Textmarke": "Textmarkenname eingeben:", "Kommentar": "Kommentarnummer eingeben:", "Fußnote": "Fußnotennummer eingeben:",
           "Endnote": "Endnotennummer eingeben:", "Feld": "Feldnummer eingeben:", "Tabelle": "Tabellennummer eingeben:",
           "Grafik": "Grafiknummer eingeben:", "Formel": "Formelnummer eingeben:", "Objekt": "Objektnummer eingeben:",
           "Überschrift": "Überschriftnummer eingeben:"}


def positionen(k, element: str) -> list[int]:
    """Die Anfänge aller Elemente einer Art, der Reihe nach."""
    dok = k.sitzung.dokument
    if element == "Seite":
        return [seitenstart(k, n) for n in range(1, _seitenzahl(k) + 1)]
    if element == "Zeile":
        stellen = _stellen(dok)
        return [stellen[a.id] for a in dok.absaetze()]
    if element == "Feld":
        return sorted({position_zu_offset(dok, f.anker) for f in k.sitzung.bereiche(lambda f: "feld" in f)})
    if element == "Formel":
        return [p for p, _a in _objekte(k, "formel")]
    if element == "Objekt":
        return [p for p, _a in _objekte(k)]
    return sorted({p for _t, p in ziele(k, "Bild" if element == "Grafik" else element)})


def _ziel_index_leer(alle: list[int], element: str, i: int, hier: int, richtung: int) -> int:
    """Index für „Weiter“/„Zurück“ ohne Eingabe."""
    if element == "Seite":
        return i + richtung
    if richtung > 0:
        return next((j for j, p in enumerate(alle) if p > hier), len(alle))
    return max((j for j, p in enumerate(alle) if p < hier), default=-1)


def ziel(k, element: str, eingabe: str = "", richtung: int = 1) -> int | None:
    """Wohin „Weiter“ (``richtung`` 1) oder „Zurück“ (-1) springt. ``eingabe``: leer = nächstes/voriges Element, „4“ = das vierte,
    „+2“/„-2“ = zwei weiter/zurück; bei Textmarken auch der Name."""
    alle = positionen(k, element)
    if not alle:
        return None
    hier = k.position()
    i = max((j for j, p in enumerate(alle) if p <= hier), default=-1)          # das Element, in dem die Schreibmarke steht
    if element == "Seite":
        i = max(0, min(len(alle), k.aktuelle_seite()) - 1)
    t = (eingabe or "").strip().replace("–", "-")
    if not t:
        n = _ziel_index_leer(alle, element, i, hier, richtung)
    elif t[0] in "+-" and t[1:].isdigit():
        n = i + int(t)
    elif t.isdigit():
        n = int(t) - 1
    elif element == "Textmarke":
        treffer = [p for name, p in ziele(k, "Textmarke") if name.casefold() == t.casefold()]
        return treffer[0] if treffer else None
    else:
        return None
    return alle[n] if 0 <= n < len(alle) else None
