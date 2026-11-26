"""Text aus einer Datei in ein Dokument einfügen: Die Datei wird geladen und bereitgehalten, dann fügt ein Befehl ihren Haupttext an der Schreibmarke ein."""
from __future__ import annotations

from framework.schnittstellen import Dateifehler
from framework.sitzungen import sitzung as _steuerung

_GELADEN: dict = {}                    # Nummer → geladenes Dokument, bis es eingefügt oder verworfen ist
_naechste = [1]


def _fremde_bloecke(s, fremd) -> list:
    """Die Blöcke des Haupttextes eines geladenen Dokuments für die Sitzung ``s``: Listen werden angelegt, Bilddaten unter neuen Namen abgelegt."""
    import copy
    from core.dokument import Absatz, InlineObjekt, Rahmen, Tabelle
    bloecke = copy.deepcopy([b for a in fremd.abschnitte for b in a.bloecke])
    listen: dict = {}
    namen: dict = {}

    def absatz(a):
        if a.liste_id is not None:
            if a.liste_id not in listen:
                d = fremd.listen.get(a.liste_id)
                listen[a.liste_id] = s.liste_anlegen(copy.deepcopy(d.ebenen)) if d is not None and d.ebenen else None
            a.liste_id = listen[a.liste_id]
        for x in a.inhalte:
            if isinstance(x, InlineObjekt) and x.ressource and x.ressource in fremd.ressourcen:
                if x.ressource not in namen:
                    namen[x.ressource] = f"import-{len(s.dokument.ressourcen) + len(namen) + 1}-{x.ressource}"
                    s.ressource_setzen(namen[x.ressource], fremd.ressourcen[x.ressource])
                x.ressource = namen[x.ressource]

    def lauf(liste):
        for b in liste:
            if isinstance(b, Absatz):
                absatz(b)
            elif isinstance(b, Tabelle):
                for zeile in b.zellen:
                    for z in zeile:
                        lauf(z.bloecke)
            elif isinstance(b, Rahmen):
                lauf(b.bloecke)
    lauf(bloecke)
    return bloecke


def datei_laden(pfad: str) -> tuple[int, tuple[str, ...]]:
    """Eine Datei (DOCX, ODT, RTF, TXT …) zum Einfügen laden; → (Nummer, Hinweise über Nicht-Übernommenes). Eine Datei, die sich nicht lesen lässt,
    meldet ``Dateifehler``."""
    from core.dokument import DocumentIOError
    from framework.dokumentverwaltung.dateizugriff import lade_modell
    try:
        geladen = lade_modell(pfad)
    except DocumentIOError as e:
        raise Dateifehler(str(e)) from e
    nummer = _naechste[0]
    _naechste[0] += 1
    _GELADEN[nummer] = geladen.document
    return nummer, tuple(geladen.report.warnings)


def datei_verwerfen(nummer: int) -> None:
    _GELADEN.pop(nummer, None)


def datei_einfuegen(kennung: int, nummer: int) -> bool:
    """Den Haupttext der geladenen Datei ``nummer`` an der Schreibmarke einfügen (ein Schritt); ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    fremd = _GELADEN.pop(nummer)
    s = _steuerung._sitzungen[kennung].sitzung
    try:
        with s.gruppe("Text aus Datei"):
            s.ausschnitt_einfuegen(_fremde_bloecke(s, fremd))
    except BearbeitungsFehler:
        return False
    return True
