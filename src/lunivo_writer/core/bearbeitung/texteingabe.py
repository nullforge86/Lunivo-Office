"""Textoperationen der Sitzung: einfügen, löschen, ersetzen, Absätze teilen, suchen. Ohne Qt."""
from __future__ import annotations

import dataclasses
import re

from lunivo_writer.core.dokument.dokument import Absatz, Abschnitt, Auswahl, Lauf, Position, absaetze_in, format_an, normalisiere, teile
from lunivo_writer.core.dokument.formate import pruefe, verschmelze
from .verlauf import BearbeitungsFehler, schritt

# Was an genau einer Textstelle hängt und nicht auf weitergetippten Text übergeht
NICHT_WEITERTIPPEN = ("note", "feld", "formular", "anker", "link", "index", "index_opt", "zitat", "aenderung", "autor", "datum")
# Was auch Text, der einen markierten Bereich ersetzt, nicht übernimmt
NICHT_ERSETZEN = ("note", "feld", "aenderung", "autor", "datum")
# Absatzeigenschaften, die beim Teilen am ersten Absatz bleiben
NICHT_ERBEN = ("seitenumbruch_vor", "spaltenumbruch_vor", "liste_start", "deckblatt_umbruch", "notenziel", "toc", "verzeichnis_art", "toc_opt")


def ohne_marken(fmt: dict) -> dict:
    return {k: v for k, v in fmt.items() if k not in NICHT_WEITERTIPPEN}


def tippformat_bei(a: Absatz, versatz: int) -> dict:
    """Das Format für Text, der an dieser Stelle getippt wird: das des Zeichens davor. Markierungen (Verknüpfung, Feld, Textmarke …)
    gelten nur weiter, wenn die Stelle mitten in der Markierung liegt — an ihrem Rand endet sie."""
    fmt = format_an(a, versatz)
    if versatz <= 0 or versatz >= a.laenge:
        return ohne_marken(fmt)
    danach = format_an(a, versatz + 1)
    return {k: v for k, v in fmt.items() if k not in NICHT_WEITERTIPPEN or danach.get(k) == v}


def alle_absaetze(bloecke) -> list:
    """Alle Absätze einer Blockliste, auch die in Tabellen und Rahmen."""
    return list(absaetze_in(bloecke))


