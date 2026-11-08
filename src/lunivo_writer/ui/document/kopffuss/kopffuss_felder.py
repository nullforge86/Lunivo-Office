"""Bausteine des Kopf-/Fußzeilen-Bearbeiters: Konstanten, Stile und die vier Qt-Elemente (Linie, Einfügen-Panel, Textfeld, Leiste).

Die Steuerung (``KopfFussBearbeiter``) liegt in ``kopffuss_bearbeiter.py``. Kein HTML."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
import re

from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPen, QPixmap, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
                               QRadioButton, QToolButton, QVBoxLayout, QWidget)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.seite import seitenzahl as SZ
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.controls.formular_gitter import FlussLayout
from lunivo_writer.ui.baukasten.controls.karten_raster import kachel_gitter
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_ENG,
    ABSTAND_GROSS,
    ABSTAND_NORMAL,
    GROESSE_EINFUEGKNOPF,
    GROESSE_EINFUEGKNOPF_BILD,
    PADDING_KOPFFUSS_PANELKNOPF,
    PADDING_KOPFFUSS_PANELTASTE,
    RADIUS_LEISTENKNOPF,
    RADIUS_RUNDE_OPTION,
    RAND_EINFUEGEN_PANEL,
    RAND_KEIN,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf

ZONEN = ("kopf", "fuss")
_FLAG = {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}
FELD_EIGENSCHAFT = int(QTextFormat.UserProperty) + 1          # in der Zeichenformatierung: "PAGE" oder "PAGES" (das Feld, das die Zahl zeigt)
_FELDER = re.compile(r"\{(PAGES|PAGE)\}")
FORMATE = [("dezimal", "1, 2, 3 …"), ("klein", "a, b, c …"), ("gross", "A, B, C …"), ("roem_klein", "i, ii, iii …"), ("roem_gross", "I, II, III …")]


_ETIKETT_STIL = "QLabel { background: @LEISTE; color: @GRAU; border: 1px dashed @GRAU; }"
_PANEL_STIL = """
QWidget#kfPanel { background: @PAPIER; color: @TINTE; }
#kfPanel QLabel, #kfPanel QRadioButton { color: @TINTE; background: transparent; }
#kfPanel QToolButton { background: @LEISTE; color: @TINTE; border: 1px solid transparent; padding: """ f"{PADDING_KOPFFUSS_PANELKNOPF}" """; }
#kfPanel QToolButton:checked { background: @BLAU_HELL; }
#kfPanel QToolButton:hover { border: 1px solid @LEISTE_RAND; }
#kfPanel QRadioButton::indicator { width: 12px; height: 12px; border: 1px solid @GRAU; border-radius: """ f"{RADIUS_RUNDE_OPTION}" """px; background: @PAPIER; }
#kfPanel QPushButton { border: none; border-radius: """ f"{RADIUS_LEISTENKNOPF}" """px; padding: """ f"{PADDING_KOPFFUSS_PANELTASTE}" """; }
"""


def _stil(vorlage: str) -> str:
    """Stylesheet zur Laufzeit aus den Farbe-Tokens bilden (Farbe.* setzt apply_theme erst nach dem Import)."""
    return re.sub(r"@([A-Z_]+)", lambda t: getattr(Farbe, t.group(1)), vorlage)


def etikett_stil() -> str:
    return _stil(_ETIKETT_STIL)


def panel_stil() -> str:
    return _stil(_PANEL_STIL)


def _symbol(art: str) -> QIcon:
    """Aktionssymbol aus dem zentralen Lucide-Katalog."""
    from lunivo_writer.ui.widgets import icons
    return icons.icon({"x": "x", "neu": "file-plus", "format": "file-text"}.get(art, "file"), 16, Farbe.SYMBOL)           # die Knöpfe sind hell (Papier): dunkles Symbol in jedem Thema


class _Linie(QWidget):
    """Gestrichelte graue Linie über die ganze Blattbreite, an der der Kopf-/Fußbereich endet."""

    def __init__(self, eltern):
        super().__init__(eltern)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, e):
        p = QPainter(self)
        pen = QPen(QColor(Farbe.GRAU)); pen.setStyle(Qt.DashLine); p.setPen(pen)
        p.drawLine(0, self.height() // 2, self.width(), self.height() // 2)


from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe


class _EinfuegenPanel(MenueListe):
    """Aufklappfeld „Seitenzahl einfügen“: Format, Position (fünf Kacheln mit Seitenbildchen), Übernehmen für, OK."""
    uebernommen = Signal(str, str, str, str)          # Ausrichtung, Muster, Zahlenart, Bereich (dokument | seite | abschnitt)
    POS = [("left", "Links"), ("center", "Zentriert"), ("right", "Rechts"), ("aussen", "Außen"), ("innen", "Innen")]

    def __init__(self, eltern):
        super().__init__(eltern)
        self.ort = "kopf"
        w = QWidget(); w.setObjectName("kfPanel"); w.setStyleSheet(panel_stil())
        v = QVBoxLayout(w); v.setContentsMargins(*RAND_EINFUEGEN_PANEL); v.setSpacing(ABSTAND_NORMAL)
        self.format = Auswahlfeld(); self.format.setAccessibleName("Format")
        for muster, zahl, text in SZ.MUSTER:
            self.format.addItem("Format: " + text, (muster, zahl))
        v.addWidget(self.format)
        v.addWidget(QLabel("Position:"))
        kacheln = []
        self.gruppe = QButtonGroup(self); self.gruppe.setExclusive(True)
        self.kacheln = {}
        for i, (schl, text) in enumerate(self.POS):
            k = QToolButton(); k.setCheckable(True); k.setText(text); k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            k.setIconSize(QSize(*GROESSE_EINFUEGKNOPF_BILD)); k.setMinimumSize(*GROESSE_EINFUEGKNOPF); k.setAccessibleName(text)
            self.gruppe.addButton(k); self.kacheln[schl] = k
            kacheln.append(k)
        self.kacheln["center"].setChecked(True)
        v.addLayout(kachel_gitter(kacheln, 3, abstand=ABSTAND_ENG))
        v.addWidget(QLabel("Übernehmen für:"))
        r = QHBoxLayout(); r.setSpacing(ABSTAND_GROSS)
        self.bereich = {}
        for schl, text in (("dokument", "Gesamtes Dokument"), ("seite", "Von aktueller Seite"), ("abschnitt", "Aktueller Abschnitt")):
            b = QRadioButton(text); self.bereich[schl] = b; r.addWidget(b)
        self.bereich["dokument"].setChecked(True)
        v.addLayout(r)
        ok = QPushButton("OK"); ok.clicked.connect(self._ok)
        z = QHBoxLayout(); z.addStretch(1); z.addWidget(ok); v.addLayout(z)
        self.widget(w)

    def ort_setzen(self, ort: str) -> None:
        from lunivo_writer.ui.baukasten.medien.seiten_bildchen import seitenzahl_zeichner
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


class _Feld(QPlainTextEdit):
    """Das Textfeld über dem Kopf- bzw. Fußbereich: randlos, gestrichelter Rahmen, Esc beendet."""
    schliessen = Signal()
    fokus = Signal(str)                                           # bekommt die Schreibmarke: "kopf" oder "fuss"

    def __init__(self, eltern, zone: str = "kopf"):
        super().__init__(eltern)
        self.zone = zone
        self.setFrameShape(QPlainTextEdit.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAccessibleName("Kopfzeile" if zone == "kopf" else "Fußzeile")
        # Das Feld steht auf dem weißen Papier: Farben unabhängig vom Programm-Thema (Papier, schwarzer Text, sichtbare Schreibmarke)
        pal = QPalette(self.palette())
        for gr in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            pal.setColor(gr, QPalette.Base, QColor(Farbe.PAPIER)); pal.setColor(gr, QPalette.Window, QColor(Farbe.PAPIER))
            pal.setColor(gr, QPalette.Text, QColor(Farbe.SCHWARZ)); pal.setColor(gr, QPalette.WindowText, QColor(Farbe.SCHWARZ))
            pal.setColor(gr, QPalette.Highlight, QColor(Farbe.AKZENT)); pal.setColor(gr, QPalette.HighlightedText, QColor(Farbe.AUF_AKZENT))
        self.setPalette(pal)
        self.setStyleSheet(_stil("QPlainTextEdit { background: @PAPIER; color: @SCHWARZ; border: none; selection-background-color: palette(highlight); selection-color: palette(highlighted-text); }"))
        self.setCursorWidth(1)
        self.basis = QTextCharFormat()                            # das Zeichenformat der ganzen Zeile (Schrift, Größe, F/K/U, Farbe)

    # ---- Felder: {PAGE}/{PAGES} stehen als Zahl mit Hintergrund im Text und werden beim Speichern wieder zu {PAGE}/{PAGES} ----
    @staticmethod
    def _feld_format(art: str) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setProperty(FELD_EIGENSCHAFT, art)
        f.setBackground(QColor(Farbe.GITTER))
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
                self.setCurrentCharFormat(self.basis)
                return
        elif e.text() and e.text().isprintable() and not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier)) and not c.hasSelection():
            nah = self._feld_bei(c.position())
            if "davor" in nah and "dahinter" in nah and nah["davor"] == nah["dahinter"]:     # mitten im Feld: dahinter schreiben
                c.setPosition(nah["davor"][1]); self.setTextCursor(c)
            self.setCurrentCharFormat(self.basis)                     # Tippen neben dem Feld erbt dessen Hintergrund nicht
        super().keyPressEvent(e)

    def _effekte_zeichnen(self, p: QPainter) -> None:
        """Schatten, Spiegelung, Leuchten usw. (``editor/text/textfx.py``) an der Stelle, an der das Feld den Text zeichnet. Das Feld setzt seine Blöcke
        selbst (``blockBoundingGeometry``), die Schreibweise des Dokumenteditors (Ursprung der Textzeile) trifft hier nicht zu."""
        from lunivo_writer.editor.text import textfx
        p.setRenderHint(QPainter.Antialiasing)
        b = self.firstVisibleBlock()
        while b.isValid():
            tl = b.layout()
            if tl is not None and tl.lineCount():
                ziel = self.blockBoundingGeometry(b).translated(self.contentOffset()).topLeft()
                p.save(); p.translate(ziel - tl.position())
                it = b.begin()
                while not it.atEnd():
                    fr = it.fragment(); cf = fr.charFormat()
                    if fr.isValid() and textfx.hat_zeichen_effekt(cf):
                        textfx._stueck(p, b, tl, fr.position() - b.position(), fr.length(), cf, textfx.aus_text(cf.stringProperty(textfx._P("P_EFFEKT"))))
                    it += 1
                p.restore()
            b = b.next()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self.viewport())
        self._effekte_zeichnen(p)
        pen = QPen(QColor(Farbe.GRAU)); pen.setStyle(Qt.DashLine); pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(self.viewport().rect().adjusted(0, 0, -1, -1))


class _Leiste(QWidget):
    """Die schwebende Leiste neben dem Etikett des aktiven Bereichs: mit Seitenzahl drei Knöpfe, ohne nur „Seitenzahl einfügen“."""

    def __init__(self, eltern):
        super().__init__(eltern)
        self.setObjectName("kfLeiste")
        h = self.h = FlussLayout(4); self.setLayout(h); h.setContentsMargins(*RAND_KEIN)    # bricht um, wenn das Blatt zu schmal ist
        self.knopf = {}
        for schl, text, sym in (("neu", "Seitenzahl neu aufbauen", "neu"), ("format", "Seitenzahlenformat", "format"),
                                ("loeschen", "Seitenzahl löschen", "x"), ("einfuegen", "Seitenzahl einfügen", "neu")):
            k = DropdownKnopf(); k.setText(text); k.setIcon(_symbol(sym)); k.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            k.setParent(self); self.knopf[schl] = k
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
