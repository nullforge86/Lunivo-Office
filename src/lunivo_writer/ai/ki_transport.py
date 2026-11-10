"""Gemeinsames der Anbieter-Anfragen: HTTP-Aufruf, Antwort als Wörterbuch, Nachrichten- und Bildformat, Denkstufe, Stoppwörter.

Die Anbieter selbst stehen in ``ki_claude``, ``ki_ollama`` und ``ki_eigen``. Kein Import von ``ki`` (keine Kreise).
"""
from __future__ import annotations

import base64
import json
import re
import urllib.request

from lunivo_writer.ai import modellfaehigkeit as MF


def json_dict(r) -> dict:
    """Antwort eines Anbieters als Wörterbuch. Alles andere (kein JSON, keine Zeichenfolge, Liste statt Objekt) ist ein ValueError und wird als
    Fehler gemeldet statt das Programm zu stören."""
    daten = json.loads(r.read().decode("utf-8"))
    if not isinstance(daten, dict):
        raise ValueError("Antwort ist kein JSON-Objekt")
    return daten


def post(url: str, kopf: dict, body: dict, timeout: float):
    """Sendet über ``ki._post`` (so bleibt der Transport für Tests und Anbindungen austauschbar)."""
    from lunivo_writer.ai import ki
    return ki._post(url, kopf, body, timeout)


def post_roh(url: str, kopf: dict, body: dict, timeout: float):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"content-type": "application/json", **kopf}, method="POST")
    return urllib.request.urlopen(req, timeout=timeout)


def bearer_kopf(schluessel: str) -> dict:
    """Kopfzeile für OpenAI-kompatible Anbieter (leer, wenn kein Schlüssel eingetragen ist)."""
    return {"authorization": "Bearer " + schluessel} if schluessel else {}


def stufe(optionen) -> dict:
    return MF.DENKSTUFEN[MF.denkstufe((optionen or {}).get("denktiefe"))]


def stopp_liste(optionen) -> list[str]:
    return [t.strip() for t in str((optionen or {}).get("stopp", "")).split(",") if t.strip()]


def erste_nachricht(daten: dict) -> dict:
    """``choices[0].message`` einer OpenAI-kompatiblen Antwort, sonst ein leeres Wörterbuch."""
    wahl = daten.get("choices")
    erste = wahl[0] if isinstance(wahl, list) and wahl else None
    nachricht = erste.get("message") if isinstance(erste, dict) else None
    return nachricht if isinstance(nachricht, dict) else {}


def json_nach_marken(roh: str):
    """JSON aus einer Modellantwort, auch wenn sie in ```-Marken steht."""
    return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", roh.strip()))


def ohne_gruebeln(roh: str) -> str:
    ohne = re.sub(r"<think>[\s\S]*?</think>", "", str(roh), flags=re.I)
    return ohne[ohne.rfind("</think>") + 8:] if "</think>" in ohne else ohne


# ---------------------------------------------------------------- Nachrichten und Bilder
def bild_block(b: dict, anbieter: str):
    """Ein Bildanhang im Format des Anbieters: „claude“, „ollama“ oder „openai“ (eigene Anbieter). ``b["b64"]`` ist beim Senden schon gelesen."""
    if anbieter == "claude":
        return {"type": "image", "source": {"type": "base64", "media_type": b["typ"], "data": b["b64"]}}
    return {"type": "image_url", "image_url": {"url": f"data:{b['typ']};base64,{b['b64']}"}}


def _bild_inhalt(text: str, bilder: list[dict], anbieter: str) -> dict:
    if anbieter == "ollama":
        return {"content": text, "images": [b["b64"] for b in bilder]}
    bloecke = [bild_block(b, anbieter) for b in bilder]
    wort = [{"type": "text", "text": text}] if text else []
    return {"content": bloecke + wort if anbieter == "claude" else wort + bloecke}      # Claude: Bild vor dem Text


def nachricht(z: dict, anbieter: str, letzte: bool) -> dict:
    rolle = "assistant" if z.get("rolle") == "ki" else "user"
    text, bilder = z["text"], z.get("bilder") or []
    if not bilder:
        return {"role": rolle, "content": text}
    if not letzte:                                   # frühere Bilder werden nicht erneut gesendet
        return {"role": rolle, "content": (text + "\n" if text else "") + "[Bild]"}
    return {"role": rolle, **_bild_inhalt(text, [b for b in bilder if b.get("b64")], anbieter)}


def nachrichten(text, anbieter: str = "claude") -> list[dict]:
    if isinstance(text, list):
        return [nachricht(z, anbieter, i == len(text) - 1) for i, z in enumerate(text)]
    return [{"role": "user", "content": text}]


def bilder_lesen(verlauf: list[dict]) -> tuple[list[dict], str | None]:
    """Liest und kodiert (Base64) nur die Bilder der LETZTEN Nachricht, erst beim Senden. Liefert (Kopie des Verlaufs, Fehlertext)."""
    ergebnis = [dict(z) for z in verlauf]
    if not ergebnis or not ergebnis[-1].get("bilder"):
        return ergebnis, None
    neu = []
    for b in ergebnis[-1]["bilder"]:
        p = MF.bild_pruefen(b.get("pfad"))
        if "fehler" in p:
            return ergebnis, p["fehler"]
        with open(p["pfad"], "rb") as fh:
            neu.append({**p, "b64": base64.b64encode(fh.read()).decode("ascii")})
    ergebnis[-1]["bilder"] = neu
    return ergebnis, None
