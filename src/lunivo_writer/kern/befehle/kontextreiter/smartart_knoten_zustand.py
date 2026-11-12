"""Befehle: Zustand des gewählten SmartArt-Knotens – seine Maße fürs Band und ob „Aufzählungszeichen einfügen“ geht.

Mixin zu ``SmartArtToolsBefehle`` (``kern/befehle/kontextreiter/smartarttools.py``); steht in ``Befehle`` davor und ersetzt dessen Aufzählungs-Zustand.
Die Knotenmaße kommen aus dem Zeichnen (``SA.knoten_rechtecke``) und sind nur ablesbar: das Datenmodell speichert keine Knotengröße,
das Layout bestimmt sie. Das Band zeigt sie schreibgeschützt."""
from __future__ import annotations

from lunivo_writer.modelle.seite import px_to_mm


class SmartArtKnotenZustand:
    def smartartKnotenMasse(self) -> tuple[float, float] | None:
        """(Breite, Höhe) des gewählten Knotens in mm; ohne gewählten Knoten None (dann gelten die Maße des Objekts)."""
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.editor.objekte import smartart as SA
        ed = self.ed
        if not ed:
            return None
        ident, d, z = SA.knoten_gewaehlt(ed), SA.daten_der_auswahl(ed), BL.ziel(ed)
        if ident is None or d is None or z is None or z[0] != "frei":
            return None
        b, h = float(z[2]["b"]), float(z[2]["h"])
        schl = (repr(sorted((k, v) for k, v in d.items() if k != "auswahl")), round(b), round(h))
        c = getattr(ed, "_sa_masse_cache", None)
        if c is None or c[0] != schl:
            c = (schl, SA.knoten_rechtecke(d, b, h)); ed._sa_masse_cache = c
        r = c[1].get(ident)
        return (px_to_mm(r.width()), px_to_mm(r.height())) if r is not None else None

    def kann_smartartAufzaehlung(self) -> bool:
        """Ein Knoten ist gewählt und das Layout erlaubt Aufzählungspunkte (im Organigramm sind Unterpunkte eigene Knoten: im Foto grau)."""
        from lunivo_writer.editor.objekte import smartart as SA
        d = self._sa()
        return self._sa_kann("knoten") and d is not None and d.get("layout", "Liste") not in SA.HIERARCHIE_LAYOUTS

    def smartartAufzaehlung(self, k=None):
        """Ohne Wirkung, solange der Knopf grau ist."""
        if self._sa() is not None and not self.kann_smartartAufzaehlung():
            return False
        return super().smartartAufzaehlung(k)
