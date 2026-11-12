"""Der Editor: QTextEdit mit Seitenbreite, Formatierungsbefehlen und Seitenzählung."""
from __future__ import annotations

from PySide6.QtCore import QRect, QRectF, QSizeF, QTimer, Qt, Signal, QUrl
from PySide6.QtGui import QColor, QFont, QPainter, QPalette, QPen, QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat
from PySide6.QtWidgets import QListWidget, QScrollArea, QTextEdit

from lunivo_writer.editor.seite.anzeige_extra import VersteckterText
from lunivo_writer.modelle.seite import PageSettings, mm_to_px
from lunivo_writer.editor.seite.seiten_aufteilung import bind_layout
from lunivo_writer.editor.text import stile
from lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_bedienung import FreieBilderMixin
from lunivo_writer.oberflaeche.dokument.bearbeitung.zusatz_editor import ZusatzMixin
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_einfuegen import EinfuegenMixin

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_anzeige import AnzeigeBaustein
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_spalten import SpaltenBaustein
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_lauf import LAUF_STANDARD, LaufBaustein
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_seiten import SeitenBaustein
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_formatierung import FormatierungBaustein
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_bilder import BilderBaustein
from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_schreibhilfe import SchreibhilfeBaustein

STREIFEN_DUNKEL, STREIFEN_HELL = "#2b2d30", "#d9dee5"   # Arbeitsfläche neben dem Blatt (dunkel/hell)

STYLES = dict.fromkeys(stile.NAMEN)       # nur die eingebauten; selbst angelegte: stile.namen()            # Namen der Formatvorlagen (Definitionen: editor/text/stile.py)


