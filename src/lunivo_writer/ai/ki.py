"""Die KI-Ebene: Korrigieren, Vorschläge, Übersetzen, Zusammenfassen, Text bearbeiten, Chat.

Freiwillig und nach außen nur auf ausdrücklichen Knopfdruck:
  · Ollama — läuft auf diesem Rechner (127.0.0.1:11434), der Text verlässt das Gerät nicht.
  · Claude — Anthropic-API, nur mit eigenem Schlüssel und nur nach Ihrer Zustimmung (siehe KIKonfig.claude_erlaubt).
  · Eigener Anbieter — OpenAI-kompatible Schnittstelle unter einer von Ihnen eingetragenen Adresse.
Schlüssel stehen nie im Quelltext, sondern in einer Datei mit Zugriff nur für den Benutzer (0600).
"""
from __future__ import annotations

import json
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



from lunivo_writer.ai import ki_bildgenerierung as BG
from lunivo_writer.ai import ki_chat_kontext as CK
from lunivo_writer.ai import ki_claude as CL
from lunivo_writer.ai import ki_eigen as EG
from lunivo_writer.ai import ki_ollama as OL
from lunivo_writer.ai import ki_textaktionen as TA
from lunivo_writer.ai import ki_transport as T

# Die Bausteine der Anbieter bleiben unter dem bisherigen Importpfad verfügbar.
from lunivo_writer.ai.ki_transport import (
    json_dict as _json_dict, post_roh as _post, bild_block as _bild_block, nachricht as _nachricht, nachrichten as _nachrichten,
    bilder_lesen, ohne_gruebeln,
)
from lunivo_writer.ai.ki_claude import cent_fuer
from lunivo_writer.ai.ki_ollama import (
    KEEP_ALIVE_MIN, KEEP_ALIVE_MAX, NUM_CTX_STUFEN, NUM_PREDICT_CHAT, NUM_PREDICT_MIN, NUM_PREDICT_MAX, ZEICHEN_JE_TOKEN,
    keep_alive_begrenzen, num_thread_begrenzen, num_ctx_begrenzen, num_predict_fuer, num_ctx_fuer,
)

# Anweisungen bleiben unter dem bisherigen Importpfad verfügbar.
from lunivo_writer.ai.ki_anweisungen import (
    _NUR_ZEILEN, _zettel, steckbrief, anweisung_korrektur, anweisung_uebersetzung,
    anweisung_vorschlaege, ANWEISUNG_ZUSAMMENFASSUNG, ANWEISUNG_ANALYSE,
    anweisung_text_aktion,
)




