"""Konstanten, Assistentenvorlagen und persistente KI-Konfiguration."""
from __future__ import annotations

import base64
import json
import os
import re
import threading
import time
import difflib
import urllib.error
import urllib.parse
import urllib.request

from lunivo_writer.ki import modellfaehigkeit as MF

OLLAMA_URL = "http://127.0.0.1:11434"
CLAUDE_URL = "https://api.anthropic.com/v1/messages"
OLLAMA_MARKE, EIGEN_MARKE = "ollama:", "eigen:"
ARGOS_MARKE, AUTO_MARKE = "argos:", "auto:"      # lokale Übersetzung (Argos) / Automatisch: KI, sonst lokal
LERN_SCHWELLE = 5
ZETTEL_GRENZE = 300
UMFAENGE = {"auszug": "markierte Textauszüge", "dokument": "den ganzen Text des Dokuments",
           "bild": "ein angehängtes Bild", "dauer": "bei jeder Änderung den geänderten Absatz (fortlaufende Assistenten)"}      # was an einen Anbieter im Internet gehen darf

EMPFAENGER = {
    "egal": "Lass den Tonfall genau so, wie er im Text steht: Förmliches bleibt förmlich, Lockeres bleibt locker. "
            "Ändere die Wortwahl nur da, wo sie falsch ist.",
    "Amt": "Der Text geht an eine Behörde — Amt, Jobcenter, Krankenkasse, Versicherung, Gericht. Halte den Tonfall "
           "durchgehend förmlich und höflich: Siezen, vollständige Sätze, keine Umgangssprache, keine Abkürzungen "
           "mitten im Satz. Sachlich bleiben auch dort, wo der Text ärgerlich klingt — der Vorwurf darf inhaltlich "
           "stehen bleiben, aber im ruhigen Ton. Stehen Anrede, Betreff oder ein Aktenzeichen schon da, bring sie in "
           "die übliche Form; fehlen sie, erfinde sie nicht.",
    "Arbeit": "Der Text geht an jemanden aus dem Beruf — Chefin, Kollege, Kundschaft. Höflich und knapp: keine "
              "Ausschmückung, keine Floskelketten, aber auch nicht schroff. Ob geduzt oder gesiezt wird, entscheidet "
              "der Text — dreh das nicht um.",
    "Freunde": "Der Text geht an jemanden, den man kennt — Familie, Freundin, Nachbar. Duzen, freundlich und "
               "zugewandt, kurze Sätze, ruhig so, wie man redet. Nicht flapsig und nicht anbiedernd. Emojis, "
               "Ausrufezeichen und Anreden wie „Hey“ bleiben stehen.",
    "Forum": "Der Text wird öffentlich gelesen — Forum, Kommentar, Bewertung, soziales Netz. Er muss auch für Fremde "
             "verständlich sein, die die Vorgeschichte nicht kennen: klare Sätze, Absätze statt eines Blocks. Geduzt "
             "wird, wie es dort üblich ist. Nicht belehrend — eine deutliche Meinung darf deutlich bleiben, aber ohne "
             "Beleidigung.",
    "Bewerbung": "Der Text ist eine Bewerbung oder gehört dazu. Siezen, förmlich, aber nicht steif. Selbstbewusst "
                 "ohne Angeberei: klare Aussagesätze statt „ich würde gerne“ und statt Floskelketten. Erfinde keine "
                 "Fähigkeiten, keine Stationen und keine Zahlen dazu.",
}
SPRACHEN = ["Englisch", "Deutsch", "Türkisch", "Russisch", "Ukrainisch", "Polnisch", "Rumänisch", "Arabisch",
            "Französisch", "Spanisch", "Italienisch", "Griechisch", "Niederländisch", "Portugiesisch"]
MODELLE_FEST = [("claude-opus-5", "Beste Qualität · Opus 5"), ("claude-sonnet-5", "Mittelweg · Sonnet 5"),
                ("claude-haiku-4-5", "Günstig & schnell · Haiku 4.5")]
