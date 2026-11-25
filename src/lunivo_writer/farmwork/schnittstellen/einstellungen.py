"""Einstellungen für Oberfläche und Funktionen: dünne Hülle um den JSON-Speicher mit festen Lese- und Schreibfunktionen.

Die Oberfläche liest und ändert Einstellungen nur hierüber (und über ``funktionen/<name>/einstellungen.py``). Der Kern liest keine Einstellungen;
das Framework übergibt ihm die Werte als Parameter."""
from __future__ import annotations

import os

from lunivo_writer.plattform.einstellungen.speicher import JsonSpeicher, gemeinsamer_speicher
from lunivo_writer.plattform.pfade.pfade import ORGANISATION, PROGRAMM  # noqa: F401  (Namen des Programms für Oberfläche und Übernahme)

MAX_ZULETZT = 12
ERSTSTART_MARKE = "_qsettings_uebernommen"


class Einstellungen:
    def __init__(self, speicher: JsonSpeicher | None = None):
        self.speicher = speicher or gemeinsamer_speicher()

    # Werte
    def get(self, key: str, default=None):
        return self.speicher.lesen(key, default)

    def set(self, key: str, value) -> None:
        self.speicher.schreiben(key, value)

    def remove(self, key: str) -> None:
        self.speicher.entfernen(key)

    def get_bool(self, key: str, default: bool) -> bool:
        v = self.speicher.lesen(key, default)
        return v if isinstance(v, bool) else str(v).lower() in ("1", "true", "yes")

    def get_int(self, key: str, default: int) -> int:
        try:
            return int(self.speicher.lesen(key, default))
        except (TypeError, ValueError):
            return default

    # Zuletzt verwendete Dokumente
    def recent(self) -> list[str]:
        v = self.speicher.lesen("recent", [])
        if isinstance(v, str):
            v = [v]
        return [p for p in (v or []) if isinstance(p, str)]

    def add_recent(self, path: str) -> None:
        path = os.path.abspath(path)
        items = [p for p in self.recent() if p != path]
        items.insert(0, path)
        self.set("recent", items[:MAX_ZULETZT])

    def remove_recent(self, path: str) -> None:
        self.set("recent", [p for p in self.recent() if p != path])

    def clear_recent(self) -> None:
        self.set("recent", [])

    # Einmalige Übernahme der früheren QSettings-Werte (die Oberfläche liest sie und übergibt sie hierher)
    def qsettings_uebernommen(self) -> bool:
        return bool(self.speicher.lesen(ERSTSTART_MARKE, False))

    def uebernehmen(self, werte: dict) -> None:
        """Übernimmt die alten Werte, ohne vorhandene neue Werte zu überschreiben, und setzt die Marke (danach wird QSettings nie mehr gelesen)."""
        neu = {k: v for k, v in werte.items() if k not in self.speicher.schluessel()}
        neu[ERSTSTART_MARKE] = True
        self.speicher.mehrere_schreiben(neu)
