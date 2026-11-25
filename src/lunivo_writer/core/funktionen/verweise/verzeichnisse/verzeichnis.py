"""Verzeichnisse: Inhalt, Abbildungen, Tabellen, Stichwörter, Literatur.

Ein Verzeichnis besteht im Dokumentmodell aus einem Kopfabsatz (Format ``toc: kopf``, ``verzeichnis_art``, beim Inhaltsverzeichnis ``toc_opt``) und je Eintrag
einem Absatz (``toc: zeileN``) mit rechtem Tabstopp und der Seitenzahl hinter dem Text (``verzeichnis_setzen`` der Bearbeitungssitzung). „Verzeichnisse
aktualisieren“ findet sie daran wieder. In DOCX tragen sie die Formatvorlagen „TOC Heading“, „TOC 1–3“, „Table of Figures“, „Index 1“ und „Bibliography“.

Das Inhaltsverzeichnis merkt sich am Kopf seine Einstellungen (``toc_opt``, Fenster „Inhaltsverzeichnis“): Füllzeichen, Ebenen 1–9, Seitenzahlen anzeigen,
rechtsbündig, Verknüpfungen. Mit Verknüpfungen bekommt jede Überschrift eine verborgene Textmarke „_Toc…“, die Zeile verweist darauf (Strg+Klick springt hin).
"""
from __future__ import annotations

from lunivo_writer.core.dokument.dokument import Auswahl, Position
from lunivo_writer.core.dokument.formatvorlagen import ueberschriftsebene
from lunivo_writer.core.geometrie import mm_to_px
from lunivo_writer.core.bearbeitung.suche import offset_zu_position, position_zu_offset

TOC_VORGABE = {"fuell": "punkt", "ebenen": 3, "seitenzahlen": True, "rechts": True, "links": True}
TOC_FUELL = ("", "punkt", "strich", "linie")           # Auswahl im Fenster (Schlüssel aus editor/text/tabfuell.py)

ARTEN = {
    "toc": "Inhaltsverzeichnis",
    "abb": "Abbildungsverzeichnis",
    "tab": "Tabellenverzeichnis",
    "index": "Stichwortverzeichnis",
    "lit": "Literaturverzeichnis",
}


def toc_opt_text(opt: dict) -> str:
    o = {**TOC_VORGABE, **opt}
    return f"{o['fuell']}|{int(o['ebenen'])}|{int(bool(o['seitenzahlen']))}|{int(bool(o['rechts']))}|{int(bool(o['links']))}"


def toc_opt_lesen(text: str | None) -> dict:
    o = dict(TOC_VORGABE)
    teile = (text or "").split("|")
    if len(teile) == 5:
        try:
            o.update(fuell=teile[0] if teile[0] in TOC_FUELL else "", ebenen=max(1, min(9, int(teile[1]))),
                     seitenzahlen=teile[2] == "1", rechts=teile[3] == "1", links=teile[4] == "1")
        except ValueError:
            pass
    return o


def _koepfe(dok) -> list:
    """Die Kopfabsätze aller Verzeichnisse in Dokumentreihenfolge."""
    return [a for a in dok.absaetze() if a.format.get("toc") == "kopf" and a.format.get("verzeichnis_art")]


def toc_optionen(doc) -> dict | None:
    """Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt)."""
    for a in _koepfe(doc):
        if a.format.get("verzeichnis_art") == "toc":
            return toc_opt_lesen(a.format.get("toc_opt"))
    return None


def vorhanden(doc, art: str) -> bool:
    return any(a.format.get("verzeichnis_art") == art for a in _koepfe(doc))


def _stellen(dok) -> dict:
    """Absatz-Id → Stelle des Absatzanfangs im Rohtext."""
    aus, n = {}, 0
    for a in dok.absaetze():
        aus[a.id] = n
        n += a.laenge + 1
    return aus


def _ueberschriften(dok, ebenen: int = 3):
    """(Ebene, Text, Absatz-Id, Stelle) der Überschriften außerhalb von Verzeichnissen."""
    stellen = _stellen(dok)
    for a in dok.absaetze():
        lvl = ueberschriftsebene(dok, a)
        if 1 <= lvl <= ebenen and a.text().strip() and a.format.get("toc") is None:
            yield lvl, a.text().strip(), a.id, stellen[a.id]


