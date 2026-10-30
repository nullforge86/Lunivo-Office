"""Frei positionierte Bilder im Editor: zeichnen, anklicken, verschieben, in der Größe ändern, löschen (siehe editor/freie_bilder.py).

Ein Klick auf ein Bild vor dem Text wählt es aus (Strg+Alt+Klick: auch eines hinter dem Text, zum Beispiel das Band im Briefkopf);
Ziehen verschiebt, die Griffe an den Ecken und Kanten ändern die Größe (an den Ecken bleibt das Seitenverhältnis, mit Umschalt frei),
Entf löscht, Esc hebt die Auswahl auf. Bilder in der Kopf-/Fußzeile gehören zum Blatt, Bilder im Text zu einem Absatz.
"""
from __future__ import annotations

import json

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF, QTextCursor, QTransform

from lunivo_writer.editor import freie_bilder as FB
from lunivo_writer.editor.zusatz import B_BILDANKER

from lunivo_writer.core.farben import Farbe
GRIFF = 9.0                                                  # Seitenlänge eines Griffs in Bildschirmpunkten
GRIFFE = {"nw": (0, 0), "n": (0.5, 0), "ne": (1, 0), "e": (1, 0.5), "se": (1, 1), "s": (0.5, 1), "sw": (0, 1), "w": (0, 0.5)}
ROT_ABSTAND = 24.0                                           # Drehgriff: so weit über der Oberkante des Rahmens
CURSOR = {"rot": Qt.PointingHandCursor, "adj": Qt.PointingHandCursor, "nw": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor, "ne": Qt.SizeBDiagCursor, "sw": Qt.SizeBDiagCursor,
          "n": Qt.SizeVerCursor, "s": Qt.SizeVerCursor, "e": Qt.SizeHorCursor, "w": Qt.SizeHorCursor}


