"""Fortlaufende KI-Assistenten: reine Regeln ohne Qt — wann ein Absatz neu geschickt wird, wie gedrosselt wird, was ein Ergebnis wert ist.

Der Dienst (``ai_service.KIDienst``) ruft diese Funktionen; hier steht keine Oberfläche und kein Netz.
"""
from __future__ import annotations

import time

VERZOEGERUNG_MIN, VERZOEGERUNG_MAX, VERZOEGERUNG_VORGABE = 2, 60, 15     # Sekunden Ruhe nach der letzten Änderung
MINDESTABSTAND = 10.0                 # Sekunden zwischen zwei Anfragen
HOECHSTZAHL_STUNDE = 60               # Anfragen je Stunde, danach Pause mit Meldung
MIN_ZEICHEN = 12                      # kürzere Absätze sind kein Anlass für eine Anfrage
MAX_ZEICHEN = 4000                    # längere Absätze gehen nie vollständig hinaus (Umfang bleibt „Absatz“)
BEGRUENDUNG_TRENNER = "###BEGRUENDUNG###"


def verzoegerung_begrenzen(wert) -> float:
    try:
        w = float(wert)
    except (TypeError, ValueError):
        w = VERZOEGERUNG_VORGABE
    return max(VERZOEGERUNG_MIN, min(VERZOEGERUNG_MAX, w))


def absatz_geaendert(zuletzt: str | None, jetzt: str) -> bool:
    """Lohnt eine Anfrage? Nur wenn der Absatz lang genug ist und sich gegenüber dem zuletzt gesendeten Stand wirklich geändert hat."""
    jetzt = (jetzt or "").strip()
    return len(jetzt) >= MIN_ZEICHEN and jetzt != (zuletzt or "").strip()


def eingabe_kuerzen(text: str) -> str:
    return (text or "")[:MAX_ZEICHEN]


def ergebnis_wirkt(alt: str, neu: str) -> bool:
    """Leer oder (bis auf Leerraum) gleich dem Eingang: keine Wirkung."""
    n = (neu or "").strip()
    return bool(n) and " ".join(n.split()) != " ".join((alt or "").split())


def trenne_begruendung(text: str) -> tuple[str, str]:
    """(geänderter Text, Begründung); ohne Trenner ist die Begründung leer."""
    kopf, trenner, rest = (text or "").partition(BEGRUENDUNG_TRENNER)
    return kopf.strip(), (rest.strip() if trenner else "")


class Drossel:
    """Mindestabstand und Höchstzahl je Stunde; die Uhr ist austauschbar (Tests)."""

    def __init__(self, abstand: float = MINDESTABSTAND, je_stunde: int = HOECHSTZAHL_STUNDE, uhr=time.monotonic):
        self.abstand, self.je_stunde, self.uhr = abstand, je_stunde, uhr
        self._zeiten: list[float] = []

    def warten_noch(self) -> float:
        """Sekunden bis zur nächsten erlaubten Anfrage (0 = jetzt); ``float('inf')`` heißt: Stundengrenze erreicht."""
        jetzt = self.uhr()
        self._zeiten = [t for t in self._zeiten if jetzt - t < 3600]
        if len(self._zeiten) >= self.je_stunde:
            return float("inf")
        if self._zeiten and jetzt - self._zeiten[-1] < self.abstand:
            return self.abstand - (jetzt - self._zeiten[-1])
        return 0.0

    def erlaubt(self) -> bool:
        return self.warten_noch() == 0.0

    def gesendet(self) -> None:
        self._zeiten.append(self.uhr())

    def stundengrenze(self) -> bool:
        return self.warten_noch() == float("inf")
