"""Frei positionierte Bilder im Editor: Teile eines Diagramms und Knoten eines SmartArt — Lage der Knoten, Teil bzw. Knoten per Klick wählen,
Tooltip des Teils unter der Maus, Text im Knoten schreiben (Eingabefeld). Die Fachlogik liegt in ``editor/diagramme/diagramm_teile.py`` und
``editor/objekte/smartart.py``; hier steht nur die Bedienung im Editor. Zusammengesetzt wird in ``freie_bilder_bedienung.py`` (``FreieBilderMixin``).
"""
from __future__ import annotations

import json

from PySide6.QtCore import QPointF, QRectF, Qt

from lunivo_writer.core.farben import Farbe


class FreieBilderKnotenMixin:
    def _frei_sa_geo(self, a: dict) -> dict:
        """Rechtecke der SmartArt-Knoten (logisch), zwischengemerkt, bis sich Knoten oder Größe ändern."""
        from lunivo_writer.editor.objekte import smartart as SA
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

    # ---- Teil eines Diagramms / Knoten eines SmartArt wählen -----------------------------------------------------------------------
    def _frei_teil_klick(self, pos: QPointF, a: dict) -> None:
        """Ein Klick in das markierte Diagramm wählt den Teil darunter, in das markierte SmartArt den Knoten darunter."""
        fenster = self.window()
        if a.get("art") == "diagramm":
            from lunivo_writer.editor.diagramme import diagramm_teile as T
            teil = T.teil_bei(self, pos)
            if teil != (a.get("daten") or {}).get("teil"):
                T.teil_waehlen(self, teil)
        else:
            from lunivo_writer.editor.objekte import smartart as SA
            k = SA.knoten_bei(self, pos)
            if k != (a.get("daten") or {}).get("auswahl"):
                SA.knoten_waehlen(self, k)
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
        a = self._frei_angabe()
        d = (a or {}).get("daten") or {}
        if a is None:
            return
        if a.get("art") == "diagramm" and d.get("teil"):
            from lunivo_writer.editor.diagramme import diagramm_teile as T
            T.teil_waehlen(self, None)
        elif a.get("art") == "smartart" and d.get("auswahl"):
            from lunivo_writer.editor.objekte import smartart as SA
            SA.knoten_waehlen(self, None)

    def _frei_teil_tipp(self, e, pos: QPointF, griff) -> None:
        """Beim Überfahren des markierten Diagramms steht der Name des Teils unter der Maus im Tooltip."""
        a = self._frei_angabe()
        if a is None or a.get("art") != "diagramm" or griff or e.buttons():
            return
        from lunivo_writer.editor.diagramme import diagramm as D
        from lunivo_writer.editor.diagramme import diagramm_teile as T
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
        from PySide6.QtWidgets import QLineEdit
        from lunivo_writer.editor.objekte import smartart as SA
        w = QLineEdit(self.viewport())
        bisher = SA.knoten_text(self, ident) or ""
        ersetzt = bool(self.opt("bearbeiten/tippen_ersetzt", False)) if callable(getattr(self, "opt", None)) else False
        w.setText(text if (text is not None and ersetzt) else bisher + (text or ""))
        w.setAlignment(Qt.AlignCenter)
        f = w.font(); f.setPixelSize(max(8, int(kn.height() * 0.3))); w.setFont(f)
        w.setStyleSheet(f"QLineEdit {{ background: {Farbe.PAPIER}; color: {Farbe.SYMBOL}; border: 1px solid palette(highlight); }}")
        w.setGeometry(kn.toRect())
        return w

    def frei_knoten_edit_starten(self, text: str | None = None) -> bool:
        """Ein Eingabefeld über dem gewählten SmartArt-Knoten (Doppelklick, Enter oder Tippen). ``text``: bereits getippte Zeichen werden hinter den
        Knotentext geschrieben; sie ersetzen ihn nur, wenn „Tippen ersetzt die Auswahl“ an ist (Standard: aus, Markieren löscht nichts)."""
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
        w, ident = ed
        text = w.text()
        w.blockSignals(True); w.hide(); w.deleteLater()
        if not verwerfen:
            from lunivo_writer.editor.objekte import smartart as SA
            if text != (SA.knoten_text(self, ident) or ""):
                SA.knoten_text_setzen(self, ident, text)
        self.viewport().update(); self.setFocus()