PREISE = {"claude-opus-5": (5, 25), "claude-sonnet-5": (3, 15), "claude-haiku-4-5": (1, 5)}   # Dollar je Million Token
TEXT_AKTIONEN = [("verbessern", "Verbessern"), ("umformulieren", "Umformulieren"), ("kuerzen", "Kürzen"),
                 ("erweitern", "Erweitern"), ("professioneller", "Professioneller formulieren"),
                 ("einfacher", "Einfacher formulieren"), ("ton-freundlich", "Tonalität: Freundlich"),
                 ("ton-foermlich", "Tonalität: Förmlich"), ("ton-sachlich", "Tonalität: Sachlich"),
                 ("ton-locker", "Tonalität: Locker"), ("ton-bestimmt", "Tonalität: Bestimmt")]
_AKTION_SATZ = {
    "verbessern": "Verbessere den folgenden Text — klarer und natürlicher, ohne den Sinn zu ändern.",
    "umformulieren": "Formuliere den folgenden Text um — derselbe Sinn, andere Worte und Sätze.",
    "kuerzen": "Kürze den folgenden Text deutlich — nur das Wichtigste bleibt.",
    "erweitern": "Erweitere den folgenden Text um sinnvolle Einzelheiten, ohne abzuschweifen.",
    "professioneller": "Formuliere den folgenden Text professioneller und sachlicher.",
    "einfacher": "Formuliere den folgenden Text einfacher — kurze Sätze, geläufige Wörter.",
    "ton-freundlich": "Ändere die Tonalität des folgenden Textes zu freundlich und zugewandt.",
    "ton-foermlich": "Ändere die Tonalität des folgenden Textes zu förmlich.",
    "ton-sachlich": "Ändere die Tonalität des folgenden Textes zu sachlich und neutral.",
    "ton-locker": "Ändere die Tonalität des folgenden Textes zu locker und ungezwungen.",
    "ton-bestimmt": "Ändere die Tonalität des folgenden Textes zu bestimmt und klar.",
}
# Anweisungen der Chat-Vorschläge, die es als Schnelle Aktion noch nicht gab (Titel, Anweisung); die übrigen kommen aus TEXT_AKTIONEN/_AKTION_SATZ
VORLAGE_ANWEISUNG = {
    "umschreiben": ("Text umschreiben", "Schreiben Sie den folgenden Text um, damit er klar, prägnant und professioneller wird. Verbessern Sie die Lesbarkeit und den Satzbau, "
                    "während Sie die ursprüngliche Bedeutung und Absicht beibehalten."),
    "vereinfachen": ("Text vereinfachen", "Vereinfachen Sie den folgenden Text: kurze Sätze, geläufige Wörter, leicht verständlich, ohne die Bedeutung zu verändern."),
    "erweitern_inhalt": ("Inhalt erweitern", "Erweitern Sie den folgenden Inhalt um sinnvolle Einzelheiten, Beispiele und Erklärungen, ohne vom Thema abzuschweifen."),
    "inhaltsverzeichnis": ("Inhaltsverzeichnis erstellen", "Erstellen Sie ein Inhaltsverzeichnis für das folgende Dokument, das seine Gliederung und die wichtigsten Abschnitte widerspiegelt."),
    "titel": ("Titel vorschlagen", "Schlagen Sie drei passende, prägnante Titel für das folgende Dokument vor."),
    "kernpunkte": ("Kernpunkte hervorheben", "Heben Sie die Kernpunkte des folgenden Textes hervor und nennen Sie sie als kurze Liste."),
    "korrektur": ("Dokument Korrektur lesen", "Lesen Sie das folgende Dokument Korrektur: Nennen Sie Rechtschreib-, Grammatik- und Zeichensetzungsfehler und verbessern Sie sie, "
                  "ohne Inhalt und Stil zu verändern."),
    "dokument_zusammenfassen": ("Dokument zusammenfassen", "Fassen Sie das folgende Dokument in wenigen Sätzen zusammen und nennen Sie nur die wichtigsten Aussagen."),
    "zusammenfassung": ("Zusammenfassung erstellen", "Erstellen Sie eine Zusammenfassung des folgenden Textes als kurzen Abschnitt, den man auch ohne den Originaltext versteht."),
    "entwurf": ("Entwurf schreiben", "Schreiben Sie einen ersten Entwurf für ein Dokument zu dem Thema, das ich Ihnen nenne. Fragen Sie nach dem Thema, wenn es fehlt."),
    "gliederung": ("Gliederung vorschlagen", "Schlagen Sie eine übersichtliche Gliederung für ein neues Dokument vor und fragen Sie nach dem Thema, wenn es fehlt."),
}
ANBIETER_TAGS = [("text", "Text"), ("bilder", "Bilder"), ("einbettungen", "Einbettungen"), ("audio", "Audioverarbeitung"),
                 ("moderation", "Inhaltsmoderation"), ("echtzeit", "Echtzeitaufgaben"),
                 ("programmieren", "Hilfe zum Programmieren"), ("visuell", "Visuelle Analyse")]
