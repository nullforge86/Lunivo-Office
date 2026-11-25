"""Das maßgebliche Dokumentmodell — reine Python-Daten, ohne Qt.

Aufbau::

    Dokument
      abschnitte: [Abschnitt]            jeder mit eigener Seiteneinrichtung (``modelle.seite.PageSettings``, samt Kopf-/Fußzeilen)
        bloecke: [Absatz | Tabelle | Rahmen]
          Absatz.inhalte: [Lauf | InlineObjekt]
          Tabelle.zellen[zeile][spalte]: Zelle mit bloecke: [Absatz | Tabelle | Rahmen]   (verschachtelte Tabellen)
          Rahmen.bloecke: [Absatz | Tabelle | Rahmen]   (Textrahmen im Fluss)
      vorlagen, listen, kommentare, noten, objekte (frei positioniert, an einem Absatz verankert), ressourcen, quellen, eigenschaften

Jeder Absatz, jede Tabelle, jeder Rahmen, jeder Abschnitt und jedes Objekt hat eine im Dokument eindeutige ``id``. Eine Textstelle ist
``Position(absatz_id, versatz)``; sie bleibt gültig, wenn anderswo im Dokument etwas geändert wird.

Geändert wird das Modell nur über ``core.editing.Bearbeitungssitzung`` — sie führt das Änderungsprotokoll für Rückgängig/Wiederholen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, NamedTuple

from core.dokument.seite import PageSettings

OBJEKT_ZEICHEN = "￼"           # steht in ``Absatz.text()`` für ein Objekt im Text
OBJEKT_ARTEN = ("bild", "form", "textfeld", "wordart", "diagramm", "smartart", "formel", "piktogramm", "zeichenbereich", "gruppe", "roh")
UMBRUCH_ARTEN = ("quadrat", "eng", "durch", "oben_unten", "hinter", "vor")      # Textumbruch frei positionierter Objekte
ABSCHNITT_BEGINN = ("naechste", "fortlaufend", "gerade", "ungerade")
ZAHLENARTEN = ("dezimal", "klein", "gross", "roem_klein", "roem_gross")
AUFZAEHLUNGEN = ("disc", "circle", "square", "zeichen")
LISTEN_EBENEN = 9


class Position(NamedTuple):
    absatz_id: int
    versatz: int = 0


class Auswahl(NamedTuple):
    anker: Position
    kopf: Position

    @property
    def leer(self) -> bool:
        return self.anker == self.kopf


@dataclass
class Lauf:
    """Ein Textstück mit einheitlichem Zeichenformat."""
    text: str
    format: dict = field(default_factory=dict)


@dataclass
class InlineObjekt:
    """Ein Objekt, das wie ein Zeichen im Text steht (Bild, Form, Textfeld, Formel …). Zählt als eine Textstelle."""
    id: int
    art: str = "bild"
    breite: float = 0.0
    hoehe: float = 0.0
    ressource: str = ""                                  # Schlüssel in ``Dokument.ressourcen`` (Bilddaten)
    daten: dict = field(default_factory=dict)            # artspezifisch: Zuschnitt, Effekte, Formbeschreibung, Text des Textfelds …
    alt_text: str = ""
    format: dict = field(default_factory=dict)           # Zeichenformat an dieser Stelle (Kommentar, Änderung, Verweis …)


@dataclass
class Absatz:
    id: int
    inhalte: list = field(default_factory=list)          # [Lauf | InlineObjekt]
    format: dict = field(default_factory=dict)           # Absatzformat
    zeichenformat: dict = field(default_factory=dict)    # Format der Absatzmarke: gilt für Text, der in den leeren Absatz getippt wird
    liste_id: int | None = None
    ebene: int = 0                                       # Listenebene 0…8
    format_aufgeloest: bool = False                      # Import enthält bereits das sichtbare Absatzformat

    @property
    def laenge(self) -> int:
        return sum(len(x.text) if isinstance(x, Lauf) else 1 for x in self.inhalte)

    def text(self) -> str:
        return "".join(x.text if isinstance(x, Lauf) else OBJEKT_ZEICHEN for x in self.inhalte)


@dataclass
class Zelle:
    bloecke: list = field(default_factory=list)          # [Absatz | Tabelle | Rahmen]; leer nur bei verdeckten Zellen
    format: dict = field(default_factory=dict)
    zeilenspanne: int = 1
    spaltenspanne: int = 1
    verdeckt_von: tuple | None = None                    # (zeile, spalte) der verbundenen Zelle, zu der dieses Feld gehört


@dataclass
class Tabelle:
    id: int
    zellen: list = field(default_factory=list)           # Zeilen × Spalten, immer ein volles Gitter
    spaltenbreiten: list = field(default_factory=list)   # je Spalte; 0 = automatisch
    zeilenhoehen: list = field(default_factory=list)     # Mindesthöhe je Zeile; 0 = automatisch
    format: dict = field(default_factory=dict)

    @property
    def zeilen(self) -> int:
        return len(self.zellen)

    @property
    def spalten(self) -> int:
        return len(self.zellen[0]) if self.zellen else 0

    def anker(self, zeile: int, spalte: int) -> tuple:
        """Die Gitterstelle der sichtbaren Zelle, zu der (zeile, spalte) gehört."""
        return self.zellen[zeile][spalte].verdeckt_von or (zeile, spalte)

    def zelle(self, zeile: int, spalte: int) -> Zelle:
        z, s = self.anker(zeile, spalte)
        return self.zellen[z][s]


@dataclass
class Rahmen:
    """Ein Textrahmen im Fluss: enthält eigene Blöcke, hat Rahmen, Ränder, Breite und Umfluss. Wie eine Tabelle steht er immer hinter
    einem Absatz."""
    id: int
    bloecke: list = field(default_factory=list)          # [Absatz | Tabelle | Rahmen]; endet mit einem Absatz
    format: dict = field(default_factory=dict)


@dataclass
class Abschnitt:
    id: int
    bloecke: list = field(default_factory=list)
    seite: PageSettings = field(default_factory=PageSettings)
    beginn: str = "naechste"


@dataclass
class ListenEbene:
    stil: str = "dezimal"                # Zahlenart oder Aufzählungsart
    format: str = ""                     # Zahlenformat mit ①…⑨ für die Nummern der Ebenen 1…9; leer: „①.“ der eigenen Ebene
    start: int = 1
    ausr: float = 0.0                    # mm: wo die Nummer beginnt
    einzug: float = 0.0                  # mm: wo der Text beginnt
    zeichen: str = ""                    # eigenes Aufzählungszeichen (stil „zeichen“)
    zusatz: dict = field(default_factory=dict)      # tab, ausr_art, danach, neu, norm, vorlage


@dataclass
class ListenDefinition:
    id: int
    ebenen: list = field(default_factory=list)      # bis zu 9 × ListenEbene
    name: str = ""


@dataclass
class Formatvorlage:
    name: str
    art: str = "absatz"                  # absatz | zeichen | tabelle
    basis: str = ""
    folge: str = ""                      # Vorlage des folgenden Absatzes
    ebene: int = 0                       # Überschriftsebene, 0 = Fließtext
    zeichen: dict = field(default_factory=dict)
    absatz: dict = field(default_factory=dict)
    zusatz: dict = field(default_factory=dict)      # Tastenkürzel, Fremdschlüssel (DOCX-Name), Liste, Tabellenangaben


@dataclass
class Kommentar:
    id: int
    autor: str = ""
    initialen: str = ""
    datum: str = ""
    text: str = ""
    geloest: bool = False
    antwort_auf: int | None = None


@dataclass
class Note:
    id: int
    art: str = "f"                       # f = Fußnote, e = Endnote
    text: str = ""


@dataclass
class FreiesObjekt:
    """Ein frei positioniertes Objekt, an einem Absatz verankert (Bild, Form, Textfeld …)."""
    id: int
    anker: int                           # Absatz-Id
    art: str = "bild"
    breite: float = 0.0
    hoehe: float = 0.0
    bezug_h: str = "spalte"              # seite | rand | spalte
    x: float = 0.0
    ausr_h: str = ""                     # left | center | right | inside | outside
    bezug_v: str = "absatz"              # seite | rand | absatz
    y: float = 0.0
    ausr_v: str = ""                     # top | center | bottom
    umbruch: str = "vor"
    ebene: int = 0                       # Stapelreihenfolge
    ressource: str = ""
    daten: dict = field(default_factory=dict)
    alt_text: str = ""


@dataclass
class Dokument:
    abschnitte: list = field(default_factory=list)
    vorlagen: dict = field(default_factory=dict)         # Name → Formatvorlage
    listen: dict = field(default_factory=dict)           # Id → ListenDefinition
    kommentare: dict = field(default_factory=dict)       # Id → Kommentar
    noten: dict = field(default_factory=lambda: {"f": {}, "e": {}})      # Art → Id → Note
    objekte: dict = field(default_factory=dict)          # Id → FreiesObjekt
    ressourcen: dict = field(default_factory=dict)       # Schlüssel → bytes
    quellen: list = field(default_factory=list)          # Literaturquellen
    eigenschaften: dict = field(default_factory=dict)    # title, author, sprache, zitierweise, kennwort, kompat …
    standardformat: dict = field(default_factory=dict)   # Grundschrift des Dokuments: schrift, groesse_pt, rand (Dokumentrand in Bildpunkten)
    naechste_id: int = 1

    def neue_id(self) -> int:
        n = self.naechste_id
        self.naechste_id += 1
        return n

    # ---- Durchlaufen ---------------------------------------------------------------------------------------------
    def behaelter(self) -> Iterator[tuple]:
        """Alle Blocklisten in Dokumentreihenfolge als (Besitzer, Liste); Besitzer ist ein Abschnitt, eine Zelle oder ein Rahmen."""
        for abschnitt in self.abschnitte:
            yield from _behaelter(abschnitt)

    def absaetze(self) -> Iterator[Absatz]:
        """Alle Absätze in Dokumentreihenfolge — der Inhalt einer Tabelle steht an der Stelle der Tabelle, Zelle für Zelle."""
        for abschnitt in self.abschnitte:
            yield from absaetze_in(abschnitt.bloecke)

    def tabellen(self) -> Iterator[Tabelle]:
        """Alle Tabellen in Dokumentreihenfolge, eine äußere vor den Tabellen in ihren Zellen."""
        for abschnitt in self.abschnitte:
            yield from _tabellen(abschnitt.bloecke)

    def finde(self, block_id: int):
        """(Besitzer, Blockliste, Index, Block) zu einer Absatz-, Tabellen- oder Rahmen-Id; ``None``, wenn es sie nicht gibt."""
        for besitzer, bloecke in self.behaelter():
            for i, b in enumerate(bloecke):
                if b.id == block_id:
                    return besitzer, bloecke, i, b
        return None

    def absatz(self, absatz_id: int) -> Absatz:
        f = self.finde(absatz_id)
        if f is None or not isinstance(f[3], Absatz):
            raise KeyError(f"Kein Absatz mit der Id {absatz_id}")
        return f[3]

    def tabelle(self, tabellen_id: int) -> Tabelle:
        f = self.finde(tabellen_id)
        if f is None or not isinstance(f[3], Tabelle):
            raise KeyError(f"Keine Tabelle mit der Id {tabellen_id}")
        return f[3]

    def abschnitt_von(self, block_id: int) -> Abschnitt:
        for abschnitt in self.abschnitte:
            for _besitzer, bloecke in _behaelter(abschnitt):
                if any(b.id == block_id for b in bloecke):
                    return abschnitt
        raise KeyError(f"Kein Block mit der Id {block_id}")

    def reihenfolge(self) -> dict:
        """Absatz-Id → laufende Nummer in Dokumentreihenfolge (zum Vergleichen von Positionen)."""
        return {a.id: i for i, a in enumerate(self.absaetze())}

    def text(self) -> str:
        return "\n".join(a.text() for a in self.absaetze())

    def anfang(self) -> Position:
        return Position(next(self.absaetze()).id, 0)

    def ende(self) -> Position:
        letzter = None
        for letzter in self.absaetze():
            pass
        return Position(letzter.id, letzter.laenge)


def _behaelter(besitzer) -> Iterator[tuple]:
    yield besitzer, besitzer.bloecke
    for b in besitzer.bloecke:
        if isinstance(b, Tabelle):
            for zeile in b.zellen:
                for zelle in zeile:
                    if zelle.verdeckt_von is None:
                        yield from _behaelter(zelle)
        elif isinstance(b, Rahmen):
            yield from _behaelter(b)


def absaetze_in(bloecke: list) -> Iterator[Absatz]:
    """Alle Absätze einer Blockliste, auch die in Tabellen und Rahmen, in Dokumentreihenfolge."""
    for b in bloecke:
        if isinstance(b, Absatz):
            yield b
        elif isinstance(b, Rahmen):
            yield from absaetze_in(b.bloecke)
        else:
            for zeile in b.zellen:
                for zelle in zeile:
                    if zelle.verdeckt_von is None:                      # verdeckte Zellen (verbunden) halten nur einen leeren Platzhalterabsatz
                        yield from absaetze_in(zelle.bloecke)


def _tabellen(bloecke: list) -> Iterator[Tabelle]:
    for b in bloecke:
        if isinstance(b, Tabelle):
            yield b
            for zeile in b.zellen:
                for zelle in zeile:
                    yield from _tabellen(zelle.bloecke)
        elif isinstance(b, Rahmen):
            yield from _tabellen(b.bloecke)


def neues_dokument(seite: PageSettings | None = None) -> Dokument:
    """Ein leeres Dokument: ein Abschnitt mit einem leeren Absatz."""
    d = Dokument()
    d.abschnitte.append(Abschnitt(d.neue_id(), [Absatz(d.neue_id())], seite or PageSettings()))
    return d


def normalisiere(inhalte: list) -> list:
    """Leere Läufe weglassen, benachbarte Läufe mit gleichem Format zusammenziehen."""
    neu: list = []
    for x in inhalte:
        if isinstance(x, Lauf):
            if not x.text:
                continue
            if neu and isinstance(neu[-1], Lauf) and neu[-1].format == x.format:
                neu[-1] = Lauf(neu[-1].text + x.text, neu[-1].format)
                continue
            neu.append(Lauf(x.text, x.format))
        else:
            neu.append(x)
    return neu


def teile(inhalte: list, versatz: int) -> tuple:
    """Teilt eine Inhaltsliste an der Textstelle ``versatz`` in (davor, danach)."""
    davor: list = []
    danach: list = []
    rest = versatz
    for x in inhalte:
        n = len(x.text) if isinstance(x, Lauf) else 1
        if rest >= n:
            davor.append(x); rest -= n
        elif rest <= 0:
            danach.append(x)
        else:
            davor.append(Lauf(x.text[:rest], x.format)); danach.append(Lauf(x.text[rest:], x.format)); rest = 0
    return davor, danach


def format_an(absatz: Absatz, versatz: int) -> dict:
    """Das Zeichenformat, mit dem an dieser Stelle weitergeschrieben wird (das des Zeichens davor, am Absatzanfang das des ersten)."""
    rest = versatz
    for x in absatz.inhalte:
        n = len(x.text) if isinstance(x, Lauf) else 1
        if rest <= n:
            return x.format
        rest -= n
    return absatz.zeichenformat
