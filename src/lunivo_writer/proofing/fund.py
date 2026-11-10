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


def _bestaetigen(f: ProofingIssue) -> ProofingIssue:
    """Punkt a): Quellen mit gleichem Vorschlag bestätigen den Fund und heben seine Konfidenz."""
    quellen = tuple(q for q in dict.fromkeys(v.quelle for v in f.verdraengt if v.neu == f.neu)
                    if q and q != f.quelle)
    neue = [q for q in quellen if q not in f.bestaetigt_von]
    if not neue:
        return f
    mehr = max([f.konfidenz or 0.0] + [v.konfidenz or 0.0 for v in f.verdraengt if v.quelle in neue])
    return f.ersetzt(bestaetigt_von=f.bestaetigt_von + tuple(neue), konfidenz=min(1.0, mehr + 0.1))


def _konsens(f: ProofingIssue) -> ProofingIssue:
    """Punkte a) und b): Bestätigung durch andere Quellen, ein abweichender Vorschlag macht aus „fehler“ einen „tipp“."""
    f = _bestaetigen(f)
    if f.art == "fehler" and any(v.neu and v.neu != f.neu and v.quelle and v.quelle != f.quelle for v in f.verdraengt):
        f = f.ersetzt(art="tipp")
    return f


def _gegenprobe_faellig(f: ProofingIssue, geprueft: dict) -> bool:
    """Punkt c): unbestätigter, unsicherer Fehler, den eine andere Quelle im ganzen Bereich geprüft und nicht beanstandet hat."""
    if not (f.art == "fehler" and not f.bestaetigt_von and f.konfidenz is not None and f.konfidenz < 0.9):
        return False
    return any(q != f.quelle and not any(v.quelle == q for v in f.verdraengt)
               and any(a <= f.von and f.bis <= b for a, b in bereiche) for q, bereiche in geprueft.items())


def abstimmen(funde: list[ProofingIssue], geprueft: dict | None = None, in_ruhe: dict | None = None, selbst: dict | None = None,
              gegenprobe: bool = False) -> list[ProofingIssue]:
    """Konsens zwischen den Quellen nach ``loesen`` (reine Funktion, idempotent).

    a) Melden überlagerte Funde anderer Quellen denselben Vorschlag, wird der Gewinner von ihnen ``bestaetigt_von`` und seine Konfidenz
       steigt (höchstens 1.0, nur einmal je neu hinzugekommener Quelle).
    b) Melden andere Quellen einen anderen Vorschlag, wird ein „fehler“ zum „tipp“ (Widerspruch bleibt in ``verdraengt``).
    d) Ein „fehler“, dessen Wort in ``in_ruhe`` steht, entfällt – außer das Wort steht in ``selbst`` (selbst gelernte Schreibweise).
    c) Nur mit ``gegenprobe``: ein unbestätigter Fund unter 0.9, dessen Bereich eine andere Quelle laut ``geprueft``
       (Quelle → Liste (von, bis)) vollständig geprüft und nicht beanstandet hat, wird zum „tipp“ (nie ausgeblendet)."""
    in_ruhe, selbst, geprueft = in_ruhe or {}, selbst or {}, geprueft or {}
    aus = []
    for f in funde:
        w = f.alt.lower()
        if f.art == "fehler" and in_ruhe.get(w) and w not in selbst:
            continue
        if f.neu:
            f = _konsens(f)
        if gegenprobe and _gegenprobe_faellig(f, geprueft):
            f = f.ersetzt(art="tipp")
        aus.append(f)
    return aus
