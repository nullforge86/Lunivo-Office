"""Hilfe: Handbuch, Tastenkürzel, Erweiterungen."""
from __future__ import annotations

import os
from lunivo_writer.ui.baukasten.basis.texte import hinweis_stil
from lunivo_writer.core import paths

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.basis.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.geruest.einklappgruppe import EinklappGruppe
from lunivo_writer.ui.baukasten.controls.formular_gitter import FormularGitter, abschnittstitel
from lunivo_writer.ui.baukasten.geruest.spalten import ZweiSpalter
from lunivo_writer.ui.baukasten.geruest.zusatz_panel import PanelFaehig

from lunivo_writer.ui import kuerzel




from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_BLOCK,
    ABSTAND_ENG,
    ABSTAND_MITTEL,
    ABSTAND_NORMAL,
    BREITE_NAVIGATION_HILFE,
    GROESSE_FENSTER_HANDBUCH,
    GROESSE_PLAKETTE,
    HOEHE_LESEFELD,
    HOEHE_NAVIGATION_HILFE,
    HOEHE_ZEILE_ABSCHNITT,
    HOEHE_ZEILE_ERWEITERUNG_KOPF,
    PADDING_HANDBUCH_EINTRAG,
    PADDING_HANDBUCH_NAVIGATION,
    RADIUS_EINTRAG,
    RADIUS_FELD,
    RADIUS_MITTEL,
    RAND_ERWEITERUNG_KARTE,
    RAND_HILFE_DIALOG,
    RAND_HILFE_FUSS,
    RAND_HILFE_SEITE,
    RAND_KEIN,
)
def _browser(parent, titel: str, breite=860, hoehe=640) -> tuple[QDialog, QTextBrowser, QVBoxLayout]:
    d = QDialog(parent)
    d.setWindowTitle(titel)
    d.resize(breite, hoehe)
    v = QVBoxLayout(d)
    b = QTextBrowser()
    b.setOpenExternalLinks(True)
    v.addWidget(b, 1)
    return d, b, v


GRUPPEN = [("Anfangen", ["Das erste Blatt", "Mehrere Dokumente", "Die Oberfläche einrichten", "Das ☰ Menü"]),
           ("Schreiben", ["Text und Gestaltung", "Die rechte Maustaste", "Formatvorlagen", "Die Seite"]),
           ("Was hilft", ["Die Schreibhilfe", "Für wen? — Themenwörter", "Die Lesehilfe", "Vorlesen"]),
           ("Bausteine", ["Textbausteine", "Eigene Bausteine", "Vorlagen"]),
           ("Heraus", ["Speichern", "Drucken"]),
           ("Nachschlagen", ["Woher es kommt", "Tastenkürzel", "Wo was liegt", "Wenn etwas klemmt"])]


class HilfeFenster(PanelFaehig, QDialog):
    """Hilfefenster (Handbuch, Tastenkürzel, Erweiterungen, Über): öffnet mit ``exec()`` in der Seitenleiste."""


