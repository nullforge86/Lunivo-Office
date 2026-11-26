"""Dokumentverwaltung ohne Oberfläche: Laden, Speichern, automatische Sicherung, Wiederherstellung, zuletzt benutzte Dateien.

Das Hauptfenster ruft diese Klasse auf und kümmert sich selbst nur um Dialoge (Kennwort, Fehlermeldungen, Hinweise).
"""
from __future__ import annotations

from collections.abc import Mapping

import os

from framework.dokumentverwaltung.dateizugriff import dateiformate as formats
from framework.dokumentverwaltung.dokumentpflege import wiederherstellung
from framework.schnittstellen.einstellungen import Einstellungen
from framework.befehle.datei import einstellungen as datei_einstellungen


class DocumentManager:
    def __init__(self, settings: Einstellungen):
        self.settings = settings

    # ---- Laden und Speichern -------------------------------------------------------------------------
    def laden(self, path: str, kennwort: str | None = None):
        """Liest eine Datei; Fehler (DocumentIOError, PasswortNoetig) gehen an den Aufrufer."""
        from framework.dokumentverwaltung.dateizugriff.modell_laden import lade_modell
        return lade_modell(path, kennwort)

    def meta_fuer_speichern(self, meta: dict) -> dict:
        """Dokument-Metadaten plus Einstellungen: Verfasser (Benutzername oder gelöscht)."""
        m = dict(meta)
        m["bilder_komprimieren"] = datei_einstellungen.bilder_komprimieren(self.settings)
        m["kompat"] = datei_einstellungen.kompatibilitaet(self.settings)
        verfasser = datei_einstellungen.verfasser(self.settings)
        if verfasser is not None:
            m["author"] = verfasser
        return m

    def speichern(self, path: str, dokument, seite, meta: dict, erwartet=None):
        """Schreibt das Dokument; gibt den Bericht über nicht Übernommenes zurück. ``erwartet``: der zuletzt gesehene ``stand`` der Zieldatei
        (siehe ``sicher_schreiben.schreiben``); ohne Angabe wird nicht verglichen."""
        from core.dokument import Dokument
        if not isinstance(dokument, Dokument):
            raise TypeError("Gespeichert wird nur das Dokumentmodell (core.document.Dokument), kein Qt-Textdokument.")
        from framework.dokumentverwaltung.dateizugriff import modell_speichern, sicher_schreiben
        stand = erwartet[0] if erwartet is not None else sicher_schreiben.UNGEPRUEFT
        return modell_speichern.speichere_modell(path, dokument, seite, self.meta_fuer_speichern(meta), erwartet=stand)

    def speichern_dokument(self, kennung: int, path: str, seite, meta: Mapping, erwartet=None) -> tuple[str, ...]:
        """Schreibt das Dokument ``kennung`` nach ``path``; → Hinweise über nicht Übernommenes. ``erwartet``: der zuletzt gesehene ``stand`` der
        Zieldatei. Lässt sich die Datei nicht schreiben (auch: sie wurde inzwischen von anderer Seite geändert), meldet das ``Dateifehler``."""
        from core.dokument import DocumentIOError
        from framework.schnittstellen import Dateifehler
        from framework.sitzungen.dokumentsteuerung import sitzung as _steuerung
        try:
            bericht = self.speichern(path, _steuerung._sitzungen[kennung].sitzung.dokument, seite, dict(meta), erwartet)
        except DocumentIOError as e:
            raise Dateifehler(str(e)) from None
        return tuple(bericht.warnings)

    # ---- Zuletzt benutzt -------------------------------------------------------------------------------
    def zuletzt(self) -> list[str]:
        return self.settings.recent()

    def gelesen(self, path: str) -> None:
        datei_einstellungen.letzten_ordner_merken(self.settings, os.path.dirname(path))
        self.settings.add_recent(path)

    def vergessen(self, path: str) -> None:
        self.settings.remove_recent(path)

    # ---- Sicherung und Wiederherstellung ---------------------------------------------------------------
    def sichern(self, tabs) -> None:
        """Automatische Sicherung aller geänderten Dokumente. Fehler stören die Arbeit nie."""
        if not datei_einstellungen.sicherung_aktiv(self.settings):
            return
        for t in tabs:
            if not t.is_modified():
                continue
            docx_path, _ = wiederherstellung.paths(t.token)
            try:
                modell = t.modell_fuer_speichern() if hasattr(t, "modell_fuer_speichern") else None
                if modell is None:
                    continue
                from framework.dokumentverwaltung.dateizugriff.modell_speichern import speichere_modell
                speichere_modell(docx_path, modell, t.page, t.meta, sicherung=False)
                wiederherstellung.write_meta(t.token, t.path or "", t.title)
                if datei_einstellungen.staende_sichern(self.settings):
                    wiederherstellung.zwischenstand(t.token, t.title, datei_einstellungen.aufbewahrung_tage(self.settings))
            except Exception:
                pass

    def wiederherstellbar(self, offene_token: set):
        return wiederherstellung.pending(exclude=offene_token)

    def verwerfen(self, token) -> None:
        wiederherstellung.discard(token)
