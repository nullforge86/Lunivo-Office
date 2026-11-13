"""Dokumentverwaltung ohne Oberfläche: Laden, Speichern, automatische Sicherung, Wiederherstellung, zuletzt benutzte Dateien.

Das Hauptfenster ruft diese Klasse auf und kümmert sich selbst nur um Dialoge (Kennwort, Fehlermeldungen, Hinweise).
"""
from __future__ import annotations

import os

from lunivo_writer.dienste import datei_dienst as formats
from lunivo_writer.dienste import wiederherstellung
from lunivo_writer.dienste.einstellungen_dienst import Settings


class DocumentManager:
    def __init__(self, settings: Settings):
        self.settings = settings

    # ---- Laden und Speichern -------------------------------------------------------------------------
    def laden(self, path: str, kennwort: str | None = None):
        """Liest eine Datei; Fehler (DocumentIOError, PasswortNoetig) gehen an den Aufrufer."""
        return formats.load(path, kennwort)

    def meta_fuer_speichern(self, meta: dict) -> dict:
        """Dokument-Metadaten plus Einstellungen: Verfasser (Benutzername oder gelöscht)."""
        m = dict(meta)
        m["bilder_komprimieren"] = not self.settings.get_bool("speichern/bilder_nicht_komprimieren", True)
        m["kompat"] = [n for k, n in (("kompat/seitenumbruch", "splitPgBreakAndParaMark"), ("kompat/haengend", "doNotUseIndentAsNumberingTabStop"),
                                      ("kompat/leerstellen", "ulTrailSpace"), ("kompat/fussnoten", "footnoteLayoutLikeWW8"),
                                      ("kompat/zeilenhoehe", "adjustLineHeightInTable")) if self.settings.get_bool(k, False)]
        if self.settings.get_bool("sicherheit/personendaten_weg", False) or not self.settings.get_bool("benutzer/verwenden", True):
            m["author"] = ""
        elif self.settings.get("benutzer/name", ""):
            m["author"] = self.settings.get("benutzer/name", "")
        return m

    def speichern(self, path: str, dokument, seite, meta: dict, erwartet=None):
        """Schreibt das Dokument; gibt den Bericht über nicht Übernommenes zurück. ``erwartet``: der zuletzt gesehene ``stand`` der Zieldatei
        (siehe ``sicher_schreiben.schreiben``); ohne Angabe wird nicht verglichen."""
        from lunivo_writer.core.document import Document
        if isinstance(dokument, Document):
            from lunivo_writer.dienste import modell_speichern, sicher_schreiben
            stand = erwartet[0] if erwartet is not None else sicher_schreiben.UNGEPRUEFT
            return modell_speichern.speichere_modell(path, dokument, seite, self.meta_fuer_speichern(meta), erwartet=stand)
        if erwartet is None:
            return formats.save(path, dokument, seite, self.meta_fuer_speichern(meta))
        return formats.save(path, dokument, seite, self.meta_fuer_speichern(meta), erwartet=erwartet[0])

    # ---- Zuletzt benutzt -------------------------------------------------------------------------------
    def zuletzt(self) -> list[str]:
        return self.settings.recent()

    def gelesen(self, path: str) -> None:
        self.settings.set("last_dir", os.path.dirname(path))
        self.settings.add_recent(path)

    def vergessen(self, path: str) -> None:
        self.settings.remove_recent(path)

    # ---- Sicherung und Wiederherstellung ---------------------------------------------------------------
    def sichern(self, tabs) -> None:
        """Automatische Sicherung aller geänderten Dokumente. Fehler stören die Arbeit nie."""
        if not self.settings.get_bool("sicherung/aktiv", True):
            return
        for t in tabs:
            if not t.is_modified():
                continue
            docx_path, _ = wiederherstellung.paths(t.token)
            try:
                modell = t.modell_fuer_speichern() if hasattr(t, "modell_fuer_speichern") else None
                if modell is None:
                    formats.save(docx_path, t.editor.document(), t.page, t.meta, sicherung=False)
                else:
                    from lunivo_writer.dienste.modell_speichern import speichere_modell
                    speichere_modell(docx_path, modell, t.page, t.meta, sicherung=False)
                wiederherstellung.write_meta(t.token, t.path or "", t.title)
                if self.settings.get_bool("sicherung/staende", False):
                    wiederherstellung.zwischenstand(t.token, t.title, self.settings.get_int("sicherung/tage", 7))
            except Exception:
                pass

    def wiederherstellbar(self, offene_token: set):
        return wiederherstellung.pending(exclude=offene_token)

    def verwerfen(self, token) -> None:
        wiederherstellung.discard(token)
