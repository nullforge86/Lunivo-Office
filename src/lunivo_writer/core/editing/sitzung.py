"""Bearbeitungssitzung über einem ``core.document.Document``.

Eine Stelle im Dokument ist ein ``Caret``: der Pfad des Absatzes (Abschnitt, Block, bei Tabellen Zeile, Zelle und Block darin; bei Rahmen der Block darin) und der Versatz in Zeichen
(ein Bild zählt ein Zeichen). Jede Änderung ersetzt ein Stück einer Blockliste (``Ersetzung``) und wird als ``Aenderung`` gemerkt: daraus folgen Rückgängig und Wiederholen, und
ein Adapter (zum Beispiel für ein ``QTextDocument``) kann dieselbe Änderung nachvollziehen. Geändert wird nie an Ort und Stelle, sondern durch neue Absätze; das Modell bleibt so
jederzeit gültig."""
from __future__ import annotations

import copy
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from lunivo_writer.core.document.model import CharacterFormat, Document, Frame, Image, ListFormat, Paragraph, ParagraphFormat, Table, TableCell, TableRow, TextRun

Pfad = tuple[int, ...]


@dataclass(frozen=True, order=True)
class Caret:
    pfad: Pfad
    versatz: int = 0


@dataclass
class Ersetzung:
    """Im Block-Container ``behaelter`` (Pfad ohne den letzten Index) ersetzen die Blöcke ``neu`` die Blöcke ``alt`` ab Index ``start``."""
    behaelter: Pfad
    start: int
    alt: list
    neu: list


@dataclass
class Aenderung:
    art: str                                   # "text", "loeschen", "zeichenformat", "absatzformat", "bild", "absatz"
    ersetzungen: list[Ersetzung] = field(default_factory=list)
    parameter: dict = field(default_factory=dict)           # was geändert wurde (für Adapter): text, von, bis, eigenschaften, entfernen, bild
    vorher: tuple[Caret, Caret | None] | None = None      # Schreibmarke und Anker vor der Änderung
    nachher: tuple[Caret, Caret | None] | None = None
    listen: dict = field(default_factory=dict)             # Listen, die diese Änderung zu ``Document.lists`` hinzufügt (Rückgängig nimmt sie wieder heraus)
    medien: dict = field(default_factory=dict)             # Bilder, die diese Änderung zu ``Document.media`` hinzufügt (Rückgängig nimmt sie wieder heraus)


# ---- Zugriff ----------------------------------------------------------------------------------------------------------------
def behaelter(dok: Document, pfad: Pfad) -> list:
    """Die Blockliste, in der der Absatz mit dem Pfad ``pfad + (index,)`` steht."""
    liste = dok.sections[pfad[0]].content
    i = 1
    while i < len(pfad):
        b = liste[pfad[i]]
        if isinstance(b, Table):
            liste = b.table_rows[pfad[i + 1]].cells[pfad[i + 2]].content
            i += 3
        elif isinstance(b, Frame):
            liste = b.content
            i += 1
        else:
            raise ValueError(f"Pfad {pfad}: kein Behälter bei {i}")
    return liste


def innerste_tabelle(dok: Document, pfad: Pfad) -> Pfad | None:
    """Der Pfad des innersten Tabellenblocks, in dem der Absatz mit dem Pfad ``pfad`` steht; ``None``, wenn er in keiner Tabelle steht."""
    liste = dok.sections[pfad[0]].content
    i, tabelle = 1, None
    while i < len(pfad) - 1:
        b = liste[pfad[i]]
        if isinstance(b, Table):
            tabelle = pfad[:i + 1]
            liste = b.table_rows[pfad[i + 1]].cells[pfad[i + 2]].content
            i += 3
        elif isinstance(b, Frame):
            liste = b.content
            i += 1
        else:
            break
    return tabelle


def absatz_bei(dok: Document, pfad: Pfad) -> Paragraph:
    b = behaelter(dok, pfad[:-1])[pfad[-1]]
    if not isinstance(b, Paragraph):
        raise ValueError(f"Pfad {pfad} ist kein Absatz")
    return b


