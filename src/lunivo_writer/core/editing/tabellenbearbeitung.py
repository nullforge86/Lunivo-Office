"""Tabellenoperationen der Sitzung: anlegen, löschen, Zeilen und Spalten, Zellen verbinden und teilen, Formate, Tabelle ↔ Text.

Eine Tabelle ist immer ein volles Gitter. Eine verbundene Zelle steht an ihrer linken oberen Gitterstelle und trägt
``zeilenspanne``/``spaltenspanne``; die übrigen Gitterstellen, die sie bedeckt, sind Platzhalter mit ``verdeckt_von``.
Jede Operation rechnet ein neues Gitter aus (Zellen werden dabei nie an Ort und Stelle geändert) und setzt es in einem Stück —
so ist sie mit einem Eintrag rückgängig zu machen.
"""
from __future__ import annotations

import dataclasses

from ..document.dokument import Absatz, Auswahl, Lauf, Position, Rahmen, Tabelle, Zelle, normalisiere, teile
from ..document.formate import pruefe, verschmelze
from .texteingabe import alle_absaetze
from .verlauf import BearbeitungsFehler, schritt


# ---- Gitterrechnung (reine Funktionen) -------------------------------------------------------------------------------
def gedreht(gitter: list) -> list:
    """Zeilen und Spalten vertauscht — so gilt jede Zeilenoperation auch für Spalten."""
    if not gitter:
        return []
    neu = []
    for s in range(len(gitter[0])):
        spalte = []
        for z in range(len(gitter)):
            c = gitter[z][s]
            if c is not None:
                c = dataclasses.replace(c, zeilenspanne=c.spaltenspanne, spaltenspanne=c.zeilenspanne,
                                        verdeckt_von=c.verdeckt_von[::-1] if c.verdeckt_von else None)
            spalte.append(c)
        neu.append(spalte)
    return neu


def abgleichen(gitter: list, frisch) -> list:
    """Bringt Platzhalter und Spannen in Ordnung: Spannen enden am Tabellenrand, jede bedeckte Stelle ist ein Platzhalter, jede
    freie Stelle ohne Zelle bekommt eine neue (``frisch(zeile, spalte)``)."""
    zeilen, spalten = len(gitter), len(gitter[0]) if gitter else 0
    belegt: dict = {}
    for z in range(zeilen):
        for s in range(spalten):
            c = gitter[z][s]
            if c is None or c.verdeckt_von is not None:
                continue
            zs, ss = max(1, min(c.zeilenspanne, zeilen - z)), max(1, min(c.spaltenspanne, spalten - s))
            if (zs, ss) != (c.zeilenspanne, c.spaltenspanne):
                gitter[z][s] = dataclasses.replace(c, zeilenspanne=zs, spaltenspanne=ss)
            for dz in range(zs):
                for ds in range(ss):
                    if dz or ds:
                        belegt[(z + dz, s + ds)] = (z, s)
    for z in range(zeilen):
        for s in range(spalten):
            c = gitter[z][s]
            ziel = belegt.get((z, s))
            if ziel is not None:
                if c is None or c.verdeckt_von != ziel:
                    gitter[z][s] = Zelle([], {}, 1, 1, ziel)
            elif c is None or c.verdeckt_von is not None:
                gitter[z][s] = frisch(z, s)
    return gitter


def _anker(gitter: list):
    for z, zeile in enumerate(gitter):
        for s, c in enumerate(zeile):
            if c is not None and c.verdeckt_von is None:
                yield z, s, c


def zeilen_einfuegen(gitter: list, index: int, anzahl: int) -> list:
    g = [list(zeile) for zeile in gitter]
    for z, s, c in list(_anker(g)):
        if z < index < z + c.zeilenspanne:
            g[z][s] = dataclasses.replace(c, zeilenspanne=c.zeilenspanne + anzahl)
    spalten = len(g[0])
    g[index:index] = [[None] * spalten for _ in range(anzahl)]
    return g


