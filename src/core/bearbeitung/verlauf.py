"""Änderungsprotokoll der Bearbeitungssitzung: Schritte, Rückgängig/Wiederholen, Ereignisse, Änderungsstatus. Ohne Qt.

Jede fachliche Operation läuft in einem *Schritt*. Alle Änderungen am Modell gehen durch drei Grundbausteine (``_attr``, ``_liste``,
``_dict``); jeder trägt ein, was vorher galt. Rückgängig spielt die Einträge rückwärts ab, Wiederholen vorwärts. Schlägt eine
Operation fehl, wird ihr Teil des Protokolls sofort zurückgespielt — das Dokument bleibt, wie es war.
"""
from __future__ import annotations

import functools
from contextlib import contextmanager
from dataclasses import dataclass, field

from core.dokument.dokument import Absatz, Abschnitt, Auswahl, Rahmen, Tabelle

_FEHLT = object()
_EINFACH = (int, float, str, bool, type(None), dict, tuple)


class BearbeitungsFehler(Exception):
    """Eine Operation ist an dieser Stelle oder mit diesen Angaben nicht möglich. Das Dokument ist unverändert."""


@dataclass(frozen=True)
class Aenderung:
    """Was ein Schritt geändert hat — Layout und Ansicht gleichen damit ihre Darstellung ab."""
    name: str
    herkunft: str                         # bearbeitung | rueckgaengig | wiederholen
    bereiche: frozenset                   # text, format, liste, tabelle, objekt, abschnitt, seite, zusatz, vorlage, meta
    bloecke: frozenset                    # Ids der berührten Absätze und Tabellen
    struktur: bool                        # Blöcke kamen hinzu oder fielen weg


@dataclass
class _Schritt:
    name: str
    vor: Auswahl
    nach: Auswahl | None = None
    eintraege: list = field(default_factory=list)
    bereiche: set = field(default_factory=set)
    bloecke: set = field(default_factory=set)
    struktur: bool = False
    tippen: bool = False
    anhaengen: bool = False
    neu_bloecke: set = field(default_factory=set)       # seit der letzten Zwischenmeldung berührt
    neu_bereiche: set = field(default_factory=set)
    neu_struktur: bool = False


def schritt(name: str, bereich: str):
    """Macht aus einer Methode eine Operation: ein Schritt im Verlauf, bei Fehler alles zurück."""
    def deko(fn):
        @functools.wraps(fn)
        def huelle(self, *a, **k):
            with self.gruppe(name):
                self._offen.bereiche.add(bereich)
                self._offen.neu_bereiche.add(bereich)
                ergebnis = fn(self, *a, **k)
                self._nach_op()
                return ergebnis
        return huelle
    return deko


