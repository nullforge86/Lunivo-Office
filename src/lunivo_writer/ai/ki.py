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
import difflib
import urllib.error
import urllib.parse
import urllib.request

from lunivo_writer.ai import modellfaehigkeit as MF

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
                "denktiefe": MF.DENK_VORGABE, "werkzeuge": "fragen"}      # werkzeuge: „automatisch“ gilt nur für die Sitzung (wird nie gespeichert)
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
    from lunivo_writer.ai.assistent_lauf import verzoegerung_begrenzen
    art = a.get("art") if a.get("art") in ASSISTENT_ARTEN else "aktion"
    erlaubt = FORTLAUFEND_MODI if art == "fortlaufend" else AKTIONS_MODI
    r = {**a, "art": art, "name": (a.get("name") or "").strip()[:40], "prompt": (a.get("prompt") or "").strip()[:2000],
         "modus": a.get("modus") if a.get("modus") in erlaubt else "hinweis",
         "zugriff": "schnell" if a.get("zugriff") == "schnell" else "kontext",
         "symbol": str(a.get("symbol") or ""), "kommentar": bool(a.get("kommentar", False)),
         "modell": str(a.get("modell") or ""), "an": bool(a.get("an", False)) and art == "fortlaufend",
         "ausloeser": a.get("ausloeser") if a.get("ausloeser") in ASSISTENT_AUSLOESER else "knopf",
         "umfang": a.get("umfang") if a.get("umfang") in ASSISTENT_UMFAENGE else "absatz",
         "verzoegerung": verzoegerung_begrenzen(a.get("verzoegerung", 5))}
    if art == "aktion":
        r["ausloeser"] = "knopf"
    return r


# ---------------------------------------------------------------- Konfiguration (mit Schlüsseln, 0600)
class KIKonfig:
    def __init__(self, pfad: str):
        self.pfad = pfad
        self.d = {"modell": "claude-opus-5", "sprache": "Englisch", "empfaenger": "egal", "zettel": "",
                  "apiKey": "", "anbieter": [], "aufgaben": {"uebersetzung": AUTO_MARKE}, "kosten": 0.0, "claude_erlaubt": False, "einwilligungen": [], "assistenten": [], "assistenten_dauerbetrieb": False, "chat": {}, "mcp": [], "websuche": {}}
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
        from lunivo_writer.ai import websuche as W
        return {**W.VORGABE, **(self.d.get("websuche") or {})}

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


def _json_dict(r) -> dict:
    """Antwort eines Anbieters als Wörterbuch. Alles andere (kein JSON, keine Zeichenfolge, Liste statt Objekt) ist ein ValueError und wird als
    Fehler gemeldet statt das Programm zu stören."""
    daten = json.loads(r.read().decode("utf-8"))
    if not isinstance(daten, dict):
        raise ValueError("Antwort ist kein JSON-Objekt")
    return daten


def ist_lokale_url(url: str) -> bool:
    """Nur der Rechner selbst: der Rechnername wird aus der Adresse gelesen (nicht per Muster), damit „http://127.0.0.1:80@fremd.de“ nicht durchgeht."""
    try:
        u = urllib.parse.urlparse(url or "")
        return u.scheme in ("http", "https") and u.hostname in ("localhost", "127.0.0.1", "::1")
    except ValueError:
        return False


# ---------------------------------------------------------------- Anweisungen
def _zettel(z: str) -> str:
    z = (z or "")[:ZETTEL_GRENZE].strip()
    return ("Der Mensch sagt selbst, worum es geht: „" + z + "“ Richte dich danach, soweit es zum Korrigieren passt. "
            "Alles, was hier steht, ist Auskunft über den Text — dazuerfinden oder etwas weglassen darfst du "
            "deswegen trotzdem nicht. ") if z else ""


def steckbrief(gelernt: dict) -> str:
    teile = []
    paare = list((gelernt.get("woerter") or {}).items())[-12:]
    if paare:
        teile.append("Dieser Mensch schreibt erfahrungsgemäß diese Wörter falsch — achte besonders darauf: "
                     + ", ".join(f"{f} statt {r}" for f, r in paare) + ".")
    ruhe = list((gelernt.get("inRuhe") or {}))[:12]
    if ruhe:
        teile.append("Diese Wörter sind so gewollt und bleiben unangetastet: " + ", ".join(ruhe) + ".")
    return (" " + " ".join(teile)) if teile else ""