class _Lesefeld(QTextBrowser):
    """Der Text des Handbuchs in einer ruhigen Spalte: nicht breiter als ~780 px, die Spalte steht in der Mitte (schmal: kleiner Rand)."""
    BREITE = 780

    def resizeEvent(self, e):
        super().resizeEvent(e)
        rand = max(28 if self.width() > 520 else 12, (self.width() - self.BREITE) // 2)
        self.setViewportMargins(0, 0, 0, 0)
        self.document().setDocumentMargin(rand)


def _hb_bloecke(d, grund2) -> None:
    """Absätze und Überschriften: Abstände, Zeilenhöhe, Merkkästen."""
    from PySide6.QtGui import QBrush, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor
    blk = d.begin()
    while blk.isValid():
        cf = QTextCharFormat()
        ebene = blk.blockFormat().headingLevel()
        bf = blk.blockFormat()
        if ebene:
            bf.setTopMargin({1: 6, 2: 34, 3: 20}.get(ebene, 14)); bf.setBottomMargin({1: 4, 2: 10, 3: 6}.get(ebene, 6))
            cf.setFontPointSize({1: 30, 2: 21, 3: 15}.get(ebene, 13)); cf.setFontWeight(QFont.Bold)
            cf.setFontFamilies(["Georgia", "Liberation Serif", "serif"])
        else:
            bf.setLineHeight(128.0, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
            if blk.blockFormat().intProperty(0x1080) == 0 and not blk.textList():
                bf.setBottomMargin(10)
        if blk.blockFormat().intProperty(0x1080):
            bf.setBackground(QBrush(grund2)); bf.setLeftMargin(10); bf.setRightMargin(6); bf.setTopMargin(4); bf.setBottomMargin(4)
            bf.setIndent(0)
        QTextCursor(blk).setBlockFormat(bf)
        if ebene:
            cur2 = QTextCursor(blk); cur2.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor); cur2.mergeCharFormat(cf)
        blk = blk.next()


def _hb_tastenchips(d, grund2) -> None:
    """Tastenchips und Wege (Schrift mit fester Breite)."""
    from PySide6.QtGui import QBrush, QTextCharFormat, QTextCursor
    blk = d.begin()
    while blk.isValid():
        it = blk.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().fontFixedPitch():
                cur = QTextCursor(d); cur.setPosition(f.position()); cur.setPosition(f.position() + f.length(), QTextCursor.KeepAnchor)
                cf = QTextCharFormat(); cf.setBackground(QBrush(grund2)); cf.setFontFamilies(["DejaVu Sans Mono", "Liberation Mono", "monospace"]); cf.setFontPointSize(10.5)
                cur.mergeCharFormat(cf)
            it += 1
        blk = blk.next()


def _hb_tabellen(d, linie) -> None:
    """Tabellen: kein Gitter, nur feine Linien zwischen den Zeilen; leere Kopfzeile fällt weg."""
    from PySide6.QtGui import QBrush, QTextFrameFormat, QTextLength, QTextTable
    tabellen = [fr for fr in d.rootFrame().childFrames() if isinstance(fr, QTextTable)]
    for t in tabellen:
        if all(not t.cellAt(0, k).firstCursorPosition().block().text().strip() for k in range(t.columns())):
            t.removeRows(0, 1)
        tf = t.format()
        tf.setBorder(0); tf.setCellPadding(9); tf.setCellSpacing(0); tf.setBorderCollapse(True)
        tf.setTopMargin(6); tf.setBottomMargin(14)
        tf.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        if t.columns() == 2:
            tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 34), QTextLength(QTextLength.PercentageLength, 66)])
        t.setFormat(tf)
        for r in range(t.rows()):
            for k in range(t.columns()):
                cell = t.cellAt(r, k); cf = cell.format().toTableCellFormat()
                cf.setBorder(0); cf.setBorderBrush(QBrush(linie)); cf.setBottomBorder(1); cf.setBottomBorderStyle(QTextFrameFormat.BorderStyle_Solid)
                cf.setBottomBorderBrush(QBrush(linie))
                cell.setFormat(cf)


def _handbuch_gestalten(b: QTextBrowser) -> None:
    """Gibt dem Markdown-Text die Gestalt der Vorlage: Antiqua mit Luft, Überschriften, Tabellen ohne Gitter, Merkkästen, Tastenchips."""
    from PySide6.QtGui import QColor, QFont, QPalette
    d = b.document()
    pal = b.palette()
    linie = pal.color(QPalette.Mid); linie.setAlpha(90)
    grund2 = QColor(pal.color(QPalette.Text)); grund2.setAlpha(18)
    serif = QFont("Georgia"); serif.setStyleHint(QFont.Serif); serif.setPointSizeF(12.5)
    d.setDefaultFont(serif)
    _hb_bloecke(d, grund2)
    _hb_tastenchips(d, grund2)
    _hb_tabellen(d, linie)


