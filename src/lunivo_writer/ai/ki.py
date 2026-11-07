"""Die KI-Ebene: Korrigieren, Vorschläge, Übersetzen, Zusammenfassen, Text bearbeiten, Chat.

Freiwillig und nach außen nur auf ausdrücklichen Knopfdruck:
  · Ollama — läuft auf diesem Rechner (127.0.0.1:11434), der Text verlässt das Gerät nicht.
  · Claude — Anthropic-API, nur mit eigenem Schlüssel und nur nach Ihrer Zustimmung (siehe KIKonfig.claude_erlaubt).
  · Eigener Anbieter — OpenAI-kompatible Schnittstelle unter einer von Ihnen eingetragenen Adresse.
Schlüssel stehen nie im Quelltext, sondern in einer Datei mit Zugriff nur für den Benutzer (0600).
"""
from __future__ import annotations

import base64
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from lunivo_writer.ai import modellfaehigkeit as MF

from lunivo_writer.ai.ki_konfiguration import (
    OLLAMA_URL, CLAUDE_URL, OLLAMA_MARKE, EIGEN_MARKE, ARGOS_MARKE, AUTO_MARKE,
    LERN_SCHWELLE, UMFAENGE, EMPFAENGER, SPRACHEN, MODELLE_FEST,
    PREISE, TEXT_AKTIONEN, VORLAGE_ANWEISUNG, ANBIETER_TAGS,
    CHAT_VORGABE, AUFGABEN, ANBIETER_VORLAGEN, ASSISTENT_ARTEN, AKTIONS_MODI,
    FORTLAUFEND_MODI, ASSISTENT_AUSLOESER, ASSISTENT_UMFAENGE,
    KOMMENTAR_ZUSATZ, KOMMENTAR_NUR, VORLAGEN_ASSISTENT, VORSCHLAG_BAUPLAN,
    assistent_normiert, KIKonfig, ist_lokale_url,
)



def _json_dict(r) -> dict:
    """Antwort eines Anbieters als Wörterbuch. Alles andere (kein JSON, keine Zeichenfolge, Liste statt Objekt) ist ein ValueError und wird als
    Fehler gemeldet statt das Programm zu stören."""
    daten = json.loads(r.read().decode("utf-8"))
    if not isinstance(daten, dict):
        raise ValueError("Antwort ist kein JSON-Objekt")
    return daten




# Anweisungen bleiben unter dem bisherigen Importpfad verfügbar.
from lunivo_writer.ai.ki_anweisungen import (
    _NUR_ZEILEN, _zettel, steckbrief, anweisung_korrektur, anweisung_uebersetzung,
    anweisung_vorschlaege, ANWEISUNG_ZUSAMMENFASSUNG, ANWEISUNG_ANALYSE,
    anweisung_text_aktion,
)


# ---------------------------------------------------------------- Anfragen
def _bild_block(b: dict, anbieter: str):
    """Ein Bildanhang im Format des Anbieters: „claude“, „ollama“ oder „openai“ (eigene Anbieter). ``b["b64"]`` ist beim Senden schon gelesen."""
    if anbieter == "claude":
        return {"type": "image", "source": {"type": "base64", "media_type": b["typ"], "data": b["b64"]}}
    return {"type": "image_url", "image_url": {"url": f"data:{b['typ']};base64,{b['b64']}"}}


def _nachricht(z: dict, anbieter: str, letzte: bool) -> dict:
    rolle = "assistant" if z.get("rolle") == "ki" else "user"
    text, bilder = z["text"], z.get("bilder") or []
    if not bilder:
        return {"role": rolle, "content": text}
    if not letzte:                                   # frühere Bilder werden nicht erneut gesendet
        return {"role": rolle, "content": (text + "\n" if text else "") + "[Bild]"}
    bilder = [b for b in bilder if b.get("b64")]
    if anbieter == "ollama":
        return {"role": rolle, "content": text, "images": [b["b64"] for b in bilder]}
    bloecke = [_bild_block(b, anbieter) for b in bilder]
    wort = [{"type": "text", "text": text}] if text else []
    return {"role": rolle, "content": bloecke + wort if anbieter == "claude" else wort + bloecke}      # Claude: Bild vor dem Text


def _nachrichten(text, anbieter: str = "claude") -> list[dict]:
    if isinstance(text, list):
        return [_nachricht(z, anbieter, i == len(text) - 1) for i, z in enumerate(text)]
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


def ohne_gruebeln(roh: str) -> str:
    ohne = re.sub(r"<think>[\s\S]*?</think>", "", str(roh), flags=re.I)
    return ohne[ohne.rfind("</think>") + 8:] if "</think>" in ohne else ohne


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


def als_geld(cent) -> str:
    if cent is None:
        return ""
    return "unter 1 Cent" if cent < 1 else f"{cent / 100:.2f} $".replace(".", ",")


# ---- Ollama-Tempo: Modell im Speicher halten, Kontext und Antwortlänge dem Auftrag anpassen
KEEP_ALIVE_MIN, KEEP_ALIVE_MAX = 0, 240            # Minuten; 0 = sofort entladen
NUM_CTX_STUFEN = (2048, 4096, 8192, 16384, 32768)  # erlaubte Kontextgrößen (Tokens)
NUM_PREDICT_CHAT, NUM_PREDICT_MIN, NUM_PREDICT_MAX = 1024, 512, 2048
ZEICHEN_JE_TOKEN = 3                               # grobe Schätzung für deutschen Text (eher zu viel als zu wenig)


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


def _post(url: str, kopf: dict, body: dict, timeout: float):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"content-type": "application/json", **kopf}, method="POST")
    return urllib.request.urlopen(req, timeout=timeout)


