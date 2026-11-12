"""Bild aus Text: nur eigene Anbieter mit „Bilder“, OpenAI-Schnittstelle POST <URL>/images/generations."""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from lunivo_writer.ki import ki_transport as T
from lunivo_writer.ki.ki_konfiguration import EIGEN_MARKE


def anbieter_pruefen(konfig, modell: str):
    """(Anbieter, None) oder (None, Fehler)."""
    if not modell.startswith(EIGEN_MARKE):
        return None, {"fehler": "Dafür fehlt ein Anbieter mit „Bilder“ — in der KI-Konfiguration eintragen."}
    a = konfig.anbieter_holen(modell[len(EIGEN_MARKE):])
    if not a:
        return None, {"fehler": "Der gewählte Anbieter ist nicht mehr da. In der KI-Konfiguration neu wählen."}
    if not a["modell"]:
        return None, {"fehler": f"Für „{a['name']}“ ist kein Modell eingetragen."}
    return a, None


def _bild_aus(a: dict, daten: dict) -> dict:
    liste = daten.get("data") if isinstance(daten.get("data"), list) and daten.get("data") else [{}]
    e = liste[0] if isinstance(liste[0], dict) else {}
    if e.get("b64_json"):
        return {"bild": base64.b64decode(e["b64_json"])}
    if not e.get("url"):
        return {"fehler": f"„{a['name']}“ hat kein Bild zurückgegeben."}
    if urllib.parse.urlparse(str(e["url"])).scheme not in ("http", "https"):
        return {"fehler": f"„{a['name']}“ hat eine unzulässige Bildadresse geschickt."}      # kein file:// o. Ä. aus fremder Antwort
    with urllib.request.urlopen(e["url"], timeout=90) as r:
        return {"bild": r.read()}


def _http_fehler(a: dict, e: urllib.error.HTTPError) -> dict:
    try:
        zusatz = (json.loads(e.read().decode("utf-8")).get("error") or {}).get("message", "")
    except (OSError, ValueError, AttributeError):
        zusatz = ""
    return {"fehler": f"„{a['name']}“ meldet Fehler {e.code}" + (f" ({zusatz})" if zusatz else "")}


def erzeugen(a: dict, beschreibung: str) -> dict:
    try:
        with T.post(a["url"] + "/images/generations", T.bearer_kopf(a["schluessel"]),
                    {"model": a["modell"], "prompt": beschreibung, "n": 1, "size": "1024x1024"}, 90) as r:
            daten = T.json_dict(r)
        return _bild_aus(a, daten)
    except urllib.error.HTTPError as e:
        return _http_fehler(a, e)
    except TimeoutError:
        return {"fehler": f"„{a['name']}“ hat zu lange gebraucht. Bitte noch einmal versuchen."}
    except (urllib.error.URLError, OSError, ValueError):
        return {"fehler": f"„{a['name']}“ ist unter {a['url']} nicht zu erreichen. Stimmt die URL?"}
