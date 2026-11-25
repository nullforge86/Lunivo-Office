"""Was ein KI-Modell kann und was erlaubt ist — reine Logik ohne Qt. Schicht 1: kennt weder Dienst noch Oberfläche.

Denkstufen, Fähigkeitentabelle der Claude-Modelle, Prüfung eines Bildanhangs und die Frage, welche Werkzeugarten im Modus „automatisch“
ohne Rückfrage laufen dürfen."""
from __future__ import annotations

import os

# Schlüssel -> Anzeigename und die Werte je Anbieter. None = Feld weglassen (Vorgabe des Anbieters).
# „auto“ ist das bisherige Verhalten: Claude low + adaptives Denken, OpenAI nichts senden, Ollama think=False.
DENKSTUFEN: dict[str, dict] = {
    "auto":    {"name": "Automatisch", "claude": "low",  "openai": None,      "ollama": False},
    "aus":     {"name": "Aus",         "claude": None,   "openai": "minimal", "ollama": False},
    "niedrig": {"name": "Niedrig",     "claude": "low",  "openai": "low",     "ollama": "low"},
    "mittel":  {"name": "Mittel",      "claude": "medium", "openai": "medium", "ollama": "medium"},
    "hoch":    {"name": "Hoch",        "claude": "high", "openai": "high",    "ollama": "high"},
}
DENK_VORGABE = "auto"

# Claude-Modelle nach Namensanfang: (kann denken, kann Bilder). Unbekannte claude-Modelle: wie bisher im Code angenommen, Denken ja.
CLAUDE_FAEHIGKEITEN: dict[str, tuple[bool, bool]] = {
    "claude-opus": (True, True),
    "claude-sonnet": (True, True),
    "claude-haiku": (False, True),
}

BILD_TYPEN = {"image/png": "PNG", "image/jpeg": "JPEG", "image/webp": "WebP"}
BILD_MAX_BYTES = 5 * 1024 * 1024

WERKZEUG_MODI = ("fragen", "automatisch")
WERKZEUG_AUTOMATISCH = ("lesen", "schreiben")          # alles andere fragt weiter


def denkstufe(schluessel) -> str:
    return schluessel if schluessel in DENKSTUFEN else DENK_VORGABE


def claude_faehig(modell: str) -> tuple[bool, bool]:
    """(denken, bild) für ein Claude-Modell."""
    m = str(modell or "")
    for anfang, f in CLAUDE_FAEHIGKEITEN.items():
        if m.startswith(anfang):
            return f
    return (True, True)


def bildtyp_aus_inhalt(kopf: bytes) -> str | None:
    """Medientyp nach den ersten Bytes der Datei (nicht nach der Endung)."""
    if kopf.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if kopf.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if kopf[:4] == b"RIFF" and kopf[8:12] == b"WEBP":
        return "image/webp"
    return None


def bild_pruefen(pfad) -> dict:
    """Prüft einen Bildanhang. Liefert {pfad, typ, bytes} oder {fehler}."""
    pfad = str(pfad or "")
    if not pfad or not os.path.isfile(pfad):
        return {"fehler": "Die Bilddatei gibt es nicht."}
    try:
        groesse = os.path.getsize(pfad)
        if groesse > BILD_MAX_BYTES:
            return {"fehler": f"Das Bild ist zu groß ({groesse / 1024 / 1024:.1f} MB). Erlaubt sind höchstens {BILD_MAX_BYTES // 1024 // 1024} MB."}
        with open(pfad, "rb") as fh:
            typ = bildtyp_aus_inhalt(fh.read(16))
    except OSError as e:
        return {"fehler": f"Die Bilddatei lässt sich nicht lesen: {e.strerror or e}"}
    if typ is None:
        return {"fehler": "Dieses Bildformat wird nicht unterstützt. Erlaubt sind PNG, JPEG und WebP."}
    return {"pfad": pfad, "typ": typ, "bytes": groesse}


def werkzeug_erlaubt(modus: str, art: str) -> bool:
    """Darf ein Werkzeug dieser Art ohne Rückfrage laufen? Nur im Modus „automatisch“ und nur für Lesen und Schreiben.
    Löschen, Netzwerk und Unbekanntes fragen immer. Die Rückfrage zum Programmstart („start“) und die Datenschutz-Einwilligung
    gehen nicht über diese Funktion und bleiben immer aktiv."""
    return modus == "automatisch" and art in WERKZEUG_AUTOMATISCH
