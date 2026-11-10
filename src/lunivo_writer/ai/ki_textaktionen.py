"""Auswertung der KI-Antworten für Vorschläge und Synonyme (Thesaurus): Antwort lesen, prüfen, bereinigen. Die Anfrage selbst stellt ``KI``."""
from __future__ import annotations

from lunivo_writer.ai import ki_transport as T

FEHLER_FORM = {"fehler": "Die Antwort kam nicht in der erwarteten Form."}
SYNONYM_MAX, SYNONYM_LAENGE = 8, 40
SYNONYM_BAUPLAN = {"type": "object", "properties": {"woerter": {"type": "array", "items": {"type": "string"}}},
                   "required": ["woerter"], "additionalProperties": False}


def anweisung_synonyme(wort: str) -> str:
    return (f"Nenne gebräuchliche deutsche Wörter, die statt „{wort}“ an dieser Stelle stehen könnten. "
            "Achte auf den Zusammenhang: Dasselbe Wort bedeutet je nach Satz Verschiedenes. "
            "Nimm einfache, geläufige Wörter — dieser Text wird von einem Menschen mit Legasthenie geschrieben, "
            "und ein seltenes Fremdwort hilft ihm nicht. Höchstens acht, jedes in der Form, in der es im Satz "
            "stehen müsste. Fällt dir nichts Passendes ein, bleibt die Liste leer.")


def liste_lesen(roh: str, schluessel: str):
    """Die Liste unter ``schluessel`` aus der Antwort, oder None, wenn die Form nicht stimmt."""
    try:
        lst = T.json_nach_marken(roh)[schluessel]
    except (ValueError, KeyError, TypeError):
        return None
    return lst if isinstance(lst, list) else None


def _vorschlag_gueltig(v, text: str) -> bool:
    """Nur, was sich zeichengenau im Text wiederfindet, lässt sich einsetzen."""
    if not isinstance(v, dict):
        return False
    alt, neu = v.get("alt"), v.get("neu")
    return isinstance(alt, str) and isinstance(neu, str) and bool(alt.strip()) and bool(neu.strip()) and alt != neu and alt in text


def vorschlaege_bereinigen(lst: list, text: str) -> list[dict]:
    from lunivo_writer.proofing.fund import klemmen
    gut = [v for v in lst if _vorschlag_gueltig(v, text)]
    for v in gut:                                   # Sicherheit des Modells (0…1), fehlt sie oder ist sie Unsinn: 0,5
        v["konfidenz"] = klemmen(v.get("konfidenz"))
        v["quelle"] = "ki"
    gut.sort(key=lambda v: -v["konfidenz"])
    return gut


def synonyme_bereinigen(lst: list, wort: str) -> list[str]:
    sauber = []
    for w in lst:
        if isinstance(w, str) and w.strip() and len(w) < SYNONYM_LAENGE and w.strip().lower() != wort.lower() and w.strip() not in sauber:
            sauber.append(w.strip())
    return sauber[:SYNONYM_MAX]
