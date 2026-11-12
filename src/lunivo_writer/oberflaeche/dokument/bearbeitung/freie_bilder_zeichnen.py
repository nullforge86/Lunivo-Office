"""Frei positionierte Bilder im Editor: Darstellung — die Bilder selbst, der Auswahlrahmen mit Griffen, die Schaltflächen neben dem Objekt und die Rahmen
um gewählte Diagrammteile und SmartArt-Knoten. Reine Darstellung: Maus und Tastatur stehen in ``freie_bilder_interaktion.py``, Maße in
``freie_bilder_geometrie.py``; zusammengesetzt wird in ``freie_bilder_bedienung.py`` (``FreieBilderMixin``).
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.oberflaeche.baukasten.basis.mass import ICON_FREIBILD_BEDIENUNG
from lunivo_writer.oberflaeche.baukasten.geruest import schnellleiste_zustand as SZ
from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_geometrie import GRIFF, GRIFFE, ROT_ABSTAND, SINNBILD_GELB, SINNBILD_GELB_HELL, SINNBILD_KONTUR


class FreieBilderZeichnenMixin:
    # ---- Bilder ------------------------------------------------------------------------------------------------------
    def _frei_edit_nachfuehren(self) -> None:
        """Das Eingabefeld im SmartArt-Knoten bzw. im Objekt folgt dem Blatt."""
        if self.__dict__.get("_sa_edit") is not None:
            kn = self._frei_knoten_rect()
            if kn is not None:
                self._sa_edit[0].setGeometry(kn.toRect())
        if getattr(self, "_frei_edit", None) is not None:
            from lunivo_writer.editor.objekte import frei_objekt as FO
            FO.edit_platzieren(self)

    def _frei_bild_zeichnen(self, p: QPainter, r: QRectF, a: dict, bild) -> None:
        z = self.zoom
        p.save(); p.translate(r.x(), r.y()); p.scale(z, z)
        FB.bild_zeichnen(p, bild, QRectF(0, 0, r.width() / z, r.height() / z), bool(a.get("ellipse")), a.get("rand"), float(a.get("dreh", 0.0)), a.get("fuell"),
                         a.get("_fuellbild") or (a.get("fuell") or {}).get("bild"), a.get("fx"))
        p.restore()

    def _frei_zeichnen(self, p: QPainter, sicht: QRectF, hinter: bool) -> None:
        """Bilder der sichtbaren Blätter, hinter (``hinter``) oder vor dem Text; die vorderen zeichnen auch die Auswahl."""
        self._frei_edit_nachfuehren()
        for key, a, bild, r, hinten, n in self._frei_liste():
            if hinten != hinter or not r.intersects(sicht):
                continue
            if getattr(self, "_frei_edit", None) is not None and key == self._frei_edit_key:      # wird gerade im Objekt geschrieben: das Eingabefeld zeigt den Text
                from PySide6.QtGui import QImage
                bild = QImage(1, 1, QImage.Format_ARGB32); bild.fill(0)
            self._frei_bild_zeichnen(p, r, a, bild)
        if not hinter and self._frei_sel is not None:
            self._frei_auswahl_ueber(p, sicht)

    def _frei_auswahl_ueber(self, p: QPainter, sicht: QRectF) -> None:
        """Die Auswahl des gewählten Objekts (Textmarkierung, Rahmen, Griffe, Knöpfe) über den Bildern."""
        for key, a, bild, r, hinten, n in self._frei_liste():
            if key == self._frei_sel and r.intersects(sicht):
                self._frei_text_markieren(p, r, a, bild)
                self._frei_auswahl_zeichnen(p, r, a)

    @staticmethod
    def _frei_text_markieren(p: QPainter, r: QRectF, a: dict, bild) -> None:
        """WordArt wie in der Vorlage: der Text im gewählten Objekt ist grau hinterlegt (nur der Text, kein Kasten über dem Objekt)."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        t = FO.text_bereich(a, bild)
        if t is not None:
            p.save(); p.setPen(Qt.NoPen); p.setBrush(QColor(110, 110, 110, 95))
            p.drawRect(QRectF(r.x() + t.x() * r.width(), r.y() + t.y() * r.height(), t.width() * r.width(), t.height() * r.height()))
            p.restore()

    # ---- Schaltflächen neben dem Objekt: Lage ----------------------------------------------------------------------------
    KNOPF = 30.0                                              # Kantenlänge einer Schaltfläche neben dem Bild
    KNOPF_TIPPS = {"layout": "Layoutoptionen", "formstile": "Formeffekte", "fuell": "Formfüllung", "minus": "Schnellleiste einklappen",
                   "anker": "Absatz-Layout", "lupe": "Vergrößern", "zuschnitt": "Zuschneiden",
                   "dg_element": "Diagrammelemente", "dg_stile": "Diagrammstile", "zahnrad": "Formatierung", "dg_filter": "Diagrammfilter",
                   "sa_form": "Form einfügen", "sa_layout": "Layout", "sa_level": "Level", "sa_bullet": "Aufzählungszeichen einfügen",
                   "sa_stil": "Formvorlagen",
                   "kontur": "Formkontur\n\nFarbe, Breite und Linienart für die Konturlinie der ausgewählten Form auswählen.\n\n"
                             "Auf den Pfeil klicken, um detaillierte Einstellungen für die Konturlinie auszuwählen."}
    # Knopfsätze genau nach den Fotos der Vorlage (von oben nach unten); nur beim Diagramm zeigt das Foto das Zahnrad (Seitenleiste „Formatierung“)
    KNOEPFE = ("layout", "formstile", "fuell", "kontur")                  # Form: Layoutoptionen, Formstile, Füllung, Kontur
    KNOEPFE_BILD = ("layout", "lupe", "zuschnitt")                        # Bild: Layoutoptionen, Vergrößern, Zuschneiden
    KNOEPFE_DIAGRAMM = ("layout", "dg_element", "dg_stile", "dg_filter", "zahnrad")   # Diagramm: Layoutoptionen, Elemente, Stile, Filter, Formatierung
    KNOEPFE_SMARTART_LEER = ("layout", "fuell", "kontur")                 # SmartArt ohne gewählten Knoten: Layoutoptionen, Füllung, Kontur
    KNOEPFE_SMARTART = ("sa_form", "sa_layout", "sa_level", "sa_bullet", "sa_stil")    # am gewählten SmartArt-Knoten
    KNOPF_SYMBOLE = {"lupe": "lupe", "zuschnitt": "crop", "dg_element": "diagrammteil", "dg_stile": "pinsel", "zahnrad": "zahnrad", "dg_filter": "funnel",
                     "sa_form": "network", "sa_layout": "layout-dashboard", "sa_level": "workflow", "sa_bullet": "list-plus", "sa_stil": "pinsel"}

    def _frei_leiste(self) -> tuple[str, ...]:
        """Die Schaltflächen neben dem markierten Objekt: für Bilder und Diagramme eigene, sonst die der Formen und WordArt."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        from lunivo_writer.editor.objekte import frei_objekt as FO
        if FO.art_gewaehlt(self) == "diagramm":
            return self.KNOEPFE_DIAGRAMM
        if self._frei_knoten_rect() is not None:
            return self.KNOEPFE_SMARTART
        if FO.art_gewaehlt(self) == "smartart":
            return self.KNOEPFE_SMARTART_LEER
        return self.KNOEPFE_BILD if BW.frei_bild(self) is not None else self.KNOEPFE

    def _frei_anker_rect(self, r: QRectF) -> QRectF:
        """Das Absatz-Symbol links vom Rahmen; beim Textfeld neben dem Drehgriff (wie in der Vorlage)."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        if FO.art_gewaehlt(self) == "textfeld":
            return QRectF(r.center().x() + 16, r.top() - ROT_ABSTAND - 10, 30, 20)
        return QRectF(r.left() - 46, r.center().y() - 10, 30, 20)

    def _frei_leisten_rects(self, r: QRectF, x: float, leiste: tuple[str, ...]) -> tuple[dict[str, QRectF], QRectF | None]:
        """Die Knöpfe der Leiste: rechts neben dem Bild, am SmartArt-Knoten senkrecht daneben (wie in der Vorlage); dazu der Knoten."""
        kn = self._frei_knoten_rect(r) if leiste is self.KNOEPFE_SMARTART else None
        out = {}
        for i, k in enumerate(leiste):
            out[k] = QRectF(kn.right() + 10, kn.top() + i * 40, self.KNOPF, self.KNOPF) if kn is not None else QRectF(x, r.top() + 32 + i * 40, self.KNOPF, self.KNOPF)
        return out, kn

    def _frei_knopf_rects(self, r: QRectF) -> dict[str, QRectF]:
        """Die Schaltflächen rechts neben dem Bild: oben der Minus-Knopf (klappt sie ein), darunter Layoutoptionen, Formstile, Füllung, Kontur."""
        x = r.right() + 12
        leiste = self._frei_leiste()
        zuschneiden = leiste is self.KNOEPFE_BILD and bool(self.__dict__.get("_frei_zuschnitt"))
        out = {} if zuschneiden else {"minus": QRectF(x + 5, r.top(), 20, 20)}              # beim Zuschneiden bleibt nur dessen Knopf (wie in der Vorlage)
        if getattr(self, "_frei_anker_zeigen", True):
            out["anker"] = self._frei_anker_rect(r)
        if zuschneiden:
            out["zuschnitt"] = QRectF(x, r.top(), self.KNOPF, self.KNOPF)
        elif getattr(self, "_frei_knoepfe_offen", True):
            rects, kn = self._frei_leisten_rects(r, x, leiste)
            out.update(rects)
            if SZ.ohne_minus(leiste, kn):
                out.pop("minus", None)                              # am gewählten Knoten steht kein ⊖ (wie in der Vorlage)
        return out

    # ---- Schaltflächen neben dem Objekt: Zeichnen ------------------------------------------------------------------------
    @staticmethod
    def _frei_anker_zeichnen(p: QPainter, k: QRectF) -> None:
        """Seite mit Pfeil nach unten (Menü)."""
        p.drawRoundedRect(k, 3, 3); p.setPen(QPen(QColor(Farbe.BLAU), 1.3)); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(k.left() + 5, k.top() + 4, 10, 12)); p.drawLine(QPointF(k.left() + 7, k.top() + 8), QPointF(k.left() + 13, k.top() + 8))
        p.drawLine(QPointF(k.left() + 7, k.top() + 11), QPointF(k.left() + 13, k.top() + 11))
        p.setPen(QPen(QColor(Farbe.TINTE), 1.3)); c = k.center().x() + 8
        p.drawLine(QPointF(c - 3, k.center().y() - 1), QPointF(c, k.center().y() + 2)); p.drawLine(QPointF(c, k.center().y() + 2), QPointF(c + 3, k.center().y() - 1))

    @staticmethod
    def _frei_minus_zeichnen(p: QPainter, k: QRectF, offen: bool) -> None:
        p.drawEllipse(k); p.setPen(QPen(QColor(Farbe.TINTE), 1.6))
        p.drawLine(int(k.left() + 5), int(k.center().y()), int(k.right() - 5), int(k.center().y()))
        if not offen:
            p.drawLine(int(k.center().x()), int(k.top() + 5), int(k.center().x()), int(k.bottom() - 5))

    def _frei_knopf_zeichnen(self, p: QPainter, name: str, k: QRectF, offen: bool) -> None:
        """Eine Schaltfläche: weißer Grund, grau, wenn der Befehl nicht möglich ist, darauf das Sinnbild."""
        from lunivo_writer.oberflaeche.baukasten.medien.umbruch_symbole import umbruch_zeichner
        p.setOpacity(1.0 if SZ.knopf_aktiv(getattr(self.window(), "befehle", None), name) else 0.4)
        p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1)); p.setBrush(QColor(Farbe.WEISS))
        if name == "anker":
            return self._frei_anker_zeichnen(p, k)
        if name == "minus":
            return self._frei_minus_zeichnen(p, k, offen)
        p.drawRoundedRect(k, 4, 4)
        inner = k.adjusted(5, 5, -5, -5)
        if name == "layout":
            umbruch_zeichner("quadrat")(p, k.adjusted(4, 4, -4, -4))
        elif name in self.KNOPF_SYMBOLE:                      # Lupe, Zuschneiden, Diagrammknöpfe: ein dunkles Symbol
            p.drawPixmap(inner.toRect(), self._frei_dunkel(self.KNOPF_SYMBOLE[name]))
        elif name == "formstile":
            p.drawPixmap(inner.toRect(), self._frei_dunkel("pinsel"))
        elif name == "fuell":
            p.drawPixmap(inner.adjusted(0, -2, 0, -3).toRect(), self._frei_dunkel("farbe"))
            p.fillRect(QRectF(inner.left(), inner.bottom() - 2, inner.width(), 3), QColor(SINNBILD_GELB))
        else:                                                  # Kontur: ein Rahmen
            p.setPen(QPen(QColor(SINNBILD_KONTUR), 2)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(inner.adjusted(1, 1, -1, -1), 2, 2)

    @staticmethod
    def _frei_dunkel(name: str):
        """Das Symbol dunkel gefärbt: die Knöpfe am Bild sind immer weiß, auch im dunklen Design (dort wären die Symbole sonst hell auf weiß)."""
        from lunivo_writer.oberflaeche.bauteile import symbole
        pm = symbole.icon(name, ICON_FREIBILD_BEDIENUNG).pixmap(ICON_FREIBILD_BEDIENUNG, ICON_FREIBILD_BEDIENUNG)
        p = QPainter(pm); p.setCompositionMode(QPainter.CompositionMode_SourceIn); p.fillRect(pm.rect(), QColor(Farbe.TINTE)); p.end()
        return pm

    # ---- Auswahlrahmen und Griffe ----------------------------------------------------------------------------------------
    def _frei_zuschnitt_griffe(self, p: QPainter, r: QRectF) -> None:
        """Zuschneiden: schwarze Eckwinkel und Kantenstriche statt der runden Griffe."""
        p.setPen(QPen(QColor(Farbe.SCHWARZ), 3, Qt.SolidLine, Qt.FlatCap, Qt.MiterJoin)); p.setBrush(Qt.NoBrush)
        lg = 16.0
        for name in GRIFFE:
            c = self._frei_griff_mitte(r, name)
            sx = -1 if GRIFFE[name][0] == 1 else 1
            sy = -1 if GRIFFE[name][1] == 1 else 1
            if len(name) == 2:                                   # Ecke: ein Winkel
                p.drawPolyline([QPointF(c.x() + sx * lg, c.y()), c, QPointF(c.x(), c.y() + sy * lg)])
            elif name in ("n", "s"):
                p.drawLine(QPointF(c.x() - lg / 2, c.y()), QPointF(c.x() + lg / 2, c.y()))
            else:
                p.drawLine(QPointF(c.x(), c.y() - lg / 2), QPointF(c.x(), c.y() + lg / 2))

    def _frei_drehgriff_zeichnen(self, p: QPainter, r: QRectF, a: dict | None) -> None:
        """Der Drehgriff über der Mitte der Oberkante (nicht beim Zeichenbereich, wie in der Vorlage)."""
        if a is not None and a.get("art") == "zeichenbereich":
            return
        rc = self._frei_griff_mitte(r, "rot")
        p.setPen(QPen(QColor(Farbe.AUSWAHL), 1)); p.drawLine(QPointF(rc.x(), r.top()), QPointF(rc.x(), rc.y() + GRIFF / 2))
        p.setBrush(QColor(Farbe.WEISS)); p.drawEllipse(rc, GRIFF / 2 + 1, GRIFF / 2 + 1)
        p.setPen(QPen(QColor(Farbe.AUSWAHL), 1.4)); p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(rc.x() - 2.5, rc.y() - 2.5, 5, 5), 40 * 16, 280 * 16)

    def _frei_rund_griffe(self, p: QPainter, r: QRectF, a: dict | None) -> None:
        """Runde Griffe wie in der Vorlage (weiße Kreise, grauer Rand), Drehgriff und die gelbe Raute der Anpassungsgriffe."""
        p.setPen(QPen(QColor(Farbe.GRIFF_RAND), 1.2)); p.setBrush(QColor(Farbe.WEISS))
        for name in GRIFFE:
            p.drawEllipse(self._frei_griff_mitte(r, name), GRIFF / 2, GRIFF / 2)
        self._frei_drehgriff_zeichnen(p, r, a)
        for c in self._frei_adj_lagen(r, a).values():             # Anpassungsgriff der Form: eine gelbe Raute
            raute = QPolygonF([QPointF(c.x(), c.y() - 6), QPointF(c.x() + 6, c.y()), QPointF(c.x(), c.y() + 6), QPointF(c.x() - 6, c.y())])
            p.setPen(QPen(QColor(Farbe.GRIFF_RAND), 1)); p.setBrush(QColor(SINNBILD_GELB_HELL)); p.drawPolygon(raute)

    def _frei_auswahl_zeichnen(self, p: QPainter, r: QRectF, a: dict | None = None) -> None:
        if a is None:
            a = self._frei_angabe()
        offen = getattr(self, "_frei_knoepfe_offen", True)
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        for name, k in self._frei_knopf_rects(r).items():
            self._frei_knopf_zeichnen(p, name, k, offen)
        p.restore()
        p.save()
        p.setPen(QPen(QColor(Farbe.AUSWAHL), 1.5, Qt.DashLine)); p.setBrush(Qt.NoBrush)
        p.drawRect(r)
        p.setRenderHint(QPainter.Antialiasing)
        if self.__dict__.get("_fp_key") is not None and self.__dict__["_fp_key"] == self._frei_sel and a is not None:      # Punkte bearbeiten
            from lunivo_writer.oberflaeche.dokument.bearbeitung import freiform_bedienung as FP
            FP.zeichnen(self, p, r, a)
            p.restore()
            return
        if self.__dict__.get("_frei_zuschnitt"):
            self._frei_zuschnitt_griffe(p, r)
            p.restore()
            return
        self._frei_rund_griffe(p, r, a)
        p.restore()
        if a is not None:
            self._frei_teile_zeichnen(p, r, a)

    # ---- Teile des Diagramms, Knoten des SmartArt ------------------------------------------------------------------------
    _ACHSEN = {"achse_horizontal": "h", "achse_vertikal": "v", "zeichnungsbereich": "kein"}      # Teil → Achse, an der Griffe sitzen (Enden bzw. keine)

    def _frei_diagramm_teil_rects(self, r: QRectF, a: dict) -> tuple[list[QRectF], str | None]:
        """Rechtecke (Editor-Koordinaten) des gewählten Diagrammteils und die Achse, an der Griffe an den Enden sitzen (``h``, ``v``, ``kein`` oder None)."""
        from lunivo_writer.editor.diagramme import diagramm as D
        from lunivo_writer.editor.diagramme import diagramm_teile as T
        d = a.get("daten") or {}
        teil = d.get("teil")
        if not teil or teil == "diagrammbereich" or teil not in {k for k, _n in D.teile(d)}:
            return [], None
        geo = T._geo(self, d, float(a["b"]), float(a["h"]))
        rs = geo.get("balken_" + teil[6:]) if teil.startswith("reihe_") else None
        rs = rs or ([geo[teil]] if isinstance(geo.get(teil), QRectF) else [])
        return [self._frei_abbilden(r, a, x) for x in rs], self._ACHSEN.get(teil)

    @staticmethod
    def _frei_teil_punkte(x: QRectF, achse: str | None) -> list[QPointF]:
        """Die Griffpunkte um ein Teilrechteck: an den Enden einer Achse, sonst alle acht."""
        if achse == "kein":
            return []
        if achse == "h":
            return [QPointF(x.left(), x.center().y()), QPointF(x.right(), x.center().y())]
        if achse == "v":
            return [QPointF(x.center().x(), x.top()), QPointF(x.center().x(), x.bottom())]
        return [QPointF(x.left() + x.width() * fx, x.top() + x.height() * fy) for fx, fy in GRIFFE.values()]

    def _frei_teil_rects(self, r: QRectF, a: dict) -> tuple[list[QRectF], str | None]:
        """Rechtecke des gewählten Diagrammteils bzw. SmartArt-Knotens (Editor-Koordinaten) und die Achsenart."""
        if a.get("art") == "diagramm":
            return self._frei_diagramm_teil_rects(r, a)
        if a.get("art") == "smartart":
            kn = self._frei_knoten_rect(r)
            return ([kn] if kn is not None else []), None
        return [], None

    def _frei_teile_zeichnen(self, p: QPainter, r: QRectF, a: dict) -> None:
        """Rahmen mit kleinen runden Griffen um den gewählten Diagrammteil bzw. SmartArt-Knoten (dünner als der Rahmen des Objekts)."""
        if self.__dict__.get("_frei_zuschnitt"):
            return
        rects, achse = self._frei_teil_rects(r, a)
        if not rects:
            return
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        dreh = float(a.get("dreh", 0.0) or 0.0)
        if dreh:
            p.translate(r.center()); p.rotate(dreh); p.translate(-r.center())
        p.setPen(QPen(QColor(Farbe.AUSWAHL), 1, Qt.DotLine if a.get("art") == "smartart" else Qt.SolidLine)); p.setBrush(Qt.NoBrush)
        for x in rects:
            p.drawRect(x)
        p.setPen(QPen(QColor(Farbe.GRIFF_RAND), 1)); p.setBrush(QColor(Farbe.WEISS))
        klein = GRIFF * 0.75 / 2
        for x in rects:
            for c in self._frei_teil_punkte(x, achse):
                p.drawEllipse(c, klein, klein)
        p.restore()
