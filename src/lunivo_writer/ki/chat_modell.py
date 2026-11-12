"""Zustand des KI-Chats ohne Oberfläche: Nachrichten, Phase, Anfragekennung, Gesprächsliste. Schicht 1 — kennt weder Dienst noch Qt."""
from __future__ import annotations

from lunivo_writer.ki import chat_antwort as CA

MAX_GESPRAECHE = 20          # so viele frühere Gespräche merkt sich „Verlauf“ (nur im Speicher)
TITEL_LAENGE = 40
PHASEN = ("leer", "laufend", "fehler", "bereit")


def fehler_objekt(text: str) -> dict:
    """Aus einer Fehlermeldung des Dienstes {titel, art, text}; ``art`` steuert die Darstellung."""
    t = text.lower()
    if "zustimmung" in t:
        art, titel = "zustimmung", "Keine Zustimmung"
    elif "schlüssel" in t or "modell" in t:
        art, titel = "konfiguration", "KI nicht eingerichtet"
    else:
        art, titel = "fehler", "Keine Antwort"
    return {"titel": titel, "art": art, "text": text}


def gespraechstitel(text: str) -> str:
    z = " ".join(text.split())
    return z if len(z) <= TITEL_LAENGE else z[:TITEL_LAENGE - 1].rstrip() + "…"