def als_geld(cent) -> str:
    if cent is None:
        return ""
    return "unter 1 Cent" if cent < 1 else f"{cent / 100:.2f} $".replace(".", ",")



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

    _stufe = staticmethod(T.stufe)
    _stopp = staticmethod(T.stopp_liste)

    def _claude(self, anweisung, text, bauplan, modell, optionen=None) -> dict:
        return CL.anfrage(CLAUDE_URL, self.k["apiKey"], anweisung, text, bauplan, modell, optionen)

    def _ollama(self, anweisung, text, bauplan, modell, optionen=None) -> dict:
        return OL.anfrage(OLLAMA_URL, self.k.chat_optionen(), anweisung, text, bauplan, modell, optionen)

    def _eigen(self, a, anweisung, text, bauplan, optionen=None) -> dict:
        return EG.anfrage(a, anweisung, text, bauplan, optionen)

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
    def eigener_assistent(self, text, prompt, kommentar: bool = False, modell: str = "", nur_kommentar: bool = False, optionen: dict | None = None):
        """``kommentar``: die KI begründet ihre Änderung nach ``KOMMENTAR_ZUSATZ``; ``nur_kommentar``: sie antwortet nur mit einem Kommentar;
        ``modell``: Modell des Assistenten (leer = Standard); ``optionen``: z. B. ``_strom``/``_abbruch`` (abbrechbare Hintergrundanfrage)."""
        prompt = prompt + (KOMMENTAR_NUR if nur_kommentar else KOMMENTAR_ZUSATZ if kommentar else "")
        r = self.anfrage(prompt, text, None, modell or self.modell(None), optionen)
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
        modell = self.modell("chatbot")
        if (sperre := CK.sperre(self, modell, verlauf, dokumenttext, markiert)) is not None:
            return sperre
        verlauf, fehler = CK.bilder(self, modell, verlauf)
        if fehler is not None:
            return fehler
        system = CK.system_text(self, dokumenttext)
        web, notiz = CK.websuche(self, verlauf)
        dok, notiz_dok, quellen = CK.dokumentensuche(self, verlauf, modell)
        system, notiz = system + web + dok, notiz + notiz_dok
        server = [m for m in self.k["mcp"] if m.get("an") and m.get("befehl")]
        if server and modell.startswith((EIGEN_MARKE, OLLAMA_MARKE)):
            r = self._chat_werkzeuge(system, verlauf, server, modell, self.k.chat_optionen())
        else:
            r = self._text(system, verlauf, "chatbot", self._chat_optionen(strom, abbruch, notiz))
        return CK.abschliessen(r, quellen, notiz)

    def _chat_optionen(self, strom, abbruch, notiz: str) -> dict:
        opt = self.k.chat_optionen()
        if strom is None:
            return opt
        return {**opt, "_strom": (lambda t: strom(notiz + t)), "_abbruch": abbruch}

    def _chat_ziel(self, modell: str):
        """(Adresse, Modellname beim Anbieter, Kopfzeilen) für den Chat mit Werkzeugen; None, wenn der eigene Anbieter fehlt."""
        if not modell.startswith(EIGEN_MARKE):
            return OLLAMA_URL + "/v1/chat/completions", modell[len(OLLAMA_MARKE):], {}
        a = self.k.anbieter_holen(modell[len(EIGEN_MARKE):])
        return (a["url"] + "/chat/completions", a["modell"], T.bearer_kopf(a["schluessel"])) if a else None

    def _chat_werkzeuge(self, system: str, verlauf: list[dict], server: list[dict], modell: str, optionen: dict) -> dict:
        """Chat mit MCP-Werkzeugen über die OpenAI-kompatible Schnittstelle (Ollama und eigene Anbieter), siehe ``ki_werkzeugschleife``."""
        from lunivo_writer.ai import ki_werkzeugschleife as WS
        ziel = self._chat_ziel(modell)
        if ziel is None:
            return {"fehler": "Der gewählte Anbieter ist nicht mehr da."}
        return WS.chat(self, system, verlauf, server, ziel, optionen)

    def vorschlaege(self, text: str) -> dict:
        r = self.anfrage(anweisung_vorschlaege(self.k), text, VORSCHLAG_BAUPLAN, self.modell("textanalyse"))
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        lst = TA.liste_lesen(r["ergebnis"], "vorschlaege")
        if lst is None:
            return dict(TA.FEHLER_FORM)
        return {"vorschlaege": TA.vorschlaege_bereinigen(lst, text), "cent": r.get("cent")}

    def synonyme(self, wort: str, umgebung: str = "") -> dict:
        """Wörter, die statt `wort` an dieser Stelle stehen könnten (Thesaurus — geht nur mit KI)."""
        r = self.anfrage(TA.anweisung_synonyme(wort), umgebung or wort, TA.SYNONYM_BAUPLAN)
        if "fehler" in r:
            return r
        self._kosten(r.get("cent"))
        lst = TA.liste_lesen(r["ergebnis"], "woerter")
        if lst is None:
            return dict(TA.FEHLER_FORM)
        return {"woerter": TA.synonyme_bereinigen(lst, wort), "cent": r.get("cent")}

    def bild_erzeugen(self, beschreibung: str) -> dict:
        """Bild aus Text: nur eigene Anbieter mit „Bilder“, siehe ``ki_bildgenerierung``."""
        modell = self.k["aufgaben"].get("bildgenerierung", "")
        a, fehler = BG.anbieter_pruefen(self.k, modell)
        if fehler is not None:
            return fehler
        if (sperre := self.zustimmung_fehlt(modell)) is not None:
            return sperre
        return BG.erzeugen(a, beschreibung)

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
