"""Eine Linie als Wert: Farbe, Stärke, Art und (für Absatzrahmen) die Seiten, auf denen sie steht.

Gespeichert wird sie als Text ``farbe|pt|art`` und, wenn nicht alle vier Seiten gemeint sind, ``|seiten`` dahinter —
``t`` oben, ``b`` unten, ``l`` links, ``r`` rechts, ``h`` die Linie zwischen zwei Absätzen. Ohne vierten Teil gelten alle vier
Seiten, so bleiben ältere Dateien gültig.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from lunivo_writer.core.rendering.linien import STILE as KERN_STILE, zeichne_linie, zeichne_rahmen
from lunivo_writer.kern.farben import Farbe
LINIENBREITEN = (0.25, 0.5, 0.75, 1.0, 1.5, 2.25, 3.0, 4.5, 6.0)                       # pt
ALLE_SEITEN = "tblr"


_STRICH = {None: Qt.SolidLine, "dot": Qt.DotLine, "dash": Qt.DashLine, "dashdot": Qt.DashDotLine, "dashdotdot": Qt.DashDotDotLine}


def _bauen() -> dict:
    """Die Linienarten der Auswahl „Formatvorlage“: Schlüssel → (Name, Strichart, DOCX-Wert, Bahnen, wellig). Die Tabelle steht Qt-frei in ``core/rendering/linien.py``;
    hier wird nur die Strichart zu Qt-Werten."""
    return {k: (n, s if isinstance(s, tuple) else _STRICH[s], d, bahnen, wellig) for k, (n, s, d, bahnen, wellig) in KERN_STILE.items()}


STILE = _bauen()
# Die Strichlinien für Formen und Bilder (Auswahl „Strichart“): Schlüssel und Name — die einzige Liste dafür, Menü und Seitenleiste lesen sie hier
OBJEKT_STRICHE = (("einfach", "Durchgezogen"), ("gepunktet", "Gepunktet"), ("fein_gestrichelt", "Fein gestrichelt"), ("gestrichelt", "Gestrichelt"),
                  ("strichpunkt", "Strich-Punkt"), ("strichpunktpunkt", "Strich-Punkt-Punkt"))
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
    seiten: str = ALLE_SEITEN
    abstand: str = ""                    # Abstand zum Text in pt: "oben,unten,links,rechts" (leer = Vorgabe), nur beim Absatzrahmen

    def text(self) -> str:
        basis = f"{self.farbe}|{self.breite_pt:g}|{self.art}"
        if self.abstand:
            return f"{basis}|{self.seiten}|{self.abstand}"
        return basis if self.seiten == ALLE_SEITEN else f"{basis}|{self.seiten}"

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
                       t[3] if len(t) > 3 else ALLE_SEITEN, t[4] if len(t) > 4 else "")
        except ValueError:
            return None

    def mit_seiten(self, seiten: str) -> "Linie":
        return Linie(self.farbe, self.breite_pt, self.art, "".join(s for s in "tblrh" if s in seiten), self.abstand)

    def stift(self, massstab: float = 1.0) -> QPen:
        """QPen der Linie (bei Mehrfachlinien die Gesamtbreite); ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom)."""
        p = QPen(QColor(self.farbe), max(0.6, self.breite_pt * massstab))
        p.setStyle(LINIENARTEN.get(self.art, LINIENARTEN["einfach"])[1] if not isinstance(STILE.get(self.art, STILE["einfach"])[1], tuple) else Qt.SolidLine)
        return p

    def _bahn_stift(self, w: float, dicke: float, strich) -> QPen:
        p = QPen(QColor(self.farbe), max(0.6, w * dicke))
        if isinstance(strich, tuple):
            p.setDashPattern(list(strich))
        else:
            p.setStyle(strich)
        p.setCapStyle(Qt.FlatCap)
        return p

    def zeichne(self, p: QPainter, x1: float, y1: float, x2: float, y2: float, massstab: float = 1.0) -> None:
        """Eine einzelne Linie in ihrer Art: einfach, gestrichelt, mehrfach (Bahnen nebeneinander) oder wellig (gezeichnet über ``core/rendering/linien.py``)."""
        from lunivo_writer.adapter.qt.rendering import QtRenderBackend
        zeichne_linie(QtRenderBackend(p), self.farbe, self.breite_pt, self.art, x1, y1, x2, y2, massstab)

    def rahmen_zeichnen(self, p: QPainter, r: QRectF, massstab: float = 1.0, innen_y=()) -> None:
        """Zeichnet die gemeinten Seiten eines Rechtecks in der Linienart. ``innen_y``: Höhen der Linien zwischen Absätzen (nur wenn ``h`` gesetzt ist)."""
        from lunivo_writer.adapter.qt.rendering import QtRenderBackend
        from lunivo_writer.core.geometry import Rect
        zeichne_rahmen(QtRenderBackend(p), self.farbe, self.breite_pt, self.art, self.seiten, Rect(r.x(), r.y(), r.width(), r.height()), massstab, innen_y)