def _beschriftungen(dok, label: str):
    stellen = _stellen(dok)
    for a in dok.absaetze():
        if a.format.get("beschriftung") == label and a.text().strip():
            yield 1, a.text().strip(), a.id, stellen[a.id]


def _toc_marken(editor, ueberschriften: list) -> dict:
    """Absatz-Id → Name der verborgenen Textmarke „_Toc…“ an der Überschrift; fehlende werden gesetzt (in einem Schritt mit dem Verzeichnis)."""
    s = editor.sitzung
    marken = s.textmarken()
    vorhanden_ = {n for n in marken}
    aus = {}
    for n, a in marken.items():
        if n.startswith("_Toc"):
            aus.setdefault(a.anker.absatz_id, n)
    zaehler = 1
    for _l, _t, aid, _p in ueberschriften:
        if aid in aus:
            continue
        while f"_Toc{zaehler:06d}" in vorhanden_:
            zaehler += 1
        name = f"_Toc{zaehler:06d}"
        vorhanden_.add(name)
        s.textmarke_setzen(name, Auswahl(Position(aid, 0), Position(aid, max(1, s._absatz(aid).laenge))))
        aus[aid] = name
    return aus


def _stichwoerter(editor):
    """[(Eintrag, Stelle)] aus den markierten Textstellen (eine Stelle je zusammenhängender Markierung)."""
    from lunivo_writer.core.funktionen.verweise.stichwoerter.indexeintrag import aus_text
    dok = editor.sitzung.dokument
    aus = []
    for fund in editor.sitzung.bereiche(lambda f: "index" in f, lambda f: (f["index"], f.get("index_opt", ""))):
        a = editor.sitzung._absatz(fund.anker.absatz_id)
        versatz, schl = 0, None
        for x in a.inhalte:
            n = len(x.text) if hasattr(x, "text") else 1
            if versatz == fund.anker.versatz:
                schl = (x.format.get("index", ""), x.format.get("index_opt", ""))
            versatz += n
        if schl:
            aus.append((aus_text(*schl), position_zu_offset(dok, fund.anker)))
    return aus


def _index_zeilen(editor) -> list:
    """Zeilen des Stichwortverzeichnisses: Haupteinträge, darunter eingerückt die Untereinträge; „Siehe …“ statt Seitenzahl,
    Seitenbereiche aus Textmarken, fette/kursive Seitenzahlen als Stücke (Text, fett, kursiv)."""
    from lunivo_writer.core.funktionen.verweise.textmarken.textmarke import lesezeichen_liste
    eintraege = _stichwoerter(editor)
    marken = {d["name"]: d for d in lesezeichen_liste(editor)}
    pos = []
    for e, p in eintraege:
        pos.append(p)
        if e.marke in marken:
            pos += [marken[e.marke]["von"], max(marken[e.marke]["von"], marken[e.marke]["bis"] - 1)]
    seiten = iter(editor.seiten_von(pos)) if pos else iter(())
    from lunivo_writer.core.funktionen.verweise.verzeichnisse.verzeichnis_kern import index_zeilen_bilden
    return index_zeilen_bilden(eintraege, seiten, marken)


def zeilen_fuer(editor, art: str, opt: dict | None = None) -> list[tuple]:
    """→ [(Ebene, Text, Seitenangabe)]; beim Inhaltsverzeichnis mit Verknüpfungen (``opt["links"]``) als viertes die Textmarke.
    Die Seitenangabe ist Text oder eine Liste von Stücken (Text, fett, kursiv)."""
    dok = editor.sitzung.dokument
    if art == "toc":
        o = {**TOC_VORGABE, **(opt or {})}
        ue = list(_ueberschriften(dok, int(o["ebenen"])))
        s = editor.seiten_von([p for _l, _t, _i, p in ue]) if ue else []
        if o["links"]:
            marken = _toc_marken(editor, ue)
            return [(l, t, n, marken[aid]) for (l, t, aid, _p), n in zip(ue, s)]
        return [(l, t, n) for (l, t, _i, _p), n in zip(ue, s)]
    if art in ("abb", "tab"):
        ue = list(_beschriftungen(dok, "Abbildung" if art == "abb" else "Tabelle"))
        s = editor.seiten_von([p for _l, _t, _i, p in ue]) if ue else []
        return [(l, t, n) for (l, t, _i, _p), n in zip(ue, s)]
    if art == "index":
        return _index_zeilen(editor)
    if art == "lit":
        from lunivo_writer.core.funktionen.verweise.quellen.literatur import literaturverzeichnis
        return [(1, z, "") for z in literaturverzeichnis(editor.quellen, editor.zitierweise)]
    return []