def handbuch(parent) -> QDialog:
    """Das Handbuch: oben die Gliederung (Gruppen, Abschnitte), darunter der Text. Er liegt als Markdown in resources/handbuch.md."""
    from PySide6.QtCore import QSize
    from PySide6.QtWidgets import QListWidget, QListWidgetItem
    d = HilfeFenster(parent)
    d.setWindowTitle("Handbuch"); d.resize(*GROESSE_FENSTER_HANDBUCH)
    v = QVBoxLayout(d); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_NORMAL)
    # Schmal: oben die Gliederung (einklappbar), darunter Suche und Text. Breit (ZweiSpalter): Gliederung links, Suche und Text rechts
    themen = EinklappGruppe("Themen")
    themen.setContentsMargins(*RAND_HILFE_SEITE)
    nav = QListWidget(); nav.setMaximumHeight(HOEHE_NAVIGATION_HILFE); nav.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded); nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); nav.setFrameShape(QFrame.NoFrame); nav.setFocusPolicy(Qt.StrongFocus); nav.setAccessibleName("Handbuch-Abschnitte")
    nav.setObjectName("hilfeNav")
    nav.setStyleSheet("QListWidget { background: palette(window); border: 1px solid palette(midlight); border-radius: " f"{RADIUS_FELD}" "px; padding: " f"{PADDING_HANDBUCH_NAVIGATION}" "; outline: none; }"
                      "QListWidget::item { padding: " f"{PADDING_HANDBUCH_EINTRAG}" "; border-radius: " f"{RADIUS_EINTRAG}" "px; }"
                      "QListWidget::item:selected { background: palette(midlight); color: palette(window-text); }")
    themen.innen.addWidget(nav)
    themen.ausklappen(True)
    rechts = QWidget(); rv = QVBoxLayout(rechts); rv.setContentsMargins(*RAND_KEIN); rv.setSpacing(ABSTAND_NORMAL)
    spalten = ZweiSpalter(themen, rechts, links_breite=BREITE_NAVIGATION_HILFE, oben="links", abstand=ABSTAND_NORMAL)
    d.spalten = spalten
    v.addWidget(spalten, 1)

    def angeordnet(breit: bool) -> None:                                 # breit steht die Liste immer offen und so hoch wie das Fenster
        themen.knopf.setVisible(not breit)
        if breit:
            themen.ausklappen(True)
        nav.setMaximumHeight(16777215 if breit else HOEHE_NAVIGATION_HILFE)
    spalten.angeordnet.connect(angeordnet)
    such = QLineEdit(); such.setPlaceholderText("Im Handbuch suchen …"); such.setClearButtonEnabled(True)
    such.setContentsMargins(*RAND_KEIN)
    sz = QHBoxLayout(); sz.setContentsMargins(*RAND_HILFE_SEITE); sz.addWidget(such, 1)
    rv.addLayout(sz)
    b = _Lesefeld(); b.setOpenExternalLinks(True); b.setFrameShape(QFrame.NoFrame); b.setMinimumHeight(HOEHE_LESEFELD)
    with open(os.path.join(paths.RESSOURCEN, "handbuch.md"), encoding="utf-8") as fh:
        b.setMarkdown(fh.read())
    _handbuch_gestalten(b)
    rv.addWidget(b, 1)
    fz = QVBoxLayout(); fz.setContentsMargins(*RAND_HILFE_FUSS); fussleiste(d, fz, nur_ok=True, ok_text="Schließen")
    v.addLayout(fz)

    stellen = {}
    blk = b.document().begin()
    while blk.isValid():
        if blk.blockFormat().headingLevel() in (2, 3):
            stellen.setdefault(blk.text().strip(), blk)
            if blk.text().strip() == "Woher dieses Programm kommt":          # die Gliederung nennt es kürzer
                stellen.setdefault("Woher es kommt", blk)
        blk = blk.next()
    ueber_kopf = QListWidgetItem("Lunivo Writer\nEin Raum für Worte — das Handbuch"); ueber_kopf.setData(Qt.UserRole, "")
    f = ueber_kopf.font(); f.setBold(True); ueber_kopf.setFont(f); ueber_kopf.setSizeHint(QSize(0, HOEHE_ZEILE_ERWEITERUNG_KOPF))
    nav.addItem(ueber_kopf)
    for gruppe, titel in GRUPPEN:
        kopf = QListWidgetItem(gruppe.upper()); kopf.setFlags(Qt.NoItemFlags)
        f = kopf.font(); f.setPointSizeF(8); f.setBold(True); kopf.setFont(f); kopf.setSizeHint(QSize(0, HOEHE_ZEILE_ABSCHNITT))
        nav.addItem(kopf)
        for t in titel:
            if t in stellen:
                it = QListWidgetItem(t); it.setData(Qt.UserRole, t); nav.addItem(it)

    def springe(it):
        t = it.data(Qt.UserRole)
        if t == "":
            b.verticalScrollBar().setValue(0)
        elif t in stellen:
            lay = b.document().documentLayout()
            b.verticalScrollBar().setValue(int(lay.blockBoundingRect(stellen[t]).top()) - 8)
    nav.itemClicked.connect(springe)
    nav.currentItemChanged.connect(lambda cur, _vor: springe(cur) if cur is not None else None)       # Pfeiltasten springen mit
    such.returnPressed.connect(lambda: b.find(such.text()) or (b.moveCursor(b.textCursor().Start), b.find(such.text())))
    return d


def _fuss(d: QDialog, v: QVBoxLayout) -> None:
    """Knopfzeile unten („Schließen“); in der Seitenleiste bleibt sie angeheftet."""
    fussleiste(d, v, nur_ok=True, ok_text="Schließen")


def _titel(text: str) -> QLabel:
    t = QLabel(text); f = t.font(); f.setPointSize(f.pointSize() + 3); f.setBold(True); t.setFont(f)
    return t


def _dialog(parent, titel: str, breite: int) -> tuple[QDialog, QVBoxLayout]:
    d = HilfeFenster(parent); d.setWindowTitle(titel)
    if breite: d.setMinimumWidth(breite)
    v = QVBoxLayout(d); v.setContentsMargins(*RAND_HILFE_DIALOG); v.setSpacing(ABSTAND_MITTEL)
    v.addWidget(_titel(titel)); v.addSpacing(4)
    return d, v


