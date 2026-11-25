"""Befehle der Funktion „Sendungen“, die den Text ändern: Umschlag, Etiketten, Seriendruckfelder, Adressblock, Regel – für das Dokument mit der
Kennung, über den Änderungsrahmen. Die Fachlogik steht in ``framework.serienbriefe.erstellung`` und ``platzhalter``; nach außen gehen nur Grundtypen."""
from __future__ import annotations

from framework.befehle import ausfuehren, lesen
from framework.serienbriefe.erstellung import etiketten, umschlag
from framework.serienbriefe.platzhalter import konstanten, serienfelder


def _blatt_ersetzen(kennung: int, dokument, seite) -> None:
    """Inhalt durch ``dokument`` ersetzen, dann das Blatt des Abschnitts an der Schreibmarke auf ``seite`` stellen (zwei Rückgängig-Schritte, wie bisher)."""
    if ausfuehren(kennung, lambda s: s.dokument_ersetzen(dokument) or 1) is None:
        return
    ausfuehren(kennung, lambda s: s.seite_ersetzen(s.abschnitt_index(s.auswahl.kopf.absatz_id), seite) or 1)


def umschlag_aufbauen(kennung: int, format_name: str, absender: str, empfaenger: str) -> None:
    """Ersetzt den Inhalt des Dokuments durch einen Umschlag und stellt das Blatt auf dessen Format."""
    _blatt_ersetzen(kennung, *umschlag.umschlag_erstellen(format_name, absender, empfaenger))


def etiketten_aufbauen(kennung: int, bogen: str, text: str, gleich: bool) -> None:
    """Ersetzt den Inhalt des Dokuments durch einen Etikettenbogen und stellt das Blatt darauf ein."""
    _blatt_ersetzen(kennung, *etiketten.etiketten_erstellen(bogen, text, gleich))


def feld_einfuegen(kennung: int, name: str) -> None:
    ausfuehren(kennung, lambda s: serienfelder.feld_einfuegen(s, name))


def adressblock_einfuegen(kennung: int, was: str) -> None:
    ausfuehren(kennung, lambda s: serienfelder.adressblock_einfuegen(s, was))


def regel_einfuegen(kennung: int, feld: str, wert: str, dann: str, sonst: str) -> None:
    ausfuehren(kennung, lambda s: serienfelder.regel_einfuegen(s, feld, wert, dann, sonst))


def felder_hervorheben(kennung: int, an: bool) -> None:
    ausfuehren(kennung, lambda s: serienfelder.felder_hervorheben(s, an))


def naechster_einfuegen(kennung: int) -> None:
    ausfuehren(kennung, lambda s: serienfelder.naechster_einfuegen(s))


def felder_im_text(kennung: int) -> tuple[str, ...]:
    """Die Namen der Seriendruckfelder im Text des Dokuments."""
    return tuple(lesen(kennung, lambda s: serienfelder.felder_im_text(s.dokument)) or ())


def zuordenbare_felder(kennung: int) -> tuple[str, ...]:
    """Die Seriendruckfelder im Text, die einer Spalte der Empfängerliste zugeordnet werden (ohne „Nächster Datensatz“)."""
    return tuple(f for f in felder_im_text(kennung) if f != konstanten.NAECHSTER)