class ChatModell:
    def __init__(self) -> None:
        self.nachrichten: list[dict] = []        # {rolle: "mensch"|"ki", nr (fortlaufende Kennung; ältere ohne), text, cent, fehler: dict|None, bilder: [{pfad, typ, bytes}], bezug: dict|None (nur KI, nur im Speicher; siehe chat_bezug); nur KI: einleitung/kern/erklaerung (siehe chat_antwort; ältere Nachrichten ohne), notiz/kuerzung/fundstellen (Hinweise, optional)}
        self.gespraeche: list[dict] = []         # frühere Gespräche, neuestes zuerst: {titel, nachrichten}
        self._offen: int | None = None           # Kennung der Anfrage, auf die noch gewartet wird
        self._zaehler = 0
        self._nr = 0                             # fortlaufende Kennung der Nachrichten (``nr``); der Index ist nicht stabil
        self.teil = ""                           # bisher eingetroffener Antworttext der laufenden Anfrage (Streaming), nur im Speicher
        self._bezug_offen: dict | None = None    # Bezug (Stelle im Text) der laufenden Anfrage; nur im Speicher
        self.wiederhol_bilder: list[dict] = []   # Anhang der Nachricht, die ``wiederholen()`` zuletzt herausgenommen hat

    # ---- Zustand
    @property
    def phase(self) -> str:
        if self._offen is not None:
            return "laufend"
        if not self.nachrichten:
            return "leer"
        return "fehler" if self.nachrichten[-1].get("fehler") else "bereit"

    @property
    def titel(self) -> str:
        for n in self.nachrichten:
            if n["rolle"] == "mensch":
                return gespraechstitel(n["text"])
        return ""

    def verlauf(self) -> list[dict]:
        """Was an die KI geht: ohne Fehler, im Format des Dienstes."""
        return [{"rolle": n["rolle"], "text": n["text"], **({"bilder": n["bilder"]} if n.get("bilder") else {})}
                for n in self.nachrichten if not n.get("fehler")]

    # ---- Änderungen
    def _neu(self, rolle: str, text: str, cent=None, fehler: dict | None = None, bilder: list | None = None, bezug: dict | None = None) -> dict:
        self._nr += 1
        n = {"rolle": rolle, "text": text, "cent": cent, "fehler": fehler, "nr": self._nr}
        if bezug:
            n["bezug"] = bezug
        if bilder:
            n["bilder"] = [dict(b) for b in bilder]
        self.nachrichten.append(n)
        return n

    def anfrage(self, text: str, bilder: list | None = None, bezug: dict | None = None) -> int:
        """Nutzernachricht (mit geprüften Bildanhängen {pfad, typ, bytes}) aufnehmen und eine Anfrage beginnen; liefert deren Kennung."""
        self._neu("mensch", text, bilder=bilder)
        return self.beginnen(bezug)

    def beginnen(self, bezug: dict | None = None) -> int:
        self._bezug_offen = bezug
        self.teil = ""
        self._zaehler += 1
        self._offen = self._zaehler
        return self._offen

    def teil_setzen(self, kennung: int, text: str) -> bool:
        """Zwischenstand der Antwort; veraltete Anfragen werden verworfen."""
        if kennung != self._offen:
            return False
        self.teil = text
        return True

    def antwort(self, kennung: int, text: str, cent=None, zusatz: dict | None = None) -> bool:
        if kennung != self._offen:
            return False                      # veraltet (neues Gespräch, Abbruch, Wiederholung)
        self._offen = None
        self.teil = ""
        bezug, self._bezug_offen = self._bezug_offen, None
        self._neu("ki", text, cent, bezug=bezug).update(CA.felder(text), **(zusatz or {}))
        return True

    def fehler(self, kennung: int, text: str) -> bool:
        if kennung != self._offen:
            return False
        self._offen = None
        self.teil = ""
        self._neu("ki", text, None, fehler_objekt(text))
        return True

    def aktion(self, name: str, text: str, cent=None, bezug: dict | None = None) -> None:
        """Ergebnis einer Schnellen KI-Aktion: Verlauf und Anzeige führen dieselben zwei Nachrichten."""
        self._neu("mensch", f"Aktion „{name}“ auf den Text anwenden.")
        self._neu("ki", text, cent, bezug=bezug).update(CA.felder(text))

    def bezug_von(self, index: int) -> dict | None:
        """Bezug der KI-Nachricht ``index`` (None, wenn es keinen gibt)."""
        if not 0 <= index < len(self.nachrichten):
            return None
        n = self.nachrichten[index]
        return n.get("bezug") if n["rolle"] == "ki" and not n.get("fehler") else None

    def index_von_nr(self, nr: int | None) -> int | None:
        """Aktueller Platz der Nachricht mit Kennung ``nr`` (None, wenn sie nicht mehr im Gespräch ist; Nachrichten ohne Feld haben keine)."""
        if nr is None:
            return None
        for i, n in enumerate(self.nachrichten):
            if n.get("nr") == nr:
                return i
        return None

    def abbrechen(self) -> None:
        """Die Antwort der laufenden Anfrage wird nicht mehr angenommen."""
        self.teil = ""
        self._offen = None
        self._bezug_offen = None

    def wiederholen(self) -> str | None:
        """Letzte Nutzernachricht erneut senden: davor liegende Antwort/Fehler fällt weg. Liefert den Text oder None; danach ``beginnen()``."""
        self._offen = None
        self._bezug_offen = None
        self.wiederhol_bilder = []
        self.teil = ""
        while self.nachrichten and self.nachrichten[-1]["rolle"] != "mensch":
            self.nachrichten.pop()
        if not self.nachrichten:
            return None
        letzte = self.nachrichten.pop()
        self.wiederhol_bilder = letzte.get("bilder") or []
        return letzte["text"]

    def neues_gespraech(self) -> None:
        if self.nachrichten:
            self.gespraeche.insert(0, {"titel": self.titel or "Gespräch", "nachrichten": list(self.nachrichten)})
            del self.gespraeche[MAX_GESPRAECHE:]
        self.nachrichten = []
        self.wiederhol_bilder = []              # ein Anhang gehört zum Gespräch und fällt mit ihm weg
        self.teil = ""
        self._offen = None
        self._bezug_offen = None

    def gespraech_laden(self, index: int) -> bool:
        if not 0 <= index < len(self.gespraeche):
            return False
        eintrag = self.gespraeche.pop(index)
        self.neues_gespraech()
        self.nachrichten = list(eintrag["nachrichten"])
        return True
