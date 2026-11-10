"""Claude (Anthropic-API): Anfrage bauen, senden, Antwort und Fehler lesen. Die Adresse kommt vom Aufrufer (``ki.CLAUDE_URL``)."""
from __future__ import annotations

import json
import re
import urllib.error

from lunivo_writer.ai import ki_transport as T
from lunivo_writer.ai import modellfaehigkeit as MF
from lunivo_writer.ai.ki_konfiguration import PREISE

FEHLER_HTTP = {401: "Der Schlüssel wird abgelehnt. Er wird bei der Erstellung nur einmal angezeigt — "
                    "vollständig kopiert? Sonst auf console.anthropic.com einen neuen anlegen.",
               400: "Die Anfrage wurde abgelehnt.",
               429: "Zu viele Anfragen. Bitte kurz warten und noch einmal versuchen."}


def cent_fuer(modell: str, verbrauch: dict | None):
    if not verbrauch:
        return None
    name = next((k for k in PREISE if str(modell or "").startswith(k)), None)
    if not name:
        return None
    hin = (verbrauch.get("input_tokens", 0) + verbrauch.get("cache_read_input_tokens", 0)
           + verbrauch.get("cache_creation_input_tokens", 0))
    her = verbrauch.get("output_tokens", 0)
    p = PREISE[name]
    return (hin * p[0] + her * p[1]) / 1e6 * 100


def _ausgabe_einstellungen(modell: str, bauplan, optionen) -> dict:
    ausgabe = {}
    effort = T.stufe(optionen)["claude"]              # „aus“ = kein thinking; „auto“ = bisher (low, adaptiv); Haiku denkt nicht
    if effort and MF.claude_faehig(modell)[0]:
        ausgabe["effort"] = effort
    if bauplan:
        ausgabe["format"] = {"type": "json_schema", "schema": bauplan}
    return ausgabe


def bitte_bauen(anweisung, text, bauplan, modell, optionen=None) -> dict:
    bitte = {"model": modell, "max_tokens": int((optionen or {}).get("maxLaenge") or 16000), "system": anweisung,
             "messages": T.nachrichten(text, "claude")}
    stopp = T.stopp_liste(optionen)
    if stopp:
        bitte["stop_sequences"] = stopp                  # Temperatur und Top P gelten hier nicht (Claude regelt das selbst)
    ausgabe = _ausgabe_einstellungen(modell, bauplan, optionen)
    if "effort" in ausgabe:
        bitte["thinking"] = {"type": "adaptive"}
    if ausgabe:
        bitte["output_config"] = ausgabe
    return bitte


def _meldung(e: urllib.error.HTTPError) -> str:
    try:
        return json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
    except (ValueError, OSError):
        return ""


def fehler_http(e: urllib.error.HTTPError) -> dict:
    zusatz = _meldung(e)
    if re.search(r"credit balance", zusatz, re.I):
        return {"fehler": "Das Guthaben ist aufgebraucht. Bitte bei Anthropic aufladen."}
    return {"fehler": FEHLER_HTTP.get(e.code, f"Fehler {e.code}") + (f" ({zusatz})" if zusatz else "")}


def antwort_lesen(daten: dict, modell: str) -> dict:
    if daten.get("stop_reason") == "refusal":
        return {"fehler": "Die KI wollte diesen Text nicht bearbeiten."}
    bloecke = daten.get("content") if isinstance(daten.get("content"), list) else []
    erg = "".join(b["text"] for b in bloecke if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)).strip()
    if not erg:
        return {"fehler": "Es kam keine Antwort zurück."}
    return {"ergebnis": erg, "cent": cent_fuer(daten.get("model") or modell, daten.get("usage"))}


def anfrage(url: str, schluessel: str, anweisung, text, bauplan, modell, optionen=None) -> dict:
    if not schluessel:
        return {"fehler": "Es ist kein Schlüssel gespeichert. Optionen ▸ Schreibhilfe und KI."}
    bitte = bitte_bauen(anweisung, text, bauplan, modell, optionen)
    try:
        with T.post(url, {"x-api-key": schluessel, "anthropic-version": "2023-06-01"}, bitte, 90) as r:
            daten = T.json_dict(r)
    except urllib.error.HTTPError as e:
        return fehler_http(e)
    except TimeoutError:
        return {"fehler": "Die KI hat zu lange gebraucht. Bitte noch einmal versuchen."}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"fehler": f"Es hat nicht geklappt: {getattr(e, 'reason', e)}"}
    return antwort_lesen(daten, modell)
