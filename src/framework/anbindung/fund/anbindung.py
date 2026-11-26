"""Funde der Schreibhilfe für die Oberfläche: ein eigener, unveränderlicher Fund-Typ des Frameworks (Spiegel des Fundes im Kern) und die Funktionen
des Kerns, die Funde prüfen, auflösen und abstimmen. Hinaus gehen nur ``Fund``-Werte, nie Objekte des Kerns."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

import core.korrektur as _k


@dataclass(frozen=True)
class Verdraengter:
    """Ein Fund einer anderen Quelle, der von einem besseren überlagert wurde (nur zur Nachvollziehbarkeit)."""
    quelle: str | None = None
    neu: str | None = None
    grund: str | None = None
    konfidenz: float | None = None


@dataclass(frozen=True)
class Fund:
    von: int                                   # Textposition (Zeichen), Anfang
    bis: int                                   # Ende (exklusiv)
    alt: str                                   # ursprünglicher Text
    neu: str | None = None                     # Verbesserungsvorschlag
    grund: str = ""                            # Beschreibung
    art: str = "fehler"                        # Fehlerart / Schweregrad
    wort_ebene: bool = False
    quelle: str | None = None                  # Herkunft; None = noch nicht markiert
    konfidenz: float | None = None
    verdraengt: tuple[Verdraengter, ...] = ()  # von diesem Fund überlagerte Funde anderer Quellen
    stelle: str = ""                           # bei Hinweisen auf einen Satz: der ganze Satz
    bestaetigt_von: tuple[str, ...] = ()       # andere Quellen, die denselben Vorschlag melden
    weitere: tuple = ()                        # unbekannte Schlüssel als (Name, Wert)-Paare

    @property
    def laenge(self) -> int:
        return self.bis - self.von

    @property
    def zeige_alt(self) -> str:
        return _k.zeige_leer(self.alt)

    @property
    def zeige_neu(self) -> str:
        return _k.zeige_leer(self.neu or "")

    @property
    def hat_vorschlag(self) -> bool:
        return bool(self.neu)

    def ersetzt(self, **felder: str | int | float | bool | tuple | None) -> "Fund":
        """Eine Kopie mit geänderten Feldern (der Fund selbst ist unveränderlich)."""
        return replace(self, **felder)

    def verschoben(self, delta: int) -> "Fund":
        return replace(self, von=self.von + delta, bis=self.bis + delta)

    @property
    def stellenschluessel(self) -> tuple[int, int]:
        """Sortierung nach Stelle: früher zuerst, bei gleichem Anfang der längere."""
        return (self.von, -(self.bis - self.von))


def _aus_kern(f) -> Fund:
    return Fund(f.von, f.bis, f.alt, f.neu, f.grund, f.art, f.wort_ebene, f.quelle, f.konfidenz,
                tuple(Verdraengter(v.quelle, v.neu, v.grund, v.konfidenz) for v in f.verdraengt), f.stelle, tuple(f.bestaetigt_von), tuple(f.weitere))


def _in_kern(f):
    """Ein ``Fund`` als Fund des Kerns; alles andere (Wörterbücher von außen) bleibt, wie es ist."""
    if not isinstance(f, Fund):
        return f
    return _k.ProofingIssue(f.von, f.bis, f.alt, f.neu, f.grund, f.art, f.wort_ebene, f.quelle, f.konfidenz,
                            tuple(_k.Verdraengt(v.quelle, v.neu, v.grund, v.konfidenz) for v in f.verdraengt), f.stelle, tuple(f.bestaetigt_von), tuple(f.weitere))


def _hinaus(funde) -> tuple[Fund, ...]:
    return tuple(_aus_kern(f) for f in funde)


def _hinein(funde):
    return [_in_kern(f) for f in funde]


def finde_probleme(text: str, gelernt: Mapping | None = None, schalter: Mapping | None = None) -> tuple[Fund, ...]:
    """Alle Stellen des Textes, die auffällig sind (eigene Regeln der Rechtschreib- und Stilprüfung)."""
    from core.korrektur.rechtschreibung import finde_probleme as finde
    return _hinaus(finde(text, gelernt, schalter))


def verschieben(funde: Sequence[Fund], pos: int, entfernt: int, hinzu: int) -> tuple[Fund, ...]:
    """Die Funde nach einer Textänderung an ``pos`` (so viele Zeichen entfernt und hinzugefügt) an ihre neuen Stellen schieben."""
    return _hinaus(_k.verschieben(_hinein(funde), pos, entfernt, hinzu))


def einsetzen(alt: Sequence[Fund], von: int, bis: int, neue_relativ: Sequence[Fund | Mapping]) -> tuple[Fund, ...]:
    """Die Funde des neu geprüften Bereichs ``von``–``bis`` an die Stelle der alten Funde dieses Bereichs setzen."""
    return _hinaus(_k.einsetzen(_hinein(alt), von, bis, _hinein(neue_relativ)))


def markieren(funde: Sequence[Fund | Mapping], quelle: str, text_laenge: int | None = None) -> tuple[Fund, ...]:
    """Funde gegen den Datenvertrag prüfen (ungültige fallen weg; Wörterbücher von außen werden umgewandelt), dann Quelle und Standard-Konfidenz eintragen."""
    return _hinaus(_k.markieren(_hinein(funde), quelle, text_laenge))


def loesen(funde: Sequence[Fund]) -> tuple[Fund, ...]:
    """Überlappende Funde verschiedener Quellen auflösen: der bessere bleibt, die anderen stehen in ``verdraengt``."""
    return _hinaus(_k.loesen(_hinein(funde)))


def abstimmen(funde: Sequence[Fund], geprueft: Mapping | None = None, in_ruhe: Mapping | None = None, selbst: Mapping | None = None,
              gegenprobe: bool = False) -> tuple[Fund, ...]:
    """Konsens zwischen den Quellen nach ``loesen``."""
    return _hinaus(_k.abstimmen(_hinein(funde), geprueft, in_ruhe, selbst, gegenprobe))


def uebernimm_schreibweise(original: str, verbesserung: str) -> str:
    """Die Verbesserung in der Schreibweise (groß/klein) des Originals."""
    from core.korrektur.rechtschreibung import uebernimm_schreibweise as uebernimm
    return uebernimm(original, verbesserung)


def wort_muster() -> str:
    """Das Muster (regulärer Ausdruck), nach dem die Prüfung Wörter im Text findet."""
    from core.korrektur.rechtschreibung import WORT_MUSTER
    return WORT_MUSTER.pattern


def wort_bekannt(wort: str) -> bool:
    """Steht das Wort (klein geschrieben) in der Wörterliste?"""
    from core.korrektur.rechtschreibung import lade_woerter
    return wort in lade_woerter()


def autokorrigiere(text: str, schalter: Mapping[str, bool]) -> str:
    """Die Autokorrektur auf den Text vor der Schreibmarke anwenden; ``schalter``: Name der Regelgruppe → an?"""
    from core.korrektur.rechtschreibung import korrigiere
    return korrigiere(text, lambda name: schalter[name])


def thema_aufnehmen(woerter: frozenset[str] | Sequence[str]) -> None:
    """Themenwörter sind richtig geschrieben und bekommen keine Wellenlinie."""
    from core.korrektur.woerterbuecher import thema_aufnehmen as aufnehmen
    aufnehmen(woerter)
