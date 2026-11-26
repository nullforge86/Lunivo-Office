"""Abfragen und Befehle des Editors über das ganze Dokument (Rohtext, Stellen von Tabellen und Objekten, gleiche Formatierung, Seitenzahl)
anhand der Kennung. Stellen sind Zeichenstellen im Rohtext (Absätze durch ein Zeichen getrennt)."""
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from framework.anbindung import Daten, fest
from framework.befehle.bearbeiten.stellen import _sitzung, _zeichen_an_marke

MERKMALE = ("schrift", "groesse_pt", "fett", "kursiv", "unterstrichen", "durchgestrichen", "farbe", "marker", "hoch_tief", "kapitaelchen", "grossbuchstaben")


def rohtext(kennung: int) -> str:
    """Der Text des Dokuments mit U+2029 zwischen den Absätzen."""
    from core.suche.textsuche import roh_text
    return roh_text(_sitzung(kennung).dokument)


def tab_abstand(kennung: int) -> float:
    """Der Standardabstand der Tabulatoren des Dokuments in Bildpunkten."""
    v = _sitzung(kennung).dokument.eigenschaften.get("tab_abstand")
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 48.0


def ueberschriftsebene_an_marke(kennung: int) -> int:
    """Die Gliederungsebene des Absatzes an der Schreibmarke (0 = Fließtext)."""
    from core.formatvorlagen import ueberschriftsebene
    s = _sitzung(kennung)
    return ueberschriftsebene(s.dokument, s._absatz(s.auswahl.kopf.absatz_id))


def tabellen_ohne_rahmen(kennung: int) -> tuple[tuple[int, int], ...]:
    """(Stelle des Tabellenanfangs, Tabellen-Id) aller Tabellen ohne Rahmen, nach der Stelle geordnet."""
    from core.dokument import gehe_zu_stellen, gehe_zu_tabellen
    dok = _sitzung(kennung).dokument
    stellen = gehe_zu_stellen(dok)
    alle = sorted((p, t) for a in dok.abschnitte for t, p in gehe_zu_tabellen(a.bloecke, stellen) if float(t.format.get("rahmen_breite") or 0) <= 0)
    return tuple((p, t.id) for p, t in alle)


def aehnlich_formatiert(kennung: int) -> tuple[tuple[int, int], ...]:
    """Alle Strecken (von, bis) mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke."""
    from core.layout.drucklayout import zeichenformat
    s = _sitzung(kennung)
    dok = s.dokument
    soll = tuple(_zeichen_an_marke(s).get(k) for k in MERKMALE)
    aus, n = [], 0
    for a in dok.absaetze():
        versatz = 0
        for x in a.inhalte:
            laenge = len(x.text) if hasattr(x, "text") else 1
            if hasattr(x, "text") and x.text.strip():
                fmt = zeichenformat(dok, a, x.format)
                if tuple(fmt.get(k) for k in MERKMALE) == soll:
                    v, e = n + versatz, n + versatz + laenge
                    if aus and aus[-1][1] == v:
                        aus[-1] = (aus[-1][0], e)
                    else:
                        aus.append((v, e))
            versatz += laenge
        n += a.laenge + 1
    return tuple(aus)


def objekte_nach_stelle(kennung: int) -> tuple[tuple[int, str, int], ...]:
    """(Stelle, Art, Id) aller Objekte – ``text`` (im Text) oder ``frei`` (frei positioniert, Stelle des Ankerabsatzes) – nach der Stelle geordnet."""
    from core.dokument import InlineObjekt, gehe_zu_stellen
    dok = _sitzung(kennung).dokument
    stellen = gehe_zu_stellen(dok)
    liste = []
    for a in dok.absaetze():
        versatz = 0
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                liste.append((stellen[a.id] + versatz, "text", x.id))
                versatz += 1
            else:
                versatz += len(x.text)
    liste += [(stellen.get(o.anker, 0), "frei", o.id) for o in dok.objekte.values()]
    liste.sort()
    return tuple(liste)


