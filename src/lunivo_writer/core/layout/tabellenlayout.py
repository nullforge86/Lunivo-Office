"""Tabellen im Fluss: Spaltenbreiten, verbundene Zellen, wiederholte Kopfzeilen, Teilung hoher Zeilen. Ohne Qt. Teil des Flusses in ``seitenlayout.py``."""
from __future__ import annotations

from lunivo_writer.core.document.dokument import Tabelle
from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.layout import formatwerte as F
from .ergebnis import Platz, Seite
from .geometrie import ZELLEN_POLSTER, ZELLEN_ZWISCHENRAUM, MIN_TEILHOEHE, MIN_TABELLENBREITE, MIN_SPALTENBREITE, _Z


class TabellenLayout:
    """Tabellen im Fluss: Spaltenbreiten, verbundene Zellen, wiederholte Kopfzeilen, Teilung hoher Zeilen."""

    @staticmethod
    def masz(wert, art, gesamt: float):
        """Eine Maßangabe (Bildpunkte, Art fest/prozent/auto) in Bildpunkten; ``None`` bei automatischer Größe."""
        if not isinstance(wert, (int, float)) or isinstance(wert, bool) or wert <= 0 or art == "auto":
            return None
        return gesamt * wert / 100.0 if art == "prozent" else float(wert)

    @staticmethod
    def spaltenbreiten(t: Tabelle, breite_tab: float, luecke: float) -> list:
        """Spaltenbreiten aus den Vorgaben (größer 0 = fest, 0 = frei): freie Spalten teilen sich den Rest; passt die Summe nicht, wird auf die
        Tabellenbreite gebracht."""
        n = t.spalten
        vorgaben = list(t.spaltenbreiten)[:n] + [0.0] * max(0, n - len(t.spaltenbreiten))
        innen = max(MIN_SPALTENBREITE, breite_tab - luecke * (n + 1))
        b, frei = [0.0] * n, []
        for i, v in enumerate(vorgaben):
            if v > 0:
                b[i] = v
            else:
                frei.append(i)
        rest = innen - sum(b)
        for i in frei:
            b[i] = max(MIN_SPALTENBREITE, rest / len(frei)) if rest > 0 else MIN_SPALTENBREITE
        summe = sum(b)
        if summe > 0 and abs(summe - innen) > 0.5 and (summe > innen or not frei):
            b = [w * innen / summe for w in b]
        return b

    def tabelle(self, t: Tabelle) -> None:
        """Eine Tabelle setzen: Spaltenbreiten aus den Vorgaben, Zeilenhöhen aus dem Inhalt (und der Mindesthöhe), Zeilen untereinander. Passt eine
        Zeile nicht mehr, beginnt sie in der nächsten Spalte oder Seite; dort stehen die Kopfzeilen noch einmal. Eine Zeile, die höher ist als eine
        ganze Seite, wird zwischen ihren Textzeilen geteilt."""
        if not t.spalten or not t.zeilen:
            return
        eig = t.format
        luecke = max(0.0, F._zahl(eig.get("zellabstand"), ZELLEN_ZWISCHENRAUM))
        polster = max(0.0, F._zahl(eig.get("zellpolster"), ZELLEN_POLSTER))
        rand = max(0.0, F._zahl(eig.get("rahmen_breite")))
        einzug = max(0.0, F._zahl(eig.get("einzug_links")))
        verfuegbar = max(MIN_TABELLENBREITE, self.breite() - einzug)
        fest = self.masz(eig.get("breite"), eig.get("breite_art"), verfuegbar)
        breite_tab = min(verfuegbar, max(MIN_TABELLENBREITE, fest)) if fest is not None else verfuegbar
        breiten = self.spaltenbreiten(t, breite_tab, luecke)
        xs = [luecke]
        for b in breiten[:-1]:
            xs.append(xs[-1] + b + luecke)
        frei_b = max(0.0, verfuegbar - breite_tab)
        ausr = eig.get("ausrichtung", "links")
        dx_tab = einzug + (frei_b / 2 if ausr == "mitte" else frei_b if ausr == "rechts" else 0.0)

        zellen = [_Z(z, s, c) for z, zeile in enumerate(t.zellen) for s, c in enumerate(zeile) if c.verdeckt_von is None]

        def breite_von(c: _Z) -> float:
            return sum(breiten[c.s:c.s + c.zelle.spaltenspanne]) + luecke * (c.zelle.spaltenspanne - 1)

        def innen(c: _Z) -> tuple:
            def pad(name: str) -> float:
                v = c.zelle.format.get(f"polster_{name}")
                return max(0.0, F._zahl(v)) if v is not None else polster
            return pad("links"), pad("oben"), pad("rechts"), pad("unten")

        def zelle_platz(c: _Z, seite: Seite, links: float, y: float, h: float, kopie: bool = False) -> Rect:
            zr = Rect(links + dx_tab + xs[c.s], y, breite_von(c), h)
            seite.plaetze.append(Platz("zelle", zr, t.id, c.z, c.s, (c.zelle.format, eig), kopie))
            return zr

        inhalt: dict = {}
        hoehen = [0.0] * t.zeilen
        for c in zellen:
            l, o, r, u = innen(c)
            inhalt[(c.z, c.s)] = self.teilfluss(c.zelle.bloecke, max(MIN_SPALTENBREITE, breite_von(c) - l - r - rand))
            if c.zelle.zeilenspanne == 1:
                mindest = F._zahl(t.zeilenhoehen[c.z]) if c.z < len(t.zeilenhoehen) else 0.0
                hoehen[c.z] = max(hoehen[c.z], inhalt[(c.z, c.s)][0] + o + u + rand, mindest)
        for z in range(t.zeilen):                                           # Zeilen ohne Einzelzelle behalten ihre Mindesthöhe
            if z < len(t.zeilenhoehen):
                hoehen[z] = max(hoehen[z], F._zahl(t.zeilenhoehen[z]))
        ueberspannt: set = set()
        for c in zellen:
            if c.zelle.zeilenspanne > 1:
                _l, o, _r, u = innen(c)
                letzte = min(t.zeilen - 1, c.z + c.zelle.zeilenspanne - 1)
                ueberspannt.update(range(c.z, letzte + 1))
                fehlt = inhalt[(c.z, c.s)][0] + o + u + rand - sum(hoehen[c.z:letzte + 1]) - luecke * (letzte - c.z)
                if fehlt > 0:                                               # fehlende Höhe geht an die letzte Zeile der Zelle
                    hoehen[letzte] += fehlt
        im_fluss = self.seite.index >= 0
        kopf_n = min(max(0, int(F._zahl(eig.get("kopfzeilen")))), t.zeilen - 1) if im_fluss else 0
        self.abstand_vor(luecke + rand)
        orte: list = [None] * t.zeilen                                      # je Zeile (Seite, linker Rand der Spalte, y auf der Seite)
        kopien: list = []                                                   # je Seitenwechsel die Orte der wiederholten Kopfzeilen
        geteilt: set = set()
        for r in range(t.zeilen):
            h = hoehen[r]
            passt_nicht = self.y + h + luecke > self.frei() + 0.01
            if im_fluss and passt_nicht and h + luecke > self.frei() and r not in ueberspannt:
                self.zeile_teilen([c for c in zellen if c.z == r], inhalt, innen, zelle_platz, rand, luecke)
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
            if c.z in geteilt:
                continue
            seite, links, y0 = orte[c.z]
            bis = min(t.zeilen - 1, c.z + c.zelle.zeilenspanne - 1)
            h = hoehen[c.z]
            if bis > c.z and orte[bis] is not None and orte[bis][0] is seite and orte[bis][2] > y0:
                h = orte[bis][2] + hoehen[bis] - y0
            l, o, _r, u = innen(c)
            zr = zelle_platz(c, seite, links, y0, h)
            h_inhalt, plaetze = inhalt[(c.z, c.s)]
            frei_h = max(0.0, h - o - u - rand - h_inhalt)
            senkrecht = c.zelle.format.get("vertikal", "oben")
            versatz = frei_h / 2 if senkrecht == "mitte" else frei_h if senkrecht == "unten" else 0.0
            self.auf_seite_setzen(plaetze, zr.x + rand / 2 + l, zr.y + rand / 2 + o + versatz, seite)
        for neu in kopien:
            for c in zellen:
                if c.z < kopf_n and c.zelle.zeilenspanne == 1:
                    seite, links, y = neu[c.z]
                    l, o, _r, _u = innen(c)
                    zr = zelle_platz(c, seite, links, y, hoehen[c.z], kopie=True)
                    self.auf_seite_setzen(inhalt[(c.z, c.s)][1], zr.x + rand / 2 + l, zr.y + rand / 2 + o, seite, kopie=True)
        self.unten = rand
        self.y += self.unten

    def zeile_teilen(self, zellen: list, inhalt: dict, innen, zelle_platz, rand: float, luecke: float) -> None:
        """Eine Tabellenzeile, die höher ist als eine ganze Seite, über mehrere Seiten setzen: je Seite so viele Zeilen jeder Zelle, wie passen."""
        schluessel = lambda c: (c.z, c.s)
        rest = {schluessel(c): list(inhalt[schluessel(c)][1]) for c in zellen}
        ab = {schluessel(c): 0.0 for c in zellen}                           # bis zu dieser Höhe ist der Inhalt der Zelle gesetzt
        while True:
            raum = self.frei() - self.y - luecke
            if raum < MIN_TEILHOEHE and not self.leer:
                self.weiter()
                continue
            teile, teil_h, fertig = [], 0.0, True
            for c in zellen:
                k = schluessel(c)
                _l, o, _r, u = innen(c)
                liste = rest[k]
                grenze = ab[k] + raum - o - u - rand
                n = 0
                while n < len(liste) and liste[n].rect.bottom <= grenze + 0.01:
                    n += 1
                if n == 0 and liste and self.leer:                          # passt auf keine Seite: das erste Stück steht trotzdem hier
                    n = 1
                    while n < len(liste) and liste[n].rect.bottom <= liste[0].rect.bottom + 0.01:
                        n += 1
                nimm, rest[k] = liste[:n], liste[n:]
                unten = max((p.rect.bottom for p in nimm), default=ab[k])
                teile.append((c, nimm, ab[k]))
                teil_h = max(teil_h, unten - ab[k] + o + u + rand)
                if rest[k]:
                    fertig = False
                    ab[k] = min(p.rect.y for p in rest[k])
            if not fertig and not self.leer and not any(nimm for _c, nimm, _a in teile):
                for c, _nimm, a in teile:
                    ab[schluessel(c)] = a
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
