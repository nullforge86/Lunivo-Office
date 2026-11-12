"""Seitenumbruch über dem Dokumentenmodell, ohne Qt.

Abschnitte (``next_page``-Art: neue Seite; ``continuous``: gleiche Seite, neue Spalteneinteilung), Spalten, Absätze (Läufe in verschiedenen Schriften, Bilder
in der Zeile, Ausrichtung, Einzüge, Abstände mit Zusammenfall, Zeilenabstand, Seitenumbruch davor/danach), Tabellen (Spaltenbreiten aus Vorgaben, verbundene Zellen,
Zeilen wandern ungeteilt auf die nächste Seite) und Rahmen (als Block in der Spalte), Fußnoten (Platz unten auf der Seite der Marke), schwebende Rahmen mit Textumfluss (Text läuft links/rechts herum). Nicht berücksichtigt wird und in ``Ergebnis.hinweise`` gemeldet:
Endnoten.

Die Seiteneinrichtung eines Abschnitts (``Section.page``) wird nur gelesen (``width_mm``, ``height_mm``, ``margin_*_mm``, ``spaltenraster_px()``, ``content_height_px``)."""
from __future__ import annotations

from dataclasses import dataclass, field

from lunivo_writer.core.document.model import Document, Frame, Image, Paragraph, Section, Table, TableCell, TextRun
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.layout import eigenschaften as E, regeln
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine
from lunivo_writer.core.textlayout.paragraph import OBJEKT, Absatzsatz, Objekt, absatz_setzen

MM_JE_PX = 96.0 / 25.4
ZELLEN_ABSTAND = 4.0                  # Standard von Qt: Abstand zwischen Zelle und Inhalt
ZELLEN_ZWISCHENRAUM = 2.0
STANDARD_BILD = (64.0, 64.0)
NOTEN_ABSTAND = 3.0                   # px zwischen zwei Fußnoten
NOTEN_TRENNER = 12.0                  # px für den Trennstrich über den Fußnoten
NOTEN_SCHRIFT = 0.85                  # Fußnotenschrift im Verhältnis zur Grundschrift
NOTEN_SEITENANTEIL = 0.85             # füllen die Fußnoten mehr als diesen Teil der Seite, läuft der Rest über
P_ABSATZOPT = "user:1048614"           # Absatzoptionen "Schlüssel=Wert;…" (nur Abweichungen von der Vorgabe), siehe editor/seite/absatzopt.py
P_NOTE = "user:21"                    # Eigenschaft des Textstücks mit der Notenmarke: "f:3" (Fußnote Nr. 3) oder "e:2" (Endnote)


@dataclass
class AbsatzOrt:
    """Wo ein Absatz steht: je Zeile Seite, Spalte und Rechteck (Seitenkoordinaten, Bildpunkte)."""
    pfad: tuple
    satz: Absatzsatz
    zeilen: list[tuple[int, int, Rect]] = field(default_factory=list)       # (Seitenindex, Zeilenindex im Satz, Rechteck der Zeile auf der Seite)
    marke: str | None = None                                                 # Aufzählungszeichen oder Nummer der Liste (nur erste Zeile): "•", "◦", "▪" oder "3."
    ohne_zeilennummer: bool = False                                          # „Zeilennummern unterdrücken“ (``ohne_zeilennr`` der Absatzoptionen)


@dataclass
class Platz:
    """Ein Stück Seite: eine Absatzzeile, eine Tabellenzelle oder ein Rahmen (für Zeichnen, Treffertest und Cursor)."""
    art: str                         # "zeile" | "zelle" | "tabelle"
    rect: Rect
    pfad: tuple
    zeile: int = -1
    daten: object = None             # Zelle: (Zellformat-Eigenschaften, Tabellenformat-Eigenschaften); Fußnote: der gesetzte Text (``Absatzsatz``)


