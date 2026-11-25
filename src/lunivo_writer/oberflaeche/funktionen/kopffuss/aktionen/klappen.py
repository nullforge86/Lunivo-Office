"""Klappen (Pfeilmenüs) der Knöpfe im Reiter „Kopf- und Fußzeile“: baut die Menüs aus den Datenbeschreibungen des Frameworks."""
from __future__ import annotations

from lunivo_writer.farmwork.funktionen.kopffuss import menues
from lunivo_writer.farmwork.funktionen.kopffuss.typen import MenueEintrag
from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe


class KopfFussKlappen:
    def _kf_menue(self, eintraege: tuple[MenueEintrag, ...]) -> MenueListe:
        m = MenueListe()
        for e in eintraege:
            if e.ist_trenner:
                m.trenner()
            else:
                m.eintrag(e.text, lambda a=e.aktion: self._kf_aktion(a), aktiv=e.aktiv)
        return m

    def menue_kfGruppeKlappe(self):
        fw = self._fw()
        return self._kf_menue(menues.gruppe(fw.bearbeitung_aktiv() if fw is not None else False))

    def menue_kopfzeileKlappe(self): return self._kf_menue(menues.zone("kopf"))

    def menue_fusszeileKlappe(self): return self._kf_menue(menues.zone("fuss"))

    def menue_kopfLinieKlappe(self): return self._kf_menue(menues.linie())

    def menue_kfEinstellungenKlappe(self): return self._kf_menue(menues.einstellungen())
