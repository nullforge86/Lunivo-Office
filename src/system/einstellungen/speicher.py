"""JSON-Speicher der Einstellungen: eine Datei ``$XDG_CONFIG_HOME/lunivo/einstellungen.json`` (Standard ``~/.config/lunivo/``).

Nur Lesen und Schreiben, kein Fachwissen: Schlüssel sind Zeichenketten wie ``"ui/weich"``, Werte alles, was JSON kennt (Wahrheitswerte, Zahlen,
Zeichenketten, Listen, Wörterbücher). Geschrieben wird atomar (Zwischendatei, dann Umbenennen)."""
from __future__ import annotations

import json
import os
import threading

from system.pfade import pfade

DATEINAME = "einstellungen.json"


def standarddatei() -> str:
    return os.path.join(pfade.config_dir(), DATEINAME)


class JsonSpeicher:
    def __init__(self, datei: str | None = None) -> None:
        self._datei = datei or standarddatei()
        self._sperre = threading.RLock()
        self._werte: dict = {}
        self._lesen()

    @property
    def datei(self) -> str:
        return self._datei

    def _lesen(self) -> None:
        try:
            with open(self._datei, encoding="utf-8") as f:
                daten = json.load(f)
            self._werte = daten if isinstance(daten, dict) else {}
        except (OSError, ValueError):
            self._werte = {}

    def _schreiben(self) -> None:
        os.makedirs(os.path.dirname(self._datei), exist_ok=True)
        zwischen = self._datei + ".tmp"
        with open(zwischen, "w", encoding="utf-8") as f:
            json.dump(self._werte, f, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(zwischen, self._datei)

    def vorhanden(self) -> bool:
        return os.path.exists(self._datei)

    def lesen(self, schluessel: str, vorgabe=None):
        with self._sperre:
            return self._werte.get(schluessel, vorgabe)

    def schreiben(self, schluessel: str, wert) -> None:
        with self._sperre:
            self._werte[schluessel] = wert
            self._schreiben()

    def entfernen(self, schluessel: str) -> None:
        with self._sperre:
            if self._werte.pop(schluessel, None) is not None:
                self._schreiben()

    def mehrere_schreiben(self, werte: dict) -> None:
        with self._sperre:
            self._werte.update(werte)
            self._schreiben()

    def schluessel(self) -> list[str]:
        with self._sperre:
            return list(self._werte)


_gemeinsam: JsonSpeicher | None = None


def gemeinsamer_speicher() -> JsonSpeicher:
    """Der Speicher des Programms (eine Instanz je Prozess), damit alle Leser dieselben Werte sehen."""
    global _gemeinsam
    if _gemeinsam is None:
        _gemeinsam = JsonSpeicher()
    return _gemeinsam
