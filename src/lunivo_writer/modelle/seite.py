"""Seiteneinrichtung: Papier, Ränder, Ausrichtung, Kopf- und Fußzeile.

Alle Maße in Millimetern. Umrechnung in Bildpunkte (96 dpi) nur hier.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from lunivo_writer.core.geometry.units import PX_PER_MM, mm_to_px, px_to_mm, umbruchraster
from lunivo_writer.kern.farben import Farbe

PAPER_MM = {
    "A4": (210.0, 297.0),
    "A5": (148.0, 210.0),
    "A3": (297.0, 420.0),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
}


@dataclass
class HeaderFooter:
    """Text mit Platzhalter {PAGE} und {PAGES}. Ausrichtung: left|center|right, dazu aussen|innen (ungerade Seiten rechts bzw. links,
    gerade Seiten umgekehrt — wie bei gebundenen Büchern)."""
    text: str = ""
    align: str = "center"
    fmt: dict = field(default_factory=dict)      # Zeichenformat der ganzen Zeile: family, size_pt, bold, italic, underline, color
    runs: list = field(default_factory=list)     # [{"text", "fmt"}]: Textstücke mit eigenem Format (aus DOCX); gelten nur, wenn sie den Text ergeben

    def kopie(self, text: str | None = None, align: str | None = None) -> "HeaderFooter":
        return HeaderFooter(self.text if text is None else text, self.align if align is None else align, dict(self.fmt),
                            [dict(r) for r in self.runs])

    def laeufe(self) -> list:
        """(Text, Zeichenformat)-Stücke in Reihenfolge. Ohne gültige eigene Läufe gilt ein Stück: der ganze Text mit ``fmt``."""
        if self.runs and "".join(r.get("text", "") for r in self.runs) == self.text:
            return [(r.get("text", ""), r.get("fmt") or self.fmt) for r in self.runs]
        return [(self.text, self.fmt)]

    def is_empty(self) -> bool:
        return not self.text.strip()


@dataclass
class PageSettings:
    width_mm: float = 210.0
    height_mm: float = 297.0
    margin_top_mm: float = 25.0
    margin_bottom_mm: float = 25.0
    margin_left_mm: float = 32.0
    margin_right_mm: float = 32.0
    header: HeaderFooter = field(default_factory=HeaderFooter)
    footer: HeaderFooter = field(default_factory=HeaderFooter)
    color: str = ""                      # Seitenfarbe als „#rrggbb“; leer = keine
    border: dict | None = None           # {"farbe": Farbe.SCHWARZ, "breite_pt": 1.0, "art": Linienart (editor/objekte/linie.py), "abstand_mm": 8.0, "seiten": "tblr"}
    watermark: dict | None = None        # {"text": …, "farbe": "#c0c0c0", "winkel": -45, "groesse_pt": 80}
    zeilennummern: bool = False
    zeilennummern_neu: str = ""          # "" fortlaufend, "seite" auf jeder Seite neu (siehe editor/seite/zeilennummern.py)
    diff_first: bool = False                 # „Erste Seite anders“
    first_header: HeaderFooter = field(default_factory=HeaderFooter)
    first_footer: HeaderFooter = field(default_factory=HeaderFooter)
    diff_even: bool = False                  # „Gerade und ungerade Seiten sind unterschiedlich“: gerade Seiten haben eine eigene Kopf-/Fußzeile
    even_header: HeaderFooter = field(default_factory=HeaderFooter)
    even_footer: HeaderFooter = field(default_factory=HeaderFooter)
    spalten: int = 1                         # Textspalten (Seitenansicht, Druck, PDF; die Bearbeitungsansicht bleibt einspaltig)
    spalten_abstand_mm: float = 10.0
    spalten_linie: bool = False              # Trennlinie zwischen den Spalten
    spalten_raster_mm: list | None = None    # ungleich breite Spalten (DOCX w:cols mit w:col): je Spalte [Breite, Abstand danach] in mm; None = gleich breit
    silbentrennung: bool = False             # automatische Silbentrennung (Seitenansicht, Druck, PDF; DOCX: autoHyphenation)
    silben_sprache: str = "de_DE"
    kopf_verknuepft: bool = False            # Abschnitt ab dem zweiten: Kopfzeile wie im vorigen Abschnitt
    bilder: list = field(default_factory=list)   # frei positionierte Bilder in Kopf-/Fußzeilen (siehe editor/objekte/freie_bilder.py)
    kopf_abstand_mm: float = 12.7            # Abstand der Kopfzeile vom oberen Blattrand (DOCX w:header)
    fuss_abstand_mm: float = 12.7            # Abstand der Fußzeile vom unteren Blattrand (DOCX w:footer)
    fuss_verknuepft: bool = False
    # Seitenzahl (Einfügen ▸ Seitenzahl ▸ Seitenzahl einfügen …; DOCX w:pgNumType)
    seiten_format: str = "dezimal"           # Zahlenart von {PAGE}: dezimal, klein, gross, roem_klein, roem_gross (mehrstufig.nummer_text)
    seiten_start: int = 0                    # 0 = fortsetzen vom vorherigen Abschnitt, sonst „Beginnen mit“
    kapitel_ebene: int = 0                   # Kapitelnummer voranstellen: Nummer der letzten Überschrift dieser Ebene (0 = nein)
    kapitel_trenner: str = "-"

    @property
    def landscape(self) -> bool:
        return self.width_mm > self.height_mm

    def set_orientation(self, landscape: bool) -> None:
        if landscape != self.landscape:
            self.width_mm, self.height_mm = self.height_mm, self.width_mm

    def set_paper(self, name: str) -> None:
        w, h = PAPER_MM[name]
        if self.landscape:
            w, h = h, w
        self.width_mm, self.height_mm = w, h

    def paper_name(self) -> str:
        a, b = sorted((self.width_mm, self.height_mm))
        for name, (w, h) in PAPER_MM.items():
            if abs(a - w) < 1.0 and abs(b - h) < 1.0:
                return name
        return "Benutzerdefiniert"

    @property
    def content_width_px(self) -> float:
        return mm_to_px(self.width_mm - self.margin_left_mm - self.margin_right_mm)

    @property
    def content_height_px(self) -> float:
        """Höhe der Textfläche einer Seite, im Raster des Seitenumbruchs (``umbruchraster``)."""
        return umbruchraster(mm_to_px(self.height_mm - self.margin_top_mm - self.margin_bottom_mm))

    ZEILE_KOPF_PX = 16.0                       # Höhe einer Zeile in Kopf-/Fußzeile (Schrift 11 pt mit Zeilenabstand)

    def kopf_fuss_art(self, blatt: int, nummer: int) -> str:
        """Welche Kopf-/Fußzeile ein Blatt trägt: "first" (Blatt 1 bei „Erste Seite anders“), "even" (gerade angezeigte Seitenzahl bei
        „Gerade und ungerade Seiten unterschiedlich“) oder "" (die gewöhnliche). ``blatt`` ist 1-basiert, ``nummer`` die angezeigte Seitenzahl."""
        if blatt == 1 and self.diff_first:
            return "first"
        if self.diff_even and nummer % 2 == 0:
            return "even"
        return ""

    def kopf_fuss(self, blatt: int, nummer: int) -> tuple:
        """(Kopfzeile, Fußzeile) für das Blatt, siehe ``kopf_fuss_art``."""
        art = self.kopf_fuss_art(blatt, nummer)
        if art:
            return getattr(self, art + "_header"), getattr(self, art + "_footer")
        return self.header, self.footer

    def erste_seite_versatz_px(self) -> float:
        """Wie weit der Text der ersten Seite nach unten rückt, weil die Kopfzeile länger ist als der obere Rand: Der Text beginnt erst unter der
        Kopfzeile. Gilt für die Kopfzeile der ersten Seite, bei „Erste Seite anders“ für die eigene."""
        hf = self.first_header if self.diff_first else self.header
        ort = "kopf1" if self.diff_first else "kopf"
        oberes_drittel = mm_to_px(self.height_mm) / 3                                           # Kopfzeilenbilder stehen oben; Lagen weiter unten sind fehlerhaft
        bild_unten = max((float(a.get("yv") or 0) + float(a.get("h") or 0) for a in self.bilder
                          if a.get("ort") == ort and a.get("bild") is not None
                          and float(a.get("yv") or 0) + float(a.get("h") or 0) <= oberes_drittel), default=0.0)   # Bilder der Kopfzeile zählen mit
        if hf.is_empty() and not bild_unten:
            return 0.0
        zeile = self.ZEILE_KOPF_PX
        groesse = float((hf.fmt or {}).get("size_pt") or 0)
        if groesse > 0:                                       # Zeilenhöhe der Kopfzeilenschrift: Schriftgröße × 1,22 (wie die Schrift setzt)
            zeile = groesse * 96 / 72 * 1.22
        unten = mm_to_px(self.kopf_abstand_mm) + (len(hf.text.split("\n")) * zeile if not hf.is_empty() else 0.0)
        return max(0.0, max(unten, bild_unten) - mm_to_px(self.margin_top_mm))

    def copy(self) -> "PageSettings":
        import dataclasses
        return dataclasses.replace(
            self, header=self.header.kopie(), footer=self.footer.kopie(),
            border=dict(self.border) if self.border else None, watermark=dict(self.watermark) if self.watermark else None,
            first_header=self.first_header.kopie(),
            first_footer=self.first_footer.kopie(),
            even_header=self.even_header.kopie(),
            even_footer=self.even_footer.kopie(), bilder=list(self.bilder),
            spalten_raster_mm=[list(x) for x in self.spalten_raster_mm] if self.spalten_raster_mm else None)

    def spaltenraster_px(self) -> list[tuple[float, float]]:
        """Das Spaltenraster der Textfläche: [(x, Breite)] je Spalte in Bildpunkten, x vom linken Textrand. Gleich breit oder — mit
        ``spalten_raster_mm`` — wie in der Datei; passt die Liste nicht zur Spaltenzahl oder zur Textbreite, gilt das gleich breite Raster.
        Die einzige Stelle, die das Raster berechnet (Seitenplan, Seitenansicht, Druck)."""
        n = max(1, int(self.spalten))
        raster = self.spalten_raster_mm
        if raster and len(raster) == n and n > 1:
            try:
                breiten = [mm_to_px(float(b[0])) for b in raster]
                luecken = [mm_to_px(float(b[1])) for b in raster[:-1]]
                if min(breiten) > 0 and abs(sum(breiten) + sum(luecken) - self.content_width_px) <= max(2.0, self.content_width_px * 0.02):
                    x, aus = 0.0, []
                    for i, b in enumerate(breiten):
                        aus.append((x, b))
                        x += b + (luecken[i] if i < len(luecken) else 0.0)
                    return aus
            except (TypeError, ValueError, IndexError):
                pass
        b = self.spalten_breite_px
        luecke = mm_to_px(self.spalten_abstand_mm)
        return [(i * (b + luecke), b) for i in range(n)]

    @property
    def spalten_breite_px(self) -> float:
        """Breite einer Textspalte (bei einer Spalte: die ganze Textbreite)."""
        n = max(1, int(self.spalten))
        return (self.content_width_px - mm_to_px(self.spalten_abstand_mm) * (n - 1)) / n