# Erweiterte Einstellungen des Chats: maxLaenge 0 = Vorgabe des Anbieters; temperatur/topP gelten für Ollama und eigene Anbieter
CHAT_VORGABE = {"maxLaenge": 0, "temperatur": 0.2, "topP": 1.0, "stopp": "", "direkt": False,
                "denktiefe": MF.DENK_VORGABE, "werkzeuge": "fragen",
                "keepAlive": 30, "numCtx": 8192, "streaming": True, "numThread": 0}      # numThread 0 = Ollama wählt selbst      # werkzeuge: „automatisch“ gilt nur für die Sitzung (wird nie gespeichert)
AUFGABEN = [("chatbot", "Chatbot"), ("zusammenfassen", "Zusammenfassen"), ("uebersetzung", "Übersetzung"),
            ("textanalyse", "Textanalyse"), ("bildgenerierung", "Bildgenerierung")]
# Bekannte Anbieter mit der Adresse, die sie selbst angeben (Claude fehlt bewusst: kein OpenAI-kompatibles /chat/completions)
ANBIETER_VORLAGEN = [("andere", "Andere", ""), ("ollama", "Ollama (auf diesem Rechner)", "http://localhost:11434/v1"),
                     ("openai", "OpenAI", "https://api.openai.com/v1"), ("openrouter", "OpenRouter", "https://openrouter.ai/api/v1"),
                     ("gemini", "Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai"),
                     ("mistral", "Mistral", "https://api.mistral.ai/v1"), ("groq", "Groq", "https://api.groq.com/openai/v1"),
                     ("deepseek", "DeepSeek", "https://api.deepseek.com/v1"), ("together", "Together AI", "https://api.together.xyz/v1")]
# ---- Assistenten: Schnelle KI-Aktionen (art „aktion“, auf Knopfdruck) und fortlaufende Assistenten (art „fortlaufend“)
ASSISTENT_ARTEN = ("aktion", "fortlaufend")
AKTIONS_MODI = ("ersetzen", "anhaengen", "hinweis")                        # bisherige Wirkungen einer Schnellen KI-Aktion
FORTLAUFEND_MODI = AKTIONS_MODI + ("kommentar", "hervorheben")           # fortlaufend zusätzlich: Kommentar anlegen / Fund in der Schreibhilfe
ASSISTENT_AUSLOESER = ("knopf", "absatz", "markierung")                  # nur „absatz“ und „markierung“ werden überwacht
ASSISTENT_UMFAENGE = ("absatz", "markierung")                            # nie das ganze Dokument
KOMMENTAR_ZUSATZ = ("\n\nBegründe deine Änderung kurz (ein bis zwei Sätze). Schreibe zuerst den Text, dann eine eigene Zeile "
                    "###BEGRUENDUNG### und danach die Begründung.")
