"""KI-Dienst der Oberfläche (Chat, Aktionen, fortlaufende Assistenten): ordnet die Bedienung dem KI-Dienst des Frameworks zu.

Die Oberfläche holt hier die Dienstobjekte (Konfiguration, KI, Chatverlauf, Drossel), die Regeln des Chat-Bezugs und der Assistenten sowie die
Marken und Meldungstexte. Die Fachlogik bleibt im Framework (``framework.ki``)."""
from __future__ import annotations

from collections.abc import Mapping

from framework.ki import anbieter as _anbieter, chat as _chat, dienst as _dienst
from writer.werte import unveraenderlich

# ---- Marken der Modelle, Textaktionen, Meldungen (als unveränderliche Werte, nie die Objekte des Frameworks) ------------------------


def ollama_marke() -> str:
    """Vorsilbe der Modelle, die Ollama auf diesem Rechner ausführt."""
    return str(_dienst.OLLAMA_MARKE)


def eigen_marke() -> str:
    """Vorsilbe der Modelle eigener Anbieter."""
    return str(_dienst.EIGEN_MARKE)


def auto_marke() -> str:
    """Vorsilbe der automatischen Modellwahl."""
    return str(_dienst.AUTO_MARKE)


def text_aktionen() -> tuple[tuple[str, str], ...]:
    """(Schlüssel, Name) der Textaktionen."""
    return unveraenderlich(_dienst.TEXT_AKTIONEN)


def mindestabstand() -> float:
    """Sekunden zwischen zwei Anfragen fortlaufender Assistenten."""
    return float(_dienst.MINDESTABSTAND)


def denkstufen() -> Mapping[str, Mapping[str, str]]:
    return unveraenderlich(_anbieter.DENKSTUFEN)


def werkzeug_modi() -> tuple[str, ...]:
    return unveraenderlich(_anbieter.WERKZEUG_MODI)


_MELDUNGEN = {"editor": "MELDUNG_EDITOR", "geaendert": "MELDUNG_GEAENDERT", "keine_rezension": "MELDUNG_KEINE_REZENSION",
              "kein_bezug": "MELDUNG_KEIN_BEZUG", "ohne_markierung": "MELDUNG_OHNE_MARKIERUNG", "ohne_verfolgung": "MELDUNG_OHNE_VERFOLGUNG",
              "rezension": "MELDUNG_REZENSION"}


def chat_meldung(art: str) -> str:
    """Meldungstext zum Übernehmen einer Chat-Antwort: ``editor``, ``geaendert``, ``keine_rezension``, ``kein_bezug``, ``ohne_markierung``,
    ``ohne_verfolgung`` oder ``rezension``."""
    return str(getattr(_chat, _MELDUNGEN[art]))


# ---- Dienstobjekte -------------------------------------------------------------------------------------------------------------------
def ki_konfiguration(pfad: str):
    """Die KI-Einstellungen aus der Datei ``pfad`` (``KIKonfig`` des Frameworks)."""
    return _dienst.KIKonfig(pfad)


def ki_anbinden(konfig, gelernt: dict | None = None):
    """Der KI-Dienst des Frameworks für diese Einstellungen (``KI``)."""
    return _dienst.KI(konfig, gelernt)


def chat_verlauf():
    """Ein leerer Chatverlauf (``ChatModell``)."""
    return _chat.ChatModell()


def assistenten_drossel():
    """Mindestabstand und Höchstzahl je Stunde für fortlaufende Assistenten (``Drossel``)."""
    return _dienst.Drossel()


# ---- Geld, Ersetzen ------------------------------------------------------------------------------------------------------------------
def als_geld(cent) -> str:
    return _dienst.als_geld(cent)


def ersetze_ergebnis(alt: str, neu: str):
    """→ (Ersetzungen (von, bis, Text) von hinten nach vorn, ganz, Absätze)."""
    return _dienst.ersetze_ergebnis(alt, neu)


# ---- Chat-Bezug: Antwort und Stelle im Text ----------------------------------------------------------------------------------------------
def bezug_bauen(von: int, bis: int, markiert: bool, revision: int, alt: str, kennung: int, ganz: str = "") -> dict:
    return _chat.bezug_bauen(von, bis, markiert, revision, alt, kennung, ganz)


def bezug_angewendet() -> dict:
    return _chat.bezug_angewendet()


def bezug_pruefen(bezug: dict | None, revision_jetzt: int | None, kennung_jetzt: int | None) -> tuple[bool, str]:
    return _chat.bezug_pruefen(bezug, revision_jetzt, kennung_jetzt)


def ersetz_schritte(alt: str, neu: str) -> list[tuple[int, int, str]] | None:
    return _chat.ersetz_schritte(alt, neu)


def vorher_der_nachricht(nachricht: dict, bezug: dict | None) -> str:
    return _chat.vorher_der_nachricht(nachricht, bezug)


def vorschau_der_nachricht(nachricht: dict, bezug: dict | None) -> list[tuple[str, str]] | None:
    return _chat.vorschau_der_nachricht(nachricht, bezug)


def vorschau_einfuegen(neu: str) -> list[tuple[str, str]]:
    return _chat.vorschau_einfuegen(neu)


def vorschau_stuecke(alt: str, neu: str) -> list[tuple[str, str]]:
    return _chat.vorschau_stuecke(alt, neu)


def kern_von(nachricht: dict) -> str:
    """Der Kern einer Chat-Antwort (ohne Vorrede und Hinweise)."""
    return _chat.kern_von(nachricht)


def chat_vorschlaege(auswahl: bool, leer: bool, konfig=None) -> list[dict]:
    return _chat.chat_vorschlaege_chat_vorschlaege(auswahl, leer, konfig)


# ---- Modellfähigkeiten ---------------------------------------------------------------------------------------------------------------
def bild_pruefen(pfad) -> dict:
    return _anbieter.bild_pruefen(pfad)


def denkstufe(schluessel) -> str:
    return _anbieter.denkstufe(schluessel)


# ---- Fortlaufende Assistenten -------------------------------------------------------------------------------------------------------------
def verzoegerung_begrenzen(wert) -> float:
    return _dienst.verzoegerung_begrenzen(wert)


def absatz_geaendert(zuletzt: str | None, jetzt: str) -> bool:
    return _dienst.absatz_geaendert(zuletzt, jetzt)


def eingabe_kuerzen(text: str) -> str:
    return _dienst.eingabe_kuerzen(text)


def ergebnis_wirkt(alt: str, neu: str) -> bool:
    return _dienst.ergebnis_wirkt(alt, neu)


def trenne_begruendung(text: str) -> tuple[str, str]:
    return _dienst.trenne_begruendung(text)
