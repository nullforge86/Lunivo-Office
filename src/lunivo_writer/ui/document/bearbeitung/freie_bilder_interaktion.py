"""Frei positionierte Bilder im Editor: Bedienung mit Maus und Tastatur — anklicken, Griffe, ziehen, ablegen, Entf/Esc/Enter.

Hier steht nur die Interaktion: gezeichnet wird in ``freie_bilder_zeichnen.py``, Maße rechnet ``freie_bilder_geometrie.py``, Knoten und Teile des
Diagramms/SmartArt stehen in ``freie_bilder_knoten.py``, die Schaltflächen und ihre Menüs in ``freie_bilder_knoepfe.py``. Zusammengesetzt wird in
``freie_bilder_bedienung.py`` (``FreieBilderMixin``).
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt

from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.ui.document.bearbeitung import freie_bilder_geometrie as G
from lunivo_writer.ui.document.bearbeitung.freie_bilder_geometrie import CURSOR, GRIFF, GRIFFE


class FreieBilderInteraktionMixin:
    # ---- Treffer -------------------------------------------------------------------------------------------------------
    def _frei_griff_bei(self, pos: QPointF):
        if self._frei_sel is None:
            return None, None
        for treffer in self._frei_treffer:
            if treffer[0] == self._frei_sel:
                name = self._frei_griff_name(pos, treffer[1], treffer[2])
                return (name, treffer) if name else (None, treffer if treffer[2].contains(pos) else None)
        return None, None

    def _frei_griff_name(self, pos: QPointF, a: dict, r: QRectF) -> str | None:
        """Der Griff unter ``pos``: erst die Anpassungsgriffe der Form, dann die acht Größengriffe und der Drehgriff."""
        def nah(c: QPointF) -> bool:
            return abs(pos.x() - c.x()) <= GRIFF and abs(pos.y() - c.y()) <= GRIFF
        for name, c in self._frei_adj_lagen(r, a).items():
            if nah(c):
                return name
        for name in (*GRIFFE, *(() if a.get("art") == "zeichenbereich" else ("rot",))):
            if nah(self._frei_griff_mitte(r, name)):
                return name
        return None

    def _frei_text_bei(self, pos: QPointF) -> bool:
        """Liegt an dieser Stelle Text? Dann gehört der Klick dem Text, nicht einem Bild dahinter."""
        try:
            x, y = self._sp_doc(pos.x(), pos.y())
            return self.document().documentLayout().hitTest(QPointF(x, y), Qt.ExactHit) >= 0
        except Exception:                                                  # noqa: BLE001
            return False

    def _frei_bild_bei(self, pos: QPointF, auch_hinten: bool):
        for t in reversed(self._frei_treffer):                      # zuletzt gezeichnet = oben
            if (auch_hinten or not t[3]) and t[2].contains(pos):
                return t
        return None

    def _frei_gewaehlt_rect(self):
        """(Schlüssel, Rechteck im Editor) des gewählten Objekts oder None."""
        return next(((key, r) for key, a, r, hinten, n in self._frei_treffer if key == self._frei_sel), None)

    # ---- Maus ----------------------------------------------------------------------------------------------------------
    def _frei_maus(self, e, art: str) -> bool:
        """True, wenn das Ereignis ein Bild betrifft und der Editor es nicht weiter behandeln soll."""
        if not hasattr(self, "_frei_treffer"):
            self._frei_init()
        self._frei_liste()
        if not self._frei_treffer or self.isReadOnly():
            return self._frei_maus_leer(art)
        if self._frei_punkte_maus(e, art):
            return True
        pos = e.position()
        if art == "press" and e.button() == Qt.LeftButton:
            if self._frei_sel is not None and self._frei_knopf_klick(e, pos):
                return True
            return self._frei_maus_druecken(e, pos)
        if art == "move":
            return self._frei_maus_bewegen(e, pos)
        if art == "release" and self._frei_zug is not None:
            self._frei_ablegen()
            return True
        return False

    def _frei_maus_leer(self, art: str) -> bool:
        """Keine Bilder oder schreibgeschützt: ein Klick hebt eine alte Auswahl auf; der Editor behandelt das Ereignis."""
        if art == "press" and self._frei_sel is not None:
            self._frei_sel = None; self.viewport().update()
        return False

    def _frei_punkte_maus(self, e, art: str) -> bool:
        """Punkte einer Form bearbeiten: die Maus gehört zuerst der Punktbearbeitung."""
        if self.__dict__.get("_fp_key") is None:
            return False
        from lunivo_writer.ui.document.bearbeitung import freiform_bedienung as FP
        return bool(FP.maus(self, e, art))

    def _frei_knopf_klick(self, e, pos: QPointF) -> bool:
        """Klick auf eine Schaltfläche neben dem gewählten Objekt."""
        gewaehlt = self._frei_gewaehlt_rect()
        if gewaehlt is None:
            return False
        for name, k in self._frei_knopf_rects(gewaehlt[1]).items():
            if k.contains(pos):
                self._frei_knopf(name, e.globalPosition().toPoint())
                return True
        return False

    def _frei_treffer_bei(self, e, pos: QPointF):
        """(Griff, Treffer) unter der Maus: erst Griffe und Rahmen des gewählten Objekts, sonst ein Bild — hinter dem Text mit Strg+Alt, oder wenn an der
        Stelle kein Text liegt (zum Beispiel das Band im Briefkopf)."""
        griff, treffer = self._frei_griff_bei(pos)
        if treffer is None or (griff is None and not treffer[2].contains(pos)):
            treffer = self._frei_bild_bei(pos, bool(e.modifiers() & Qt.ControlModifier and e.modifiers() & Qt.AltModifier) or not self._frei_text_bei(pos))
            griff = None
        return griff, treffer

    def _frei_abwaehlen(self) -> None:
        """Klick ins Leere: Teil, Knoten und Objekt abwählen; ein offener Formatbereich geht zu."""
        if self._frei_sel is not None:
            self._frei_teilwahl_aufheben()
            self._frei_sel = None; self.viewport().update()
            if hasattr(self.window(), "objektformat_folgen"):
                self.window().objektformat_folgen()                  # Text statt Objekt: offener Formatbereich geht zu

    def _frei_format_uebertragen(self, key, merk) -> None:
        """„Format übertragen“ wartet auf das Zielbild: das Format auf das angeklickte Objekt anwenden."""
        self._frei_format_merk = None
        self._frei_sel = key
        from lunivo_writer.editor.objekte import bildlayout as BL
        BL.format_uebertragen(self, BL.ziel(self), merk)
        self.viewport().setCursor(Qt.IBeamCursor)

    def _frei_maus_druecken(self, e, pos: QPointF) -> bool:
        griff, treffer = self._frei_treffer_bei(e, pos)
        if treffer is None:
            self._frei_abwaehlen()
            return False
        key, a, r, hinten, n = treffer
        merk = getattr(self, "_frei_format_merk", None)
        if merk is not None and key != self._frei_sel:                    # „Format übertragen“ wartet auf das Zielbild
            self._frei_format_uebertragen(key, merk)
            return True
        self._frei_auswaehlen(key, a, pos, griff)
        zugart = "drehen" if griff == "rot" else "anpassen" if (griff or "").startswith("adj") else "groesse" if griff else "bewegen"
        self._frei_zug = (zugart, griff, pos, dict(a), QRectF(r), n)
        self.viewport().update()
        return True

    def _frei_auswaehlen(self, key, a: dict, pos: QPointF, griff) -> None:
        """Das Objekt ``key`` wählen: Teil und Knoten eines vorher gewählten anderen Objekts werden abgewählt, ein Klick in das schon markierte
        Diagramm/SmartArt wählt den Teil bzw. Knoten darunter."""
        vorher = self._frei_sel
        if vorher is not None and vorher != key:
            self._frei_teilwahl_aufheben()                                  # ein anderes Objekt: Teil und Knoten des alten sind nicht mehr gewählt
        elif vorher == key and griff is None and a.get("art") in ("diagramm", "smartart"):
            self._frei_teil_klick(pos, a)                                   # Klick in das markierte Diagramm/SmartArt: Teil bzw. Knoten wählen
        self._frei_sel = key
        if hasattr(self.window(), "objektformat_folgen"):
            self.window().objektformat_folgen()

    def _frei_knopf_tipp_zeigen(self, e, pos: QPointF) -> bool:
        """Tooltip der Schaltfläche unter der Maus; True, wenn die Maus über einer Schaltfläche des gewählten Objekts steht."""
        gewaehlt = self._frei_gewaehlt_rect()
        if gewaehlt is None:
            return False
        ueber = False
        for name, k in self._frei_knopf_rects(gewaehlt[1]).items():
            if k.contains(pos) and name in self.KNOPF_TIPPS:
                from PySide6.QtWidgets import QToolTip
                QToolTip.showText(e.globalPosition().toPoint(), self.KNOPF_TIPPS[name], self.viewport(), k.toRect())
                ueber = True
        return ueber

    def _frei_cursor_setzen(self, cursor) -> None:
        self.viewport().setCursor(cursor); self._frei_cursor_gesetzt = True

    def _frei_maus_bewegen(self, e, pos: QPointF) -> bool:
        if self._frei_zug is not None and e.buttons() & Qt.LeftButton:
            self._frei_ziehen(e)
            return True
        ueber_knopf = self._frei_knopf_tipp_zeigen(e, pos)
        griff, treffer = self._frei_griff_bei(pos)
        self._frei_teil_tipp(e, pos, griff)
        if ueber_knopf:
            self._frei_cursor_setzen(Qt.PointingHandCursor)          # Knopf der Schnellleiste (Zahnrad usw.): Hand statt Textcursor
        elif griff:
            self._frei_cursor_setzen(CURSOR[griff])
        elif treffer is not None or self._frei_bild_bei(pos, not self._frei_text_bei(pos)) is not None:
            self._frei_cursor_setzen(Qt.SizeAllCursor)               # das Bild lässt sich anfassen
        elif self._frei_cursor_gesetzt:
            self.viewport().setCursor(Qt.IBeamCursor); self._frei_cursor_gesetzt = False
        return False

    # ---- Ziehen --------------------------------------------------------------------------------------------------------
    def _frei_ziehen_anpassen(self, e, griff: str, a0: dict, r0: QRectF) -> None:
        """Gelbe Raute: der Parameter folgt der Maus, gespeichert wird beim Loslassen."""
        from lunivo_writer.editor.objekte import formen as F
        p = QPointF(e.position())
        if float(a0.get("dreh", 0.0) or 0.0):
            p = G.um_mitte_drehen(p, r0, -float(a0["dreh"]))
        i = int(griff[3:])
        wert = F.anpass_wert((a0.get("daten") or {}).get("form", "Rechteck"), QRectF(r0), p, i)
        self.__dict__["_frei_adj_wert"] = (i, wert)
        self._frei_adj_vorschau(a0, i, wert)
        self.viewport().update()

    def _frei_ziehen_drehen(self, e, a0: dict, r0: QRectF) -> None:
        """Drehgriff: der Winkel zeigt von der Mitte zur Maus (mit Umschalt in 15-Grad-Schritten)."""
        w = G.drehwinkel(r0.center(), e.position(), bool(e.modifiers() & Qt.ShiftModifier))
        self._frei_vorlaeufig[self._frei_sel] = {**a0, "dreh": round(w, 1)}
        self.viewport().update()

    def _frei_ziehen_rahmen(self, e, art: str, griff, start: QPointF, a0: dict, r0: QRectF, n: int) -> None:
        """Verschieben und Größe ändern: der vorläufige Rahmen in Blattkoordinaten."""
        z = self.zoom
        dx, dy = (e.position().x() - start.x()) / z, (e.position().y() - start.y()) / z
        r = QRectF(r0.x() / z, 0, r0.width() / z, r0.height() / z)          # Blattkoordinaten: x wie im Editor, y wird unten ergänzt
        r.moveTop((r0.y() - self.blatt_oben(n - 1)) / z)
        if art == "bewegen":
            r.translate(dx, dy)
        else:
            zuschnitt = bool(self.__dict__.get("_frei_zuschnitt"))
            sperre = bool(a0.get("sperre")) and not zuschnitt       # Seitenverhältnis sperren: auch die Kanten halten es
            frei = bool(e.modifiers() & Qt.ShiftModifier) or (griff in ("n", "s", "e", "w") and not sperre) or zuschnitt
            r = G.groesse_rechteck(r, griff, dx, dy, frei)
        self._frei_vorlaeufig[self._frei_sel] = FB.versatz_fuer(a0, r, self.page, n)
        self.viewport().update()

    def _frei_ziehen(self, e) -> None:
        art, griff, start, a0, r0, n = self._frei_zug
        if art == "anpassen":
            self._frei_ziehen_anpassen(e, griff, a0, r0)
        elif art == "drehen":
            self._frei_ziehen_drehen(e, a0, r0)
        else:
            self._frei_ziehen_rahmen(e, art, griff, start, a0, r0, n)

    def _frei_adj_vorschau(self, a0: dict, i: int, wert: float) -> None:
        """Die Form beim Ziehen der gelben Raute laufend neu zeichnen (nur das Bild, kein Dokumentschritt)."""
        from lunivo_writer.editor.objekte import formen as F
        from lunivo_writer.editor.objekte import frei_objekt as FO
        d = {**FO.FORM_STANDARD, **(a0.get("daten") or {})}
        d["adj"] = F.anpassen(d["form"], wert, d.get("adj"), i)
        n = self.__dict__.get("_frei_vz", 0) + 1
        self.__dict__["_frei_vz"] = n
        self._frei_vorlaeufig[self._frei_sel] = {**a0, "_vorschau": FO.zeichnen("form", d, a0["b"], a0["h"]), "_vz": n}

    def _frei_ablegen(self) -> None:
        zug, self._frei_zug = self._frei_zug, None
        if zug[0] == "anpassen":
            self._frei_vorlaeufig.clear()
            vorl = self.__dict__.pop("_frei_adj_wert", None)
            if vorl is not None:
                from lunivo_writer.editor.objekte import formen as F
                F.anpass_setzen(self, vorl[1], vorl[0])
            self.viewport().update()
            return
        neu = self._frei_vorlaeufig.pop(self._frei_sel, None)
        self._frei_vorlaeufig.clear()
        if neu is None:
            return                                                           # nur angeklickt
        from lunivo_writer.editor.objekte import frei_objekt as FO
        if zug[0] == "groesse" and self.__dict__.get("_frei_zuschnitt"):      # Zuschneiden-Modus: Ziehen schneidet ab (editor/objekte/bildzuschnitt.py)
            from lunivo_writer.editor.objekte import bildzuschnitt as BZ
            neu = BZ.aus_ziehen(zug[3], neu, zug[1])
        self._frei_ablage_speichern(FO.nach_groesse(self, neu))               # Textfeld: Text in der neuen Größe setzen
        self.viewport().update()

    def _frei_ablage_speichern(self, neu: dict) -> None:
        """Die neue Lage/Größe in das Objekt schreiben: frei an der Seite oder am Absatz (dann als ein Rückgängig-Schritt)."""
        if self._frei_sel[0] == "k":
            for a in self.page.bilder:
                if id(a) == self._frei_sel[1]:
                    a.update(FB.ohne_hilfsangaben(neu))
            self.document().setModified(True)
            self.pageApplied.emit()
            return
        from lunivo_writer.editor.objekte import frei_objekt as FO
        self._frei_absatz_aendern(neu["_blk"], neu["_idx"], FB.ohne_hilfsangaben(neu))
        if neu.get("art") == "textfeld":
            FO.kette_aktualisieren(self)                                  # verknüpfte Textfelder: der Text läuft neu von Feld zu Feld

    # ---- Tasten --------------------------------------------------------------------------------------------------------
    def _frei_taste_esc(self) -> bool:
        if self.__dict__.get("_frei_zuschnitt"):               # Esc beendet zuerst den Zuschneiden-Modus
            self.__dict__["_frei_zuschnitt"] = False; self.viewport().update()
            if getattr(self.window(), "befehle", None) is not None:
                self.window().band.aktualisieren()
            return True
        self._frei_teilwahl_aufheben()
        self._frei_sel = None; self.viewport().update()
        return True

    def _frei_taste_loeschen(self) -> bool:
        key, self._frei_sel = self._frei_sel, None
        if key[0] == "k":
            self.page.bilder[:] = [a for a in self.page.bilder if id(a) != key[1]]
            self.document().setModified(True)
            self.pageApplied.emit()
        else:
            self._frei_absatz_aendern(key[1], key[2], None)
        self.viewport().update()
        return True

    def _frei_taste_knoten(self, e) -> bool | None:
        """SmartArt-Knoten: Enter/F2 oder Tippen schreibt im Knoten; None, wenn die Taste nicht dafür ist."""
        if self._frei_knoten_rect() is None or self.__dict__.get("_sa_edit") is not None:
            return None
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
            return self.frei_knoten_edit_starten()
        if e.text() and e.text().isprintable() and not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier)):
            return self.frei_knoten_edit_starten(e.text())
        return None

    def _frei_taste(self, e) -> bool:
        if not hasattr(self, "_frei_treffer") or self._frei_sel is None or self.isReadOnly():
            return False
        if self.__dict__.get("_fp_key") is not None:                              # Punkte bearbeiten: Esc beendet, Entf löscht den Punkt
            from lunivo_writer.ui.document.bearbeitung import freiform_bedienung as FP
            if FP.taste(self, e):
                return True
        if e.key() == Qt.Key_Escape:
            return self._frei_taste_esc()
        knoten = self._frei_taste_knoten(e)
        if knoten is not None:
            return knoten
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):          # im Objekt schreiben
            from lunivo_writer.editor.objekte import frei_objekt as FO
            return FO.bearbeiten_starten(self)
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            return self._frei_taste_loeschen()
        return False
