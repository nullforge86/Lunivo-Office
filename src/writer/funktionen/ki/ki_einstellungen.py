"""KI-Einstellungen der Oberfläche (Optionen, Modelle, Aufgaben, Assistenten, Sprachen, Websuche, Dokumentsuche, MCP, Argos): ordnet die
Fenster dem KI-Dienst des Frameworks zu. Listen und Grenzwerte kommen als Werte, Prüfungen und Abrufe als Funktionen."""
from __future__ import annotations

from collections.abc import Mapping

from framework.ki import anbieter as _anbieter, dienst as _dienst, suche as _suche
from writer.funktionen.ki.werte import unveraenderlich


def argos_marke() -> str:
    """Vorsilbe der Übersetzung mit Argos (offline)."""
    return str(_dienst.ARGOS_MARKE)


def aufgaben() -> tuple[tuple[str, str], ...]:
    """(Schlüssel, Name) der KI-Aufgaben."""
    return unveraenderlich(_dienst.AUFGABEN)


def modelle_fest() -> tuple[tuple[str, str], ...]:
    """(Modell, Beschreibung) der festen Claude-Modelle."""
    return unveraenderlich(_dienst.MODELLE_FEST)


def anbieter_tags() -> tuple[tuple[str, str], ...]:
    """(Schlüssel, Name) der Fähigkeiten eines Anbieters."""
    return unveraenderlich(_dienst.ANBIETER_TAGS)


def anbieter_vorlagen() -> tuple[tuple[str, str, str], ...]:
    """(Schlüssel, Name, Adresse) bekannter Anbieter."""
    return unveraenderlich(_dienst.ANBIETER_VORLAGEN)


def sprachen() -> tuple[str, ...]:
    """Zielsprachen der Übersetzung."""
    return unveraenderlich(_dienst.SPRACHEN)


def umfaenge() -> Mapping[str, str]:
    """Was an einen Anbieter gehen darf (Schlüssel → Beschreibung)."""
    return unveraenderlich(_dienst.UMFAENGE)


def assistent_ausloeser() -> tuple:
    """Auslöser fortlaufender Assistenten."""
    return unveraenderlich(_dienst.ASSISTENT_AUSLOESER)


def assistent_umfaenge() -> tuple:
    """Umfänge fortlaufender Assistenten."""
    return unveraenderlich(_dienst.ASSISTENT_UMFAENGE)


def fortlaufend_modi() -> tuple:
    """Wirkungen fortlaufender Assistenten."""
    return unveraenderlich(_dienst.FORTLAUFEND_MODI)


def vorlagen_assistent() -> tuple:
    """Vorlagen eigener Assistenten (Name, Anweisung, Wirkung, Erklärung)."""
    return unveraenderlich(_dienst.VORLAGEN_ASSISTENT)


def verzoegerung_min() -> float:
    """Kürzeste Ruhe (Sekunden) vor einem fortlaufenden Assistenten."""
    return float(_dienst.VERZOEGERUNG_MIN)


def verzoegerung_max() -> float:
    """Längste Ruhe (Sekunden)."""
    return float(_dienst.VERZOEGERUNG_MAX)


def verzoegerung_vorgabe() -> float:
    """Vorgabe der Ruhe (Sekunden)."""
    return float(_dienst.VERZOEGERUNG_VORGABE)


def keep_alive_max() -> int:
    """Höchste Haltezeit eines lokalen Modells (Minuten)."""
    return int(_anbieter.KEEP_ALIVE_MAX)


def num_ctx_stufen() -> tuple:
    """Stufen des Kontextfensters eines lokalen Modells."""
    return unveraenderlich(_anbieter.NUM_CTX_STUFEN)


def websuche_anbieter() -> tuple[tuple[str, str], ...]:
    """(Schlüssel, Name) der Anbieter der Websuche."""
    return unveraenderlich(_suche.ANBIETER)


def ist_lokale_url(url: str) -> bool:
    return _dienst.ist_lokale_url(url)


def anbieter_modelle(url: str, schluessel: str = "") -> list[str]:
    """Die Modelle, die ein Anbieter unter ``url`` meldet (Netz)."""
    return _dienst.anbieter_modelle(url, schluessel)


def keep_alive_begrenzen(wert) -> int:
    return _anbieter.keep_alive_begrenzen(wert)


def num_ctx_begrenzen(wert) -> int:
    return _anbieter.num_ctx_begrenzen(wert)


def num_thread_begrenzen(wert) -> int:
    return _anbieter.num_thread_begrenzen(wert)


def mcp_pruefen(befehl: str) -> tuple[tuple[str, ...], str]:
    """Startet den MCP-Server ``befehl`` zur Probe. → (Namen seiner Werkzeuge, Fehlertext); der Fehlertext ist leer, wenn er erreichbar ist."""
    try:
        return tuple(str(w["name"]) for w in _anbieter.pruefen(befehl)), ""
    except _anbieter.McpFehler as e:
        return (), str(e)


def argos_installierte_richtungen() -> list[dict]:
    return _anbieter.installierte_richtungen()


def argos_verfuegbare_richtungen() -> dict:
    return _anbieter.verfuegbare_richtungen()


def argos_richtung_installieren(von: str, nach: str) -> dict:
    return _anbieter.richtung_installieren(von, nach)


def websuche(einst: dict, frage: str, zeit: float = 15.0) -> list[dict]:
    return _suche.suche(einst, frage, zeit)


def dokumentindex_anzahl(pfad: str):
    """(Dokumente, Abschnitte) im Dokumentindex unter ``pfad``."""
    return _suche.Index(pfad).anzahl()


def dokumentindex_aktualisieren(pfad: str, ordner):
    """Den Dokumentindex unter ``pfad`` aus ``ordner`` neu aufbauen; → Bericht."""
    return _suche.Index(pfad).aktualisieren(ordner)
