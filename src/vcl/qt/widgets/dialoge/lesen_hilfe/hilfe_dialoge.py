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
from system import pfade

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QLabel, QLineEdit, QPushButton, QTextBrowser, QWidget

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.zustaende.geruest.einklappgruppe import EinklappGruppe
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel, gruppe
from vcl.qt.widgets.bausteine.zustaende.geruest import Kachelraster
from vcl.qt.widgets.bausteine.zustaende.geruest.spalten import ZweiSpalter
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig

from vcl.qt.widgets.bausteine.tastaturnavigation import kuerzel




from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import (
    ABSTAND_HANDBUCH_ABSATZ, ABSTAND_HANDBUCH_TABELLE, ABSTAND_HANDBUCH_UEBER_UEBERSCHRIFT, ABSTAND_HANDBUCH_UEBER_UEBERSCHRIFT_SONST,
    ABSTAND_HANDBUCH_UNTER_UEBERSCHRIFT, ABSTAND_HANDBUCH_UNTER_UEBERSCHRIFT_SONST, BREITE_HANDBUCH_SCHMAL, BREITE_HANDBUCH_SPALTE,
    BREITE_HANDBUCH_TABELLE_PROZENT, BREITE_HANDBUCH_TABELLENSPALTEN_PROZENT, DECKKRAFT_HANDBUCH_KASTEN, DECKKRAFT_HANDBUCH_LINIE,
    POLSTER_HANDBUCH_TABELLENZELLE, RAND_HANDBUCH_MERKKASTEN, RAND_HANDBUCH_TEXT, RAND_HANDBUCH_TEXT_SCHMAL, SCHRIFT_HANDBUCH_TASTE_PT,
    SCHRIFT_HANDBUCH_TEXT_PT, SCHRIFT_HANDBUCH_UEBERSCHRIFT_PT, SCHRIFT_HILFE_ABSCHNITT_PT, SCHRIFT_HILFE_TITEL_PLUS_PT, VERSATZ_HANDBUCH_SPRUNG,
    ZEILENHOEHE_HANDBUCH_PROZENT,
)
from vcl.qt.widgets.bausteine.schrift.schriftarten import GENERISCH_MONOSPACE
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_BLOCK, ABSTAND_ENG, ABSTAND_MITTEL, ABSTAND_NORMAL, BREITE_NAVIGATION_HILFE, GROESSE_FENSTER_HANDBUCH, GROESSE_PLAKETTE, HOEHE_FELD, HOEHE_LESEFELD, HOEHE_NAVIGATION_HILFE, HOEHE_ZEILE_ABSCHNITT, HOEHE_ZEILE_ERWEITERUNG_KOPF, PADDING_HANDBUCH_EINTRAG, PADDING_HANDBUCH_NAVIGATION, RADIUS_EINTRAG, RADIUS_FELD, RADIUS_MITTEL, RAND_ERWEITERUNG_KARTE, RAND_HILFE_DIALOG, RAND_HILFE_FUSS, RAND_HILFE_SEITE, RAND_KEIN



GRUPPEN = [(_t("hilfe.anfangen"), [_t("hilfe.das_erste_blatt"), _t("hilfe.mehrere_dokumente"), _t("hilfe.die_oberflaeche_einrichten"), _t("hilfe.das_menue")]),
           (_t("hilfe.schreiben"), [_t("hilfe.text_und_gestaltung"), _t("hilfe.die_rechte_maustaste"), _t("hilfe.formatvorlagen"), _t("hilfe.die_seite")]),
           (_t("hilfe.was_hilft"), [_t("hilfe.die_schreibhilfe"), _t("hilfe.fuer_wen_themenwoerter"), _t("hilfe.die_lesehilfe"), _t("hilfe.vorlesen")]),
           (_t("hilfe.bausteine"), [_t("hilfe.textbausteine"), _t("hilfe.eigene_bausteine"), _t("hilfe.vorlagen")]),
           (_t("hilfe.heraus"), [_t("hilfe.speichern"), _t("hilfe.drucken")]),
           (_t("hilfe.nachschlagen"), [_t("hilfe.woher_es_kommt"), _t("hilfe.tastenkuerzel"), _t("hilfe.wo_was_liegt"), _t("hilfe.wenn_etwas_klemmt")])]


