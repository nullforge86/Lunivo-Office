"""Zusatzdaten der Sitzung: Kommentare, Fuß-/Endnoten, Textmarken, Felder, Verweise, Stichwörter, Zitate und Quellen,
Beschriftungen, Verzeichnisse, nachverfolgte Änderungen. Ohne Qt.

Markierungen hängen als Eigenschaften am Zeichenformat (``kommentar``, ``note``, ``anker``, ``feld`` …) und wandern so mit dem
Text; die zugehörigen Texte (Kommentartext, Notentext, Quellen) liegen im Dokument.
"""
from __future__ import annotations

import dataclasses
import re

from core.dokument.dokument import Absatz, Auswahl, Kommentar, Lauf, Note, Position, format_an, normalisiere, teile
from core.dokument.formate import pruefe, verschmelze
from core.formatvorlagen.formatvorlagen import ueberschriftsebene
from core.listen.listen import nummer_text
from core.bearbeitung.texteingabe import ohne_marken
from core.bearbeitung.verlauf import BearbeitungsFehler, schritt

MARKENNAME = re.compile(r"^[^\W\d]\w{0,39}$")
VERZEICHNIS_ARTEN = ("toc", "abb", "tab", "index", "lit")
LEERES_FELD = "​"                  # ein Feld ohne Ergebnis behält eine unsichtbare Stelle


