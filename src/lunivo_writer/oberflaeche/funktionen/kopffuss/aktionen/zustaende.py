"""Zustände der Knöpfe im Reiter „Kopf- und Fußzeile“: gedrückt (``an_…``) und möglich (``kann_…``), gelesen vom Framework."""
from __future__ import annotations


class KopfFussZustaende:
    def kann_kfVerknuepfen(self):
        """Grau auf der ersten Seite/im ersten Abschnitt: dort gibt es keinen Vorgänger."""
        fw = self._fw()
        return fw is not None and fw.bearbeitung_aktiv() and fw.verknuepfung_moeglich()

    def an_kfVerknuepfen(self):
        fw = self._fw()
        return fw is not None and fw.bearbeiter_verknuepft()

    def an_kopfVerknuepfen(self):
        fw = self._fw()
        return fw is not None and fw.verknuepft("kopf")

    def an_fussVerknuepfen(self):
        fw = self._fw()
        return fw is not None and fw.verknuepft("fuss")

    def an_geradeUngerade(self):
        fw = self._fw()
        return bool(fw is not None and fw.gerade_ungerade())

    def an_ersteSeiteAnders(self):
        fw = self._fw()
        return bool(fw is not None and fw.erste_seite_anders())
