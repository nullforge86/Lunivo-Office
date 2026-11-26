"""Hilfe: Handbuch, Tastenkürzel, Erweiterungen."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein

from vcl.qt.widgets.bausteine.abstaende.raster import RasterSpalte
from writer.anbindung import schriften as standard_datenbank
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_KLEIN as _A_KLEIN

from vcl.qt.widgets.bausteine.farben.darstellung import rolle as _rolle

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import anwenden, raender, reihe as _reihe, spalte as _spalte

from vcl.qt.widgets.bausteine.skalierung.daten import text as _t

import os
from vcl.qt.widgets.bausteine.symbole.bauteile.textfeld_fragmente import absatz_fragmente
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from system.plattform import ressourcen_pfade as pfade

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QLabel, QLineEdit, QPushButton, QTextBrowser, QWidget

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.zustaende.geruest.einklappgruppe import EinklappGruppe
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.zustaende.geruest.spalten import ZweiSpalter
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig

from vcl.qt.widgets.bausteine.tastaturnavigation import kuerzel




from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_HILFE_ABSCHNITT_PT, SCHRIFT_HILFE_SERIF_PT, SCHRIFT_HILFE_TITEL_PLUS_PT
from vcl.qt.widgets.bausteine.schrift.schriftarten import GENERISCH_MONOSPACE, GENERISCH_SERIF
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_BLOCK, ABSTAND_ENG, ABSTAND_MITTEL, ABSTAND_NORMAL, BREITE_NAVIGATION_HILFE, GROESSE_FENSTER_HANDBUCH, GROESSE_PLAKETTE, HOEHE_LESEFELD, HOEHE_NAVIGATION_HILFE, HOEHE_ZEILE_ABSCHNITT, HOEHE_ZEILE_ERWEITERUNG_KOPF, PADDING_HANDBUCH_EINTRAG, PADDING_HANDBUCH_NAVIGATION, RADIUS_EINTRAG, RADIUS_FELD, RADIUS_MITTEL, RAND_ERWEITERUNG_KARTE, RAND_HILFE_DIALOG, RAND_HILFE_FUSS, RAND_HILFE_SEITE, RAND_KEIN



GRUPPEN = [(_t("hilfe.anfangen"), [_t("hilfe.das_erste_blatt"), _t("hilfe.mehrere_dokumente"), _t("hilfe.die_oberflaeche_einrichten"), _t("hilfe.das_menue")]),
           (_t("hilfe.schreiben"), [_t("hilfe.text_und_gestaltung"), _t("hilfe.die_rechte_maustaste"), _t("hilfe.formatvorlagen"), _t("hilfe.die_seite")]),
           (_t("hilfe.was_hilft"), [_t("hilfe.die_schreibhilfe"), _t("hilfe.fuer_wen_themenwoerter"), _t("hilfe.die_lesehilfe"), _t("hilfe.vorlesen")]),
           (_t("hilfe.bausteine"), [_t("hilfe.textbausteine"), _t("hilfe.eigene_bausteine"), _t("hilfe.vorlagen")]),
           (_t("hilfe.heraus"), [_t("hilfe.speichern"), _t("hilfe.drucken")]),
           (_t("hilfe.nachschlagen"), [_t("hilfe.woher_es_kommt"), _t("hilfe.tastenkuerzel"), _t("hilfe.wo_was_liegt"), _t("hilfe.wenn_etwas_klemmt")])]


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
            cf.setFontFamilies([_t("hilfe.georgia"), _t("hilfe.liberation_serif"), GENERISCH_SERIF])
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
        for f in absatz_fragmente(blk):
            if f.charFormat().fontFixedPitch():
                cur = QTextCursor(d); cur.setPosition(f.position()); cur.setPosition(f.position() + f.length(), QTextCursor.KeepAnchor)
                cf = QTextCharFormat(); cf.setBackground(QBrush(grund2)); cf.setFontFamilies([_t("hilfe.dejavu_sans_mono"), _t("hilfe.liberation_mono"), GENERISCH_MONOSPACE]); cf.setFontPointSize(10.5)
                cur.mergeCharFormat(cf)
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
    serif = QFont(_t("hilfe.georgia")); serif.setStyleHint(QFont.Serif); serif.setPointSizeF(SCHRIFT_HILFE_SERIF_PT)
    d.setDefaultFont(serif)
    _hb_bloecke(d, grund2)
    _hb_tastenchips(d, grund2)
    _hb_tabellen(d, linie)


def handbuch_inhalt() -> QWidget:
    """Der Inhalt des Handbuchs (ohne Fenster): Gliederung, Suche und Text. Er liegt als Markdown in ressourcen/handbuch.md. Das Dashboard zeigt ihn als Seite,
    ``handbuch(parent)`` als Fenster."""
    from PySide6.QtCore import QSize
    from PySide6.QtWidgets import QListWidget, QListWidgetItem
    d = QWidget()
    v = _spalte("standard", d)
    # Schmal: oben die Gliederung (einklappbar), darunter Suche und Text. Breit (ZweiSpalter): Gliederung links, Suche und Text rechts
    themen = EinklappGruppe(_t("hilfe.themen"))
    raender(themen, "rand_seitlich")
    nav = QListWidget(); nav.setMaximumHeight(HOEHE_NAVIGATION_HILFE); nav.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded); nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); nav.setFrameShape(QFrame.NoFrame); nav.setFocusPolicy(Qt.StrongFocus); nav.setAccessibleName(_t("hilfe.handbuch_abschnitte"))
    nav.setObjectName("hilfeNav")
    themen.innen.addWidget(nav)
    themen.ausklappen(True)
    rechts = QWidget(); rv = _spalte("standard", rechts)
    spalten = ZweiSpalter(themen, rechts, links_breite=BREITE_NAVIGATION_HILFE, oben="links", abstand=ABSTAND_NORMAL)
    d.spalten = spalten
    v.addWidget(spalten, 1)

    def angeordnet(breit: bool) -> None:                                 # breit steht die Liste immer offen und so hoch wie das Fenster
        themen.knopf.setVisible(not breit)
        if breit:
            themen.ausklappen(True)
        nav.setMaximumHeight(16777215 if breit else HOEHE_NAVIGATION_HILFE)
    spalten.angeordnet.connect(angeordnet)
    such = zeilenfeld("frei", platzhalter=_t("hilfe.im_handbuch_suchen")); such.setClearButtonEnabled(True)
    raender(such, "kein")
    sz = _reihe("rand_seitlich"); sz.addWidget(such, 1)
    rv.addLayout(sz)
    b = _Lesefeld(); b.setOpenExternalLinks(True); b.setFrameShape(QFrame.NoFrame); b.setMinimumHeight(HOEHE_LESEFELD)
    try:
        with open(os.path.join(pfade.RESSOURCEN, "handbuch.md"), encoding="utf-8") as fh:
            b.setMarkdown(fh.read())
    except OSError:
        b.setMarkdown(_t("hilfe.das_handbuch_konnte_nicht_gelesen_werden"))
    _handbuch_gestalten(b)
    rv.addWidget(b, 1)

    stellen = {}
    blk = b.document().begin()
    while blk.isValid():
        if blk.blockFormat().headingLevel() in (2, 3):
            stellen.setdefault(blk.text().strip(), blk)
            if blk.text().strip() == _t("hilfe.woher_dieses_programm_kommt"):          # die Gliederung nennt es kürzer
                stellen.setdefault(_t("hilfe.woher_es_kommt"), blk)
        blk = blk.next()
    ueber_kopf = QListWidgetItem(_t("hilfe.lunivo_writer_ein_raum_fuer_worte_das_ha")); ueber_kopf.setData(Qt.UserRole, "")
    f = ueber_kopf.font(); f.setBold(True); ueber_kopf.setFont(f); ueber_kopf.setSizeHint(QSize(0, HOEHE_ZEILE_ERWEITERUNG_KOPF))
    nav.addItem(ueber_kopf)
    for gruppe, titel in GRUPPEN:
        kopf = QListWidgetItem(gruppe.upper()); kopf.setFlags(Qt.NoItemFlags)
        f = kopf.font(); f.setPointSizeF(SCHRIFT_HILFE_ABSCHNITT_PT); f.setBold(True); kopf.setFont(f); kopf.setSizeHint(QSize(0, HOEHE_ZEILE_ABSCHNITT))
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


def handbuch(parent) -> QDialog:
    """Das Handbuch als Fenster (öffnet mit ``exec()`` in der Seitenleiste)."""
    d = HilfeFenster(parent)
    d.setWindowTitle(_t("hilfe.handbuch")); d.resize(*GROESSE_FENSTER_HANDBUCH)
    v = _spalte("standard", d)
    v.addWidget(handbuch_inhalt(), 1)
    fz = _spalte("fuss"); fussleiste(d, fz, nur_ok=True, ok_text=_t("hilfe.schliessen"))
    v.addLayout(fz)
    return d


def _fuss(d: QDialog, v: RasterSpalte) -> None:
    """Knopfzeile unten („Schließen“); in der Seitenleiste bleibt sie angeheftet."""
    fussleiste(d, v, nur_ok=True, ok_text=_t("hilfe.schliessen"))


def _titel(text: str) -> QLabel:
    t = QLabel(text); f = t.font(); f.setPointSize(f.pointSize() + SCHRIFT_HILFE_TITEL_PLUS_PT); f.setBold(True); t.setFont(f)
    return t


def _dialog(parent, titel: str, breite: int) -> tuple[QDialog, RasterSpalte]:
    d = HilfeFenster(parent); d.setWindowTitle(titel)
    if breite: d.setMinimumWidth(breite)
    v = _spalte("fenster", d)
    v.addWidget(_titel(titel)); v.addSpacing(_A_KLEIN)
    return d, v


def tastenkuerzel_inhalt() -> QWidget:
    """Inhalt „Tastenkombinationen“: je Gruppe eine Überschrift, darunter zwei Kürzel mit Wirkung nebeneinander."""
    d = QWidget(); v = _spalte("inhalt", d)
    for gruppe, zeilen in kuerzel.HILFE:
        v.addWidget(abschnittstitel(gruppe))
        w = QWidget(); g = FormularGitter(w)
        for taste, text in zeilen:
            wirkung = QLabel(text); wirkung.setWordWrap(True)
            t = QLabel(taste); f = t.font(); f.setBold(True); t.setFont(f); t.setWordWrap(True)
            g.zeile(wirkung, t)
        v.addWidget(w)
    v.addStretch(1)
    return d


def tastenkuerzel(parent) -> QDialog:
    d, v = _dialog(parent, _t("hilfe.tastenkombinationen"), 0)
    v.addWidget(tastenkuerzel_inhalt(), 1)
    _fuss(d, v)
    return d


def _erweiterungen_liste() -> list[tuple[bool, str, str, str]]:
    from writer.anbindung import vorlesen
    from writer.anbindung import languagetool
    schriften = [f for f in ("OpenDyslexic", "Lexend", _t("hilfe.atkinson_hyperlegible")) if standard_datenbank.hat_familie(f)]
    return [(bool(languagetool.verfuegbar()), "LanguageTool", _t("hilfe.gruendlich_pruefen_grammatik_ueber_die_e"), _t("hilfe.ca_386_mb")),
            (bool(vorlesen.piper_da()), _t("hilfe.stimmen_zum_vorlesen"), _t("hilfe.aufgenommene_stimmen_statt_der_blecherne"), _t("hilfe.ca_439_mb")),
            (len(schriften) == 3, _t("hilfe.schriften_zum_leichteren_lesen_0_3").format(len(schriften)), _t("hilfe.opendyslexic_lexend_atkinson_hyperlegibl"), _t("hilfe.ca_1_mb"))]


def erweiterungen_inhalt() -> QWidget:
    """Inhalt „Erweiterungen“: jede Karte zeigt mit „DA“, ob der Teil schon geholt ist."""
    d = QWidget(); v = _spalte("inhalt", d)
    hin = QLabel(_t("hilfe.drei_teile_liegen_ausserhalb_des_program"))
    hin.setWordWrap(True); v.addWidget(hin)
    for da, name, text, groesse in _erweiterungen_liste():
        karte = rahmen_baustein("flach", name="erwKarte")
        h = _reihe("karte", karte)
        b = QLabel("DA" if da else "—"); b.setAlignment(Qt.AlignCenter); b.setFixedSize(*GROESSE_PLAKETTE)
        _rolle(b, "plakette", status="an" if da else "aus")
        mitte = _spalte("eng")
        n = QLabel(name); n.setWordWrap(True); f = n.font(); f.setBold(True); n.setFont(f)
        t = QLabel(text); t.setWordWrap(True); f = t.font(); f.setItalic(True); t.setFont(f); hinweis_stil(t)
        mitte.addWidget(n); mitte.addWidget(t)
        h.addWidget(b); h.addLayout(mitte, 1)
        g = QLabel(groesse); hinweis_stil(g); h.addWidget(g, 0, Qt.AlignTop)
        v.addWidget(karte)
    fuss = QLabel(_t("hilfe.erweiterungen_von_fremder_hand_nimmt_die"))
    fuss.setWordWrap(True); v.addWidget(fuss)
    v.addStretch(1)
    return d


def erweiterungen(parent) -> QDialog:
    d, v = _dialog(parent, _t("hilfe.erweiterungen"), 0)
    v.addWidget(erweiterungen_inhalt(), 1)
    _fuss(d, v)
    return d


def ueber_inhalt(version: str | None = None) -> QWidget:
    """Inhalt „Über Lunivo Writer“."""
    if version is None:
        from writer.anbindung.version import version as _programmversion
        version = _programmversion()
    d = QWidget(); v = _spalte("inhalt", d)
    for text in (_t("hilfe.lunivo_writer_0_ein_raum_fuer_worte").format(version),
                 _t("hilfe.die_pruefung_und_der_wortschatz_stammen"),
                 _t("hilfe.was_geschrieben_wird_bleibt_auf_diesem_r")):
        l = QLabel(text); l.setWordWrap(True); v.addWidget(l); v.addSpacing(ABSTAND_NORMAL)
    v.addStretch(1)
    return d


def ueber(parent, version: str) -> QDialog:
    d, v = _dialog(parent, _t("hilfe.ueber_lunivo_writer"), 0)
    v.addWidget(ueber_inhalt(version), 1)
    _fuss(d, v)
    return d