def zeilen_loeschen(gitter: list, index: int, anzahl: int) -> list:
    g = [list(zeile) for zeile in gitter]
    ende = index + anzahl
    for z, s, c in list(_anker(g)):
        unten = z + c.zeilenspanne
        if z < index and unten > index:
            g[z][s] = dataclasses.replace(c, zeilenspanne=c.zeilenspanne - (min(unten, ende) - index))
        elif index <= z < ende and unten > ende:             # die Zelle beginnt in einer gelöschten Zeile und reicht darunter
            g[ende][s] = dataclasses.replace(c, zeilenspanne=unten - ende)
    del g[index:ende]
    return g


def zeilen_dehnen(gitter: list, index: int, anzahl: int) -> list:
    """Fügt Zeilen ein, die keine neuen Zellen bringen: Jede Zelle, die bis zur Zeile ``index - 1`` reicht, wird höher."""
    g = [list(zeile) for zeile in gitter]
    gesehen = set()
    for s in range(len(g[0])):
        c = g[index - 1][s]
        z0, s0 = c.verdeckt_von or (index - 1, s)
        if (z0, s0) not in gesehen:
            gesehen.add((z0, s0))
            g[z0][s0] = dataclasses.replace(g[z0][s0], zeilenspanne=g[z0][s0].zeilenspanne + anzahl)
    g[index:index] = [[None] * len(g[0]) for _ in range(anzahl)]
    return g


def verbinden(gitter: list, zeile: int, spalte: int, zeilen: int, spalten: int) -> tuple:
    """Verbindet das Rechteck zu einer Zelle. Gibt (Gitter, weggefallene leere Absätze) zurück."""
    if zeilen < 1 or spalten < 1 or zeile < 0 or spalte < 0 or zeile + zeilen > len(gitter) or spalte + spalten > len(gitter[0]):
        raise BearbeitungsFehler("Der Zellbereich liegt nicht in der Tabelle")
    g = [list(z) for z in gitter]
    inhalt: list = []
    weg: list = []
    for z, s, c in list(_anker(g)):
        drin_z = zeile <= z and z + c.zeilenspanne <= zeile + zeilen
        drin_s = spalte <= s and s + c.spaltenspanne <= spalte + spalten
        beruehrt = z < zeile + zeilen and z + c.zeilenspanne > zeile and s < spalte + spalten and s + c.spaltenspanne > spalte
        if not beruehrt:
            continue
        if not (drin_z and drin_s):
            raise BearbeitungsFehler("Der Bereich schneidet eine verbundene Zelle")
        if ist_leer(c):
            weg += c.bloecke
        else:
            inhalt += c.bloecke
        if (z, s) != (zeile, spalte):
            g[z][s] = None
    erste = g[zeile][spalte]
    if erste is None or erste.verdeckt_von is not None:
        raise BearbeitungsFehler("Der Bereich schneidet eine verbundene Zelle")
    if not inhalt:
        inhalt, weg = list(erste.bloecke), [b for b in weg if b not in erste.bloecke]
    g[zeile][spalte] = dataclasses.replace(erste, bloecke=inhalt, zeilenspanne=zeilen, spaltenspanne=spalten)
    return g, weg


def ist_leer(zelle: Zelle) -> bool:
    return len(zelle.bloecke) == 1 and isinstance(zelle.bloecke[0], Absatz) and zelle.bloecke[0].laenge == 0


def _aufteilung(gesamt: int, teile_: int) -> list:
    grund, rest = divmod(gesamt, teile_)
    return [grund + (1 if i < rest else 0) for i in range(teile_)]


