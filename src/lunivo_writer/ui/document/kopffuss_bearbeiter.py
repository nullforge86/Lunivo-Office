"""Kopf- und Fußzeile direkt auf der Seite bearbeiten (Einfügen ▸ Kopf- und Fußzeile, Doppelklick in den Seitenrand).

    b = editor.kopffuss()                 # der Bearbeiter des Editors (wird beim ersten Aufruf angelegt)
    b.starte("kopf")                      # oder "fuss"; ``b.aktiv``, ``b.beende()``, ``b.wechseln()``, ``b.abschnitt_springen(+1)``

Gespeichert wird weiter in ``PageSettings.header`` / ``footer`` (Text mit {PAGE}); die Seite wird nicht anders gezeichnet. Wie in der
Vorlage liegen gleichzeitig zwei randlose Textfelder (gestrichelter Rahmen) über Kopf- und Fußbereich des Blattes: oben darunter Linie,
Etikett „Kopfzeile“ und die Seitenzahl-Knöpfe, unten Etikett „Fußzeile“ über der Linie. Nur eine Leiste (``b.leiste``) hängt am aktiven
Bereich (``b.zone``, ``b.feld``); ein Klick in den anderen Bereich oder ``wechseln()`` verschiebt sie. Esc oder Doppelklick in den Text
beenden. Kein HTML."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRectF, QSize, Qt, QTimer, Signal
import re

from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPen, QPixmap, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import (QButtonGroup, QComboBox, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel, QMenu, QTextEdit, QPushButton,
                               QRadioButton, QToolButton, QVBoxLayout, QWidget, QWidgetAction)

from lunivo_writer.editor import seitenzahl as SZ
from lunivo_writer.models.page import HeaderFooter, mm_to_px
from lunivo_writer.ui.baukasten.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout

ZONEN = ("kopf", "fuss")
_FLAG = {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}
FELD_EIGENSCHAFT = int(QTextFormat.UserProperty) + 1          # in der Zeichenformatierung: "PAGE" oder "PAGES" (das Feld, das die Zahl zeigt)
_FELDER = re.compile(r"\{(PAGES|PAGE)\}")
FORMATE = [("dezimal", "1, 2, 3 …"), ("klein", "a, b, c …"), ("gross", "A, B, C …"), ("roem_klein", "i, ii, iii …"), ("roem_gross", "I, II, III …")]


LEISTE_STIL = """
#kfLeiste QToolButton { background: #f5f5f5; color: #333333; border: 1px solid #c8c8c8; border-radius: 2px; padding: 2px 6px; }
#kfLeiste QToolButton:hover { background: #e6e6e6; }
#kfLeiste QToolButton::menu-indicator { image: none; width: 0px; }
#kfLeiste QMenu, #kfAbsatz QMenu { background: #ffffff; color: #333333; border: 1px solid #c8c8c8; }
#kfLeiste QMenu::item:selected, #kfAbsatz QMenu::item:selected { background: #e8f0fe; color: #333333; }
#kfLeiste QMenu::item:disabled { color: #9a9a9a; }
"""
ABSATZ_STIL = ("QToolButton { background: #f5f5f5; color: #333333; border: 1px solid #c8c8c8; border-radius: 2px; padding: 1px 4px; }"
               "QToolButton:hover { background: #e6e6e6; } QToolButton::menu-indicator { image: none; width: 0px; }"
               "QMenu { background: #ffffff; color: #333333; border: 1px solid #c8c8c8; } QMenu::item:selected { background: #e8f0fe; color: #333333; }")
ETIKETT_STIL = "QLabel { background: #f5f5f5; color: #777777; border: 1px dashed #9a9a9a; }"
PANEL_STIL = """
QWidget#kfPanel { background: #ffffff; color: #333333; }
#kfPanel QLabel, #kfPanel QRadioButton { color: #333333; background: transparent; }
#kfPanel QComboBox { background: #ffffff; color: #333333; border: 1px solid #c8c8c8; border-radius: 2px; padding: 2px 6px; }
#kfPanel QComboBox QAbstractItemView { background: #ffffff; color: #333333; selection-background-color: #cfe0fb; selection-color: #333333; }
#kfPanel QToolButton { background: #f7f7f7; color: #333333; border: 1px solid transparent; padding: 3px; }
#kfPanel QToolButton:checked { background: #cfe0fb; }
#kfPanel QToolButton:hover { border: 1px solid #c8c8c8; }
#kfPanel QRadioButton::indicator { width: 12px; height: 12px; border: 1px solid #8a8a8a; border-radius: 7px; background: #ffffff; }
#kfPanel QRadioButton::indicator:checked { background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 #3e78d0, stop:0.5 #3e78d0, stop:0.6 #ffffff, stop:1 #ffffff); border-color: #3e78d0; }
#kfPanel QPushButton { background: #3e78d0; color: #ffffff; border: none; border-radius: 2px; padding: 3px 22px; }
"""


def _symbol(art: str) -> QIcon:
    """Aktionssymbol aus dem zentralen Lucide-Katalog."""
    from lunivo_writer.ui.widgets import icons
    return icons.icon({"x": "x", "neu": "file-plus", "format": "file-text"}.get(art, "file"), 16)


class _Linie(QWidget):
    """Gestrichelte graue Linie über die ganze Blattbreite, an der der Kopf-/Fußbereich endet."""

    def __init__(self, eltern):
        super().__init__(eltern)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, e):
        p = QPainter(self)
        pen = QPen(QColor("#9a9a9a")); pen.setStyle(Qt.DashLine); p.setPen(pen)
        p.drawLine(0, self.height() // 2, self.width(), self.height() // 2)


class _EinfuegenPanel(QMenu):
    """Aufklappfeld „Seitenzahl einfügen“: Format, Position (fünf Kacheln mit Seitenbildchen), Übernehmen für, OK."""
    uebernommen = Signal(str, str, str, str)          # Ausrichtung, Muster, Zahlenart, Bereich (dokument | seite | abschnitt)
    POS = [("left", "Links"), ("center", "Zentriert"), ("right", "Rechts"), ("aussen", "Außen"), ("innen", "Innen")]

    def __init__(self, eltern):
        super().__init__(eltern)
        self.ort = "kopf"
        self.setStyleSheet("QMenu { background: #ffffff; border: 1px solid #c8c8c8; }")
        w = QWidget(); w.setObjectName("kfPanel"); w.setStyleSheet(PANEL_STIL)
        v = QVBoxLayout(w); v.setContentsMargins(10, 8, 10, 10); v.setSpacing(6)
        self.format = QComboBox(); self.format.setAccessibleName("Format")
        for muster, zahl, text in SZ.MUSTER:
            self.format.addItem("Format: " + text, (muster, zahl))
        v.addWidget(self.format)
        v.addWidget(QLabel("Position:"))
        g = QGridLayout(); g.setSpacing(2)
        self.gruppe = QButtonGroup(self); self.gruppe.setExclusive(True)
        self.kacheln = {}
        for i, (schl, text) in enumerate(self.POS):
            k = QToolButton(); k.setCheckable(True); k.setText(text); k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            k.setIconSize(QSize(40, 50)); k.setMinimumSize(92, 80); k.setAccessibleName(text)
            self.gruppe.addButton(k); self.kacheln[schl] = k
            g.addWidget(k, i // 3, i % 3)
        self.kacheln["center"].setChecked(True)
        v.addLayout(g)
        v.addWidget(QLabel("Übernehmen für:"))
        r = QHBoxLayout(); r.setSpacing(10)
        self.bereich = {}
        for schl, text in (("dokument", "Gesamtes Dokument"), ("seite", "Von aktueller Seite"), ("abschnitt", "Aktueller Abschnitt")):
            b = QRadioButton(text); self.bereich[schl] = b; r.addWidget(b)
        self.bereich["dokument"].setChecked(True)
        v.addLayout(r)
        ok = QPushButton("OK"); ok.clicked.connect(self._ok)
        z = QHBoxLayout(); z.addStretch(1); z.addWidget(ok); v.addLayout(z)
        a = QWidgetAction(self); a.setDefaultWidget(w); self.addAction(a)

    def ort_setzen(self, ort: str) -> None:
        from lunivo_writer.ui.baukasten.seiten_bildchen import seitenzahl_zeichner
        self.ort = ort
        for schl, k in self.kacheln.items():
            pm = QPixmap(40, 50); pm.fill(Qt.transparent)
            p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
            seitenzahl_zeichner(ort, schl)(p, QRectF(0, 0, 40, 50)); p.end()
            k.setIcon(QIcon(pm))

    def _ok(self) -> None:
        pos = next(s for s, k in self.kacheln.items() if k.isChecked())
        bereich = next(s for s, b in self.bereich.items() if b.isChecked())
        muster, zahl = self.format.currentData()
        self.close()
        self.uebernommen.emit(pos, muster, zahl, bereich)


class _Feld(QTextEdit):
    """Das Textfeld über dem Kopf- bzw. Fußbereich: randlos, gestrichelter Rahmen, Esc beendet."""
    schliessen = Signal()
    fokus = Signal(str)                                           # bekommt die Schreibmarke: "kopf" oder "fuss"

    def __init__(self, eltern, zone: str = "kopf"):
        super().__init__(eltern)
        self.zone = zone
        self.setFrameShape(QTextEdit.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAccessibleName("Kopfzeile" if zone == "kopf" else "Fußzeile")
        # Das Feld steht auf dem weißen Papier: Farben unabhängig vom Programm-Thema (Papier, schwarzer Text, sichtbare Schreibmarke)
        pal = QPalette(self.palette())
        for gr in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            pal.setColor(gr, QPalette.Base, QColor("#ffffff")); pal.setColor(gr, QPalette.Window, QColor("#ffffff"))
            pal.setColor(gr, QPalette.Text, QColor("#000000")); pal.setColor(gr, QPalette.WindowText, QColor("#000000"))
            pal.setColor(gr, QPalette.Highlight, QColor("#3e78d0")); pal.setColor(gr, QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(pal)
        self.setStyleSheet("QTextEdit { background: #ffffff; color: #000000; border: none; selection-background-color: #3e78d0; selection-color: #ffffff; }")
        self.setCursorWidth(1)

    # ---- Felder: {PAGE}/{PAGES} stehen als Zahl mit Hintergrund im Text und werden beim Speichern wieder zu {PAGE}/{PAGES} ----
    @staticmethod
    def _feld_format(art: str) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setProperty(FELD_EIGENSCHAFT, art)
        f.setBackground(QColor("#d9d9d9"))
        return f

    def felder_setzen(self, text: str, zahlen: dict) -> None:
        """Den Text mit {PAGE}/{PAGES} ins Feld schreiben; die Felder erscheinen als ``zahlen["PAGE"]`` bzw. ``zahlen["PAGES"]``."""
        self.clear()
        c = QTextCursor(self.document())
        for i, zeile in enumerate(text.split("\n")):
            if i:
                c.insertBlock()
            rest = 0
            for m in _FELDER.finditer(zeile):
                c.insertText(zeile[rest:m.start()], QTextCharFormat())
                c.insertText(zahlen.get(m.group(1), m.group(1)), self._feld_format(m.group(1)))
                rest = m.end()
            c.insertText(zeile[rest:], QTextCharFormat())

    def text_lesen(self) -> str:
        """Der Text, in dem jedes Feld wieder als {PAGE}/{PAGES} steht."""
        zeilen = []
        b = self.document().begin()
        while b.isValid():
            teile = []
            it = b.begin()
            while not it.atEnd():
                fr = it.fragment()
                art = fr.charFormat().property(FELD_EIGENSCHAFT)
                teile.append("{" + art + "}" if art else fr.text())
                it += 1
            zeilen.append("".join(teile))
            b = b.next()
        return "\n".join(zeilen)

    def formatierung_lesen(self) -> list[dict]:
        """Liefert den Inhalt absatzweise mit Zeichenformaten; unabhängig von HTML."""
        abschnitte = []
        block = self.document().begin()
        while block.isValid():
            zeichen = []
            it = block.begin()
            while not it.atEnd():
                fragment = it.fragment()
                fmt = fragment.charFormat()
                vordergrund = fmt.foreground()
                zeichen.append({
                    "text": fragment.text(),
                    "feld": fmt.property(FELD_EIGENSCHAFT) or None,
                    "schriftart": fmt.fontFamily() or None,
                    "schriftgroesse": fmt.fontPointSize() or None,
                    "fett": fmt.fontWeight() >= QFont.Bold,
                    "kursiv": fmt.fontItalic(),
                    "unterstrichen": fmt.fontUnderline(),
                    "farbe": vordergrund.color().name()
                        if vordergrund.style() != Qt.NoBrush else None,
                })
                it += 1
            abschnitte.append({
                "ausrichtung": int(block.blockFormat().alignment()),
                "zeichen": zeichen,
            })
            block = block.next()
        return abschnitte

    def _feld_bei(self, pos: int):
        """(Anfang, Ende) des Feldes, das die Zeichen vor/hinter ``pos`` berührt, sonst None — getrennt nach 'davor' und 'dahinter'."""
        c = QTextCursor(self.document())
        res = {}
        for seite, p in (("davor", pos - 1), ("dahinter", pos)):
            if p < 0 or p >= self.document().characterCount() - 1:
                continue
            c.setPosition(p); c.setPosition(p + 1, QTextCursor.KeepAnchor)
            if c.charFormat().property(FELD_EIGENSCHAFT):
                b = self.document().findBlock(p)
                a = e = None
                it = b.begin()
                while not it.atEnd():
                    fr = it.fragment()
                    if fr.position() <= p < fr.position() + fr.length():
                        a, e = fr.position(), fr.position() + fr.length()
                        break
                    it += 1
                res[seite] = (a, e)
        return res

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self.fokus.emit(self.zone)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.schliessen.emit()
            return
        c = self.textCursor()
        if e.key() in (Qt.Key_Backspace, Qt.Key_Delete) and not c.hasSelection():
            f = self._feld_bei(c.position()).get("davor" if e.key() == Qt.Key_Backspace else "dahinter")
            if f:                                                     # das Feld ganz löschen
                c.setPosition(f[0]); c.setPosition(f[1], QTextCursor.KeepAnchor); c.removeSelectedText()
                self.setCurrentCharFormat(QTextCharFormat())
                return
        elif e.text() and e.text().isprintable() and not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier)) and not c.hasSelection():
            nah = self._feld_bei(c.position())
            if "davor" in nah and "dahinter" in nah and nah["davor"] == nah["dahinter"]:     # mitten im Feld: dahinter schreiben
                c.setPosition(nah["davor"][1]); self.setTextCursor(c)
            self.setCurrentCharFormat(QTextCharFormat())              # Tippen neben dem Feld erbt dessen Hintergrund nicht
        super().keyPressEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self.viewport())
        pen = QPen(QColor("#9a9a9a")); pen.setStyle(Qt.DashLine); pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(self.viewport().rect().adjusted(0, 0, -1, -1))


class _Leiste(QWidget):
    """Die schwebende Leiste neben dem Etikett des aktiven Bereichs: mit Seitenzahl drei Knöpfe, ohne nur „Seitenzahl einfügen“."""

    def __init__(self, eltern):
        super().__init__(eltern)
        self.setObjectName("kfLeiste")
        h = self.h = FlussLayout(4); self.setLayout(h); h.setContentsMargins(0, 0, 0, 0)    # bricht um, wenn das Blatt zu schmal ist
        self.knopf = {}
        for schl, text, sym in (("neu", "Seitenzahl neu aufbauen", "neu"), ("format", "Seitenzahlenformat", "format"),
                                ("loeschen", "Seitenzahl löschen", "x"), ("einfuegen", "Seitenzahl einfügen", "neu")):
            k = QToolButton(); k.setText(text); k.setIcon(_symbol(sym)); k.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            k.setPopupMode(QToolButton.InstantPopup)
            k.setParent(self); self.knopf[schl] = k
        self.setStyleSheet(LEISTE_STIL)                        # sitzt auf dem weißen Papier: unabhängig vom Thema
        self.zahl_zeigen(True)

    def zahl_zeigen(self, mit: bool) -> None:
        """Mit Seitenzahl: drei Knöpfe; ohne: nur „Seitenzahl einfügen“ (beides linksbündig, direkt neben dem Etikett)."""
        while self.h.count():
            self.h.takeAt(0)
        for schl in ("neu", "format", "loeschen"):
            self.knopf[schl].setVisible(mit)
        self.knopf["einfuegen"].setVisible(not mit)
        for k in self.knopf.values():                           # nur Sichtbares im Fluss, sonst entstehen Lücken
            if not k.isHidden():
                self.h.addWidget(k)

    def natuerliche_breite(self) -> int:
        ks = [self.h.itemAt(i).widget() for i in range(self.h.count())]
        return sum(k.sizeHint().width() for k in ks) + 4 * max(0, len(ks) - 1)


class KopfFussBearbeiter(QObject):
    gestartet = Signal(); beendet = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.ed = editor
        self.aktiv = False
        self.zone = "kopf"
        self.blatt = 0
        self.leiste = self.absatz = self.panel = None
        self.felder, self.linien, self.etiketten = {}, {}, {}
        self._laedt = False
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
                self.linien[z] = _Linie(vp)
                et = self.etiketten[z] = QLabel("Kopfzeile" if z == "kopf" else "Fußzeile", vp)
                et.setStyleSheet(ETIKETT_STIL); et.setContentsMargins(6, 2, 6, 2)
            self.leiste = _Leiste(vp)
            from lunivo_writer.ui.widgets import icons
            self.absatz = QToolButton(vp); self.absatz.setText("Absatz"); self.absatz.setIcon(icons.icon("pilcrow", 16)); self.absatz.setStyleSheet(ABSATZ_STIL); self.absatz.setObjectName("kfAbsatz")
            self.absatz.setPopupMode(QToolButton.InstantPopup); self.absatz.setToolTip("Absatz")
            vp.installEventFilter(self)
            self._menues()
        self.aktiv = True
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
        from lunivo_writer.editor import abschnitte as AB
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
        page = self.ed.abschnitt_seite()
        n = SZ.erste_nummer(page) + self.blatt
        zahlen = {"PAGE": SZ.nummer(n, page), "PAGES": str(max(1, int(getattr(self.ed, "_pages", 1) or 1)))}
        for z in ZONEN:
            hf = self.hf(page, z)
            self._laedt = True
            self.felder[z].felder_setzen(hf.text, zahlen)
            self._laedt = False
            self._ausrichten(z, hf.align)
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
        bf = c.blockFormat(); bf.setAlignment(al); c.setBlockFormat(bf)

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
                setattr(page, self._name(page, z), HeaderFooter(text, hf.align)); geaendert = True
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
            setattr(page, self._name(page), HeaderFooter(hf.text, align))
        self.aendern(f)

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
            if feld.geometry() != g:
                feld.setGeometry(g)
            if feld.font() != f:
                feld.setFont(f)
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
        except RuntimeError:                                    # Editor beim Beenden schon abgebaut
            pass
        return False

    # ---- Menüs -------------------------------------------------------------------------------------------------------
    def _menues(self) -> None:
        k = self.leiste.knopf
        m = MenueListe(self.leiste); k["neu"].setMenu(m); m.aboutToShow.connect(lambda m=m: self._menue_neu(m))
        m = MenueListe(self.leiste); k["format"].setMenu(m); m.aboutToShow.connect(lambda m=m: self._menue_format(m))
        m = MenueListe(self.leiste); k["loeschen"].setMenu(m); m.aboutToShow.connect(lambda m=m: self._menue_loeschen(m))
        self.panel = _EinfuegenPanel(self.leiste); k["einfuegen"].setMenu(self.panel)
        self.panel.aboutToShow.connect(lambda: self.panel.ort_setzen(self.zone))
        self.panel.uebernommen.connect(self.seitenzahl_einfuegen)
        m = MenueListe(self.absatz); self.absatz.setMenu(m)
        m.eintrag("Absatzformat zurücksetzen", lambda: self.ausrichtung_setzen("center"))
        m.eintrag("Symbol vom Absatz-Layout ausblenden", self.absatz.hide)

    def _menue_neu(self, m: MenueListe) -> None:
        m.clear()
        page = self.ed.abschnitt_seite()
        # Wie die Vorlage: Beschriftung und kleines Zahlfeld nebeneinander, hell wie das übrige Aufklappfeld auf dem Papier
        zeile = QWidget(); zeile.setObjectName("seitennummerierung")
        zeile.setStyleSheet("#seitennummerierung { background: #ffffff; } QLabel { color: #333333; background: transparent; }"
                            " QDoubleSpinBox { background: #ffffff; color: #000000; border: 1px solid #b8b8b8; border-radius: 2px;"
                            " padding: 1px 2px; selection-background-color: #3e78d0; selection-color: #ffffff; }")
        lay = QHBoxLayout(zeile); lay.setContentsMargins(8, 4, 8, 4); lay.setSpacing(6)
        lay.addWidget(QLabel("Seitennummerierung:"))
        sp = QDoubleSpinBox(); sp.setDecimals(0); sp.setRange(1, 99999); sp.setValue(SZ.erste_nummer(page)); sp.setFixedWidth(64)
        sp.setAccessibleName("Seitennummerierung")
        sp.editingFinished.connect(lambda: self._start_setzen(int(sp.value())))
        lay.addWidget(sp); lay.addStretch(1)
        a = QWidgetAction(m); a.setDefaultWidget(zeile); m.addAction(a)
        m.eintrag("Nummerierung fortsetzen", lambda: self._start_setzen(0), aktiv=page.seiten_start > 0)

    def seitenzahl_einfuegen(self, ausr: str, muster: str, zahl: str, bereich: str) -> None:
        """Seitenzahl in die Zeile setzen, die gerade bearbeitet wird („Seitenzahl einfügen ▾“); ``bereich``: dokument | seite | abschnitt."""
        from lunivo_writer.editor import abschnitte as AB
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
        from lunivo_writer.editor import abschnitte as AB
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