class HilfeFenster(PanelFaehig, QDialog):
    """Hilfefenster (Handbuch, Tastenkürzel, Erweiterungen, Über): öffnet mit ``exec()`` in der Seitenleiste."""


class _Lesefeld(QTextBrowser):
    """Der Text des Handbuchs in einer ruhigen Spalte: sie beginnt links am Seitenrand wie jede Dashboard-Seite und wird nicht breiter als
    ``BREITE_HANDBUCH_SPALTE`` (schmal: kleiner Rand). Alle Maße stehen in ``mass``."""

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.setViewportMargins(*RAND_KEIN)
        self.raender_setzen()

    def raender_setzen(self) -> None:
        """Der Rand ist rundum gleich; nur rechts wächst er mit der Breite, damit die Zeilen lesbar kurz bleiben. Nach jedem neuen Text erneut nötig."""
        rand = RAND_HANDBUCH_TEXT if self.width() > BREITE_HANDBUCH_SCHMAL else RAND_HANDBUCH_TEXT_SCHMAL
        wurzel = self.document().rootFrame()
        ff = wurzel.frameFormat()
        ff.setMargin(rand); ff.setRightMargin(max(rand, self.width() - BREITE_HANDBUCH_SPALTE - rand))
        wurzel.setFrameFormat(ff)


def _hb_bloecke(d, grund2) -> None:
    """Absätze und Überschriften: Abstände, Zeilenhöhe, Merkkästen."""
    from PySide6.QtGui import QBrush, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextFormat
    zitat = QTextFormat.BlockQuoteLevel.value                            # Merkkasten: im Markdown ein Zitatblock
    blk = d.begin()
    while blk.isValid():
        cf = QTextCharFormat()
        ebene = blk.blockFormat().headingLevel()
        bf = blk.blockFormat()
        if ebene:                                                        # Überschriften in der Schrift der Oberfläche, Größen wie auf den Dashboard-Seiten
            bf.setTopMargin(ABSTAND_HANDBUCH_UEBER_UEBERSCHRIFT.get(ebene, ABSTAND_HANDBUCH_UEBER_UEBERSCHRIFT_SONST))
            bf.setBottomMargin(ABSTAND_HANDBUCH_UNTER_UEBERSCHRIFT.get(ebene, ABSTAND_HANDBUCH_UNTER_UEBERSCHRIFT_SONST))
            cf.setFontPointSize(SCHRIFT_HANDBUCH_UEBERSCHRIFT_PT.get(ebene, SCHRIFT_HANDBUCH_TEXT_PT)); cf.setFontWeight(QFont.DemiBold)
        else:
            bf.setLineHeight(ZEILENHOEHE_HANDBUCH_PROZENT, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
            if blk.blockFormat().intProperty(zitat) == 0 and not blk.textList():
                bf.setBottomMargin(ABSTAND_HANDBUCH_ABSATZ)
        if blk.blockFormat().intProperty(zitat):
            links, oben, rechts, unten = RAND_HANDBUCH_MERKKASTEN
            bf.setBackground(QBrush(grund2)); bf.setLeftMargin(links); bf.setRightMargin(rechts); bf.setTopMargin(oben); bf.setBottomMargin(unten)
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
                cf = QTextCharFormat(); cf.setBackground(QBrush(grund2)); cf.setFontFamilies([_t("hilfe.dejavu_sans_mono"), _t("hilfe.liberation_mono"), GENERISCH_MONOSPACE]); cf.setFontPointSize(SCHRIFT_HANDBUCH_TASTE_PT)
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
        tf.setBorder(0); tf.setCellPadding(POLSTER_HANDBUCH_TABELLENZELLE); tf.setCellSpacing(0); tf.setBorderCollapse(True)
        oben, unten = ABSTAND_HANDBUCH_TABELLE
        tf.setTopMargin(oben); tf.setBottomMargin(unten)
        tf.setWidth(QTextLength(QTextLength.PercentageLength, BREITE_HANDBUCH_TABELLE_PROZENT))
        if t.columns() == len(BREITE_HANDBUCH_TABELLENSPALTEN_PROZENT):
            tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, anteil) for anteil in BREITE_HANDBUCH_TABELLENSPALTEN_PROZENT])
        t.setFormat(tf)
        for r in range(t.rows()):
            for k in range(t.columns()):
                cell = t.cellAt(r, k); cf = cell.format().toTableCellFormat()
                cf.setBorder(0); cf.setBorderBrush(QBrush(linie)); cf.setBottomBorder(1); cf.setBottomBorderStyle(QTextFrameFormat.BorderStyle_Solid)
                cf.setBottomBorderBrush(QBrush(linie))
                cell.setFormat(cf)


