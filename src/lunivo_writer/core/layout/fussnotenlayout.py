"""Fußnoten am Seitenende und Endnoten am Dokumentende. Ohne Qt. Teil des Flusses in ``seitenlayout.py``."""
from __future__ import annotations

from lunivo_writer.core.dokument.listen import nummer_text
from lunivo_writer.core.geometrie import Rect, mm_to_px
from lunivo_writer.core.textsatz.engine import FontSpec
from lunivo_writer.core.textsatz.paragraph import Absatzsatz, absatz_setzen
from lunivo_writer.core.layout import formatwerte as F
from .ergebnis import Platz, Seite
from .geometrie import NOTEN_ABSTAND, NOTEN_TRENNER, NOTEN_SCHRIFT, NOTEN_SEITENANTEIL, NOTEN_LINIE_ANTEIL


class FussnotenLayout:
    """Fußnoten am Seitenende und Endnoten am Dokumentende."""

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
        g = F.schrift(dict(self.dok.standardformat))
        klein = FontSpec(g.family, max(6.0, g.size_pt * NOTEN_SCHRIFT), g.weight, g.italic)
        return absatz_setzen(self.engine, [(f"{marke}  {text}", klein)], breite)

    def endnoten_setzen(self) -> None:
        """Die Endnoten am Ende des Dokuments: Trennstrich, dann jede Note mit kleiner römischer Nummer in der Reihenfolge ihrer Marken."""
        texte = {n.id: n.text for n in self.dok.noten.get("e", {}).values()}
        ids = [nid for nid in dict.fromkeys(self.endnoten) if nid in texte]
        if not ids or self.seite is None:
            return
        erste = self.noten_satz(nummer_text("roem_klein", 1), texte[ids[0]], self.breite())
        self.abstand_vor(NOTEN_TRENNER)
        self.platz_fuer(erste.zeilen[0].hoehe)
        self.seite.plaetze.append(Platz("notenlinie", Rect(self.links(), self.rand_oben + self.y - NOTEN_TRENNER / 2, self.breite() * NOTEN_LINIE_ANTEIL, 0.0)))
        for n, nid in enumerate(ids, 1):
            satz = self.noten_satz(nummer_text("roem_klein", n), texte[nid], self.breite())
            for i, z in enumerate(satz.zeilen):
                self.platz_fuer(z.hoehe)
                self.seite.plaetze.append(Platz("endnote", Rect(self.links(), self.rand_oben + self.y, self.breite(), z.hoehe), nid, i, daten=satz))
                self.y += z.hoehe
                self.leer = False
            self.y += NOTEN_ABSTAND

    def noten_platzieren(self) -> None:
        """Die Fußnoten unten auf jede Seite mit Marken setzen (Rechtecke in Seitenkoordinaten)."""
        for index, eintraege in self.noten.items():
            seite = self.erg.seiten[index]
            p = seite.einrichtung
            links, oben = mm_to_px(p.margin_left_mm), mm_to_px(p.margin_top_mm)
            unten = oben + p.content_height_px
            breite = p.content_width_px
            y = unten - self.noten_hoehe_seite(eintraege, breite, p.content_height_px) + NOTEN_TRENNER
            seite.plaetze.append(Platz("notenlinie", Rect(links, y - NOTEN_TRENNER / 2, breite * NOTEN_LINIE_ANTEIL, 0.0)))
            for nr, nid in eintraege:
                satz = self.noten_satz(str(nr), self.noten_text.get(nid, ""), breite)
                seite.plaetze.append(Platz("fussnote", Rect(links, y, breite, satz.hoehe), nid, 0, daten=satz))
                y += satz.hoehe + NOTEN_ABSTAND

    def noten_hoehe_seite(self, eintraege: list, breite: float, hoehe: float) -> float:
        gesamt = NOTEN_TRENNER + sum(self.noten_satz(str(nr), self.noten_text.get(nid, ""), breite).hoehe + NOTEN_ABSTAND for nr, nid in eintraege)
        return min(gesamt, hoehe * NOTEN_SEITENANTEIL)
