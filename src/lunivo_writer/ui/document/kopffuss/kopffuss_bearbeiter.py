"""Kopf- und Fußzeile direkt auf der Seite bearbeiten (Einfügen ▸ Kopf- und Fußzeile, Doppelklick in den Seitenrand).

    b = editor.kopffuss()                 # der Bearbeiter des Editors (wird beim ersten Aufruf angelegt)
    b.starte("kopf")                      # oder "fuss"; ``b.aktiv``, ``b.beende()``, ``b.wechseln()``, ``b.abschnitt_springen(+1)``

Gespeichert wird weiter in ``PageSettings.header`` / ``footer`` (Text mit {PAGE}); die Seite wird nicht anders gezeichnet. Wie in der
Vorlage liegen gleichzeitig zwei randlose Textfelder (gestrichelter Rahmen) über Kopf- und Fußbereich des Blattes: oben darunter Linie,
Etikett „Kopfzeile“ und die Seitenzahl-Knöpfe, unten Etikett „Fußzeile“ über der Linie. Nur eine Leiste (``b.leiste``) hängt am aktiven
Bereich (``b.zone``, ``b.feld``); ein Klick in den anderen Bereich oder ``wechseln()`` verschiebt sie. Esc oder Doppelklick in den Text
beenden. Kein HTML."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRect, QRectF, Qt, QTimer, Signal

from PySide6.QtGui import QColor, QFont, QPen, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import (QDoubleSpinBox, QHBoxLayout, QLabel, QWidget)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.seite import seitenzahl as SZ
from lunivo_writer.models.page import HeaderFooter, mm_to_px
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_NORMAL,
    BREITE_SEITENZAHL_FELD,
    ICON_NORMAL,
    PADDING_ZAHLENFELD_KOPFFUSS,
    RADIUS_ZAHLENFELD_KLEIN,
    RAND_ETIKETT,
    RAND_SEITENZAHL_ZEILE,
)
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf

from lunivo_writer.ui.document.kopffuss.kopffuss_felder import (FELD_EIGENSCHAFT, FORMATE, ZONEN, _FLAG, _EinfuegenPanel, _Feld, _Leiste, _Linie, _stil, etikett_stil)



class KopfFussBearbeiter(QObject):
    gestartet = Signal(); beendet = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.ed = editor
        self.aktiv = False
        self.im_feld = False                                    # die Schreibmarke steht im Kopf-/Fußfeld: Start-Werkzeuge wirken dorthin
        self.zone = "kopf"
        self.blatt = 0
        self.leiste = self.absatz = self.panel = None
        self.felder, self.linien, self.etiketten = {}, {}, {}
        self._laedt = False
        self._verlauf, self._wieder = [], []                    # Rückgängig/Wiederholen: ("text", zone) oder ("hf", zone, vorher, nachher)
        self._zeit = QTimer(self); self._zeit.setSingleShot(True); self._zeit.setInterval(200); self._zeit.timeout.connect(self.speichern)

    @property
    def feld(self):
        """Das Feld des aktiven Bereichs (``zone``); None, solange noch nie gestartet."""
        return self.felder.get(self.zone)

    def _teile(self) -> list:
        return [w for z in ZONEN for w in (self.linien.get(z), self.felder.get(z), self.etiketten.get(z))] + [self.leiste, self.absatz]

    # ---- Start und Ende ------------------------------------------------------------------------------------------
    def starte(self, zone: str = "kopf", blatt: int | None = None) -> bool:
        ed = self.ed
        if ed.web:
            return False
        if self.aktiv:
            self.speichern()
        self.zone = "fuss" if zone == "fuss" else "kopf"
        self.blatt = self._cursor_blatt() if blatt is None else blatt
        if not self.felder:
            vp = ed.viewport()
            for z in ZONEN:
                f = self.felder[z] = _Feld(vp, z)
                f.schliessen.connect(self.beende); f.textChanged.connect(self._geaendert); f.fokus.connect(self._fokus)
                f.document().undoCommandAdded.connect(lambda z=z: self._text_gemerkt(z))
                self.linien[z] = _Linie(vp)
                et = self.etiketten[z] = QLabel("Kopfzeile" if z == "kopf" else "Fußzeile", vp)
                et.setStyleSheet(etikett_stil()); et.setContentsMargins(*RAND_ETIKETT)
            self.leiste = _Leiste(vp)
            from lunivo_writer.ui.widgets import icons
            self.absatz = DropdownKnopf(vp); self.absatz.setText("Absatz"); self.absatz.setIcon(icons.icon("pilcrow", ICON_NORMAL, Farbe.SYMBOL)); self.absatz.setProperty("papierKnopf", "absatz"); self.absatz.setObjectName("kfAbsatz")
            self.absatz.setToolTip("Absatz")
            vp.installEventFilter(self)
            self._menues()
        self.aktiv = True
        self.im_feld = True
        self._laden()
        self._platzieren()
        for w in self._teile():
            w.show(); w.raise_()
        self.feld.setFocus()
        self.gestartet.emit()
        return True

    def beende(self) -> None:
        if not self.aktiv:
            return
        self.speichern()
        self.aktiv = False
        self.im_feld = False
        for w in self._teile():
            if w is not None:
                w.hide()
        self.ed.viewport().update()
        self.ed.setFocus()
        self.beendet.emit()

    def wechseln(self) -> None:
        """Zwischen Kopf- und Fußzeile springen: Schreibmarke ins andere Feld, die Leiste zieht mit."""
        if self.aktiv:
            self.starte("fuss" if self.zone == "kopf" else "kopf", self.blatt)

    def abschnitt_springen(self, schritt: int) -> bool:
        """Zur Kopfzeile des vorigen/nächsten Abschnitts; → False, wenn es keinen gibt."""
        from lunivo_writer.editor.seite import abschnitte as AB
        ed = self.ed
        ziel = ed.abschnitt_nr() + schritt
        if ziel < 0 or ziel >= AB.anzahl(ed.document()):
            return False
        self.speichern()
        c = ed.textCursor(); c.setPosition(AB.beginn(ed.document(), ziel)); ed.setTextCursor(c)
        if self.aktiv:
            self.starte(self.zone)
        return True

    def _fokus(self, zone: str) -> None:
        """Klick/Schreibmarke in den anderen Bereich: die Leiste und das Absatz-Symbol ziehen dorthin."""
        if self.aktiv:
            self.im_feld = True
        if not self.aktiv or self._laedt or zone == self.zone:
            return
        self.zone = zone
        self._leiste_laden(self.ed.abschnitt_seite())
        self._platzieren()

    # ---- Seite und Text --------------------------------------------------------------------------------------------
    def _cursor_blatt(self) -> int:
        ed = self.ed
        try:
            y = ed.cursorRect().center().y()
            return max(0, int(ed._blatt_bei_y(y)))
        except Exception:
            return 0

    def _art(self, page) -> str:
        """"first", "even" oder "": welche Kopf-/Fußzeile das Blatt trägt (siehe ``PageSettings.kopf_fuss_art``)."""
        return page.kopf_fuss_art(self.blatt + 1, SZ.erste_nummer(page) + self.blatt)

    def _name(self, page, zone: str | None = None) -> str:
        art = self._art(page)
        return (art + "_" if art else "") + ("header" if (zone or self.zone) == "kopf" else "footer")

    def _etikett(self, page, zone: str) -> str:
        name = "Kopfzeile" if zone == "kopf" else "Fußzeile"
        if page.diff_even:
            return f"{name} {'gerader' if self._art(page) == 'even' else 'ungerader'} Seiten"
        return name

    def hf(self, page=None, zone: str | None = None) -> HeaderFooter:
        page = page or self.ed.abschnitt_seite()
        return getattr(page, self._name(page, zone))

    def _laden(self) -> None:
        """Beide Felder (Kopf und Fuß) des aktuellen Blatts füllen."""
        self._verlauf = [a for a in self._verlauf if a[0] != "text"]      # der Text der Felder wird neu gesetzt: ihre Schritte sind weg
        self._wieder = [a for a in self._wieder if a[0] != "text"]
        page = self.ed.abschnitt_seite()
        n = SZ.erste_nummer(page) + self.blatt
        zahlen = {"PAGE": SZ.nummer(n, page), "PAGES": str(max(1, int(getattr(self.ed, "_pages", 1) or 1)))}
        for z in ZONEN:
            hf = self.hf(page, z)
            self._laedt = True
            self.felder[z].felder_setzen(hf.text, zahlen)
            self._laedt = False
            self._ausrichten(z, hf.align)
            self._basis_anwenden(z, hf)
            self.felder[z].document().clearUndoRedoStacks()
            et = self.etiketten[z]
            et.setText(self._etikett(page, z)); et.setAccessibleName(et.text()); et.adjustSize()
        self._leiste_laden(page)

    def _leiste_laden(self, page) -> None:
        self.leiste.zahl_zeigen("{PAGE" in self.hf(page).text)

    def _ausrichten(self, zone: str, align: str) -> None:
        feld = self.felder[zone]
        al = _FLAG.get(SZ.ausrichtung(align, self.blatt + 1), Qt.AlignLeft)
        o = feld.document().defaultTextOption(); o.setAlignment(al | Qt.AlignVCenter)
        feld.document().setDefaultTextOption(o)
        c = feld.textCursor(); c.select(c.SelectionType.Document)
        bf = c.blockFormat(); bf.setAlignment(al)
        alt, self._laedt = self._laedt, True                    # die Ausrichtung ist kein Schritt des Textes
        c.joinPreviousEditBlock(); c.setBlockFormat(bf); c.endEditBlock()
        self._laedt = alt

    def _geaendert(self) -> None:
        if not self._laedt and self.aktiv:
            self._zeit.start()

    def speichern(self) -> None:
        """Den Text des Feldes in die Seiteneinrichtung des Abschnitts schreiben (sofort; sonst nach kurzer Pause beim Tippen)."""
        self._zeit.stop()
        if not self.aktiv or not self.felder:
            return
        page = self.ed.abschnitt_seite()
        geaendert = False
        for z in ZONEN:
            hf = self.hf(page, z)
            text = self.felder[z].text_lesen().strip("\n")
            if text != hf.text:
                setattr(page, self._name(page, z), hf.kopie(text)); geaendert = True
        if geaendert:
            self.ed.page_settings_changed(page)

    def aendern(self, aendere, neu_laden: bool = True) -> None:
        """``aendere(page)`` auf die Einrichtung des aktuellen Abschnitts anwenden und speichern; → danach das Feld neu füllen."""
        self.speichern()
        page = self.ed.abschnitt_seite()
        if aendere(page) is False:
            return
        self.ed.page_settings_changed(page)
        if self.aktiv and neu_laden:
            self._laden()
            self._platzieren()

    def ausrichtung_setzen(self, align: str) -> None:
        def f(page):
            hf = self.hf(page)
            setattr(page, self._name(page), hf.kopie(align=align))
        vorher = self._stand()
        self.aendern(f, neu_laden=False)
        self._ausrichten(self.zone, align)
        self._merken(vorher)

    # ---- Rückgängig / Wiederholen (Schnellzugriff oben): Text im Feld und Format/Ausrichtung der Zeile in einer Reihenfolge ------------------
    def _stand(self) -> tuple:
        hf = self.hf()
        return (self.zone, dict(hf.fmt), hf.align)

    def _merken(self, vorher: tuple) -> None:
        nachher = self._stand()
        if nachher != vorher:
            self._verlauf.append(("hf", vorher[0], vorher, nachher)); self._wieder.clear()

    def _text_gemerkt(self, zone: str) -> None:
        if self.aktiv and not self._laedt:
            self._verlauf.append(("text", zone)); self._wieder.clear()

    def _stand_setzen(self, stand: tuple) -> None:
        zone, fmt, align = stand
        alt, self.zone = self.zone, zone
        def f(page):
            hf = self.hf(page, zone)
            neu = hf.kopie(align=align); neu.fmt = dict(fmt)
            setattr(page, self._name(page, zone), neu)
        self.aendern(f, neu_laden=False)
        self._ausrichten(zone, align); self._basis_anwenden(zone)
        self.zone = alt

    @staticmethod
    def _text_schritt(feld, rueck: bool) -> None:
        """Rückgängig/Wiederholen im Feld, bis sich der Text ändert (Schriftschritte, die Qt dazwischen merkt, zählen nicht)."""
        vor = feld.toPlainText()
        d = feld.document()
        while (d.isUndoAvailable() if rueck else d.isRedoAvailable()):
            feld.undo() if rueck else feld.redo()
            if feld.toPlainText() != vor:
                break

    def rueckgaengig(self) -> None:
        self.speichern()
        if not self._verlauf:
            return
        a = self._verlauf.pop()
        if a[0] == "text":
            self._text_schritt(self.felder[a[1]], rueck=True)
        else:
            self._stand_setzen(a[2])
        self._wieder.append(a)

    def wiederholen(self) -> None:
        if not self._wieder:
            return
        a = self._wieder.pop()
        if a[0] == "text":
            self._text_schritt(self.felder[a[1]], rueck=False)
        else:
            self._stand_setzen(a[3])
        self._verlauf.append(a)

    # ---- Zeichenformat der Zeile (Start ▸ Schriftart) ----------------------------------------------------------------
    def basis_format(self, fmt: dict, zoom: float = 1.0) -> QTextCharFormat:
        """Das Zeichenformat für ein Format aus ``HeaderFooter.fmt``; die Größe wird mit dem Zoom des Editors skaliert."""
        f = QTextCharFormat()
        if fmt.get("family"):
            f.setFontFamilies([fmt["family"]])
        if fmt.get("size_pt"):
            f.setFontPointSize(float(fmt["size_pt"]) * zoom)
        if "bold" in fmt:
            f.setFontWeight(QFont.Bold if fmt["bold"] else QFont.Normal)
        if "italic" in fmt:
            f.setFontItalic(bool(fmt["italic"]))
        if "underline" in fmt:
            f.setFontUnderline(bool(fmt["underline"]))
        if fmt.get("color"):
            f.setForeground(QColor(fmt["color"]))
        if "strike" in fmt:
            f.setFontStrikeOut(bool(fmt["strike"]))
        if "script" in fmt:
            f.setVerticalAlignment({"sup": QTextCharFormat.AlignSuperScript, "sub": QTextCharFormat.AlignSubScript}.get(fmt["script"], QTextCharFormat.AlignNormal))
        if fmt.get("highlight"):
            f.setBackground(QColor(fmt["highlight"]))
        if fmt.get("kontur"):
            k = fmt["kontur"]
            f.setTextOutline(QPen(QColor(k["farbe"]), k["breite"], Qt.PenStyle(k.get("stil", 1))))
        from lunivo_writer.editor.dokument.zusatz import P_EFFEKT
        f.setProperty(P_EFFEKT, fmt.get("effekt", ""))              # Schatten, Spiegelung, Leuchten, Verlauf (siehe editor/text/textfx.py)
        return f

    def _basis_anwenden(self, zone: str, hf=None) -> None:
        feld = self.felder[zone]
        hf = hf or self.hf(None, zone)
        feld.basis = self.basis_format(hf.fmt, self.ed.zoom)
        feld._zoom_basis = self.ed.zoom
        c = QTextCursor(feld.document()); c.select(QTextCursor.Document)
        alt, self._laedt = self._laedt, True
        c.joinPreviousEditBlock()                               # gehört zum vorigen Schritt: kein eigener Rückgängig-Schritt für die Zeilenschrift
        c.mergeCharFormat(feld.basis)
        c.endEditBlock()
        feld.setCurrentCharFormat(feld.basis)
        self._laedt = alt

    def format_anwenden(self, f: QTextCharFormat, farbe_weg: bool = False) -> None:
        """Ein Zeichenformat der Start-Werkzeuge (Schrift, Größe, Fett, Kursiv, Unterstrichen, Farbe) auf die aktive Zeile anwenden."""
        if not self.aktiv:
            return
        vorher = self._stand()
        neu = {}
        if f.hasProperty(QTextFormat.FontFamilies):
            fam = f.fontFamilies()
            name = fam[0] if isinstance(fam, (list, tuple)) and fam else str(fam)
            if name:
                neu["family"] = name
        if f.fontPointSize() > 0:
            neu["size_pt"] = f.fontPointSize()
        if f.hasProperty(QTextFormat.FontWeight):
            neu["bold"] = f.fontWeight() >= 600
        if f.hasProperty(QTextFormat.FontItalic):
            neu["italic"] = f.fontItalic()
        if f.hasProperty(QTextFormat.TextUnderlineStyle) or f.hasProperty(QTextFormat.FontUnderline):
            neu["underline"] = f.underlineStyle() != QTextCharFormat.NoUnderline
        if f.hasProperty(QTextFormat.ForegroundBrush) and f.foreground().style() != Qt.NoBrush:
            neu["color"] = f.foreground().color().name(QColor.HexArgb)
        if f.hasProperty(QTextFormat.FontStrikeOut):
            neu["strike"] = f.fontStrikeOut()
        if f.hasProperty(QTextFormat.TextVerticalAlignment):
            neu["script"] = {QTextCharFormat.AlignSuperScript: "sup", QTextCharFormat.AlignSubScript: "sub"}.get(f.verticalAlignment(), "")
        if f.hasProperty(QTextFormat.BackgroundBrush):
            neu["highlight"] = f.background().color().name() if f.background().style() != Qt.NoBrush else None
        from lunivo_writer.editor.dokument.zusatz import P_EFFEKT
        if f.hasProperty(P_EFFEKT):
            neu["effekt"] = f.stringProperty(P_EFFEKT)
        if f.hasProperty(QTextFormat.TextOutline):
            pen = f.textOutline()
            neu["kontur"] = None if pen.style() == Qt.NoPen else {"farbe": pen.color().name(), "breite": pen.widthF(), "stil": int(pen.style().value)}

        def setze(page):
            hf = self.hf(page)
            fmt = dict(hf.fmt); fmt.update(neu)
            if farbe_weg:
                fmt.pop("color", None)
            for schl in ("effekt", "kontur", "highlight", "script"):
                if schl in fmt and not fmt[schl]:
                    del fmt[schl]
            setattr(page, self._name(page), hf.kopie()); getattr(page, self._name(page)).fmt = fmt
        self.aendern(setze, neu_laden=False)
        self._basis_anwenden(self.zone)
        self._merken(vorher)

    def format_loeschen(self) -> None:
        """„Formatierung löschen“: Schrift, Größe, F/K/U, Farbe und Effekte der aktiven Zeile zurück auf die Vorgabe (die Seitenzahl-Felder bleiben)."""
        vorher = self._stand()
        if not self.hf().fmt:
            return
        def setze(page):
            hf = self.hf(page)
            neu = hf.kopie(); neu.fmt = {}
            setattr(page, self._name(page), neu)
        self.aendern(setze, neu_laden=False)
        feld = self.feld
        alt, self._laedt = self._laedt, True
        c = QTextCursor(feld.document()); c.joinPreviousEditBlock()
        for blk in range(feld.document().blockCount()):
            it = feld.document().findBlockByNumber(blk).begin()
            while not it.atEnd():
                fr = it.fragment()
                if not fr.charFormat().property(FELD_EIGENSCHAFT):
                    k = QTextCursor(feld.document()); k.setPosition(fr.position()); k.setPosition(fr.position() + fr.length(), QTextCursor.KeepAnchor)
                    k.setCharFormat(QTextCharFormat())
                it += 1
        c.endEditBlock()
        self._laedt = alt
        self._basis_anwenden(self.zone)
        self._merken(vorher)

    def format_lesen(self) -> QTextCharFormat:
        """Das Zeichenformat der aktiven Zeile (für die Schalterstellung der Start-Werkzeuge)."""
        f = self.basis_format(self.hf().fmt)
        if not self.hf().fmt.get("size_pt"):
            f.setFontPointSize(10.0)                              # so groß wie die Standardschrift der Zeile (13 px)
        return f

    def ausrichtung_vom_werkzeug(self, al) -> None:
        self.ausrichtung_setzen("right" if al & Qt.AlignRight else "center" if al & Qt.AlignHCenter else "left")

    def tabstopp_einfuegen(self) -> None:
        if self.aktiv:
            self.feld.insertPlainText("\t"); self.feld.setFocus()

    # ---- Lage ----------------------------------------------------------------------------------------------------
    def _rect(self, zone: str) -> QRectF:
        ed = self.ed
        z = ed.zoom
        b = ed._blatt(self.blatt)
        oben = ed.blatt_oben(self.blatt)
        h = mm_to_px(10) * z
        y = oben + mm_to_px(8) * z if zone == "kopf" else oben + b["H"] - mm_to_px(18) * z       # wie ``editor_anzeige`` die Zeilen zeichnet
        return QRectF(b["x"] + b["ml"], y, b["cw"], h)

    def _platzieren(self) -> None:
        if not self.aktiv:
            return
        b = self.ed._blatt(self.blatt)
        f = QFont(self.ed.font()); f.setPixelSize(max(6, round(13 * self.ed.zoom)))
        geo = {}
        for z in ZONEN:
            g = geo[z] = self._rect(z).toRect()
            feld = self.felder[z]
            gf = QRect(g)
            if "reflektion" in self.hf(None, z).fmt.get("effekt", ""):      # die Spiegelung liegt unter der Zeile: das Feld braucht Platz dafür
                gf.setHeight(g.height() + round(mm_to_px(5) * self.ed.zoom))
            if feld.geometry() != gf:
                feld.setGeometry(gf)
            if feld.font() != f:
                feld.setFont(f)
            if getattr(feld, "_zoom_basis", None) != self.ed.zoom:
                self._basis_anwenden(z)
            ly_linie = g.bottom() + 6 if z == "kopf" else g.top() - 6
            self.linien[z].setGeometry(round(b["x"]), ly_linie - 1, round(b["W"]), 3)
            et = self.etiketten[z]
            et.adjustSize()
            # Kopf: Etikett unter der Linie; Fuß: Etikett über der Linie
            ey = ly_linie + 4 if z == "kopf" else ly_linie - et.height() - 4
            et.move(g.left(), max(0, ey))
        g, et = geo[self.zone], self.etiketten[self.zone].geometry()
        links, rechts = round(b["x"]) + 4, round(b["x"] + b["W"]) - 4
        lw = self.leiste.natuerliche_breite()
        if et.right() + 6 + lw <= rechts:                       # passt neben das Etikett
            lh = self.leiste.h.heightForWidth(lw)
            self.leiste.setFixedSize(lw, lh)
            self.leiste.move(et.right() + 6, max(0, et.center().y() - lh // 2))
        else:                                                   # sonst unter (Kopf) bzw. über (Fuß) das Etikett, umbrechend, nie über den Blattrand
            lw = min(lw, rechts - links)
            lh = self.leiste.h.heightForWidth(lw)
            self.leiste.setFixedSize(lw, lh)
            x = max(links, min(et.left(), rechts - lw))
            y = et.bottom() + 4 if self.zone == "kopf" else et.top() - lh - 4
            self.leiste.move(x, max(0, y))
        self.absatz.adjustSize()
        self.absatz.move(max(0, g.left() - self.absatz.width() - 4), g.top())

    def eventFilter(self, o, e):
        try:
            if self.aktiv and o is self.ed.viewport() and e.type() in (QEvent.Resize, QEvent.Paint):
                self._platzieren()
            elif self.aktiv and o is self.ed.viewport() and e.type() == QEvent.MouseButtonPress:
                self.im_feld = False                            # Klick ins Dokument: die Werkzeuge wirken wieder auf den Text
        except RuntimeError:                                    # Editor beim Beenden schon abgebaut
            pass
        return False

    # ---- Menüs -------------------------------------------------------------------------------------------------------
    def _menues(self) -> None:
        k = self.leiste.knopf
        m = MenueListe(self.leiste); k["neu"].menue_setzen(m, geteilt=False); m.aboutToShow.connect(lambda m=m: self._menue_neu(m))
        m = MenueListe(self.leiste); k["format"].menue_setzen(m, geteilt=False); m.aboutToShow.connect(lambda m=m: self._menue_format(m))
        m = MenueListe(self.leiste); k["loeschen"].menue_setzen(m, geteilt=False); m.aboutToShow.connect(lambda m=m: self._menue_loeschen(m))
        self.panel = _EinfuegenPanel(self.leiste); k["einfuegen"].menue_setzen(self.panel, geteilt=False)
        self.panel.aboutToShow.connect(lambda: self.panel.ort_setzen(self.zone))
        self.panel.uebernommen.connect(self.seitenzahl_einfuegen)
        m = MenueListe(self.absatz); self.absatz.menue_setzen(m, geteilt=False)
        m.eintrag("Absatzformat zurücksetzen", lambda: self.ausrichtung_setzen("center"))
        m.eintrag("Symbol vom Absatz-Layout ausblenden", self.absatz.hide)

    def _menue_neu(self, m: MenueListe) -> None:
        m.clear()
        page = self.ed.abschnitt_seite()
        # Wie die Vorlage: Beschriftung und kleines Zahlfeld nebeneinander, hell wie das übrige Aufklappfeld auf dem Papier
        zeile = QWidget(); zeile.setObjectName("seitennummerierung")
        zeile.setStyleSheet(_stil("#seitennummerierung { background: @PAPIER; } QLabel { color: @TINTE; background: transparent; }"
                                  " QDoubleSpinBox { background: @PAPIER; color: @SCHWARZ; border: 1px solid @LEISTE_RAND; border-radius: " f"{RADIUS_ZAHLENFELD_KLEIN}" "px;"
                                  " padding: " f"{PADDING_ZAHLENFELD_KOPFFUSS}" "; selection-background-color: palette(highlight); selection-color: palette(highlighted-text); }"))
        lay = QHBoxLayout(zeile); lay.setContentsMargins(*RAND_SEITENZAHL_ZEILE); lay.setSpacing(ABSTAND_NORMAL)
        lay.addWidget(QLabel("Seitennummerierung:"))
        sp = QDoubleSpinBox(); sp.setDecimals(0); sp.setRange(1, 99999); sp.setValue(SZ.erste_nummer(page)); sp.setFixedWidth(BREITE_SEITENZAHL_FELD)
        sp.setAccessibleName("Seitennummerierung")
        sp.editingFinished.connect(lambda: self._start_setzen(int(sp.value())))
        lay.addWidget(sp); lay.addStretch(1)
        m.widget(zeile)
        m.eintrag("Nummerierung fortsetzen", lambda: self._start_setzen(0), aktiv=page.seiten_start > 0)

    def seitenzahl_einfuegen(self, ausr: str, muster: str, zahl: str, bereich: str) -> None:
        """Seitenzahl in die Zeile setzen, die gerade bearbeitet wird („Seitenzahl einfügen ▾“); ``bereich``: dokument | seite | abschnitt."""
        from lunivo_writer.editor.seite import abschnitte as AB
        self.speichern()
        ed = self.ed
        doc = ed.document()
        if bereich == "dokument":
            ziele = list(range(AB.anzahl(doc)))
        elif bereich == "seite":
            pos = ed.textCursor().position()
            anfang = max([AB.beginn(doc, ed.abschnitt_nr())] + [x for x in ed.seitenwechsel if x <= pos])
            ziele = [AB.einfuegen_an(doc, anfang, "naechste", ed.page)]
        else:
            ziele = [ed.abschnitt_nr()]
        for nr in ziele:
            ps = SZ.seitenzahl_setzen(ed.abschnitt_seite(nr), self.zone, ausr, muster, zahl)
            if nr == 0:
                ed.apply_page(ps)
            else:
                AB.setzen(doc, nr, ps)
        ed._recount(); doc.setModified(True)
        if self.aktiv:
            self._laden(); self._platzieren()

    def _start_setzen(self, n: int) -> None:
        self.aendern(lambda p: setattr(p, "seiten_start", max(0, n)))

    def _menue_format(self, m: MenueListe) -> None:
        m.clear()
        aktuell = self.ed.abschnitt_seite().seiten_format
        for schl, text in FORMATE:
            m.eintrag(text, lambda s=schl: self.aendern(lambda p: setattr(p, "seiten_format", s)), haken=schl == aktuell)

    def _menue_loeschen(self, m: MenueListe) -> None:
        m.clear()
        m.eintrag("Aktuelle Seite", lambda: self.seitenzahl_loeschen("aktuelle"))
        m.eintrag("Gesamtes Dokument", lambda: self.seitenzahl_loeschen("dokument"))
        m.eintrag("Auf aktuelle Seite", lambda: self.seitenzahl_loeschen("auf"))
        m.eintrag("Von aktueller Seite", lambda: self.seitenzahl_loeschen("von"))
        m.eintrag("Aktueller Abschnitt", lambda: self.seitenzahl_loeschen("abschnitt"))

    def seitenzahl_loeschen(self, art: str) -> bool | None:
        """Seitenzahl entfernen: "dokument" (alle Abschnitte), "abschnitt", "aktuelle", "auf", "von" (siehe ``seitenzahl_loeschen_bereich``).
        → True/False: geändert/gab keine, None: nicht darstellbar (Hinweis in der Statusleiste)."""
        from lunivo_writer.editor.seite import abschnitte as AB
        self.speichern()
        ed = self.ed
        if art == "dokument":
            gab = False
            for nr in range(AB.anzahl(ed.document())):
                pg = ed.abschnitt_seite(nr)
                if SZ.seitenzahlen_entfernen(pg):
                    gab = True
                    if nr > 0:
                        AB.setzen(ed.document(), nr, pg)
                    else:
                        ed.apply_page(pg)
            ed._recount(); ed.viewport().update(); ed.document().setModified(True)
            ergebnis = gab
        else:
            pg = ed.abschnitt_seite()
            ergebnis = SZ.seitenzahl_loeschen_bereich(pg, art, self.blatt)
            if ergebnis:
                ed.page_settings_changed(pg)
        if ergebnis is None:
            self._hinweis("Das lässt sich nur für die erste Seite oder einen ganzen Abschnitt einstellen.")
        elif not ergebnis:
            self._hinweis("Hier steht keine Seitenzahl.")
        if self.aktiv:
            self._laden()
        return ergebnis

    def _hinweis(self, text: str) -> None:
        w = self.ed.window()
        sb = getattr(w, "statusBar", None)
        if callable(sb):
            sb().showMessage(text, 4000)
