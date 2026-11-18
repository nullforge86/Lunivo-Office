"""Prüfkonfiguration und Speicherorte. Gespeichert wird als JSON im Datenordner des Werkzeugs."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field, fields

ALLE_ARTEN = ("import", "struktur", "format", "layout", "export", "roundtrip")


def datenordner() -> str:
    """``<Programmdaten>/kompatibilitaetspruefer`` (Qt-Standardpfade; Anwendungsname muss vorher gesetzt sein)."""
    from lunivo_writer.plattform.pfade import data_dir
    ordner = os.path.join(data_dir(), "kompatibilitaetspruefer")
    os.makedirs(ordner, exist_ok=True)
    return ordner


def cacheordner() -> str:
    from lunivo_writer.plattform.pfade import cache_dir
    ordner = os.path.join(cache_dir(), "kompatibilitaetspruefer")
    os.makedirs(ordner, exist_ok=True)
    return ordner


@dataclass
class Konfiguration:
    testordner: str = "~/Lunivo-Testdateien"          # Vorgabe wie ``werkzeuge/pruefungen/referenzbestand.py``
    referenzordner: str = ""                          # leer: Referenzen werden nur über ausdrückliche Zuordnung gefunden
    ergebnisordner: str = ""                          # leer: Datenordner des Werkzeugs (Exporte werden beim Export abgefragt)
    aktive_arten: list = field(default_factory=lambda: list(ALLE_ARTEN))
    exportformate: list = field(default_factory=lambda: ["docx", "odt", "rtf", "pdf"])
    # Visuelle Toleranzen
    zellanteil: float = 0.08                          # Anteil abweichender Bildpunkte in einer Rasterzelle, ab dem die Zelle als abweichend gilt
    seitenanteil: float = 0.02                        # Anteil abweichender Rasterzellen einer Seite, bis zu dem die Abweichung „gering“ bleibt
    verschiebung_mm: float = 3.0                      # Toleranz für verschobene Inhaltsbereiche und Seitenränder
    # Grenzen
    zeitlimit_s: int = 180                            # je Datei; danach wird der Prüfprozess beendet
    speicher_mb: int = 4096                           # Grenze für den belegten Arbeitsspeicher des Prüfprozesses in MB (0 = keine)
    max_seiten: int = 80                              # höchstens so viele Seiten je Dokument werden bildlich verglichen
    max_dateigroesse_mb: int = 256
    parallel: int = 2
    roundtrip_bearbeitung: bool = False               # zusätzlich: Marke einfügen, speichern, neu öffnen
    unterordner: bool = True
    rendern_dpi_faktor: float = 1.0                   # 1.0 = 96 dpi

    def pruefsumme(self) -> str:
        """Nur die Einstellungen, die ein Ergebnis beeinflussen (nicht Orte, Parallelität oder aktive Arten)."""
        relevant = {k: getattr(self, k) for k in ("exportformate", "roundtrip_bearbeitung", "zellanteil", "seitenanteil", "verschiebung_mm", "max_seiten",
                                                  "max_dateigroesse_mb", "rendern_dpi_faktor")}
        return hashlib.sha1(json.dumps(relevant, sort_keys=True).encode()).hexdigest()[:16]

    def als_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def aus_dict(d: dict) -> "Konfiguration":
        k = Konfiguration()
        for f in fields(Konfiguration):
            if f.name in d:
                setattr(k, f.name, d[f.name])
        return k


def _pfad() -> str:
    return os.path.join(datenordner(), "konfiguration.json")


def laden() -> Konfiguration:
    try:
        with open(_pfad(), encoding="utf-8") as f:
            return Konfiguration.aus_dict(json.load(f))
    except (OSError, ValueError):
        k = Konfiguration()
        k.parallel = max(1, min(4, (os.cpu_count() or 2) // 2))
        return k


def speichern(k: Konfiguration) -> None:
    tmp = _pfad() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(k.als_dict(), f, indent=2, ensure_ascii=False)
    os.replace(tmp, _pfad())


def ergebnisordner(k: Konfiguration) -> str:
    ordner = os.path.expanduser(k.ergebnisordner) if k.ergebnisordner else datenordner()
    os.makedirs(ordner, exist_ok=True)
    return ordner