KOMMENTAR_NUR = "\n\nAntworte nur mit einem kurzen Kommentar (höchstens drei Sätze); ändere den Text nicht und gib ihn nicht noch einmal aus."
VORLAGEN_ASSISTENT = [
    # (Name, Prompt, Aktion = modus, Erklärender Kommentar)
    ("Korrekturlesen", "Korrigiere Rechtschreibung, Grammatik und Zeichensetzung des Textes. Ändere weder Inhalt noch Stil. "
     "Antworte ausschließlich mit dem korrigierten Text.", "ersetzen", True),
    ("KI-Inhaltsindikator", "Beurteile, ob der Text eher von einem Menschen oder von einer KI geschrieben wirkt. Nenne die Merkmale, "
     "die dafür sprechen, und gib eine vorsichtige Einschätzung. Sei ehrlich über die Unsicherheit dieser Einschätzung.", "kommentar", False),
    ("Textoptimierer", "Verbessere Lesbarkeit und Ausdruck des Textes: klarere Wortwahl, kürzere Sätze, keine Füllwörter. "
     "Der Sinn und der Tonfall bleiben. Antworte ausschließlich mit dem verbesserten Text.", "ersetzen", True),
    ("Faktenprüfung", "Prüfe die Tatsachenbehauptungen im Text. Nenne jede Behauptung, die falsch oder zweifelhaft ist oder sich "
     "nicht belegen lässt, und sage kurz warum. Erfinde keine Quellen; sage, wenn du etwas nicht sicher weißt.", "kommentar", False),
    ("Professionelle Umschreibung", "Schreibe den Text in einem professionellen, sachlichen und höflichen Ton um. "
     "Der Inhalt bleibt, nichts wird hinzugefügt. Antworte ausschließlich mit dem umgeschriebenen Text.", "ersetzen", True),
    ("Logik- und Argumentationsprüfung", "Prüfe die Argumentation des Textes auf Denkfehler, Widersprüche, fehlende Begründungen und "
     "Trugschlüsse. Nenne die Stellen und erkläre knapp, was nicht schlüssig ist.", "hervorheben", True),
]
VORSCHLAG_BAUPLAN = {"type": "object", "properties": {"vorschlaege": {"type": "array", "items": {
    "type": "object", "properties": {"alt": {"type": "string"}, "neu": {"type": "string"}, "grund": {"type": "string"},
                                                                        "konfidenz": {"type": "number"}},
    "required": ["alt", "neu", "grund", "konfidenz"], "additionalProperties": False}}},
    "required": ["vorschlaege"], "additionalProperties": False}


def assistent_normiert(a: dict) -> dict:
    """Ein Assistenteneintrag mit allen Feldern und gültigen Werten; fehlende Felder (ältere Einträge) bekommen ihre Vorgabe.
    aktion: id, name, prompt, modus, zugriff.  fortlaufend zusätzlich: ausloeser, umfang, verzoegerung, an.  Beide: symbol, kommentar, modell."""
    from lunivo_writer.ki.assistent_lauf import VERZOEGERUNG_VORGABE, verzoegerung_begrenzen
    art = a.get("art") if a.get("art") in ASSISTENT_ARTEN else "aktion"
    erlaubt = FORTLAUFEND_MODI if art == "fortlaufend" else AKTIONS_MODI
    r = {**a, "art": art, "name": (a.get("name") or "").strip()[:40], "prompt": (a.get("prompt") or "").strip()[:2000],
         "modus": a.get("modus") if a.get("modus") in erlaubt else "hinweis",
         "zugriff": "schnell" if a.get("zugriff") == "schnell" else "kontext",
         "symbol": str(a.get("symbol") or ""), "kommentar": bool(a.get("kommentar", False)),
         "modell": str(a.get("modell") or ""), "an": bool(a.get("an", False)) and art == "fortlaufend",
         "ausloeser": a.get("ausloeser") if a.get("ausloeser") in ASSISTENT_AUSLOESER else "knopf",
         "umfang": a.get("umfang") if a.get("umfang") in ASSISTENT_UMFAENGE else "absatz",
         "verzoegerung": verzoegerung_begrenzen(a.get("verzoegerung", VERZOEGERUNG_VORGABE))}
    if art == "aktion":
        r["ausloeser"] = "knopf"
    return r


