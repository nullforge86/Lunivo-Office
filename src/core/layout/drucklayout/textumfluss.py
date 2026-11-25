"""Rahmen im Fluss und Flächen, um die der Text läuft (schwebende Objekte). Ohne Qt. Teil des Flusses in ``seitenlayout.py``."""
from __future__ import annotations

from core.dokument.dokument import Rahmen
from core.geometrie import Rect
from core.layout.drucklayout import formatwerte as F
from core.layout.drucklayout.ergebnis import Platz
from core.layout.drucklayout.geometrie import MIN_SPALTENBREITE


class TextUmfluss:
    """Rahmen im Fluss und Flächen, um die der Text läuft (schwebende Objekte)."""

    def ausschluss_fuer(self):
        """Funktion (y, h) → (Einengung links, Einengung rechts, Unterkante): wie weit Flächen den Text ab dem jetzigen Stand einengen."""
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
                if art == "voll":
                    links = max(links, breite)
                elif art == "links":
                    links = max(links, r.right - links_x)
                else:
                    rechts = max(rechts, links_x + breite - r.x)
                unter = max(unter or 0.0, r.bottom - oben - y0)
            return links, rechts, unter
        return ausschluss

    def rahmen(self, fr: Rahmen) -> None:
        """Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum.
        Sonst: Block in der Spalte mit Rand, Abstand und Füllung; ein Rahmen ohne all das (oder höher als die Spalte) fließt wie sein Inhalt."""
        eig = fr.format
        art = {1: "links", 2: "rechts"}.get(int(F._zahl(eig.get("umfluss"))))
        rand = max(0.0, F._zahl(eig.get("rand")))
        innen = max(0.0, F._zahl(eig.get("polster"))) + max(0.0, F._zahl(eig.get("rahmen_breite")))
        fest = self.masz(eig.get("breite"), eig.get("breite_art"), self.breite())
        h_fest = self.masz(eig.get("hoehe"), eig.get("hoehe_art"), 0.0)
        im_fluss = self.seite is not None and self.seite.index >= 0
        if art is None or not im_fluss:
            schlicht = rand == 0 and innen == 0 and fest is None and F.farbwert(eig.get("hintergrund")) is None
            if schlicht:
                self.blocks(fr.bloecke)
                return
            breite = max(MIN_SPALTENBREITE, (min(fest, self.breite() - 2 * rand) if fest is not None else self.breite() - 2 * rand) - 2 * innen)
            h, plaetze = self.teilfluss(fr.bloecke, breite)
            hoehe = max(h, h_fest) if h_fest is not None else h
            aussen_h = hoehe + 2 * innen
            if im_fluss and aussen_h + 2 * rand > self.frei():             # höher als die Spalte: der Inhalt fließt über die Seiten
                self.blocks(fr.bloecke)
                return
            self.abstand_vor(rand)
            self.platz_fuer(aussen_h + rand)
            x, y = self.links() + rand, self.rand_oben + self.y
            self.seite.plaetze.append(Platz("rahmen", Rect(x, y, breite + 2 * innen, aussen_h), fr.id, daten=eig))
            self.auf_seite_setzen(plaetze, x + innen, y + innen)
            self.y += aussen_h + rand
            self.unten, self.leer = rand, False
            return
        breite = fest if fest is not None else self.breite() / 3
        h, plaetze = self.teilfluss(fr.bloecke, max(MIN_SPALTENBREITE, breite))
        hoehe = h_fest if h_fest is not None else h
        x = self.links() + rand if art == "links" else self.links() + self.breite() - breite - 2 * innen - rand
        y = self.rand_oben + self.y + rand
        self.seite.plaetze.append(Platz("rahmen", Rect(x, y, breite + 2 * innen, hoehe + 2 * innen), fr.id, daten=eig))
        self.auf_seite_setzen(plaetze, x + innen, y + innen)
        zone = Rect(x - rand, y - rand, breite + 2 * innen + 2 * rand, hoehe + 2 * innen + 2 * rand)
        self.ausschluesse.append((self.seite.index, self.spalte, zone, art))
