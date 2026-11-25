"""Chat-Antwort der KI in Einleitung, Kern (der eigentliche Text) und Erklärung teilen. Reine Logik, ohne Qt.

Primär mit festen Textmarkern (``MARKE_ANFANG``/``MARKE_ENDE``, vom Systemtext verlangt); ohne Marker eine vorsichtige
Heuristik. Im Zweifel wird nichts abgetrennt (Kern = ganzer Text)."""
from __future__ import annotations

import re

MARKE_ANFANG = "=== TEXT ==="
MARKE_ENDE = "=== ENDE ==="
FORMAT_ZEILE = (f"Wenn du einen Text schreibst oder überarbeitest, setze genau diesen Text zwischen die Zeilen {MARKE_ANFANG} und {MARKE_ENDE}. "
                "Vorrede und Erläuterungen gehören außerhalb dieser Zeilen.")

_EINLEITUNG = re.compile(r"^\s*(hier ist|hier sind|gern|gerne|natürlich|selbstverständlich)\b[^\n]*:\s*$", re.I)
_ERKLAERUNG = re.compile(r"^\s*(ich habe|änderungen|erläuterung|erklärung|anmerkung|zu den änderungen)\b", re.I)
_PARAGRAPHEN = re.compile(r"\n[ \t]*\n")


def _ohne_marke(text: str) -> str:
    return text.replace(MARKE_ANFANG, "").replace(MARKE_ENDE, "")


def teilen(text: str) -> tuple[str, str, str]:
    """(einleitung, kern, erklaerung); alle drei zusammen ergeben bis auf Marker und Leerraum den Text."""
    a = text.find(MARKE_ANFANG)
    if a >= 0:
        rest = text[a + len(MARKE_ANFANG):]
        e = rest.find(MARKE_ENDE)
        kern, nach = (rest, "") if e < 0 else (rest[:e], rest[e + len(MARKE_ENDE):])
        if kern.strip():
            return text[:a].strip(), kern.strip(), nach.strip()
        return "", _ohne_marke(text).strip(), ""
    einleitung, kern, erklaerung = "", text, ""
    zeilen = kern.split("\n")
    if len(zeilen) > 1 and _EINLEITUNG.match(zeilen[0]):
        einleitung, kern = zeilen[0].strip(), "\n".join(zeilen[1:])
    teile = _PARAGRAPHEN.split(kern.strip())
    for i in range(1, len(teile)):                           # nie der erste Absatz: der Kern darf nicht leer werden
        if _ERKLAERUNG.match(teile[i]):
            erklaerung = "\n\n".join(teile[i:])
            kern = "\n\n".join(teile[:i])
            break
    kern = kern.strip()
    if not kern:
        return "", text.strip(), ""
    return einleitung, kern, erklaerung.strip()


def strom_text(teil: str) -> str:
    """Zwischentext einer laufenden Antwort ohne Marker, auch ohne halb eingetroffene Marker am Ende."""
    t = _ohne_marke(teil)
    for m in (MARKE_ANFANG, MARKE_ENDE):
        for n in range(len(m) - 1, 0, -1):
            if teil.endswith(m[:n]):
                return t[:len(t) - n] if t.endswith(m[:n]) else t
    return t


def felder(text: str) -> dict:
    """Die Felder ``einleitung``, ``kern``, ``erklaerung`` für eine Nachricht."""
    e, k, x = teilen(text)
    return {"einleitung": e, "kern": k, "erklaerung": x}


def kern_von(nachricht: dict) -> str:
    """Kern einer Nachricht; ältere Nachrichten ohne Felder: der ganze Text."""
    return nachricht.get("kern") or nachricht["text"]