def _seite_text(seite) -> str:
    """Die Seitenangabe als Text: ein Text oder Stücke (Text, fett, kursiv), wie sie das Stichwortverzeichnis liefert."""
    return seite if isinstance(seite, str) else "".join(t for t, _f, _k in seite)


def _schreiben(editor, s, art: str, zeilen: list, opt: dict | None) -> None:
    """Schreibt das Verzeichnis (ersetzt ein vorhandenes der Art) im Rahmen eines laufenden Schrittes."""
    o = {**TOC_VORGABE, **(opt or {})} if art == "toc" else {**TOC_VORGABE, "fuell": "", "links": False}
    breite = editor.page.content_width_px
    eintraege = []
    for lvl, text, seite, *marke in zeilen:
        angabe = _seite_text(seite) if o["seitenzahlen"] else ""
        rechts = bool(angabe) and o["rechts"]
        eintraege.append((lvl, text + (("\t" if rechts else " ") + angabe if angabe else ""), marke[0] if marke and marke[0] else None, rechts))
    ids = s.verzeichnis_setzen(art, ARTEN[art], [(l, t, "#" + m if m else "") for l, t, m, _r in eintraege], optionen=toc_opt_text(o) if art == "toc" else "")
    kopf = ids[0]
    s.zeichenformat_anwenden({"fett": True, "groesse_pt": 14.0}, Auswahl(Position(kopf, 0), Position(kopf, s._absatz(kopf).laenge)))
    s.absatzformat_anwenden({"abstand_nach": 6.0 / 0.75 * 0.75}, absatz_ids=[kopf])
    for aid, (lvl, _t, _m, rechts) in zip(ids[1:], eintraege):
        fmt = {}
        if art in ("toc", "index"):
            fmt["einzug_links"] = mm_to_px(6) * (lvl - 1) or None
        if rechts:
            fmt["tabstopps"] = [[float(breite), "rechts", ""]]
            if o["fuell"]:
                fmt["tabfuell"] = f"{round(float(breite), 2)}:{o['fuell']}"
        if fmt:
            s.absatzformat_anwenden(fmt, absatz_ids=[aid])


def verzeichnis_einfuegen(editor, art: str = "toc", opt: dict | None = None) -> int:
    """Verzeichnis an der Schreibmarke einfügen. Gibt es schon eines der Art, wird es mit ``opt`` neu geschrieben."""
    anzahl = [0]

    def f(s):
        with s.gruppe("Verzeichnis"):
            zeilen = zeilen_fuer(editor, art, opt)
            anzahl[0] = len(zeilen)
            if zeilen:
                _schreiben(editor, s, art, zeilen, opt)
    editor.ansicht._aendern(f)
    if anzahl[0]:
        verzeichnis_aktualisieren(editor)       # Seitenzahlen nach dem Einfügen (das Verzeichnis schiebt den Text)
    return anzahl[0]


def verzeichnis_aktualisieren(editor, nur: str | None = None) -> int:
    """Alle Verzeichnisse (oder nur die der Art ``nur``) neu schreiben; gibt die Zahl der Zeilen zurück."""
    n = [0]

    def f(s):
        with s.gruppe("Verzeichnisse aktualisieren"):
            for kopf in list(_koepfe(s.dokument)):
                art = kopf.format["verzeichnis_art"]
                if nur and art != nur:
                    continue
                opt = toc_opt_lesen(kopf.format.get("toc_opt")) if art == "toc" else None
                zeilen = zeilen_fuer(editor, art, opt)
                _schreiben(editor, s, art, zeilen, opt)
                n[0] += len(zeilen)
    editor.ansicht._aendern(f)
    return n[0]