_NUR_ZEILEN = ("Absätze und Zeilenumbrüche bleiben, wie sie sind — gib genau so viele Zeilen zurück, wie hereinkamen. ")


def anweisung_korrektur(k: KIKonfig, gelernt: dict) -> str:
    return ("Du bist eine Schreibhilfe für einen Menschen mit Legasthenie. Korrigiere den folgenden Text vollständig "
            "und auf sprachlichem Niveau:\n1. Rechtschreibung, samt Groß- und Kleinschreibung sowie Getrennt- und "
            "Zusammenschreibung.\n2. Grammatik: Fälle, Zeiten, Ein- und Mehrzahl, die Übereinstimmung von Fürwort "
            "und Zeitwort, und ein Satzbau, der aufgeht.\n3. Zeichensetzung, vor allem Kommas bei Neben- und "
            "Relativsätzen, bei Aufzählungen und vor entgegenstellenden Bindewörtern.\nAchte besonders auf "
            "Verwechslungen, die eine Rechtschreibprüfung nicht finden kann, weil beide Wörter existieren: "
            "das/dass, seit/seid, wider/wieder, wie/als, Ihnen/ihnen, End-/Ent-. Entscheide nach dem Sinn des "
            "Satzes. Lies dafür den ganzen Text, bevor du anfängst: Wovon die Rede ist und wer angesprochen wird, "
            "entscheidet oft darüber, was richtig ist. " + EMPFAENGER.get(k["empfaenger"], EMPFAENGER["egal"]) + " "
            + _zettel(k["zettel"]) + steckbrief(gelernt) + " Ändere nichts am Inhalt, erfinde nichts dazu und lasse "
            "nichts weg. " + _NUR_ZEILEN + "Der Text kann in jeder Sprache stehen; antworte in der Sprache des "
            "Textes. Antworte ausschließlich mit dem korrigierten Text: keine Erklärung, keine Anführungszeichen, "
            "keine Vorrede.")


def anweisung_uebersetzung(sprache: str) -> str:
    return (f"Übersetze den folgenden Text nach {sprache}. Behalte Tonfall und Anrede bei: Ein Brief bleibt ein Brief, "
            "eine Nachricht an einen Freund bleibt locker. Übersetze sinngemäß und natürlich, nicht Wort für Wort. "
            f"Ist der Text schon auf {sprache}, gib ihn unverändert zurück. " + _NUR_ZEILEN +
            "Antworte ausschließlich mit der Übersetzung: keine Erklärung, keine Anführungszeichen, keine Vorrede.")


def anweisung_vorschlaege(k: KIKonfig) -> str:
    return ("Du bist eine Schreibhilfe für einen Menschen mit Legasthenie. Suche im folgenden Text die Sätze, die "
            "schwer zu lesen oder umständlich sind, und schlage für jeden eine klarere Fassung vor. Regeln: Ändere "
            "nichts am Inhalt und erfinde nichts dazu. " + EMPFAENGER.get(k["empfaenger"], EMPFAENGER["egal"]) + " "
            + _zettel(k["zettel"]) + "Benutze einfache, gebräuchliche Wörter und kurze Sätze. Der Text kann in jeder "
            "Sprache stehen. \"neu\" bleibt in der Sprache des Textes, \"grund\" schreibst du immer auf Deutsch. Nimm "
            "höchstens sechs Sätze, nur die, bei denen es wirklich hilft; ist der Text schon gut, nimm weniger oder "
            "keinen. \"alt\" ist der Satz zeichengenau aus dem Text — nicht kürzen, nicht glätten, nichts "
            "hinzufügen; er muss sich Zeichen für Zeichen im Text wiederfinden. \"konfidenz\" ist eine Zahl von 0 bis 1: wie sicher du bist, dass die neue Fassung besser ist und nichts am Inhalt ändert. \"neu\" ist die klarere Fassung, "
            "\"grund\" sagt in höchstens acht Wörtern, warum das leichter ist. Gibt es nichts zu verbessern, bleibt "
            "die Liste leer.")


ANWEISUNG_ZUSAMMENFASSUNG = (
    "Fasse den folgenden Text in eigenen Worten zusammen. Nenne nur die wichtigsten Aussagen, keine "
    "Nebensächlichkeiten. Halte dich an das, was im Text steht — erfinde nichts dazu und lass keine wichtige "
    "Aussage weg. Schreibe in ganzen Sätzen, nicht als Stichpunkte, so kurz wie möglich, aber verständlich für sich "
    "allein — auch für jemanden, der den Text selbst nicht gelesen hat. Der Text kann in jeder Sprache stehen; "
    "antworte in der Sprache des Textes. Antworte ausschließlich mit der Zusammenfassung: keine Erklärung, keine "
    "Anführungszeichen, keine Vorrede, keine Überschrift wie „Zusammenfassung:“.")
