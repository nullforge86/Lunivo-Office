"""Einstellungs-Anbieter für den Korrekturdienst: das Farmwork meldet ihn beim Dienst an, der Dienst fragt nur ihn (und kennt das Farmwork nicht).

Der Dienst in ``korrektur/`` erwartet ``thema``, ``thema_setzen``, ``schalter``, ``schalter_setzen``, ``pruefer_aktiv``, ``konsens_gegenprobe``,
``vorschlaege_anzeigen`` und ``get_bool``; hier stehen sie, gestützt auf ``einstellungen.py`` dieser Funktion."""
from __future__ import annotations

from framework.befehle.korrektur import einstellungen as korrektur_einstellungen
from framework.schnittstellen.einstellungen import Einstellungen


class KorrekturEinstellungenAnbieter:
    def __init__(self, einstellungen: Einstellungen):
        self._e = einstellungen

    def thema(self) -> str:
        return korrektur_einstellungen.thema(self._e)

    def thema_setzen(self, name: str) -> None:
        korrektur_einstellungen.thema_setzen(self._e, name)

    def schalter(self, name: str, vorgabe: bool) -> bool:
        return korrektur_einstellungen.schalter(self._e, name, vorgabe)

    def schalter_setzen(self, name: str, wert: bool) -> None:
        korrektur_einstellungen.schalter_setzen(self._e, name, wert)

    def pruefer_aktiv(self, name: str) -> bool:
        return korrektur_einstellungen.pruefer_aktiv(self._e, name)

    def konsens_gegenprobe(self) -> bool:
        return korrektur_einstellungen.konsens_gegenprobe(self._e)

    def vorschlaege_anzeigen(self) -> bool:
        return korrektur_einstellungen.vorschlaege_anzeigen(self._e)

    def get_bool(self, schluessel: str, vorgabe: bool) -> bool:
        return self._e.get_bool(schluessel, vorgabe)