def absaetze(dok: Document) -> Iterator[tuple[Pfad, Paragraph]]:
    """Alle Absätze in Dokumentreihenfolge (auch in Tabellenzellen und Rahmen) mit ihrem Pfad."""
    def lauf(bloecke: list, pfad: Pfad) -> Iterator[tuple[Pfad, Paragraph]]:
        for i, b in enumerate(bloecke):
            if isinstance(b, Paragraph):
                yield pfad + (i,), b
            elif isinstance(b, Table):
                for r, zeile in enumerate(b.table_rows):
                    for c, zelle in enumerate(zeile.cells):
                        yield from lauf(zelle.content, pfad + (i, r, c))
            elif isinstance(b, Frame):
                yield from lauf(b.content, pfad + (i,))
    for s, sec in enumerate(dok.sections):
        yield from lauf(sec.content, (s,))


def laenge(p: Paragraph) -> int:
    return sum(len(r.text) if isinstance(r, TextRun) else 1 for r in p.runs)


def _teilen(runs: list, versatz: int) -> tuple[list, list]:
    """Die Läufe in die vor und die ab ``versatz`` teilen (ein Textlauf wird an der Stelle geschnitten)."""
    links, rechts, pos = [], [], 0
    for r in runs:
        n = len(r.text) if isinstance(r, TextRun) else 1
        if pos + n <= versatz:
            links.append(r)
        elif pos >= versatz:
            rechts.append(r)
        else:
            k = versatz - pos
            links.append(TextRun(r.text[:k], copy.deepcopy(r.format)))
            rechts.append(TextRun(r.text[k:], copy.deepcopy(r.format)))
        pos += n
    return links, rechts


def _verschmelzen(runs: list) -> list:
    """Benachbarte Textläufe mit gleichem Format zu einem zusammenfassen, leere weglassen."""
    aus: list = []
    for r in runs:
        if isinstance(r, TextRun):
            if not r.text:
                continue
            if aus and isinstance(aus[-1], TextRun) and aus[-1].format == r.format:
                aus[-1] = TextRun(aus[-1].text + r.text, aus[-1].format)
                continue
        aus.append(r)
    return aus


def _neuer(p: Paragraph, runs: list) -> Paragraph:
    return Paragraph(copy.deepcopy(p.format), _verschmelzen(runs))