def seitenzahl_setzen(kennung: int, bereich: str, erster_absatz: int | None, abschnitt: int, ort: str, ausrichtung: str, muster: str, zahlformat: str | None,
                      start: int | None = None, kapitel: tuple[int, str] | None = None, mit_start: bool = False) -> bool:
    """Seitenzahl in Kopf- oder Fußzeile: ``bereich`` „dokument“ (alle Abschnitte), „seite“ (neuer Abschnitt ab dem Absatz ``erster_absatz``, ohne Angabe
    ab dem Absatz der Schreibmarke) oder sonst der Abschnitt ``abschnitt``. ``mit_start``: Startwert (nur im ersten Ziel) und Kapitelnummer mitsetzen."""
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument import Position
    from core.dokument.kopf_fusszeilen import seitenzahl_setzen as setzen
    s = _sitzung(kennung)
    try:
        with s.gruppe("Seitenzahl"):
            if bereich == "dokument":
                ziele = list(range(len(s.dokument.abschnitte)))
            elif bereich == "seite":
                ziele = [s.abschnitt_einfuegen(Position(erster_absatz if erster_absatz is not None else s.auswahl.kopf.absatz_id, 0), "naechste")]
            else:
                ziele = [abschnitt]
            for i, nr in enumerate(ziele):
                seite = s.dokument.abschnitte[nr].seite.copy()
                if mit_start:
                    s.seite_ersetzen(nr, setzen(seite, ort, ausrichtung, muster, zahlformat, start if i == 0 else 0, kapitel))
                else:
                    s.seite_ersetzen(nr, setzen(seite, ort, ausrichtung, muster, zahlformat))
    except BearbeitungsFehler:
        return False
    return True


def objektliste(kennung: int) -> tuple[tuple[int, str, int, str], ...]:
    """(Stelle, ``text`` | ``frei``, Id, Objektart) aller Objekte: erst die Objekte im Text in Dokumentreihenfolge, dann die frei positionierten
    (Stelle des Ankerabsatzes)."""
    from core.dokument import InlineObjekt, gehe_zu_stellen
    dok = _sitzung(kennung).dokument
    stellen = gehe_zu_stellen(dok)
    gefunden = []
    for a in dok.absaetze():
        versatz = 0
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                gefunden.append((stellen[a.id] + versatz, "text", x.id, x.art))
                versatz += 1
            else:
                versatz += len(x.text)
    gefunden += [(stellen.get(o.anker, 0), "frei", o.id, o.art) for o in dok.objekte.values()]
    return tuple(gefunden)


def tabellenstellen(kennung: int) -> tuple[int, ...]:
    """Die Stellen der Tabellenanfänge aller Tabellen (auch geschachtelter), aufsteigend."""
    from core.dokument import gehe_zu_stellen, gehe_zu_tabellen
    dok = _sitzung(kennung).dokument
    stellen = gehe_zu_stellen(dok)
    return tuple(p for p, _t in sorted((p, t) for a in dok.abschnitte for t, p in gehe_zu_tabellen(a.bloecke, stellen)))


@dataclass(frozen=True)
class Barrierebefund:
    """Was die Prüfung der Barrierefreiheit im Dokument gezählt hat."""
    bilder_ohne_text: int                                        # Bilder und Zeichnungen ohne Alternativtext (dekorative zählen nicht)
    ebenen: tuple[int, ...]                                      # Gliederungsebenen der Überschriften mit Text, in Dokumentreihenfolge
    woerter: int
    textfarben: tuple[tuple[Daten, Daten], ...]                  # je Textstück (Schriftfarbe, Hervorhebung), wie im wirksamen Zeichenformat
    schlechte_links: int                                         # Verweise, die nur „hier“, „mehr“ … heißen
    tabellen_ohne_kopf: int


_LINK_SCHLECHT = re.compile(r"^(hier|klick|mehr|link|weiter)", re.I)


def _bild_ohne_alt(o) -> bool:
    """Ein Objekt (``InlineObjekt`` oder ``FreiesObjekt``) ohne Alternativtext; dekorative brauchen keinen."""
    if o.daten.get("dekor"):
        return False
    return not (o.alt_text or "").strip()


def _tabellen(dok):
    """Alle Tabellen des Dokuments (auch geschachtelte) in Dokumentreihenfolge."""
    from core.dokument import Tabelle

    def lauf(bloecke):
        for b in bloecke:
            if isinstance(b, Tabelle):
                yield b
                for zeile in b.zellen:
                    for zelle in zeile:
                        yield from lauf(zelle.bloecke)
    for ab in dok.abschnitte:
        yield from lauf(ab.bloecke)