class TabellenTeil:
    def _tabelle(self, tabellen_id: int) -> Tabelle:
        try:
            return self.dokument.tabelle(tabellen_id)
        except KeyError as e:
            raise BearbeitungsFehler(str(e)) from None

    def _frische_zelle(self, vorbild: Zelle | None = None) -> Zelle:
        absatz = Absatz(self._id())
        if vorbild is not None and vorbild.bloecke and isinstance(vorbild.bloecke[0], Absatz):
            muster = vorbild.bloecke[0]
            absatz.format = {k: v for k, v in muster.format.items() if k in ("vorlage", "ausrichtung", "einzug_links", "einzug_rechts",
                                                                             "abstand_vor", "abstand_nach", "zeilenabstand_art", "zeilenabstand")}
            absatz.zeichenformat = dict(muster.zeichenformat)
        return Zelle([absatz], dict(vorbild.format) if vorbild is not None else {})

    def _gitter_setzen(self, t: Tabelle, gitter: list, vorbild=None, weg_bloecke=()) -> None:
        """Setzt das neue Gitter; räumt auf, was an weggefallenen Absätzen hing; rettet die Schreibmarke."""
        alt = t.zellen

        def frisch(z, s):
            return self._frische_zelle(vorbild(z, s) if vorbild else None)

        gitter = abgleichen(gitter, frisch)
        behalten = {id(c) for zeile in gitter for c in zeile}
        geblieben = {id(b) for zeile in gitter for c in zeile for b in c.bloecke}
        weg = [b for zeile in alt for c in zeile if id(c) not in behalten for b in c.bloecke if id(b) not in geblieben]
        weg += list(weg_bloecke)
        absaetze = alle_absaetze(weg)
        ids = {a.id for a in absaetze}
        self._attr(t, "zellen", gitter)
        for oid, o in list(self.dokument.objekte.items()):
            if o.anker in ids:
                self._dict(self.dokument.objekte, oid)
        self._verwaiste_entfernen([x for a in absaetze for x in a.inhalte])
        self._beruehrt(t.id)
        self._offen.struktur = True
        self._auswahl_retten(self.zelle_anfang(t.id, 0, 0))

    # ---- Anlegen und Löschen -------------------------------------------------------------------------------------------
    @schritt("Tabelle einfügen", "tabelle")
    def tabelle_einfuegen(self, zeilen: int, spalten: int, pos: Position | None = None, format: dict | None = None,
                          spaltenbreiten=None, zellformat: dict | None = None) -> int:
        """Fügt eine Tabelle ein — am Absatzanfang vor dem Absatz, sonst wird der Absatz geteilt. Die Schreibmarke steht danach in
        der ersten Zelle. Gibt die Id der Tabelle zurück."""
        if zeilen < 1 or spalten < 1:
            raise BearbeitungsFehler("Eine Tabelle braucht mindestens eine Zeile und eine Spalte")
        if spaltenbreiten is not None and len(spaltenbreiten) != spalten:
            raise BearbeitungsFehler("Für jede Spalte wird genau eine Breite gebraucht")
        pos = self._pruefe_position(self.auswahl.kopf if pos is None else pos)
        zellformat = pruefe("zelle", zellformat or {})
        _bes, bloecke, i, _a = self.dokument.finde(pos.absatz_id)
        if pos.versatz > 0:
            self._teilen(pos)
            i += 1
        t = Tabelle(self._id(), [], list(spaltenbreiten or [0.0] * spalten), [0.0] * zeilen, pruefe("tabelle", format or {}))
        t.zellen = [[Zelle([Absatz(self._id())], dict(zellformat)) for _ in range(spalten)] for _ in range(zeilen)]
        self._liste(bloecke, i, 0, [t])
        self._beruehrt(t.id)
        self._setze(self.zelle_anfang(t.id, 0, 0))
        return t.id

    @schritt("Tabelle löschen", "tabelle")
    def tabelle_loeschen(self, tabellen_id: int) -> None:
        self._tabelle(tabellen_id)
        _bes, bloecke, i, t = self.dokument.finde(tabellen_id)
        weg = [x for a in alle_absaetze([t]) for x in a.inhalte]
        self._bloecke_entfernen(bloecke, i, 1)
        if i >= len(bloecke):                                    # ein Textfluss endet immer mit einem Absatz
            self._liste(bloecke, i, 0, [Absatz(self._id())])
        self._verwaiste_entfernen(weg)
        self._auswahl_retten(Position(alle_absaetze(bloecke[i:i + 1])[0].id, 0))

    # ---- Zeilen und Spalten ----------------------------------------------------------------------------------------------
    @schritt("Zeilen einfügen", "tabelle")
    def zeilen_einfuegen(self, tabellen_id: int, index: int, anzahl: int = 1) -> None:
        """Neue Zeilen vor der Zeile ``index`` (``index == Zeilenzahl``: am Ende). Sie übernehmen das Format der Nachbarzeile."""
        t = self._tabelle(tabellen_id)
        if not 0 <= index <= t.zeilen or anzahl < 1:
            raise BearbeitungsFehler("Die Zeile liegt nicht in der Tabelle")
        muster = t.zellen[index - 1 if index > 0 else 0]
        hoehe = t.zeilenhoehen[index - 1 if index > 0 else 0] if t.zeilenhoehen else 0.0
        self._attr(t, "zeilenhoehen", t.zeilenhoehen[:index] + [hoehe] * anzahl + t.zeilenhoehen[index:])
        self._gitter_setzen(t, zeilen_einfuegen(t.zellen, index, anzahl), lambda z, s: muster[s])

    @schritt("Spalten einfügen", "tabelle")
    def spalten_einfuegen(self, tabellen_id: int, index: int, anzahl: int = 1, breite: float | None = None) -> None:
        t = self._tabelle(tabellen_id)
        if not 0 <= index <= t.spalten or anzahl < 1:
            raise BearbeitungsFehler("Die Spalte liegt nicht in der Tabelle")
        nachbar = index - 1 if index > 0 else 0
        alt = t.zellen
        b = t.spaltenbreiten[nachbar] if breite is None else float(breite)
        self._attr(t, "spaltenbreiten", t.spaltenbreiten[:index] + [b] * anzahl + t.spaltenbreiten[index:])
        self._gitter_setzen(t, gedreht(zeilen_einfuegen(gedreht(t.zellen), index, anzahl)), lambda z, s: alt[z][nachbar])

    @schritt("Zeilen löschen", "tabelle")
    def zeilen_loeschen(self, tabellen_id: int, index: int, anzahl: int = 1) -> None:
        """Löscht Zeilen; fällt die letzte weg, verschwindet die Tabelle."""
        t = self._tabelle(tabellen_id)
        if not 0 <= index < t.zeilen or anzahl < 1 or index + anzahl > t.zeilen:
            raise BearbeitungsFehler("Die Zeilen liegen nicht in der Tabelle")
        if anzahl == t.zeilen:
            self.tabelle_loeschen(tabellen_id)
            return
        self._attr(t, "zeilenhoehen", t.zeilenhoehen[:index] + t.zeilenhoehen[index + anzahl:])
        self._gitter_setzen(t, zeilen_loeschen(t.zellen, index, anzahl))

    @schritt("Spalten löschen", "tabelle")
    def spalten_loeschen(self, tabellen_id: int, index: int, anzahl: int = 1) -> None:
        t = self._tabelle(tabellen_id)
        if not 0 <= index < t.spalten or anzahl < 1 or index + anzahl > t.spalten:
            raise BearbeitungsFehler("Die Spalten liegen nicht in der Tabelle")
        if anzahl == t.spalten:
            self.tabelle_loeschen(tabellen_id)
            return
        self._attr(t, "spaltenbreiten", t.spaltenbreiten[:index] + t.spaltenbreiten[index + anzahl:])
        self._gitter_setzen(t, gedreht(zeilen_loeschen(gedreht(t.zellen), index, anzahl)))

    # ---- Verbinden und Teilen ----------------------------------------------------------------------------------------------
    @schritt("Zellen verbinden", "tabelle")
    def zellen_verbinden(self, tabellen_id: int, zeile: int, spalte: int, zeilen: int, spalten: int) -> None:
        """Verbindet das Rechteck ab (zeile, spalte). Der Inhalt aller Zellen bleibt, leere Zellen bringen nichts mit."""
        t = self._tabelle(tabellen_id)
        gitter, weg = verbinden(t.zellen, zeile, spalte, zeilen, spalten)
        self._gitter_setzen(t, gitter, weg_bloecke=weg)

    @schritt("Zelle teilen", "tabelle")
    def zelle_teilen(self, tabellen_id: int, zeile: int, spalte: int, zeilen: int = 1, spalten: int = 1) -> None:
        """Teilt die Zelle in ``zeilen`` × ``spalten`` Zellen. Eine verbundene Zelle zerfällt zuerst entlang ihrer Gitterlinien;
        reicht das nicht, kommen Zeilen oder Spalten hinzu, und die Nachbarzellen werden entsprechend breiter oder höher.
        Der Inhalt bleibt in der ersten Teilzelle."""
        t = self._tabelle(tabellen_id)
        if not (0 <= zeile < t.zeilen and 0 <= spalte < t.spalten) or zeilen < 1 or spalten < 1:
            raise BearbeitungsFehler("Die Zelle liegt nicht in der Tabelle")
        z0, s0 = t.anker(zeile, spalte)
        zelle = t.zellen[z0][s0]
        hoch, breit = zelle.zeilenspanne, zelle.spaltenspanne
        gitter = t.zellen
        breiten, hoehen = list(t.spaltenbreiten), list(t.zeilenhoehen)
        if spalten > breit:
            mehr = spalten - breit
            letzte = s0 + breit - 1
            gitter = gedreht(zeilen_dehnen(gedreht(gitter), letzte + 1, mehr))
            anteil = breiten[letzte] / (mehr + 1)
            breiten[letzte:letzte + 1] = [anteil] * (mehr + 1)
            breit = spalten
        if zeilen > hoch:
            mehr = zeilen - hoch
            letzte = z0 + hoch - 1
            gitter = zeilen_dehnen(gitter, letzte + 1, mehr)
            anteil = hoehen[letzte] / (mehr + 1)
            hoehen[letzte:letzte + 1] = [anteil] * (mehr + 1)
            hoch = zeilen
        gitter = [list(z) for z in gitter]
        for z in range(z0, z0 + hoch):
            for s in range(s0, s0 + breit):
                gitter[z][s] = None
        z = z0
        for i, h in enumerate(_aufteilung(hoch, zeilen)):
            s = s0
            for j, b in enumerate(_aufteilung(breit, spalten)):
                teil = zelle if (i, j) == (0, 0) else self._frische_zelle(zelle)
                gitter[z][s] = dataclasses.replace(teil, zeilenspanne=h, spaltenspanne=b)
                s += b
            z += h
        self._attr(t, "spaltenbreiten", breiten)
        self._attr(t, "zeilenhoehen", hoehen)
        self._gitter_setzen(t, gitter)

    @schritt("Zellen leeren", "tabelle")
    def zellen_leeren(self, tabellen_id: int, zellen=None) -> None:
        """Löscht den Inhalt der genannten Zellen (``[(zeile, spalte)]``; ohne Angabe: aller Zellen), der Aufbau bleibt."""
        t = self._tabelle(tabellen_id)
        gitter = [list(z) for z in t.zellen]
        for z, s in self._zellen(t, zellen):
            gitter[z][s] = dataclasses.replace(self._frische_zelle(gitter[z][s]), zeilenspanne=gitter[z][s].zeilenspanne,
                                               spaltenspanne=gitter[z][s].spaltenspanne)
        self._gitter_setzen(t, gitter)

    def _zellen(self, t: Tabelle, zellen) -> list:
        if zellen is None:
            return [(z, s) for z in range(t.zeilen) for s in range(t.spalten) if t.zellen[z][s].verdeckt_von is None]
        stellen = []
        for z, s in zellen:
            if not (0 <= z < t.zeilen and 0 <= s < t.spalten):
                raise BearbeitungsFehler("Die Zelle liegt nicht in der Tabelle")
            if t.anker(z, s) not in stellen:
                stellen.append(t.anker(z, s))
        return stellen

    # ---- Formate und Maße --------------------------------------------------------------------------------------------------
    @schritt("Zellformat", "tabelle")
    def zellformat_anwenden(self, tabellen_id: int, aenderung: dict, zellen=None, ersetzen: bool = False) -> None:
        t = self._tabelle(tabellen_id)
        aenderung = pruefe("zelle", aenderung, leer_erlaubt=True)
        gitter = [list(z) for z in t.zellen]
        for z, s in self._zellen(t, zellen):
            gitter[z][s] = dataclasses.replace(gitter[z][s], format=verschmelze({} if ersetzen else gitter[z][s].format, aenderung))
        self._attr(t, "zellen", gitter)
        self._beruehrt(t.id)

    @schritt("Tabellenformat", "tabelle")
    def tabellenformat_anwenden(self, tabellen_id: int, aenderung: dict, ersetzen: bool = False) -> None:
        t = self._tabelle(tabellen_id)
        self._attr(t, "format", verschmelze({} if ersetzen else t.format, pruefe("tabelle", aenderung, leer_erlaubt=True)))
        self._beruehrt(t.id)

    @schritt("Spaltenbreite", "tabelle")
    def spaltenbreiten_setzen(self, tabellen_id: int, breiten) -> None:
        """Setzt alle Spaltenbreiten (Liste) oder einzelne (``{Spalte: Breite}``); 0 = automatisch."""
        t = self._tabelle(tabellen_id)
        neu = list(t.spaltenbreiten)
        paare = breiten.items() if isinstance(breiten, dict) else enumerate(breiten)
        for s, b in paare:
            if not 0 <= s < t.spalten or b < 0:
                raise BearbeitungsFehler("Ungültige Spaltenbreite")
            neu[s] = float(b)
        if not isinstance(breiten, dict) and len(neu) != t.spalten:
            raise BearbeitungsFehler("Für jede Spalte wird genau eine Breite gebraucht")
        self._attr(t, "spaltenbreiten", neu)
        self._beruehrt(t.id)

    @schritt("Zeilenhöhe", "tabelle")
    def zeilenhoehen_setzen(self, tabellen_id: int, hoehen) -> None:
        """Setzt die Mindesthöhen aller Zeilen (Liste) oder einzelner (``{Zeile: Höhe}``); 0 = automatisch."""
        t = self._tabelle(tabellen_id)
        neu = list(t.zeilenhoehen)
        paare = hoehen.items() if isinstance(hoehen, dict) else enumerate(hoehen)
        for z, h in paare:
            if not 0 <= z < t.zeilen or h < 0:
                raise BearbeitungsFehler("Ungültige Zeilenhöhe")
            neu[z] = float(h)
        self._attr(t, "zeilenhoehen", neu)
        self._beruehrt(t.id)

    @schritt("Spalten gleichmäßig verteilen", "tabelle")
    def spalten_gleich(self, tabellen_id: int, von: int = 0, bis: int | None = None) -> None:
        """Die Spalten ``von`` bis ``bis`` (einschließlich) bekommen dieselbe Breite; ihre Gesamtbreite bleibt."""
        t = self._tabelle(tabellen_id)
        bis = t.spalten - 1 if bis is None else bis
        if not 0 <= von <= bis < t.spalten:
            raise BearbeitungsFehler("Die Spalten liegen nicht in der Tabelle")
        neu = list(t.spaltenbreiten)
        mittel = sum(neu[von:bis + 1]) / (bis - von + 1)
        neu[von:bis + 1] = [mittel] * (bis - von + 1)
        self._attr(t, "spaltenbreiten", neu)
        self._beruehrt(t.id)

    @schritt("Zeilen gleichmäßig verteilen", "tabelle")
    def zeilen_gleich(self, tabellen_id: int, hoehe: float, von: int = 0, bis: int | None = None) -> None:
        """Die Zeilen bekommen dieselbe Mindesthöhe (die gemessene Höhe liefert das Layout)."""
        t = self._tabelle(tabellen_id)
        bis = t.zeilen - 1 if bis is None else bis
        if not 0 <= von <= bis < t.zeilen or hoehe < 0:
            raise BearbeitungsFehler("Die Zeilen liegen nicht in der Tabelle")
        neu = list(t.zeilenhoehen)
        neu[von:bis + 1] = [float(hoehe)] * (bis - von + 1)
        self._attr(t, "zeilenhoehen", neu)
        self._beruehrt(t.id)

    @schritt("Tabelle skalieren", "tabelle")
    def tabelle_skalieren(self, tabellen_id: int, faktor_breite: float = 1.0, faktor_hoehe: float = 1.0) -> None:
        t = self._tabelle(tabellen_id)
        if faktor_breite <= 0 or faktor_hoehe <= 0:
            raise BearbeitungsFehler("Der Faktor muss größer als 0 sein")
        self._attr(t, "spaltenbreiten", [b * faktor_breite for b in t.spaltenbreiten])
        self._attr(t, "zeilenhoehen", [h * faktor_hoehe for h in t.zeilenhoehen])
        if "breite" in t.format and t.format.get("breite_art", "fest") == "fest":
            self._attr(t, "format", verschmelze(t.format, {"breite": t.format["breite"] * faktor_breite}))
        self._beruehrt(t.id)

    # ---- Tabelle ↔ Text ----------------------------------------------------------------------------------------------------
    @schritt("Tabelle in Text umwandeln", "tabelle")
    def tabelle_zu_text(self, tabellen_id: int, trenner: str = "\t", geschachtelt: bool = True) -> list:
        """Ersetzt die Tabelle durch Textabsätze, ohne Läufe oder Objekte in Klartext umzuwandeln.

        Innere Tabellen werden mit ihren Zelltrennern aufgelöst oder unverändert hinter die Textabsätze verschoben.
        Bei Absatzmarken als Zelltrenner entsteht für jede Zelle ein eigener Absatz.
        """
        t = self._tabelle(tabellen_id)
        _bes, bloecke, i, _t = self.dokument.finde(tabellen_id)
        behalten = []

        def verbinden_(links, rechts, separator: str, leere_trennen: bool = True):
            if not links:
                return rechts
            if not rechts:
                return links
            if separator == "\n":
                return links + rechts
            davor, quellen_vor = links[-1]
            danach, quellen_nach = rechts[0]
            mitte = [Lauf(separator, {})] if separator and (leere_trennen or (davor and danach)) else []
            return links[:-1] + [(davor + mitte + danach, quellen_vor + quellen_nach)] + rechts[1:]

        def zellinhalt(inhalt):
            ergebnis = []
            for block in inhalt:
                if isinstance(block, Absatz):
                    stuecke = [(list(block.inhalte), [block])]
                elif isinstance(block, Rahmen):
                    stuecke = zellinhalt(block.bloecke)
                elif isinstance(block, Tabelle):
                    if not geschachtelt:
                        behalten.append(block)
                        continue
                    stuecke = []
                    for zeile in tabellenzeilen(block):
                        stuecke = verbinden_(stuecke, zeile, " ", False)
                else:
                    raise BearbeitungsFehler("Unbekannter Block in einer Tabellenzelle")
                ergebnis = verbinden_(ergebnis, stuecke, " ", False)
            return ergebnis or [([], [])]

        def tabellenzeilen(tabelle):
            zeilen = []
            for zeile in tabelle.zellen:
                ausgabe = []
                for zelle in zeile:
                    if zelle.verdeckt_von is None:
                        ausgabe = verbinden_(ausgabe, zellinhalt(zelle.bloecke), trenner)
                # Auch eine durch Zeilenspannen vollständig bedeckte Zeile bleibt eine Textzeile.
                zeilen.append(ausgabe or [([], [])])
            return zeilen

        absaetze, anker = [], {}
        for zeile in tabellenzeilen(t):
            for inhalte, quellen in zeile:
                erste = quellen[0] if quellen else None
                a = Absatz(self._id(), normalisiere(inhalte), dict(erste.format) if erste else {},
                           dict(erste.zeichenformat) if erste else {}, erste.liste_id if erste else None,
                           erste.ebene if erste else 0, erste.format_aufgeloest if erste else False)
                absaetze.append(a)
                for quelle in quellen:
                    anker.setdefault(quelle.id, a.id)
        for oid, objekt in list(self.dokument.objekte.items()):
            if objekt.anker in anker:
                self._dict(self.dokument.objekte, oid, dataclasses.replace(objekt, anker=anker[objekt.anker]))
        ersatz = list(absaetze)
        for innere in behalten:
            ersatz.extend((innere, Absatz(self._id())))
        self._liste(bloecke, i, 1, ersatz)
        self._beruehrt(tabellen_id, *(a.id for a in absaetze))
        if absaetze:
            self._setze(Position(absaetze[0].id, 0))
        else:
            self._auswahl_retten(self.dokument.anfang())
        return [a.id for a in absaetze]

    @schritt("Text in Tabelle umwandeln", "tabelle")
    def text_zu_tabelle(self, auswahl: Auswahl | None = None, trenner: str = "\t", spalten: int | None = None) -> int:
        """Macht aus den markierten Absätzen eines Textflusses eine Tabelle: je Absatz eine Zeile, Zellen an ``trenner`` getrennt.
        Gibt die Id der Tabelle zurück."""
        start, ende = self._bereich(auswahl)
        _b1, liste1, i, _a = self.dokument.finde(start.absatz_id)
        _b2, liste2, j, _b = self.dokument.finde(ende.absatz_id)
        if liste1 is not liste2 or any(not isinstance(b, Absatz) for b in liste1[i:j + 1]):
            raise BearbeitungsFehler("Nur zusammenhängende Absätze ohne Tabelle lassen sich umwandeln")
        quellen = liste1[i:j + 1]
        zeilen = []
        for a in quellen:
            stuecke, rest, text = [], a.inhalte, a.text()
            if trenner:
                while trenner in text:
                    n = text.index(trenner)
                    davor, rest = teile(rest, n)
                    rest = teile(rest, len(trenner))[1]
                    stuecke.append(davor)
                    text = text[n + len(trenner):]
            stuecke.append(rest)
            zeilen.append((a, stuecke))
        breite = spalten or max(len(s) for _a, s in zeilen)
        if breite < 1:
            raise BearbeitungsFehler("Eine Tabelle braucht mindestens eine Spalte")
        t = Tabelle(self._id(), [], [0.0] * breite, [0.0] * len(zeilen), {})
        anker = {}
        for a, stuecke in zeilen:
            if len(stuecke) > breite:                    # Überzähliges bleibt mit Trenner in der letzten Zelle
                letzte = list(stuecke[breite - 1])
                for s in stuecke[breite:]:
                    letzte += [Lauf(trenner, {})] + list(s)
                stuecke = stuecke[:breite - 1] + [letzte]
            zeile = []
            for s in range(breite):
                inhalt = normalisiere(list(stuecke[s])) if s < len(stuecke) else []
                neu_absatz = Absatz(self._id(), inhalt, dict(a.format), dict(a.zeichenformat), a.liste_id, a.ebene,
                                    a.format_aufgeloest)
                zeile.append(Zelle([neu_absatz]))
                anker.setdefault(a.id, neu_absatz.id)
            t.zellen.append(zeile)
        for oid, objekt in list(self.dokument.objekte.items()):
            if objekt.anker in anker:
                self._dict(self.dokument.objekte, oid, dataclasses.replace(objekt, anker=anker[objekt.anker]))
        neu = [t]
        if j + 1 >= len(liste1):
            neu.append(Absatz(self._id()))
        self._liste(liste1, i, j - i + 1, neu)
        self._beruehrt(t.id, *(a.id for a in quellen))
        self._setze(self.zelle_anfang(t.id, 0, 0))
        return t.id

    # ---- Auskunft --------------------------------------------------------------------------------------------------------
    def zelle_anfang(self, tabellen_id: int, zeile: int, spalte: int) -> Position:
        """Die erste Textstelle der Zelle."""
        t = self._tabelle(tabellen_id)
        return Position(alle_absaetze(t.zelle(zeile, spalte).bloecke)[0].id, 0)

    def zellen_im_bereich(self, auswahl: Auswahl | None = None):
        """(Tabellen-Id, [(zeile, spalte)]) der Zellen, die die Auswahl in einer Tabelle überstreicht (das Rechteck zwischen
        Anfangs- und Endzelle) — ``None``, wenn Anfang und Ende nicht in derselben Tabelle liegen."""
        start, ende = self._bereich(auswahl)
        a, b = self.tabelle_von(start.absatz_id), self.tabelle_von(ende.absatz_id)
        if a is None or b is None or a[0] is not b[0]:
            return None
        t = a[0]
        z1, z2 = sorted((a[1], b[1]))
        s1, s2 = sorted((a[2], b[2]))
        z2 = max(z2, *(z + t.zellen[z][s].zeilenspanne - 1 for z, s in ((a[1], a[2]), (b[1], b[2]))))
        s2 = max(s2, *(s + t.zellen[z][s].spaltenspanne - 1 for z, s in ((a[1], a[2]), (b[1], b[2]))))
        return t.id, [(z, s) for z in range(z1, z2 + 1) for s in range(s1, s2 + 1) if t.zellen[z][s].verdeckt_von is None]
