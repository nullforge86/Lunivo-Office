"""Zustände der Knöpfe im Reiter „Überprüfen“: ob ein Knopf geht (``kann_…``) oder gedrückt ist (``an_…``), gelesen vom Farmwork und vom Dokumentschutz."""
from __future__ import annotations


class UeberpruefenZustaende:
    def _hat_kommentare(self) -> bool:
        fw = self._markup()
        return bool(fw is not None and fw.hat_kommentare())

    def _hat_aenderungen(self) -> bool:
        fw = self._markup()
        return bool(fw is not None and fw.hat_aenderungen())

    def _schutz(self) -> str | None:
        return self._schutz_wert()

    def _darf_aendern(self) -> bool:
        """Annehmen und Ablehnen: nicht, solange ein Dokumentschutz steht."""
        return self._schutz() is None

    kann_kommentarWeg = kann_kommentarWeiter = kann_kommentarZurueck = _hat_kommentare
    kann_aenderungAnnehmen = kann_aenderungAblehnen = _darf_aendern

    def an_bearbeitungEinschraenken(self) -> bool:
        return self._schutz() is not None
