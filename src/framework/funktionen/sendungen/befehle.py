"""Befehle der Funktion „Sendungen“, die den Text ändern: Umschlag, Etiketten, Seriendruckfelder, Adressblock, Regel.

Der Editor kommt über den ``AenderungsPort`` herein; die Fachlogik steht in ``kern/funktionen/sendungen``. Nach außen gehen nur Grundtypen."""
from __future__ import annotations

from framework.schnittstellen.aenderungs_port import AenderungsPort
from core.funktionen.sendungen import etiketten, umschlag
from core.funktionen.sendungen.serienbrief import serienfelder


def umschlag_aufbauen(editor: AenderungsPort, format_name: str, absender: str, empfaenger: str) -> None:
    """Ersetzt den Inhalt des Editors durch einen Umschlag und stellt das Blatt auf dessen Format."""
    dokument, seite = umschlag.umschlag_erstellen(format_name, absender, empfaenger)
    editor.aendern(lambda sitzung: sitzung.dokument_ersetzen(dokument))
    editor.page_settings_changed(seite)


def etiketten_aufbauen(editor: AenderungsPort, bogen: str, text: str, gleich: bool) -> None:
    """Ersetzt den Inhalt des Editors durch einen Etikettenbogen und stellt das Blatt darauf ein."""
    dokument, seite = etiketten.etiketten_erstellen(bogen, text, gleich)
    editor.aendern(lambda sitzung: sitzung.dokument_ersetzen(dokument))
    editor.page_settings_changed(seite)


def feld_einfuegen(editor: AenderungsPort, name: str) -> None:
    editor.aendern(lambda sitzung: serienfelder.feld_einfuegen(sitzung, name))


def adressblock_einfuegen(editor: AenderungsPort, was: str) -> None:
    editor.aendern(lambda sitzung: serienfelder.adressblock_einfuegen(sitzung, was))


def regel_einfuegen(editor: AenderungsPort, feld: str, wert: str, dann: str, sonst: str) -> None:
    editor.aendern(lambda sitzung: serienfelder.regel_einfuegen(sitzung, feld, wert, dann, sonst))


def felder_hervorheben(editor: AenderungsPort, an: bool) -> None:
    editor.aendern(lambda sitzung: serienfelder.felder_hervorheben(sitzung, an))


def naechster_einfuegen(editor: AenderungsPort) -> None:
    editor.aendern(lambda sitzung: serienfelder.naechster_einfuegen(sitzung))


def felder_im_text(editor: AenderungsPort) -> list[str]:
    """Die Namen der Seriendruckfelder im Text des Editors."""
    return editor.lesen(lambda sitzung: serienfelder.felder_im_text(sitzung.dokument))
