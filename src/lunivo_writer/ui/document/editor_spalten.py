"""Spalten im Editor."""
from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRect, QRectF, QSizeF, Qt
from PySide6.QtGui import QAbstractTextDocumentLayout, QBrush, QColor, QDragMoveEvent, QDropEvent, QMouseEvent, QPainter, QPalette, QPen, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit
from lunivo_writer.services.docx_reader import STYLE_PROP
from lunivo_writer.models.page import PageSettings, mm_to_px
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.document.editor_gemeinsam import BLATT_ABSTAND_PX


class SpaltenBaustein:
    """Spalten im Editor. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/ui/document/document_editor.py``)."""


    # ---- Spalten im Editor -----------------------------------------------------------------------------------------
    def _blatt_aktiv(self) -> bool:
        """Blattmodus (Drucklayout): echte Blätter mit Rand und Zwischenraum; nur das Weblayout ist ein Endlosfluss."""
        return not self.web


    def _mehrspaltig(self) -> bool:
        return (not self.web) and int(self.page.spalten) > 1


    def _sp_geo(self) -> dict:
        """Maße des Textflusses und (bei gleich großen Blättern) jedes Blattes. Bei verschieden großen Blättern (``_qplan``) sind
        ``cb``/``ch`` die größte Textbreite und -höhe; die Maße eines Blattes liefert ``_blatt(k)``."""
        z, pg = self.zoom, self.page
        n = max(1, int(pg.spalten))
        gap = max(10.0, BLATT_ABSTAND_PX * z)
        q = getattr(self, "_qmasse", None)
        return {"n": n, "cb": round((q[0] if q else pg.spalten_breite_px) * z), "g": mm_to_px(pg.spalten_abstand_mm) * z if n > 1 else 0.0,
                "ch": (q[1] if q else pg.content_height_px) * z, "ml": mm_to_px(pg.margin_left_mm) * z, "mt": mm_to_px(pg.margin_top_mm) * z,
                "mb": mm_to_px(pg.margin_bottom_mm) * z,
                "H": mm_to_px(pg.height_mm) * z,              # Höhe eines Blattes
                "gap": gap,                                    # grauer Zwischenraum zwischen zwei Blättern
                "top": gap}                                    # grauer Streifen über dem ersten Blatt


    def blatt_oben(self, nr: int = 0) -> float:
        """y des oberen Randes von Blatt `nr` (0-basiert) im Editor — die Lineale richten sich danach."""
        g = self._sp_geo()
        if getattr(self, "_qplan", None):
            oben = self._q_oben()
            if nr < len(oben):
                return oben[nr]
            return oben[-1] + (nr - len(oben) + 1) * (self._blatt(len(oben) - 1)["H"] + g["gap"])
        return g["top"] + nr * (g["H"] + g["gap"])


    # ---- Blätter verschiedener Größe (editor/querblatt.py) ---------------------------------------------------------
    def _blatt(self, k: int) -> dict:
        """Maße von Blatt `k` im Editor (mit Zoom): x (linker Blattrand), W, H, ml, mt, mb, cw (Textbreite), ch (Texthöhe), pg."""
        z = self.zoom
        plan = getattr(self, "_qplan", None)
        pg = (plan[min(k, len(plan) - 1)] if plan else self.page)
        breite = getattr(self, "_qbreite", mm_to_px(self.page.width_mm))
        return {"x": (breite - mm_to_px(pg.width_mm)) * z / 2 if plan else 0.0, "W": mm_to_px(pg.width_mm) * z,
                "H": mm_to_px(pg.height_mm) * z, "ml": mm_to_px(pg.margin_left_mm) * z, "mt": mm_to_px(pg.margin_top_mm) * z,
                "mb": mm_to_px(pg.margin_bottom_mm) * z, "cw": pg.content_width_px * z, "ch": pg.content_height_px * z, "pg": pg}


    def _q_oben(self) -> list[float]:
        """Obere Blattränder bei verschieden großen Blättern (zwischengespeichert je Plan und Zoom)."""
        schl = (id(self._qplan), len(self._qplan), self.zoom)
        if getattr(self, "_qoben_schl", None) != schl:
            g = self._sp_geo()
            y, oben = g["top"], []
            for k in range(len(self._qplan)):
                oben.append(y)
                y += self._blatt(k)["H"] + g["gap"]
            self._qoben, self._qoben_schl = oben, schl
        return self._qoben


    def _quer_auffrischen(self) -> bool:
        """Plan der Blattgrößen neu bestimmen (nur einspaltig, nicht im Weblayout). → True, wenn sich Breite oder Fluss geändert haben."""
        from lunivo_writer.editor import querblatt
        doc = self.document()
        an = (not self.web) and querblatt.aktiv(doc, self.page)
        alt = getattr(self, "_qmasse", None)
        if an:
            self._qmasse = querblatt.masse(doc, self.page)
            self._qbreite = max(mm_to_px(p.width_mm) for _n, p in querblatt.einrichtungen(doc, self.page))
            self._qplan = querblatt.blattplan(doc, self.page, self._qmasse[1] * self.zoom)
        else:
            self._qmasse, self._qplan = None, None
            self._qbreite = mm_to_px(self.page.width_mm)
        if alt != self._qmasse and not self.web:
            self._sp_einrichten()
            breite = int(self._qbreite * self.zoom) + getattr(self, "_blasen_extra", 0)
            if self.width() != breite:
                self.setFixedWidth(breite)
            return True
        return False


    def _blatt_bei_y(self, vy: float) -> int:
        if getattr(self, "_qplan", None):
            import bisect
            return max(0, bisect.bisect_right(self._q_oben(), vy) - 1)
        g = self._sp_geo()
        return max(0, int((vy - g["top"]) // (g["H"] + g["gap"])))


    def _sp_ursprung(self, lp: int) -> tuple[float, float]:
        """Ecke links oben der Textspalte, in der die logische Seite `lp` des Textflusses steht (Editorkoordinaten)."""
        g = self._sp_geo()
        if getattr(self, "_qplan", None):
            b = self._blatt(lp)
            return b["x"] + b["ml"], self.blatt_oben(lp) + b["mt"]
        s, j = divmod(lp, g["n"])
        return g["ml"] + j * (g["cb"] + g["g"]), self.blatt_oben(s) + g["mt"]


    def _sp_einrichten(self) -> None:
        """Dokument in Spaltenbreite und -höhe legen: feste Zeilenbreite, damit QTextEdit die Seitenhöhe nicht wieder auf „endlos“ setzt."""
        g = self._sp_geo()
        self.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.setLineWrapColumnOrWidth(int(g["cb"]))
        self.document().setPageSize(QSizeF(g["cb"], g["ch"]))
        if self.hasFocus():
            self._sp_timer.start()


    def _sp_view(self, dx: float, dy: float) -> tuple[float, float]:
        """Dokumentkoordinate (fortlaufender Fluss der Spaltenseiten) → Punkt auf dem Blatt."""
        g = self._sp_geo()
        lp = max(0, int((dy + 1.0) // g["ch"]))        # +1: Qt gibt Rechtecke ganzzahlig, die Seitengrenze liegt meist knapp darüber
        x0, y0 = self._sp_ursprung(lp)
        return x0 + dx, y0 + max(0.0, dy - lp * g["ch"])


    def _sp_doc(self, vx: float, vy: float) -> tuple[float, float]:
        """Punkt auf dem Blatt → Dokumentkoordinate; Punkte in Rändern und Lücken landen in der nächsten Spalte."""
        g = self._sp_geo()
        s = self._blatt_bei_y(vy)
        if getattr(self, "_qplan", None):
            b = self._blatt(s)
            letzte = max(0, self.document().pageCount() - 1)
            if s > letzte:
                return 0.0, self.document().size().height() - 1
            y_in = min(max(vy - self.blatt_oben(s) - b["mt"], 0.0), b["ch"] - 1)
            dx = min(max(vx - b["x"] - b["ml"], 0.0), b["cw"])
            return dx, s * g["ch"] + y_in
        y_in = min(max(vy - self.blatt_oben(s) - g["mt"], 0.0), g["ch"] - 1)      # Ränder und Lücken: nächste Textzeile
        j = min(g["n"] - 1, max(0, int((vx - g["ml"] + g["g"] / 2) // (g["cb"] + g["g"]))))
        dx = min(max(vx - (g["ml"] + j * (g["cb"] + g["g"])), 0.0), g["cb"])
        lp = s * g["n"] + j
        letzte = max(0, self.document().pageCount() - 1)
        if lp > letzte:
            return dx, self.document().size().height() - 1
        return dx, lp * g["ch"] + y_in


    def _sp_neu_zeichnen(self, *_) -> None:
        try:
            if self._blatt_aktiv():
                self._sp_caret = True
                self.viewport().update()
        except RuntimeError:                           # beim Abbau ist das Widget schon weg
            pass


    def _sp_blinken(self) -> None:
        if self._blatt_aktiv() and self.hasFocus():
            self._sp_caret = not self._sp_caret
            self.viewport().update()


    def cursorRect(self, *args) -> QRect:
        r = super().cursorRect(*args)
        if self._blatt_aktiv():
            x, y = self._sp_view(r.x(), r.y())
            return QRect(int(x), int(y), r.width(), r.height())
        return r


    def cursorForPosition(self, pos: QPoint) -> QTextCursor:
        if self._blatt_aktiv():
            x, y = self._sp_doc(pos.x(), pos.y())
            pos = QPoint(int(x), int(y))
        return super().cursorForPosition(pos)


    def anchorAt(self, pos: QPoint) -> str:
        if self._blatt_aktiv():
            x, y = self._sp_doc(pos.x(), pos.y())
            pos = QPoint(int(x), int(y))
        return super().anchorAt(pos)


    def _maus_abgebildet(self, e):
        """Mausereignis mit Dokumentkoordinaten (nur bei Spalten); QTextEdit selbst rechnet in Dokumentkoordinaten."""
        if not self._blatt_aktiv():
            return e
        x, y = self._sp_doc(e.position().x(), e.position().y())
        return QMouseEvent(e.type(), QPointF(x, y), e.globalPosition(), e.button(), e.buttons(), e.modifiers())


    def _ziehen_abgebildet(self, e):
        """Ziehen/Ablegen: QTextEdit rechnet in Dokumentkoordinaten, der Editor zeigt aber Blätter → Position abbilden."""
        if not self._blatt_aktiv():
            return e
        x, y = self._sp_doc(e.position().x(), e.position().y())
        art = type(e)
        if art is QDropEvent:
            return QDropEvent(QPointF(x, y), e.possibleActions(), e.mimeData(), e.buttons(), e.modifiers())
        return QDragMoveEvent(QPoint(int(x), int(y)), e.possibleActions(), e.mimeData(), e.buttons(), e.modifiers())


    def _kopffuss_zone(self, y: float) -> str:
        """„kopf“ im oberen, „fuss“ im unteren Rand der Seite (nur Seitenansicht, nicht im Weblayout)."""
        if self.web:
            return ""
        g = self._sp_geo()
        if y < g["top"]:
            return ""
        s = self._blatt_bei_y(y)
        b = self._blatt(s) if getattr(self, "_qplan", None) else g
        rel = y - self.blatt_oben(s)
        if rel > b["H"]:                                 # grauer Zwischenraum
            return ""
        if rel < b["mt"] - 4:
            return "kopf"
        if rel > b["H"] - b["mb"] + 4:
            return "fuss"
        return ""


    def _arbeitsflaeche(self) -> QColor:
        """Grauer Arbeitsbereich zwischen und um die Blätter (gleich dem Grund hinter dem Editor)."""
        return self.palette().color(QPalette.Dark)


    def _blatt_zeichnen(self, e) -> None:
        """Arbeitsfläche, Blätter mit Schatten, dann Text, Auswahl, Schreibmarke und Wellenlinien: jede Seite des Textflusses
        in ihre Spalte auf ihrem Blatt."""
        vp = self.viewport()
        p = QPainter(vp)
        g = self._sp_geo()
        p.fillRect(e.rect(), self._arbeitsflaeche())
        papier = QColor(self._lese_papier or self.page.color or "white")
        sicht = QRectF(e.rect())
        quer = bool(getattr(self, "_qplan", None))
        for k in range(self._blatt_anzahl()):
            if quer:
                bk = self._blatt(k)
                blatt = QRectF(bk["x"], self.blatt_oben(k), bk["W"], bk["H"])
            else:
                blatt = QRectF(0, self.blatt_oben(k), vp.width(), g["H"])
            if not blatt.adjusted(-2, -2, 6, 8).intersects(sicht):
                continue
            # weicher, mehrstufiger Schatten wie bei modernen Office-Programmen: nur nach unten, zu den Seiten hin ausblendend
            tiefe = max(4, int(9 * self.zoom))
            for i in range(tiefe, 0, -1):
                t = i / tiefe
                alpha = int(26 * (1 - t) ** 2 + 2)
                p.fillRect(QRectF(blatt.left() + i * 0.5, blatt.bottom(), blatt.width() - i, i), QColor(16, 24, 40, alpha))
            p.fillRect(blatt, papier)
            self._deckblatt_grafik(p, k, blatt)                              # Grafik eines Deckblatts liegt hinter dem Text
        if self.page.border and not self.page.border.get("vordergrund", True):      # Seitenrahmen hinter dem Text
            from lunivo_writer.editor.pagination import seitenschmuck
            z = self.zoom
            for k in range(self._blatt_anzahl()):
                a = self.blatt_oben(k)
                bk = self._blatt(k) if quer else {"x": 0.0, "W": vp.width(), "H": g["H"], "pg": self.page}
                if QRectF(bk["x"], a, bk["W"], bk["H"]).intersects(sicht):
                    p.save(); p.scale(z, z)
                    seitenschmuck(p, bk["pg"], False, QRectF(bk["x"] / z, a / z, bk["W"] / z, bk["H"] / z), "hinten", False)
                    p.restore()
        self._frei_zeichnen(p, sicht, True)                                  # frei positionierte Bilder hinter dem Text
        doc = self.document()
        lay = doc.documentLayout()
        ctx = QAbstractTextDocumentLayout.PaintContext()
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Text, QColor(self._lese_text or "black"))
        ctx.palette = pal
        auswahl = []
        for es in self.extraSelections():
            a = QAbstractTextDocumentLayout.Selection()
            a.cursor, a.format = es.cursor, es.format
            auswahl.append(a)
        c = self.textCursor()
        if c.hasSelection():
            a = QAbstractTextDocumentLayout.Selection()
            a.cursor = c
            a.format.setBackground(self.palette().highlight())
            a.format.setForeground(self.palette().highlightedText())
            auswahl.append(a)
        ctx.selections = auswahl
        ctx.cursorPosition = c.position() if (self._sp_caret and self.hasFocus() and not c.hasSelection()
                                              and not self.isReadOnly()) else -1
        for lp in range(max(1, doc.pageCount())):
            x0, y0 = self._sp_ursprung(lp)
            hoehe = self._blatt(lp)["ch"] + 1 if quer else g["ch"]
            feld = QRectF(x0 - 6, y0, g["cb"] + 12, hoehe)
            if not feld.intersects(sicht):
                continue
            p.save()
            p.setClipRect(feld)
            p.translate(x0, y0 - lp * g["ch"])
            ctx.clip = QRectF(-6, lp * g["ch"], g["cb"] + 12, hoehe)
            lay.draw(p, ctx)
            p.restore()
        self._frei_zeichnen(p, sicht, False)                                 # … und davor (Foto, Unterschrift)
        p.end()


    def set_web(self, an: bool) -> None:
        if an != self.web:
            self.web = an
            self.apply_page(self.page)
            self.viewport().update()


    def set_web_breite(self, px: int) -> None:
        if px != self._web_breite:
            self._web_breite = px
            if self.web:
                self.apply_page(self.page)


    def set_gliederung(self, an: bool) -> None:
        """Gliederungsansicht: nur Überschriften sind sichtbar; der Text dazwischen ist ausgeblendet (nicht gelöscht)."""
        self.gliederung = an
        b = self.document().firstBlock()
        while b.isValid():
            b.setVisible(not an or b.blockFormat().headingLevel() > 0)
            b = b.next()
        self.document().markContentsDirty(0, self.document().characterCount())
        self.viewport().update()


    def gliederung_ebene(self, delta: int) -> None:
        """Überschrift hoch-/herabstufen (Gliederung): Ebene 1..6, darüber/darunter wird sie zu Text/Titel."""
        c = self.textCursor()
        bf = c.blockFormat()
        lv = bf.headingLevel() + delta
        if bf.headingLevel() and 1 <= lv <= 6:
            self.apply_style(f"Überschrift {lv}")


    def set_zeilennummern(self, an: bool) -> None:
        self.page.zeilennummern = an
        self.viewport().update()


    def _zeilennummern_zeichnen(self, p: QPainter) -> None:
        from lunivo_writer.editor.zeilennummern import nummern
        vp = self.viewport()
        f = p.font(); f.setPixelSize(max(7, int(9 * self.zoom))); p.setFont(f)
        p.setPen(QColor(Farbe.GRAU))
        ml = mm_to_px(self.page.margin_left_mm) * self.zoom
        for _b, z, y_fluss, nr in nummern(self.document(), self._sp_geo()["ch"], self.page.zeilennummern_neu):
            y = self._sp_view(0, y_fluss)[1]
            if -20 < y < vp.height():
                p.drawText(QRectF(ml - 52, y, 44, z.height()), Qt.AlignRight | Qt.AlignVCenter, str(nr))


    def apply_design(self, fliess: str | None = None, kopf: str | None = None, farbe: str | None = None) -> None:
        """Design: Schriftart für Text und Überschriften, Farbe der Überschriften — für das ganze Dokument."""
        doc = self.document()
        cur = QTextCursor(doc)
        cur.beginEditBlock()
        if fliess:
            f = doc.defaultFont(); f.setFamily(fliess); doc.setDefaultFont(f)
        b = doc.firstBlock()
        while b.isValid():
            kopf_block = b.blockFormat().headingLevel() > 0 or (
                b.blockFormat().hasProperty(STYLE_PROP) and b.blockFormat().property(STYLE_PROP) in ("title", "subtitle", "Title", "Subtitle"))
            fam = kopf if kopf_block and kopf else fliess
            if fam or (kopf_block and farbe):
                c = QTextCursor(b)
                c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                cf = QTextCharFormat()
                if fam:
                    cf.setFontFamilies([fam])
                if kopf_block and farbe:
                    cf.setForeground(QColor(farbe))
                c.mergeCharFormat(cf)
            b = b.next()
        cur.endEditBlock()


    def set_absatzrahmen(self, wert: str | None) -> None:
        from lunivo_writer.editor.zusatz import B_RAHMEN

        def f(bf):
            if wert:
                bf.setProperty(B_RAHMEN, wert)
            else:
                bf.clearProperty(B_RAHMEN)
        self._block_merge(f)
        self.viewport().update()


    def absatzrahmen(self):
        """Der Rahmen des Absatzes an der Schreibmarke (bei Auswahl: des ersten Absatzes) als ``Linie``, sonst None."""
        from lunivo_writer.editor.linie import Linie
        from lunivo_writer.editor.zusatz import B_RAHMEN
        c = self.textCursor()
        bf = c.document().findBlock(min(c.position(), c.anchor())).blockFormat()
        return Linie.aus_text(bf.stringProperty(B_RAHMEN)) if bf.hasProperty(B_RAHMEN) else None


    def set_absatzschatten(self, fuell: str | None, muster: tuple[str, str] | None = None) -> None:
        """Füllung (und Muster darüber) der markierten Absätze; ``None`` und kein Muster nehmen sie weg."""
        from lunivo_writer.editor import muster as M
        from lunivo_writer.editor.zusatz import B_MUSTER

        def f(bf):
            bf.clearProperty(B_MUSTER)
            if muster:
                bf.setBackground(M.pinsel(muster[0], muster[1], fuell))
                bf.setProperty(B_MUSTER, M.als_text(muster[0], muster[1], fuell))
            elif fuell:
                bf.setBackground(QBrush(QColor(fuell)))
            else:
                bf.clearBackground()
        self._block_merge(f)
        self.viewport().update()


    def absatzschatten(self):
        """(Füllfarbe oder None, (Musterschlüssel, Musterfarbe) oder None) des Absatzes an der Schreibmarke."""
        from lunivo_writer.editor import muster as M
        from lunivo_writer.editor.zusatz import B_MUSTER
        c = self.textCursor()
        bf = c.document().findBlock(min(c.position(), c.anchor())).blockFormat()
        m = M.aus_text(bf.stringProperty(B_MUSTER)) if bf.hasProperty(B_MUSTER) else None
        if m:
            return m[2], (m[0], m[1])
        bg = bf.background()
        return (bg.color().name() if bg.style() != Qt.NoBrush and bg.color().isValid() else None), None


    def toggle_rtl(self) -> None:
        rtl = self.textCursor().blockFormat().layoutDirection() == Qt.RightToLeft
        self._block_merge(lambda bf: bf.setLayoutDirection(Qt.LeftToRight if rtl else Qt.RightToLeft))


    def _fluss_planen(self) -> None:
        if not self._fluss_laeuft:
            self._fluss.start()


    def _seitenfluss(self) -> None:
        """Umbruchregeln (Zusammenhalten, nicht vom nächsten Absatz trennen, Absatzkontrolle) auf die Seiten anwenden."""
        if self.web or self._fluss_laeuft:
            return
        from lunivo_writer.editor import querblatt, seitenfluss
        self._fluss_laeuft = True
        try:
            doc = self.document()
            self._quer_auffrischen()
            quer = bool(getattr(self, "_qplan", None))
            neu = querblatt.breite_anwenden(doc, self.page, self.zoom, an=quer)       # schmalere Blätter: Einzug nur in der Anzeige
            weitere = (lambda: querblatt.grenzen(doc, self.page, self._sp_geo()["ch"], self.zoom)) if quer else None
            if seitenfluss.anwenden(doc, self.page.content_height_px, weitere) or neu:
                self._quer_auffrischen()
                self.viewport().update()
        finally:
            self._fluss_laeuft = False


    def _hat_effekt(self) -> bool:
        """Gibt es Textstücke mit Effekten, die Lunivo selbst zeichnet (Verlauf, Schatten, Spiegelung, Leuchten, 3D)? Das Ergebnis gilt bis zur nächsten Änderung."""
        if self._effekt_cache is not None:
            return self._effekt_cache
        from lunivo_writer.editor.textfx import hat_zeichen_effekt
        gefunden = False
        b = self.document().firstBlock()
        while b.isValid() and not gefunden:
            it = b.begin()
            while not it.atEnd():
                if hat_zeichen_effekt(it.fragment().charFormat()):
                    gefunden = True; break
                it += 1
            b = b.next()
        self._effekt_cache = gefunden
        return gefunden


    def _hat_tabfuell(self) -> bool:
        from lunivo_writer.editor.zusatz import B_TABFUELL
        b = self.document().firstBlock()
        while b.isValid():
            if b.blockFormat().hasProperty(B_TABFUELL):
                return True
            b = b.next()
        return False


    def _hat_mehrstufig(self) -> bool:
        from lunivo_writer.editor.zusatz import B_MEHRSTUFIG
        b = self.document().firstBlock()
        while b.isValid():
            if b.blockFormat().hasProperty(B_MEHRSTUFIG):
                return True
            b = b.next()
        return False


    def _hat_rahmen(self) -> bool:
        from lunivo_writer.editor.zusatz import B_RAHMEN
        b = self.document().firstBlock()
        while b.isValid():
            if b.blockFormat().hasProperty(B_RAHMEN):
                return True
            b = b.next()
        return False


    def set_gitter(self, an: bool) -> None:
        self.gitter = an
        self.viewport().update()


    def seitenspannen(self) -> list[tuple[int, int]]:
        """Senkrechte Bereiche (von, bis) jedes Blattes im Editor."""
        if self.web:
            h = self.viewport().height() + self.verticalScrollBar().value()
            return [(0, max(h, int(self.document().size().height())))]
        g = self._sp_geo()
        if getattr(self, "_qplan", None):
            return [(int(self.blatt_oben(k)), int(self.blatt_oben(k) + self._blatt(k)["H"])) for k in range(self._blatt_anzahl())]
        return [(int(self.blatt_oben(k)), int(self.blatt_oben(k) + g["H"])) for k in range(self._blatt_anzahl())]


    def _wasserzeichen_je_blatt(self) -> list | None:
        """Wasserzeichen je Blatt, wenn ein Abschnitt ein eigenes hat („Übernehmen für: Aktueller Abschnitt“); sonst None."""
        from lunivo_writer.editor import abschnitte as AB
        doc = self.document()
        schl = (doc.revision(), id(self.page.watermark), tuple(self.seitenwechsel))
        if getattr(self, "_wz_schl", None) != schl:
            eigene = {i + 1: ps.watermark for i, (_n, _t, ps) in enumerate(AB.umbrueche(doc)) if (ps.watermark or {}).get("abschnitt")}
            liste = None
            if eigene:
                anfaenge = [0] + list(self.seitenwechsel)
                liste = [eigene.get(AB.index_bei(doc, a), self.page.watermark) for a in anfaenge]
            self._wz_schl, self._wz_liste = schl, liste
        return self._wz_liste

    def _deckblatt_grafik(self, p: QPainter, k: int, blatt: QRectF) -> None:
        """Ganzseitiges Bild (Deckblatt, ``editor/deckblatt.py``) des Blattes ``k`` auf die Blattfläche, vor dem Text."""
        if self.web:
            return
        je_blatt = self._wasserzeichen_je_blatt()
        w = je_blatt[min(k, len(je_blatt) - 1)] if je_blatt else self.page.watermark
        if (w or {}).get("ganzseitig"):
            from lunivo_writer.editor import wasserzeichen as WZ
            WZ.zeichnen(p, w, blatt)

    def _schmuck_zeichnen(self, p: QPainter) -> None:
        pg, z = self.page, self.zoom
        je_blatt = None if self.web else self._wasserzeichen_je_blatt()
        if self.web or not (pg.border or pg.watermark or je_blatt):
            return
        from lunivo_writer.editor.pagination import seitenschmuck
        vp = self.viewport()
        quer = bool(getattr(self, "_qplan", None))
        for k, (a, b) in enumerate(self.seitenspannen()):
            if b < 0 or a > vp.height():
                continue
            bk = self._blatt(k) if quer else {"x": 0.0, "W": vp.width(), "pg": pg}
            bp = bk["pg"]
            if je_blatt:
                bp = bp.copy(); bp.watermark = je_blatt[min(k, len(je_blatt) - 1)]
            if (bp.watermark or {}).get("ganzseitig"):                       # schon hinter dem Text gezeichnet (_deckblatt_grafik)
                bp = bp.copy(); bp.watermark = None
            p.save()
            p.scale(z, z)
            seitenschmuck(p, bp, False, QRectF(bk["x"] / z, a / z, bk["W"] / z, (b - a) / z), "vorn")
            p.restore()


    def _gitter_zeichnen(self, p: QPainter) -> None:
        vp = self.viewport()
        schritt = mm_to_px(10) * self.zoom
        if schritt < 6:
            return
        c = QColor(Farbe.GRAU); c.setAlpha(70)
        p.setPen(QPen(c, 1))
        x = schritt
        while x < vp.width():
            p.drawLine(int(x), 0, int(x), vp.height()); x += schritt
        y = schritt
        while y < vp.height():
            p.drawLine(0, int(y), vp.width(), int(y)); y += schritt


    def seitenfarbe_anwenden(self) -> None:
        c = self.page.color or "white"
        # der Rahmen hat die Farbe der Arbeitsfläche: um das Blatt herum ist kein Strich zu sehen
        self.setStyleSheet("QTextEdit { background: palette(dark); color: black; border: none; }")


    def set_zoom(self, faktor: float) -> None:
        """Ansicht vergrößern/verkleinern. Das Dokument selbst (Schriftgrößen, Maße) bleibt unverändert."""
        faktor = max(self.ZOOM_MIN, min(self.ZOOM_MAX, round(faktor, 3)))
        if abs(faktor - self.zoom) < 1e-6:
            return
        self.zoom = faktor
        self.apply_page(self.page)
        self.viewport().update()
        self.zoomChanged.emit(faktor)


    def page_settings_changed(self, page: PageSettings) -> None:
        """Seiteneinrichtung ändern — für den Abschnitt, in dem die Schreibmarke steht (der erste Abschnitt ist das Dokument)."""
        from lunivo_writer.editor import abschnitte as AB
        nr = self.abschnitt_nr()
        if nr > 0 and AB.setzen(self.document(), nr, page):
            self._recount()
            self.viewport().update()
        else:
            self.apply_page(page)
        self.document().setModified(True)