class FreieBilderMixin:
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

    # ---- Zeichnen ------------------------------------------------------------------------------------------------------
    @staticmethod
    def _frei_schluessel(a: dict) -> tuple:
        return ("t", a["_blk"], a["_idx"]) if "_blk" in a else ("k", id(a))

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
        if getattr(self, "_frei_schl", None) != schl[:4]:
            roh = FB.koerper_index(doc, g["ch"], g["n"])
            self._frei_idx = {k: [(a, y / z, sp) for a, y, sp in v] for k, v in roh.items()}
            self._frei_schl = schl[:4]
        if getattr(self, "_frei_liste_schl", None) == schl:
            return self._frei_liste_wert
        liste = []
        for k in range(self._blatt_anzahl()):
            oben = self.blatt_oben(k)
            for a, bild, r in FB.objekte_der_seite(self.page, doc, k + 1, self._frei_idx):
                key = self._frei_schluessel(a)
                if key in self._frei_vorlaeufig:                      # wird gerade gezogen
                    a = self._frei_vorlaeufig[key]
                    r = QRectF(*self._frei_rechteck(a, k + 1))
                    if a.get("_vorschau") is not None:                # Live-Vorschau (Anpassungsgriff, Punkte): das Bild wird laufend neu gezeichnet
                        bild = a["_vorschau"]
                liste.append((key, a, bild, QRectF(r.x() * z, oben + r.y() * z, r.width() * z, r.height() * z), bool(a.get("hinter")), k + 1))
        self._frei_liste_schl, self._frei_liste_wert = schl, liste
        self._frei_treffer = [(key, a, r, hinten, n) for key, a, bild, r, hinten, n in liste]
        return liste

    def _frei_zeichnen(self, p: QPainter, sicht: QRectF, hinter: bool) -> None:
        """Bilder der sichtbaren Blätter, hinter (``hinter``) oder vor dem Text; die vorderen zeichnen auch die Auswahl."""
        z = self.zoom
        if self.__dict__.get("_sa_edit") is not None:                  # das Eingabefeld im SmartArt-Knoten folgt dem Blatt
            kn = self._frei_knoten_rect()
            if kn is not None:
                self._sa_edit[0].setGeometry(kn.toRect())
        if getattr(self, "_frei_edit", None) is not None:
            from lunivo_writer.editor import frei_objekt as FO
            FO.edit_platzieren(self)
        for key, a, bild, r, hinten, n in self._frei_liste():
            if hinten != hinter or not r.intersects(sicht):
                continue
            if getattr(self, "_frei_edit", None) is not None and key == self._frei_edit_key:      # wird gerade im Objekt geschrieben: das Eingabefeld zeigt den Text
                from PySide6.QtGui import QImage
                bild = QImage(1, 1, QImage.Format_ARGB32); bild.fill(0)
            p.save(); p.translate(r.x(), r.y()); p.scale(z, z)
            FB.bild_zeichnen(p, bild, QRectF(0, 0, r.width() / z, r.height() / z), bool(a.get("ellipse")), a.get("rand"), float(a.get("dreh", 0.0)), a.get("fuell"), a.get("_fuellbild") or (a.get("fuell") or {}).get("bild"), a.get("fx"))
            p.restore()
        if not hinter and self._frei_sel is not None:
            for key, a, bild, r, hinten, n in self._frei_liste():
                if key == self._frei_sel and r.intersects(sicht):
                    self._frei_text_markieren(p, r, a, bild)
                    self._frei_auswahl_zeichnen(p, r, a)

    @staticmethod
    def _frei_text_markieren(p: QPainter, r: QRectF, a: dict, bild) -> None:
        """WordArt wie in WPS: der Text im gewählten Objekt ist grau hinterlegt (nur der Text, kein Kasten über dem Objekt)."""
        from lunivo_writer.editor import frei_objekt as FO
        t = FO.text_bereich(a, bild)
        if t is not None:
            p.save(); p.setPen(Qt.NoPen); p.setBrush(QColor(110, 110, 110, 95))
            p.drawRect(QRectF(r.x() + t.x() * r.width(), r.y() + t.y() * r.height(), t.width() * r.width(), t.height() * r.height()))
            p.restore()

    def _frei_rechteck(self, a: dict, n: int):
        from lunivo_writer.models.page import mm_to_px
        pg = self.page
        r = FB.rechteck(a, mm_to_px(pg.width_mm), mm_to_px(pg.height_mm), mm_to_px(pg.margin_left_mm), mm_to_px(pg.margin_top_mm),
                        pg.content_width_px, pg.content_height_px, a.get("_ay", 0.0), a.get("_sx"), n)
        return r.x(), r.y(), r.width(), r.height()

    KNOPF = 30.0                                              # Kantenlänge einer Schaltfläche neben dem Bild
    KNOPF_TIPPS = {"layout": "Layoutoptionen", "formstile": "Formeffekte", "fuell": "Formfüllung", "minus": "Schnellleiste einklappen",
                   "anker": "Absatz-Layout", "lupe": "Vergrößern", "zuschnitt": "Zuschneiden",
                   "dg_element": "Diagrammelemente", "dg_stile": "Diagrammstile", "zahnrad": "Formatierung", "dg_filter": "Diagrammfilter",
                   "sa_form": "Form einfügen", "sa_layout": "Layout", "sa_level": "Level", "sa_bullet": "Aufzählungszeichen einfügen",
                   "sa_stil": "Formvorlagen",
                   "kontur": "Formkontur\n\nFarbe, Breite und Linienart für die Konturlinie der ausgewählten Form auswählen.\n\n"
                             "Auf den Pfeil klicken, um detaillierte Einstellungen für die Konturlinie auszuwählen."}
    KNOEPFE = ("layout", "formstile", "fuell", "kontur", "zahnrad")   # von oben nach unten, wie in der Vorlage; das Zahnrad öffnet die Seitenleiste „Formatierung“
    KNOEPFE_BILD = ("layout", "lupe", "zuschnitt", "zahnrad")    # Bild: Layoutoptionen, Vergrößern, Zuschneiden, Formatierung
    KNOEPFE_DIAGRAMM = ("layout", "dg_element", "dg_stile", "dg_filter", "zahnrad")   # Diagramm: Layoutoptionen, Elemente, Stile, Filter, Formatierung
    KNOEPFE_SMARTART = ("sa_form", "sa_layout", "sa_level", "sa_bullet", "sa_stil", "zahnrad")    # am gewählten SmartArt-Knoten
    KNOPF_SYMBOLE = {"lupe": "lupe", "zuschnitt": "crop", "dg_element": "diagrammteil", "dg_stile": "pinsel", "zahnrad": "zahnrad", "dg_filter": "funnel",
                     "sa_form": "network", "sa_layout": "layout-dashboard", "sa_level": "workflow", "sa_bullet": "list-plus", "sa_stil": "pinsel"}

    def _frei_leiste(self) -> tuple[str, ...]:
        """Die Schaltflächen neben dem markierten Objekt: für Bilder und Diagramme eigene, sonst die der Formen und WordArt."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        from lunivo_writer.editor import frei_objekt as FO
        if FO.art_gewaehlt(self) == "diagramm":
            return self.KNOEPFE_DIAGRAMM
        if self._frei_knoten_rect() is not None:
            return self.KNOEPFE_SMARTART
        return self.KNOEPFE_BILD if BW.frei_bild(self) is not None else self.KNOEPFE

    def _frei_knopf_rects(self, r: QRectF) -> dict[str, QRectF]:
        """Die Schaltflächen rechts neben dem Bild: oben der Minus-Knopf (klappt sie ein), darunter Layoutoptionen, Formstile, Füllung, Kontur."""
        x = r.right() + 12
        leiste = self._frei_leiste()
        zuschneiden = leiste is self.KNOEPFE_BILD and bool(self.__dict__.get("_frei_zuschnitt"))
        out = {} if zuschneiden else {"minus": QRectF(x + 5, r.top(), 20, 20)}              # beim Zuschneiden bleibt nur dessen Knopf (wie in der Vorlage)
        if getattr(self, "_frei_anker_zeigen", True):              # das Absatz-Symbol links vom Rahmen
            from lunivo_writer.editor import frei_objekt as FO
            if FO.art_gewaehlt(self) == "textfeld":                  # beim Textfeld neben dem Drehgriff (wie in der Vorlage)
                out["anker"] = QRectF(r.center().x() + 16, r.top() - ROT_ABSTAND - 10, 30, 20)
            else:
                out["anker"] = QRectF(r.left() - 46, r.center().y() - 10, 30, 20)
        if zuschneiden:
            out["zuschnitt"] = QRectF(x, r.top(), self.KNOPF, self.KNOPF)
        elif getattr(self, "_frei_knoepfe_offen", True):
            kn = self._frei_knoten_rect(r) if leiste is self.KNOEPFE_SMARTART else None
            for i, k in enumerate(leiste):
                if kn is not None:                                  # die Leiste am Knoten steht rechts daneben, senkrecht (wie in der Vorlage)
                    out[k] = QRectF(kn.right() + 10, kn.top() + i * 40, self.KNOPF, self.KNOPF)
                else:
                    out[k] = QRectF(x, r.top() + 32 + i * 40, self.KNOPF, self.KNOPF)
        return out

    def _frei_auswahl_zeichnen(self, p: QPainter, r: QRectF, a: dict | None = None) -> None:
        from lunivo_writer.ui.baukasten.umbruch_symbole import umbruch_zeichner
        if a is None:
            a = self._frei_angabe()
        from lunivo_writer.ui.widgets import icons
        offen = getattr(self, "_frei_knoepfe_offen", True)
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        for name, k in self._frei_knopf_rects(r).items():
            p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1)); p.setBrush(QColor(Farbe.WEISS))
            if name == "anker":                                    # Seite mit Pfeil nach unten (Menü)
                p.drawRoundedRect(k, 3, 3); p.setPen(QPen(QColor(Farbe.BLAU), 1.3)); p.setBrush(Qt.NoBrush)
                p.drawRect(QRectF(k.left() + 5, k.top() + 4, 10, 12)); p.drawLine(QPointF(k.left() + 7, k.top() + 8), QPointF(k.left() + 13, k.top() + 8))
                p.drawLine(QPointF(k.left() + 7, k.top() + 11), QPointF(k.left() + 13, k.top() + 11))
                p.setPen(QPen(QColor("#495057"), 1.3)); c = k.center().x() + 8
                p.drawLine(QPointF(c - 3, k.center().y() - 1), QPointF(c, k.center().y() + 2)); p.drawLine(QPointF(c, k.center().y() + 2), QPointF(c + 3, k.center().y() - 1))
                continue
            if name == "minus":
                p.drawEllipse(k); p.setPen(QPen(QColor("#495057"), 1.6))
                p.drawLine(int(k.left() + 5), int(k.center().y()), int(k.right() - 5), int(k.center().y()))
                if not offen:
                    p.drawLine(int(k.center().x()), int(k.top() + 5), int(k.center().x()), int(k.bottom() - 5))
                continue
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
                p.fillRect(QRectF(inner.left(), inner.bottom() - 2, inner.width(), 3), QColor("#f2c200"))
            else:                                                  # Kontur: ein Rahmen
                p.setPen(QPen(QColor("#1c3faa"), 2)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(inner.adjusted(1, 1, -1, -1), 2, 2)
        p.restore()
        p.save()
        pen = QPen(QColor(Farbe.AUSWAHL), 1.5, Qt.DashLine)
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        p.drawRect(r)
        p.setRenderHint(QPainter.Antialiasing)
        if self.__dict__.get("_fp_key") is not None and self.__dict__["_fp_key"] == self._frei_sel and a is not None:      # Punkte bearbeiten
            from lunivo_writer.ui.document import freiform_bedienung as FP
            FP.zeichnen(self, p, r, a)
            p.restore()
            return
        if self.__dict__.get("_frei_zuschnitt"):                   # Zuschneiden: schwarze Eckwinkel und Kantenstriche statt der runden Griffe
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
            p.restore()
            return
        p.setPen(QPen(QColor(Farbe.GRIFF_RAND), 1.2)); p.setBrush(QColor(Farbe.WEISS))          # runde Griffe wie in WPS: weiße Kreise, grauer Rand
        for name in GRIFFE:
            c = self._frei_griff_mitte(r, name)
            p.drawEllipse(c, GRIFF / 2, GRIFF / 2)
        rc = self._frei_griff_mitte(r, "rot")                     # der Drehgriff über der Mitte der Oberkante
        p.setPen(QPen(QColor(Farbe.AUSWAHL), 1)); p.drawLine(QPointF(rc.x(), r.top()), QPointF(rc.x(), rc.y() + GRIFF / 2))
        p.setBrush(QColor(Farbe.WEISS)); p.drawEllipse(rc, GRIFF / 2 + 1, GRIFF / 2 + 1)
        p.setPen(QPen(QColor(Farbe.AUSWAHL), 1.4)); p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(rc.x() - 2.5, rc.y() - 2.5, 5, 5), 40 * 16, 280 * 16)
        for c in self._frei_adj_lagen(r, a).values():             # Anpassungsgriff der Form: eine gelbe Raute
            raute = QPolygonF([QPointF(c.x(), c.y() - 6), QPointF(c.x() + 6, c.y()), QPointF(c.x(), c.y() + 6), QPointF(c.x() - 6, c.y())])
            p.setPen(QPen(QColor(Farbe.GRIFF_RAND), 1)); p.setBrush(QColor("#ffe45c")); p.drawPolygon(raute)
        p.restore()
        if a is not None:
            self._frei_teile_zeichnen(p, r, a)


    # ---- Teile des Diagramms, Knoten des SmartArt, Anpassungsgriff ---------------------------------------------------------------------
    def _frei_angabe(self) -> dict | None:
        """Die Angabe des gewählten freien Objekts (oder None)."""
        return next((x[1] for x in getattr(self, "_frei_treffer", []) if x[0] == self._frei_sel), None)

    @staticmethod
    def _frei_abbilden(r: QRectF, a: dict, rr: QRectF) -> QRectF:
        """Ein Rechteck in logischen Bildpunkten des Objekts (Breite ``b`` × Höhe ``h``) in Editor-Koordinaten (Zoom, Lage) umrechnen."""
        sx, sy = r.width() / max(1.0, float(a["b"])), r.height() / max(1.0, float(a["h"]))
        return QRectF(r.x() + rr.x() * sx, r.y() + rr.y() * sy, rr.width() * sx, rr.height() * sy)

    def _frei_sa_geo(self, a: dict) -> dict:
        """Rechtecke der SmartArt-Knoten (logisch), zwischengemerkt, bis sich Knoten oder Größe ändern."""
        from lunivo_writer.editor import smartart as SA
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

    def _frei_teile_zeichnen(self, p: QPainter, r: QRectF, a: dict) -> None:
        """Rahmen mit kleinen runden Griffen um den gewählten Diagrammteil bzw. SmartArt-Knoten (dünner als der Rahmen des Objekts)."""
        if self.__dict__.get("_frei_zuschnitt"):
            return
        rects, achse = [], None
        if a.get("art") == "diagramm":
            from lunivo_writer.editor import diagramm as D
            from lunivo_writer.editor import diagramm_teile as T
            d = a.get("daten") or {}
            teil = d.get("teil")
            if not teil or teil == "diagrammbereich" or teil not in {k for k, _n in D.teile(d)}:
                return
            geo = T._geo(self, d, float(a["b"]), float(a["h"]))
            rs = geo.get("balken_" + teil[6:]) if teil.startswith("reihe_") else None
            rs = rs or ([geo[teil]] if isinstance(geo.get(teil), QRectF) else [])
            rects = [self._frei_abbilden(r, a, x) for x in rs]
            achse = "h" if teil == "achse_horizontal" else "v" if teil == "achse_vertikal" else "kein" if teil == "zeichnungsbereich" else None
        elif a.get("art") == "smartart":
            kn = self._frei_knoten_rect(r)
            rects = [kn] if kn is not None else []
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
            if achse == "kein":
                continue
            if achse in ("h", "v"):                                       # Achse: Griffe an den Enden
                pts = [QPointF(x.left(), x.center().y()), QPointF(x.right(), x.center().y())] if achse == "h" else \
                      [QPointF(x.center().x(), x.top()), QPointF(x.center().x(), x.bottom())]
            else:
                pts = [QPointF(x.left() + x.width() * fx, x.top() + x.height() * fy) for fx, fy in GRIFFE.values()]
            for c in pts:
                p.drawEllipse(c, klein, klein)
        p.restore()

    def _frei_adj_lagen(self, r: QRectF, a: dict | None) -> dict[str, QPointF]:
        """Lage der Anpassungsgriffe (gelbe Raute) der gewählten Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten."""
        if a is None or a.get("art") != "form":
            return {}
        from lunivo_writer.editor import formen as F
        d = a.get("daten") or {}
        form = d.get("form", "Rechteck")
        adj = d.get("adj")
        vorl = self.__dict__.get("_frei_adj_wert")
        if vorl is not None and self._frei_zug is not None and self._frei_zug[0] == "anpassen":
            adj = F.anpassen(form, vorl[1], adj, vorl[0])
        out = {}
        for i in range(len(F.anpass_griffe(form, QRectF(0, 0, 1, 1)))):
            c = F.anpass_griff(form, QRectF(r), adj, i)
            if c is None:
                continue
            dreh = float(a.get("dreh", 0.0) or 0.0)
            if dreh:
                c = QTransform().translate(r.center().x(), r.center().y()).rotate(dreh).translate(-r.center().x(), -r.center().y()).map(c)
            out[f"adj{i}"] = c
        return out

    @staticmethod
    def _frei_dunkel(name: str):
        """Das Symbol dunkel gefärbt: die Knöpfe am Bild sind immer weiß, auch im dunklen Design (dort wären die Symbole sonst hell auf weiß)."""
        from PySide6.QtGui import QPixmap
        from lunivo_writer.ui.widgets import icons
        pm = icons.icon(name, 20).pixmap(20, 20)
        p = QPainter(pm); p.setCompositionMode(QPainter.CompositionMode_SourceIn); p.fillRect(pm.rect(), QColor(Farbe.TINTE)); p.end()
        return pm

    @staticmethod
    def _frei_griff_mitte(r: QRectF, name: str) -> QPointF:
        if name == "rot":
            return QPointF(r.center().x(), r.top() - ROT_ABSTAND)
        fx, fy = GRIFFE[name]
        return QPointF(r.left() + r.width() * fx, r.top() + r.height() * fy)

    # ---- Treffer -------------------------------------------------------------------------------------------------------
    def _frei_griff_bei(self, pos: QPointF):
        if self._frei_sel is None:
            return None, None
        for key, a, r, hinten, n in self._frei_treffer:
            if key == self._frei_sel:
                for name, c in self._frei_adj_lagen(r, a).items():
                    if abs(pos.x() - c.x()) <= GRIFF and abs(pos.y() - c.y()) <= GRIFF:
                        return name, (key, a, r, hinten, n)
                for name in (*GRIFFE, "rot"):
                    c = self._frei_griff_mitte(r, name)
                    if abs(pos.x() - c.x()) <= GRIFF and abs(pos.y() - c.y()) <= GRIFF:
                        return name, (key, a, r, hinten, n)
                return None, (key, a, r, hinten, n) if r.contains(pos) else None
        return None, None

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

    # ---- Maus ----------------------------------------------------------------------------------------------------------
    def _frei_maus(self, e, art: str) -> bool:
        """True, wenn das Ereignis ein Bild betrifft und der Editor es nicht weiter behandeln soll."""
        if not hasattr(self, "_frei_treffer"):
            self._frei_init()
        self._frei_liste()
        if not self._frei_treffer or self.isReadOnly():
            if art == "press" and self._frei_sel is not None:
                self._frei_sel = None; self.viewport().update()
            return False
        pos = e.position()
        if self.__dict__.get("_fp_key") is not None:                              # Punkte einer Form bearbeiten
            from lunivo_writer.ui.document import freiform_bedienung as FP
            if FP.maus(self, e, art):
                return True
        if art == "press" and e.button() == Qt.LeftButton and self._frei_sel is not None:
            for key, a, r, hinten, n in self._frei_treffer:
                if key == self._frei_sel:
                    for name, k in self._frei_knopf_rects(r).items():                            # die Schaltflächen neben dem Bild
                        if k.contains(pos):
                            self._frei_knopf(name, e.globalPosition().toPoint())
                            return True
        if art == "press" and e.button() == Qt.LeftButton:
            griff, treffer = self._frei_griff_bei(pos)
            if treffer is None or (griff is None and not treffer[2].contains(pos)):
                # Bilder hinter dem Text: mit Strg+Alt, oder wenn an der Stelle kein Text liegt (zum Beispiel das Band im Briefkopf)
                treffer = self._frei_bild_bei(pos, bool(e.modifiers() & Qt.ControlModifier and e.modifiers() & Qt.AltModifier)
                                              or not self._frei_text_bei(pos))
                griff = None
            if treffer is None:
                if self._frei_sel is not None:
                    self._frei_teilwahl_aufheben()
                    self._frei_sel = None; self.viewport().update()
                return False
            key, a, r, hinten, n = treffer
            vorher = self._frei_sel
            merk = getattr(self, "_frei_format_merk", None)
            if merk is not None and key != self._frei_sel:                    # „Format übertragen“ wartet auf das Zielbild
                self._frei_format_merk = None
                self._frei_sel = key
                from lunivo_writer.editor import bildlayout as BL
                BL.format_uebertragen(self, BL.ziel(self), merk)
                self.viewport().setCursor(Qt.IBeamCursor)
                return True
            if vorher is not None and vorher != key:
                self._frei_teilwahl_aufheben()                                  # ein anderes Objekt: Teil und Knoten des alten sind nicht mehr gewählt
            elif vorher == key and griff is None and a.get("art") in ("diagramm", "smartart"):
                self._frei_teil_klick(pos, a)                                   # Klick in das markierte Diagramm/SmartArt: Teil bzw. Knoten wählen
            self._frei_sel = key
            if hasattr(self.window(), "objektformat_folgen"):
                self.window().objektformat_folgen()
            self._frei_zug = ("drehen" if griff == "rot" else "anpassen" if (griff or "").startswith("adj") else "groesse" if griff else "bewegen",
                              griff, pos, dict(a), QRectF(r), n)
            self.viewport().update()
            return True
        if art == "move":
            if self._frei_zug is not None and e.buttons() & Qt.LeftButton:
                self._frei_ziehen(e)
                return True
            if self._frei_sel is not None:
                for key, a, r, hinten, n in self._frei_treffer:
                    if key == self._frei_sel:
                        for name, k in self._frei_knopf_rects(r).items():
                            if k.contains(pos) and name in self.KNOPF_TIPPS:
                                from PySide6.QtWidgets import QToolTip
                                QToolTip.showText(e.globalPosition().toPoint(), self.KNOPF_TIPPS[name], self.viewport(), k.toRect())
            griff, treffer = self._frei_griff_bei(pos)
            self._frei_teil_tipp(e, pos, griff)
            if griff:
                self.viewport().setCursor(CURSOR[griff]); self._frei_cursor_gesetzt = True
            elif treffer is not None or self._frei_bild_bei(pos, not self._frei_text_bei(pos)) is not None:
                self.viewport().setCursor(Qt.SizeAllCursor); self._frei_cursor_gesetzt = True      # das Bild lässt sich anfassen
            elif self._frei_cursor_gesetzt:
                self.viewport().setCursor(Qt.IBeamCursor); self._frei_cursor_gesetzt = False
            return False
        if art == "release" and self._frei_zug is not None:
            self._frei_ablegen()
            return True
        return False

    def _frei_ziehen(self, e) -> None:
        art, griff, start, a0, r0, n = self._frei_zug
        z = self.zoom
        if art == "anpassen":                                                # gelbe Raute: der Parameter folgt der Maus, gespeichert wird beim Loslassen
            from lunivo_writer.editor import formen as F
            p = QPointF(e.position())
            if float(a0.get("dreh", 0.0) or 0.0):
                p = QTransform().translate(r0.center().x(), r0.center().y()).rotate(-float(a0["dreh"])).translate(-r0.center().x(), -r0.center().y()).map(p)
            i = int(griff[3:])
            wert = F.anpass_wert((a0.get("daten") or {}).get("form", "Rechteck"), QRectF(r0), p, i)
            self.__dict__["_frei_adj_wert"] = (i, wert)
            self._frei_adj_vorschau(a0, i, wert)
            self.viewport().update()
            return
        if art == "drehen":                                                  # Drehgriff: der Winkel zeigt von der Mitte zur Maus
            import math
            m = r0.center()
            w = math.degrees(math.atan2(e.position().x() - m.x(), m.y() - e.position().y())) % 360.0
            if e.modifiers() & Qt.ShiftModifier:
                w = round(w / 15.0) * 15.0 % 360.0
            self._frei_vorlaeufig[self._frei_sel] = {**a0, "dreh": round(w, 1)}
            self.viewport().update()
            return
        dx, dy = (e.position().x() - start.x()) / z, (e.position().y() - start.y()) / z
        r = QRectF(r0.x() / z, 0, r0.width() / z, r0.height() / z)          # Blattkoordinaten: x wie im Editor, y wird unten ergänzt
        oben = self.blatt_oben(n - 1)
        r.moveTop((r0.y() - oben) / z)
        if art == "bewegen":
            r.translate(dx, dy)
        else:
            verhaeltnis = r.width() / max(1.0, r.height())
            sperre = bool(a0.get("sperre")) and not self.__dict__.get("_frei_zuschnitt")       # Seitenverhältnis sperren: auch die Kanten halten es
            frei = bool(e.modifiers() & Qt.ShiftModifier) or (griff in ("n", "s", "e", "w") and not sperre) or bool(self.__dict__.get("_frei_zuschnitt"))
            l, t, rr, b = r.left(), r.top(), r.right(), r.bottom()
            if "w" in griff:
                l = min(l + dx, rr - 8)
            if "e" in griff:
                rr = max(rr + dx, l + 8)
            if "n" in griff:
                t = min(t + dy, b - 8)
            if "s" in griff:
                b = max(b + dy, t + 8)
            if not frei and griff in ("n", "s"):                             # gesperrt, obere/untere Kante: die Höhe bestimmt die Breite
                rr = l + (b - t) * verhaeltnis
            elif not frei:                                                   # Ecke: Seitenverhältnis halten, Breite bestimmt die Höhe
                breite = rr - l
                hoehe = breite / verhaeltnis
                if "n" in griff:
                    t = b - hoehe
                else:
                    b = t + hoehe
            r = QRectF(l, t, rr - l, b - t)
        neu = FB.versatz_fuer(a0, r, self.page, n)
        self._frei_vorlaeufig[self._frei_sel] = neu
        self.viewport().update()

    def _frei_adj_vorschau(self, a0: dict, i: int, wert: float) -> None:
        """Die Form beim Ziehen der gelben Raute laufend neu zeichnen (nur das Bild, kein Dokumentschritt)."""
        from lunivo_writer.editor import formen as F
        from lunivo_writer.editor import frei_objekt as FO
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
                from lunivo_writer.editor import formen as F
                F.anpass_setzen(self, vorl[1], vorl[0])
            self.viewport().update()
            return
        neu = self._frei_vorlaeufig.pop(self._frei_sel, None)
        self._frei_vorlaeufig.clear()
        if neu is None:
            return                                                           # nur angeklickt
        from lunivo_writer.editor import frei_objekt as FO
        if zug[0] == "groesse" and self.__dict__.get("_frei_zuschnitt"):      # Zuschneiden-Modus: Ziehen schneidet ab (editor/bildzuschnitt.py)
            from lunivo_writer.editor import bildzuschnitt as BZ
            neu = BZ.aus_ziehen(zug[3], neu, zug[1])
        neu = FO.nach_groesse(self, neu)                                      # Textfeld: Text in der neuen Größe setzen
        if self._frei_sel[0] == "k":
            for a in self.page.bilder:
                if id(a) == self._frei_sel[1]:
                    a.update(FB.ohne_hilfsangaben(neu))
            self.document().setModified(True)
            self.pageApplied.emit()
        else:
            self._frei_absatz_aendern(neu["_blk"], neu["_idx"], FB.ohne_hilfsangaben(neu))
            if neu.get("art") == "textfeld":
                FO.kette_aktualisieren(self)                                  # verknüpfte Textfelder: der Text läuft neu von Feld zu Feld
        self.viewport().update()

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

    # ---- Teil eines Diagramms / Knoten eines SmartArt wählen -----------------------------------------------------------------------
    def _frei_teil_klick(self, pos: QPointF, a: dict) -> None:
        """Ein Klick in das markierte Diagramm wählt den Teil darunter, in das markierte SmartArt den Knoten darunter."""
        fenster = self.window()
        if a.get("art") == "diagramm":
            from lunivo_writer.editor import diagramm_teile as T
            teil = T.teil_bei(self, pos)
            if teil != (a.get("daten") or {}).get("teil"):
                T.teil_waehlen(self, teil)
        else:
            from lunivo_writer.editor import smartart as SA
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
            from lunivo_writer.editor import diagramm_teile as T
            T.teil_waehlen(self, None)
        elif a.get("art") == "smartart" and d.get("auswahl"):
            from lunivo_writer.editor import smartart as SA
            SA.knoten_waehlen(self, None)

    def _frei_teil_tipp(self, e, pos: QPointF, griff) -> None:
        """Beim Überfahren des markierten Diagramms steht der Name des Teils unter der Maus im Tooltip."""
        a = self._frei_angabe()
        if a is None or a.get("art") != "diagramm" or griff or e.buttons():
            return
        from lunivo_writer.editor import diagramm as D
        from lunivo_writer.editor import diagramm_teile as T
        teil = T.teil_bei(self, pos)
        if teil is None or teil == self.__dict__.get("_dg_hover"):
            self.__dict__["_dg_hover"] = teil
            return
        self.__dict__["_dg_hover"] = teil
        from PySide6.QtWidgets import QToolTip
        QToolTip.showText(e.globalPosition().toPoint(), dict(D.teile(a.get("daten") or {})).get(teil, ""), self.viewport())

    # ---- Text im SmartArt-Knoten schreiben -------------------------------------------------------------------------------------------
    def frei_knoten_edit_starten(self, text: str | None = None) -> bool:
        """Ein Eingabefeld über dem gewählten SmartArt-Knoten (Doppelklick, Enter oder Tippen). ``text``: bereits getippte Zeichen werden hinter den
        Knotentext geschrieben; sie ersetzen ihn nur, wenn „Tippen ersetzt die Auswahl“ an ist (Standard: aus, Markieren löscht nichts)."""
        kn = self._frei_knoten_rect()
        a = self._frei_angabe()
        if kn is None or a is None:
            return False
        from PySide6.QtWidgets import QLineEdit
        from lunivo_writer.editor import smartart as SA
        self._frei_knoten_edit_ende(True)
        ident = (a.get("daten") or {}).get("auswahl")
        w = QLineEdit(self.viewport())
        bisher = SA.knoten_text(self, ident) or ""
        ersetzt = bool(self.opt("bearbeiten/tippen_ersetzt", False)) if callable(getattr(self, "opt", None)) else False
        w.setText(text if (text is not None and ersetzt) else bisher + (text or ""))
        w.setAlignment(Qt.AlignCenter)
        f = w.font(); f.setPixelSize(max(8, int(kn.height() * 0.3))); w.setFont(f)
        w.setStyleSheet("QLineEdit { background: white; color: #1f1f1f; border: 1px solid #1c7ed6; }")
        w.setGeometry(kn.toRect())
        self.__dict__["_sa_edit"] = (w, ident)

        def fertig() -> None:
            self._frei_knoten_edit_ende(False)
        w.editingFinished.connect(fertig)
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
            from lunivo_writer.editor import smartart as SA
            if text != (SA.knoten_text(self, ident) or ""):
                SA.knoten_text_setzen(self, ident, text)
        self.viewport().update(); self.setFocus()

    # ---- Schaltflächen neben dem Bild -------------------------------------------------------------------------------------------
    def _frei_knopf(self, name: str, pos) -> None:
        if name == "anker":
            self._frei_anker_menue(pos)
        elif name == "minus":
            self._frei_knoepfe_offen = not getattr(self, "_frei_knoepfe_offen", True)
            self.viewport().update()
        elif name == "layout":
            self._frei_layout_popup(pos)
        elif name == "zahnrad":
            self._frei_formatierung()
        elif name in ("lupe", "zuschnitt", "dg_element", "dg_stile", "dg_filter") or name.startswith("sa_"):
            self._frei_befehl_knopf(name, pos)
        elif name == "formstile":
            self._frei_formstile(pos)
        elif name == "fuell":
            self._frei_fuell(pos)
        elif name == "kontur":
            self._frei_kontur(pos)

    def _frei_befehl_knopf(self, name: str, pos) -> None:
        """Bild: Vergrößern (Ansicht mit Zoom) und Zuschneiden; Diagramm: Elemente, Stile, Einstellungen (Datenfenster) — jeweils der Befehl des Bandes."""
        b = getattr(self.window(), "befehle", None)
        if b is None:
            return
        if name == "lupe":
            b.bildVergroessern()
        elif name == "zuschnitt":
            b.bildZuschneidenModus()
        elif name == "sa_bullet":
            b.smartartAufzaehlung(); self.viewport().update()
        else:
            from lunivo_writer.ui.baukasten import diagramm_popups as DP
            from lunivo_writer.ui.baukasten import smartart_menues as SM
            bau = {"dg_element": DP.elemente_popup, "dg_stile": DP.stile_popup, "dg_filter": DP.filter_popup, "sa_form": SM.form_menue,
                   "sa_layout": lambda bb: SM.hierarchie_menue(bb, True), "sa_level": SM.level_menue, "sa_stil": SM.stile_menue}[name]
            m = bau(b)
            m.popup(pos); self._frei_menue = m

    def _frei_anker_menue(self, pos) -> None:
        """Menü des Absatz-Symbols links vom Rahmen: Absatzformat zurücksetzen, Symbol ausblenden."""
        from PySide6.QtWidgets import QMenu
        m = QMenu(self)
        m.addAction("Absatzformat zurücksetzen", self._frei_absatz_zuruecksetzen)
        m.addAction("Symbol vom Absatz-Layout ausblenden", self._frei_anker_ausblenden)
        m.popup(pos); self._frei_menue = m

    def _frei_anker_ausblenden(self) -> None:
        self._frei_anker_zeigen = False
        self.viewport().update()

    def _frei_absatz_zuruecksetzen(self) -> None:
        """Der Absatz, an dem das Objekt hängt, bekommt Ausrichtung, Einzüge und Abstände zurück (das Objekt bleibt)."""
        sel = self._frei_sel
        if sel is None or sel[0] != "t":
            return
        b = self.document().findBlockByNumber(sel[1])
        if not b.isValid():
            return
        from PySide6.QtGui import QTextBlockFormat
        alt = b.blockFormat(); neu = QTextBlockFormat()
        if alt.hasProperty(B_BILDANKER):
            neu.setProperty(B_BILDANKER, alt.stringProperty(B_BILDANKER))
        QTextCursor(b).setBlockFormat(neu)
        self.document().setModified(True); self._frei_rev = None; self.viewport().update()

    def _frei_wirken(self, **teile) -> None:
        from lunivo_writer.editor import bildlayout as BL
        BL.format_setzen(self, BL.ziel(self), **teile)

    def _frei_formstile(self, pos) -> None:
        m = self.frei_formstile_menue(self)
        m.popup(pos); self._frei_menue = m

    def frei_formstile_menue(self, parent=None, ed=None):
        E = ed or (lambda: self)                               # der Editor, auf den die Wahl wirkt (zur Wahlzeit, nicht zur Bauzeit)
        from lunivo_writer.ui.baukasten.objekt_menues import formstil_werte, formstile
        m = formstile(parent)
        def waehlen(k: str) -> None:
            ed = E()
            from lunivo_writer.editor import frei_objekt as FO
            if FO.art_gewaehlt(ed) == "form" and hasattr(ed.window(), "befehle"):        # Form: Füllung, Verlauf, Linie und Effekt des Rasters (formStilRaster)
                ed.window().befehle.formStilRaster(None, int(k[1]), int(k[2]))
            else:                                                                           # Bild, Textfeld, WordArt: Füllung und Rand
                w = formstil_werte(k)
                ed._frei_wirken(fuell=w["fuell"], rand=w["rand"])
            m.close()
        m.gewaehlt.connect(waehlen)
        m.fuss("Weitere Effekte(O)…", lambda: E()._frei_effekte())
        return m

    def _frei_formatierung(self, reiter: int = 0) -> None:
        """Zahnrad der Schnellleiste und Rechtsklick „Formatieren“: die Seitenleiste „Formatierung“ für das gewählte Objekt (Diagramm, SmartArt, Form, Bild …)."""
        fenster = self.window()
        if hasattr(fenster, "formatierung_seitenleiste"):
            fenster.formatierung_seitenleiste(reiter)

    def _frei_effekte(self) -> None:
        """„Weitere Effekte …“: die Seitenleiste „Formatierung“ mit den Effekten."""
        fenster = self.window()
        if hasattr(fenster, "objektformat_seitenleiste"):
            fenster.objektformat_seitenleiste(1)

    def _frei_fuell(self, pos) -> None:
        m = self.frei_fuell_menue(self)
        m.popup(pos); self._frei_menue = m

    def frei_fuell_menue(self, parent=None, ed=None):
        E = ed or (lambda: self)                               # der Editor, auf den die Wahl wirkt (zur Wahlzeit, nicht zur Bauzeit)
        from lunivo_writer.ui.baukasten.speichern_fenster import Dateifenster
        from PySide6.QtGui import QImage
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.ui.baukasten.objekt_menues import FuellMenue
        m = FuellMenue(parent)
        m.gewaehlt.connect(lambda c: E()._frei_wirken(fuell=None if c is None else {"art": "farbe", "farbe": c.name(QColor.HexArgb)}))
        m.verlauf_gewaehlt.connect(lambda c: E()._frei_wirken(fuell={"art": "verlauf", "farbe": c.name(QColor.HexArgb)}))
        m.graduell_gewaehlt.connect(lambda d, h: E()._frei_wirken(fuell={"art": "graduell", "dunkel": d, "hell": h, "farbe": d}))
        m.muster_gewaehlt.connect(lambda k: E()._frei_wirken(fuell={"art": "muster", "key": k, "farbe": Farbe.TINTE, "grund": Farbe.WEISS}))
        m.textur_gewaehlt.connect(lambda k: E()._frei_wirken(fuell={"art": "textur", "key": k}))

        def bild():
            pfad, _ = Dateifenster.getOpenFileName(E().window(), "Bild als Füllung", "", "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
            if pfad:
                BL.fuellbild_setzen(E(), BL.ziel(E()), QImage(pfad))
        m.bild_gewaehlt.connect(bild)
        m.weitere_fuellung.connect(lambda art: E()._frei_fuell_fenster(art))
        return m

    def _frei_fuell_fenster(self, art: str) -> None:
        """„Fülleffekte“, „Weitere Farbverläufe/Texturen/Muster“: die Seitenleiste „Formatierung“ auf „Füllung und Linie“ mit dieser Füllungsart."""
        fenster = self.window()
        if hasattr(fenster, "objektformat_seitenleiste"):
            fenster.objektformat_seitenleiste(0, art)

    def _frei_kontur(self, pos) -> None:
        m = self.frei_kontur_menue(self)
        m.popup(pos); self._frei_menue = m

    def frei_kontur_menue(self, parent=None, ed=None):
        E = ed or (lambda: self)                               # der Editor, auf den die Wahl wirkt (zur Wahlzeit, nicht zur Bauzeit)
        from lunivo_writer.ui.baukasten.objekt_menues import KonturMenue
        m = KonturMenue(parent)
        m.gewaehlt.connect(lambda c: E()._frei_wirken(rand=None) if c is None else E()._frei_wirken(rand_teil={"farbe": c.name(QColor.HexArgb)}))
        m.breite_gewaehlt.connect(lambda pt: E()._frei_wirken(rand_teil={"b": pt * 96 / 72}))
        m.strich_gewaehlt.connect(lambda a: E()._frei_wirken(rand_teil={"art": a}))
        m.weitere_linien.connect(lambda: E()._frei_linien_fenster())
        return m

    def _frei_linien_fenster(self) -> None:
        """„Weitere Linien …“: die Seitenleiste „Formatierung“ auf dem Reiter „Füllung und Linie“ (Farbe, Breite, Strichart)."""
        fenster = self.window()
        if hasattr(fenster, "objektformat_seitenleiste"):
            fenster.objektformat_seitenleiste(0)

    # ---- Layout: Popup neben dem Bild und das Fenster ---------------------------------------------------------------------------
    def bild_layout_popup(self, global_pos) -> None:
        self._frei_layout_popup(global_pos)

    def _frei_layout_popup(self, global_pos) -> None:
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.ui.baukasten.layout_optionen import LayoutOptionen
        z = BL.ziel(self)
        if z is None:
            return
        w = BL.lesen(self, z)
        p = LayoutOptionen(self, w["umbruch"], bool(w.get("mit_text")))
        p.gewaehlt.connect(lambda art: BL.anwenden(self, BL.ziel(self), {"umbruch": art}) if BL.ziel(self) else None)
        p.verschieben.connect(lambda an: BL.anwenden(self, BL.ziel(self), {"mit_text": bool(an)}) if BL.ziel(self) else None)
        p.mehr.connect(self.bild_layout_dialog)
        p.zeigen_bei(global_pos)
        self._frei_popup = p

    def bild_layout_dialog(self) -> None:
        """Das Fenster „Layout“ für das markierte Bild (frei oder im Text)."""
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.ui.baukasten.layout_dialog import LayoutDialog
        z = BL.ziel(self)
        if z is None:
            return
        d = LayoutDialog(self.window(), BL.lesen(self, z))
        if d.exec():
            z = BL.ziel(self)
            if z is not None:
                BL.anwenden(self, z, d.werte())

    # ---- Tasten --------------------------------------------------------------------------------------------------------
    def _frei_taste(self, e) -> bool:
        if not hasattr(self, "_frei_treffer") or self._frei_sel is None or self.isReadOnly():
            return False
        if self.__dict__.get("_fp_key") is not None:                              # Punkte bearbeiten: Esc beendet, Entf löscht den Punkt
            from lunivo_writer.ui.document import freiform_bedienung as FP
            if FP.taste(self, e):
                return True
        if e.key() == Qt.Key_Escape:
            self._frei_teilwahl_aufheben()
            self._frei_sel = None; self.viewport().update()
            return True
        if self._frei_knoten_rect() is not None and self.__dict__.get("_sa_edit") is None:          # SmartArt-Knoten: Enter/F2 oder Tippen schreibt im Knoten
            if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
                return self.frei_knoten_edit_starten()
            if e.text() and e.text().isprintable() and not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier)):
                return self.frei_knoten_edit_starten(e.text())
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):          # im Objekt schreiben
            from lunivo_writer.editor import frei_objekt as FO
            return FO.bearbeiten_starten(self)
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            key, self._frei_sel = self._frei_sel, None
            if key[0] == "k":
                self.page.bilder[:] = [a for a in self.page.bilder if id(a) != key[1]]
                self.document().setModified(True)
                self.pageApplied.emit()
            else:
                self._frei_absatz_aendern(key[1], key[2], None)
            self.viewport().update()
            return True
        return False
