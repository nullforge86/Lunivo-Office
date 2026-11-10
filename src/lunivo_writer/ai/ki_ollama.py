"""Ollama (läuft auf diesem Rechner): Tempo-Einstellungen, Anfrage bauen, senden, Antwort und Strom (NDJSON) lesen.
Die Adresse kommt vom Aufrufer (``ki.OLLAMA_URL``)."""
from __future__ import annotations

import json
import os
import time
import urllib.error

from lunivo_writer.ai import ki_transport as T
from lunivo_writer.ai.ki_konfiguration import CHAT_VORGABE

# ---- Tempo: Modell im Speicher halten, Kontext und Antwortlänge dem Auftrag anpassen
KEEP_ALIVE_MIN, KEEP_ALIVE_MAX = 0, 240            # Minuten; 0 = sofort entladen
NUM_CTX_STUFEN = (2048, 4096, 8192, 16384, 32768)  # erlaubte Kontextgrößen (Tokens)
NUM_PREDICT_CHAT, NUM_PREDICT_MIN, NUM_PREDICT_MAX = 1024, 512, 2048
ZEICHEN_JE_TOKEN = 3                               # grobe Schätzung für deutschen Text (eher zu viel als zu wenig)
STROM_TAKT = 0.05                                  # höchstens ~20 Aktualisierungen je Sekunde

FEHLER_ZEIT = "Der eigene Rechner hat zu lange gebraucht. Ein kleineres Modell geht schneller."


def _leer() -> dict:
    return {"fehler": "Es kam keine Antwort zurück."}


def keep_alive_begrenzen(wert) -> int:
    try:
        return max(KEEP_ALIVE_MIN, min(KEEP_ALIVE_MAX, int(wert)))
    except (TypeError, ValueError):
        return CHAT_VORGABE["keepAlive"]


def num_thread_begrenzen(wert) -> int:
    """0 = automatisch; sonst 1 bis zur Zahl der logischen Kerne dieses Rechners."""
    try:
        w = int(wert)
    except (TypeError, ValueError):
        return 0
    return 0 if w <= 0 else min(w, os.cpu_count() or w)


def num_ctx_begrenzen(wert) -> int:
    try:
        w = int(wert)
    except (TypeError, ValueError):
        return CHAT_VORGABE["numCtx"]
    return min(NUM_CTX_STUFEN, key=lambda x: abs(x - w))


