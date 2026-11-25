"""Auflösen von Formatvorlagen (reine Funktionen über dem Dokumentmodell)."""
from __future__ import annotations

from .dokument import Absatz, Dokument


def vorlagenkette(dokument: Dokument, name: str) -> list:
    """Die Vorlage und ihre Basisvorlagen, von der allgemeinsten zur genannten."""
    kette: list = []
    gesehen = set()
    while name and name in dokument.vorlagen and name not in gesehen:
        gesehen.add(name)
        kette.append(dokument.vorlagen[name])
        name = dokument.vorlagen[name].basis
    return kette[::-1]


def wirksames_absatzformat(dokument: Dokument, absatz: Absatz) -> dict:
    """Absatzformat mit allem, was die Formatvorlage des Absatzes vorgibt; eigene Angaben gewinnen."""
    fmt: dict = {}
    for v in vorlagenkette(dokument, absatz.format.get("vorlage", "")):
        fmt.update(v.absatz)
    fmt.update(absatz.format)
    return fmt


def wirksames_zeichenformat(dokument: Dokument, absatz: Absatz, zeichenformat: dict) -> dict:
    """Zeichenformat eines Laufs: Absatzvorlage, dann Zeichenvorlage, dann die eigenen Angaben."""
    fmt: dict = {}
    for v in vorlagenkette(dokument, absatz.format.get("vorlage", "")):
        fmt.update(v.zeichen)
    for v in vorlagenkette(dokument, zeichenformat.get("vorlage", "")):
        fmt.update(v.zeichen)
    fmt.update(zeichenformat)
    return fmt


def ueberschriftsebene(dokument: Dokument, absatz: Absatz) -> int:
    """1…9 für Überschriften, 0 für Fließtext."""
    if absatz.format.get("gliederungsebene"):
        return int(absatz.format["gliederungsebene"])
    kette = vorlagenkette(dokument, absatz.format.get("vorlage", ""))
    return kette[-1].ebene if kette else 0


# Eingebaute Formatvorlagen des Katalogs: (Name, Überschriftsebene, Größe pt (0 = Grundschrift), fett, kursiv, Abstand davor pt, Abstand danach pt)
EINGEBAUT = (("Standard", 0, 0, False, False, 0, 0), ("Überschrift 1", 1, 20, True, False, 9, 4.5), ("Überschrift 2", 2, 16, True, False, 6, 4.5),
             ("Überschrift 3", 3, 14, True, False, 6, 4.5), ("Überschrift 4", 4, 13, True, False, 4, 3), ("Überschrift 5", 5, 12, True, False, 4, 3),
             ("Überschrift 6", 6, 12, False, True, 4, 3), ("Überschrift 7", 7, 11, True, False, 4, 3), ("Überschrift 8", 8, 11, False, True, 4, 3),
             ("Überschrift 9", 9, 11, False, False, 4, 3), ("Titel", 0, 26, False, False, 0, 0), ("Untertitel", 0, 15, False, True, 0, 0),
             ("Zitat", 0, 0, False, True, 0, 0), ("Kein Abstand", 0, 0, False, False, 0, 0))
PX_JE_PT = 96.0 / 72.0


def eingebaute_vorlagen() -> dict:
    """Name → ``Formatvorlage`` für die eingebauten Stile; alle bauen auf „Standard“ auf, Überschriften folgt „Standard“."""
    from .dokument import Formatvorlage
    aus: dict = {}
    for name, ebene, groesse, fett, kursiv, davor, danach in EINGEBAUT:
        zeichen = {k: v for k, v in (("groesse_pt", float(groesse)) if groesse else (None, None), ("fett", True) if fett else (None, None),
                                     ("kursiv", True) if kursiv else (None, None)) if k}
        absatz = {k: v for k, v in (("abstand_vor", davor * PX_JE_PT) if davor else (None, None), ("abstand_nach", danach * PX_JE_PT) if danach else (None, None)) if k}
        aus[name] = Formatvorlage(name, "absatz", "" if name == "Standard" else "Standard", "Standard" if ebene or name in ("Titel", "Untertitel") else "",
                                  ebene, zeichen, absatz)
    return aus
