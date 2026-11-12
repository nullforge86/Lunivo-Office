"""Frei positionierte Bilder im Editor: zeichnen, anklicken, verschieben, in der Größe ändern, löschen (siehe editor/objekte/freie_bilder.py).

Ein Klick auf ein Bild vor dem Text wählt es aus (Strg+Alt+Klick: auch eines hinter dem Text, zum Beispiel das Band im Briefkopf);
Ziehen verschiebt, die Griffe an den Ecken und Kanten ändern die Größe (an den Ecken bleibt das Seitenverhältnis, mit Umschalt frei),
Entf löscht, Esc hebt die Auswahl auf. Bilder in der Kopf-/Fußzeile gehören zum Blatt, Bilder im Text zu einem Absatz.

``FreieBilderMixin`` setzt die Bausteine zusammen (jeder mit einer Aufgabe) und hält Auswahl, Trefferliste und Absatzzugriff:

* ``freie_bilder_geometrie.py``   — Maße, Griffe, Rahmen (rein, ohne Zustand)
* ``freie_bilder_zeichnen.py``    — Darstellung: Bilder, Auswahlrahmen, Griffe, Schaltflächen, Teilrahmen
* ``freie_bilder_interaktion.py`` — Maus und Tastatur: anklicken, ziehen, ablegen, Entf/Esc/Enter
* ``freie_bilder_knoten.py``      — Teile des Diagramms, Knoten des SmartArt, Text im Knoten
* ``freie_bilder_knoepfe.py``     — Schaltflächen neben dem Objekt: Menüs, Popups, Fenster
"""
from __future__ import annotations

import json

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QTextCursor

from lunivo_writer.editor.dokument.zusatz import B_BILDANKER
from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.oberflaeche.dokument.bearbeitung import freie_bilder_geometrie as G
from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_interaktion import FreieBilderInteraktionMixin
from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_knoepfe import FreieBilderKnoepfeMixin
from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_knoten import FreieBilderKnotenMixin
from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_zeichnen import FreieBilderZeichnenMixin


