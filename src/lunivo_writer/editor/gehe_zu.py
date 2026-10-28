"""„Gehe zu“: Sprungziele im Dokument — Seite, Zeile (Absatz), Überschrift, Textmarke, Kommentar, Fußnote, Endnote, Tabelle, Bild,
Beschriftung, Abschnitt. Die Oberfläche ist der Reiter „Gehe zu“ im Feld „Suchen und ersetzen“ (ui/document/suchen_feld.py)."""
from __future__ import annotations

from PySide6.QtGui import QTextTable

from lunivo_writer.editor import verweise
from lunivo_writer.editor.zusatz import P_KOMMENTAR, P_NOTE

NUMMERN = ("Seite", "Zeile")                                    # man gibt eine Zahl ein
LISTEN = ("Überschrift", "Textmarke", "Beschriftung", "Kommentar", "Fußnote", "Endnote", "Tabelle", "Bild", "Abschnitt")
ARTEN = NUMMERN + LISTEN


def _kurz(t: str, n: int = 60) -> str:
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1] + "…"


def _fragmente(doc):
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid():
                yield f
            it += 1
        b = b.next()


def _tabellen(rahmen):
    for k in rahmen.childFrames():
        if isinstance(k, QTextTable):
            yield k
        yield from _tabellen(k)


def maximum(ed, art: str) -> int:
    """Obergrenze für Seite und Zeile."""
    return max(1, ed.page_count) if art == "Seite" else max(1, ed.document().blockCount())


def seitenstart(ed, n: int) -> int:
    n = max(1, min(n, max(1, ed.page_count)))
    breaks = ed.seitenwechsel
    return 0 if n == 1 or not breaks else breaks[min(n - 2, len(breaks) - 1)]


def zeilenstart(ed, n: int) -> int:
    b = ed.document().findBlockByNumber(max(0, min(n, ed.document().blockCount()) - 1))
    return b.position()


def ziele(ed, art: str) -> list[tuple[str, int]]:
    """[(Beschriftung, Position)] für die Listen-Arten."""
    doc = ed.document()
    if art == "Überschrift":
        return [(z["text"], z["pos"]) for z in verweise.querverweis_ziele(ed) if z["art"] == "Überschrift"]
    if art == "Textmarke":
        return [(d["name"], d["von"]) for d in verweise.lesezeichen_liste(ed, versteckte=False)]
    if art == "Beschriftung":
        return [(f"{k['label']}: {_kurz(k['text'])}", k["pos"]) for k in verweise.beschriftungen_liste(ed)]
    if art == "Kommentar":
        gesehen: dict[int, int] = {}
        for f in _fragmente(doc):
            cf = f.charFormat()
            if cf.hasProperty(P_KOMMENTAR):
                gesehen.setdefault(int(cf.property(P_KOMMENTAR)), f.position())
        k = getattr(ed, "kommentare", {}) or {}
        return [(f"Kommentar {i}: {_kurz((k.get(kid) or k.get(str(kid)) or {}).get('text', ''))}".rstrip(": "), pos)
                for i, (kid, pos) in enumerate(sorted(gesehen.items(), key=lambda x: x[1]), start=1)]
    if art in ("Fußnote", "Endnote"):
        kenn = "f:" if art == "Fußnote" else "e:"
        out = []
        for f in _fragmente(doc):
            cf = f.charFormat()
            if cf.hasProperty(P_NOTE) and cf.stringProperty(P_NOTE).startswith(kenn):
                out.append((f"{art} {len(out) + 1}", f.position()))
        return out
    if art == "Tabelle":
        return [(f"Tabelle {i}: {t.rows()} × {t.columns()}", t.firstPosition()) for i, t in enumerate(
            sorted(_tabellen(doc.rootFrame()), key=lambda t: t.firstPosition()), start=1)]
    if art == "Bild":
        return [(f"Bild {i}", f.position()) for i, f in enumerate((f for f in _fragmente(doc) if f.charFormat().isImageFormat()), start=1)]
    if art == "Abschnitt":
        from lunivo_writer.editor import abschnitte as AB
        n = AB.anzahl(doc)
        return [(f"Abschnitt {i + 1}" + (f" ({AB.TYPEN[AB.alle_einrichtungen(doc, ed.page)[i][0]]})" if i else ""), AB.beginn(doc, i)) for i in range(n)]
    return []


def springen(ed, pos: int) -> None:
    from PySide6.QtGui import QTextCursor
    c = QTextCursor(ed.document())
    c.setPosition(max(0, min(pos, ed.document().characterCount() - 1)))
    ed.setTextCursor(c)
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


def _objekte(doc, nur_art: str | None = None) -> list[int]:
    import json
    from lunivo_writer.editor.zusatz import P_OBJEKT
    out = []
    for f in _fragmente(doc):
        cf = f.charFormat()
        if cf.isImageFormat() and cf.hasProperty(P_OBJEKT):
            try:
                art = json.loads(cf.stringProperty(P_OBJEKT)).get("art", "")
            except ValueError:
                art = ""
            if nur_art is None or art == nur_art:
                out.append(f.position())
    return out


def positionen(ed, element: str) -> list[int]:
    """Die Anfänge aller Elemente einer Art, der Reihe nach."""
    doc = ed.document()
    if element == "Seite":
        return [seitenstart(ed, n) for n in range(1, max(1, ed.page_count) + 1)]
    if element == "Zeile":
        b, out = doc.firstBlock(), []
        while b.isValid():
            out.append(b.position()); b = b.next()
        return out
    if element == "Feld":
        from lunivo_writer.editor.zusatz import P_FELD
        out, ende = [], -1
        for f in _fragmente(doc):
            if f.charFormat().hasProperty(P_FELD):
                if f.position() != ende:
                    out.append(f.position())
                ende = f.position() + f.length()
        return out
    if element == "Formel":
        return _objekte(doc, "formel")
    if element == "Objekt":
        return _objekte(doc)
    return sorted({p for _t, p in ziele(ed, "Bild" if element == "Grafik" else element)})


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
        if element == "Seite":
            n = i + richtung
        elif richtung > 0:
            n = next((k for k, p in enumerate(alle) if p > hier), len(alle))
        else:
            n = max((k for k, p in enumerate(alle) if p < hier), default=-1)
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