def barrierefreiheit_befund(kennung: int) -> Barrierebefund:
    """Durchläuft das Dokument für die Prüfung der Barrierefreiheit (Bilder ohne Beschreibung, Überschriften, Textfarben, Verweise, Tabellenköpfe)."""
    from core.dokument import InlineObjekt, Lauf
    from core.formatvorlagen import ueberschriftsebene
    from core.layout.drucklayout import zeichenformat
    dok = _sitzung(kennung).dokument
    bilder = links = woerter = 0
    ebenen: list = []
    farben: list = []
    for a in dok.absaetze():
        lv = ueberschriftsebene(dok, a)
        if lv and a.text().strip():
            ebenen.append(lv)
        woerter += len(a.text().split())
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                if x.art in ("bild", "piktogramm", "diagramm", "smartart", "formel", "zeichenbereich", "wordart") and _bild_ohne_alt(x):
                    bilder += 1
            elif isinstance(x, Lauf) and x.text.strip():
                fmt = zeichenformat(dok, a, x.format)
                farben.append((fest(fmt.get("farbe")), fest(fmt.get("marker"))))
                if x.format.get("link") and _LINK_SCHLECHT.match(x.text.strip()):
                    links += 1
    bilder += sum(1 for o in dok.objekte.values() if o.art in ("bild", "piktogramm", "diagramm", "smartart", "zeichenbereich") and _bild_ohne_alt(o))
    return Barrierebefund(bilder, tuple(ebenen), woerter, tuple(farben), links, sum(1 for t in _tabellen(dok) if not t.format.get("kopfzeilen")))


def vorlesetext(kennung: int, von: int = 0, bis: int | None = None) -> str:
    """Der Text des Dokuments von ``von`` bis ``bis`` (Stellen im Rohtext) zum Vorlesen; Bilder mit Beschreibung werden angesagt."""
    from framework.dokumentverwaltung.dokumentpflege import vorlesetext as text_von
    return text_von(_sitzung(kennung).dokument, von, bis)


def ueberschriften(kennung: int) -> tuple[tuple[int, int, str], ...]:
    """(Stelle des Absatzanfangs im Rohtext, Gliederungsebene, Text) aller Überschriften mit Text, in Dokumentreihenfolge."""
    from core.formatvorlagen import ueberschriftsebene
    dok = _sitzung(kennung).dokument
    aus, stelle = [], 0
    for a in dok.absaetze():
        ebene = ueberschriftsebene(dok, a)
        pos, stelle = stelle, stelle + a.laenge + 1
        if ebene and a.text().strip():
            aus.append((pos, ebene, a.text().strip()))
    return tuple(aus)


def _abschnitt_an_marke(s) -> int:
    return s.abschnitt_index(s.auswahl.kopf.absatz_id)


def seitenzahl_vorgabe_setzen(kennung: int, ort: str, ausrichtung: str) -> bool:
    """Seitenzahl nach einer Vorgabe der Galerie in Kopf- oder Fußzeile des Abschnitts an der Schreibmarke; ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument.kopf_fusszeilen import seitenzahl_setzen as setzen
    s = _sitzung(kennung)
    index = _abschnitt_an_marke(s)
    try:
        s.seite_ersetzen(index, setzen(s.dokument.abschnitte[index].seite.copy(), ort, ausrichtung))
    except BearbeitungsFehler:
        return False
    return True


def seitenzahlen_entfernen(kennung: int) -> bool | None:
    """Die Seitenzahlen aus Kopf- und Fußzeile des Abschnitts an der Schreibmarke nehmen; ``None``, wenn dort keine steht, ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument.kopf_fusszeilen import seitenzahlen_entfernen as entfernen
    s = _sitzung(kennung)
    index = _abschnitt_an_marke(s)
    seite = s.dokument.abschnitte[index].seite.copy()
    if not entfernen(seite):
        return None
    try:
        s.seite_ersetzen(index, seite)
    except BearbeitungsFehler:
        return False
    return True


def toc_optionen(kennung: int) -> Mapping[str, Daten] | None:
    """Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt)."""
    from core.verzeichnisse.inhaltsverzeichnis import toc_optionen as optionen
    return fest(optionen(_sitzung(kennung).dokument))


def silbentrennung_verfuegbar(sprache: str) -> bool:
    """Gibt es für die Sprache eine Silbentrennung (das Paket „pyphen“ mit dieser Sprache)?"""
    from core.korrektur.silbentrennung import trenner_fuer
    return trenner_fuer(sprache) is not None