# ---------------------------------------------------------------- Konfiguration (mit Schlüsseln, 0600)
class KIKonfig:
    def __init__(self, pfad: str):
        self.pfad = pfad
        self.d = {"modell": "claude-opus-5", "sprache": "Englisch", "empfaenger": "egal", "zettel": "",
                  "apiKey": "", "anbieter": [], "aufgaben": {"uebersetzung": AUTO_MARKE}, "kosten": 0.0, "claude_erlaubt": False, "einwilligungen": [], "assistenten": [], "assistenten_dauerbetrieb": False, "chat": {}, "mcp": [], "websuche": {}, "dokumentsuche": {}}
        try:
            with open(pfad, encoding="utf-8") as fh:
                self.d.update(json.load(fh))
        except (OSError, ValueError):
            pass
        if isinstance(self.d.get("chat"), dict) and self.d["chat"].get("werkzeuge") != "fragen":
            self.d["chat"] = {**self.d["chat"], "werkzeuge": "fragen"}       # beim Start immer „fragen“

    def speichern(self) -> None:
        tmp = self.pfad + ".tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({**self.d, "chat": {**(self.d.get("chat") or {}), "werkzeuge": "fragen"}}, fh, ensure_ascii=False, indent=1)     # „automatisch“ nie auf die Platte
        os.replace(tmp, self.pfad)
        os.chmod(self.pfad, 0o600)

    def __getitem__(self, k): return self.d[k]

    def setze(self, k, v) -> None:
        self.d[k] = v
        self.speichern()

    # ---- Einwilligungen: wer darf welchen Umfang an Text bekommen ---------------------------------------------------
    def einwilligungen(self) -> list[dict]:
        """[{anbieter, umfang, seit}]; ältere Einträge (nur der Name) gelten als Umfang „dokument“, wie damals gefragt wurde."""
        r = []
        for e in self.d.get("einwilligungen") or []:
            if isinstance(e, str):
                e = {"anbieter": e, "umfang": "dokument", "seit": ""}
            if isinstance(e, dict) and e.get("anbieter") and e.get("umfang") in UMFAENGE:
                r.append({"anbieter": str(e["anbieter"]), "umfang": e["umfang"], "seit": str(e.get("seit", ""))})
        return r

    def hat_einwilligung(self, anbieter: str, umfang: str = "auszug") -> bool:
        """„dokument“ schließt „auszug“ ein, nicht umgekehrt; „bild“ wird von keinem anderen Umfang abgedeckt."""
        gebraucht = {umfang} if umfang in ("dokument", "bild", "dauer") else {"auszug", "dokument"}      # „bild“ steht für sich
        return any(e["anbieter"] == anbieter and e["umfang"] in gebraucht for e in self.einwilligungen())

    def einwilligung_geben(self, anbieter: str, umfang: str) -> None:
        import time
        rest = [e for e in self.einwilligungen() if not (e["anbieter"] == anbieter and e["umfang"] == umfang)]
        self.setze("einwilligungen", rest + [{"anbieter": anbieter, "umfang": umfang, "seit": time.strftime("%Y-%m-%d")}])

    def einwilligung_widerrufen(self, anbieter: str | None = None, umfang: str | None = None) -> None:
        """Ohne Angaben: alle. Mit ``anbieter`` (und ``umfang``): nur diese."""
        def trifft(e: dict) -> bool:
            return anbieter is None or (e["anbieter"] == anbieter and (umfang is None or e["umfang"] == umfang))
        self.setze("einwilligungen", [e for e in self.einwilligungen() if not trifft(e)])

    def anbieter_holen(self, id_: str):
        return next((a for a in self.d["anbieter"] if a["id"] == id_), None)

    def anbieter_hinzufuegen(self, name, url, schluessel, modell, verwendung=None) -> dict:
        import uuid
        e = {"id": "p" + uuid.uuid4().hex[:8]}
        self.d["anbieter"].append(e)
        return self.anbieter_aktualisieren(e["id"], name, url, schluessel, modell, verwendung)

    def anbieter_aktualisieren(self, id_, name, url, schluessel, modell, verwendung=None) -> dict | None:
        e = self.anbieter_holen(id_)
        if e is None:
            return None
        gueltig = {k for k, _ in ANBIETER_TAGS}
        e.update(name=(name or "").strip()[:60] or "Eigenes Modell", url=(url or "").strip().rstrip("/"),
                 schluessel=(schluessel or "").strip(), modell=(modell or "").strip(),
                 verwendungFuer=[t for t in (verwendung if verwendung is not None else e.get("verwendungFuer", ["text"])) if t in gueltig])
        self.speichern()
        return e

    def chat_optionen(self) -> dict:
        """Die erweiterten Einstellungen des KI-Chats (Länge, Temperatur, Top P, Stoppfolgen, Antwort direkt einfügen) mit ihren Vorgaben."""
        return {**CHAT_VORGABE, **(self.d.get("chat") or {})}

    def websuche_optionen(self) -> dict:
        from lunivo_writer.ki import websuche as W
        return {**W.VORGABE, **(self.d.get("websuche") or {})}

    def dokumentsuche_optionen(self) -> dict:
        """Lokale Dokumentensuche: ``an``, freigegebene ``ordner`` (nur existierende, absolut), ``anzahl`` der Abschnitte je Frage."""
        from lunivo_writer.ki import dokumentensuche as DS
        o = {**DS.VORGABE, **(self.d.get("dokumentsuche") or {})}
        o["ordner"] = [p for p in (o.get("ordner") or []) if isinstance(p, str) and os.path.isabs(p)]
        o["anzahl"] = max(1, min(10, int(o.get("anzahl") or DS.VORGABE["anzahl"])))
        return o

    def dokumentsuche_setzen(self, **teile) -> None:
        self.d["dokumentsuche"] = {**(self.d.get("dokumentsuche") or {}), **teile}
        self.speichern()

    def dokumentindex_pfad(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(self.pfad)), "dokumentindex.sqlite")

    def websuche_setzen(self, **teile) -> None:
        self.d["websuche"] = {**(self.d.get("websuche") or {}), **teile}
        self.speichern()

    def mcp_speichern(self, id_: str | None, name: str, befehl: str, an: bool = True) -> dict:
        """MCP-Server anlegen (``id_`` None) oder ändern."""
        import uuid
        e = next((m for m in self.d["mcp"] if m["id"] == id_), None) if id_ else None
        if e is None:
            e = {"id": "m" + uuid.uuid4().hex[:8]}
            self.d["mcp"].append(e)
        e.update(name=(name or "").strip()[:60] or "KI-Werkzeug", befehl=(befehl or "").strip(), an=bool(an))
        self.speichern()
        return e

    SUCHDIENST_NAME = "Lunivo Dokumentensuche"

    def suchdienst_eintragen(self) -> dict:
        """Die Dokumentensuche als KI-Werkzeug (MCP-Server ``ki/suchdienst.py``) eintragen oder aktualisieren — mit den jetzt freigegebenen Ordnern.
        Der Server bekommt nur diese Ordner und den Index; jeder Aufruf wird im Chat weiterhin einzeln abgefragt."""
        import shlex
        import sys
        from lunivo_writer.ki import suchdienst
        ordner = self.dokumentsuche_optionen()["ordner"]
        befehl = shlex.join([sys.executable, os.path.abspath(suchdienst.__file__), "--index", self.dokumentindex_pfad(),
                             *[a for o in ordner for a in ("--ordner", o)]])
        alt = next((m for m in self.d["mcp"] if m.get("name") == self.SUCHDIENST_NAME), None)
        return self.mcp_speichern(alt["id"] if alt else None, self.SUCHDIENST_NAME, befehl, True)

    def mcp_entfernen(self, id_: str) -> None:
        self.d["mcp"] = [m for m in self.d["mcp"] if m["id"] != id_]
        self.speichern()

    def chat_setzen(self, **teile) -> None:
        self.d["chat"] = {**(self.d.get("chat") or {}), **teile}
        self.speichern()

    def aufgabe_setzen(self, aufgabe: str, modell: str) -> None:
        if modell:
            self.d["aufgaben"][aufgabe] = modell
        else:
            self.d["aufgaben"].pop(aufgabe, None)
        self.speichern()

    def assistent_hinzufuegen(self, name: str, prompt: str, modus: str, zugriff: str = "kontext", **mehr) -> dict:
        """Eine „Schnelle KI-Aktion“ (art „aktion“): ``modus`` = ersetzen | anhaengen | hinweis; ``zugriff`` = kontext (Rechtsklick-Menü) | schnell
        (Schnellzugriffsleiste). Mit ``art="fortlaufend"`` ein fortlaufender Assistent; ``mehr`` setzt die Zusatzfelder (siehe ``assistent_normiert``)."""
        import uuid
        e = {"id": "a" + uuid.uuid4().hex[:8], "name": name, "prompt": prompt, "modus": modus, "zugriff": zugriff, **mehr}
        e = assistent_normiert(e)
        self.d["assistenten"].append(e)
        self.speichern()
        return e

    def assistent_holen(self, id_: str) -> dict | None:
        return next((a for a in self.d["assistenten"] if a.get("id") == id_), None)

    def assistent_aendern(self, id_: str, **teile) -> dict | None:
        """Felder eines Assistenten ändern (der Eintrag bleibt dasselbe Objekt, Werte werden geprüft)."""
        e = self.assistent_holen(id_)
        if e is None:
            return None
        e.update(assistent_normiert({**e, **teile}))
        self.speichern()
        return e

    def assistenten(self, art: str | None = None) -> list[dict]:
        """Alle Assistenten (``art`` None) oder nur die einer Art; ältere Einträge ohne Art gelten als „aktion“."""
        return [a for a in self.d["assistenten"] if art is None or a.get("art", "aktion") == art]

    def assistent_entfernen(self, id_: str) -> None:
        self.d["assistenten"] = [a for a in self.d["assistenten"] if a["id"] != id_]
        self.speichern()

    def anbieter_entfernen(self, id_: str) -> None:
        self.d["anbieter"] = [a for a in self.d["anbieter"] if a["id"] != id_]
        for aufgabe, m in list(self.d["aufgaben"].items()):      # eine Zuweisung auf den gelöschten Anbieter fällt auf „Standard“
            if m == EIGEN_MARKE + id_:
                del self.d["aufgaben"][aufgabe]
        self.speichern()

    def alle_modelle(self) -> list[dict]:
        """Eine Liste für alle Felder „welches Modell?“: Claude, eigene Anbieter (mit Fähigkeiten und ‚lokal‘)."""
        r = [{"id": m, "name": n, "lokal": False, "verwendungFuer": ["text"]} for m, n in MODELLE_FEST]
        for a in self.d["anbieter"]:
            r.append({"id": EIGEN_MARKE + a["id"], "name": f"{a['name']} ({a['modell']})", "lokal": ist_lokale_url(a["url"]),
                      "verwendungFuer": a.get("verwendungFuer", [])})
        r.append({"id": ARGOS_MARKE, "name": "Lokal (offline) · Argos", "lokal": True, "verwendungFuer": ["uebersetzung"]})
        r.append({"id": AUTO_MARKE, "name": "Automatisch (KI, sonst lokal)", "lokal": False, "verwendungFuer": ["uebersetzung"]})
        return r

def ist_lokale_url(url: str) -> bool:
    """Nur der Rechner selbst: der Rechnername wird aus der Adresse gelesen (nicht per Muster), damit „http://127.0.0.1:80@fremd.de“ nicht durchgeht."""
    try:
        u = urllib.parse.urlparse(url or "")
        return u.scheme in ("http", "https") and u.hostname in ("localhost", "127.0.0.1", "::1")
    except ValueError:
        return False
