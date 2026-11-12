"""Seitenumbruch über dem Dokumentenmodell, ohne Qt.

Abschnitte (``next_page``-Art: neue Seite; ``continuous``: gleiche Seite, neue Spalteneinteilung), Spalten, Absätze (Läufe in verschiedenen Schriften, Bilder
in der Zeile, Ausrichtung, Einzüge, Abstände mit Zusammenfall, Zeilenabstand, Seitenumbruch davor/danach), Tabellen (Spaltenbreiten aus Vorgaben, verbundene Zellen,
Ausrichtung der Tabelle, Zellabstände je Seite, senkrechte Ausrichtung, Mindesthöhe der Zeile, wiederholte Kopfzeilen; eine Zeile bleibt ungeteilt, außer sie ist höher als eine Seite),
Rahmen (mit Rand, Abstand und Füllung als Block in der Spalte), Fußnoten (Platz unten auf der Seite der Marke), Endnoten (am Ende des Dokuments), schwebende Rahmen mit Textumfluss
(Text läuft links/rechts herum), Tabstopps und Absatzhintergrund.

Die Seiteneinrichtung eines Abschnitts (``Section.page``) wird nur gelesen (``width_mm``, ``height_mm``, ``margin_*_mm``, ``spaltenraster_px()``, ``content_height_px``)."""
from __future__ import annotations

from dataclasses import dataclass, field

from lunivo_writer.core.document.model import Document, Frame, Paragraph, Section, Table, TableCell, TextRun
from lunivo_writer.core.document.values import Length
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.modelle.seite import mm_to_px
from lunivo_writer.core.layout import eigenschaften as E, regeln
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine
from lunivo_writer.core.textlayout.paragraph import OBJEKT, Absatzsatz, Objekt, absatz_setzen

MM_JE_PX = 96.0 / 25.4
BLATT_ABSTAND_PX = 32.0               # grauer Zwischenraum zwischen zwei Blättern (wie der Seitenlauf, bei 100 % Zoom)
ZELLEN_ABSTAND = 4.0                  # Standard von Qt: Abstand zwischen Zelle und Inhalt
ZELLEN_ZWISCHENRAUM = 2.0
STANDARD_BILD = (64.0, 64.0)
NOTEN_ABSTAND = 3.0                   # px zwischen zwei Fußnoten
NOTEN_TRENNER = 12.0                  # px für den Trennstrich über den Fußnoten
NOTEN_SCHRIFT = 0.85                  # Fußnotenschrift im Verhältnis zur Grundschrift
NOTEN_SEITENANTEIL = 0.85             # füllen die Fußnoten mehr als diesen Teil der Seite, läuft der Rest über
P_ABSATZOPT = "user:1048614"           # Absatzoptionen "Schlüssel=Wert;…" (nur Abweichungen von der Vorgabe), siehe editor/seite/absatzopt.py
ABSCHNITT_FORTLAUFEND = ("fortlaufend", "continuous")         # Lunivo-Name und DOCX-Name: gleiche Seite, neue Spalteneinteilung
ABSCHNITT_SEITE_GERADE = ("gerade", "even_page")             # nur gerade Seiten (Leerseite davor, wenn nötig)
ABSCHNITT_SEITE_UNGERADE = ("ungerade", "odd_page")
P_ZEILE_MINHOEHE = "user:1048638"      # an jeder Zelle einer Zeile: Mindesthöhe der Zeile in Bildpunkten (``Z_MINHOEHE``, DOCX: w:trHeight)
P_ZEILE_HOEHE_ART = "user:1048639"     # DOCX-Brücke: minimum oder exact
MIN_TEILHOEHE = 40.0                  # weniger Platz als das bleibt am Seitenende: eine zu hohe Tabellenzeile beginnt erst auf der nächsten Seite
MIN_TABELLENBREITE = 20.0
MIN_SPALTENBREITE = 10.0
NOTEN_LINIE_ANTEIL = 1 / 3            # Länge des Trennstrichs über den Noten im Verhältnis zur Spaltenbreite
P_NOTE = "user:1048597"                # QTextFormat.UserProperty + 21: "f:3" (Fußnote Nr. 3) oder "e:2" (Endnote)


@dataclass
class AbsatzOrt:
    """Wo ein Absatz steht: je Zeile Seite, Spalte und Rechteck (Seitenkoordinaten, Bildpunkte)."""
    pfad: tuple
    satz: Absatzsatz
    zeilen: list[tuple[int, int, Rect]] = field(default_factory=list)       # (Seitenindex, Zeilenindex im Satz, Rechteck der Zeile auf der Seite)
    marke: str | None = None                                                 # Aufzählungszeichen oder Nummer der Liste (nur erste Zeile): "•", "◦", "▪" oder "3."
    ohne_zeilennummer: bool = False                                          # „Zeilennummern unterdrücken“ (``ohne_zeilennr`` der Absatzoptionen)
    hintergrund: tuple | None = None                                         # Füllfarbe des Absatzes (r, g, b, a)
    rahmen: str | None = None                                                # Absatzrahmen („Farbe|Breite pt|Art|Seiten|Abstände“); gleiche Angabe an Nachbarn = ein gemeinsamer Rahmen