def _handbuch_gestalten(b: QTextBrowser) -> None:
    """Gibt dem Markdown-Text seine Gestalt: die Schrift der Oberfläche in der Größe der Dashboard-Seiten, Überschriften, Tabellen ohne Gitter,
    Merkkästen, Tastenchips. Größen und Abstände kommen aus ``mass``."""
    from PySide6.QtGui import QColor, QFont, QPalette
    d = b.document()
    pal = b.palette()
    linie = pal.color(QPalette.Mid); linie.setAlpha(DECKKRAFT_HANDBUCH_LINIE)
    grund2 = QColor(pal.color(QPalette.Text)); grund2.setAlpha(DECKKRAFT_HANDBUCH_KASTEN)
    schrift = QFont(b.font()); schrift.setPointSizeF(SCHRIFT_HANDBUCH_TEXT_PT)       # dieselbe Schriftart wie der Rest der Oberfläche
    d.setDefaultFont(schrift)
    _hb_bloecke(d, grund2)
    _hb_tastenchips(d, grund2)
    _hb_tabellen(d, linie)


_KAPITEL, _ABSCHNITT = "## ", "### "                                     # Überschriften im Markdown des Handbuchs: Kapitel und Abschnitt


def _hb_seiten(text: str) -> list[str]:
    """Teilt das Handbuch an den Kapiteln in Seiten (Markdown je Seite). Die erste Seite ist der Vorspann vor dem ersten Kapitel."""
    seiten: list[list[str]] = [[]]
    for z in text.split("\n"):
        if z.startswith(_KAPITEL):
            seiten.append([])
        seiten[-1].append(z)
    return ["\n".join(s) for s in seiten]


def handbuch_ansicht() -> QWidget:
    """Das Handbuch als Ansicht über die ganze Breite, aufgebaut wie die Optionen: links Suche und Gliederung, rechts der Text."""
    return handbuch_inhalt(als_ansicht=True)


