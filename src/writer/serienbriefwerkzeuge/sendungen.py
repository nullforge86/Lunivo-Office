"""Sendungen (Umschlag, Etiketten, Seriendruckfelder, Adressblock, Regel): ordnet die Bedienung den Framework-Befehlen zu. Die Oberfläche gibt
die Kennung des Dokuments, nicht den Editor."""
from __future__ import annotations

from framework import serienbriefe as _befehle


def umschlag_aufbauen(kennung: int, format_name: str, absender: str, empfaenger: str) -> None:
    _befehle.umschlag_aufbauen(kennung, format_name, absender, empfaenger)


def etiketten_aufbauen(kennung: int, bogen: str, text: str, gleich: bool) -> None:
    _befehle.etiketten_aufbauen(kennung, bogen, text, gleich)


def seriendruckfeld_einfuegen(kennung: int, name: str) -> None:
    _befehle.feld_einfuegen(kennung, name)


def adressblock_einfuegen(kennung: int, was: str) -> None:
    _befehle.adressblock_einfuegen(kennung, was)


def seriendruckregel_einfuegen(kennung: int, feld: str, wert: str, dann: str, sonst: str) -> None:
    _befehle.regel_einfuegen(kennung, feld, wert, dann, sonst)


def seriendruckfelder_hervorheben(kennung: int, an: bool) -> None:
    _befehle.felder_hervorheben(kennung, an)


def naechster_datensatz_einfuegen(kennung: int) -> None:
    _befehle.naechster_einfuegen(kennung)


def seriendruckfelder_im_text(kennung: int) -> tuple[str, ...]:
    return _befehle.felder_im_text(kennung)


def zuordenbare_seriendruckfelder(kennung: int) -> tuple[str, ...]:
    return _befehle.zuordenbare_felder(kennung)