class FreieBilderMixin(FreieBilderZeichnenMixin, FreieBilderInteraktionMixin, FreieBilderKnotenMixin, FreieBilderKnoepfeMixin):
    @property
    def _frei_sel(self):
        return self.__dict__.get("_frei_sel_wert")

    @_frei_sel.setter
    def _frei_sel(self, wert) -> None:
        alt = self.__dict__.get("_frei_sel_wert")
        self.__dict__["_frei_sel_wert"] = wert
        if alt != wert:
            self.__dict__["_frei_zuschnitt"] = False                  # der Zuschneiden-Modus gilt nur für das eben gewählte Bild
            self.__dict__["_fp_key"] = None                           # ebenso das Bearbeiten der Punkte einer Form
        if alt != wert and hasattr(self, "freiAuswahlGeaendert"):
            self.freiAuswahlGeaendert.emit()

    def _frei_init(self) -> None:
        self._frei_treffer: list[tuple] = []                  # (Schlüssel, Angabe, Rechteck im Editor, hinter, Blatt-Nr.)
        self._frei_sel = None                                 # Schlüssel des gewählten Bildes
        self._frei_vorlaeufig: dict = {}                      # Schlüssel → Angabe während des Ziehens
        self._frei_zug = None                                 # (Art, Griff, Start, Angabe zu Beginn, Rechteck zu Beginn, Blatt)
        self._frei_cursor_gesetzt = False

    # ---- Liste der Bilder ----------------------------------------------------------------------------------------------
    @staticmethod
    def _frei_schluessel(a: dict) -> tuple:
        return ("t", a["_blk"], a["_idx"]) if "_blk" in a else ("k", id(a))

    def _frei_index_pruefen(self, doc, g: dict, z: float, schl: tuple) -> None:
        """Den Index der Körperbilder (Absatz → Angaben) neu bauen, wenn sich Dokument, Zoom, Seite oder Bildzahl geändert haben."""
        if self._lauf is not None:
            self._frei_idx = self._lauf_frei_index()
            return
        if getattr(self, "_frei_schl", None) != schl[:4]:
            roh = FB.koerper_index(doc, g["ch"], g["n"])
            self._frei_idx = {k: [(a, y / z, sp) for a, y, sp in v] for k, v in roh.items()}
            self._frei_schl = schl[:4]

    def _frei_vorlaeufig_anwenden(self, key: tuple, bild, k: int):
        """Das Objekt, das gerade gezogen wird: vorläufige Angabe, Rechteck und (bei Live-Vorschau) das Vorschaubild."""
        a = self._frei_vorlaeufig[key]
        r = QRectF(*self._frei_rechteck(a, k + 1))
        if a.get("_vorschau") is not None:                # Live-Vorschau (Anpassungsgriff, Punkte): das Bild wird laufend neu gezeichnet
            bild = a["_vorschau"]
        return a, bild, r

    def _frei_liste_bauen(self, doc, z: float) -> list[tuple]:
        liste = []
        for k in range(self._blatt_anzahl()):
            oben = self.blatt_oben(k)
            for a, bild, r in FB.objekte_der_seite(self._blatt(k)["pg"] if self._lauf is not None else self.page, doc, k + 1, self._frei_idx):
                key = self._frei_schluessel(a)
                if key in self._frei_vorlaeufig:                      # wird gerade gezogen
                    a, bild, r = self._frei_vorlaeufig_anwenden(key, bild, k)
                liste.append((key, a, bild, QRectF(r.x() * z, oben + r.y() * z, r.width() * z, r.height() * z), bool(a.get("hinter")), k + 1))
        return liste

    def _frei_liste(self) -> list[tuple]:
        """Alle frei positionierten Bilder aller Blätter: (Schlüssel, Angabe, Bild, Rechteck im Editor, hinter, Blatt-Nr.). Unabhängig davon, was
        gerade gezeichnet wird (ein Zeichenvorgang für die blinkende Schreibmarke berührt nur einen kleinen Teil)."""
        doc, g, z = self.document(), self._sp_geo(), self.zoom
        if not hasattr(self, "_frei_treffer"):
            self._frei_init()
        if getattr(self, "_frei_rev", None) != doc.revision():
            self._frei_rev, self._frei_hat = doc.revision(), FB.hat_bilder(doc)
        if not (self.page.bilder or self._frei_hat):
            return []
        schl = (doc.revision(), z, id(self.page), doc.pageCount(), len(self.page.bilder), tuple(sorted(map(repr, self._frei_vorlaeufig.items()))))
        self._frei_index_pruefen(doc, g, z, schl)
        if getattr(self, "_frei_liste_schl", None) == schl:
            return self._frei_liste_wert
        liste = self._frei_liste_bauen(doc, z)
        self._frei_liste_schl, self._frei_liste_wert = schl, liste
        self._frei_treffer = [(key, a, r, hinten, n) for key, a, bild, r, hinten, n in liste]
        return liste

    # ---- Geometrie des gewählten Objekts ---------------------------------------------------------------------------------
    def _frei_rechteck(self, a: dict, n: int):
        from lunivo_writer.modelle.seite import mm_to_px
        pg = self._blatt(n - 1)["pg"] if self._lauf is not None else self.page
        r = FB.rechteck(a, mm_to_px(pg.width_mm), mm_to_px(pg.height_mm), mm_to_px(pg.margin_left_mm), mm_to_px(pg.margin_top_mm),
                        pg.content_width_px, pg.content_height_px, a.get("_ay", 0.0), a.get("_sx"), n)
        return r.x(), r.y(), r.width(), r.height()

    def _frei_angabe(self) -> dict | None:
        """Die Angabe des gewählten freien Objekts (oder None)."""
        return next((x[1] for x in getattr(self, "_frei_treffer", []) if x[0] == self._frei_sel), None)

    @staticmethod
    def _frei_abbilden(r: QRectF, a: dict, rr: QRectF) -> QRectF:
        return G.abbilden(r, a, rr)

    @staticmethod
    def _frei_griff_mitte(r: QRectF, name: str) -> QPointF:
        return G.griff_mitte(r, name)

    def _frei_adj_lagen(self, r: QRectF, a: dict | None) -> dict[str, QPointF]:
        """Lage der Anpassungsgriffe (gelbe Raute) der gewählten Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten."""
        vorl = self.__dict__.get("_frei_adj_wert")
        zieht = vorl is not None and self._frei_zug is not None and self._frei_zug[0] == "anpassen"
        return G.adj_lagen(r, a, vorl if zieht else None)

    # ---- Absatz ----------------------------------------------------------------------------------------------------------
    def _frei_absatz_aendern(self, blk: int, idx: int, neu: dict | None) -> None:
        """Ändert (oder, mit ``neu=None``, entfernt) die Angabe ``idx`` am Absatz ``blk`` — als ein Schritt, den Rückgängig zurücknimmt."""
        b = self.document().findBlockByNumber(blk)
        if not b.isValid():
            return
        liste = FB.aus_absatz(b.blockFormat())
        if idx >= len(liste):
            return
        c = QTextCursor(b)
        c.beginEditBlock()
        if neu is None:
            liste.pop(idx)
        else:
            liste[idx] = neu
        bf = b.blockFormat()
        if liste:
            bf.setProperty(B_BILDANKER, json.dumps(liste, separators=(",", ":")))
        else:
            bf.clearProperty(B_BILDANKER)
        c.setBlockFormat(bf)
        c.endEditBlock()
        self.document().setModified(True)
        self._frei_rev = None