@dataclass
class Platz:
    """Ein Stück Seite: eine Absatzzeile, eine Tabellenzelle, ein Rahmen, eine Note oder der Trennstrich über den Noten (für Zeichnen, Treffertest und Cursor)."""
    art: str                         # "zeile" | "zelle" | "rahmen" | "fussnote" | "endnote" | "notenlinie"
    rect: Rect
    pfad: tuple
    zeile: int = -1
    daten: object = None             # Zelle: (Zellformat-Eigenschaften, Tabellenformat-Eigenschaften); Rahmen: Eigenschaften; Fuß-/Endnote: der gesetzte Text (``Absatzsatz``)
    kopie: bool = False              # wiederholte Kopfzeile einer Tabelle: wird gezeichnet, zählt aber nicht für Cursor, Treffertest und Zeilennummern


@dataclass
class Seite:
    index: int
    abschnitt: int
    einrichtung: object
    plaetze: list[Platz] = field(default_factory=list)
    oben: float = 0.0                 # y der Blattoberkante im Blattraum (wie der Seitenlauf: Blätter stehen untereinander mit Abstand)


@dataclass
class Ergebnis:
    seiten: list[Seite] = field(default_factory=list)
    absaetze: dict = field(default_factory=dict)                           # Pfad → AbsatzOrt
    hinweise: list[str] = field(default_factory=list)

    def cursor(self, pfad: tuple, index: int) -> tuple[int, Point] | None:
        """Seite und Punkt (Seitenkoordinaten, obere linke Ecke der Zeile) des Cursors vor dem Zeichen ``index`` des Absatzes ``pfad``."""
        ort = self.absaetze.get(pfad)
        if ort is None:
            return None
        zi = ort.satz.zeile_von(index)
        for seite, z, r in ort.zeilen:
            if z == zi:
                return seite, Point(r.x + ort.satz.cursor_x(index, zi), r.y)
        return None

    def zeilennummern(self, art: str = ""):
        """(Seitenindex, y auf der Seite, Zeilenhöhe, Nummer) für jede nummerierte Zeile in Lesereihenfolge; ``art`` „seite“: auf jeder Seite neu ab 1.
        Absätze mit unterdrückten Zeilennummern bekommen keine und werden nicht mitgezählt."""
        nr, aktuell = 0, -1
        for seite in self.seiten:
            for p in seite.plaetze:
                if p.art != "zeile" or p.kopie or self.absaetze[p.pfad].ohne_zeilennummer:
                    continue
                if art == "seite" and seite.index != aktuell:
                    nr = 0
                aktuell = seite.index
                nr += 1
                yield seite.index, p.rect.y, p.rect.height, nr

    def treffer(self, seite: int, punkt: Point) -> tuple[tuple, int] | None:
        """Absatz (Pfad) und Zeichenstelle für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat."""
        zeilen = [p for p in self.seiten[seite].plaetze if p.art == "zeile" and not p.kopie]
        if not zeilen:
            return None

        def abstand(p: Platz) -> tuple[float, float]:
            dy = max(p.rect.y - punkt.y, 0.0, punkt.y - p.rect.bottom)
            dx = max(p.rect.x - punkt.x, 0.0, punkt.x - p.rect.right)
            return dy, dx
        best = min(zeilen, key=abstand)
        satz = self.absaetze[best.pfad].satz
        return best.pfad, satz.treffer(punkt.x - best.rect.x, satz.zeilen[best.zeile].y + 0.1)