# ---- Sitzung ---------------------------------------------------------------------------------------------------------------
class Sitzung:
    def __init__(self, dok: Document):
        self.dok = dok
        self.cursor = Caret((0, 0), 0)
        self.anker: Caret | None = None
        self._rueckgaengig: list[Aenderung] = []
        self._wiederholen: list[Aenderung] = []
        self.beobachter: list = []                          # Funktionen ``f(aenderung, richtung)`` mit richtung "vor" | "zurueck" | "wiederholen"

    def dok_tabelle(self, behaelter_pfad: Pfad, index: int) -> Table:
        """Die Tabelle an Stelle ``index`` im Behälter."""
        t = behaelter(self.dok, behaelter_pfad)[index]
        if not isinstance(t, Table):
            raise ValueError("keine Tabelle")
        return t

    # -- Lesen --
    def text(self, von: Caret | None = None, bis: Caret | None = None) -> str:
        """Der Text zwischen zwei Stellen (Absätze durch Zeilenumbruch getrennt); ohne Angaben das ganze Dokument."""
        a, b = (von, bis) if von is not None and bis is not None else (None, None)
        teile = []
        for pfad, p in absaetze(self.dok):
            t = p.text
            if a is not None:
                if (pfad, 0) < (a.pfad, 0) or (pfad, 0) > (b.pfad, 0):
                    continue
                s = a.versatz if pfad == a.pfad else 0
                e = b.versatz if pfad == b.pfad else len(t)
                t = t[s:e]
            teile.append(t)
        return "\n".join(teile)

    def auswahl(self) -> tuple[Caret, Caret] | None:
        if self.anker is None or self.anker == self.cursor:
            return None
        return (self.anker, self.cursor) if self.anker < self.cursor else (self.cursor, self.anker)

    def auswaehlen(self, anker: Caret, cursor: Caret) -> None:
        self.anker, self.cursor = anker, cursor

    def setzen(self, caret: Caret) -> None:
        self.cursor, self.anker = caret, None

    def bewegen(self, caret: Caret, schritte: int) -> Caret:
        """Um ``schritte`` Zeichen weiter (negativ: zurück); über Absatzgrenzen hinweg, am Dokumentrand bleibt die Stelle stehen."""
        liste = list(absaetze(self.dok))
        pfade = [p for p, _a in liste]
        i = pfade.index(caret.pfad)
        v = caret.versatz + schritte
        while v > laenge(liste[i][1]) and i + 1 < len(liste):
            v -= laenge(liste[i][1]) + 1
            i += 1
        while v < 0 and i > 0:
            i -= 1
            v += laenge(liste[i][1]) + 1
        return Caret(pfade[i], max(0, min(v, laenge(liste[i][1]))))

    # -- Rückgängig --
    def _anwenden(self, e: Aenderung, vor: bool) -> None:
        for nr, lf in e.listen.items():
            if vor:
                self.dok.lists[nr] = copy.deepcopy(lf)
            else:
                self.dok.lists.pop(nr, None)
        for name, bild in e.medien.items():
            if vor:
                self.dok.media[name] = copy.deepcopy(bild)
            else:
                self.dok.media.pop(name, None)
        reihe = e.ersetzungen if vor else list(reversed(e.ersetzungen))
        for er in reihe:
            liste = behaelter(self.dok, er.behaelter)
            alt, neu = (er.alt, er.neu) if vor else (er.neu, er.alt)
            liste[er.start:er.start + len(alt)] = copy.deepcopy(neu)

    def _buchen(self, e: Aenderung, nachher: Caret) -> Caret:
        self._buchen_mit(e, nachher, None)
        return nachher

    def kann_rueckgaengig(self) -> bool:
        return bool(self._rueckgaengig)

    def kann_wiederholen(self) -> bool:
        return bool(self._wiederholen)

    def rueckgaengig(self) -> bool:
        if not self._rueckgaengig:
            return False
        e = self._rueckgaengig.pop()
        self._anwenden(e, False)
        self.cursor, self.anker = e.vorher
        self._wiederholen.append(e)
        for f in self.beobachter:
            f(e, "zurueck")
        return True

    def wiederholen(self) -> bool:
        if not self._wiederholen:
            return False
        e = self._wiederholen.pop()
        self._anwenden(e, True)
        self.cursor, self.anker = e.nachher
        self._rueckgaengig.append(e)
        for f in self.beobachter:
            f(e, "wiederholen")
        return True

    @contextmanager
    def gruppiert(self):
        """Mehrere Änderungen zu einem Schritt zusammenfassen: Rückgängig und Wiederholen nehmen sie gemeinsam zurück."""
        start = len(self._rueckgaengig)
        yield
        teile = self._rueckgaengig[start:]
        if len(teile) > 1:
            del self._rueckgaengig[start:]
            g = Aenderung("gruppe", [er for t in teile for er in t.ersetzungen], {"teile": teile})
            g.vorher, g.nachher = teile[0].vorher, teile[-1].nachher
            self._rueckgaengig.append(g)

    # -- Ändern --
    def _ersetzung(self, pfad: Pfad, anzahl: int, neu: list) -> Ersetzung:
        liste = behaelter(self.dok, pfad[:-1])
        return Ersetzung(pfad[:-1], pfad[-1], copy.deepcopy(liste[pfad[-1]:pfad[-1] + anzahl]), neu)

    def einfuegen(self, text: str, caret: Caret | None = None, format: CharacterFormat | None = None) -> Caret:
        """Text an der Stelle einfügen (``\\n`` beginnt einen neuen Absatz mit dem Absatzformat des geteilten). Eine Auswahl wird zuerst gelöscht. → neue Schreibmarke."""
        if caret is None and self.auswahl():
            self.loeschen()
        c = caret or self.cursor
        p = absatz_bei(self.dok, c.pfad)
        links, rechts = _teilen(p.runs, c.versatz)
        if format is None and links and isinstance(links[-1], TextRun):
            format = links[-1].format
        stuecke = text.split("\n")
        neue: list[Paragraph] = []
        for k, stueck in enumerate(stuecke):
            lauf = [TextRun(stueck, copy.deepcopy(format or CharacterFormat()))] if stueck else []
            if k == 0:
                neue.append(_neuer(p, links + lauf))
            else:
                neue.append(Paragraph(copy.deepcopy(p.format), []))
                neue[-1].runs = _verschmelzen(lauf)
        ende_laenge = sum(len(r.text) for r in neue[-1].runs if isinstance(r, TextRun)) + sum(1 for r in neue[-1].runs if isinstance(r, Image))
        neue[-1] = Paragraph(neue[-1].format, _verschmelzen(neue[-1].runs + rechts))
        nach = Caret(c.pfad[:-1] + (c.pfad[-1] + len(neue) - 1,), ende_laenge)
        return self._buchen(Aenderung("text", [self._ersetzung(c.pfad, 1, neue)], {"caret": c, "text": text, "format": copy.deepcopy(format.properties) if format else {}, "format_gesetzt": format is not None}), nach)

    def bild_einfuegen(self, bild: Image, caret: Caret | None = None) -> Caret:
        c = caret or self.cursor
        p = absatz_bei(self.dok, c.pfad)
        links, rechts = _teilen(p.runs, c.versatz)
        neu = [_neuer(p, links + [bild] + rechts)]
        return self._buchen(Aenderung("bild", [self._ersetzung(c.pfad, 1, neu)], {"caret": c, "bild": bild}), Caret(c.pfad, c.versatz + 1))

    def tabelle_einfuegen(self, zeilen: int, spalten: int, eigenschaften: dict | None = None, caret: Caret | None = None, zellformat: dict | None = None) -> Caret:
        """Eine Tabelle an der Stelle einfügen: der Absatz wird dort geteilt (davor der Text links, danach der Text rechts, auch wenn sie leer sind — wie bei Qt). → Schreibmarke in der ersten Zelle."""
        c = caret or self.cursor
        p = absatz_bei(self.dok, c.pfad)
        links, rechts = _teilen(p.runs, c.versatz)
        tab = Table(zeilen, spalten, copy.deepcopy(eigenschaften or {}),
                    [TableRow([TableCell(r, k, 1, 1, copy.deepcopy(zellformat or {}), [Paragraph(ParagraphFormat(char_format=CharacterFormat(copy.deepcopy(zellformat or {}))), [])])
                               for k in range(spalten)]) for r in range(zeilen)])
        neu = [_neuer(p, links), tab, _neuer(p, rechts)]
        nach = Caret(c.pfad[:-1] + (c.pfad[-1] + 1, 0, 0, 0), 0)
        return self._buchen(Aenderung("tabelle", [self._ersetzung(c.pfad, 1, neu)], {"caret": c, "zeilen": zeilen, "spalten": spalten,
                                                                                    "eigenschaften": copy.deepcopy(eigenschaften or {})}), nach)

    def tabelle_aendern(self, tabelle: Pfad, art: str, index: int, anzahl: int = 1) -> None:
        """Zeilen oder Spalten der Tabelle am Pfad ``tabelle`` (Pfad des Tabellenblocks) einfügen oder löschen: ``art`` = ``zeilen_einfuegen`` | ``zeilen_loeschen`` | ``spalten_einfuegen`` |
        ``spalten_loeschen``."""
        from lunivo_writer.core.editing import tabelle as T
        alt = self.dok_tabelle(tabelle[:-1], tabelle[-1])
        neu = getattr(T, art)(alt, index, anzahl)
        self._buchen_ohne_bewegung(Aenderung("tabellenstruktur", [self._ersetzung(tabelle, 1, [neu])], {"tabelle": tabelle, "art": art, "index": index, "anzahl": anzahl}))

    def freies_bild_einfuegen(self, absatz: Pfad, name: str, bild: Image, angabe: dict, neuer_absatz: bool = False) -> Caret:
        """Ein frei positioniertes Bild am Absatz verankern: die Angabe kommt in die Absatzeigenschaft ``P_BILDANKER``, das Bild unter ``name`` in ``Document.media``. Mit ``neuer_absatz``
        steht es an einem neuen leeren Absatz hinter ``absatz``. → Schreibmarke im Absatz des Bildes."""
        import json
        from lunivo_writer.core.document.objekte import P_BILDANKER
        ziel = absatz[:-1] + (absatz[-1] + 1,) if neuer_absatz else absatz
        alt = absatz_bei(self.dok, absatz)
        neu = Paragraph(ParagraphFormat(), []) if neuer_absatz else Paragraph(copy.deepcopy(alt.format), copy.deepcopy(alt.runs))
        vorhanden = neu.format.properties.get(P_BILDANKER)
        liste = (json.loads(vorhanden) if isinstance(vorhanden, str) else []) + [dict(angabe, n=name)]
        neu.format.properties[P_BILDANKER] = json.dumps(liste, separators=(",", ":"))
        if neuer_absatz:
            er = Ersetzung(absatz[:-1], absatz[-1] + 1, [], [neu])
        else:
            er = self._ersetzung(absatz, 1, [neu])
        e = Aenderung("freies_objekt", [er], {"absatz": absatz, "name": name, "angabe": dict(angabe), "neuer_absatz": neuer_absatz}, medien={name: bild})
        return self._buchen(e, Caret(ziel, 0))

    def zellen_verbinden(self, tabelle: Pfad, zeile: int, spalte: int, zeilen: int, spalten: int) -> None:
        from lunivo_writer.core.editing import tabelle as T
        alt = self.dok_tabelle(tabelle[:-1], tabelle[-1])
        neu = T.zellen_verbinden(alt, zeile, spalte, zeilen, spalten)
        self._buchen_ohne_bewegung(Aenderung("zellen_verbinden", [self._ersetzung(tabelle, 1, [neu])], {"tabelle": tabelle, "rechteck": (zeile, spalte, zeilen, spalten)}))

    def liste_anlegen(self, absaetze: list[Pfad], eigenschaften: dict) -> int:
        """Eine neue Liste anlegen; alle genannten Absätze sind ihre Einträge (Listenformat: ``eigenschaften``). → Nummer der Liste."""
        nr = max(self.dok.lists, default=0) + 1
        ers = []
        for pfad in absaetze:
            p = absatz_bei(self.dok, pfad)
            neu = Paragraph(copy.deepcopy(p.format), copy.deepcopy(p.runs))
            neu.format.list_id = nr
            ers.append(self._ersetzung(pfad, 1, [neu]))
        self._buchen_ohne_bewegung(Aenderung("liste_anlegen", ers, {"absaetze": list(absaetze), "eigenschaften": copy.deepcopy(eigenschaften)},
                                             listen={nr: ListFormat(copy.deepcopy(eigenschaften))}))
        return nr

    def liste_entfernen(self, absatz: Pfad) -> None:
        """Den Absatz aus seiner Liste nehmen; Einzug und linker Rand werden 0 (wie der Befehl „Liste aufheben“ der Oberfläche)."""
        p = absatz_bei(self.dok, absatz)
        neu = Paragraph(copy.deepcopy(p.format), copy.deepcopy(p.runs))
        neu.format.list_id = None
        neu.format.properties.update({"BlockIndent": 0, "BlockLeftMargin": 0.0})
        self._buchen_ohne_bewegung(Aenderung("liste_entfernen", [self._ersetzung(absatz, 1, [neu])], {"absatz": absatz}))

    def tabellenformat(self, tabelle: Pfad, setzen: dict, entfernen: tuple = ()) -> None:
        """Das Tabellenformat (Rahmen, Breite, Spaltenvorgaben, Kopfzeilen …) der Tabelle am Pfad ``tabelle`` ändern."""
        alt = self.dok_tabelle(tabelle[:-1], tabelle[-1])
        neu = copy.deepcopy(alt)
        for k in entfernen:
            neu.properties.pop(k, None)
        neu.properties.update(copy.deepcopy(setzen))
        self._buchen_ohne_bewegung(Aenderung("tabellenformat", [self._ersetzung(tabelle, 1, [neu])],
                                             {"tabelle": tabelle, "setzen": copy.deepcopy(setzen), "entfernen": tuple(entfernen)}))

    def zelle_teilen(self, tabelle: Pfad, zeile: int, spalte: int, spalten: int, zeilen: int) -> bool:
        """Die einfache Zelle in ``spalten`` × ``zeilen`` Zellen teilen; ``False`` (nichts geändert), wenn die Zelle verbunden ist."""
        from lunivo_writer.core.editing import tabelle as T
        alt = self.dok_tabelle(tabelle[:-1], tabelle[-1])
        neu = T.zelle_teilen(alt, zeile, spalte, spalten, zeilen)
        if neu is None:
            return False
        self._buchen_ohne_bewegung(Aenderung("zelle_teilen", [self._ersetzung(tabelle, 1, [neu])],
                                             {"tabelle": tabelle, "zelle": (zeile, spalte), "teilung": (spalten, zeilen)}))
        return True

    def zellformat(self, tabelle: Pfad, zelle: tuple[int, int], setzen: dict, entfernen: tuple = ()) -> None:
        """Das Zellformat der Zelle (``zelle`` = Zeile, Spalte) der Tabelle am Pfad ``tabelle`` ändern: ``setzen`` kommt dazu, die Namen in ``entfernen`` fallen weg. Das Zeichenformat des ersten
        Absatzes der Zelle ist wie bei Qt das Zellformat selbst und folgt mit."""
        alt = self.dok_tabelle(tabelle[:-1], tabelle[-1])
        neu = copy.deepcopy(alt)
        z = next(z for r in neu.table_rows for z in r.cells if (z.row, z.column) == tuple(zelle))
        for k in entfernen:
            z.properties.pop(k, None)
        z.properties.update(copy.deepcopy(setzen))
        if z.content and isinstance(z.content[0], Paragraph):
            z.content[0].format.char_format = CharacterFormat(dict(z.properties))
        self._buchen_ohne_bewegung(Aenderung("zellformat", [self._ersetzung(tabelle, 1, [neu])],
                                             {"tabelle": tabelle, "zelle": tuple(zelle), "setzen": copy.deepcopy(setzen), "entfernen": tuple(entfernen)}))

    def loeschen(self, von: Caret | None = None, bis: Caret | None = None) -> Caret:
        """Den Bereich löschen (ohne Angaben die Auswahl; ohne Auswahl ein Zeichen vor der Schreibmarke bleibt unverändert). Die Absätze am Rand verschmelzen; beide müssen im
        selben Behälter (Abschnitt, Zelle, Rahmen) stehen."""
        if von is None or bis is None:
            sel = self.auswahl()
            if sel is None:
                return self.cursor
            von, bis = sel
        if von > bis:
            von, bis = bis, von
        if von.pfad[:-1] != bis.pfad[:-1]:
            raise ValueError("Löschen über Zellen, Rahmen oder Abschnitte hinweg ist nicht möglich")
        erster, letzter = absatz_bei(self.dok, von.pfad), absatz_bei(self.dok, bis.pfad)
        links, _x = _teilen(erster.runs, von.versatz)
        _y, rechts = _teilen(letzter.runs, bis.versatz)
        neu = [_neuer(erster, links + rechts)]
        anzahl = bis.pfad[-1] - von.pfad[-1] + 1
        return self._buchen(Aenderung("loeschen", [self._ersetzung(von.pfad, anzahl, neu)], {"von": von, "bis": bis}), von)

    def _bereich_absaetze(self, von: Caret, bis: Caret) -> list[tuple[Pfad, Paragraph, int, int]]:
        aus = []
        for pfad, p in absaetze(self.dok):
            if (pfad, 0) < (von.pfad, 0) or (pfad, 0) > (bis.pfad, 0):
                continue
            s = von.versatz if pfad == von.pfad else 0
            e = bis.versatz if pfad == bis.pfad else laenge(p)
            aus.append((pfad, p, s, e))
        return aus

    def zeichenformat(self, eigenschaften: dict, von: Caret | None = None, bis: Caret | None = None, entfernen: tuple = ()) -> None:
        """Zeichenformat im Bereich (ohne Angaben: die Auswahl) setzen: ``eigenschaften`` werden gesetzt, die Namen in ``entfernen`` fallen weg."""
        sel = (von, bis) if von is not None and bis is not None else self.auswahl()
        if sel is None:
            return
        ers = []
        for pfad, p, s, e in self._bereich_absaetze(*sel):
            if s >= e:
                continue
            links, rest = _teilen(p.runs, s)
            mitte, rechts = _teilen(rest, e - s)
            for r in mitte:
                if isinstance(r, TextRun):
                    for k in entfernen:
                        r.format.properties.pop(k, None)
                    r.format.properties.update(copy.deepcopy(eigenschaften))
                else:
                    r.format.properties.update(copy.deepcopy(eigenschaften))
            ers.append(self._ersetzung(pfad, 1, [_neuer(p, links + mitte + rechts)]))
        if ers:
            self._buchen_ohne_bewegung(Aenderung("zeichenformat", ers, {"von": sel[0], "bis": sel[1], "eigenschaften": copy.deepcopy(eigenschaften), "entfernen": entfernen}))

    def absatzformat(self, eigenschaften: dict, von: Caret | None = None, bis: Caret | None = None, entfernen: tuple = ()) -> None:
        """Absatzformat aller Absätze im Bereich (ohne Angaben: die Auswahl oder der Absatz der Schreibmarke) setzen."""
        sel = (von, bis) if von is not None and bis is not None else (self.auswahl() or (self.cursor, self.cursor))
        ers = []
        for pfad, p, _s, _e in self._bereich_absaetze(*sel):
            neu = Paragraph(copy.deepcopy(p.format), copy.deepcopy(p.runs))
            for k in entfernen:
                neu.format.properties.pop(k, None)
            neu.format.properties.update(copy.deepcopy(eigenschaften))
            ers.append(self._ersetzung(pfad, 1, [neu]))
        if ers:
            self._buchen_ohne_bewegung(Aenderung("absatzformat", ers, {"von": sel[0], "bis": sel[1], "eigenschaften": copy.deepcopy(eigenschaften), "entfernen": entfernen}))

    def absatzformate(self, aenderungen: list[tuple[Pfad, dict, tuple]]) -> None:
        """Das Absatzformat einzelner Absätze ändern, jeder mit eigenen Werten: ``[(Pfad, Eigenschaften setzen, Namen entfernen)]`` — als ein Schritt (Rückgängig macht alle zusammen rückgängig)."""
        ers = []
        for pfad, setzen, entfernen in aenderungen:
            p = absatz_bei(self.dok, pfad)
            neu = Paragraph(copy.deepcopy(p.format), copy.deepcopy(p.runs))
            for k in entfernen:
                neu.format.properties.pop(k, None)
            neu.format.properties.update(copy.deepcopy(setzen))
            ers.append(self._ersetzung(pfad, 1, [neu]))
        if ers:
            self._buchen_ohne_bewegung(Aenderung("absatzformate", ers, {"liste": copy.deepcopy(aenderungen)}))

    def _buchen_ohne_bewegung(self, e: Aenderung) -> None:
        self._buchen_mit(e, self.cursor, self.anker)

    def _buchen_mit(self, e: Aenderung, cursor: Caret, anker: Caret | None) -> None:
        e.vorher = (self.cursor, self.anker)
        self._anwenden(e, True)
        self.cursor, self.anker = cursor, anker
        e.nachher = (cursor, anker)
        self._rueckgaengig.append(e)
        self._wiederholen.clear()
        for f in self.beobachter:
            f(e, "vor")
