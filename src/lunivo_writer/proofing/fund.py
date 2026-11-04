"""Herkunft und Sicherheit eines Fundes; Auflösung, wenn mehrere Quellen dieselbe Stelle melden.

Jeder Fund trägt `quelle` ("eigen" | "languagetool" | "ki") und `konfidenz` (0…1). Eigene Regeln und LanguageTool liefern keine
echte Wahrscheinlichkeit; ihre Werte sind feste Schätzungen je Fundart (unten), nur bei der KI kommt die Zahl vom Modell.
Bei Überschneidung gewinnt: höchste Konfidenz, dann Art (Fehler vor Tipp vor Hinweis), dann Quelle (eigen vor LanguageTool vor KI)."""
from __future__ import annotations

from lunivo_writer.models.proofing import ProofingIssue, Verdraengt

ART_RANG = {"fehler": 0, "tipp": 1, "hinweis": 2}
QUELLE_RANG = {"eigen": 0, "languagetool": 1, "ki": 2}
STANDARD = {("eigen", True): 0.9, ("eigen", False): 0.8, ("languagetool", True): 0.7, ("languagetool", False): 0.5,
            ("ki", True): 0.5, ("ki", False): 0.5}


def klemmen(wert, vorgabe: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(wert)))
    except (TypeError, ValueError):
        return vorgabe


def markieren(funde: list, quelle: str, text_laenge: int | None = None) -> list[ProofingIssue]:
    """Funde gegen den Datenvertrag ``ProofingIssue`` prüfen (ungültige fallen weg; Wörterbücher von außen werden umgewandelt), dann Quelle und
    – falls nicht vorhanden – Standard-Konfidenz eintragen. ``text_laenge``: Länge des geprüften Textes; Bereiche darüber hinaus sind ungültig."""
    from lunivo_writer.models.proofing import bereinigen
    out = []
    for f in bereinigen(funde, text_laenge):
        wort_oder_vorschlag = f.wort_ebene or f.art == "fehler"
        out.append(f.ersetzt(quelle=f.quelle or quelle,
                             konfidenz=klemmen(f.konfidenz) if f.konfidenz is not None else STANDARD.get((quelle, wort_oder_vorschlag), 0.5)))
    return out


def _rang(f: ProofingIssue):
    return (-(f.konfidenz if f.konfidenz is not None else 0.5), ART_RANG.get(f.art, 3), QUELLE_RANG.get(f.quelle or "eigen", 3),
            f.von, -(f.bis - f.von))


def loesen(funde: list[ProofingIssue]) -> list[ProofingIssue]:
    """Überschneidende Funde auflösen: der beste bleibt, die unterlegenen werden nicht angezeigt, aber als `verdraengt` vermerkt."""
    belegt: list[ProofingIssue] = []
    for f in sorted(funde, key=_rang):
        gegner = [i for i, b in enumerate(belegt) if f.von < b.bis and b.von < f.bis]
        if gegner:
            b = belegt[gegner[0]]
            belegt[gegner[0]] = b.ersetzt(verdraengt=b.verdraengt + (Verdraengt(f.quelle, f.neu, f.grund, f.konfidenz),))
        else:
            belegt.append(f)
    return sorted(belegt, key=lambda f: f.stellenschluessel)
