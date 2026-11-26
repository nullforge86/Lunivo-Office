"""Frei positionierte Bilder im Editor: Teile eines Diagramms und Knoten eines SmartArt — Lage der Knoten, Teil bzw. Knoten per Klick wählen,
Tooltip des Teils unter der Maus, Text im Knoten schreiben (Eingabefeld). Die Fachlogik liegt in ``editor/diagramme/diagramm_teile.py`` und
``editor/objekte/smartart.py``; hier steht nur die Bedienung im Editor. Zusammengesetzt wird in ``freie_bilder_bedienung.py`` (``FreieBilderMixin``).
"""
from __future__ import annotations

import json

from PySide6.QtCore import QPointF, QRectF, Qt

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.darstellung import knoten_eingabe, knoten_zeilen_eingabe
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld


class FreieBilderKnotenMixin:
    def _frei_sa_geo(self, a: dict) -> dict:
        """Rechtecke der SmartArt-Knoten (logisch), zwischengemerkt, bis sich Knoten oder Größe ändern."""
        from vcl.qt.rendering import smartart as SA
        d, b, h = a.get("daten") or {}, float(a["b"]), float(a["h"])
        schl = (json.dumps({k: v for k, v in d.items() if k != "auswahl"}, sort_keys=True, default=str), round(b), round(h))
        c = self.__dict__.get("_sa_geo")
        if c is None or c[0] != schl:
            c = (schl, SA.knoten_rechtecke(d, b, h)); self.__dict__["_sa_geo"] = c
        return c[1]

    def _frei_knoten_rect(self, r: QRectF | None = None) -> QRectF | None:
        """Der gewählte SmartArt-Knoten in Editor-Koordinaten (ohne Drehung) oder None."""
        a = self._frei_angabe()
        if a is None or a.get("art") != "smartart":
            return None
        ident = (a.get("daten") or {}).get("auswahl")
        if r is None:
            r = next((x[2] for x in self._frei_treffer if x[0] == self._frei_sel), None)
        rr = self._frei_sa_geo(a).get(ident) if ident else None
        return self._frei_abbilden(r, a, rr) if (rr is not None and r is not None) else None

    def frei_teil_rahmen(self, r: QRectF) -> tuple:
        """(Drehwinkel, Mitte des Objekts, [(Rechteck, Griffpunkte)]) des gewählten Diagrammteils bzw. SmartArt-Knotens in Koordinaten der Ansicht;
        ``r`` ist das Rechteck des gewählten Objekts in der Ansicht. Ohne gewählten Teil ist die Liste leer. Die Ansicht zeichnet daraus Rahmen und Griffe."""
        o = self.objekt_gewaehlt()
        if o is None or o.art not in ("diagramm", "smartart") or self.__dict__.get("_frei_zuschnitt"):
            return 0.0, QPointF(), []
        a = self._frei_angabe()
        if a is None:
            return 0.0, QPointF(), []
        rects, achse = [], None
        if a.get("art") == "diagramm":
            from vcl.qt.rendering import diagramme as T
            d = a.get("daten") or {}
            teil = d.get("teil")
            if not teil or teil == "diagrammbereich" or teil not in {k for k, _n in T.teile(d)}:
                return 0.0, QPointF(), []
            geo = T.teil_geo_gemerkt(self, d, float(a["b"]), float(a["h"]))
            rs = geo.get("balken_" + teil.removeprefix("reihe_")) if teil.startswith("reihe_") else None
            rs = rs or ([geo[teil]] if isinstance(geo.get(teil), QRectF) else [])
            rects = [self._frei_abbilden(r, a, x) for x in rs]
            achse = "h" if teil == "achse_horizontal" else "v" if teil == "achse_vertikal" else "kein" if teil == "zeichnungsbereich" else None
        else:
            kn = self._frei_bildfeld_rect(r, a) or self._frei_punktfeld_rect(r, a) or self._frei_knoten_rect(r)
            rects = [kn] if kn is not None else []
        return float(a.get("dreh", 0.0) or 0.0), r.center(), [(x, self._frei_teil_griffe(x, achse)) for x in rects]

    @staticmethod
    def _frei_teil_griffe(x: QRectF, achse) -> list:
        """Die Griffpunkte am Rahmen eines Teils: an einer Achse die beiden Enden, am Zeichnungsbereich keine, sonst die acht des Rahmens."""
        from vcl.qt.widgets.dokumentansicht.bearbeitung.freie_bilder_geometrie import GRIFFE
        if achse == "kein":
            return []
        if achse == "h":
            return [QPointF(x.left(), x.center().y()), QPointF(x.right(), x.center().y())]
        if achse == "v":
            return [QPointF(x.center().x(), x.top()), QPointF(x.center().x(), x.bottom())]
        return [QPointF(x.left() + x.width() * fx, x.top() + x.height() * fy) for fx, fy in GRIFFE.values()]

    # ---- Bildfeld eines SmartArt-Knotens (Layouts mit Bild je Eintrag) ---------------------------------------------------------------
    def _frei_bildfeld_gewaehlt(self, a: dict | None = None) -> str | None:
        """Die Id des Knotens, dessen Bildfeld gewählt ist (Klick in das Bildfeld des gewählten Knotens), sonst None."""
        a = a or self._frei_angabe()
        ident = self.__dict__.get("_sa_bildfeld")
        if a is None or a.get("art") != "smartart" or not ident:
            return None
        return ident if ident == (a.get("daten") or {}).get("auswahl") else None

    def _frei_bildfeld_rect(self, r: QRectF, a: dict) -> QRectF | None:
        """Das gewählte Bildfeld in Koordinaten der Ansicht oder None."""
        ident = self._frei_bildfeld_gewaehlt(a)
        if ident is None:
            return None
        rr = self._frei_sa_felder(a)[0].get(ident)
        return self._frei_abbilden(r, a, rr) if rr is not None else None

    def _frei_sa_felder(self, a: dict) -> tuple:
        """(Bildfelder, Felder der Aufzählungspunkte) der SmartArt-Knoten (logisch), zwischengemerkt, bis sich Knoten oder Größe ändern."""
        from vcl.qt.rendering import smartart as SA
        d, b, h = a.get("daten") or {}, float(a["b"]), float(a["h"])
        schl = (json.dumps({k: v for k, v in d.items() if k != "auswahl"}, sort_keys=True, default=str), round(b), round(h))
        c = self.__dict__.get("_sa_feld_geo")
        if c is None or c[0] != schl:
            c = (schl, (SA.bild_rechtecke(d, b, h), SA.punkt_rechtecke(d, b, h))); self.__dict__["_sa_feld_geo"] = c
        return c[1]

    # ---- Feld mit den Aufzählungspunkten eines SmartArt-Knotens ------------------------------------------------------------------------
    def _frei_punktfeld(self, a: dict | None = None):
        """(Id, Rechteck logisch, Überschrift steht mit im Feld) des gewählten Felds mit Aufzählungspunkten (Klick in das Feld des gewählten Knotens)
        oder None."""
        a = a or self._frei_angabe()
        ident = self.__dict__.get("_sa_punktfeld")
        if a is None or a.get("art") != "smartart" or not ident or ident != (a.get("daten") or {}).get("auswahl"):
            return None
        feld = self._frei_sa_felder(a)[1].get(ident)
        return (ident, feld[0], feld[1]) if feld is not None else None

    def _frei_punktfeld_rect(self, r: QRectF, a: dict) -> QRectF | None:
        """Das gewählte Feld mit Aufzählungspunkten in Koordinaten der Ansicht oder None."""
        pf = self._frei_punktfeld(a)
        return self._frei_abbilden(r, a, pf[1]) if pf is not None else None

    def _frei_punktfeld_edit_starten(self, text: str | None) -> bool:
        """Mehrzeiliges Eingabefeld über dem gewählten Feld mit Aufzählungspunkten: eine Zeile je Punkt (steht die Überschrift mit im Feld, ist sie
        die erste Zeile). Esc verwirft, Klick daneben übernimmt. ``False``, wenn kein solches Feld gewählt ist."""
        a = self._frei_angabe()
        pf = self._frei_punktfeld(a)
        r = next((x[2] for x in self._frei_treffer if x[0] == self._frei_sel), None)
        if pf is None or r is None:
            return False
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QPlainTextEdit
        from vcl.qt.rendering import smartart as SA
        editor = self

        class Feld(QPlainTextEdit):
            def keyPressEvent(self, e):
                if e.key() == Qt.Key_Escape:
                    editor._frei_knoten_edit_ende(True)
                    return
                super().keyPressEvent(e)

            def focusOutEvent(self, e):
                super().focusOutEvent(e)
                editor._frei_knoten_edit_ende(False)

        self._frei_knoten_edit_ende(True)
        ident, rr, mit_kopf = pf
        w = Feld(self.viewport())
        w.setPlainText("\n".join(SA.knoten_zeilen(self, ident, mit_kopf)))
        knoten_zeilen_eingabe(w)
        w.setGeometry(self._frei_abbilden(r, a, rr).toRect())
        self.__dict__["_sa_edit"] = (w, ident, mit_kopf)
        w.show(); w.setFocus()
        w.moveCursor(QTextCursor.MoveOperation.End)
        if text:
            w.insertPlainText(text)
        return True

    def frei_knoten_bild_waehlen(self) -> bool:
        """Das gewählte Bildfeld bekommt ein Bild aus einer Datei (Doppelklick oder Enter); ``False``, wenn kein Bildfeld gewählt ist."""
        ident = self._frei_bildfeld_gewaehlt()
        if ident is None:
            return False
        from vcl.qt.rendering import smartart as SA
        from vcl.qt.rendering.formen import bild_aus_datei
        from vcl.qt.widgets.bausteine.symbole.medien import BILD_FILTER
        from vcl.qt.widgets.dialoge.dokument import Dateifenster
        pfad, _ = Dateifenster.getOpenFileName(self.window(), "Bild einfügen", "", BILD_FILTER)
        if pfad:
            SA.knoten_bild_setzen(self, ident, bild_aus_datei(pfad, still=True))
            self.viewport().update()
        return True

    def frei_bildfeld_gewaehlt(self) -> bool:
        """Ob das Bildfeld des gewählten SmartArt-Knotens gewählt ist (für das Rechtsklick-Menü)."""
        return self._frei_bildfeld_gewaehlt() is not None

    def frei_knoten_hat_bild(self) -> bool:
        """Ob der Knoten des gewählten Bildfelds ein Bild hat."""
        from vcl.qt.rendering import smartart as SA
        ident = self._frei_bildfeld_gewaehlt()
        return ident is not None and bool(SA.knoten_bild(self, ident))

    def frei_knoten_bild_entfernen(self) -> bool:
        """Das Bild aus dem gewählten Bildfeld entfernen (der Platzhalter kommt zurück); ``False``, wenn dort keines ist."""
        from vcl.qt.rendering import smartart as SA
        ident = self._frei_bildfeld_gewaehlt()
        if ident is None or not SA.knoten_bild(self, ident):
            return False
        SA.knoten_bild_setzen(self, ident, None)
        self.viewport().update()
        return True

    def _frei_knoten_bild_taste(self, e) -> bool:
        """Taste bei gewähltem Bildfeld: Enter/F2 wählt ein Bild, Entf/Rücktaste entfernt das Bild des Knotens."""
        ident = self._frei_bildfeld_gewaehlt()
        if ident is None:
            return False
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
            return self.frei_knoten_bild_waehlen()
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            return self.frei_knoten_bild_entfernen()
        return False

    def frei_teil_tipp(self, e) -> None:
        """Mausbewegung über dem gewählten Objekt (kein Griff, kein Knopf): Name des Diagrammteils als Tooltip."""
        self._frei_teil_tipp(e, e.position(), None)

    def frei_knoten_taste(self, e) -> bool:
        """Taste bei gewähltem SmartArt-Knoten: Enter/F2 oder Tippen schreibt im Knoten; ``True``, wenn die Taste dazu gehört."""
        if self._frei_knoten_rect() is None or self.__dict__.get("_sa_edit") is not None:
            return False
        if self._frei_knoten_bild_taste(e):
            return True
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
            return self.frei_knoten_edit_starten()
        if e.text() and e.text().isprintable() and not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier)):
            return self.frei_knoten_edit_starten(e.text())
        return False

    # ---- Teil eines Diagramms / Knoten eines SmartArt wählen -----------------------------------------------------------------------
    def _frei_teil_klick(self, pos: QPointF, a: dict) -> None:
        """Ein Klick in das markierte Diagramm wählt den Teil darunter, in das markierte SmartArt den Knoten darunter."""
        fenster = self.window()
        if a.get("art") == "diagramm":
            from vcl.qt.rendering import diagramme as T
            teil = T.teil_bei(self, pos)
            if teil != (a.get("daten") or {}).get("teil"):
                T.teil_waehlen(self, teil)
        else:
            from vcl.qt.rendering import smartart as SA
            k = SA.knoten_bei(self, pos)
            punkte = SA.punktfeld_bei(self, pos)
            punkte = punkte if punkte is not None and k in (None, punkte) else None     # das Feld gehört zum Knoten; Unterknoten darin gehen vor
            k = punkte or k
            if k != (a.get("daten") or {}).get("auswahl"):
                SA.knoten_waehlen(self, k)
            self.__dict__["_sa_bildfeld"] = SA.bildfeld_bei(self, pos)          # Klick in das Bildfeld: das Feld statt des Knotens ist gewählt
            self.__dict__["_sa_punktfeld"] = punkte if self.__dict__["_sa_bildfeld"] is None else None      # Klick in die Aufzählungspunkte
        self._frei_rev = None
        if hasattr(fenster, "band"):
            fenster.band.aktualisieren()
        if hasattr(fenster, "diagrammformat_folgen"):
            fenster.diagrammformat_folgen()
        if hasattr(fenster, "smartartformat_folgen"):
            fenster.smartartformat_folgen()
        self.viewport().update()

    def _frei_teilwahl_aufheben(self) -> None:
        """Vor dem Abwählen des Objekts: den gewählten Diagrammteil bzw. SmartArt-Knoten wieder abwählen."""
        self._frei_knoten_edit_ende(True)
        self.__dict__.pop("_sa_bildfeld", None)
        self.__dict__.pop("_sa_punktfeld", None)
        a = self._frei_angabe()
        d = (a or {}).get("daten") or {}
        if a is None:
            return
        if a.get("art") == "diagramm" and d.get("teil"):
            from vcl.qt.rendering import diagramme as T
            T.teil_waehlen(self, None)
        elif a.get("art") == "smartart" and d.get("auswahl"):
            from vcl.qt.rendering import smartart as SA
            SA.knoten_waehlen(self, None)

    def _frei_teil_tipp(self, e, pos: QPointF, griff) -> None:
        """Beim Überfahren des markierten Diagramms steht der Name des Teils unter der Maus im Tooltip."""
        a = self._frei_angabe()
        if a is None or a.get("art") != "diagramm" or griff or e.buttons():
            return
        from vcl.qt.rendering import diagramme as D
        from vcl.qt.rendering import diagramme as T
        teil = T.teil_bei(self, pos)
        if teil is None or teil == self.__dict__.get("_dg_hover"):
            self.__dict__["_dg_hover"] = teil
            return
        self.__dict__["_dg_hover"] = teil
        from PySide6.QtWidgets import QToolTip
        QToolTip.showText(e.globalPosition().toPoint(), dict(D.teile(a.get("daten") or {})).get(teil, ""), self.viewport())

    # ---- Text im SmartArt-Knoten schreiben -------------------------------------------------------------------------------------------
    def _frei_knoten_feld(self, kn: QRectF, ident, text: str | None):
        """Das Eingabefeld über dem Knoten ``ident``: Knotentext, dahinter (oder statt seiner, mit „Tippen ersetzt die Auswahl“) die getippten Zeichen."""
        from vcl.qt.rendering import smartart as SA
        w = zeilenfeld("frei", eltern=self.viewport())
        bisher = SA.knoten_text(self, ident) or ""
        ersetzt = bool(self.opt("bearbeiten/tippen_ersetzt", False)) if callable(getattr(self, "opt", None)) else False
        w.setText(text if (text is not None and ersetzt) else bisher + (text or ""))
        w.setAlignment(Qt.AlignCenter)
        f = w.font(); f.setPixelSize(max(8, int(kn.height() * 0.3))); w.setFont(f)
        knoten_eingabe(w)
        w.setGeometry(kn.toRect())
        return w

    def frei_knoten_edit_starten(self, text: str | None = None) -> bool:
        """Ein Eingabefeld über dem gewählten SmartArt-Knoten (Doppelklick, Enter oder Tippen). ``text``: bereits getippte Zeichen werden hinter den
        Knotentext geschrieben; sie ersetzen ihn nur, wenn „Tippen ersetzt die Auswahl“ an ist (Standard: aus, Markieren löscht nichts)."""
        if self._frei_punktfeld_edit_starten(text):                      # Feld mit Aufzählungspunkten: mehrzeilig schreiben
            return True
        kn = self._frei_knoten_rect()
        a = self._frei_angabe()
        if kn is None or a is None:
            return False
        self._frei_knoten_edit_ende(True)
        ident = (a.get("daten") or {}).get("auswahl")
        w = self._frei_knoten_feld(kn, ident, text)
        self.__dict__["_sa_edit"] = (w, ident)
        w.editingFinished.connect(lambda: self._frei_knoten_edit_ende(False))
        w.show(); w.setFocus(); w.deselect() if text is not None else w.selectAll()
        if text is not None:
            w.setCursorPosition(len(w.text()))
        return True

    def _frei_knoten_edit_ende(self, verwerfen: bool = False) -> None:
        """Das Eingabefeld schließen und den Text in den Knoten übernehmen (``verwerfen``: nicht übernehmen)."""
        ed = self.__dict__.pop("_sa_edit", None)
        if ed is None:
            return
        w, ident, *punktfeld = ed
        text = w.toPlainText() if punktfeld else w.text()
        w.blockSignals(True); w.hide(); w.deleteLater()
        if not verwerfen:
            from vcl.qt.rendering import smartart as SA
            if punktfeld:                                                # Feld mit Aufzählungspunkten: eine Zeile je Punkt
                zeilen = text.split("\n")
                if [z for z in zeilen if z.strip()] != SA.knoten_zeilen(self, ident, punktfeld[0]):
                    SA.knoten_zeilen_setzen(self, ident, zeilen, punktfeld[0])
            elif text != (SA.knoten_text(self, ident) or ""):
                SA.knoten_text_setzen(self, ident, text)
        self.viewport().update(); self.setFocus()