class _Fluss:
    def __init__(self, engine: TextLayoutEngine, dok: Document):
        self.engine, self.dok = engine, dok
        self.erg = Ergebnis()
        self.grund = E.grundschrift(dok)
        self.abschnitt = -1
        self.einr = None
        self.spalten: list[tuple[float, float]] = []
        self.rand_links = self.rand_oben = 0.0
        self.hoehe = 0.0
        self.spalte = 0
        self.y = 0.0
        self.seite: Seite | None = None
        self.unten = 0.0                    # Abstand unter dem letzten Absatz (fällt mit dem oberen des nächsten zusammen)
        self.leer = True
        self.y0 = 0.0
        self.noten_text = {n.id: n.text for n in dok.notes if n.kind == "f"}
        self.noten: dict[int, list[tuple[int, int]]] = {}       # Seitenindex → [(laufende Nummer, Id)]
        self.noten_zaehler = 0
        self.listen_zaehler: dict[int, int] = {}                    # Liste → bisher gezählte Absätze (für die Nummern)
        self.ausschluesse: list = []                 # schwebende Rahmen: (Seitenindex, Spalte, Rect, 'links' | 'rechts'), um die der Text läuft
        self.endnoten: list[int] = []                # Ids der Endnoten in der Reihenfolge ihrer Marken

    # ---- Seiten und Spalten ----
    def neue_seite(self) -> None:
        oben = 0.0
        if self.erg.seiten:
            letzte = self.erg.seiten[-1]
            oben = letzte.oben + (mm_to_px(letzte.einrichtung.height_mm) if letzte.einrichtung is not None else 0.0) + BLATT_ABSTAND_PX
        self.seite = Seite(len(self.erg.seiten), self.abschnitt, self.einr, oben=oben)
        self.erg.seiten.append(self.seite)
        self.spalte, self.y, self.y0, self.leer, self.unten = 0, 0.0, 0.0, True, 0.0

    def weiter(self) -> None:
        if self.spalte + 1 < len(self.spalten):
            self.spalte += 1
            self.y, self.leer, self.unten = self.y0, True, 0.0
        else:
            self.neue_seite()

    def breite(self) -> float:
        return self.spalten[self.spalte][1]

    def links(self) -> float:
        return self.rand_links + self.spalten[self.spalte][0]

    def frei(self) -> float:
        """Höhe der Spalte auf dieser Seite abzüglich des Platzes, den die Fußnoten unten brauchen."""
        return self.hoehe - self.noten_hoehe(self.noten.get(self.seite.index, []))

    def platz_fuer(self, h: float, extra: float = 0.0) -> None:
        if self.y + h > self.frei() - extra + 0.01 and not self.leer:
            self.weiter()

    def noten_hoehe(self, eintraege: list) -> float:
        if not eintraege:
            return 0.0
        gesamt = NOTEN_TRENNER + sum(self.note_satz(nr, nid).hoehe + NOTEN_ABSTAND for nr, nid in eintraege)
        return min(gesamt, self.hoehe * NOTEN_SEITENANTEIL)

    def note_satz(self, nr: int, nid: int) -> Absatzsatz:
        breite = self.spalten[0][1] if len(self.spalten) == 1 else sum(b for _x, b in self.spalten)
        return self.noten_satz(str(nr), self.noten_text.get(nid, ""), breite)

    def noten_satz(self, marke: str, text: str, breite: float) -> Absatzsatz:
        """Eine Fuß- oder Endnote gesetzt: Marke, zwei Leerzeichen, Text in der kleineren Notenschrift."""
        g = E.schrift(None, self.grund)
        klein = FontSpec(g.family, max(6.0, g.size_pt * NOTEN_SCHRIFT), g.weight, g.italic)
        return absatz_setzen(self.engine, [(f"{marke}  {text}", klein)], breite)

    def abschnitt_beginnt(self, nr: int, s: Section) -> None:
        self.abschnitt, self.einr = nr, s.page
        p = s.page
        self.rand_links = float(getattr(p, "margin_left_mm", 20.0)) * MM_JE_PX
        self.rand_oben = float(getattr(p, "margin_top_mm", 25.0)) * MM_JE_PX
        self.hoehe = float(getattr(p, "content_height_px", 0.0)) or (float(getattr(p, "height_mm", 297.0)) - float(getattr(p, "margin_top_mm", 25.0)) - float(getattr(p, "margin_bottom_mm", 25.0))) * MM_JE_PX
        self.spalten = list(p.spaltenraster_px()) if hasattr(p, "spaltenraster_px") else [(0.0, (float(getattr(p, "width_mm", 210.0)) - float(getattr(p, "margin_left_mm", 20.0)) - float(getattr(p, "margin_right_mm", 20.0))) * MM_JE_PX)]
        fortlaufend = s.kind in ABSCHNITT_FORTLAUFEND and self.seite is not None and nr > 0
        if fortlaufend:
            self.spalte, self.y0, self.leer = 0, self.y, True       # neue Spalteneinteilung ab hier, auf derselben Seite
        else:
            self.neue_seite()
            if nr == 0 and hasattr(p, "erste_seite_versatz_px"):          # lange Kopfzeile: der Text der ersten Seite beginnt darunter
                self.y = self.y0 = float(p.erste_seite_versatz_px())
            if s.kind in ABSCHNITT_SEITE_GERADE + ABSCHNITT_SEITE_UNGERADE:
                gerade = s.kind in ABSCHNITT_SEITE_GERADE
                if (len(self.erg.seiten) % 2 == 0) != gerade:
                    self.neue_seite()                                  # Leerseite

    # ---- Blöcke ----
    @staticmethod
    def absatz_opt(p: Paragraph, name: str) -> bool:
        text = p.format.properties.get(P_ABSATZOPT)
        return isinstance(text, str) and f"{name}=1" in text.split(";")

    @staticmethod
    def absatz_regeln(p: Paragraph) -> dict:
        """Die Umbruchregeln eines Absatzes: ``kontrolle`` (Witwen/Waisen, Vorgabe an), ``nicht_trennen`` (mit dem nächsten zusammen), ``zusammen`` (Absatz nicht teilen)."""
        w = {"kontrolle": True, "nicht_trennen": False, "zusammen": False}
        text = p.format.properties.get(P_ABSATZOPT)
        for teil in (text.split(";") if isinstance(text, str) else []):
            k, _s, v = teil.partition("=")
            if k in w:
                w[k] = v == "1"
        return w

    def regeln_an(self) -> bool:
        """Die Umbruchregeln gelten im Seitenfluss mit gleich breiten Spalten (nicht in Zellen und Rahmen)."""
        return self.seite is not None and self.seite.index >= 0 and len({round(b, 1) for _x, b in self.spalten}) == 1

    def umbruch_stelle(self, hs: list[float], w: dict, folge: list) -> int | None:
        """Wo beginnt die nächste Spalte oder Seite, damit die Umbruchregeln gelten (``regeln.umbruch_stelle``)? ``None``: kein Umbruch nötig."""
        def naechste():
            for b in folge:
                if not isinstance(b, Paragraph):
                    return
                satz, (oben, _u) = self.satz(b, self.breite())
                yield self.absatz_regeln(b), [z.hoehe for z in satz.zeilen], oben
        return regeln.umbruch_stelle(hs, w, self.frei() - self.y, self.frei(), self.leer, naechste)

    def blocks(self, bloecke: list, pfad: tuple) -> None:
        for i, b in enumerate(bloecke):
            if isinstance(b, Paragraph):
                self.absatz(b, pfad + (i,), bloecke[i + 1:i + 5])
            elif isinstance(b, Table):
                self.tabelle(b, pfad + (i,))
            elif isinstance(b, Frame):
                self.rahmen(b, pfad + (i,))

    def ausschluss_fuer(self):
        """Funktion (y, h) → (Einengung links, Einengung rechts, Unterkante): wie weit schwebende Rahmen die Zeilen ab dem jetzigen Stand einengen."""
        y0, seite, spalte = self.y, self.seite.index, self.spalte
        links_x, breite = self.links(), self.breite()
        oben = self.rand_oben

        def ausschluss(y: float, h: float):
            ya = oben + y0 + y
            links = rechts = 0.0
            unter = None
            for si, sp, r, art in self.ausschluesse:
                if si != seite or sp != spalte or r.bottom <= ya or r.y >= ya + h:
                    continue
                if art == "links":
                    links = max(links, r.right - links_x)
                else:
                    rechts = max(rechts, links_x + breite - r.x)
                unter = max(unter or 0.0, r.bottom - oben - y0)
            return links, rechts, unter
        return ausschluss

    def satz(self, p: Paragraph, breite: float, ausschluss=None) -> tuple[Absatzsatz, tuple[float, float]]:
        laeufe: list = []
        for r in p.runs:
            if isinstance(r, TextRun):
                if r.text:
                    schrift, stil = E.schrift(r.format, self.grund), E.stil(r.format, self.grund)
                    if E.kapitaelchen(r.format, self.grund):
                        laeufe.extend((t, f, stil) for t, f in E.kapitaelchen_stuecke(r.text, schrift))
                    else:
                        laeufe.append((E.schreibweise(r.text, r.format, self.grund), schrift, stil))
            else:
                b = E._zahl(r.format.properties.get("ImageWidth"), STANDARD_BILD[0])
                h = E._zahl(r.format.properties.get("ImageHeight"), STANDARD_BILD[1])
                laeufe.append((OBJEKT, Objekt(b, h), {"bild": r.original if r.original and r.original_format == "svg" else r.raster_png}))
        links, rechts, erste = E.einzuege(p.format, self.dok.indent_width)
        if p.format.list_id is not None and p.format.list_id in self.dok.lists:         # Aufzählung: Einrückung der Liste kommt zum linken Rand
            links += E._zahl(self.dok.lists[p.format.list_id].properties.get("ListIndent")) * self.dok.indent_width
        art, wert = E.zeilenabstand(p.format)
        leer = E.schrift(p.format.char_format, self.grund)
        tabs, tab_abstand = E.tabstopps(p.format, self.dok)
        return absatz_setzen(self.engine, laeufe, breite, E.ausrichtung(p.format), erste, links, rechts, art, wert, leer, ausschluss, tabs, tab_abstand,
                             E.tabfuellung(p.format)), E.abstaende(p.format)

    @staticmethod
    def marken_von(p: Paragraph, art: str = "f") -> list[tuple[int, int]]:
        """[(Zeichenstelle, Noten-Id)] der Notenmarken im Absatz; ``art`` „f“ Fußnoten, „e“ Endnoten."""
        res, pos = [], 0
        for r in p.runs:
            if isinstance(r, TextRun):
                v = r.format.properties.get(P_NOTE)
                if isinstance(v, str) and v.startswith(art + ":") and v[2:].isdigit():
                    res.append((pos, int(v[2:])))
                pos += len(r.text)
            else:
                pos += 1
        return res

    def listenmarke(self, p: Paragraph) -> str | None:
        """Aufzählungszeichen oder Nummer des Absatzes in seiner Liste (zählt die Absätze der Liste in Dokumentreihenfolge)."""
        lid = p.format.list_id
        if lid is None or lid not in self.dok.lists:
            return None
        n = self.listen_zaehler[lid] = self.listen_zaehler.get(lid, 0) + 1
        eig = self.dok.lists[lid].properties
        return E.listenzeichen(int(E._zahl(eig.get("ListStyle"), -4)), n, str(eig.get("ListNumberPrefix") or ""), str(eig.get("ListNumberSuffix", ".")))

    def absatz(self, p: Paragraph, pfad: tuple, folge: list = ()) -> None:
        if not p.format.visible:
            return
        if E.umbruch_vor(p.format) and not self.leer:
            self.neue_seite()
        oben, unten = E.abstaende(p.format)
        if not self.leer:                                                  # Abstand oben und unten fallen zusammen: der größere gilt; am Spaltenanfang entfällt er
            self.y += max(0.0, oben - self.unten)
        satz, _ = self.satz(p, self.breite(), self.ausschluss_fuer() if self.ausschluesse else None)
        ort = AbsatzOrt(pfad, satz, marke=self.listenmarke(p), ohne_zeilennummer=self.absatz_opt(p, "ohne_zeilennr"), hintergrund=E.hintergrund(p.format), rahmen=E.absatzrahmen(p.format))
        self.erg.absaetze[pfad] = ort
        self.endnoten.extend(nid for _stelle, nid in self.marken_von(p, "e"))
        marken = self.marken_von(p)
        bruch = self.umbruch_stelle([z.hoehe for z in satz.zeilen], self.absatz_regeln(p), list(folge)) if self.regeln_an() and satz.zeilen else None
        for i, z in enumerate(satz.zeilen):
            if i == bruch and not self.leer:
                self.weiter()
            neu = [(m) for stelle, m in marken if z.box.start <= stelle < z.ende and m in self.noten_text]
            extra = 0.0
            if neu and self.seite.index >= 0:
                bisher = self.noten.get(self.seite.index, [])
                extra = self.noten_hoehe(bisher + [(0, nid) for nid in neu]) - self.noten_hoehe(bisher)
            self.platz_fuer(z.hoehe, extra)
            if neu and self.seite.index >= 0:
                for nid in neu:
                    self.noten_zaehler += 1
                    self.noten.setdefault(self.seite.index, []).append((self.noten_zaehler, nid))
            r = Rect(self.links(), self.rand_oben + self.y, self.breite(), z.hoehe)
            ort.zeilen.append((self.seite.index, i, r))
            self.seite.plaetze.append(Platz("zeile", r, pfad, i))
            self.y += z.hoehe
            self.leer = False
        self.unten = unten
        self.y += unten
        if E.umbruch_nach(p.format):
            self.neue_seite()

    # ---- Teilflüsse (Zelle, Rahmen) ----
    def teilfluss(self, bloecke: list, breite: float, pfad: tuple) -> tuple[float, list[Platz]]:
        """Blöcke in einer festen Breite setzen (Zelle, Rahmen): → (Höhe, Plätze relativ zur oberen linken Ecke). Die Absätze werden mit ihren Sätzen vermerkt, ihre Rechtecke setzt der Aufrufer."""
        fl = _Fluss(self.engine, self.dok)
        fl.spalten, fl.hoehe, fl.rand_links, fl.rand_oben = [(0.0, breite)], 1e12, 0.0, 0.0
        fl.seite = Seite(-1, self.abschnitt, self.einr)
        fl.abschnitt, fl.einr = self.abschnitt, self.einr
        fl.noten_text = {}
        fl.listen_zaehler = self.listen_zaehler                             # Listen zählen über Zellen und Rahmen hinweg weiter
        fl.blocks(bloecke, pfad)
        for k, v in fl.erg.absaetze.items():
            v.zeilen = []                                                   # die Rechtecke der Zeilen setzt der Aufrufer an ihrem Ort auf der Seite
            self.erg.absaetze[k] = v
        for h in fl.erg.hinweise:
            if h not in self.erg.hinweise:
                self.erg.hinweise.append(h)
        self.endnoten.extend(fl.endnoten)
        return fl.y, fl.seite.plaetze

    def auf_seite_setzen(self, plaetze: list[Platz], dx: float, dy: float, seite: Seite | None = None, kopie: bool = False) -> None:
        """Plätze aus einem Teilfluss (Zeilen, Zellen und Rahmen darin) an ihren Ort auf der Seite verschieben und eintragen."""
        seite = seite or self.seite
        for p in plaetze:
            r = Rect(dx + p.rect.x, dy + p.rect.y, p.rect.width, p.rect.height)
            ist_kopie = kopie or p.kopie
            seite.plaetze.append(Platz(p.art, r, p.pfad, p.zeile, p.daten, ist_kopie))
            ort = self.erg.absaetze.get(p.pfad) if p.art == "zeile" and not ist_kopie else None
            if ort is not None:
                ort.zeilen.append((seite.index, p.zeile, r))

    def abstand_vor(self, a: float) -> None:
        """Abstand vor einem Block: fällt mit dem Abstand unter dem vorigen zusammen und entfällt am Anfang der Spalte."""
        a, self.unten = max(0.0, a - self.unten), 0.0
        if not self.leer:
            self.y += a

    # ---- Rahmen ----
    def rahmen(self, fr: Frame, pfad: tuple) -> None:
        """Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum.
        Sonst: Block in der Spalte mit Rand, Rahmenstrich, Innenabstand und Füllung; ein Rahmen ohne all das (oder höher als die Spalte) fließt wie sein Inhalt."""
        eig = fr.properties
        art = {1: "links", 2: "rechts"}.get(int(E._zahl(eig.get("CssFloat"))))
        rand = max(0.0, E._zahl(eig.get("FrameMargin")))
        innen = max(0.0, E._zahl(eig.get("FramePadding"))) + max(0.0, E._zahl(eig.get("FrameBorder")))
        w_fest, h_fest = eig.get("FrameWidth"), eig.get("FrameHeight")
        fest = E.laenge(w_fest, self.breite()) if isinstance(w_fest, Length) else None
        im_fluss = self.seite is not None and self.seite.index >= 0
        if art is None or not im_fluss:
            schlicht = rand == 0 and innen == 0 and fest is None and E._brush_farbe(eig.get("BackgroundBrush")) is None
            if schlicht:
                self.blocks(fr.content, pfad)
                return
            breite = max(MIN_SPALTENBREITE, min(fest, self.breite() - 2 * rand) - 2 * innen if fest is not None else self.breite() - 2 * rand - 2 * innen)
            zaehler = dict(self.listen_zaehler)
            h, plaetze = self.teilfluss(fr.content, breite, pfad)
            hoehe = max(h, E.laenge(h_fest, h) or 0.0) if isinstance(h_fest, Length) else h
            aussen_h = hoehe + 2 * innen
            if im_fluss and aussen_h + 2 * rand > self.frei():             # höher als die Spalte: der Inhalt fließt über die Seiten
                self.listen_zaehler.clear()
                self.listen_zaehler.update(zaehler)
                self.blocks(fr.content, pfad)
                return
            self.abstand_vor(rand)
            self.platz_fuer(aussen_h + rand)
            x, y = self.links() + rand, self.rand_oben + self.y
            self.seite.plaetze.append(Platz("rahmen", Rect(x, y, breite + 2 * innen, aussen_h), pfad, daten=eig))
            self.auf_seite_setzen(plaetze, x + innen, y + innen)
            self.y += aussen_h + rand
            self.unten, self.leer = rand, False
            return
        breite = fest if fest is not None else self.breite() / 3
        h, plaetze = self.teilfluss(fr.content, max(MIN_SPALTENBREITE, breite), pfad)
        hoehe = h_fest.value if getattr(h_fest, "kind", "") == "fixed" else h
        links = self.links()
        x = links + rand if art == "links" else links + self.breite() - breite - 2 * innen - rand
        y = self.rand_oben + self.y + rand
        self.seite.plaetze.append(Platz("rahmen", Rect(x, y, breite + 2 * innen, hoehe + 2 * innen), pfad, daten=eig))
        self.auf_seite_setzen(plaetze, x + innen, y + innen)
        self.ausschluesse.append((self.seite.index, self.spalte, Rect(x - rand, y - rand, breite + 2 * innen + 2 * rand, hoehe + 2 * innen + 2 * rand), art))

    # ---- Tabellen ----
    @staticmethod
    def tabellenbreite(eig: dict, verfuegbar: float) -> float:
        w = eig.get("FrameWidth", eig.get("TableWidth"))
        if isinstance(w, Length) and w.kind == "fixed":
            return min(verfuegbar, max(MIN_TABELLENBREITE, w.value))
        if isinstance(w, Length) and w.kind == "percentage":
            return max(MIN_TABELLENBREITE, verfuegbar * w.value / 100.0)
        return verfuegbar

    @staticmethod
    def spaltenbreiten(t: Table, breite_tab: float, luecke: float) -> list[float]:
        """Spaltenbreiten aus den Vorgaben (fest, Prozent, frei): freie Spalten teilen sich den Rest; passt die Summe nicht, wird auf die Tabellenbreite gebracht."""
        n = t.columns
        vorgaben = list(t.properties.get("TableColumnWidthConstraints") or ())[:n]
        vorgaben += [None] * (n - len(vorgaben))
        innen = max(MIN_SPALTENBREITE, breite_tab - luecke * (n + 1))
        b, frei = [0.0] * n, []
        for i, v in enumerate(vorgaben):
            if isinstance(v, Length) and v.kind == "fixed":
                b[i] = v.value
            elif isinstance(v, Length) and v.kind == "percentage":
                b[i] = innen * v.value / 100.0
            else:
                frei.append(i)
        rest = innen - sum(b)
        for i in frei:
            b[i] = max(MIN_SPALTENBREITE, rest / len(frei)) if rest > 0 else MIN_SPALTENBREITE
        summe = sum(b)
        if summe > 0 and abs(summe - innen) > 0.5 and (summe > innen or not frei):
            b = [w * innen / summe for w in b]
        return b

    def tabelle(self, t: Table, pfad: tuple) -> None:
        """Eine Tabelle setzen: Spaltenbreiten aus den Vorgaben, Zeilenhöhen aus dem Inhalt (und der Mindesthöhe), Zeilen untereinander. Passt eine Zeile nicht mehr, beginnt sie in der
        nächsten Spalte oder Seite; dort stehen die Kopfzeilen noch einmal. Eine Zeile, die höher ist als eine ganze Seite, wird zwischen ihren Textzeilen geteilt."""
        if not t.columns or not t.rows:
            return
        eig = t.properties
        aussen = max(0.0, E._zahl(eig.get("FrameMargin")))
        luecke = max(0.0, E._zahl(eig.get("TableCellSpacing"), ZELLEN_ZWISCHENRAUM))
        polster = max(0.0, E._zahl(eig.get("TableCellPadding"), ZELLEN_ABSTAND))
        rand = max(0.0, E._zahl(eig.get("FrameBorder")))
        verfuegbar = max(MIN_TABELLENBREITE, self.breite() - 2 * aussen)
        breite_tab = self.tabellenbreite(eig, verfuegbar)
        breiten = self.spaltenbreiten(t, breite_tab, luecke)
        xs = [luecke]
        for b in breiten[:-1]:
            xs.append(xs[-1] + b + luecke)
        ausr = int(E._zahl(eig.get("BlockAlignment")))
        frei_b = max(0.0, verfuegbar - breite_tab)
        dx_tab = aussen + (frei_b / 2 if ausr & E.MITTE else frei_b if ausr & E.RECHTS else 0.0)

        def breite_von(c: TableCell) -> float:
            return sum(breiten[c.column:c.column + c.column_span]) + luecke * (c.column_span - 1)

        def innen(c: TableCell) -> tuple[float, float, float, float]:
            def pad(name: str) -> float:
                v = c.properties.get(f"TableCell{name}Padding")
                return max(0.0, E._zahl(v)) if v is not None else polster
            return pad("Left"), pad("Top"), pad("Right"), pad("Bottom")

        def zelle_platz(c: TableCell, seite: Seite, links: float, y: float, h: float, kopie: bool = False) -> Rect:
            zr = Rect(links + dx_tab + xs[c.column], y, breite_von(c), h)
            zeile = t.table_rows[c.row] if c.row < len(t.table_rows) else None
            seite.plaetze.append(Platz("zelle", zr, pfad + (c.row, c.column), daten=(c.properties, eig, zeile.row_height if zeile else None), kopie=kopie))
            return zr

        zellen: list[TableCell] = []
        inhalt: dict[int, tuple[float, list[Platz]]] = {}
        hoehen = [0.0] * t.rows
        for ri, zeile in enumerate(t.table_rows):
            rohe_mindesthoehe = max((E._zahl(c.properties.get(P_ZEILE_MINHOEHE)) for c in zeile.cells), default=0.0)
            row_height = zeile.row_height
            mindesthoehe = (row_height.value_px if row_height is not None else
                            zeile.minimum_height_px if zeile.minimum_height_px is not None else rohe_mindesthoehe)
            for ci, c in enumerate(zeile.cells):
                l, o, r, u = innen(c)
                inhalt[id(c)] = self.teilfluss(c.content, max(MIN_SPALTENBREITE, breite_von(c) - l - r - rand), pfad + (ri, ci))
                zellen.append(c)
                if c.row_span == 1 and c.row < t.rows:
                    inhaltshoehe = inhalt[id(c)][0] + o + u + rand
                    hoehen[c.row] = max(hoehen[c.row], mindesthoehe if row_height is not None and row_height.kind == "exact" else max(inhaltshoehe, mindesthoehe))
        ueberspannt: set[int] = set()
        for c in zellen:
            if c.row_span > 1:
                _l, o, _r, u = innen(c)
                letzte = min(t.rows - 1, c.row + c.row_span - 1)
                ueberspannt.update(range(c.row, letzte + 1))
                fehlt = inhalt[id(c)][0] + o + u + rand - sum(hoehen[c.row:letzte + 1]) - luecke * (letzte - c.row)
                if fehlt > 0:                                               # fehlende Höhe geht an die letzte Zeile der Zelle
                    hoehen[letzte] += fehlt
        im_fluss = self.seite.index >= 0
        kopf_n = min(max(0, int(E._zahl(eig.get("TableHeaderRowCount")))), t.rows - 1) if im_fluss else 0
        self.abstand_vor(aussen + luecke + rand)
        orte: list = [None] * t.rows                                        # je Zeile (Seite, linker Rand der Spalte, y auf der Seite)
        kopien: list[list] = []                                             # je Seitenwechsel die Orte der wiederholten Kopfzeilen
        geteilt: set[int] = set()
        for r in range(t.rows):
            h = hoehen[r]
            passt_nicht = self.y + h + luecke > self.frei() + 0.01
            if im_fluss and passt_nicht and h + luecke > self.frei() and r not in ueberspannt:
                self.zeile_teilen([c for c in zellen if c.row == r], inhalt, innen, zelle_platz, rand, luecke)
                geteilt.add(r)
                continue
            if kopf_n and r >= kopf_n and not self.leer and passt_nicht and sum(hoehen[:kopf_n]) + h < self.frei():
                self.weiter()                                               # die Zeile steht auf der nächsten Seite: die Kopfzeilen davor wiederholen
                neu = []
                for k in range(kopf_n):
                    neu.append((self.seite, self.links(), self.rand_oben + self.y))
                    self.y += hoehen[k] + luecke
                self.leer = False
                kopien.append(neu)
            else:
                self.platz_fuer(h + luecke)
            orte[r] = (self.seite, self.links(), self.rand_oben + self.y)
            self.y += h + luecke
            self.leer = False
        for c in zellen:
            if c.row in geteilt or c.row >= t.rows:
                continue
            seite, links, y0 = orte[c.row]
            bis = min(t.rows - 1, c.row + c.row_span - 1)
            h = hoehen[c.row]
            if bis > c.row and orte[bis] is not None and orte[bis][0] is seite and orte[bis][2] > y0:      # über einen Seitenwechsel reicht die Zelle nur bis zum Ende ihrer ersten Zeile
                h = orte[bis][2] + hoehen[bis] - y0
            l, o, _r, u = innen(c)
            zr = zelle_platz(c, seite, links, y0, h)
            h_inhalt, plaetze = inhalt[id(c)]
            frei_h = max(0.0, h - o - u - rand - h_inhalt)
            senkrecht = int(E._zahl(c.properties.get("TextVerticalAlignment")))
            versatz = frei_h / 2 if senkrecht == E.SENKRECHT_MITTE else frei_h if senkrecht == E.SENKRECHT_UNTEN else 0.0
            self.auf_seite_setzen(plaetze, zr.x + rand / 2 + l, zr.y + rand / 2 + o + versatz, seite)
        for neu in kopien:
            for c in zellen:
                if c.row < kopf_n and c.row_span == 1:
                    seite, links, y = neu[c.row]
                    l, o, _r, _u = innen(c)
                    zr = zelle_platz(c, seite, links, y, hoehen[c.row], kopie=True)
                    self.auf_seite_setzen(inhalt[id(c)][1], zr.x + rand / 2 + l, zr.y + rand / 2 + o, seite, kopie=True)
        self.unten = aussen + rand
        self.y += self.unten

    def zeile_teilen(self, zellen: list[TableCell], inhalt: dict, innen, zelle_platz, rand: float, luecke: float) -> None:
        """Eine Tabellenzeile, die höher ist als eine ganze Seite, über mehrere Seiten setzen: je Seite so viele Zeilen jeder Zelle, wie passen; die Zelle steht auf jeder Seite mit ihrem Teil."""
        rest = {id(c): list(inhalt[id(c)][1]) for c in zellen}
        ab = {id(c): 0.0 for c in zellen}                                   # bis zu dieser Höhe ist der Inhalt der Zelle gesetzt
        while True:
            raum = self.frei() - self.y - luecke
            if raum < MIN_TEILHOEHE and not self.leer:
                self.weiter()
                continue
            teile, teil_h, fertig = [], 0.0, True
            for c in zellen:
                _l, o, _r, u = innen(c)
                liste = rest[id(c)]
                grenze = ab[id(c)] + raum - o - u - rand
                n = 0
                while n < len(liste) and liste[n].rect.bottom <= grenze + 0.01:
                    n += 1
                if n == 0 and liste and self.leer:                          # passt auf keine Seite: das erste Stück (mit allem, was darin liegt) steht trotzdem hier
                    n = 1
                    while n < len(liste) and liste[n].rect.bottom <= liste[0].rect.bottom + 0.01:
                        n += 1
                nimm, rest[id(c)] = liste[:n], liste[n:]
                unten = max((p.rect.bottom for p in nimm), default=ab[id(c)])
                teile.append((c, nimm, ab[id(c)]))
                teil_h = max(teil_h, unten - ab[id(c)] + o + u + rand)
                if rest[id(c)]:
                    fertig = False
                    ab[id(c)] = min(p.rect.y for p in rest[id(c)])
            if not fertig and not self.leer and not any(nimm for _c, nimm, _a in teile):
                for c, _nimm, a in teile:
                    ab[id(c)] = a
                self.weiter()
                continue
            if not fertig:
                teil_h = max(teil_h, raum)                                  # die Zelle reicht bis zum Seitenende
            y0 = self.rand_oben + self.y
            for c, nimm, a in teile:
                l, o, _r, _u = innen(c)
                zr = zelle_platz(c, self.seite, self.links(), y0, teil_h)
                self.auf_seite_setzen(nimm, zr.x + rand / 2 + l, zr.y + rand / 2 + o - a)
            self.y += teil_h + luecke
            self.leer = False
            if fertig:
                return
            self.weiter()

    # ---- Endnoten ----
    def endnoten_setzen(self) -> None:
        """Die Endnoten am Ende des Dokuments: Trennstrich, dann jede Note mit kleiner römischer Nummer in der Reihenfolge ihrer Marken; sie fließen wie Text über die Seiten."""
        texte = {n.id: n.text for n in self.dok.notes if n.kind == "e"}
        ids = [nid for nid in dict.fromkeys(self.endnoten) if nid in texte]
        if not ids or self.seite is None:
            return
        erste = self.noten_satz(E._roemisch(1), texte[ids[0]], self.breite())
        self.abstand_vor(NOTEN_TRENNER)
        self.platz_fuer(erste.zeilen[0].hoehe)
        self.seite.plaetze.append(Platz("notenlinie", Rect(self.links(), self.rand_oben + self.y - NOTEN_TRENNER / 2, self.breite() * NOTEN_LINIE_ANTEIL, 0.0), ("note",)))
        for n, nid in enumerate(ids, 1):
            satz = self.noten_satz(E._roemisch(n), texte[nid], self.breite())
            for i, z in enumerate(satz.zeilen):
                self.platz_fuer(z.hoehe)
                self.seite.plaetze.append(Platz("endnote", Rect(self.links(), self.rand_oben + self.y, self.breite(), z.hoehe), ("note", nid), i, satz))
                self.y += z.hoehe
                self.leer = False
            self.y += NOTEN_ABSTAND

