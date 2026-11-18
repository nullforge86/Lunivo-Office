"""Eigener Anbieter (OpenAI-kompatible Schnittstelle): Anfrage bauen, senden, Antwort lesen."""
from __future__ import annotations

import urllib.error

from lunivo_writer.ki import ki_transport as T


def _optionen_uebernehmen(bitte: dict, o: dict) -> None:
    if o.get("temperatur") is not None:
        bitte["temperature"] = float(o["temperatur"])
    if o.get("topP") is not None:
        bitte["top_p"] = float(o["topP"])
    if o.get("maxLaenge"):
        bitte["max_tokens"] = int(o["maxLaenge"])
    stopp = T.stopp_liste(o)
    if stopp:
        bitte["stop"] = stopp


def bitte_bauen(a: dict, anweisung, text, bauplan, optionen=None) -> dict:
    bitte = {"model": a["modell"], "messages": [{"role": "system", "content": anweisung}] + T.nachrichten(text, "openai")}
    effort = T.stufe(optionen)["openai"]
    if effort is not None:
        bitte["reasoning_effort"] = effort       # nur bei ausdrücklicher Wahl
    _optionen_uebernehmen(bitte, optionen or {})
    if bauplan:
        bitte["response_format"] = {"type": "json_schema", "json_schema": {"name": "antwort", "schema": bauplan, "strict": True}}
    return bitte


def antwort_lesen(daten: dict) -> dict:
    erg = T.erste_nachricht(daten).get("content")
    return {"ergebnis": erg} if isinstance(erg, str) and erg else {"fehler": "Es kam keine Antwort zurück."}


def _senden(a: dict, bitte: dict) -> dict:
    kopf = T.bearer_kopf(a["schluessel"])
    for _versuch in (1, 2):
        try:
            with T.post(a["url"] + "/chat/completions", kopf, bitte, 90) as r:
                return antwort_lesen(T.json_dict(r))
        except urllib.error.HTTPError as e:
            if e.code != 400 or "reasoning_effort" not in bitte:
                return {"fehler": f"„{a['name']}“ meldet Fehler {e.code}"}
            del bitte["reasoning_effort"]                      # das Modell kennt keine Denktiefe: ohne sie noch einmal
        except TimeoutError:
            return {"fehler": f"„{a['name']}“ hat zu lange gebraucht. Bitte noch einmal versuchen."}
        except (urllib.error.URLError, OSError, ValueError):
            return {"fehler": f"„{a['name']}“ ist unter {a['url']} nicht zu erreichen. Stimmt die URL?"}
    return {"fehler": "Es kam keine Antwort zurück."}


def anfrage(a, anweisung, text, bauplan, optionen=None) -> dict:
    if not a:
        return {"fehler": "Der gewählte Anbieter ist nicht mehr da. In den Optionen neu wählen oder anlegen."}
    if not a["modell"]:
        return {"fehler": f"Für „{a['name']}“ ist kein Modell eingetragen."}
    return _senden(a, bitte_bauen(a, anweisung, text, bauplan, optionen))
