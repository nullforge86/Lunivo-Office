"""Platz im Seitenfluss ohne Qt: Blätter, gesetzte Zellen, Stand und Ergebnis des Laufs sowie die Platzvergabe für Absätze, Tabellenzeilen und Zellen.

Der Seitenlauf (``seitenlauf.py``, die Qt-Hülle um ``QAbstractTextDocumentLayout``) ruft diese Klassen; sie rechnen nur mit ``core.geometry.Rect``,
``PageSettings`` und Zahlen. Der Wächtertest ``tests/architektur/test_seitenplatz_ohne_qt.py`` hält das Modul frei von Qt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from lunivo_writer.core.geometry import Rect
from lunivo_writer.editor.layout.seitenplan import Bereich
from lunivo_writer.modelle.seite import PageSettings, mm_to_px

MIN_ZEILENBREITE = 40.0                 # schmaler als das darf neben einem schwebenden Rahmen keine Zeile werden (ohne Zoom)


@dataclass
class Blatt:
    """Ein Blatt des Laufs (Maße mit Zoom)."""
    index: int
    oben: float                       # y der Blattoberkante im Blattraum
    seite: PageSettings
    bereich: int                      # Index des Bereichs im Seitenplan
    zoom: float = 1.0
    x: float = 0.0                    # linker Rand des Blattes: schmalere Blätter stehen mittig unter dem breitesten
    leer: bool = False                # Leerseite vor „gerade/ungerade Seite“: bleibt weiß, ohne Kopf- und Fußzeile

    @property
    def breite(self) -> float:
        return mm_to_px(self.seite.width_mm) * self.zoom

    @property
    def hoehe(self) -> float:
        return mm_to_px(self.seite.height_mm) * self.zoom

    @property
    def text_links(self) -> float:
        return self.x + mm_to_px(self.seite.margin_left_mm) * self.zoom

    @property
    def text_oben(self) -> float:
        return mm_to_px(self.seite.margin_top_mm) * self.zoom

    @property
    def text_hoehe(self) -> float:
        return mm_to_px(self.seite.height_mm - self.seite.margin_top_mm - self.seite.margin_bottom_mm) * self.zoom

    @property
    def fluss_hoehe(self) -> float:
        """Höhe einer logischen Seite im Textfluss der Druckkopie (im Raster des Seitenumbruchs, wie ``PageSettings.content_height_px``)."""
        return self.seite.content_height_px * self.zoom

    @property
    def rechteck(self) -> Rect:
        return Rect(self.x, self.oben, self.breite, self.hoehe)


@dataclass
class Zelle:
    """Eine gesetzte Tabellenzelle für das Zeichnen: Rechteck im Blattraum, ihr Format und das der Tabelle."""
    rechteck: Rect
    format: object
    tabelle: object
    rand: float = 0.0                 # Rahmenstärke der Tabelle (mit Zoom)
    anweisungen: list | None = None   # Zeichenanweisungen für Füllung und Rahmen (beim ersten Zeichnen berechnet)


@dataclass
class _Stand:
    blatt: Blatt
    spalte: int
    y: float                          # y innerhalb der Textfläche (vom oberen Rand)
    leer: bool = True                 # steht noch nichts auf dem Blatt?
    y0: float = 0.0                   # y, an dem die Spalten des aktuellen Bereichs auf diesem Blatt beginnen


@dataclass
class _Ergebnis:
    rechtecke: dict = field(default_factory=dict)         # Blocknummer → Rect (Blattraum, Maße ohne Qt)
    block_blatt: dict = field(default_factory=dict)       # Blocknummer → Blattindex, auf dem der Block beginnt
    anfang: dict = field(default_factory=dict)            # Blocknummer → (Blattindex, Spalte, y vom oberen Textrand der Spalte) der ersten Zeile
    zellen: list = field(default_factory=list)            # gesetzte Tabellenzellen (``Zelle``), zum Zeichnen von Füllung und Rahmen
    tabellen: dict = field(default_factory=dict)          # Position des Tabellenanfangs → Rect der Tabelle
    ausschluesse: list = field(default_factory=list)      # schwebende Rahmen: (Blattindex, Spalte, Rect, 'links'|'rechts'), um die der Text läuft
    blaetter: list = field(default_factory=list)
    bereich_start: dict = field(default_factory=dict)     # Bereichsindex → Blattindex, auf dem der Bereich beginnt (Seitennummern, Leerseiten)
    fussnoten: dict = field(default_factory=dict)          # Blattindex → {"hoehe", "noten": [(y ab Textrand, Textdokument, Id)]} (ohne Zoom)
    kopien: list = field(default_factory=list)            # wiederholte Tabellenkopfzeilen: (Zelle am neuen Ort, [(Blocknummer, dx, dy)])


class _KoerperPlatz:
    """Der Platz für Absätze und Tabellenzeilen im Seitenfluss: Spalten des Bereichs, Blätter, Seitenwechsel."""

    def __init__(self, lauf, bereich: Bereich, stand: _Stand, erg: _Ergebnis):
        self.lauf, self.bereich, self.stand, self.erg = lauf, bereich, stand, erg
        self._stelle = None
        self._unten = 0.0

    def _spalte(self):
        sp = self.bereich.spalten
        return sp[min(self.stand.spalte, len(sp) - 1)]

    def breite(self) -> float:
        return self._spalte().breite * self.lauf.zoom

    def links(self) -> float:
        if self.lauf.fluss:
            return 0.0
        return self.stand.blatt.x + mm_to_px(self.bereich.seite.margin_left_mm) * self.lauf.zoom + self._spalte().x * self.lauf.zoom

    def _unten_y(self) -> float:
        """y des oberen Randes der Spalte im Koordinatensystem des Laufs."""
        st = self.stand
        if self.lauf.fluss:
            return (st.blatt.index * max(1, len(self.bereich.spalten)) + st.spalte) * self._hoehe()
        return st.blatt.oben + st.blatt.text_oben

    def _hoehe(self) -> float:
        if self.lauf.fluss:
            return self.stand.blatt.fluss_hoehe
        return self.stand.blatt.text_hoehe - self.lauf.reserve.get(self.stand.blatt.index, 0.0) * self.lauf.zoom      # unten bleibt Platz für Fußnoten

    def abstand(self, a: float, vor: bool) -> None:
        if vor:
            a, self._unten = max(0.0, a - self._unten), 0.0      # Abstand unten und Abstand oben des nächsten Absatzes fallen zusammen: der größere gilt
            if self.stand.leer:                                  # am Anfang einer Spalte oder Seite gilt der Abstand davor nicht
                return
        else:
            self._unten = a
        self.stand.y += a

    def umbruch_vor(self) -> None:
        if not self.stand.leer:
            self.stand = self.lauf._neues_blatt(self.erg, self.bereich)

    def _weiter(self) -> None:
        if self.stand.spalte + 1 < len(self.bereich.spalten):
            self.stand.spalte, self.stand.y, self.stand.leer = self.stand.spalte + 1, self.stand.y0, True
        else:
            self.stand = self.lauf._neues_blatt(self.erg, self.bereich)

    def vergeben(self, h: float) -> tuple[float, float, float]:
        """Platz für eine Zeile der Höhe ``h``; passt sie nicht mehr, beginnt die nächste Spalte oder Seite. → (linker Rand der Spalte, y, Breite)."""
        st = self.stand
        if st.y + h > self._hoehe() + 0.01 and not st.leer:
            self._weiter()
            st = self.stand
        sp = self._spalte()
        w = sp.breite * self.lauf.zoom
        for _ in range(40):                                  # Zeile neben schwebenden Rahmen: schmaler und eingerückt, oder darunter
            y = self._unten_y() + st.y
            links_ab, rechts_ab, unter = self._ausschluss(y, h, w)
            if w - links_ab - rechts_ab >= MIN_ZEILENBREITE * self.lauf.zoom or unter is None:
                break
            st.y = unter - self._unten_y()
        self._stelle = (st.blatt.index, st.spalte, st.y)
        st.y += h
        st.leer = False
        return self.links() + links_ab, y, w - links_ab - rechts_ab

    def _ausschluss(self, y: float, h: float, w: float):
        """Wie weit schwebende Rahmen die Zeile (y bis y + h) von links und rechts einengen; ``unter`` = Unterkante, falls zu wenig bleibt."""
        links, rechts, unter = 0.0, 0.0, None
        st = self.stand
        spalte_links = self.links()
        for blatt, spalte, r, seite in self.erg.ausschluesse:
            if blatt != st.blatt.index or spalte != st.spalte or r.bottom <= y or r.top >= y + h:
                continue
            if seite == "links":
                links = max(links, r.right - spalte_links)
            else:
                rechts = max(rechts, spalte_links + w - r.left)
            unter = max(unter or 0.0, r.bottom)
        return links, rechts, unter

    def zeile_vergeben(self, h: float) -> float:
        """Platz für eine Tabellenzeile der Höhe ``h`` (eine zu hohe Zeile steht trotzdem). → y der Oberkante."""
        return self.vergeben(h)[1]

    def stelle(self):
        return self._stelle

    def blatt_index(self) -> int:
        return self.stand.blatt.index


class _FreiPlatz:
    """Der Platz in einer Zelle: feste Breite, die Höhe wächst mit dem Inhalt."""

    def __init__(self, x: float, y: float, breite: float):
        self.x, self.y0, self.y, self.b = x, y, y, breite
        self._unten = 0.0

    def breite(self) -> float:
        return self.b

    def links(self) -> float:
        return self.x

    def abstand(self, a: float, vor: bool) -> None:
        if vor:
            a, self._unten = max(0.0, a - self._unten), 0.0
            if self.y == self.y0:
                return
        else:
            self._unten = a
        self.y += a

    def umbruch_vor(self) -> None:
        return None

    def vergeben(self, h: float) -> tuple[float, float, float]:
        y = self.y
        self.y += h
        return self.x, y, self.b

    def zeile_vergeben(self, h: float) -> float:
        return self.vergeben(h)[1]

    def stelle(self):
        return None

    def blatt_index(self):
        return None
