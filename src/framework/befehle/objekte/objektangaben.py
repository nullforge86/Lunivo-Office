"""Angaben der Objekte eines Dokuments für die Bedienung: die „Angabe“ eines frei positionierten Objekts (Wörterbuch mit Lage, Größe und Gestaltung)
lesen und zurückschreiben sowie die Objekte im Text an der Auswahl finden – alles anhand der Kennung, mit Ids statt Objekten des Kerns."""
from __future__ import annotations

from collections.abc import Mapping

from framework.anbindung import Daten, fest
from framework.sitzungen import sitzung as _steuerung


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def angabe(kennung: int, objekt_id: int) -> Mapping[str, Daten] | None:
    """Die Angabe des frei positionierten Objekts (unveränderliche Kopie); ``None``, wenn es das Objekt nicht gibt."""
    from core.dokument import angabe_von
    o = _sitzung(kennung).dokument.objekte.get(objekt_id)
    return None if o is None else fest(angabe_von(o))


def angabe_speichern(kennung: int, objekt_id: int, neue_angabe: Mapping[str, Daten], bilder: Mapping[str, bytes]) -> bool:
    """Schreibt die Angabe eines freien Objekts zurück, mit den dafür bereitgelegten Bildern (Name → Daten), in einem Schritt."""
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument import felder_aus_angabe
    s = _sitzung(kennung)
    try:
        with s.gruppe("Objekt ändern"):
            for name, daten in bilder.items():
                s.ressource_setzen(name, daten)
            s.objekt_aendern(objekt_id, **felder_aus_angabe(neue_angabe))
    except BearbeitungsFehler:
        return False
    return True


def inline_gewaehlt(kennung: int) -> int | None:
    """Id des Objekts im Text, das die Auswahl genau umfasst (ein Zeichen), sonst ``None``."""
    from core.dokument import InlineObjekt
    s = _sitzung(kennung)
    if s.auswahl.leer:
        return None
    von, bis = s._bereich()
    if von.absatz_id != bis.absatz_id or bis.versatz - von.versatz != 1:
        return None
    versatz = 0
    for x in s._absatz(von.absatz_id).inhalte:
        if isinstance(x, InlineObjekt):
            if versatz == von.versatz:
                return x.id
            versatz += 1
        else:
            versatz += len(x.text)
    return None


def inline_der_auswahl(kennung: int) -> tuple[int, ...] | None:
    """Ids der Objekte im Text, wenn die Auswahl nur aus Objekten (und Leerraum) besteht; sonst ``None``."""
    from core.dokument import InlineObjekt
    s = _sitzung(kennung)
    if s.auswahl.leer:
        return None
    von, bis = s._bereich()
    if von.absatz_id != bis.absatz_id:
        return None
    aus, versatz = [], 0
    for x in s._absatz(von.absatz_id).inhalte:
        n = 1 if isinstance(x, InlineObjekt) else len(x.text)
        if versatz + n > von.versatz and versatz < bis.versatz:
            if isinstance(x, InlineObjekt):
                aus.append(x.id)
            elif x.text.strip():
                return None
        versatz += n
    return tuple(aus)


def inline_an(kennung: int, absatz_id: int, stellen: tuple[int, ...]) -> tuple[int, ...]:
    """Ids der Objekte im Text des Absatzes, die an einer der Zeichenstellen ``stellen`` stehen, in Textreihenfolge."""
    from core.dokument import InlineObjekt
    aus, versatz = [], 0
    for x in _sitzung(kennung)._absatz(absatz_id).inhalte:
        if isinstance(x, InlineObjekt):
            if versatz in stellen:
                aus.append(x.id)
            versatz += 1
        else:
            versatz += len(x.text)
    return tuple(aus)


def textfelder(kennung: int) -> tuple[tuple[tuple[str, int], Mapping[str, Daten]], ...]:
    """Alle freien Textfelder des Dokuments: (Schlüssel ``("o", Id)``, Angabe) in Dokumentreihenfolge — frisch aus dem Modell gelesen."""
    from core.objekte.formen import textfelder as kern_textfelder
    return tuple((schluessel, fest(angabe_)) for schluessel, angabe_ in kern_textfelder(_sitzung(kennung).dokument))
