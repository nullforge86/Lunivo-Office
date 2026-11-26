"""Bilder in Kopf- und Fußzeile: ein frei platziertes Bild, das zur Kopf- oder Fußzeile eines Abschnitts gehört und auf jedem seiner Blätter steht.

Das Bild ist ein freies Objekt des Dokuments (Auswahl, Verschieben, Größe ändern und Löschen laufen über die Objektbefehle); es ist am ersten Absatz
des Abschnitts verankert und liegt bezogen auf das Blatt, zunächst links am Seitenrand in Höhe der Kopf- bzw. Fußzeile."""
from __future__ import annotations

from framework.sitzungen import sitzung as _steuerung

ZONEN = ("kopf", "fuss")


def bild_einfuegen(kennung: int, abschnitt: int, zone: str, breite: float, hoehe: float, bilddaten: bytes) -> int | None:
    """Ein Bild (Größe in Bildpunkten) in die Kopf- (``kopf``) oder Fußzeile (``fuss``) des Abschnitts legen; → die Id des Objekts,
    ``None``, wenn der Abschnitt keinen Absatz hat oder der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument import absaetze_in
    from core.geometrie import mm_to_px
    if zone not in ZONEN:
        raise ValueError(zone)
    s = _steuerung._sitzungen[kennung].sitzung
    abschnitte = s.dokument.abschnitte
    eintrag = abschnitte[max(0, min(abschnitt, len(abschnitte) - 1))]
    anker = next(absaetze_in(eintrag.bloecke), None)
    if anker is None:
        return None
    seite = eintrag.seite
    y = mm_to_px(seite.kopf_abstand_mm) if zone == ZONEN[0] else mm_to_px(seite.height_mm) - mm_to_px(seite.fuss_abstand_mm) - hoehe
    try:
        return s.objekt_frei_einfuegen("bild", breite, hoehe, anker.id, bilddaten=bilddaten, bezug_h="rand", ausr_h="left", bezug_v="seite",
                                       y=max(0.0, y), umbruch="vor", wiederholen=zone)
    except BearbeitungsFehler:
        return None


def bilder_der_zeile(kennung: int, abschnitt: int, zone: str) -> tuple[int, ...]:
    """Die Ids der Bilder und Objekte in der Kopf- bzw. Fußzeile des Abschnitts, in Stapelreihenfolge."""
    from core.dokument import absaetze_in
    s = _steuerung._sitzungen[kennung].sitzung
    abschnitte = s.dokument.abschnitte
    eigene = {a.id for a in absaetze_in(abschnitte[max(0, min(abschnitt, len(abschnitte) - 1))].bloecke)}
    treffer = [o for o in s.dokument.objekte.values() if o.wiederholen == zone and o.anker in eigene]
    return tuple(o.id for o in sorted(treffer, key=lambda o: o.ebene))
