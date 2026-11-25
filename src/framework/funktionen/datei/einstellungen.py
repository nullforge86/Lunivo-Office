"""Einstellungen der Funktion „Datei“: Schlüssel, Vorgaben, Lesen und Ändern (Speichern, Sicherung, Verfasser, Kompatibilität, zuletzt benutzt)."""
from __future__ import annotations

from framework.schnittstellen.einstellungen import Einstellungen

LETZTER_ORDNER = "last_dir"
BILDER_NICHT_KOMPRIMIEREN = "speichern/bilder_nicht_komprimieren"
SICHERUNG_AKTIV = "sicherung/aktiv"
SICHERUNG_STAENDE = "sicherung/staende"
SICHERUNG_TAGE = "sicherung/tage"
PERSONENDATEN_WEG = "sicherheit/personendaten_weg"
BENUTZER_VERWENDEN = "benutzer/verwenden"
BENUTZER_NAME = "benutzer/name"
LETZTES_OEFFNEN = "start/letztes_oeffnen"
AUTOSPEICHERN_SEKUNDEN = "autosave_seconds"

KOMPATIBILITAET = (("kompat/seitenumbruch", "splitPgBreakAndParaMark"), ("kompat/haengend", "doNotUseIndentAsNumberingTabStop"),
                   ("kompat/leerstellen", "ulTrailSpace"), ("kompat/fussnoten", "footnoteLayoutLikeWW8"),
                   ("kompat/zeilenhoehe", "adjustLineHeightInTable"))

VORGABEN = {BILDER_NICHT_KOMPRIMIEREN: True, SICHERUNG_AKTIV: True, SICHERUNG_STAENDE: False, SICHERUNG_TAGE: 7, PERSONENDATEN_WEG: False,
            BENUTZER_VERWENDEN: True, BENUTZER_NAME: "", LETZTES_OEFFNEN: False, AUTOSPEICHERN_SEKUNDEN: 60}


def bilder_komprimieren(e: Einstellungen) -> bool:
    return not e.get_bool(BILDER_NICHT_KOMPRIMIEREN, VORGABEN[BILDER_NICHT_KOMPRIMIEREN])


def kompatibilitaet(e: Einstellungen) -> list[str]:
    return [name for schluessel, name in KOMPATIBILITAET if e.get_bool(schluessel, False)]


def verfasser(e: Einstellungen) -> str | None:
    """``""`` = Verfasser löschen, ein Name = diesen eintragen, ``None`` = das Dokument behält seinen Verfasser."""
    if e.get_bool(PERSONENDATEN_WEG, VORGABEN[PERSONENDATEN_WEG]) or not e.get_bool(BENUTZER_VERWENDEN, VORGABEN[BENUTZER_VERWENDEN]):
        return ""
    return e.get(BENUTZER_NAME, "") or None


def sicherung_aktiv(e: Einstellungen) -> bool:
    return e.get_bool(SICHERUNG_AKTIV, VORGABEN[SICHERUNG_AKTIV])


def staende_sichern(e: Einstellungen) -> bool:
    return e.get_bool(SICHERUNG_STAENDE, VORGABEN[SICHERUNG_STAENDE])


def aufbewahrung_tage(e: Einstellungen) -> int:
    return e.get_int(SICHERUNG_TAGE, VORGABEN[SICHERUNG_TAGE])


def letzten_ordner_merken(e: Einstellungen, ordner: str) -> None:
    e.set(LETZTER_ORDNER, ordner)


def letztes_dokument_oeffnen(e: Einstellungen) -> bool:
    return e.get_bool(LETZTES_OEFFNEN, VORGABEN[LETZTES_OEFFNEN])