class Verlauf:
    """Grundlage der Sitzung: Protokoll, Transaktionen, Beobachter. Erwartet ``self.dokument`` und ``self._auswahl`` (siehe ``AuswahlTeil``)."""
    VERLAUF_GRENZE = 1000

    def __init__(self):
        self.tippformat: dict | None = None          # Zeichenformat für den nächsten getippten Text, solange die Schreibmarke steht
        self._rueck: list = []
        self._vor: list = []
        self._offen: _Schritt | None = None
        self._tiefe = 0
        self._beobachter: list = []
        self._gespeichert = 0                        # Zahl der Schritte beim letzten Speichern
        self._zaehler = 0                            # fortlaufende Zahl der ausgeführten Schritte
        self._zwischen: list = []                    # Beobachter, die auch innerhalb eines offenen Blocks nach jeder Operation melden
        self._block_cm = None                        # von außen geöffneter Block (``block_beginnen``)
        self._block_tiefe = 0
        self._aussen = 0                             # 1, solange ein solcher Block offen ist

    # ---- Beobachter ----------------------------------------------------------------------------------------------
    def beobachte(self, ruf) -> None:
        if ruf not in self._beobachter:
            self._beobachter.append(ruf)

    def vergiss(self, ruf) -> None:
        if ruf in self._beobachter:
            self._beobachter.remove(ruf)

    def beobachte_zwischen(self, ruf) -> None:
        """Wie ``beobachte``, aber ``ruf`` hört auch innerhalb eines offenen Blocks nach jeder Operation, was seit der letzten Meldung
        geschah (Herkunft ``bearbeitung``). So bleibt eine Ansicht auch mitten in einem Block aktuell."""
        if ruf not in self._zwischen:
            self._zwischen.append(ruf)

    def vergiss_zwischen(self, ruf) -> None:
        if ruf in self._zwischen:
            self._zwischen.remove(ruf)

    def _nach_op(self) -> None:
        if self._aussen and self._tiefe == 1 + self._aussen:
            if self._offen.neu_struktur:
                self._struktur_ordnen()
            self._zwischenmeldung()

    def _zwischenmeldung(self) -> None:
        s = self._offen
        if s is None or not self._zwischen or not (s.neu_bloecke or s.neu_bereiche or s.neu_struktur):
            return
        a = Aenderung(s.name, "bearbeitung", frozenset(s.neu_bereiche), frozenset(s.neu_bloecke), s.neu_struktur)
        s.neu_bloecke, s.neu_bereiche, s.neu_struktur = set(), set(), False
        for ruf in list(self._zwischen):
            ruf(a)

    # ---- Offene Blöcke von außen (Eingabe, die mehrere Operationen zu einem Rückgängig bündelt) -------------------------
    def block_beginnen(self, name: str = "Bearbeitung", anhaengen: bool = False) -> None:
        """Beginnt einen Schritt, den die Aufrufer selbst beenden. Verschachtelt sich (Zähler); alles darin ist ein Rückgängig."""
        if self._block_tiefe == 0:
            self._block_cm = self.gruppe(name)
            self._block_cm.__enter__()
            self._aussen = 1
        self._block_tiefe += 1
        if anhaengen and self._offen is not None:
            self._offen.anhaengen = True

    def block_beenden(self) -> None:
        if self._block_tiefe == 0:
            return
        self._block_tiefe -= 1
        if self._block_tiefe == 0:
            cm, self._block_cm = self._block_cm, None
            self._aussen = 0
            cm.__exit__(None, None, None)

    def block_abbrechen(self, fehler: BaseException) -> None:
        """Rollt einen von außen geöffneten Bearbeitungsblock vollständig zurück."""
        cm, self._block_cm = self._block_cm, None
        self._block_tiefe = 0
        self._aussen = 0
        if cm is not None:
            cm.__exit__(type(fehler), fehler, fehler.__traceback__)

    def block_offen(self) -> bool:
        return self._block_tiefe > 0

    def block_schliessen(self) -> None:
        """Schließt einen vergessenen Block."""
        if self._block_tiefe:
            self._block_tiefe = 1
            self.block_beenden()

    def _melde(self, s: _Schritt, herkunft: str) -> None:
        a = Aenderung(s.name, herkunft, frozenset(s.bereiche), frozenset(s.bloecke), s.struktur)
        for ruf in list(self._beobachter):
            ruf(a)

    # ---- Schritte ------------------------------------------------------------------------------------------------
    @contextmanager
    def gruppe(self, name: str):
        """Fasst mehrere Operationen zu einem Schritt zusammen (ein Rückgängig)."""
        aussen = self._tiefe == 0
        if aussen:
            self._offen = _Schritt(name, self._auswahl)
        self._tiefe += 1
        marke = len(self._offen.eintraege)
        vorher = self._auswahl
        try:
            yield self
        except BaseException:
            for e in reversed(self._offen.eintraege[marke:]):
                _zurueck(e)
            del self._offen.eintraege[marke:]
            self._auswahl = vorher
            self._tiefe -= 1
            if aussen:
                self._offen = None
            raise
        if aussen and self._offen.struktur:
            self._struktur_ordnen()
        if aussen and self._zwischen:
            self._zwischenmeldung()
        self._tiefe -= 1
        if aussen:
            s, self._offen = self._offen, None
            if s.eintraege:
                s.nach = self._auswahl
                self._abschliessen(s)

    def _struktur_ordnen(self) -> None:
        """Regel des Modells: Vor jeder Tabelle und jedem Rahmen und am Ende jedes Textflusses steht ein Absatz. Fehlende werden leer ergänzt."""
        erster = self.dokument.abschnitte[0]
        for besitzer, bloecke in list(self.dokument.behaelter()):
            i = 0
            anfang_ok = isinstance(besitzer, Abschnitt) and besitzer is not erster        # davor steht der letzte Absatz des vorigen Abschnitts
            while i < len(bloecke):
                if isinstance(bloecke[i], (Tabelle, Rahmen)) and ((i == 0 and not anfang_ok) or (i > 0 and not isinstance(bloecke[i - 1], Absatz))):
                    neu = Absatz(self._id())
                    self._liste(bloecke, i, 0, [neu]); self._beruehrt(neu.id)
                    i += 1
                i += 1
            if not isinstance(bloecke[-1], Absatz):
                neu = Absatz(self._id())
                self._liste(bloecke, len(bloecke), 0, [neu]); self._beruehrt(neu.id)

    def _abschliessen(self, s: _Schritt) -> None:
        if s.anhaengen and self._rueck:                 # Automatik: gehört zum vorigen Schritt, kein eigenes Rückgängig
            letzter = self._rueck[-1]
            letzter.eintraege.extend(s.eintraege)
            letzter.bloecke |= s.bloecke; letzter.struktur |= s.struktur; letzter.bereiche |= s.bereiche
            self._melde(s, "bearbeitung")
            return
        self._vor.clear()
        letzter = self._rueck[-1] if self._rueck else None
        if s.tippen and letzter is not None and letzter.tippen and letzter.nach == s.vor and self._gespeichert != self._zaehler:
            letzter.eintraege.extend(s.eintraege); letzter.nach = s.nach
            letzter.bloecke |= s.bloecke; letzter.struktur |= s.struktur; letzter.bereiche |= s.bereiche
        else:
            self._rueck.append(s)
            self._zaehler += 1
            if len(self._rueck) > self.VERLAUF_GRENZE:
                del self._rueck[0]
        self._melde(s, "bearbeitung")

    @property
    def kann_rueckgaengig(self) -> bool:
        return bool(self._rueck)

    @property
    def kann_wiederholen(self) -> bool:
        return bool(self._vor)

    def rueckgaengig(self) -> bool:
        if self._tiefe or not self._rueck:
            return False
        s = self._rueck.pop()
        for e in reversed(s.eintraege):
            _zurueck(e)
        self._vor.append(s)
        self._zaehler -= 1
        self._auswahl = s.vor
        self.tippformat = None
        self._melde(s, "rueckgaengig")
        return True

    def wiederholen(self) -> bool:
        if self._tiefe or not self._vor:
            return False
        s = self._vor.pop()
        for e in s.eintraege:
            _vorwaerts(e)
        self._rueck.append(s)
        self._zaehler += 1
        self._auswahl = s.nach
        self.tippformat = None
        self._melde(s, "wiederholen")
        return True

    @property
    def verlauf_laenge(self) -> int:
        return len(self._rueck)

    def verlauf_zurueck_auf(self, laenge: int) -> None:
        """Nimmt Schritte zurück, bis der Verlauf wieder ``laenge`` Schritte hat, und verwirft die Wiederholen-Schritte (Vorschauen)."""
        while len(self._rueck) > laenge and self.rueckgaengig():
            pass
        self._vor.clear()

    def verlauf_leeren(self) -> None:
        self._rueck.clear(); self._vor.clear()
        self._gespeichert = -1 if self.geaendert else self._zaehler

    @property
    def geaendert(self) -> bool:
        return self._zaehler != self._gespeichert

    def als_gespeichert_merken(self) -> None:
        self._gespeichert = self._zaehler

    def schrittnamen(self) -> tuple:
        """(Name des nächsten Rückgängig-Schritts, Name des nächsten Wiederholen-Schritts) — leer, wenn es keinen gibt."""
        return (self._rueck[-1].name if self._rueck else "", self._vor[-1].name if self._vor else "")

    # ---- Grundbausteine der Änderung -------------------------------------------------------------------------------
    def _muss_offen(self) -> _Schritt:
        if self._offen is None:
            raise RuntimeError("Änderung außerhalb eines Schritts")
        return self._offen

    def _attr(self, obj, name: str, neu) -> None:
        alt = getattr(obj, name)
        if alt is neu or (isinstance(alt, _EINFACH) and type(alt) is type(neu) and alt == neu):
            return
        s = self._muss_offen()
        setattr(obj, name, neu)
        s.eintraege.append(("a", obj, name, alt, neu))

    def _liste(self, liste: list, index: int, anzahl: int, neu=()) -> None:
        """Ersetzt ``liste[index:index+anzahl]`` durch ``neu``."""
        s = self._muss_offen()
        neu = list(neu)
        alt = liste[index:index + anzahl]
        liste[index:index + anzahl] = neu
        s.eintraege.append(("l", liste, index, alt, neu))
        s.struktur = s.neu_struktur = True

    def _dict(self, d: dict, schluessel, neu=_FEHLT) -> None:
        """Setzt ``d[schluessel]``; ohne ``neu`` wird der Eintrag entfernt."""
        alt = d.get(schluessel, _FEHLT)
        if alt is neu:
            return
        s = self._muss_offen()
        if neu is _FEHLT:
            del d[schluessel]
        else:
            d[schluessel] = neu
        s.eintraege.append(("d", d, schluessel, alt, neu))

    def _id(self) -> int:
        n = self.dokument.naechste_id
        self._attr(self.dokument, "naechste_id", n + 1)
        return n

    def _beruehrt(self, *block_ids) -> None:
        s = self._muss_offen()
        s.bloecke.update(block_ids)
        s.neu_bloecke.update(block_ids)


def _zurueck(e) -> None:
    art = e[0]
    if art == "a":
        setattr(e[1], e[2], e[3])
    elif art == "l":
        _, liste, index, alt, neu = e
        liste[index:index + len(neu)] = alt
    else:
        _, d, schluessel, alt, _neu = e
        if alt is _FEHLT:
            d.pop(schluessel, None)
        else:
            d[schluessel] = alt


def _vorwaerts(e) -> None:
    art = e[0]
    if art == "a":
        setattr(e[1], e[2], e[4])
    elif art == "l":
        _, liste, index, alt, neu = e
        liste[index:index + len(alt)] = neu
    else:
        _, d, schluessel, _alt, neu = e
        if neu is _FEHLT:
            d.pop(schluessel, None)
        else:
            d[schluessel] = neu