class ZusatzTeil:
    # ---- Hilfen ----------------------------------------------------------------------------------------------------------
    def _markiere(self, start: Position, ende: Position, wandle) -> None:
        """Wendet ``wandle(format) -> format`` auf alle Inhalte des Bereichs an."""
        for a, von, bis in self._stuecke(start, ende):
            if von >= bis:
                continue
            davor, rest = teile(a.inhalte, von)
            mitte, danach = teile(rest, bis - von)
            self._attr(a, "inhalte", normalisiere(davor + [dataclasses.replace(x, format=wandle(x.format)) for x in mitte] + danach))
            self._beruehrt(a.id)

    def _wandle_ueberall(self, trifft, wandle) -> None:
        """Ändert das Format aller Inhalte im Dokument, auf die ``trifft(format)`` zutrifft."""
        for a in self.dokument.absaetze():
            if any(trifft(x.format) for x in a.inhalte):
                self._attr(a, "inhalte", normalisiere([dataclasses.replace(x, format=wandle(x.format)) if trifft(x.format) else x
                                                       for x in a.inhalte]))
                self._beruehrt(a.id)

    def bereiche(self, trifft, wert=None) -> list:
        """Zusammenhängende Bereiche (je Absatz), deren Format ``trifft(format)`` erfüllt, als ``Auswahl`` in Dokumentreihenfolge.
        Mit ``wert(format)`` endet ein Bereich auch dort, wo sich dieser Wert ändert (etwa das Ziel einer Verknüpfung)."""
        funde = []
        for a in self.dokument.absaetze():
            versatz, beginn, offen = 0, None, None
            for x in a.inhalte:
                n = len(x.text) if isinstance(x, Lauf) else 1
                jetzt = (wert(x.format) if wert else True) if trifft(x.format) else None
                if beginn is not None and jetzt != offen:
                    funde.append(Auswahl(Position(a.id, beginn), Position(a.id, versatz)))
                    beginn = None
                if jetzt is not None and beginn is None:
                    beginn = versatz
                offen = jetzt
                versatz += n
            if beginn is not None:
                funde.append(Auswahl(Position(a.id, beginn), Position(a.id, versatz)))
        return funde

    def _wort_bei(self, pos: Position) -> tuple:
        """Das Wort um die Stelle; gibt es keines, das Zeichen daneben. Leerer Absatz: Fehler."""
        text = self._absatz(pos.absatz_id).text()
        if not text:
            raise BearbeitungsFehler("Hier steht kein Text, an dem die Markierung hängen könnte")
        von = bis = pos.versatz
        while von > 0 and text[von - 1].isalnum():
            von -= 1
        while bis < len(text) and text[bis].isalnum():
            bis += 1
        if von == bis:
            von, bis = (von, von + 1) if von < len(text) else (von - 1, von)
        return Position(pos.absatz_id, von), Position(pos.absatz_id, bis)

    def _bereich_oder_wort(self, auswahl: Auswahl | None) -> tuple:
        start, ende = self._bereich(auswahl)
        return self._wort_bei(start) if start == ende else (start, ende)

    # ---- Kommentare ------------------------------------------------------------------------------------------------------
    @schritt("Kommentar", "zusatz")
    def kommentar_einfuegen(self, text: str, autor: str = "", initialen: str = "", datum: str = "", auswahl: Auswahl | None = None,
                            antwort_auf: int | None = None) -> int:
        """Kommentiert den markierten Text (ohne Markierung: das Wort an der Schreibmarke). Mit ``antwort_auf`` entsteht eine
        Antwort ohne eigene Markierung. Gibt die Kommentar-Id zurück."""
        kid = max(self.dokument.kommentare, default=0) + 1
        if antwort_auf is not None:
            if antwort_auf not in self.dokument.kommentare:
                raise BearbeitungsFehler(f"Kein Kommentar mit der Id {antwort_auf}")
        else:
            start, ende = self._bereich_oder_wort(auswahl)
            self._markiere(start, ende, lambda f: verschmelze(f, {"kommentar": kid}))
        self._dict(self.dokument.kommentare, kid, Kommentar(kid, autor or self.autor, initialen, datum or self.datum, text, False, antwort_auf))
        return kid

    @schritt("Kommentar ändern", "zusatz")
    def kommentar_aendern(self, kommentar_id: int, text: str | None = None, geloest: bool | None = None) -> None:
        alt = self.dokument.kommentare.get(kommentar_id)
        if alt is None:
            raise BearbeitungsFehler(f"Kein Kommentar mit der Id {kommentar_id}")
        neu = dataclasses.replace(alt, text=alt.text if text is None else text, geloest=alt.geloest if geloest is None else bool(geloest))
        if neu != alt:
            self._dict(self.dokument.kommentare, kommentar_id, neu)
            self._beruehrt(*(b.anker.absatz_id for b in self.bereiche(lambda f: f.get("kommentar") == kommentar_id)))

    @schritt("Kommentar löschen", "zusatz")
    def kommentar_loeschen(self, kommentar_id: int | None = None) -> None:
        """Löscht einen Kommentar samt Antworten und Markierung; ohne Id alle Kommentare."""
        if kommentar_id is not None and kommentar_id not in self.dokument.kommentare:
            raise BearbeitungsFehler(f"Kein Kommentar mit der Id {kommentar_id}")
        weg = [k.id for k in self.dokument.kommentare.values()
               if kommentar_id is None or k.id == kommentar_id or k.antwort_auf == kommentar_id]
        self._wandle_ueberall(lambda f: f.get("kommentar") in weg, lambda f: verschmelze(f, {"kommentar": None}))
        for kid in weg:
            self._dict(self.dokument.kommentare, kid)

    # ---- Fuß- und Endnoten -------------------------------------------------------------------------------------------------
    @schritt("Note einfügen", "zusatz")
    def note_einfuegen(self, text: str, art: str = "f", pos: Position | None = None) -> int:
        """Fügt an der Stelle das Notenzeichen ein (hochgestellt) und legt den Notentext ab. ``art``: ``f`` Fußnote, ``e`` Endnote.
        Die Notenzeichen werden neu durchgezählt. Gibt die Id der Note zurück."""
        if art not in ("f", "e"):
            raise BearbeitungsFehler(f"Unbekannte Notenart: {art}")
        pos = self._pruefe_position(self.auswahl.kopf if pos is None else pos)
        nid = max(self.dokument.noten[art], default=0) + 1
        self._dict(self.dokument.noten[art], nid, Note(nid, art, text))
        a = self._absatz(pos.absatz_id)
        self._einsetzen(a, pos.versatz, [Lauf("?", {"note": f"{art}:{nid}", "hoch_tief": "hoch"})])
        self._noten_nummerieren()
        for fund in self.bereiche(lambda f: f.get("note") == f"{art}:{nid}"):
            self._setze(fund.kopf)
        return nid

    @schritt("Note ändern", "zusatz")
    def note_aendern(self, art: str, note_id: int, text: str) -> None:
        if note_id not in self.dokument.noten.get(art, {}):
            raise BearbeitungsFehler(f"Keine Note {art}:{note_id}")
        self._dict(self.dokument.noten[art], note_id, Note(note_id, art, text))

    @schritt("Note löschen", "zusatz")
    def note_loeschen(self, art: str, note_id: int) -> None:
        if note_id not in self.dokument.noten.get(art, {}):
            raise BearbeitungsFehler(f"Keine Note {art}:{note_id}")
        schluessel = f"{art}:{note_id}"
        for a in self.dokument.absaetze():
            if any(x.format.get("note") == schluessel for x in a.inhalte):
                self._attr(a, "inhalte", normalisiere([x for x in a.inhalte if x.format.get("note") != schluessel]))
                self._beruehrt(a.id)
        self._dict(self.dokument.noten[art], note_id)
        self._noten_nummerieren()
        self._auswahl_retten(self.dokument.anfang())

    def _noten_nummerieren(self) -> None:
        """Schreibt die Notenzeichen in Dokumentreihenfolge neu: Fußnoten 1, 2, 3 …, Endnoten i, ii, iii …"""
        zaehler = {"f": 0, "e": 0}
        gesehen: set = set()
        for a in self.dokument.absaetze():
            if not any("note" in x.format for x in a.inhalte):
                continue
            neu = []
            for x in a.inhalte:
                schluessel = x.format.get("note")
                if schluessel and isinstance(x, Lauf):
                    art = schluessel[0]
                    if schluessel in gesehen:                    # ein Zeichen, das beim Formatieren geteilt wurde: nur das erste zählt
                        continue
                    gesehen.add(schluessel)
                    zaehler[art] = zaehler.get(art, 0) + 1
                    x = Lauf(str(zaehler[art]) if art == "f" else nummer_text("roem_klein", zaehler[art]), x.format)
                neu.append(x)
            neu = normalisiere(neu)
            if neu != a.inhalte:
                self._attr(a, "inhalte", neu)
                self._beruehrt(a.id)

    def noten_reihenfolge(self, art: str = "f") -> list:
        """Die Ids der Noten in der Reihenfolge ihrer Zeichen im Text."""
        folge = []
        for a in self.dokument.absaetze():
            for x in a.inhalte:
                schluessel = x.format.get("note", "")
                if schluessel.startswith(art + ":") and int(schluessel[2:]) not in folge:
                    folge.append(int(schluessel[2:]))
        return folge

    # ---- Textmarken und Verweise ---------------------------------------------------------------------------------------------
    @schritt("Textmarke", "zusatz")
    def textmarke_setzen(self, name: str, auswahl: Auswahl | None = None) -> None:
        """Setzt eine Textmarke auf den markierten Text (ohne Markierung: auf das Wort an der Schreibmarke). Eine gleichnamige
        Marke an anderer Stelle wird versetzt."""
        if not MARKENNAME.match(name):
            raise BearbeitungsFehler("Der Name einer Textmarke beginnt mit einem Buchstaben und enthält nur Buchstaben, Ziffern und _ (höchstens 40)")
        start, ende = self._bereich_oder_wort(auswahl)
        self._marke_weg(name)
        self._markiere(start, ende, lambda f: verschmelze(f, {"anker": sorted({*f.get("anker", ()), name})}))

    def _marke_weg(self, name: str) -> None:
        def ohne(f):
            rest = [n for n in f["anker"] if n != name]
            return verschmelze(f, {"anker": rest or None})
        self._wandle_ueberall(lambda f: name in f.get("anker", ()), ohne)

    @schritt("Textmarke löschen", "zusatz")
    def textmarke_loeschen(self, name: str) -> None:
        if name not in self.textmarken():
            raise BearbeitungsFehler(f"Keine Textmarke „{name}“")
        self._marke_weg(name)

    def textmarken(self) -> dict:
        """Name → ``Auswahl`` (vom Anfang des ersten bis zum Ende des letzten markierten Stücks)."""
        marken: dict = {}
        for a in self.dokument.absaetze():
            versatz = 0
            for x in a.inhalte:
                n = len(x.text) if isinstance(x, Lauf) else 1
                for name in x.format.get("anker", ()):
                    alt = marken.get(name)
                    marken[name] = Auswahl(alt.anker if alt else Position(a.id, versatz), Position(a.id, versatz + n))
                versatz += n
        return marken

    @schritt("Verknüpfung", "zusatz")
    def link_setzen(self, ziel: str | None, auswahl: Auswahl | None = None, text: str | None = None) -> None:
        """Macht den markierten Text zur Verknüpfung auf ``ziel`` (Adresse oder ``#Textmarke``); ``None`` hebt sie auf. Mit ``text``
        wird der Bereich zuerst durch diesen Text ersetzt (oder der Text eingefügt)."""
        if text is not None:
            ende = self.ersetzen(text, auswahl)
            self._markiere(Position(ende.absatz_id, ende.versatz - len(text)), ende, lambda f: verschmelze(f, {"link": ziel}))
            return
        start, ende = self._bereich_oder_wort(auswahl)
        if ziel is None:                                 # die ganze Verknüpfung an der Stelle aufheben
            for fund in self.bereiche(lambda f: "link" in f, lambda f: f["link"]):
                if fund.anker.absatz_id == start.absatz_id and fund.anker.versatz <= start.versatz <= fund.kopf.versatz:
                    self._markiere(fund.anker, fund.kopf, lambda f: verschmelze(f, {"link": None}))
        self._markiere(start, ende, lambda f: verschmelze(f, {"link": ziel}))

    # ---- Felder ----------------------------------------------------------------------------------------------------------------
    @schritt("Feld einfügen", "zusatz")
    def feld_einfuegen(self, anweisung: str, ergebnis: str, pos: Position | None = None, format: dict | None = None) -> Position:
        """Fügt ein Feld ein: Der sichtbare Text ist das Feldergebnis, die Feldanweisung hängt am Format. Gibt die Stelle dahinter zurück."""
        if not anweisung.strip():
            raise BearbeitungsFehler("Ein Feld braucht eine Anweisung")
        if pos is None:
            if not self.auswahl.leer:
                self.loeschen()
            pos = self.auswahl.kopf
        pos = self._pruefe_position(pos)
        a = self._absatz(pos.absatz_id)
        fmt = pruefe("zeichen", format) if format is not None else ohne_marken(format_an(a, pos.versatz))
        ergebnis = ergebnis.replace("\n", " ") or LEERES_FELD
        self._einsetzen(a, pos.versatz, [Lauf(ergebnis, verschmelze(fmt, {"feld": anweisung}))])
        ziel = Position(a.id, pos.versatz + len(ergebnis))
        self._setze(ziel)
        return ziel

    def felder(self) -> list:
        """Alle Felder als (Auswahl, Anweisung, Ergebnistext) in Dokumentreihenfolge. Aufeinanderfolgende Stücke mit derselben
        Anweisung (ein Feld, das beim Formatieren geteilt wurde) zählen als ein Feld."""
        liste = []
        for a in self.dokument.absaetze():
            versatz, offen = 0, None
            for x in a.inhalte:
                n = len(x.text) if isinstance(x, Lauf) else 1
                anweisung = x.format.get("feld") if isinstance(x, Lauf) else None
                if anweisung is not None and offen == anweisung:
                    fund, _anw, text = liste[-1]
                    liste[-1] = (Auswahl(fund.anker, Position(a.id, versatz + n)), anweisung, text + x.text)
                elif anweisung is not None:
                    liste.append((Auswahl(Position(a.id, versatz), Position(a.id, versatz + n)), anweisung, x.text))
                offen = anweisung
                versatz += n
        return liste

    @schritt("Felder aktualisieren", "zusatz")
    def felder_aktualisieren(self, rechner, auswahl: Auswahl | None = None) -> int:
        """Rechnet Feldergebnisse neu: ``rechner(anweisung, bisheriger_text, absatz_id) -> str | None`` (``None``: unverändert).
        Mit ``auswahl`` nur die Felder, die der Bereich berührt. Gibt die Zahl der geänderten Felder zurück."""
        nur = None
        if auswahl is not None:
            nur = {a.id: (von, bis) for a, von, bis in self._stuecke(*self._bereich(auswahl))}
        ersatz: dict = {}                                        # Absatz-Id → [(von, bis, neuer Text)]
        for fund, anweisung, text in self.felder():
            aid, von, bis = fund.anker.absatz_id, fund.anker.versatz, fund.kopf.versatz
            if nur is not None and (aid not in nur or not (von <= nur[aid][1] and bis >= nur[aid][0])):
                continue
            neu = rechner(anweisung, text, aid)
            if neu is not None and neu != text:
                ersatz.setdefault(aid, []).append((von, bis, neu.replace("\n", " ") or LEERES_FELD))
        zahl = 0
        for aid, stellen in ersatz.items():
            a = self._absatz(aid)
            inhalte = a.inhalte
            for von, bis, text in reversed(stellen):
                davor, rest = teile(inhalte, von)
                mitte, danach = teile(rest, bis - von)
                inhalte = davor + [Lauf(text, mitte[0].format)] + danach
                zahl += 1
            self._attr(a, "inhalte", inhalte)                    # nicht zusammenziehen: jedes Feld bleibt ein eigenes Stück
            self._beruehrt(a.id)
        self._auswahl_retten(self.dokument.anfang())
        return zahl

    @schritt("Querverweis", "zusatz")
    def querverweis_einfuegen(self, marke: str, text: str, pos: Position | None = None) -> Position:
        """Verweist auf eine Textmarke: ein Feld ``REF marke \\h``, das zugleich dorthin springt."""
        if marke not in self.textmarken():
            raise BearbeitungsFehler(f"Keine Textmarke „{marke}“")
        ende = self.feld_einfuegen(f"REF {marke} \\h", text, pos)
        self._markiere(Position(ende.absatz_id, ende.versatz - max(1, len(text))), ende, lambda f: verschmelze(f, {"link": "#" + marke}))
        return ende

    # ---- Stichwörter, Zitate, Quellen ----------------------------------------------------------------------------------------------
    @schritt("Indexeintrag", "zusatz")
    def index_eintragen(self, stichwort: str | None, optionen: str = "", auswahl: Auswahl | None = None) -> None:
        """Merkt den markierten Text (oder das Wort an der Schreibmarke) für das Stichwortverzeichnis vor; ``None`` entfernt den Eintrag."""
        start, ende = self._bereich_oder_wort(auswahl)
        self._markiere(start, ende, lambda f: verschmelze(f, {"index": stichwort, "index_opt": (optionen or None) if stichwort else None}))

    @schritt("Quelle", "zusatz")
    def quelle_setzen(self, quelle: dict) -> None:
        """Legt eine Literaturquelle an oder ersetzt die mit demselben ``tag``."""
        tag = str(quelle.get("tag", "")).strip()
        if not tag:
            raise BearbeitungsFehler("Eine Quelle braucht ein Kürzel (tag)")
        for i, q in enumerate(self.dokument.quellen):
            if q.get("tag") == tag:
                self._liste(self.dokument.quellen, i, 1, [dict(quelle)])
                break
        else:
            self._liste(self.dokument.quellen, len(self.dokument.quellen), 0, [dict(quelle)])
        self._offen.struktur = self._offen.neu_struktur = False

    @schritt("Quelle löschen", "zusatz")
    def quelle_loeschen(self, tag: str) -> None:
        for i, q in enumerate(self.dokument.quellen):
            if q.get("tag") == tag:
                self._liste(self.dokument.quellen, i, 1)
                self._offen.struktur = self._offen.neu_struktur = False
                return
        raise BearbeitungsFehler(f"Keine Quelle „{tag}“")

    @schritt("Zitat einfügen", "zusatz")
    def zitat_einfuegen(self, tag: str, text: str, pos: Position | None = None) -> Position:
        """Fügt den Zitattext ein und verknüpft ihn mit der Quelle ``tag``."""
        if not any(q.get("tag") == tag for q in self.dokument.quellen):
            raise BearbeitungsFehler(f"Keine Quelle „{tag}“")
        if not text:
            raise BearbeitungsFehler("Ein Zitat braucht einen Text")
        ende = self.text_einfuegen(text.replace("\n", " "), pos)
        self._markiere(Position(ende.absatz_id, ende.versatz - len(text)), ende, lambda f: verschmelze(f, {"zitat": tag}))
        return ende

    # ---- Beschriftungen und Verzeichnisse ------------------------------------------------------------------------------------------
    @schritt("Beschriftung", "zusatz")
    def beschriftung_einfuegen(self, bezeichnung: str, text: str, nach_block: int, davor: bool = False, zahlenart: str = "dezimal") -> int:
        """Setzt unter (oder über) den Block einen Beschriftungsabsatz „Abbildung 3: Text“ mit zählendem SEQ-Feld. Gibt die Id des
        neuen Absatzes zurück; die Nummern aller Beschriftungen werden neu gezählt."""
        f = self.dokument.finde(nach_block)
        if f is None:
            raise BearbeitungsFehler(f"Kein Block mit der Id {nach_block}")
        _bes, bloecke, i, _b = f
        schalter = {"dezimal": "ARABIC", "klein": "alphabetic", "gross": "ALPHABETIC", "roem_klein": "roman", "roem_gross": "ROMAN"}
        if zahlenart not in schalter:
            raise BearbeitungsFehler(f"Unbekannte Zahlenart: {zahlenart}")
        inhalte = [Lauf(bezeichnung + " ", {}), Lauf("?", {"feld": f"SEQ {bezeichnung} \\* {schalter[zahlenart]}"})]
        if text:
            inhalte.append(Lauf(": " + text, {}))
        neu = Absatz(self._id(), inhalte, {"beschriftung": bezeichnung})
        self._liste(bloecke, i if davor else i + 1, 0, [neu])
        self._beruehrt(neu.id)
        self.beschriftungen_nummerieren()
        return neu.id

    @schritt("Beschriftungen nummerieren", "zusatz")
    def beschriftungen_nummerieren(self) -> int:
        """Zählt alle SEQ-Felder je Bezeichnung in Dokumentreihenfolge durch."""
        staende: dict = {}
        zahlenarten = {"ARABIC": "dezimal", "alphabetic": "klein", "ALPHABETIC": "gross", "roman": "roem_klein", "ROMAN": "roem_gross"}

        def rechner(anweisung, _text, _absatz_id):
            teile_ = anweisung.split()
            if len(teile_) < 2 or teile_[0].upper() != "SEQ":
                return None
            staende[teile_[1]] = staende.get(teile_[1], 0) + 1
            art = next((zahlenarten[t] for t in teile_[2:] if t in zahlenarten), "dezimal")
            return nummer_text(art, staende[teile_[1]])

        return self.felder_aktualisieren(rechner)

    def ueberschriften(self) -> list:
        """(Absatz-Id, Ebene, Text) aller Überschriften in Dokumentreihenfolge."""
        return [(a.id, e, a.text()) for a in self.dokument.absaetze() if (e := ueberschriftsebene(self.dokument, a))]

    @schritt("Verzeichnis", "zusatz")
    def verzeichnis_setzen(self, art: str, titel: str, zeilen: list, pos: Position | None = None, optionen: str = "") -> list:
        """Schreibt ein Verzeichnis (``toc`` Inhalt, ``abb``, ``tab``, ``index``, ``lit``): einen Kopfabsatz und je Eintrag eine Zeile
        ``(ebene, text)`` oder ``(ebene, text, sprungziel)``. Ein vorhandenes Verzeichnis derselben Art wird ersetzt, sonst entsteht es
        an ``pos`` (im Fließtext). Seitenzahlen liefert das Layout im Text der Zeile mit. Gibt die Ids der Absätze zurück."""
        if art not in VERZEICHNIS_ARTEN:
            raise BearbeitungsFehler(f"Unbekannte Verzeichnisart: {art}")
        alt = [a for a in self.dokument.absaetze() if a.format.get("verzeichnis_art") == art]
        if alt:
            _bes, bloecke, i, _a = self.dokument.finde(alt[0].id)
            for a in alt[1:]:
                _b, liste, j, _x = self.dokument.finde(a.id)
                if len(liste) > 1:
                    self._bloecke_entfernen(liste, j, 1)
            ziel = alt[0]
            self._attr(ziel, "inhalte", [])
        else:
            pos = self._pruefe_position(self.auswahl.kopf if pos is None else pos)
            _bes, bloecke, i, a = self.dokument.finde(pos.absatz_id)
            if a.laenge:
                i = self.dokument.finde(self._teilen(Position(a.id, a.laenge)).absatz_id)[2]
            ziel = bloecke[i]
        kopf_format = {"toc": "kopf", "verzeichnis_art": art}
        if optionen:
            kopf_format["toc_opt"] = optionen
        self._attr(ziel, "format", kopf_format)
        self._attr(ziel, "liste_id", None)
        self._attr(ziel, "inhalte", [Lauf(titel, {})] if titel else [])
        neu = []
        for eintrag in zeilen:
            ebene, text = int(eintrag[0]), str(eintrag[1])
            fmt = {"link": eintrag[2]} if len(eintrag) > 2 and eintrag[2] else {}
            neu.append(Absatz(self._id(), [Lauf(text, fmt)] if text else [], {"toc": f"zeile{min(max(ebene, 1), 9)}", "verzeichnis_art": art}))
        self._liste(bloecke, i + 1, 0, neu)
        if i + 1 + len(neu) >= len(bloecke):
            self._liste(bloecke, len(bloecke), 0, [Absatz(self._id())])
        self._beruehrt(ziel.id, *(a.id for a in neu))
        self._auswahl_retten(Position(ziel.id, 0))
        return [ziel.id] + [a.id for a in neu]

    @schritt("Verzeichnis entfernen", "zusatz")
    def verzeichnis_entfernen(self, art: str) -> None:
        for a in [a for a in self.dokument.absaetze() if a.format.get("verzeichnis_art") == art]:
            _b, liste, j, _x = self.dokument.finde(a.id)
            if len(liste) > 1 and (j + 1 < len(liste) or isinstance(liste[j - 1], Absatz)):
                self._bloecke_entfernen(liste, j, 1)
            else:
                self._attr(a, "format", {}); self._attr(a, "inhalte", [])
        self._auswahl_retten(self.dokument.anfang())

    # ---- Nachverfolgte Änderungen ----------------------------------------------------------------------------------------------------
    def aenderungen(self) -> list:
        """Alle nachverfolgten Änderungen als (Auswahl, Art ``ins``/``del``, Autor, Datum)."""
        liste = []
        for fund in self.bereiche(lambda f: "aenderung" in f, lambda f: (f["aenderung"], f.get("autor", ""), f.get("datum", ""))):
            a = self._absatz(fund.anker.absatz_id)
            fmt = teile(a.inhalte, fund.anker.versatz)[1][0].format
            liste.append((fund, fmt["aenderung"], fmt.get("autor", ""), fmt.get("datum", "")))
        return liste

    def _aenderungen_abschliessen(self, auswahl: Auswahl | None, weg: str) -> int:
        """Entfernt die Stücke der Art ``weg`` und nimmt den übrigen die Markierung."""
        nur = None
        if auswahl is not None:
            nur = {a.id: (von, bis) for a, von, bis in self._stuecke(*self._bereich(auswahl))}
        ohne = {"aenderung": None, "autor": None, "datum": None}
        zahl = 0
        for a in list(self.dokument.absaetze()):
            if not any("aenderung" in x.format for x in a.inhalte) or (nur is not None and a.id not in nur):
                continue
            neu, versatz = [], 0
            for x in a.inhalte:
                n = len(x.text) if isinstance(x, Lauf) else 1
                trifft = "aenderung" in x.format and (nur is None or (versatz < nur[a.id][1] and versatz + n > nur[a.id][0])
                                                      or (nur[a.id][0] == nur[a.id][1] and versatz <= nur[a.id][0] <= versatz + n))
                versatz += n
                if not trifft:
                    neu.append(x)
                    continue
                zahl += 1
                if x.format["aenderung"] != weg:
                    neu.append(dataclasses.replace(x, format=verschmelze(x.format, ohne)))
            self._attr(a, "inhalte", normalisiere(neu))
            self._beruehrt(a.id)
        self._auswahl_retten(self.dokument.anfang())
        return zahl

    @schritt("Änderungen annehmen", "zusatz")
    def aenderungen_annehmen(self, auswahl: Auswahl | None = None) -> int:
        """Nimmt Änderungen an (im Bereich, an der Schreibmarke — oder mit ``None`` alle): Eingefügtes bleibt, Gelöschtes verschwindet."""
        return self._aenderungen_abschliessen(auswahl, "del")

    @schritt("Änderungen ablehnen", "zusatz")
    def aenderungen_ablehnen(self, auswahl: Auswahl | None = None) -> int:
        """Lehnt Änderungen ab: Eingefügtes verschwindet, Gelöschtes bleibt."""
        return self._aenderungen_abschliessen(auswahl, "ins")
