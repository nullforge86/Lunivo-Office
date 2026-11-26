"""Suchen und Ersetzen im Dokument anhand der Kennung. Der Suchauftrag der Oberfläche ist eine unveränderliche Angabe; Bedingungen an die
Formatierung kommen als Mengen (Schlüssel der passenden Zeichenformate, Ids der passenden Absätze), nie als Rückruf."""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

from framework.anbindung import Daten, fest
from framework.befehle.bearbeiten.stellen import _sitzung


@dataclass(frozen=True)
class Suchangabe:
    text: str = ""
    gross: bool = False                    # Groß-/Kleinschreibung beachten
    ganz: bool = False                     # Nur ganzes Wort suchen
    platzhalter: bool = False              # Platzhalter verwenden (? * [ ] { } < >)
    praefix: bool = False                  # Präfix beachten: der Treffer steht am Wortanfang
    suffix: bool = False                   # Suffix beachten: der Treffer steht am Wortende
    ohne_satzzeichen: bool = False         # Interpunktionszeichen ignorieren
    ohne_leerzeichen: bool = False         # Leerzeichen ignorieren
    zeichen: frozenset[str] | None = None  # Schlüssel der Zeichenformate (aus ``zeichenformate``), die passen; ``None``: keine Bedingung
    absaetze: frozenset[int] | None = None # Ids der Absätze, die passen; ``None``: keine Bedingung

    @property
    def hat_format(self) -> bool:
        return self.zeichen is not None or self.absaetze is not None

    @property
    def leer(self) -> bool:
        return not self.text and not self.hat_format


def _schluessel(format) -> str:
    return json.dumps(format, sort_keys=True, default=repr, ensure_ascii=False)


def _auftrag(a: Suchangabe):
    from core.suche.textsuche import Suchauftrag
    k = Suchauftrag(a.text, gross=a.gross, ganz=a.ganz, platzhalter=a.platzhalter, praefix=a.praefix, suffix=a.suffix,
                    ohne_satzzeichen=a.ohne_satzzeichen, ohne_leerzeichen=a.ohne_leerzeichen)
    if a.zeichen is not None:
        erlaubt = a.zeichen
        k.zeichen.append(lambda fmt: _schluessel(fmt) in erlaubt)
    if a.absaetze is not None:
        ids = a.absaetze
        k.absatz.append(lambda b: b.id in ids)
    return k


def zeichenformate(kennung: int) -> tuple[tuple[str, Mapping[str, Daten]], ...]:
    """Die verschiedenen Zeichenformate der Textstücke des Dokuments als (Schlüssel, Format)."""
    aus: dict = {}
    for absatz in _sitzung(kennung).dokument.absaetze():
        for x in absatz.inhalte:
            k = _schluessel(x.format)
            if k not in aus:
                aus[k] = fest(x.format)
    return tuple(aus.items())


def absaetze(kennung: int) -> tuple[tuple[int, str], ...]:
    """Die Absätze des Dokuments als (Id, Name der Formatvorlage)."""
    return tuple((a.id, a.format.get("vorlage") or "Standard") for a in _sitzung(kennung).dokument.absaetze())


def gueltig(angabe: Suchangabe) -> bool:
    """Lässt sich der Suchtext (mit Platzhaltern) auswerten?"""
    from core.suche.textsuche import gueltig as kern_gueltig
    return kern_gueltig(_auftrag(angabe))


def treffer(kennung: int, angabe: Suchangabe, von: int = 0, bis: int | None = None) -> tuple[tuple[int, int], ...]:
    """Alle Treffer im Bereich [von, bis) als (von, bis), Stellen im Rohtext."""
    from core.suche.textsuche import treffer as kern_treffer
    return tuple((s, e) for s, e in kern_treffer(_sitzung(kennung).dokument, _auftrag(angabe), von, bis))


def naechster(kennung: int, angabe: Suchangabe, ab: int, rueckwaerts: bool = False, von: int = 0, bis: int | None = None,
              umlauf: bool = True) -> tuple[int, int] | None:
    """Der nächste Treffer ab der Stelle ``ab`` oder ``None``."""
    from core.suche.textsuche import naechster as kern_naechster
    t = kern_naechster(_sitzung(kennung).dokument, _auftrag(angabe), ab, rueckwaerts, von, bis, umlauf=umlauf)
    return None if t is None else (t[0], t[1])


def ersatz_text(angabe: Suchangabe, ersatz: str, gefunden: str, zwischenablage: str = "") -> str:
    """Der Text, der für die Fundstelle ``gefunden`` eingesetzt wird (Sonderzeichen und Platzhalter des Ersatztextes aufgelöst)."""
    from core.suche.textsuche import ersatz_text as kern_ersatz
    return kern_ersatz(_auftrag(angabe), ersatz, gefunden, zwischenablage)


def alle_ersetzen(kennung: int, angabe: Suchangabe, ersatz: str, von: int = 0, bis: int | None = None, zeichen: Mapping[str, Daten] | None = None,
                  absatz: Mapping[str, Daten] | None = None, zwischenablage: str = "") -> int:
    """Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen; -1, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    s = _sitzung(kennung)
    try:
        with s.gruppe("Alle ersetzen"):
            return s.alle_ersetzen_auftrag(_auftrag(angabe), ersatz, von, bis, None if zeichen is None else dict(zeichen),
                                           None if absatz is None else dict(absatz), zwischenablage)
    except BearbeitungsFehler:
        return -1
