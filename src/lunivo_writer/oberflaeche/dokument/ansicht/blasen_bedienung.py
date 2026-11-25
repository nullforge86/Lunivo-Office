"""Sprechblasen im Seitenrand (Kommentare, verfolgte Änderungen) auf der Zeichenfläche: Lage, Zeichnen und Bedienung.

Die Mischklasse ``BlasenBedienung`` gehört zur Zeichenfläche (``dokument_ansicht.py``). Die Blasen stehen rechts oder links neben jedem Blatt auf einem eigenen
Streifen, so nah wie möglich an der Stelle, auf die sie sich beziehen; Klick wählt die Textstelle, das Zeichen „☰“ öffnet das Menü des Kommentars,
Doppelklick bearbeitet ihn. Die Einstellungen kommen aus ``editor/objekte/sprechblasen.py`` (``konfig_lesen``)."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt

from lunivo_writer.core.bearbeitung.suche import offset_zu_position
from lunivo_writer.core.geometrie import mm_to_px
from lunivo_writer.core.layout import schreibmarke as SM
from lunivo_writer.editor.objekte.formen import sprechblasen as SB


class BlasenBedienung:
    def _blasen_init(self) -> None:
        self.blasen_konfig: dict | None = None        # ``sprechblasen.konfig_lesen``; ``None``: keine Blasen
        self.blasen_schrift = "mittel"
        self.blasen_hook = None                       # Rückruf(Art, Kommentar-Id, globale Stelle): ``menue`` oder ``bearbeiten``
        self._blasen_treffer: list = []

    def blasen_breite(self) -> float:
        return mm_to_px(SB.breite_mm(self.blasen_konfig)) if self.blasen_konfig else 0.0

    def blasen_aktiv(self) -> bool:
        return bool(self.blasen_konfig) and SB.aktiv(self.blasen_konfig)

    def _blasen_schrift(self):
        return SB.blasen_schrift(max(7, int(SB.blasen_px(self.blasen_schrift) * self.zoom)))

    def blasen_layout(self) -> list:
        """[(Blase, Rechteck in der Ansicht, y der Textstelle, x des Textendes)] aller Blasen, je Blatt gestapelt. ``y`` ist die Mitte der Zeile, ``x`` das Ende der
        kommentierten Stelle: dort beginnt die Linie zur Blase, so ist der Bezug zum Text sichtbar."""
        if not self.blasen_aktiv():
            return []
        erg = self.ergebnis()
        d = self.sitzung.dokument
        rechts = self.blasen_konfig.get("rand", "Rechts") == "Rechts"
        breite = self.blasen_breite() * self.zoom
        luecke = mm_to_px(SB.LUECKE_MM) * self.zoom
        font = self._blasen_schrift()
        je_seite: dict[int, list] = {}
        for bl in SB.sammeln_modell(self.sitzung, self.blasen_konfig["verwenden"]):
            pos = offset_zu_position(d, bl.von)
            stelle = erg.cursor(pos.absatz_id, pos.versatz)
            if stelle is None:
                continue
            seite, p = stelle
            ende = SM.cursor_rechteck(erg, offset_zu_position(d, bl.bis))
            if ende is not None and ende[0] == seite:                                  # Ende der Stelle auf demselben Blatt: Linie beginnt dort (bei Blasen links am Anfang), sonst am Anfang
                x_text, y_mitte = (ende[1].x + ende[1].width if rechts else p.x), ende[1].y + ende[1].height / 2
            else:
                x_text, y_mitte = p.x, p.y
            blatt = self.blatt(seite)
            je_seite.setdefault(seite, []).append((bl, blatt.top() + p.y * self.zoom, blatt.left() + x_text * self.zoom, blatt.top() + y_mitte * self.zoom))
        aus = []
        for seite, liste in je_seite.items():
            blatt = self.blatt(seite)
            hoehen = [SB.messen(bl, breite, font) for bl, _y, _x, _m in liste]
            ys = SB.stapeln([y for _b, y, _x, _m in liste], hoehen, blatt.bottom())
            x = blatt.right() + luecke if rechts else blatt.left() - luecke - breite
            for (bl, _ytop, xtext, ymitte), y, h in zip(liste, ys, hoehen):
                aus.append((bl, QRectF(x, y, breite, h), ymitte, xtext))
        return aus

    def blasen_zeichnen(self, p) -> None:
        self._blasen_treffer = []
        rechts = bool(self.blasen_konfig) and self.blasen_konfig.get("rand", "Rechts") == "Rechts"
        font = self._blasen_schrift()
        for bl, r, y_text, x_text in self.blasen_layout():
            if self.blasen_konfig.get("linien", True):
                SB.verbindung(p, bl, x_text, y_text, r, rechts)                        # vom Ende der kommentierten Stelle quer über den Rand zur Blase
            SB.zeichnen(p, bl, r, font)
            self._blasen_treffer.append((r, bl))

    def _blatt_kante(self, r: QRectF, rechts: bool) -> float:
        return r.left() - mm_to_px(SB.LUECKE_MM) * self.zoom if rechts else r.right() + mm_to_px(SB.LUECKE_MM) * self.zoom

    def blase_bei(self, pos):
        for r, bl in self._blasen_treffer:
            if r.contains(pos):
                return r, bl
        return None

    def blasen_maus_druecken(self, ev) -> bool:
        treffer = self.blase_bei(ev.position())
        if treffer is None:
            return False
        r, bl = treffer
        if bl.kid is not None and SB.menue_rect(r).contains(ev.position()) and self.blasen_hook is not None:
            self.blasen_hook("menue", bl.kid, ev.globalPosition().toPoint())
        else:
            v, b = offset_zu_position(self.sitzung.dokument, bl.von), offset_zu_position(self.sitzung.dokument, bl.bis)
            self.sitzung.setze_auswahl(v, b)
            self.nach_bewegung()
        return True

    def blasen_doppelklick(self, ev) -> bool:
        treffer = self.blase_bei(ev.position())
        if treffer is None or treffer[1].kid is None or self.blasen_hook is None:
            return False
        self.blasen_hook("bearbeiten", treffer[1].kid, ev.globalPosition().toPoint())
        return True
