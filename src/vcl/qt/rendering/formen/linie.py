from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from core.layout.drucklayout.ausgabe.objekte.linien import zeichne_linie, zeichne_rahmen
from writer.anbindung.linien import stile
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import STIFT_LINIE_MIN
from writer.anbindung.linie_daten import alle_seiten


_STRICH = {None: Qt.SolidLine, "dot": Qt.DotLine, "dash": Qt.DashLine, "dashdot": Qt.DashDotLine, "dashdotdot": Qt.DashDotDotLine}


def _bauen() -> dict:
    """Die Linienarten der Auswahl „Formatvorlage“: Schlüssel → (Name, Strichart, DOCX-Wert, Bahnen, wellig). Die Tabelle steht Qt-frei in ``core/rendering/linien.py``;
    hier wird nur die Strichart zu Qt-Werten."""
    return {k: (n, s if isinstance(s, tuple) else _STRICH[s], d, bahnen, wellig) for k, (n, s, d, bahnen, wellig) in stile().items()}


STILE = _bauen()


LINIENARTEN = {k: (v[0], v[1]) for k, v in STILE.items()}                              # Name und Strichart (wie bisher)


_VON_DOCX = {v[2]: k for k, v in STILE.items()}


def docx_wert(art: str) -> str:
    """Wert von ``w:val`` für eine Linienart (unbekannt: einfach)."""
    return STILE.get(art, STILE["einfach"])[2]


def art_aus_docx(wert: str | None) -> str:
    return _VON_DOCX.get(wert or "", "einfach")


@dataclass
class Linie:
    farbe: str = Farbe.SCHWARZ
    breite_pt: float = 1.0
    art: str = "einfach"
    seiten: str = alle_seiten()
    abstand: str = ""                    # Abstand zum Text in pt: "oben,unten,links,rechts" (leer = Vorgabe), nur beim Absatzrahmen

    def text(self) -> str:
        basis = f"{self.farbe}|{self.breite_pt:g}|{self.art}"
        if self.abstand:
            return f"{basis}|{self.seiten}|{self.abstand}"
        return basis if self.seiten == alle_seiten() else f"{basis}|{self.seiten}"

    def polster(self) -> tuple[float, float, float, float] | None:
        """(oben, unten, links, rechts) in pt, wenn ein eigener Abstand gesetzt ist."""
        try:
            o, u, l, r = (float(x) for x in self.abstand.split(","))
            return o, u, l, r
        except ValueError:
            return None

    @classmethod
    def aus_text(cls, text: str | None) -> "Linie | None":
        if not text:
            return None
        t = text.split("|")
        try:
            return cls(t[0] or Farbe.SCHWARZ, float(t[1]) if len(t) > 1 and t[1] else 1.0, t[2] if len(t) > 2 and t[2] else "einfach",
                       t[3] if len(t) > 3 else alle_seiten(), t[4] if len(t) > 4 else "")
        except ValueError:
            return None

    def mit_seiten(self, seiten: str) -> "Linie":
        return Linie(self.farbe, self.breite_pt, self.art, "".join(s for s in "tblrh" if s in seiten), self.abstand)

    def stift(self, massstab: float = 1.0) -> QPen:
        """QPen der Linie (bei Mehrfachlinien die Gesamtbreite); ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom)."""
        p = QPen(QColor(self.farbe), max(STIFT_LINIE_MIN, self.breite_pt * massstab))
        p.setStyle(LINIENARTEN.get(self.art, LINIENARTEN["einfach"])[1] if not isinstance(STILE.get(self.art, STILE["einfach"])[1], tuple) else Qt.SolidLine)
        return p

    def _bahn_stift(self, w: float, dicke: float, strich) -> QPen:
        p = QPen(QColor(self.farbe), max(STIFT_LINIE_MIN, w * dicke))
        if isinstance(strich, tuple):
            p.setDashPattern(list(strich))
        else:
            p.setStyle(strich)
        p.setCapStyle(Qt.FlatCap)
        return p

    def zeichne(self, p: QPainter, x1: float, y1: float, x2: float, y2: float, massstab: float = 1.0) -> None:
        """Eine einzelne Linie in ihrer Art: einfach, gestrichelt, mehrfach (Bahnen nebeneinander) oder wellig (gezeichnet über ``core/rendering/linien.py``)."""
        from vcl.qt.rendering.formen.anzeige import kern_malen
        rand = max(4.0, self.breite_pt * 3)
        kern_malen(p, QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)), lambda z: zeichne_linie(z, self.farbe, self.breite_pt, self.art, x1, y1, x2, y2, massstab), rand=rand)

    def rahmen_zeichnen(self, p: QPainter, r: QRectF, massstab: float = 1.0, innen_y=()) -> None:
        """Zeichnet die gemeinten Seiten eines Rechtecks in der Linienart. ``innen_y``: Höhen der Linien zwischen Absätzen (nur wenn ``h`` gesetzt ist)."""
        from vcl.qt.rendering.formen.anzeige import kern_malen
        from core.geometrie import Rect
        kern_malen(p, r, lambda z: zeichne_rahmen(z, self.farbe, self.breite_pt, self.art, self.seiten, Rect(r.x(), r.y(), r.width(), r.height()), massstab, innen_y), rand=max(4.0, self.breite_pt * 3))