class KI:
    def __init__(self, konfig: KIKonfig, gelernt: dict | None = None):
        self.k = konfig
        self.gelernt = gelernt if gelernt is not None else {"woerter": {}, "inRuhe": {}}

    def modell(self, aufgabe: str | None = None) -> str:
        return (self.k["aufgaben"].get(aufgabe) if aufgabe else None) or self.k["modell"]

    def verfuegbar(self) -> bool:
        m = self.k["modell"]
        if m.startswith(EIGEN_MARKE):
            return self.k.anbieter_holen(m[len(EIGEN_MARKE):]) is not None
        return m.startswith(OLLAMA_MARKE) or bool(self.k["apiKey"])

    def verfuegbar_fuer(self, aufgabe: str | None = None) -> bool:
        """Wie ``verfuegbar``, aber für das Modell der Aufgabe: argos: und auto: gehen auch ohne Standardmodell (lokal)."""
        m = self.modell(aufgabe)
        return True if m.startswith((ARGOS_MARKE, AUTO_MARKE)) else self.verfuegbar()

    def schickt_nach_aussen(self, modell: str | None = None) -> str | None:
        """Name des Empfängers, wenn der Text das Gerät verlässt — sonst None."""
        m = modell or self.k["modell"]
        if m.startswith(ARGOS_MARKE):
            return None
        if m.startswith(AUTO_MARKE):
            return self.schickt_nach_aussen(self.k["modell"]) if self.verfuegbar() else None
        if m.startswith(OLLAMA_MARKE):
            return None
        if m.startswith(EIGEN_MARKE):
            a = self.k.anbieter_holen(m[len(EIGEN_MARKE):])
            return None if (a and ist_lokale_url(a["url"])) else (a["name"] if a else "einen eigenen Anbieter")
        return "Anthropic (Claude)"

    # ---- Fähigkeiten des Chat-Modells (denken, Bild) — nie die Oberfläche blockieren
    _faehig: dict = {}                       # Ollama-Modell -> (Zeitpunkt, {Fähigkeiten} | None bei Fehler)
    _faehig_laeuft: set = set()
    FAEHIG_NEU_NACH = 30.0                   # Sekunden, bis ein fehlgeschlagenes Abfragen wiederholt wird
    faehigkeit_bekannt = staticmethod(lambda: None)       # vom KI-Dienst ersetzt: wird (aus einem Faden) gerufen, wenn eine Abfrage fertig ist

    def _ollama_faehigkeiten(self, name: str, warten: bool) -> set | None:
        """Fähigkeiten laut Ollama (/api/show → capabilities), mit Zwischenspeicher. ``warten=False``: nur aus dem Speicher, sonst im
        Hintergrund holen (None = noch unbekannt)."""
        alt = KI._faehig.get(name)
        if alt and (alt[1] is not None or time.monotonic() - alt[0] < self.FAEHIG_NEU_NACH):
            return alt[1]
        if not warten:
            if name not in KI._faehig_laeuft:
                KI._faehig_laeuft.add(name)
                threading.Thread(target=self._ollama_faehigkeiten_holen, args=(name,), daemon=True).start()
            return None
        return self._ollama_faehigkeiten_holen(name)

    def _ollama_faehigkeiten_holen(self, name: str) -> set | None:
        try:
            with _post(OLLAMA_URL + "/api/show", {}, {"model": name}, 3) as r:
                f = _json_dict(r).get("capabilities")
            erg = {str(x) for x in f} if isinstance(f, list) else set()
        except (urllib.error.URLError, OSError, ValueError):
            erg = None                                              # unbekannt = nicht fähig
        KI._faehig[name] = (time.monotonic(), erg)
        KI._faehig_laeuft.discard(name)
        try:
            self.faehigkeit_bekannt()
        except Exception:                                           # die Rückmeldung an die Oberfläche darf die Abfrage nie stören
            pass
        return erg

    def faehigkeit(self, modell: str, warten: bool = True) -> tuple[bool, bool]:
        """(denken, bild) für die Modellkennung (claude-…, ollama:…, eigen:…). Mit ``warten=False`` nie blockierend."""
        m = modell or ""
        if m.startswith(OLLAMA_MARKE):
            f = self._ollama_faehigkeiten(m[len(OLLAMA_MARKE):], warten) or set()
            return ("thinking" in f, "vision" in f)
        if m.startswith(EIGEN_MARKE):
            a = self.k.anbieter_holen(m[len(EIGEN_MARKE):])
            return (a is not None, bool(a) and "visuell" in (a.get("verwendungFuer") or []))     # Denktiefe wird nur bei Wahl gesendet, mit Rückfall bei 400
        if m.startswith((ARGOS_MARKE, AUTO_MARKE)):
            return (False, False)
        return MF.claude_faehig(m)

    def kann_bild(self, modell: str | None = None) -> bool:
        """Für die Oberfläche: nie blockierend; während die Abfrage bei Ollama läuft (oder scheitert) False."""
        return self.faehigkeit(modell or self.modell("chatbot"), False)[1]

    def kann_denken(self, modell: str | None = None) -> bool:
        return self.faehigkeit(modell or self.modell("chatbot"), False)[0]

    def websuche_ziel(self) -> str | None:
        """Wohin die Frage der Websuche geht, wenn das nicht dieser Rechner ist (Brave oder eine nicht lokale Adresse), sonst None."""
        ws = self.k.websuche_optionen()
        if not ws["an"]:
            return None
        if ws.get("anbieter") == "brave":
            return "Websuche (Brave Search)"
        url = (ws.get("url") or "").strip()
        if not url or ist_lokale_url(url):
            return None
        return "Websuche (" + (urllib.parse.urlparse(url).hostname or url) + ")"

    def zustimmung_fehlt(self, modell: str | None = None, umfang: str = "auszug") -> dict | None:
        """Sperre an der Sendestelle: Geht der Text an einen Dienst außerhalb dieses Rechners und liegt dafür keine Einwilligung vor, kommt eine
        Fehlermeldung zurück (sonst None). Unabhängig von der Rückfrage in der Oberfläche — ohne Zustimmung wird nichts gesendet."""
        ziel = self.schickt_nach_aussen(modell)
        if ziel is None or self.k.hat_einwilligung(ziel, umfang):
            return None
        return {"fehler": f"Es liegt keine Zustimmung vor, Text an „{ziel}“ zu senden ({UMFAENGE[umfang]}). Nichts wurde gesendet."}

    def anfrage(self, anweisung: str, text, bauplan=None, modell: str | None = None, optionen: dict | None = None) -> dict:
        m = modell or self.k["modell"]
        if self.verfuegbar() and (sperre := self.zustimmung_fehlt(m)) is not None:      # fehlt schon der Schlüssel, nennt der Zweig unten den eigentlichen Grund
            return sperre
        if m.startswith(EIGEN_MARKE):
            return self._eigen(self.k.anbieter_holen(m[len(EIGEN_MARKE):]), anweisung, text, bauplan, optionen)
        if m.startswith(OLLAMA_MARKE):
            return self._ollama(anweisung, text, bauplan, m[len(OLLAMA_MARKE):], optionen)
        return self._claude(anweisung, text, bauplan, m, optionen)

    @staticmethod
    def _stufe(optionen) -> dict:
        return MF.DENKSTUFEN[MF.denkstufe((optionen or {}).get("denktiefe"))]

    @staticmethod
    def _stopp(optionen) -> list[str]:
        return [t.strip() for t in str((optionen or {}).get("stopp", "")).split(",") if t.strip()]

    def _claude(self, anweisung, text, bauplan, modell, optionen=None) -> dict:
        if not self.k["apiKey"]:
            return {"fehler": "Es ist kein Schlüssel gespeichert. Optionen ▸ Schreibhilfe und KI."}
        bitte = {"model": modell, "max_tokens": int((optionen or {}).get("maxLaenge") or 16000), "system": anweisung, "messages": _nachrichten(text, "claude")}
        if self._stopp(optionen):
            bitte["stop_sequences"] = self._stopp(optionen)                  # Temperatur und Top P gelten hier nicht (Claude regelt das selbst)
        ausgabe = {}
        effort = self._stufe(optionen)["claude"]              # „aus“ = kein thinking; „auto“ = bisher (low, adaptiv); Haiku denkt nicht
        if effort and MF.claude_faehig(modell)[0]:
            ausgabe["effort"] = effort
            bitte["thinking"] = {"type": "adaptive"}
        if bauplan:
            ausgabe["format"] = {"type": "json_schema", "schema": bauplan}
        if ausgabe:
            bitte["output_config"] = ausgabe
        try:
            with _post(CLAUDE_URL, {"x-api-key": self.k["apiKey"], "anthropic-version": "2023-06-01"}, bitte, 90) as r:
                daten = _json_dict(r)
        except urllib.error.HTTPError as e:
            zusatz = ""
            try:
                zusatz = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
            except (ValueError, OSError):
                pass
            if re.search(r"credit balance", zusatz, re.I):
                return {"fehler": "Das Guthaben ist aufgebraucht. Bitte bei Anthropic aufladen."}
            texte = {401: "Der Schlüssel wird abgelehnt. Er wird bei der Erstellung nur einmal angezeigt — "
                          "vollständig kopiert? Sonst auf console.anthropic.com einen neuen anlegen.",
                     400: "Die Anfrage wurde abgelehnt.", 429: "Zu viele Anfragen. Bitte kurz warten und noch "
                     "einmal versuchen."}
            return {"fehler": texte.get(e.code, f"Fehler {e.code}") + (f" ({zusatz})" if zusatz else "")}
        except TimeoutError:
            return {"fehler": "Die KI hat zu lange gebraucht. Bitte noch einmal versuchen."}
        except (urllib.error.URLError, OSError, ValueError) as e:
            return {"fehler": f"Es hat nicht geklappt: {getattr(e, 'reason', e)}"}
        if daten.get("stop_reason") == "refusal":
            return {"fehler": "Die KI wollte diesen Text nicht bearbeiten."}
        bloecke = daten.get("content") if isinstance(daten.get("content"), list) else []
        erg = "".join(b["text"] for b in bloecke if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)).strip()
        if not erg:
            return {"fehler": "Es kam keine Antwort zurück."}
        return {"ergebnis": erg, "cent": cent_fuer(daten.get("model") or modell, daten.get("usage"))}

    def _ollama(self, anweisung, text, bauplan, modell, optionen=None) -> dict:
        if not modell:
            return {"fehler": "Es ist noch kein Modell gewählt. In den Optionen nachholen."}
        o = optionen or {}
        einst = self.k.chat_optionen()                                   # keepAlive/numCtx/streaming gelten für alle Ollama-Aufgaben
        nachrichten = [{"role": "system", "content": anweisung}] + _nachrichten(text, "ollama")
        zeichen = sum(len(str(n.get("content", ""))) for n in nachrichten)
        denkt = self._stufe(o)["ollama"] not in (None, False)
        opt = {"temperature": float(o.get("temperatur", 0.2))}
        if o.get("topP") is not None:
            opt["top_p"] = float(o["topP"])
        opt["num_predict"] = num_predict_fuer(zeichen, "denktiefe" in o, denkt, o.get("maxLaenge") or 0)
        opt["num_ctx"] = num_ctx_fuer(num_ctx_begrenzen(einst["numCtx"]), zeichen, opt["num_predict"])
        if num_thread_begrenzen(einst.get("numThread")):
            opt["num_thread"] = num_thread_begrenzen(einst.get("numThread"))
        if self._stopp(o):
            opt["stop"] = self._stopp(o)
        strom = o.get("_strom") if einst.get("streaming", True) else None
        abbruch = o.get("_abbruch")
        bitte = {"model": modell, "stream": bool(strom), "options": opt, "think": self._stufe(o)["ollama"],
                 "keep_alive": f"{keep_alive_begrenzen(einst['keepAlive'])}m", "messages": nachrichten}
        if bauplan:
            bitte["format"] = bauplan
        for _versuch in (1, 2):
            try:
                with _post(OLLAMA_URL + "/api/chat", {}, bitte, 600) as r:
                    if strom:
                        return self._ollama_strom(r, strom, abbruch)
                    daten = _json_dict(r)
                break
            except urllib.error.HTTPError as e:
                grund = ""
                try:
                    grund = e.read().decode("utf-8", "replace")
                except OSError:
                    pass
                if e.code == 400 and "think" in grund.lower() and "think" in bitte:
                    del bitte["think"]
                    continue
                if e.code == 404:
                    return {"fehler": f"Das Modell „{modell}“ liegt nicht auf diesem Rechner. Im Terminal holen: "
                                      f"ollama pull {modell}"}
                return {"fehler": f"Ollama meldet Fehler {e.code}" + (f" ({grund[:200]})" if grund else "")}
            except TimeoutError:
                return {"fehler": "Der eigene Rechner hat zu lange gebraucht. Ein kleineres Modell geht schneller."}
            except (urllib.error.URLError, OSError, ValueError):
                return {"fehler": f"Ollama ist unter {OLLAMA_URL} nicht zu erreichen. Läuft der Dienst?"}
        nachricht = daten.get("message") if isinstance(daten.get("message"), dict) else {}
        erg = ohne_gruebeln(nachricht.get("content") if isinstance(nachricht.get("content"), str) else "").strip()
        if not erg:
            return {"fehler": "Es kam keine Antwort zurück."}
        return {"ergebnis": erg, "abgeschnitten": daten.get("done_reason") == "length"}

    @staticmethod
    def _ollama_strom(r, strom, abbruch) -> dict:
        """Liest die Antwortzeilen (NDJSON) von Ollama; ``strom(text)`` bekommt den bisherigen Text (ohne Grübeln), ``abbruch`` (threading.Event)
        beendet die Verbindung sofort."""
        roh, grund, letzt = "", "", 0.0
        try:
            for zeile in r:
                if abbruch is not None and abbruch.is_set():
                    return {"fehler": "Abgebrochen."}
                zeile = zeile.strip()
                if not zeile:
                    continue
                try:
                    teil = json.loads(zeile)
                except ValueError:
                    continue
                if not isinstance(teil, dict):
                    continue
                if isinstance(teil.get("error"), str):
                    return {"fehler": f"Ollama meldet: {teil['error'][:200]}"}
                m = teil.get("message") if isinstance(teil.get("message"), dict) else {}
                if isinstance(m.get("content"), str):
                    roh += m["content"]
                    jetzt = time.monotonic()
                    if jetzt - letzt >= 0.05:                              # höchstens ~20 Aktualisierungen je Sekunde
                        letzt = jetzt
                        sichtbar = ohne_gruebeln(roh)
                        if "<think>" not in sichtbar.lower():
                            strom(sichtbar)
                if teil.get("done"):
                    grund = str(teil.get("done_reason") or "")
                    break
        except TimeoutError:
            return {"fehler": "Der eigene Rechner hat zu lange gebraucht. Ein kleineres Modell geht schneller."}
        except (OSError, ValueError):
            if roh.strip() and not (abbruch is not None and abbruch.is_set()):
                return {"fehler": "Die Verbindung zu Ollama brach mitten in der Antwort ab."}
            return {"fehler": "Ollama ist nicht mehr zu erreichen. Läuft der Dienst?"}
        erg = ohne_gruebeln(roh).strip()
        if erg:
            strom(erg)                                                    # der Schlussstand kommt immer an (die Drosselung kann ihn verschluckt haben)
        return {"ergebnis": erg, "abgeschnitten": grund == "length"} if erg else {"fehler": "Es kam keine Antwort zurück."}

    def _eigen(self, a, anweisung, text, bauplan, optionen=None) -> dict:
        if not a:
            return {"fehler": "Der gewählte Anbieter ist nicht mehr da. In den Optionen neu wählen oder anlegen."}
        if not a["modell"]:
            return {"fehler": f"Für „{a['name']}“ ist kein Modell eingetragen."}
        bitte = {"model": a["modell"], "messages": [{"role": "system", "content": anweisung}] + _nachrichten(text, "openai")}
        if self._stufe(optionen)["openai"] is not None:
            bitte["reasoning_effort"] = self._stufe(optionen)["openai"]       # nur bei ausdrücklicher Wahl
        if optionen:
            if optionen.get("temperatur") is not None:
                bitte["temperature"] = float(optionen["temperatur"])
            if optionen.get("topP") is not None:
                bitte["top_p"] = float(optionen["topP"])
            if optionen.get("maxLaenge"):
                bitte["max_tokens"] = int(optionen["maxLaenge"])
            if self._stopp(optionen):
                bitte["stop"] = self._stopp(optionen)
        if bauplan:
            bitte["response_format"] = {"type": "json_schema", "json_schema": {"name": "antwort", "schema": bauplan,
                                                                              "strict": True}}
        kopf = {"authorization": "Bearer " + a["schluessel"]} if a["schluessel"] else {}
        for _versuch in (1, 2):
            try:
                with _post(a["url"] + "/chat/completions", kopf, bitte, 90) as r:
                    daten = _json_dict(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 400 and "reasoning_effort" in bitte:
                    del bitte["reasoning_effort"]                      # das Modell kennt keine Denktiefe: ohne sie noch einmal
                    continue
                return {"fehler": f"„{a['name']}“ meldet Fehler {e.code}"}
            except TimeoutError:
                return {"fehler": f"„{a['name']}“ hat zu lange gebraucht. Bitte noch einmal versuchen."}
            except (urllib.error.URLError, OSError, ValueError):
                return {"fehler": f"„{a['name']}“ ist unter {a['url']} nicht zu erreichen. Stimmt die URL?"}
        wahl = daten.get("choices") if isinstance(daten.get("choices"), list) and daten.get("choices") else [{}]
        nachricht = wahl[0].get("message") if isinstance(wahl[0], dict) and isinstance(wahl[0].get("message"), dict) else {}
        erg = nachricht.get("content") if isinstance(nachricht.get("content"), str) else None
        return {"ergebnis": erg} if erg else {"fehler": "Es kam keine Antwort zurück."}

    # ---- die Anwendungen
    def _text(self, anweisung, text, aufgabe=None, optionen: dict | None = None) -> dict:
        r = self.anfrage(anweisung, text, None, self.modell(aufgabe), optionen)
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        return {"text": r["ergebnis"], "cent": r.get("cent"), **({"abgeschnitten": True} if r.get("abgeschnitten") else {})}

    def _kosten(self, cent) -> None:
        if cent:
            self.k.setze("kosten", self.k["kosten"] + cent)

    def korrigieren(self, text): return self._text(anweisung_korrektur(self.k, self.gelernt), text)
    def uebersetzen(self, text, sprache) -> dict:
        """Je nach Modell der Aufgabe: Argos (lokal), KI oder Automatisch (KI wenn eingeschaltet, erlaubt und erreichbar, sonst lokal;
        schlägt die KI fehl, einmal lokal). Im Ergebnis steht ``methode`` („KI“ oder „Lokal“)."""
        from lunivo_writer.ai import argos
        m = self.modell("uebersetzung")
        if m.startswith(ARGOS_MARKE):
            return argos.uebersetze(text, sprache)
        if m.startswith(AUTO_MARKE):
            std = self.k["modell"]
            if self.verfuegbar() and self.zustimmung_fehlt(std) is None:
                r = self._uebersetzen_ki(text, sprache, std)
                if "fehler" not in r:
                    return r
            return argos.uebersetze(text, sprache)
        r = self._text(anweisung_uebersetzung(sprache), text, "uebersetzung")
        return r if "fehler" in r else {**r, "methode": "KI"}

    def _uebersetzen_ki(self, text, sprache, modell) -> dict:
        r = self.anfrage(anweisung_uebersetzung(sprache), text, None, modell)
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        return {"text": r["ergebnis"], "cent": r.get("cent"), "methode": "KI"}
    def zusammenfassen(self, text): return self._text(ANWEISUNG_ZUSAMMENFASSUNG, text, "zusammenfassen")
    def text_analyse(self, text): return self._text(ANWEISUNG_ANALYSE, text, "textanalyse")
    def eigener_assistent(self, text, prompt, kommentar: bool = False, modell: str = "", nur_kommentar: bool = False):
        """``kommentar``: die KI begründet ihre Änderung nach ``KOMMENTAR_ZUSATZ``; ``nur_kommentar``: sie antwortet nur mit einem Kommentar;
        ``modell``: Modell des Assistenten (leer = Standard)."""
        prompt = prompt + (KOMMENTAR_NUR if nur_kommentar else KOMMENTAR_ZUSATZ if kommentar else "")
        r = self.anfrage(prompt, text, None, modell or self.modell(None))
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        return {"text": r["ergebnis"], "cent": r.get("cent"), **({"abgeschnitten": True} if r.get("abgeschnitten") else {})}

    def satz_umschreiben(self, satz: str, grund: str = "") -> dict:
        """Ein zu langer oder verschachtelter Satz in kürzere Sätze — der Sinn bleibt, nichts kommt dazu."""
        anweisung = ("Der folgende deutsche Satz ist zu lang oder zu verschachtelt (" + grund.rstrip(".") + "). Schreibe ihn in zwei oder mehr kürzere, klare Sätze um. "
                     "Ändere den Sinn nicht, erfinde nichts dazu, behalte Ton und Wortwahl bei. "
                     + EMPFAENGER.get(self.k["empfaenger"], EMPFAENGER["egal"])
                     + " Antworte ausschließlich mit den neuen Sätzen: keine Erklärung, keine Anführungszeichen, keine Vorrede.")
        return self._text(anweisung, satz, "textanalyse")

    def text_aktion(self, text, aktion): return self._text(anweisung_text_aktion(self.k, aktion), text)

    werkzeug_frage = staticmethod(lambda name, argumente, server, art="unbekannt": False)      # vom KI-Dienst ersetzt: fragt den Benutzer vor jedem Werkzeugaufruf
    server_frage = staticmethod(lambda name, befehl: False)       # vom KI-Dienst ersetzt: zeigt den vollständigen Startbefehl und fragt vor dem Start
    _server_erlaubt: set = set()                                    # Befehle, deren Start in dieser Sitzung erlaubt wurde (Zustimmung gilt nicht für Werkzeugaufrufe)

    def chat(self, verlauf: list[dict], dokumenttext: str = "", markiert: bool = False, strom=None, abbruch=None) -> dict:
        """``markiert``: ``dokumenttext`` ist nur die Markierung (Umfang „auszug“ genügt), sonst das ganze Dokument („dokument“)."""
        system = ("Du bist ein Schreibassistent in einem Textverarbeitungsprogramm und antwortest kurz und klar auf Deutsch. "
                  "Erfinde nichts dazu. " + EMPFAENGER.get(self.k["empfaenger"], EMPFAENGER["egal"]))
        if (sperre := self.zustimmung_fehlt(self.modell("chatbot"), "dokument" if dokumenttext.strip() and not markiert else "auszug")) is not None:
            return sperre
        if verlauf and verlauf[-1].get("bilder"):
            if (sperre := self.zustimmung_fehlt(self.modell("chatbot"), "bild")) is not None:
                return sperre                                       # der Bildinhalt geht an den Anbieter: eigene Einwilligung
            if not self.faehigkeit(self.modell("chatbot"))[1]:
                return {"fehler": "Das gewählte Modell kann keine Bilder verarbeiten. Bitte ein anderes Modell wählen."}
            verlauf, fehler = bilder_lesen(verlauf)                 # Lesen und Base64 erst hier, im Arbeitsfaden
            if fehler:
                return {"fehler": fehler}
        if dokumenttext.strip():
            system += "\n\nDer Mensch arbeitet gerade an diesem Text:\n" + dokumenttext[:12000]
        notiz = ""
        ws = self.k.websuche_optionen()
        ziel = self.websuche_ziel()
        if ws["an"] and verlauf and ziel and not self.k.hat_einwilligung(ziel, "auszug"):
            notiz = f"(Die Websuche wurde nicht ausgeführt: keine Zustimmung, die Frage an „{ziel}“ zu senden.)\n\n"
        elif ws["an"] and verlauf:
            from lunivo_writer.ai import websuche as W
            try:
                treffer = W.suche(ws, verlauf[-1]["text"])
                if treffer:
                    system += ("\n\nErgebnisse einer Websuche zur Frage (nenne die Nummer der Quelle, wenn du sie benutzt):\n" + W.als_text(treffer))
            except (OSError, ValueError) as e:
                notiz = f"(Die Websuche hat nicht geklappt: {getattr(e, 'reason', e)})\n\n"
        modell = self.modell("chatbot")
        quellen = []
        dso = self.k.dokumentsuche_optionen()
        if dso["an"] and dso["ordner"] and verlauf:
            aussen = self.schickt_nach_aussen(modell)
            if aussen and not self.k.hat_einwilligung(aussen, "auszug"):
                notiz += f"(Die Dokumentensuche wurde nicht ausgeführt: keine Zustimmung, Auszüge an „{aussen}“ zu senden.)\n\n"
            else:
                from lunivo_writer.ai import dokumentensuche as DS
                try:
                    idx = DS.Index(self.k.dokumentindex_pfad())
                    idx.aktualisieren(dso["ordner"], zeitgrenze=4.0)       # nur Neues und Geändertes, mit Zeitgrenze
                    quellen = idx.suchen(verlauf[-1]["text"], dso["ordner"], dso["anzahl"])
                except Exception as e:                                     # die Suche darf den Chat nie verhindern
                    notiz += f"(Die Dokumentensuche hat nicht geklappt: {e})\n\n"
                if quellen:
                    system += ("\n\nAuszüge aus Dokumenten des Benutzers (nenne die Nummer der Quelle, wenn du sie benutzt; antworte nur mit dem, "
                               "was dort steht):\n" + DS.als_text(quellen))
        server = [m for m in self.k["mcp"] if m.get("an") and m.get("befehl")]
        if server and (modell.startswith(EIGEN_MARKE) or modell.startswith(OLLAMA_MARKE)):
            r = self._chat_werkzeuge(system, verlauf, server, modell, self.k.chat_optionen())
        else:
            opt = self.k.chat_optionen()
            if strom is not None:
                opt = {**opt, "_strom": (lambda t: strom(notiz + t)), "_abbruch": abbruch}
            r = self._text(system, verlauf, "chatbot", opt)
        if "text" in r and r.pop("abgeschnitten", False):
            r["text"] += "\n\n[Antwort wegen der Längengrenze gekürzt — in den Chat-Einstellungen „Maximale Länge“ erhöhen.]"
        if quellen and "text" in r:
            from lunivo_writer.ai import dokumentensuche as DS
            r["text"] += "\n\nFundstellen:\n" + DS.fundstellen_zeilen(quellen)
        if notiz and "text" in r:
            r["text"] = notiz + r["text"]
        return r

    def _chat_werkzeuge(self, system: str, verlauf: list[dict], server: list[dict], modell: str, optionen: dict) -> dict:
        """Chat mit MCP-Werkzeugen über die OpenAI-kompatible Schnittstelle (Ollama und eigene Anbieter): das Modell darf Werkzeuge verlangen; jeder
        Aufruf wird erst nach Rückfrage beim Benutzer ausgeführt."""
        from lunivo_writer.ai import mcp as M
        if modell.startswith(EIGEN_MARKE):
            a = self.k.anbieter_holen(modell[len(EIGEN_MARKE):])
            if not a:
                return {"fehler": "Der gewählte Anbieter ist nicht mehr da."}
            url, name, kopf = a["url"] + "/chat/completions", a["modell"], ({"authorization": "Bearer " + a["schluessel"]} if a["schluessel"] else {})
        else:
            url, name, kopf = OLLAMA_URL + "/v1/chat/completions", modell[len(OLLAMA_MARKE):], {}
        clients, tools, wo = [], [], {}
        try:
            for sv in server:
                if sv["befehl"] not in self._server_erlaubt:
                    if not self.server_frage(sv["name"], sv["befehl"]):
                        return {"fehler": f"Der Start des KI-Werkzeugs „{sv['name']}“ wurde nicht erlaubt."}
                    self._server_erlaubt = self._server_erlaubt | {sv["befehl"]}
                try:
                    c = M.McpClient(sv["befehl"])
                except M.McpFehler as e:
                    return {"fehler": f"KI-Werkzeug „{sv['name']}“: {e}"}
                clients.append(c)
                for t in c.werkzeuge():
                    n = t["name"] if t["name"] not in wo else f"{sv['name']}_{t['name']}"
                    wo[n] = (c, t["name"], sv["name"], M.art_des_werkzeugs(t))
                    tools.append({"type": "function", "function": {"name": n, "description": t.get("description", ""), "parameters": t.get("inputSchema") or {"type": "object", "properties": {}}}})
            nachrichten = [{"role": "system", "content": system}] + _nachrichten(verlauf, "openai")
            effort = self._stufe(optionen)["openai"]
            modus = optionen.get("werkzeuge", "fragen")
            for _runde in range(6):
                bitte = {"model": name, "messages": nachrichten, "tools": tools, "temperature": float(optionen.get("temperatur", 0.2))}
                if optionen.get("topP") is not None:
                    bitte["top_p"] = float(optionen["topP"])
                if optionen.get("maxLaenge"):
                    bitte["max_tokens"] = int(optionen["maxLaenge"])
                if effort is not None:
                    bitte["reasoning_effort"] = effort
                try:
                    with _post(url, kopf, bitte, 300) as r:
                        daten = _json_dict(r)
                except urllib.error.HTTPError as e:
                    if e.code != 400 or effort is None:
                        raise
                    effort = None                                      # Denktiefe nicht unterstützt: ohne sie noch einmal, dauerhaft für dieses Gespräch
                    bitte.pop("reasoning_effort", None)
                    with _post(url, kopf, bitte, 300) as r:
                        daten = _json_dict(r)
                wahl = daten.get("choices") if isinstance(daten.get("choices"), list) and daten.get("choices") else [{}]
                msg = wahl[0].get("message") if isinstance(wahl[0], dict) and isinstance(wahl[0].get("message"), dict) else {}
                aufrufe = [a for a in (msg.get("tool_calls") or []) if isinstance(a, dict)] if isinstance(msg.get("tool_calls"), list) else []
                if not aufrufe:
                    erg = ohne_gruebeln(msg.get("content") or "").strip()
                    return {"text": erg} if erg else {"fehler": "Es kam keine Antwort zurück."}
                nachrichten.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": aufrufe})
                for aufruf in aufrufe:
                    f = aufruf.get("function") or {}
                    try:
                        arg = json.loads(f.get("arguments") or "{}") if isinstance(f.get("arguments"), str) else (f.get("arguments") or {})
                    except ValueError:
                        arg = {}
                    ziel = wo.get(f.get("name", ""))
                    if ziel is None:
                        ergebnis = "Dieses Werkzeug gibt es nicht."
                    elif not (MF.werkzeug_erlaubt(modus, ziel[3]) or self.werkzeug_frage(ziel[1], arg, ziel[2], ziel[3])):
                        ergebnis = "Der Benutzer hat den Aufruf abgelehnt."
                    else:
                        try:
                            ergebnis = ziel[0].aufrufen(ziel[1], arg)
                        except M.McpFehler as e:
                            ergebnis = f"Fehler: {e}"
                    nachrichten.append({"role": "tool", "tool_call_id": aufruf.get("id", ""), "content": str(ergebnis)[:8000]})
            return {"fehler": "Die KI hat zu viele Werkzeugaufrufe gebraucht. Bitte die Frage genauer stellen."}
        except M.McpFehler as e:
            return {"fehler": f"KI-Werkzeug: {e}"}
        except urllib.error.HTTPError as e:
            return {"fehler": f"Der Anbieter meldet Fehler {e.code} — unterstützt das Modell Werkzeuge" + (" und Bilder?" if any(z.get("bilder") for z in verlauf[-1:]) else "?")}
        except (urllib.error.URLError, OSError, ValueError) as e:
            return {"fehler": f"Es hat nicht geklappt: {getattr(e, 'reason', e)}"}
        finally:
            for c in clients:
                c.schliessen()

    def vorschlaege(self, text: str) -> dict:
        r = self.anfrage(anweisung_vorschlaege(self.k), text, VORSCHLAG_BAUPLAN, self.modell("textanalyse"))
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        try:
            daten = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", r["ergebnis"].strip()))
            lst = daten["vorschlaege"]
            assert isinstance(lst, list)
        except (ValueError, KeyError, AssertionError):
            return {"fehler": "Die Antwort kam nicht in der erwarteten Form."}
        # nur, was sich zeichengenau im Text wiederfindet, lässt sich einsetzen
        gut = [v for v in lst if isinstance(v, dict) and isinstance(v.get("alt"), str) and isinstance(v.get("neu"), str)
               and v["alt"].strip() and v["neu"].strip() and v["alt"] != v["neu"] and v["alt"] in text]
        from lunivo_writer.proofing.fund import klemmen
        for v in gut:                                   # Sicherheit des Modells (0…1), fehlt sie oder ist sie Unsinn: 0,5
            v["konfidenz"] = klemmen(v.get("konfidenz"))
            v["quelle"] = "ki"
        gut.sort(key=lambda v: -v["konfidenz"])
        return {"vorschlaege": gut, "cent": r.get("cent")}

    def synonyme(self, wort: str, umgebung: str = "") -> dict:
        """Wörter, die statt `wort` an dieser Stelle stehen könnten (Thesaurus — geht nur mit KI)."""
        anweisung = (f"Nenne gebräuchliche deutsche Wörter, die statt „{wort}“ an dieser Stelle stehen könnten. "
                     "Achte auf den Zusammenhang: Dasselbe Wort bedeutet je nach Satz Verschiedenes. "
                     "Nimm einfache, geläufige Wörter — dieser Text wird von einem Menschen mit Legasthenie geschrieben, "
                     "und ein seltenes Fremdwort hilft ihm nicht. Höchstens acht, jedes in der Form, in der es im Satz "
                     "stehen müsste. Fällt dir nichts Passendes ein, bleibt die Liste leer.")
        bauplan = {"type": "object", "properties": {"woerter": {"type": "array", "items": {"type": "string"}}},
                   "required": ["woerter"], "additionalProperties": False}
        r = self.anfrage(anweisung, umgebung or wort, bauplan)
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        try:
            daten = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", r["ergebnis"].strip()))
            lst = daten["woerter"]
            assert isinstance(lst, list)
        except (ValueError, KeyError, AssertionError):
            return {"fehler": "Die Antwort kam nicht in der erwarteten Form."}
        sauber = []
        for w in lst:
            if isinstance(w, str) and w.strip() and len(w) < 40 and w.strip().lower() != wort.lower() and w.strip() not in sauber:
                sauber.append(w.strip())
        return {"woerter": sauber[:8], "cent": r.get("cent")}

    def bild_erzeugen(self, beschreibung: str) -> dict:
        """Bild aus Text: nur eigene Anbieter mit „Bilder“, OpenAI-Schnittstelle POST <URL>/images/generations."""
        modell = self.k["aufgaben"].get("bildgenerierung", "")
        if not modell.startswith(EIGEN_MARKE):
            return {"fehler": "Dafür fehlt ein Anbieter mit „Bilder“ — in der KI-Konfiguration eintragen."}
        a = self.k.anbieter_holen(modell[len(EIGEN_MARKE):])
        if not a:
            return {"fehler": "Der gewählte Anbieter ist nicht mehr da. In der KI-Konfiguration neu wählen."}
        if not a["modell"]:
            return {"fehler": f"Für „{a['name']}“ ist kein Modell eingetragen."}
        if (sperre := self.zustimmung_fehlt(modell)) is not None:
            return sperre
        kopf = {"authorization": "Bearer " + a["schluessel"]} if a["schluessel"] else {}
        try:
            with _post(a["url"] + "/images/generations", kopf,
                       {"model": a["modell"], "prompt": beschreibung, "n": 1, "size": "1024x1024"}, 90) as r:
                daten = _json_dict(r)
            liste = daten.get("data") if isinstance(daten.get("data"), list) and daten.get("data") else [{}]
            e = liste[0] if isinstance(liste[0], dict) else {}
            if e.get("b64_json"):
                import base64
                return {"bild": base64.b64decode(e["b64_json"])}
            if e.get("url"):
                if urllib.parse.urlparse(str(e["url"])).scheme not in ("http", "https"):
                    return {"fehler": f"„{a['name']}“ hat eine unzulässige Bildadresse geschickt."}      # kein file:// o. Ä. aus fremder Antwort
                with urllib.request.urlopen(e["url"], timeout=90) as r2:
                    return {"bild": r2.read()}
            return {"fehler": f"„{a['name']}“ hat kein Bild zurückgegeben."}
        except urllib.error.HTTPError as e:
            zusatz = ""
            try:
                zusatz = (json.loads(e.read().decode("utf-8")).get("error") or {}).get("message", "")
            except (OSError, ValueError, AttributeError):
                pass
            return {"fehler": f"„{a['name']}“ meldet Fehler {e.code}" + (f" ({zusatz})" if zusatz else "")}
        except TimeoutError:
            return {"fehler": f"„{a['name']}“ hat zu lange gebraucht. Bitte noch einmal versuchen."}
        except (urllib.error.URLError, OSError, ValueError):
            return {"fehler": f"„{a['name']}“ ist unter {a['url']} nicht zu erreichen. Stimmt die URL?"}

    def ollama_modelle(self) -> list[str]:
        try:
            with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=3) as r:
                return sorted(m["name"] for m in _json_dict(r).get("models", []) if isinstance(m, dict) and m.get("name"))
        except (OSError, ValueError, KeyError, TypeError):
            return []


def anbieter_modelle(url: str, schluessel: str = "") -> list[str]:
    """GET <URL>/models — so fragen OpenAI und die meisten OpenAI-kompatiblen Dienste (auch Ollama unter /v1)."""
    req = urllib.request.Request(url.rstrip("/") + "/models", headers={"accept": "application/json",
                                 **({"authorization": "Bearer " + schluessel} if schluessel else {})})
    with urllib.request.urlopen(req, timeout=6) as r:
        d = _json_dict(r)
    return sorted({m.get("id") or m.get("name") for m in (d.get("data") or d.get("models") or []) if isinstance(m, dict)} - {None})


# Wort-Diff bleibt unter dem bisherigen Importpfad verfügbar.
from lunivo_writer.ai.ki_diff import _STUECKE, aenderungen, ersetze_ergebnis