class TextTeil:
    nachverfolgen = False                # Änderungen nachverfolgen: Eingefügtes und Gelöschtes wird markiert statt endgültig geändert
    autor = ""
    datum = ""                           # ISO-Text; setzt die Oberfläche vor der Bearbeitung

    # ---- Einfügen --------------------------------------------------------------------------------------------------
    @schritt("Text einfügen", "text")
    def text_einfuegen(self, text: str, pos: Position | None = None, format: dict | None = None) -> Position:
        """Fügt Text ein; ``\\n`` beginnt einen neuen Absatz (U+2029 ebenso, U+2028 bleibt ein Zeilenumbruch im Absatz). Ohne ``pos``
        an der Schreibmarke (eine Auswahl wird ersetzt). Gibt die Stelle hinter dem eingefügten Text zurück und setzt die Schreibmarke dorthin."""
        tippformat = self.tippformat
        if pos is None:
            if not self.auswahl.leer:
                self.loeschen()
            pos = self.auswahl.kopf
            self._offen.tippen = self._tiefe == 1 and len(text) == 1 and text != "\n"
        pos = self._pruefe_position(pos)
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace(" ", "\n")
        a = self._absatz(pos.absatz_id)
        if format is not None:
            fmt = pruefe("zeichen", format)
        elif tippformat is not None:
            fmt = tippformat
        else:
            fmt = tippformat_bei(a, pos.versatz)
        if self.nachverfolgen:
            fmt = verschmelze(fmt, {"aenderung": "ins", "autor": self.autor, "datum": self.datum})
        for i, stueck in enumerate(text.split("\n")):
            if i:
                pos = self._teilen(pos)
                a = self._absatz(pos.absatz_id)
            if stueck:
                if a.laenge == 0:
                    self._attr(a, "zeichenformat", ohne_marken(fmt))
                self._einsetzen(a, pos.versatz, [Lauf(stueck, fmt)])
                pos = Position(a.id, pos.versatz + len(stueck))
        self._setze(pos)
        return pos

    def _einsetzen(self, a: Absatz, versatz: int, elemente: list) -> None:
        davor, danach = teile(a.inhalte, versatz)
        self._attr(a, "inhalte", normalisiere(davor + list(elemente) + danach))
        self._beruehrt(a.id)

    @schritt("Absatz teilen", "text")
    def absatz_teilen(self, pos: Position | None = None) -> Position:
        """Neuer Absatz an der Stelle (Eingabetaste). Gibt den Anfang des neuen Absatzes zurück."""
        if pos is None:
            if not self.auswahl.leer:
                self.loeschen()
            pos = self.auswahl.kopf
        neu = self._teilen(self._pruefe_position(pos))
        self._setze(neu)
        return neu

    def _teilen(self, pos: Position) -> Position:
        _bes, bloecke, i, a = self.dokument.finde(pos.absatz_id)
        davor, danach = teile(a.inhalte, pos.versatz)
        fmt = {k: v for k, v in a.format.items() if k not in NICHT_ERBEN}
        if not danach:                                   # am Absatzende: die Folgevorlage gilt
            vorlage = self.dokument.vorlagen.get(a.format.get("vorlage", ""))
            if vorlage is not None and vorlage.folge and vorlage.folge != vorlage.name:
                fmt = {"vorlage": vorlage.folge}
        neu = Absatz(self._id(), normalisiere(danach), fmt, dict(a.zeichenformat), a.liste_id, a.ebene)
        neu.format_aufgeloest = a.format_aufgeloest if fmt.get("vorlage") == a.format.get("vorlage") else False
        self._attr(a, "inhalte", normalisiere(davor))
        self._liste(bloecke, i + 1, 0, [neu])
        self._beruehrt(a.id, neu.id)
        return Position(neu.id, 0)

    # ---- Löschen ---------------------------------------------------------------------------------------------------
    @schritt("Löschen", "text")
    def loeschen(self, auswahl: Auswahl | None = None) -> Position:
        """Löscht den markierten Bereich. Liegen Anfang und Ende im selben Textfluss, fallen die Blöcke dazwischen weg und die
        Randabsätze wachsen zusammen; sonst (über Zellgrenzen hinweg) wird nur der Inhalt geleert, der Aufbau bleibt."""
        start, ende = self._bereich(auswahl)
        if start == ende:
            return start
        if self.nachverfolgen:
            return self._loeschen_markieren(start, ende)
        # Abschnittsgrenzen gehören zum Haupttext. Eine Auswahl darüber hinweg entfernt auch diese Grenzen;
        # Zell- und Rahmengrenzen bleiben erhalten.
        vorn = self.dokument.finde(start.absatz_id)[0]
        hinten = self.dokument.finde(ende.absatz_id)[0]
        if isinstance(vorn, Abschnitt) and isinstance(hinten, Abschnitt) and vorn is not hinten:
            erster = self.dokument.abschnitte.index(vorn)
            letzter = self.dokument.abschnitte.index(hinten)
            for _ in range(letzter - erster):
                self.abschnitt_entfernen(erster + 1)
        weg: list = []
        if start.absatz_id == ende.absatz_id:
            weg += self._schneiden(self._absatz(start.absatz_id), start.versatz, ende.versatz)
        else:
            _b1, liste1, i, a = self.dokument.finde(start.absatz_id)
            _b2, liste2, j, b = self.dokument.finde(ende.absatz_id)
            if liste1 is liste2:
                davor, weg1 = teile(a.inhalte, start.versatz)
                weg2, danach = teile(b.inhalte, ende.versatz)
                weg += weg1 + weg2
                for x in alle_absaetze(liste1[i + 1:j]):
                    weg += x.inhalte
                self._attr(a, "inhalte", normalisiere(davor + danach))
                self._umankern(b.id, a.id)
                self._bloecke_entfernen(liste1, i + 1, j - i)
                self._beruehrt(a.id)
            else:
                for absatz, von, bis in self._stuecke(start, ende):
                    weg += self._schneiden(absatz, von, bis)
        self._verwaiste_entfernen(weg)
        self._setze(start)
        return start

    def _schneiden(self, a: Absatz, von: int, bis: int) -> list:
        if von >= bis:
            return []
        davor, rest = teile(a.inhalte, von)
        mitte, danach = teile(rest, bis - von)
        self._attr(a, "inhalte", normalisiere(davor + danach))
        self._beruehrt(a.id)
        return mitte

    def _loeschen_markieren(self, start: Position, ende: Position) -> Position:
        """Nachverfolgtes Löschen: selbst eingefügter Text verschwindet, alles andere wird als gelöscht markiert."""
        marke = {"aenderung": "del", "autor": self.autor, "datum": self.datum}
        for a, von, bis in self._stuecke(start, ende):
            davor, rest = teile(a.inhalte, von)
            mitte, danach = teile(rest, bis - von)
            neu = [x for x in mitte if x.format.get("aenderung") != "ins"]
            neu = [dataclasses.replace(x, format=verschmelze(x.format, marke)) for x in neu]
            self._attr(a, "inhalte", normalisiere(davor + neu + danach))
            self._beruehrt(a.id)
        self._setze(start)
        return start

    def _bloecke_entfernen(self, bloecke: list, index: int, anzahl: int) -> None:
        """Nimmt Blöcke aus einer Liste und mit ihnen die Objekte, die an ihren Absätzen verankert sind."""
        ids = {a.id for a in alle_absaetze(bloecke[index:index + anzahl])}
        for oid, o in list(self.dokument.objekte.items()):
            if o.anker in ids:
                self._dict(self.dokument.objekte, oid)
        self._beruehrt(*(b.id for b in bloecke[index:index + anzahl]))
        self._liste(bloecke, index, anzahl)

    def _umankern(self, von_id: int, zu_id: int) -> None:
        for oid, o in list(self.dokument.objekte.items()):
            if o.anker == von_id:
                self._dict(self.dokument.objekte, oid, dataclasses.replace(o, anker=zu_id))

    def _verwaiste_entfernen(self, entfernt: list) -> None:
        """Kommentare und Noten, deren letzte Markierung gerade gelöscht wurde, fallen aus dem Dokument."""
        kommentare = {x.format["kommentar"] for x in entfernt if "kommentar" in x.format}
        noten = {x.format["note"] for x in entfernt if "note" in x.format}
        if not kommentare and not noten:
            return
        for a in self.dokument.absaetze():
            for x in a.inhalte:
                kommentare.discard(x.format.get("kommentar"))
                noten.discard(x.format.get("note"))
        for kid in kommentare:
            for k in [k for k in self.dokument.kommentare.values() if k.id == kid or k.antwort_auf == kid]:
                self._dict(self.dokument.kommentare, k.id)
        for schluessel in noten:
            art, _, nid = schluessel.partition(":")
            if nid.isdigit() and int(nid) in self.dokument.noten.get(art, {}):
                self._dict(self.dokument.noten[art], int(nid))
        if noten:
            self._noten_nummerieren()

    @schritt("Löschen", "text")
    def zeichen_loeschen(self, vorwaerts: bool = False) -> Position:
        """Entf (``vorwaerts``) oder Rücktaste. Am Absatzrand wachsen zwei Absätze zusammen; vor und hinter Tabellen geschieht nichts."""
        if not self.auswahl.leer:
            return self.loeschen()
        pos = self.auswahl.kopf
        _bes, bloecke, i, a = self.dokument.finde(pos.absatz_id)
        if vorwaerts:
            if pos.versatz < a.laenge:
                return self.loeschen(Auswahl(pos, Position(a.id, pos.versatz + 1)))
            if i + 1 < len(bloecke) and isinstance(bloecke[i + 1], Absatz):
                return self.loeschen(Auswahl(pos, Position(bloecke[i + 1].id, 0)))
            return pos
        if pos.versatz > 0:
            return self.loeschen(Auswahl(Position(a.id, pos.versatz - 1), pos))
        if a.liste_id is not None:
            self._attr(a, "liste_id", None); self._attr(a, "ebene", 0)
            self._beruehrt(a.id); self._offen.bereiche.add("liste")
            return pos
        if i > 0 and isinstance(bloecke[i - 1], Absatz):
            davor = bloecke[i - 1]
            return self.loeschen(Auswahl(Position(davor.id, davor.laenge), pos))
        return pos

    @schritt("Ersetzen", "text")
    def ersetzen(self, text: str, auswahl: Auswahl | None = None, format: dict | None = None) -> Position:
        """Ersetzt den Bereich durch Text; ohne ``format`` behält der neue Text das Format des Bereichsanfangs."""
        start, ende = self._bereich(auswahl)
        if format is None and start != ende:
            a = self._absatz(start.absatz_id)
            format = {k: v for k, v in format_an(a, min(start.versatz + 1, a.laenge)).items() if k not in NICHT_ERSETZEN}
        pos = self.loeschen(Auswahl(start, ende))
        return self.text_einfuegen(text, pos, format)

    @schritt("Inhalt ersetzen", "text")
    def inhalt_setzen(self, text: str) -> Position:
        """Der ganze Dokumenttext wird durch reinen Text ersetzt (ein Abschnitt, Absätze je Zeile)."""
        d = self.dokument
        erster = d.abschnitte[0]
        self._liste(d.abschnitte, 1, len(d.abschnitte) - 1)
        neu = Absatz(self._id())
        self._bloecke_entfernen(erster.bloecke, 0, len(erster.bloecke))
        self._liste(erster.bloecke, 0, 0, [neu])
        for name in ("kommentare", "objekte"):
            for schluessel in list(getattr(d, name)):
                self._dict(getattr(d, name), schluessel)
        for art in d.noten:
            for nid in list(d.noten[art]):
                self._dict(d.noten[art], nid)
        return self.text_einfuegen(text, Position(neu.id, 0), {})

    @schritt("Sortieren", "text")
    def absaetze_umstellen(self, absatz_ids: list, ordnung: list) -> None:
        """Stellt aufeinanderfolgende Absätze eines Textflusses um: ``ordnung`` sind die Indizes in ``absatz_ids`` in der neuen Reihenfolge."""
        f = self.dokument.finde(absatz_ids[0])
        if f is None:
            raise BearbeitungsFehler(f"Kein Absatz mit der Id {absatz_ids[0]}")
        _b, liste, i, _a = f
        gruppe = liste[i:i + len(absatz_ids)]
        if [getattr(b, "id", None) for b in gruppe] != list(absatz_ids) or sorted(ordnung) != list(range(len(gruppe))):
            raise BearbeitungsFehler("Die Absätze liegen nicht nebeneinander im selben Textfluss")
        self._liste(liste, i, len(gruppe), [gruppe[k] for k in ordnung])
        self._beruehrt(*absatz_ids)

    # ---- Suchen ----------------------------------------------------------------------------------------------------
    def suche(self, muster: str, *, gross_klein: bool = False, ganzes_wort: bool = False, regex: bool = False) -> list:
        """Alle Fundstellen als ``Auswahl`` in Dokumentreihenfolge (Treffer reichen nicht über Absatzgrenzen)."""
        if not muster:
            return []
        ausdruck = muster if regex else re.escape(muster)
        if ganzes_wort:
            ausdruck = r"(?<!\w)(?:" + ausdruck + r")(?!\w)"
        try:
            such = re.compile(ausdruck, 0 if gross_klein else re.IGNORECASE)
        except re.error as e:
            raise BearbeitungsFehler(f"Ungültiges Suchmuster: {e}") from None
        funde = []
        for a in self.dokument.absaetze():
            for m in such.finditer(a.text()):
                if m.end() > m.start():
                    funde.append(Auswahl(Position(a.id, m.start()), Position(a.id, m.end())))
        return funde

    @schritt("Alle ersetzen", "text")
    def alle_ersetzen(self, muster: str, ersatz: str, **optionen) -> int:
        funde = self.suche(muster, **optionen)
        for fund in reversed(funde):
            self.ersetzen(ersatz, fund)
        return len(funde)

    # ---- Auskunft --------------------------------------------------------------------------------------------------
    def text(self, auswahl: Auswahl | None = None) -> str:
        if auswahl is None:
            return self.dokument.text()
        return "\n".join(a.text()[von:bis] for a, von, bis in self._stuecke(*self._bereich(auswahl)))

    def ist_im_haupttext(self, absatz_id: int) -> bool:
        f = self.dokument.finde(absatz_id)
        return f is not None and isinstance(f[0], Abschnitt)

    def nachbar(self, block_id: int, schritt_weite: int = 1):
        """Der nächste (``+1``) oder vorige (``-1``) Block im selben Textfluss, sonst ``None``."""
        f = self.dokument.finde(block_id)
        if f is None:
            return None
        _bes, bloecke, i, _b = f
        j = i + schritt_weite
        return bloecke[j] if 0 <= j < len(bloecke) else None

    def tabelle_von(self, absatz_id: int):
        """(Tabelle, Zeile, Spalte) der innersten Zelle, in der der Absatz steht — ``None`` im Fließtext."""
        f = self.dokument.finde(absatz_id)
        if f is None or isinstance(f[0], Abschnitt):
            return None
        for t in self.dokument.tabellen():
            for z, zeile in enumerate(t.zellen):
                for s, zelle in enumerate(zeile):
                    if zelle is f[0]:
                        return t, z, s
        return None