class DocumentEditor(LaufBaustein, AnzeigeBaustein, SpaltenBaustein, SeitenBaustein, FormatierungBaustein, BilderBaustein, SchreibhilfeBaustein, FreieBilderMixin, ZusatzMixin, EinfuegenMixin, QTextEdit):
    pageInfoChanged = Signal(int, int)       # aktuelle Seite, Seitenzahl

    formatChanged = Signal()                 # Cursor-Format hat sich geändert

    zoomChanged = Signal(float)

    freiAuswahlGeaendert = Signal()           # ein frei positioniertes Bild wurde markiert oder die Markierung aufgehoben

    pageApplied = Signal()                    # Seiteneinrichtung oder Größe hat sich geändert

    leseschutzGeaendert = Signal(bool)        # Nur-Lesen wurde ein- oder ausgeschaltet (Qt hat dafür kein eigenes Signal)

    def setReadOnly(self, ro: bool) -> None:
        alt = self.isReadOnly()
        super().setReadOnly(ro)
        if alt != self.isReadOnly():
            self.leseschutzGeaendert.emit(self.isReadOnly())


    def __init__(self, parent=None):
        super().__init__(parent)
        self.page = PageSettings()
        self.stil_tasten()
        self.setAcceptRichText(True)
        self.setFrameShape(QTextEdit.NoFrame)          # das Blatt hat keinen Rahmen; es steht frei auf der Arbeitsfläche
        self.setUndoRedoEnabled(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.show_marks = False
        self.zoom = 1.0
        self.gitter = False
        self.web = False
        self._web_breite = 800
        self.gliederung = False
        self.zeilenfokus = False
        self.marken = False                # Textbegrenzungen (Eckmarken am Textrand)
        self.vorhersage = None            # Rückruf: Wortanfang → Liste von Vorschlägen
        self.autokorr = None              # Rückruf: Text vor dem Zeiger → korrigierter Text
        self.mini_hook = None             # Rückruf(editor, globalePosition, rechtsklick): Minisymbolleiste zeigen/verbergen
        self.kontext_hook = None          # Rückruf(menü, position): ergänzt das Rechtsklick-Menü
        self.opt = lambda name, std=True: std      # Rückruf: Schalter aus den Optionen
        self.opt_text = lambda name, std="": std   # Rückruf: Textwerte aus den Optionen
        self._wellen: list = []                  # ProofingIssue (Wellenlinien der Schreibhilfe)
        self._popup = QListWidget(None)
        self._popup.setWindowFlags(Qt.ToolTip)
        self._popup.setFocusPolicy(Qt.NoFocus)
        self._popup.itemClicked.connect(lambda it: self._vorschlag_nehmen(it.data(Qt.UserRole)))
        self._pages = 1
        self._extra_seiten = 0              # Blätter, die erst der Druck (Endnoten) anhängt
        self._lese_papier = ""              # Lesehilfe: Papierfarbe / Textfarbe überschreiben die Blattfarbe
        self._lese_text = ""
        self._breaks: list[int] = []
        self._paged: QTextDocument | None = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(350)
        self._timer.timeout.connect(self._recount)
        self.cursorPositionChanged.connect(self._cursor_moved)
        self.cursorPositionChanged.connect(lambda: self.zeilenfokus and self.viewport().update())
        self.currentCharFormatChanged.connect(lambda *_: self.formatChanged.emit())
        self.document().contentsChanged.connect(self._timer.start)
        self._fluss = QTimer(self); self._fluss.setSingleShot(True); self._fluss.setInterval(500)      # Umbruchregeln nach dem Tippen prüfen
        self._fluss.timeout.connect(self._seitenfluss)
        self._fluss_laeuft = False
        self._effekt_cache: bool | None = None
        self.document().contentsChange.connect(self._effekt_geaendert)
        self.document().contentsChanged.connect(self._fluss_planen)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)       # die Seite wächst mit, der graue Grund scrollt
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cursorPositionChanged.connect(self._scroll_outer)
        self._verbinde_groesse()
        self._zusatz_init()
        from lunivo_writer.oberflaeche.dokument.tabelle.tabelle_griffe import TabellenGriffe
        self._tabellen_griffe = TabellenGriffe(self)
        from lunivo_writer.oberflaeche.dokument.ansicht.absatz_symbol import AbsatzSymbol
        self._absatz_symbol = AbsatzSymbol(self)
        self.versteckt_zeigen = False
        self._blasen_flaeche = None
        self._blasen_cache = (None, [])
        self._blasen_extra = 0
        self._versteckt_hl = VersteckterText(self.document())
        self._zeilen_cache = (-1, [])
        self._sp_caret = True
        self._sp_timer = QTimer(self)                  # Schreibmarke blinkt selbst, solange Spalten gezeichnet werden
        self._sp_timer.setInterval(530)
        self._sp_timer.timeout.connect(self._sp_blinken)
        self.cursorPositionChanged.connect(self._sp_neu_zeichnen)
        self.selectionChanged.connect(self._sp_neu_zeichnen)
        self.document().contentsChanged.connect(self._sp_neu_zeichnen)
        self.apply_page(self.page)


    # ---- Dokument und Seite ---------------------------------------------

    def _verbinde_groesse(self) -> None:
        self.document().documentLayout().documentSizeChanged.connect(self._passe_hoehe_an)


    def _passe_hoehe_an(self, *_):
        if self.web:
            h = int(self.document().size().height()) + 4
        else:
            g = self._sp_geo()
            n = self._blatt_anzahl()
            h = int(self.blatt_oben(n - 1) + (self._blatt(n - 1)["H"] if getattr(self, "_qplan", None) else g["H"]) + g["gap"])
        if h != self.height():
            self.setFixedHeight(h)
        self.pageApplied.emit()


    def _blatt_anzahl(self) -> int:
        """Anzahl der Blätter: so viele, wie der Textfluss des Editors Seiten braucht (plus Noten-Seiten, die nur der Druck anhängt)."""
        if self._lauf is not None:
            return max(1, len(self._lauf.blaetter))
        n = max(1, int(self.page.spalten))
        return max(1, -(-max(1, self.document().pageCount()) // n)) + self._extra_seiten


    def _aussen(self):
        w = self.parent()
        while w is not None and not isinstance(w, QScrollArea):
            w = w.parent()
        return w


    def _scroll_outer(self) -> None:
        sa = self._aussen()
        if sa is None or sa.widget() is None:
            return
        r = self.cursorRect()
        pt = self.viewport().mapTo(sa.widget(), r.topLeft())
        sa.ensureVisible(pt.x(), pt.y() + r.height() // 2, 10, max(40, r.height() * 2))


    def set_document_and_page(self, doc: QTextDocument, page: PageSettings) -> None:
        self.setDocument(doc)
        self._versteckt_hl = VersteckterText(doc, self.versteckt_zeigen)
        self._verbinde_groesse()
        doc.setDocumentMargin(0)
        doc.contentsChanged.connect(self._timer.start)
        doc.contentsChanged.connect(self._fluss_planen)
        doc.contentsChange.connect(self._effekt_geaendert)
        self._effekt_cache = None
        self._fluss.start()
        doc.contentsChange.connect(self._inhalt_geaendert)
        self.apply_page(page)
        doc.setModified(False)
        doc.clearUndoRedoStacks()


    def apply_page(self, page: PageSettings) -> None:
        self.page = page
        doc = self.document()
        self.seitenfarbe_anwenden()
        bind_layout(doc, self.zoom)
        doc.setDocumentMargin(0)

        root = doc.rootFrame()
        ff: QTextFrameFormat = root.frameFormat()

        if self.web:
            for setze in (
                ff.setTopMargin,
                ff.setBottomMargin,
                ff.setLeftMargin,
                ff.setRightMargin,
            ):
                setze(mm_to_px(8))
            root.setFrameFormat(ff)
            self.setFixedWidth(max(300, int(self._web_breite)))

        else:
            # Blattmodus: Die Ränder gehören zum Blatt, nicht zum Textfluss. Das Dokument wird auf die Textfläche
            # (Breite/Höhe ohne Ränder) umbrochen; jede Qt-Seite des Flusses wird auf ein eigenes Blatt gezeichnet.
            for setze in (
                ff.setTopMargin,
                ff.setBottomMargin,
                ff.setLeftMargin,
                ff.setRightMargin,
            ):
                setze(0)
            ff.setTopMargin(page.erste_seite_versatz_px())       # lange Kopfzeile: Text der ersten Seite beginnt darunter
            root.setFrameFormat(ff)
            self.setFixedWidth(int(getattr(self, "_qbreite", mm_to_px(page.width_mm)) * self.zoom))
            self._sp_einrichten()

        if self._lauf is None and LAUF_STANDARD:
            self.lauf_einschalten()                                  # der Seitenlauf ist die Anordnung des Editors
        elif self._lauf is not None:
            self._lauf_auffrischen()
        self._blasen_einrichten()

        if self.web:
            if self.lineWrapMode() != QTextEdit.WidgetWidth:
                self.setLineWrapMode(QTextEdit.WidgetWidth)
                self._sp_timer.stop()
            doc.setPageSize(QSizeF(max(300, self._web_breite), -1))

        self._recount()
        self._passe_hoehe_an()
        self._timer.start()
        self.pageApplied.emit()


    # ---- Sprechblasen ------------------------------------------------------------------------------------------------
    class _OptAdapter:
        """Gibt `sprechblasen.konfig_lesen` die Rückrufe des Editors statt einer Settings-Klasse."""
        def __init__(self, ed):
            self.ed = ed

        def get(self, name, std=None):
            return self.ed.opt_text(name, std if isinstance(std, str) else str(std if std is not None else ""))

        def get_bool(self, name, std=False):
            return self.ed.opt(name, std)


    def focusInEvent(self, e) -> None:
        super().focusInEvent(e)
        if self._blatt_aktiv():
            self._sp_timer.start()


    def mousePressEvent(self, e) -> None:
        if self._frei_maus(e, "press"):
            return
        super().mousePressEvent(self._maus_abgebildet(e))


    def dragMoveEvent(self, e) -> None:
        m = self._ziehen_abgebildet(e)
        super().dragMoveEvent(m)
        if m is not e:
            e.setDropAction(m.dropAction())
            e.setAccepted(m.isAccepted())


    def dropEvent(self, e) -> None:
        m = self._ziehen_abgebildet(e)
        super().dropEvent(m)
        if m is not e:
            e.setDropAction(m.dropAction())
            e.setAccepted(m.isAccepted())


    def mouseMoveEvent(self, e) -> None:
        if self._frei_maus(e, "move"):
            return
        zone = self._kopffuss_zone(e.position().y())
        if zone and not e.buttons() and self.opt("ui/kopffuss_tipp", True):
            from PySide6.QtWidgets import QToolTip
            QToolTip.showText(e.globalPosition().toPoint(), "Doppelklick bearbeitet die " + ("Kopfzeile" if zone == "kopf" else "Fußzeile"), self)
        super().mouseMoveEvent(self._maus_abgebildet(e))


    def mouseDoubleClickEvent(self, e) -> None:
        if self.__dict__.get("_fp_key") is not None and self._frei_maus(e, "doppel"):          # Doppelklick auf eine Kante: Punkt einfügen
            return
        zone = self._kopffuss_zone(e.position().y())
        if self._doppelklick_kopffuss(zone) or self._doppelklick_objekt(e):
            return
        super().mouseDoubleClickEvent(self._maus_abgebildet(e))

    def _doppelklick_kopffuss(self, zone) -> bool:
        """Doppelklick in die Kopf-/Fußzone öffnet sie; Doppelklick in den Text beendet das Bearbeiten der Kopfzeile."""
        kf = getattr(self, "_kopffuss", None)
        if kf is not None and kf.aktiv and not zone:
            kf.beende()
            return True
        fenster = self.window()
        if zone and hasattr(fenster, "edit_header_footer"):
            fenster.edit_header_footer(zone == "kopf")
            return True
        return False

    def _doppelklick_objekt(self, e) -> bool:
        """Doppelklick auf einen SmartArt-Knoten oder ein WordArt/Textfeld: direkt im Objekt schreiben."""
        t = self._frei_bild_bei(e.position(), True) if hasattr(self, "_frei_treffer") else None
        if t is None or t[0] != getattr(self, "_frei_sel", None):
            return False
        if t[1].get("art") == "smartart":
            from lunivo_writer.editor.objekte import smartart as SA
            if SA.knoten_bei(self, e.position()) is not None and self.frei_knoten_edit_starten():
                return True
        if hasattr(self.window(), "befehle"):
            from lunivo_writer.editor.objekte import frei_objekt as FO
            return bool(FO.bearbeiten_starten(self))
        return False


    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._blasen_geometrie()
        if self._blatt_aktiv():
            g = self._sp_geo()
            ps = self.document().pageSize()
            if abs(ps.height() - g["ch"]) > 0.5 or abs(ps.width() - g["cb"]) > 0.5:
                self.document().setPageSize(QSizeF(g["cb"], g["ch"]))


    ZOOM_MIN, ZOOM_MAX = 0.1, 5.0


    def wheelEvent(self, e) -> None:
        if e.modifiers() & Qt.ControlModifier:
            self.set_zoom(self.zoom * (1.1 if e.angleDelta().y() > 0 else 1 / 1.1))
            e.accept()
            return
        e.ignore()                      # die Seite scrollt im grauen Grund


    def contextMenuEvent(self, e) -> None:
        if self.__dict__.get("_fp_key") is not None:                                           # Punkte bearbeiten: Rechtsklick löscht einen Punkt
            e.accept()
            return
        from lunivo_writer.oberflaeche.bauteile.kontextmenue import menue_bauen
        from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
        c = self.cursorForPosition(e.pos())                            # wie in Textprogrammen: Rechtsklick außerhalb der Markierung setzt die Schreibmarke dorthin
        tc = self.textCursor()
        if not (tc.hasSelection() and tc.selectionStart() <= c.position() <= tc.selectionEnd()):
            self.setTextCursor(c)
        fenster = self.window()
        m = menue_bauen(self, fenster) if hasattr(fenster, "befehle") else MenueListe.standard(self)
        if self.kontext_hook is not None:
            pos = self.cursorForPosition(e.pos()).position()
            self.kontext_hook(m, pos)
        self._kontext_objekt_eintraege(m)
        self._kontext_text_eintraege(m)
        mini = self.mini_hook is not None and self.opt("ui/mini_rechtsklick", True) and not self.isReadOnly()
        if mini:
            self.mini_hook(self, e.globalPos(), True, m.sizeHint())      # die Leiste richtet sich nach dem Menü
        m.exec(e.globalPos())
        m.deleteLater()
        if mini:
            self.mini_hook(None, None, True)

    def _kontext_objekt_eintraege(self, m) -> None:
        """Layout und Textumbruch für ein gewähltes Objekt oder Bild."""
        from lunivo_writer.editor.objekte import bildlayout as BL
        if BL.ziel(self) is not None and not self.isReadOnly():
            m.addSeparator()
            if BL.ziel(self)[0] == "frei":
                m.eintrag("Formatieren …", self._frei_formatierung)         # dieselbe Seitenleiste „Formatierung“ wie das Zahnrad der Schnellleiste
            m.eintrag("Layout …", self.bild_layout_dialog)
        if self._bild_cursor() is not None and not self.isReadOnly():
            from lunivo_writer.editor.seite import umbruch as U
            m.addSeparator()
            c = self._bild_cursor()
            aktuell = U.schwebend(self.document(), c.selectionStart()) or "zeile"
            for modus, text in (("zeile", "Bild: mit Text in Zeile"), ("links", "Bild: links, Text umfließt"),
                                ("rechts", "Bild: rechts, Text umfließt"),
                                ("oben_unten", "Bild: oben und unten (eigene Zeile)")):
                m.eintrag(text, lambda modus=modus: U.umbruch_setzen(self, modus), haken=(modus == aktuell))

    def _kontext_text_eintraege(self, m) -> None:
        """Ausgeblendeter Text und KI-Aktionen für markierten Text (nicht in Tabellen: das Tabellenmenü bleibt wie in der Vorlage)."""
        in_tabelle = self.textCursor().currentTable() is not None
        if self.textCursor().hasSelection() and not self.isReadOnly() and not in_tabelle:
            m.addSeparator()
            m.eintrag("Ausgeblendeter Text", lambda: self.set_versteckt(not self.ist_versteckt()), haken=self.ist_versteckt())
        ki = getattr(self.window(), "ki", None)
        if ki is not None and self.textCursor().hasSelection() and not self.isReadOnly() and not in_tabelle:
            m.addSeparator()
            m.eintrag("KI: Text in Bild", ki.bild_aus_text)
            aktionen = [a for a in ki.konfig.assistenten("aktion") if a.get("zugriff", "kontext") == "kontext"]
            if aktionen:
                sub = m.untermenue("KI-Aktionen")
                for a in aktionen:
                    sub.eintrag(a["name"], lambda a=a: ki.assistent(a))


    def mouseReleaseEvent(self, e) -> None:
        if self._frei_maus(e, "release"):
            return
        if e.button() == Qt.MiddleButton and not self.opt("bearbeiten/mittlere_taste", True):
            e.accept()                                  # mittlere Maustaste fügt nichts ein (Optionen ▸ Bearbeiten)
            return
        super().mouseReleaseEvent(self._maus_abgebildet(e))
        if e.button() == Qt.LeftButton and self.opt("bearbeiten/wortweise", True) and self.textCursor().hasSelection():
            self._wortweise()
        self._mini_nach_auswahl(e)
        if self._strg_klick_link(e):
            return
        if e.button() == Qt.LeftButton and not self.textCursor().hasSelection() and not self.isReadOnly() and self._klick_auf_marke(e):
            return
        self._bild_vor_klick_waehlen(e)

    def _mini_nach_auswahl(self, e) -> None:
        if (e.button() == Qt.LeftButton and self.mini_hook is not None and self.textCursor().hasSelection()
                and not self.isReadOnly() and self.opt("ui/mini_auswahl", True) and not self._bild_cursor()):
            c = QTextCursor(self.textCursor())
            c.setPosition(c.selectionStart())
            self.mini_hook(self, self.viewport().mapToGlobal(self.cursorRect(c).topLeft()), False)

    def _strg_klick_link(self, e) -> bool:
        """Strg+Klick auf einen Verweis springt dorthin bzw. öffnet die Adresse. → behandelt?"""
        if not ((e.modifiers() & Qt.ControlModifier) and self.opt("ui/strg_klick_link", True)):
            return False
        href = self.anchorAt(e.position().toPoint())
        if href and href.startswith("#"):
            from lunivo_writer.editor.dokument.verweise import intern_springen
            intern_springen(self, href)
        elif href:
            from PySide6.QtCore import QUrl as _U
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(_U(href))
        return bool(href)

    def _klick_auf_marke(self, e) -> bool:
        """Klick auf ein Formularfeld, einen Kasten oder eine Notiz-Marke. → behandelt?"""
        from lunivo_writer.editor.dokument.sendungen import kasten_umschalten
        from lunivo_writer.editor.dokument import formular as FO
        pos = self.cursorForPosition(e.position().toPoint()).position()
        if FO.klick(self, pos, self.window()) or kasten_umschalten(self, pos):
            return True
        if (n := self.note_an(pos)) is not None and self.cursorRect(self.cursorForPosition(e.position().toPoint())).adjusted(-6, 0, 6, 0).contains(e.position().toPoint()):
            self.noteAngeklickt.emit(*n)
        return False

    def _bild_vor_klick_waehlen(self, e) -> None:
        c = self.cursorForPosition(e.position().toPoint())
        c2 = QTextCursor(c)
        c2.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        if c2.charFormat().isImageFormat() and not self.textCursor().hasSelection():
            r = self.cursorRect(c)
            if abs(e.position().toPoint().x() - r.x()) < c2.charFormat().toImageFormat().width() + 2:
                self.setTextCursor(c2)


    def paintEvent(self, e) -> None:
        sp = self._blatt_aktiv()
        if sp:
            self._blatt_zeichnen(e)
        else:
            super().paintEvent(e)
        vp = self.viewport()
        p = QPainter(vp)
        self._dekoration_zeichnen(p, vp, sp)
        p.end()
        self._lese_wachstum_zeichnen()

    def _dekoration_zeichnen(self, p: QPainter, vp, sp) -> None:
        """Alles, was über dem Text liegt: Schmuck, Gitter, Absatzzusatz, Zeilennummern, Eckmarken, Spaltenlinien, Zeilenfokus."""
        self._deko_flaechen(p, sp)
        self._deko_marken(p, vp, sp)

    def _deko_flaechen(self, p: QPainter, sp) -> None:
        """Schmuck, Gitter, Absatzzusatz und Zeilennummern."""
        fliess = not self.web
        self._schmuck_zeichnen(p)
        if self.gitter:
            self._gitter_zeichnen(p)
        if fliess and self._hat_absatzzusatz():
            self._absatzzusatz_zeichnen(p, sp)
        if fliess and self.page.zeilennummern and self._lauf is not None:
            self._lauf_zeilennummern(p)
        elif fliess and self.page.zeilennummern and not self._mehrspaltig():
            self._zeilennummern_zeichnen(p)

    def _deko_marken(self, p: QPainter, vp, sp) -> None:
        """Eckmarken, Zusätze, Spaltenlinien und Zeilenfokus."""
        is_dark = self.palette().color(QPalette.Window).lightness() < 128
        line_color = QColor(Farbe.GRAU_HELL) if is_dark else QColor(Farbe.GRAU)
        if self.marken and not self.web:
            self._eckmarken_zeichnen(p, line_color)
        self._extras_zeichnen(p, sp)
        if self._lauf is not None and not self.web:
            self._lauf_spaltenlinien(p, line_color)
        elif sp and self._mehrspaltig() and self.page.spalten_linie:
            self._spaltenlinien_zeichnen(p, line_color)
        if self.zeilenfokus and self.hasFocus() and not self.textCursor().hasSelection():
            self._zeilenfokus_zeichnen(p, vp)

    def _hat_absatzzusatz(self) -> bool:
        """Rahmen, Mehrstufiges oder Tabfüllung an irgendeinem Absatz (je Dokumentrevision nur einmal gesucht, nicht bei jedem Zeichnen) oder ein Texteffekt."""
        doc = self.document()
        schl = (id(doc), doc.revision())
        if getattr(self, "_absatzzusatz_schl", None) != schl:
            self._absatzzusatz_schl = schl
            self._absatzzusatz_hat = self._hat_blockzusatz()
        return self._absatzzusatz_hat or self._hat_effekt()

    def _absatzzusatz_zeichnen(self, p: QPainter, sp) -> None:
        """Rahmen, Mehrstufiges, Tabfüllung und Effekte der Absätze (je Blatt oder fortlaufend)."""
        from lunivo_writer.editor.seite.seiten_aufteilung_deko import absatz_zusatz_zeichnen
        if self._lauf is not None:                                   # Blattkoordinaten: nichts zu verschieben
            absatz_zusatz_zeichnen(p, self.document(), self.zoom)
            return
        if sp:
            g = self._sp_geo()
            for lp in range(max(1, self.document().pageCount())):
                x0, y0 = self._sp_ursprung(lp)
                p.save()
                p.setClipRect(QRectF(x0 - 6, y0, g["cb"] + 12, g["ch"]))
                p.translate(x0, y0 - lp * g["ch"])
                absatz_zusatz_zeichnen(p, self.document(), self.zoom)
                p.restore()
        else:
            p.save()
            p.translate(0, -self.verticalScrollBar().value())
            absatz_zusatz_zeichnen(p, self.document(), self.zoom)
            p.restore()

    def _eckmarken_zeichnen(self, p: QPainter, line_color: QColor) -> None:
        """Eckmarken liegen außerhalb der Textfläche und zeigen von ihrer Ecke nach außen."""
        g = self._sp_geo()
        L = 14
        p.setPen(QPen(line_color, 1))
        quer = bool(getattr(self, "_qplan", None))
        for k in range(self._blatt_anzahl()):
            bk = self._blatt(k) if quer else None
            oben = int(self.blatt_oben(k) + (bk or g)["mt"])
            unten = int(self.blatt_oben(k) + (bk or g)["H"] - (bk or g)["mb"])
            links = bk["x"] + bk["ml"] if bk else g["ml"]
            rechts = links + bk["cw"] if bk else g["ml"] + g["cb"] * g["n"] + g["g"] * (g["n"] - 1)
            for x, ox in ((int(links), -1), (int(rechts), 1)):
                for y, oy in ((oben, -1), (unten, 1)):
                    p.drawLine(x, y, x + ox * L, y)
                    p.drawLine(x, y, x, y + oy * L)

    def _spaltenlinien_zeichnen(self, p: QPainter, line_color: QColor) -> None:
        g = self._sp_geo()
        p.setPen(QPen(line_color, 1))
        for k in range(self._blatt_anzahl()):
            for j in range(1, g["n"]):
                x = int(g["ml"] + j * (g["cb"] + g["g"]) - g["g"] / 2)
                y0 = self.blatt_oben(k) + g["mt"]
                p.drawLine(x, int(y0), x, int(y0 + g["ch"]))

    def _zeilenfokus_zeichnen(self, p: QPainter, vp) -> None:
        """Alles außer der Zeile mit der Schreibmarke wird abgedunkelt."""
        r = self.cursorRect()
        zeile = QRect(0, r.top() - 1, vp.width(), r.height() + 2)
        dunkel = QColor(self.palette().color(self.viewport().backgroundRole()))
        dunkel.setAlpha(170)
        p.setPen(Qt.NoPen)
        p.setBrush(dunkel)
        p.drawRect(QRect(0, 0, vp.width(), zeile.top()))
        p.drawRect(QRect(0, zeile.bottom() + 1, vp.width(), vp.height()))


    # ---- Schreibhilfe: Wellenlinien, Ersetzen, Vorhersage, AutoKorrektur -------------------
    WELLE = {"fehler": Farbe.ORANGE, "tipp": Farbe.AUSWAHL, "hinweis": Farbe.GRAU}


    def keyPressEvent(self, e) -> None:
        if self._frei_taste(e):
            return
        folge = self._folge_vorher(e)
        teilen = self._teilen_vorher(e)
        self._taste(e)
        if teilen is not None:
            self._teilen_danach(teilen)
        if folge:
            self._folge_danach(*folge)
        self._auswahl_uebernehmen()                                # die Sitzung kennt Schreibmarke und Auswahl nach jeder Taste

    def _auswahl_uebernehmen(self) -> None:
        """Schreibmarke und Auswahl des Editors in die Bearbeitungssitzung übernehmen (Oberfläche → Adapter → Sitzung)."""
        if self.zu_gross_fuer_spiegel():
            return
        self.modell_spiegel().cursor_uebernehmen(self.textCursor())

    def zu_gross_fuer_spiegel(self) -> bool:
        return self.modell_spiegel().zu_gross()


    def _teilen_vorher(self, e):
        """Enter teilt einen Absatz: Absatznummer, wenn der Absatz einen Seiten-/Spaltenumbruch davor oder ein Abschnittsende trägt."""
        from lunivo_writer.editor.seite.abschnitte import B_ABSCHNITT
        from lunivo_writer.editor.dokument.zusatz import B_SPALTE
        if e.key() not in (Qt.Key_Return, Qt.Key_Enter) or self.isReadOnly() or (e.modifiers() & ~Qt.KeypadModifier):
            return None
        bf = self.textCursor().blockFormat()
        if bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore or bf.hasProperty(B_SPALTE) or bf.hasProperty(B_ABSCHNITT):
            return self.textCursor().blockNumber()
        return None


    def _teilen_danach(self, nr: int) -> None:
        """Qt kopiert das Absatzformat in den neuen Absatz. Der Umbruch davor gilt nur für den ersten Teil (sonst macht jedes Enter ein
        neues Blatt), das Abschnittsende nur für den letzten (sonst entstünde ein zweiter Abschnitt)."""
        from lunivo_writer.editor.seite.abschnitte import B_ABSCHNITT
        from lunivo_writer.editor.dokument.zusatz import B_SPALTE
        doc = self.document()
        erster, zweiter = doc.findBlockByNumber(nr), doc.findBlockByNumber(nr + 1)
        if not zweiter.isValid() or self.textCursor().blockNumber() != nr + 1:
            return
        c2 = QTextCursor(zweiter); c2.joinPreviousEditBlock()
        bf = zweiter.blockFormat()
        bf.setPageBreakPolicy(bf.pageBreakPolicy() & ~QTextFormat.PageBreak_AlwaysBefore); bf.clearProperty(B_SPALTE)
        c2.setBlockFormat(bf)
        if erster.blockFormat().hasProperty(B_ABSCHNITT) and zweiter.blockFormat().hasProperty(B_ABSCHNITT):
            c1 = QTextCursor(erster); bf1 = erster.blockFormat(); bf1.clearProperty(B_ABSCHNITT); c1.setBlockFormat(bf1)
        c2.endEditBlock()


    def focusOutEvent(self, e) -> None:
        try:
            self._popup.hide()
        except RuntimeError:          # beim Beenden schon abgebaut
            pass
        super().focusOutEvent(e)


    # ---- Tastatur ----------------------------------------------------------------