@dataclass
class Seite:
    index: int
    abschnitt: int
    einrichtung: object
    plaetze: list[Platz] = field(default_factory=list)


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
                if p.art != "zeile" or self.absaetze[p.pfad].ohne_zeilennummer:
                    continue
                if art == "seite" and seite.index != aktuell:
                    nr = 0
                aktuell = seite.index
                nr += 1
                yield seite.index, p.rect.y, p.rect.height, nr

    def treffer(self, seite: int, punkt: Point) -> tuple[tuple, int] | None:
        """Absatz (Pfad) und Zeichenstelle für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat."""
        zeilen = [p for p in self.seiten[seite].plaetze if p.art == "zeile"]
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

    # ---- Seiten und Spalten ----
    def neue_seite(self) -> None:
        self.seite = Seite(len(self.erg.seiten), self.abschnitt, self.einr)
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
        g = E.schrift(None, self.grund)
        klein = FontSpec(g.family, max(6.0, g.size_pt * NOTEN_SCHRIFT), g.weight, g.italic)
        breite = self.spalten[0][1] if len(self.spalten) == 1 else sum(b for _x, b in self.spalten)
        return absatz_setzen(self.engine, [(f"{nr}  {self.noten_text.get(nid, '')}", klein)], breite)

    def abschnitt_beginnt(self, nr: int, s: Section) -> None:
        self.abschnitt, self.einr = nr, s.page
        p = s.page
        self.rand_links = float(getattr(p, "margin_left_mm", 20.0)) * MM_JE_PX
        self.rand_oben = float(getattr(p, "margin_top_mm", 25.0)) * MM_JE_PX
        self.hoehe = float(getattr(p, "content_height_px", 0.0)) or (float(getattr(p, "height_mm", 297.0)) - float(getattr(p, "margin_top_mm", 25.0)) - float(getattr(p, "margin_bottom_mm", 25.0))) * MM_JE_PX
        self.spalten = list(p.spaltenraster_px()) if hasattr(p, "spaltenraster_px") else [(0.0, (float(getattr(p, "width_mm", 210.0)) - float(getattr(p, "margin_left_mm", 20.0)) - float(getattr(p, "margin_right_mm", 20.0))) * MM_JE_PX)]
        fortlaufend = s.kind == "continuous" and self.seite is not None and nr > 0
        if fortlaufend:
            self.spalte, self.y0, self.leer = 0, self.y, True       # neue Spalteneinteilung ab hier, auf derselben Seite
            self.seite.einrichtung = self.seite.einrichtung
        else:
            self.neue_seite()
            if nr == 0 and hasattr(p, "erste_seite_versatz_px"):          # lange Kopfzeile: der Text der ersten Seite beginnt darunter
                self.y = self.y0 = float(p.erste_seite_versatz_px())
            if s.kind in ("even_page", "odd_page"):
                gerade = s.kind == "even_page"
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
                    laeufe.append((r.text, E.schrift(r.format, self.grund), E.stil(r.format, self.grund)))
            else:
                b = E._zahl(r.format.properties.get("ImageWidth"), STANDARD_BILD[0])
                h = E._zahl(r.format.properties.get("ImageHeight"), STANDARD_BILD[1])
                laeufe.append((OBJEKT, Objekt(b, h), {"bild": r.original if r.original and r.original_format == "svg" else r.raster_png}))
        links, rechts, erste = E.einzuege(p.format, self.dok.indent_width)
        if p.format.list_id is not None and p.format.list_id in self.dok.lists:         # Aufzählung: Einrückung der Liste kommt zum linken Rand
            links += E._zahl(self.dok.lists[p.format.list_id].properties.get("ListIndent")) * self.dok.indent_width
        art, wert = E.zeilenabstand(p.format)
        leer = E.schrift(p.format.char_format, self.grund)
        return absatz_setzen(self.engine, laeufe, breite, E.ausrichtung(p.format), erste, links, rechts, art, wert, leer, ausschluss), E.abstaende(p.format)

    @staticmethod
    def marken_von(p: Paragraph) -> list[tuple[int, int]]:
        """[(Zeichenstelle, Fußnoten-Id)] der Notenmarken im Absatz."""
        res, pos = [], 0
        for r in p.runs:
            if isinstance(r, TextRun):
                v = r.format.properties.get(P_NOTE)
                if isinstance(v, str) and v.startswith("f:") and v[2:].isdigit():
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
        ort = AbsatzOrt(pfad, satz, marke=self.listenmarke(p), ohne_zeilennummer=self.absatz_opt(p, "ohne_zeilennr"))
        self.erg.absaetze[pfad] = ort
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

    # ---- Tabellen ----
    def spaltenbreiten(self, t: Table, gesamt: float) -> list[float]:
        vorgaben = t.properties.get("TableColumnWidthConstraints") or ()
        feste = [E.laenge(v, gesamt) for v in vorgaben][: t.columns]
        feste += [None] * (t.columns - len(feste))
        rest = gesamt - sum(f for f in feste if f is not None)
        offen = [i for i, f in enumerate(feste) if f is None]
        if offen:
            je = max(0.0, rest) / len(offen)
            feste = [f if f is not None else je for f in feste]
        elif sum(feste) > 0:
            k = gesamt / sum(feste)
            feste = [f * k for f in feste]
        return feste

    def teilfluss(self, bloecke: list, breite: float, pfad: tuple) -> tuple[float, list[Platz]]:
        """Blöcke in einer festen Breite setzen (Zelle, Rahmen): → (Höhe, Plätze relativ zur oberen linken Ecke). Die Absätze werden mit ihren Sätzen vermerkt, ihre Rechtecke setzt der Aufrufer."""
        fl = _Fluss(self.engine, self.dok)
        fl.spalten, fl.hoehe, fl.rand_links, fl.rand_oben = [(0.0, breite)], 1e12, 0.0, 0.0
        fl.seite = Seite(-1, self.abschnitt, self.einr)
        fl.abschnitt, fl.einr = self.abschnitt, self.einr
        fl.noten_text = {}
        fl.blocks(bloecke, pfad)
        for k, v in fl.erg.absaetze.items():
            v.zeilen = []                                                   # die Rechtecke der Zeilen setzt der Aufrufer an ihrem Ort auf der Seite
            self.erg.absaetze[k] = v
        for h in fl.erg.hinweise:
            if h not in self.erg.hinweise:
                self.erg.hinweise.append(h)
        return fl.y, fl.seite.plaetze

    def zelle_hoehe(self, c: TableCell, breite: float, pfad: tuple) -> tuple[float, list[Platz]]:
        return self.teilfluss(c.content, breite, pfad)

    def auf_seite_setzen(self, plaetze: list[Platz], dx: float, dy: float) -> None:
        """Plätze aus einem Teilfluss an ihren Ort auf der Seite verschieben und eintragen."""
        for p in plaetze:
            if p.art != "zeile":
                continue
            r = Rect(dx + p.rect.x, dy + p.rect.y, p.rect.width, p.rect.height)
            self.seite.plaetze.append(Platz("zeile", r, p.pfad, p.zeile))
            ort = self.erg.absaetze.get(p.pfad)
            if ort is not None:
                ort.zeilen.append((self.seite.index, p.zeile, r))

    def rahmen(self, fr: Frame, pfad: tuple) -> None:
        """Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum. Sonst oder in einer Zelle: Block im Fluss."""
        art = {1: "links", 2: "rechts"}.get(int(E._zahl(fr.properties.get("CssFloat"))))
        if art is None or self.seite is None or self.seite.index < 0:
            self.blocks(fr.content, pfad)
            return
        rand = max(0.0, E._zahl(fr.properties.get("FrameMargin")))
        innen = max(0.0, E._zahl(fr.properties.get("FramePadding"))) + max(0.0, E._zahl(fr.properties.get("FrameBorder")))
        w_fest = fr.properties.get("FrameWidth")
        breite = w_fest.value if getattr(w_fest, "kind", "") == "fixed" else self.breite() / 3
        h, plaetze = self.teilfluss(fr.content, max(10.0, breite), pfad)
        h_fest = fr.properties.get("FrameHeight")
        hoehe = h_fest.value if getattr(h_fest, "kind", "") == "fixed" else h
        links = self.links()
        x = links + rand if art == "links" else links + self.breite() - breite - 2 * innen - rand
        y = self.rand_oben + self.y + rand
        self.auf_seite_setzen(plaetze, x + innen, y + innen)
        self.ausschluesse.append((self.seite.index, self.spalte, Rect(x - rand, y - rand, breite + 2 * innen + 2 * rand, hoehe + 2 * innen + 2 * rand), art))
        self.seite.plaetze.append(Platz("rahmen", Rect(x, y, breite + 2 * innen, hoehe + 2 * innen), pfad))

    def tabelle(self, t: Table, pfad: tuple) -> None:
        gesamt = E.laenge(t.properties.get("TableWidth"), self.breite()) or self.breite()
        abstand = E._zahl(t.properties.get("TableCellPadding"), ZELLEN_ABSTAND)
        zwischen = E._zahl(t.properties.get("TableCellSpacing"), ZELLEN_ZWISCHENRAUM)
        breiten = self.spaltenbreiten(t, gesamt - zwischen * (t.columns + 1))
        x_spalte = [zwischen + sum(breiten[:i]) + zwischen * i for i in range(t.columns)]
        hoehen = [0.0] * t.rows
        zellen, inhalte = [], {}
        for ri, zeile in enumerate(t.table_rows):
            for ci, c in enumerate(zeile.cells):
                b = sum(breiten[c.column:c.column + c.column_span]) + zwischen * (c.column_span - 1) - 2 * abstand
                h, plaetze = self.zelle_hoehe(c, max(1.0, b), pfad + (ri, ci))
                inhalte[id(c)] = plaetze
                zellen.append((c, h + 2 * abstand))
        for c, h in zellen:
            if c.row_span == 1:
                hoehen[c.row] = max(hoehen[c.row], h)
        for c, h in zellen:
            if c.row_span > 1:
                letzte = min(t.rows - 1, c.row + c.row_span - 1)
                fehlt = h - sum(hoehen[c.row:letzte + 1]) - zwischen * (letzte - c.row)
                if fehlt > 0:
                    hoehen[letzte] += fehlt
        y_zeile = [zwischen + sum(hoehen[:i]) + zwischen * i for i in range(t.rows)]
        # Zeilenweise auf die Seite: eine Zeile bleibt ungeteilt; was nicht passt, beginnt in der nächsten Spalte oder Seite
        ri = 0
        while ri < t.rows:
            self.platz_fuer(hoehen[ri] + zwischen)
            y_basis = self.rand_oben + self.y
            zeilen_h = hoehen[ri] + zwischen
            for c, h in zellen:
                if c.row == ri:
                    zb = sum(breiten[c.column:c.column + c.column_span]) + zwischen * (c.column_span - 1)
                    zh = sum(hoehen[c.row:c.row + c.row_span]) + zwischen * (c.row_span - 1)
                    zr = Rect(self.links() + x_spalte[c.column], y_basis + zwischen, zb, zh)
                    self.seite.plaetze.append(Platz("zelle", zr, pfad + (c.row, c.column), daten=(c.properties, t.properties)))
                    self.auf_seite_setzen(inhalte[id(c)], zr.x + abstand, zr.y + abstand)
            self.y += zeilen_h
            self.leer = False
            ri += 1
        self.unten = 0.0


def _noten_platzieren(self) -> None:
    """Die Fußnoten unten auf jede Seite mit Marken setzen (Rechtecke in Seitenkoordinaten)."""
    for index, eintraege in self.noten.items():
        seite = self.erg.seiten[index]
        unten = self.rand_oben + self.hoehe
        y = unten - self.noten_hoehe(eintraege) + NOTEN_TRENNER
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
    f.noten_platzieren()
    return f.erg