def handbuch_inhalt(als_ansicht: bool = False) -> QWidget:
    """Der Inhalt des Handbuchs (ohne Fenster): Gliederung, Suche und Text. Er liegt als Markdown in ressourcen/handbuch.md. Das Dashboard zeigt ihn als
    Ansicht (``als_ansicht``: Suche und Gliederung in der linken Fläche wie bei den Optionen), ``handbuch(parent)`` als Fenster."""
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import QListWidget, QListWidgetItem
    d = QWidget()
    v = _spalte("kein" if als_ansicht else "standard", d)
    nav = QListWidget(); nav.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded); nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); nav.setFrameShape(QFrame.NoFrame); nav.setFocusPolicy(Qt.StrongFocus); nav.setAccessibleName(_t("hilfe.handbuch_abschnitte"))
    such = zeilenfeld("frei", platzhalter=_t("hilfe.im_handbuch_suchen")); such.setClearButtonEnabled(True)
    rechts = QWidget(); rv = _spalte("standard", rechts)
    if als_ansicht:
        # Wie die Optionen: die linke Fläche trägt Suche und Gliederung, rechts steht nur der Text
        nav.setObjectName("optNavigation")                              # dieselbe Navigation wie in den Optionen: eine Regel für beide
        such.setMinimumHeight(HOEHE_FELD)
        links = QWidget(); links.setObjectName("optLinks"); links.setAttribute(Qt.WA_StyledBackground, True)
        lv = _spalte("panel", links)
        lv.addWidget(such); lv.addWidget(nav, 1)
        spalten = ZweiSpalter(links, rechts, links_breite=BREITE_NAVIGATION_HILFE, oben="links")
    else:
        # Schmal: oben die Gliederung (einklappbar), darunter Suche und Text. Breit (ZweiSpalter): Gliederung links, Suche und Text rechts
        themen = EinklappGruppe(_t("hilfe.themen"))
        raender(themen, "rand_seitlich")
        unbegrenzt = nav.maximumHeight()                                 # die Höchsthöhe, die Qt einem Widget ohne Vorgabe gibt
        nav.setMaximumHeight(HOEHE_NAVIGATION_HILFE)
        nav.setObjectName("hilfeNav")
        themen.innen.addWidget(nav)
        themen.ausklappen(True)
        spalten = ZweiSpalter(themen, rechts, links_breite=BREITE_NAVIGATION_HILFE, oben="links", abstand=ABSTAND_NORMAL)

        def angeordnet(breit: bool) -> None:                                 # breit steht die Liste immer offen und so hoch wie das Fenster
            themen.knopf.setVisible(not breit)
            if breit:
                themen.ausklappen(True)
            nav.setMaximumHeight(unbegrenzt if breit else HOEHE_NAVIGATION_HILFE)
        spalten.angeordnet.connect(angeordnet)
        raender(such, "kein")
        sz = _reihe("rand_seitlich"); sz.addWidget(such, 1)
        rv.addLayout(sz)
    d.spalten = spalten
    v.addWidget(spalten, 1)
    b = _Lesefeld(); b.setOpenExternalLinks(True); b.setFrameShape(QFrame.NoFrame); b.setMinimumHeight(HOEHE_LESEFELD)
    try:
        with open(os.path.join(pfade.RESSOURCEN, "handbuch.md"), encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        text = _t("hilfe.das_handbuch_konnte_nicht_gelesen_werden")
    # Als Ansicht hat das Handbuch je Kapitel eine eigene Seite (wie die Optionen); als Fenster bleibt es ein durchlaufender Text
    seiten = _hb_seiten(text) if als_ansicht else [text]
    offen: list[int] = []

    def seite_zeigen(i: int) -> None:
        if offen != [i]:
            offen[:] = [i]
            b.setMarkdown(seiten[i]); _handbuch_gestalten(b); b.raender_setzen()
    seite_zeigen(0)
    rv.addWidget(b, 1)

    stellen: dict[str, tuple[int, str]] = {}                             # Überschrift → (Seite, Text der Überschrift)
    for i, seite in enumerate(seiten):
        for z in seite.split("\n"):
            if z.startswith((_KAPITEL, _ABSCHNITT)):
                kopf = z.lstrip("#").strip()
                stellen.setdefault(kopf, (i, kopf))
                if kopf == _t("hilfe.woher_dieses_programm_kommt"):          # die Gliederung nennt es kürzer
                    stellen.setdefault(_t("hilfe.woher_es_kommt"), (i, kopf))
    for _gruppe, titel in GRUPPEN:                                       # die Gliederung nennt manche Überschrift kürzer („Die rechte Maustaste“)
        for t in titel:
            if t not in stellen:
                lang = next((k for k in stellen if k.startswith(t)), None)
                if lang is not None:
                    stellen[t] = stellen[lang]
    eintraege: dict[int, QListWidgetItem] = {}                           # Seite → ihr Eintrag in der Gliederung
    ueber_kopf = QListWidgetItem(_t("hilfe.lunivo_writer_ein_raum_fuer_worte_das_ha")); ueber_kopf.setData(Qt.UserRole, "")
    f = ueber_kopf.font(); f.setBold(True); ueber_kopf.setFont(f)
    if not als_ansicht:                                                  # in der Ansicht steht der Name schon im Kopf („← Handbuch“): dort kein eigener Eintrag
        ueber_kopf.setSizeHint(QSize(0, HOEHE_ZEILE_ERWEITERUNG_KOPF))
        nav.addItem(ueber_kopf)
    for gruppe, titel in GRUPPEN:
        kopf = QListWidgetItem(gruppe.upper()); kopf.setFlags(Qt.NoItemFlags)
        f = kopf.font(); f.setBold(True)
        if not als_ansicht:                                              # in der Ansicht führt die Überschrift: volle Schriftgröße, fett, in Textfarbe
            f.setPointSizeF(SCHRIFT_HILFE_ABSCHNITT_PT); kopf.setSizeHint(QSize(0, HOEHE_ZEILE_ABSCHNITT))
        kopf.setFont(f)
        nav.addItem(kopf)
        for t in titel:
            if t in stellen:
                it = QListWidgetItem(t); it.setData(Qt.UserRole, t); nav.addItem(it)
                eintraege.setdefault(stellen[t][0], it)
    if not als_ansicht:
        eintraege[0] = ueber_kopf

    def springe(it):
        t = it.data(Qt.UserRole)
        if t == "":
            seite_zeigen(0)
            b.verticalScrollBar().setValue(0)
        elif t in stellen:
            i, kopf = stellen[t]
            seite_zeigen(i)
            blk = b.document().begin()
            while blk.isValid() and not (blk.blockFormat().headingLevel() and blk.text().strip() == kopf):
                blk = blk.next()
            if blk.isValid():
                lay = b.document().documentLayout()
                b.verticalScrollBar().setValue(int(lay.blockBoundingRect(blk).top()) - VERSATZ_HANDBUCH_SPRUNG)
    nav.itemClicked.connect(springe)
    nav.currentItemChanged.connect(lambda cur, _vor: springe(cur) if cur is not None else None)       # Pfeiltasten springen mit

    def suchen() -> None:
        """Sucht auf der offenen Seite weiter; ist dort nichts mehr, auf den folgenden Seiten (am Ende wieder von vorn)."""
        if b.find(such.text()):
            return
        for schritt in range(len(seiten)):
            i = (offen[0] + schritt + 1) % len(seiten)
            seite_zeigen(i)
            b.moveCursor(QTextCursor.Start)
            if b.find(such.text()):
                nav.blockSignals(True); nav.setCurrentItem(eintraege.get(i)); nav.blockSignals(False)      # der Vorspann hat in der Ansicht keinen Eintrag: dann ist nichts markiert
                return
    such.returnPressed.connect(suchen)
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


class _GemeinsameSpalte(QWidget):
    """Seite aus mehreren Karten: alle Beschriftungen sind so breit wie die längste — die Felder beginnen über die Karten hinweg an derselben Kante.
    Gemessen wird beim Zeigen, weil erst dann die Schrift der Seite gilt."""

    def __init__(self):
        super().__init__()
        self.beschriftungen: list[QLabel] = []

    def showEvent(self, e):
        super().showEvent(e)
        for l in self.beschriftungen:
            l.setMinimumWidth(0)
        breite = max((l.sizeHint().width() for l in self.beschriftungen), default=0)
        for l in self.beschriftungen:
            l.setMinimumWidth(breite)


def tastenkuerzel_inhalt() -> QWidget:
    """Inhalt „Tastenkombinationen“, aufgebaut wie eine Optionenseite: je Gruppe eine Karte im Kachelraster, darin die Wirkungen mit ihrem Kürzel
    (zwei Paare nebeneinander, wenn der Platz reicht). Wirkung und Kürzel beginnen in allen Karten an derselben Kante."""
    d = _GemeinsameSpalte(); v = _spalte("inhalt", d)
    raster = Kachelraster()
    for name, zeilen in kuerzel.HILFE:
        karte = gruppe(name.upper(), karte=True)
        g = FormularGitter(karte); raender(g, "gruppe")
        for taste, text in zeilen:
            wirkung = QLabel(text); wirkung.setWordWrap(True)
            t = QLabel(taste); f = t.font(); f.setBold(True); t.setFont(f); t.setWordWrap(True)
            g.zeile(wirkung, t)
            d.beschriftungen.append(wirkung)
        raster.hinzu(karte)
    v.addWidget(raster)
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