def num_predict_fuer(eingang_zeichen: int, chat: bool, denkt: bool, gesetzt: int = 0) -> int:
    """Antwortgrenze: ausdrücklich gesetzt (Chat-Einstellung) gilt immer; sonst Chat 1024, Überarbeitung nach Länge des Eingangs
    (512–2048). Denkende Modelle bekommen Reserve, damit das Nachdenken die Antwort nicht abschneidet."""
    if gesetzt:
        return int(gesetzt)
    n = NUM_PREDICT_CHAT if chat else max(NUM_PREDICT_MIN, min(NUM_PREDICT_MAX, eingang_zeichen // ZEICHEN_JE_TOKEN + 256))
    return n + (1024 if denkt else 0)


def num_ctx_fuer(eingestellt: int, zeichen: int, vorhersage: int) -> int:
    """Eingestellte Größe, aber nie kleiner als Gespräch plus Antwort brauchen — der Verlauf wird nie abgeschnitten."""
    noetig = zeichen // ZEICHEN_JE_TOKEN + vorhersage + 64
    return next((x for x in NUM_CTX_STUFEN if x >= max(eingestellt, noetig)), NUM_CTX_STUFEN[-1])


# ---------------------------------------------------------------- Anfrage
def _optionen_bauen(o: dict, einst: dict, zeichen: int, denkt: bool) -> dict:
    opt = {"temperature": float(o.get("temperatur", 0.2))}
    if o.get("topP") is not None:
        opt["top_p"] = float(o["topP"])
    opt["num_predict"] = num_predict_fuer(zeichen, "denktiefe" in o, denkt, o.get("maxLaenge") or 0)
    opt["num_ctx"] = num_ctx_fuer(num_ctx_begrenzen(einst["numCtx"]), zeichen, opt["num_predict"])
    threads = num_thread_begrenzen(einst.get("numThread"))
    if threads:
        opt["num_thread"] = threads
    stopp = T.stopp_liste(o)
    if stopp:
        opt["stop"] = stopp
    return opt


def bitte_bauen(modell: str, anweisung, text, bauplan, o: dict, einst: dict, strom) -> dict:
    nachrichten = [{"role": "system", "content": anweisung}] + T.nachrichten(text, "ollama")
    zeichen = sum(len(str(n.get("content", ""))) for n in nachrichten)
    denken = T.stufe(o)["ollama"]
    bitte = {"model": modell, "stream": bool(strom), "options": _optionen_bauen(o, einst, zeichen, denken not in (None, False)),
             "think": denken, "keep_alive": f"{keep_alive_begrenzen(einst['keepAlive'])}m", "messages": nachrichten}
    if bauplan:
        bitte["format"] = bauplan
    return bitte


def _http_fehler(e: urllib.error.HTTPError, bitte: dict, modell: str):
    """Fehlertext als Wörterbuch; None = „think“ wurde entfernt, noch einmal senden."""
    try:
        grund = e.read().decode("utf-8", "replace")
    except OSError:
        grund = ""
    if e.code == 400 and "think" in grund.lower() and "think" in bitte:
        del bitte["think"]
        return None
    if e.code == 404:
        return {"fehler": f"Das Modell „{modell}“ liegt nicht auf diesem Rechner. Im Terminal holen: ollama pull {modell}"}
    return {"fehler": f"Ollama meldet Fehler {e.code}" + (f" ({grund[:200]})" if grund else "")}


def antwort_lesen(daten: dict) -> dict:
    nachricht = daten.get("message") if isinstance(daten.get("message"), dict) else {}
    erg = T.ohne_gruebeln(nachricht.get("content") if isinstance(nachricht.get("content"), str) else "").strip()
    if not erg:
        return _leer()
    return {"ergebnis": erg, "abgeschnitten": daten.get("done_reason") == "length"}


def _senden(url: str, bitte: dict, strom, abbruch, modell: str) -> dict:
    for _versuch in (1, 2):
        try:
            with T.post(url + "/api/chat", {}, bitte, 600) as r:
                return strom_lesen(r, strom, abbruch) if strom else antwort_lesen(T.json_dict(r))
        except urllib.error.HTTPError as e:
            fehler = _http_fehler(e, bitte, modell)
            if fehler is not None:
                return fehler
        except TimeoutError:
            return {"fehler": FEHLER_ZEIT}
        except (urllib.error.URLError, OSError, ValueError):
            return {"fehler": f"Ollama ist unter {url} nicht zu erreichen. Läuft der Dienst?"}
    return _leer()


def anfrage(url: str, einst: dict, anweisung, text, bauplan, modell, optionen=None) -> dict:
    """``einst``: Chat-Einstellungen (keepAlive/numCtx/numThread/streaming gelten für alle Ollama-Aufgaben)."""
    if not modell:
        return {"fehler": "Es ist noch kein Modell gewählt. In den Optionen nachholen."}
    o = optionen or {}
    strom = o.get("_strom") if einst.get("streaming", True) else None
    bitte = bitte_bauen(modell, anweisung, text, bauplan, o, einst, strom)
    return _senden(url, bitte, strom, o.get("_abbruch"), modell)


# ---------------------------------------------------------------- Strom
def _abgebrochen(abbruch) -> bool:
    return abbruch is not None and abbruch.is_set()


def _json_teil(zeile):
    """Eine Zeile des Stroms als Wörterbuch; leere, kaputte und fremde Zeilen sind None."""
    zeile = zeile.strip()
    if not zeile:
        return None
    try:
        teil = json.loads(zeile)
    except ValueError:
        return None
    return teil if isinstance(teil, dict) else None


class _Strom:
    """Sammelt den Text des Stroms; ``strom(text)`` bekommt den bisherigen Text (ohne Grübeln), gedrosselt."""

    def __init__(self, strom):
        self.strom, self.roh, self.grund, self.letzt, self.fertig = strom, "", "", 0.0, False

    def zeile(self, zeile):
        """Fehler als Wörterbuch, sonst None."""
        teil = _json_teil(zeile)
        if teil is None:
            return None
        if isinstance(teil.get("error"), str):
            return {"fehler": f"Ollama meldet: {teil['error'][:200]}"}
        self._inhalt(teil)
        if teil.get("done"):
            self.grund, self.fertig = str(teil.get("done_reason") or ""), True
        return None

    def _inhalt(self, teil: dict) -> None:
        m = teil.get("message") if isinstance(teil.get("message"), dict) else {}
        if not isinstance(m.get("content"), str):
            return
        self.roh += m["content"]
        jetzt = time.monotonic()
        if jetzt - self.letzt < STROM_TAKT:
            return
        self.letzt = jetzt
        sichtbar = T.ohne_gruebeln(self.roh)
        if "<think>" not in sichtbar.lower():
            self.strom(sichtbar)

    def ergebnis(self) -> dict:
        erg = T.ohne_gruebeln(self.roh).strip()
        if not erg:
            return _leer()
        self.strom(erg)                                              # der Schlussstand kommt immer an (die Drosselung kann ihn verschluckt haben)
        return {"ergebnis": erg, "abgeschnitten": self.grund == "length"}


def strom_lesen(r, strom, abbruch) -> dict:
    """Liest die Antwortzeilen (NDJSON) von Ollama; ``abbruch`` (threading.Event) beendet die Verbindung sofort."""
    s = _Strom(strom)
    try:
        for zeile in r:
            if _abgebrochen(abbruch):
                return {"fehler": "Abgebrochen."}
            fehler = s.zeile(zeile)
            if fehler is not None:
                return fehler
            if s.fertig:
                break
    except TimeoutError:
        return {"fehler": FEHLER_ZEIT}
    except (OSError, ValueError):
        if s.roh.strip() and not _abgebrochen(abbruch):
            return {"fehler": "Die Verbindung zu Ollama brach mitten in der Antwort ab."}
        return {"fehler": "Ollama ist nicht mehr zu erreichen. Läuft der Dienst?"}
    return s.ergebnis()