def tastenkuerzel(parent) -> QDialog:
    """„Tastenkombinationen“: je Gruppe eine Überschrift, darunter zwei Kürzel mit Wirkung nebeneinander."""
    d, v = _dialog(parent, "Tastenkombinationen", 0)
    for gruppe, zeilen in kuerzel.HILFE:
        v.addWidget(abschnittstitel(gruppe))
        w = QWidget(); g = FormularGitter(w)
        for taste, text in zeilen:
            wirkung = QLabel(text); wirkung.setWordWrap(True)
            t = QLabel(taste); f = t.font(); f.setBold(True); t.setFont(f); t.setWordWrap(True)
            g.zeile(wirkung, t)
        v.addWidget(w)
    v.addStretch(1)
    _fuss(d, v)
    return d


def _erweiterungen_liste() -> list[tuple[bool, str, str, str]]:
    from PySide6.QtGui import QFontDatabase
    from lunivo_writer.services import vorlesen
    from lunivo_writer.services.integrations import languagetool
    schriften = [f for f in ("OpenDyslexic", "Lexend", "Atkinson Hyperlegible") if f.lower() in {x.lower() for x in QFontDatabase.families()}]
    return [(bool(languagetool.verfuegbar()), "LanguageTool", "„Gründlich prüfen“ — Grammatik über die eigenen Regeln hinaus", "ca. 386 MB"),
            (bool(vorlesen.piper_da()), "Stimmen zum Vorlesen", "aufgenommene Stimmen statt der blechernen des Systems", "ca. 439 MB"),
            (len(schriften) == 3, f"Schriften zum leichteren Lesen ({len(schriften)}/3)", "OpenDyslexic, Lexend, Atkinson Hyperlegible", "ca. 1 MB")]


def erweiterungen(parent) -> QDialog:
    """„Erweiterungen“: jede Karte zeigt mit „DA“, ob der Teil schon geholt ist."""
    d, v = _dialog(parent, "Erweiterungen", 0)
    hin = QLabel("Drei Teile liegen außerhalb des Programms, weil sie zu groß sind. Sie werden geholt, wenn sie zum ersten Mal gebraucht werden — "
                 "und ohne sie läuft alles Übrige weiter: Schreiben, Prüfen.")
    hin.setWordWrap(True); v.addWidget(hin)
    for da, name, text, groesse in _erweiterungen_liste():
        karte = QFrame(); karte.setObjectName("erwKarte")
        karte.setStyleSheet("QFrame#erwKarte { border: 1px solid palette(midlight); border-radius: " f"{RADIUS_MITTEL}" "px; }")
        h = QHBoxLayout(karte); h.setContentsMargins(*RAND_ERWEITERUNG_KARTE); h.setSpacing(ABSTAND_BLOCK)
        b = QLabel("DA" if da else "—"); b.setAlignment(Qt.AlignCenter); b.setFixedSize(*GROESSE_PLAKETTE)
        b.setStyleSheet("background: %s; color: %s; border-radius: " f"{RADIUS_EINTRAG}" "px; font-weight: 700;" % (Farbe.AN if da else Farbe.GRAU, Farbe.AN_SCHRIFT))
        mitte = QVBoxLayout(); mitte.setSpacing(ABSTAND_ENG)
        n = QLabel(name); n.setWordWrap(True); f = n.font(); f.setBold(True); n.setFont(f)
        t = QLabel(text); t.setWordWrap(True); f = t.font(); f.setItalic(True); t.setFont(f); hinweis_stil(t)
        mitte.addWidget(n); mitte.addWidget(t)
        h.addWidget(b); h.addLayout(mitte, 1)
        g = QLabel(groesse); hinweis_stil(g); h.addWidget(g, 0, Qt.AlignTop)
        v.addWidget(karte)
    fuss = QLabel("Erweiterungen von fremder Hand nimmt dieses Programm nicht an. Was es kann, steckt im Programm.")
    fuss.setWordWrap(True); v.addWidget(fuss)
    v.addStretch(1)
    _fuss(d, v)
    return d


def ueber(parent, version: str) -> QDialog:
    d, v = _dialog(parent, "Über Lunivo Writer", 0)
    for text in (f"Lunivo Writer {version}\nEin Raum für Worte",
                 "Die Prüfung und der Wortschatz stammen aus der Schreibhilfe.\nDOCX, ODT, RTF, TXT und PDF schreibt Lunivo selbst — ohne fremdes Programm im Hintergrund.",
                 "Was geschrieben wird, bleibt auf diesem Rechner.\nNichts geht hinaus, ohne dass du es selbst schickst."):
        l = QLabel(text); l.setWordWrap(True); v.addWidget(l); v.addSpacing(6)
    v.addStretch(1)
    _fuss(d, v)
    return d