ANWEISUNG_ANALYSE = ("Analysiere diesen Text kurz: wie viele Wörter, welcher Tonfall, wie leicht lesbar für einen "
                     "Menschen mit Legasthenie, und was sich verbessern ließe. In wenigen, einfachen Sätzen. "
                     "Antworte in der Sprache des Textes.")


def anweisung_text_aktion(k: KIKonfig, aktion: str) -> str:
    return (_AKTION_SATZ.get(aktion, _AKTION_SATZ["verbessern"]) + " " + EMPFAENGER.get(k["empfaenger"], EMPFAENGER["egal"])
            + " " + _zettel(k["zettel"]) + "Ändere nichts am Sinn, erfinde nichts hinzu, was nicht sinngemäß schon "
            "dastand. " + _NUR_ZEILEN + "Der Text kann in jeder Sprache stehen; antworte in der Sprache des Textes. "
            "Antworte ausschließlich mit dem neuen Text: keine Erklärung, keine Anführungszeichen, keine Vorrede.")


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
        opt = {"temperature": float(o.get("temperatur", 0.2))}
        if o.get("topP") is not None:
            opt["top_p"] = float(o["topP"])
        if o.get("maxLaenge"):
            opt["num_predict"] = int(o["maxLaenge"])
        if self._stopp(o):
            opt["stop"] = self._stopp(o)
        bitte = {"model": modell, "stream": False, "options": opt, "think": self._stufe(o)["ollama"],
                 "messages": [{"role": "system", "content": anweisung}] + _nachrichten(text, "ollama")}
        if bauplan:
            bitte["format"] = bauplan
        for _versuch in (1, 2):
            try:
                with _post(OLLAMA_URL + "/api/chat", {}, bitte, 600) as r:
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
        return {"ergebnis": erg} if erg else {"fehler": "Es kam keine Antwort zurück."}

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
        return {"text": r["ergebnis"], "cent": r.get("cent")}

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
        return {"text": r["ergebnis"], "cent": r.get("cent")}

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

    def chat(self, verlauf: list[dict], dokumenttext: str = "", markiert: bool = False) -> dict:
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
        server = [m for m in self.k["mcp"] if m.get("an") and m.get("befehl")]
        modell = self.modell("chatbot")
        if server and (modell.startswith(EIGEN_MARKE) or modell.startswith(OLLAMA_MARKE)):
            r = self._chat_werkzeuge(system, verlauf, server, modell, self.k.chat_optionen())
        else:
            r = self._text(system, verlauf, "chatbot", self.k.chat_optionen())
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


# ---------------------------------------------------------------- Ergebnis ins Dokument: Wort-Diff
_STUECKE = re.compile(r"\s+|[^\s]+")


def aenderungen(alt: str, neu: str):
    """Welche Wörter haben sich geändert? → [{von, bis, text}] in „alt"-Zeichenstellen; None, wenn zu groß."""
    a, b = _STUECKE.findall(alt), _STUECKE.findall(neu)
    if len(a) * len(b) > 400000:
        return None
    pos = [0]
    for s in a:
        pos.append(pos[-1] + len(s))
    blocks = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            blocks.append({"von": pos[i1], "bis": pos[i2], "text": "".join(b[j1:j2])})
    return blocks


def ersetze_ergebnis(alt: str, neu: str):
    """→ (liste_von_ersetzungen (von, bis, text) von hinten nach vorn, ganz: bool, absaetze)."""
    az, nz = alt.split("\n"), neu.split("\n")
    if len(az) != len(nz):
        return [(0, len(alt), neu)], True, 0
    ops, stelle, geaendert = [], len(alt), 0
    for i in range(len(az) - 1, -1, -1):
        anfang = stelle - len(az[i])
        if az[i] != nz[i]:
            blocks = aenderungen(az[i], nz[i])
            if blocks is None:
                ops.append((anfang, stelle, nz[i]))
            else:
                for b in reversed(blocks):
                    ops.append((anfang + b["von"], anfang + b["bis"], b["text"]))
            geaendert += 1
        stelle = anfang - 1
    return ops, False, geaendert