def _noten_platzieren(self) -> None:
    """Die Fußnoten unten auf jede Seite mit Marken setzen (Rechtecke in Seitenkoordinaten)."""
    for index, eintraege in self.noten.items():
        seite = self.erg.seiten[index]
        unten = self.rand_oben + self.hoehe
        y = unten - self.noten_hoehe(eintraege) + NOTEN_TRENNER
        seite.plaetze.append(Platz("notenlinie", Rect(self.rand_links, y - NOTEN_TRENNER / 2, self.spalten[0][1] * NOTEN_LINIE_ANTEIL, 0.0), ("note",)))
        for nr, nid in eintraege:
            satz = self.note_satz(nr, nid)
            seite.plaetze.append(Platz("fussnote", Rect(self.rand_links, y, self.spalten[0][1], satz.hoehe), ("note", nid), 0, satz))
            y += satz.hoehe + NOTEN_ABSTAND


_Fluss.noten_platzieren = _noten_platzieren


def hoehe_von_bloecken(dok: Document, engine: TextLayoutEngine, bloecke: list, breite: float) -> float:
    """Summe der Zeilenhöhen der Absätze in den Blöcken bei der festen Breite ``breite`` (ohne Absatzabstände): wie ``QTextDocumentLayout.blockBoundingRect`` summiert,
    zum Beispiel für den Inhalt einer Tabellenzelle."""
    fluss = _Fluss(engine, dok)
    fluss.teilfluss(bloecke, breite, ())
    return sum(ort.satz.hoehe for ort in fluss.erg.absaetze.values())


def umbrechen(dok: Document, engine: TextLayoutEngine) -> Ergebnis:
    """Das Dokument auf Seiten legen. ``engine`` liefert Schriftmaße und Vorschübe (zum Beispiel ``HarfBuzzEngine``)."""
    f = _Fluss(engine, dok)
    for nr, s in enumerate(dok.sections):
        f.abschnitt_beginnt(nr, s)
        f.blocks(s.content, (nr,))
    if not f.erg.seiten:
        f.neue_seite()
    f.endnoten_setzen()
    f.noten_platzieren()
    return f.erg
