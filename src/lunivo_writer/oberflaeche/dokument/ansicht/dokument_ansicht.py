"""Die Dokument-Zeichenfläche: zeigt ein ``Dokument`` über die neue Layout-Engine und den Dokument-Renderer, mit Schreibmarke, Auswahl, Maus, Tastatur,
Zoom und Scrollen.

Die Ansicht hält keinen eigenen Inhalt. Sie arbeitet auf der Bearbeitungssitzung (``core.editing.Bearbeitungssitzung``), die dem Dokument-Tab gehört, und
ändert das Dokument nur über sie. Das Layout (``core.layout.LayoutEngine``) wird bei jeder Änderung der Sitzung neu berechnet; gezeichnet wird mit
``core.rendering.DokumentRenderer`` über das Qt-Backend (``QPainter`` ist nur Ausgabe). Eingabe und Zwischenablage stehen in ``eingabe.py``.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QAbstractScrollArea, QApplication, QScrollArea, QWidget

from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.core.document import Position
from lunivo_writer.core.document.dokument import Auswahl
from lunivo_writer.core.editing import Bearbeitungssitzung
from lunivo_writer.core.geometry import Point, Rect, mm_to_px
from lunivo_writer.core.layout import LayoutEngine, LayoutErgebnis
from lunivo_writer.core.layout import formatwerte as F, schreibmarke as SM
from lunivo_writer.core.layout.seitenlayout import BLATT_ABSTAND_PX
from lunivo_writer.core.rendering import DokumentRenderer, zeichne_auswahl, zeichne_cursor
from lunivo_writer.core.rendering.linien import zeichne_linie
from lunivo_writer.core.rendering.textrenderer import zeichne_formatzeichen
from lunivo_writer.core.rendering.backend import Style, rgba
from lunivo_writer.core.textlayout.engine import TextLayoutEngine
from lunivo_writer.kern.farben import Farbe

from .eingabe import EingabeTeil
from .objekt_bedienung import ObjektBedienung
from .tabellen_bedienung import TabellenBedienung
from .blasen_bedienung import BlasenBedienung

AUSWAHL_DECKKRAFT = 90                 # Deckkraft der Auswahlfarbe über dem Text (0–255)
SICHT_RAND = 40                        # so viel Platz bleibt beim Rollen um die Schreibmarke
STANDARD_BLATT_MM = (210.0, 297.0)
RAND_OBEN = 28.0                       # Abstand zwischen Reiterleiste und erstem Blatt (Bildpunkte bei 100 % Zoom)
RAND_UNTEN = 28.0
SEITEN_LUECKE = 16.0                    # Abstand der beiden Blätter in der Zwei-Seiten-Ansicht
WELLEN_FARBE = {"fehler": "#e03131", "tipp": "#1971c2", "hinweis": "#f08c00"}
AUTOR_FARBEN = ("#c92a2a", "#1971c2", "#2f9e44", "#e8590c", "#7048a8", "#0b7285", "#a61e4d", "#5c940d")
WELLEN_STANDARD = "#e03131"


class DokumentAnsicht(EingabeTeil, ObjektBedienung, TabellenBedienung, BlasenBedienung, QWidget):
    freiAuswahlGeaendert = Signal()                # ein Objekt wurde gewählt oder die Wahl aufgehoben
    objektKnopf = Signal(str, object)              # Klick auf eine Schaltfläche neben dem Objekt: Name und globale Stelle
    zoomChanged = Signal(float)
    geaendert = Signal()                   # das Dokument wurde geändert (über diese Ansicht oder von außen über die Sitzung)
    cursorBewegt = Signal()
    linkAngeklickt = Signal(str)                   # Strg+Klick auf eine Verknüpfung: ihr Ziel
    noteAngeklickt = Signal(str, int)              # Klick auf das Zeichen einer Fuß- oder Endnote: Art und Id
    kontextGewuenscht = Signal(object)             # Rechtsklick: globale Stelle für das Menü
    auswahlBeendet = Signal(object)                # Maus nach dem Auswählen losgelassen: globale Stelle für die Minileiste

    ZOOM_MIN, ZOOM_MAX = 0.1, 5.0

    def __init__(self, sitzung: Bearbeitungssitzung, parent=None, engine: TextLayoutEngine | None = None):
        super().__init__(parent)
        self.sitzung = sitzung
        self._layout = LayoutEngine(engine)
        self._renderer = DokumentRenderer(self._layout.engine)
        self._erg: LayoutErgebnis | None = None
        self._x: float | None = None           # gemerkte Spalte der Schreibmarke bei „hoch“/„runter“
        self._an = True
        self._zieht = False
        self._doppelklick = 0.0
        self.nur_lesen = False
        self._objekt_init()
        self.formular_hook = None                    # Rückruf(Stelle im Rohtext) → True, wenn ein Formularfeld den Klick bekommen hat
        self.nur_lesen_formular = False
        self.gliederung_hook = None                  # Rückruf(±1): Alt+Umschalt+←/→ in der Gliederungsansicht
        self._tabelle_init()
        self._blasen_init()
        self.textgrenzen = False                      # Eckmarken am Rand des Textbereichs
        self.gitter = False
        self.lesefokus = 1.0                          # Deckkraft der Teile außerhalb des Absatzes der Schreibmarke
        self.zeilenfokus = False                      # die Zeile der Schreibmarke hervorheben
        self.papier = Farbe.PAPIER                    # Blattfarbe (Lesehilfe)
        self.seitenansicht = "einzeln"
        self.markup = True                            # Kommentare und Änderungen zeigen
        self.vor_aenderung = None                     # Rückruf(Sitzung) vor jeder Änderung über die Ansicht
        self._markup_cache = None
        self.wellen: list = []                        # Funde der Schreibhilfe (``ProofingIssue``) als Wellenlinien
        self.suchtreffer: list = []                   # Fundstellen als Stellen im Rohtext
        self.formatzeichen = (False, False)           # Absatzmarken, Leerzeichen und Tabulatoren zeigen
        self.zoom = 1.0
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.IBeamCursor)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setAutoFillBackground(False)
        sitzung.beobachte(self._modell_geaendert)
        self._blink = QTimer(self)
        self._blink.timeout.connect(self._blinken)
        zeit = QApplication.cursorFlashTime()
        if zeit > 0:
            self._blink.start(zeit // 2)

    # ---- Zustand: gesetztes Dokument --------------------------------------------------------------------------------------------
    def ergebnis(self) -> LayoutErgebnis:
        """Das Layout zum jetzigen Stand des Dokuments (bei Änderung neu berechnet)."""
        if self._erg is None:
            self._erg = self._layout.berechnen(self.sitzung.dokument)
            self._groesse_setzen()
        return self._erg

    def _modell_geaendert(self, _aenderung) -> None:
        self._erg = None
        self._markup_cache = None
        if self.gewaehltes_objekt is not None and self.gewaehltes_objekt not in self.sitzung.dokument.objekte:
            self.gewaehltes_objekt = None
        self.update()
        self.geaendert.emit()

    def nach_aenderung(self) -> None:
        """Nach einer Änderung über die Eingabe: Layout neu, Schreibmarke zeigen, Blinken zurücksetzen."""
        self._an = True
        self.ergebnis()
        self._sichtbar_machen()
        self.update()
        self.cursorBewegt.emit()

    def nach_bewegung(self) -> None:
        self._an = True
        self._sichtbar_machen()
        self.update()
        self.cursorBewegt.emit()

    def _markup_flaechen(self) -> dict:
        """Seitenindex → [(Art, Rechteck, Farbe)] für Kommentare (Hintergrund) und nachverfolgte Änderungen (unterstrichen/durchgestrichen), je Layout einmal."""
        if self._markup_cache is not None:
            return self._markup_cache
        erg, s = self.ergebnis(), self.sitzung
        aus: dict = {}
        if self.markup:
            from lunivo_writer.core.document.dokument import teile
            from lunivo_writer.core.rendering.backend import rgba

            def format_bei(pos) -> dict:
                rest = teile(s.dokument.absatz(pos.absatz_id).inhalte, pos.versatz)[1]
                return rest[0].format if rest else {}
            farben = AUTOR_FARBEN
            for b in s.bereiche(lambda f: "aenderung" in f, lambda f: (f["aenderung"], f.get("autor", ""))):
                art, autor = format_bei(b.anker)["aenderung"], format_bei(b.anker).get("autor", "")
                farbe = rgba(farben[sum(map(ord, autor)) % len(farben)])
                for seite_nr, rects in SM.auswahl_rechtecke(erg, b).items():
                    aus.setdefault(seite_nr, []).extend(("unter" if art == "ins" else "durch", r, farbe) for r in rects)
            for b in s.bereiche(lambda f: "kommentar" in f, lambda f: f.get("kommentar")):
                for seite_nr, rects in SM.auswahl_rechtecke(erg, b).items():
                    aus.setdefault(seite_nr, []).extend(("kommentar", r, (255, 200, 60, 70)) for r in rects)
        self._markup_cache = aus
        return aus

    def set_ansicht(self, **werte) -> None:
        """Ansichtseinstellungen: ``textgrenzen``, ``gitter``, ``zeilenfokus``, ``papier`` (Farbe) sowie für das Layout ``buchstaben``, ``wort``,
        ``zeilenluft`` und ``versteckt`` (ausgeblendeten Text zeigen)."""
        neu_setzen = False
        for k, v in werte.items():
            if k in ("textgrenzen", "gitter", "zeilenfokus", "papier", "lesefokus"):
                setattr(self, k, v)
            elif self._layout.optionen.get(k) != v:
                self._layout.optionen[k] = v
                neu_setzen = True
        if neu_setzen:
            self._erg = None
            self._markup_cache = None
        self.update()

    def set_markup(self, an: bool) -> None:
        self.markup = bool(an)
        self.update()

    def set_wellen(self, funde: list) -> None:
        self.wellen = list(funde)
        self.update()

    def set_suchtreffer(self, treffer: list) -> None:
        self.suchtreffer = list(treffer)
        self.update()

    def set_formatzeichen(self, absatz: bool, leer: bool) -> None:
        self.formatzeichen = (bool(absatz), bool(leer))
        self.update()

    def setReadOnly(self, an: bool) -> None:
        self.nur_lesen = bool(an)

    def isReadOnly(self) -> bool:
        return self.nur_lesen

    def seitenzahl(self) -> int:
        return len(self.ergebnis().seiten)

    # ---- Geometrie ---------------------------------------------------------------------------------------------------------------
    def set_zoom(self, faktor: float) -> None:
        faktor = max(self.ZOOM_MIN, min(self.ZOOM_MAX, round(faktor, 3)))
        if abs(faktor - self.zoom) < 1e-6:
            return
        self.zoom = faktor
        self._groesse_setzen()
        self.update()
        self.zoomChanged.emit(faktor)

    def _blattmass(self, i: int) -> tuple:
        seite = self._erg.seiten[i]
        if seite.breite_px:                                            # Weblayout
            return seite.breite_px, seite.hoehe_px
        einr = seite.einrichtung
        b, h = (einr.width_mm, einr.height_mm) if einr is not None else STANDARD_BLATT_MM
        return mm_to_px(b), mm_to_px(h)

    def set_seitenansicht(self, art: str) -> None:
        """``einzeln`` (Drucklayout), ``doppelt`` (zwei Seiten nebeneinander) oder ``web`` (eine endlose Seite in der Breite des Fensters)."""
        self.seitenansicht = art
        self.set_ansicht(web=(self._web_breite() if art == "web" else None))
        self._erg = None
        self._markup_cache = None
        self.ergebnis()
        self.update()

    def _web_breite(self) -> float:
        w = self.parentWidget()
        breite = w.width() if w is not None else self.width()
        return max(300.0, (breite - 24) / self.zoom)

    def _anordnung(self) -> list:
        """(x, y, Breite, Höhe) jedes Blatts bei Zoom 1 im Blattraum: untereinander, bei zwei Seiten paarweise nebeneinander (x ab dem linken Rand des Blattraums)."""
        n = len(self._erg.seiten)
        masse = [self._blattmass(i) for i in range(n)]
        if self.seitenansicht != "doppelt":
            return [(0.0, self._erg.seiten[i].oben + RAND_OBEN, masse[i][0], masse[i][1]) for i in range(n)]
        aus, y = [], RAND_OBEN
        for z in range(0, n, 2):
            reihe = masse[z:z + 2]
            for k, (b, h) in enumerate(reihe):
                aus.append((sum(m[0] for m in reihe[:k]) + SEITEN_LUECKE * k, y, b, h))
            y += max(m[1] for m in reihe) + BLATT_ABSTAND_PX
        return aus

    def _groesse_setzen(self) -> None:
        if self._erg is None or not self._erg.seiten:
            return
        a = self._anordnung()
        breite = max(x + b for x, _y, b, _h in a) + (self.blasen_breite() + mm_to_px(3.0) if self.blasen_aktiv() else 0.0)
        hoehe = max(y + h for _x, y, _b, h in a)
        self.setMinimumSize(round(breite * self.zoom), round((hoehe + RAND_UNTEN) * self.zoom))
        self.updateGeometry()

    def blatt(self, i: int) -> QRectF:
        """Das Blatt ``i`` in den Koordinaten der Ansicht (waagerecht in der Mitte)."""
        a = self._anordnung()
        x, y, b, h = a[i]
        gesamt = max(xx + bb for xx, _y, bb, _h in a) * self.zoom
        return QRectF(max(0.0, (self.width() - gesamt) / 2) + x * self.zoom, y * self.zoom, b * self.zoom, h * self.zoom)

    def _naechstes_blatt(self, pos) -> int:
        erg = self.ergebnis()
        return min(range(len(erg.seiten)), key=lambda k: max(self.blatt(k).top() - pos.y(), 0.0, pos.y() - self.blatt(k).bottom()))

    def stelle(self, pos) -> Position | None:
        """Die Textstelle unter einem Punkt der Ansicht (auf dem nächstgelegenen Blatt)."""
        erg = self.ergebnis()
        if not erg.seiten:
            return None
        i = self._naechstes_blatt(pos)
        r = self.blatt(i)
        t = erg.treffer(i, Point((pos.x() - r.left()) / self.zoom, (pos.y() - r.top()) / self.zoom))
        return Position(t[0], t[1]) if t is not None else None

    def objekt_bei(self, pos) -> int | None:
        """Das frei positionierte Objekt unter einem Punkt der Ansicht."""
        erg = self.ergebnis()
        if not erg.seiten:
            return None
        i = self._naechstes_blatt(pos)
        r = self.blatt(i)
        return erg.objekt_bei(i, Point((pos.x() - r.left()) / self.zoom, (pos.y() - r.top()) / self.zoom))

    def cursor_flaeche(self) -> QRectF | None:
        """Die Schreibmarke in den Koordinaten der Ansicht."""
        c = SM.cursor_rechteck(self.ergebnis(), self.sitzung.auswahl.kopf)
        if c is None:
            return None
        blatt = self.blatt(c[0])
        r = c[1]
        return QRectF(blatt.left() + r.x * self.zoom, blatt.top() + r.y * self.zoom, max(1.0, r.width * self.zoom), r.height * self.zoom)

    def _sichtbar_machen(self) -> None:
        r = self.cursor_flaeche() if self._erg is not None else None
        w = self.parentWidget()
        while r is not None and w is not None:
            if isinstance(w, QScrollArea):
                w.ensureVisible(round(r.center().x()), round(r.center().y()), SICHT_RAND, SICHT_RAND + round(r.height() / 2))
                return
            if isinstance(w, QAbstractScrollArea):
                return
            w = w.parentWidget()

    # ---- Zeichnen ----------------------------------------------------------------------------------------------------------------
    def paintEvent(self, ev) -> None:
        erg, s = self.ergebnis(), self.sitzung
        dok = s.dokument
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        flaechen = SM.auswahl_rechtecke(erg, s.auswahl) if not s.auswahl.leer else {}
        wellen_je_seite: dict = {}
        if self.wellen:
            from lunivo_writer.core.editing.suche import offset_zu_position
            for fund in self.wellen[:3000]:
                for seite_nr, rects in SM.auswahl_rechtecke(erg, Auswahl(offset_zu_position(dok, fund.von), offset_zu_position(dok, fund.bis))).items():
                    wellen_je_seite.setdefault(seite_nr, []).extend((r, WELLEN_FARBE.get(fund.art, WELLEN_STANDARD)) for r in rects)
        treffer: dict = {}
        if self.suchtreffer:
            from lunivo_writer.core.editing.suche import offset_zu_position
            for von, bis in self.suchtreffer[:2000]:
                for seite_nr, rects in SM.auswahl_rechtecke(erg, Auswahl(offset_zu_position(dok, von), offset_zu_position(dok, bis))).items():
                    treffer.setdefault(seite_nr, []).extend(rects)
        marke = SM.cursor_rechteck(erg, s.auswahl.kopf)
        hell = self.palette().color(QPalette.Highlight)
        auswahlfarbe = (hell.red(), hell.green(), hell.blue(), AUSWAHL_DECKKRAFT)
        grund = F.schrift(dict(dok.standardformat))
        sicht = QRectF(ev.rect())
        for i in range(len(erg.seiten)):
            blatt = self.blatt(i)
            if not blatt.intersects(sicht):
                continue
            p.save()
            p.fillRect(blatt, QColor(self.papier))
            p.setClipRect(blatt)
            p.translate(blatt.topLeft())
            p.scale(self.zoom, self.zoom)
            b = QtRenderBackend(p)
            self._renderer.zeichne_seite(b, dok, erg, i, grund)
            if any(self.formatzeichen):
                zeichne_formatzeichen(b, erg, i, *self.formatzeichen)
            for art, r, farbe in self._markup_flaechen().get(i, []):
                if art == "kommentar":
                    b.draw_rect(r, Style(color=farbe, width=0, filled=True))
                else:
                    y = r.bottom - 2 if art == "unter" else r.y + r.height * 0.55
                    b.draw_line(Point(r.x, y), Point(r.right, y), Style(color=farbe, width=1.2))
            for r, farbe in wellen_je_seite.get(i, []):
                zeichne_linie(b, farbe, 0.8, "wellig", r.x, r.bottom - 1.5, r.right, r.bottom - 1.5, 96.0 / 72.0)
            zeichne_auswahl(b, treffer.get(i, []), (255, 214, 0, 110))
            zeichne_auswahl(b, flaechen.get(i, []), auswahlfarbe)
            self._hilfen_zeichnen(b, erg, i, marke)
            self.objekt_zeichnen(b, i)
            if marke is not None and marke[0] == i and self._an and self.hasFocus() and not self.nur_lesen and s.auswahl.leer:
                zeichne_cursor(b, marke[1], rgba(Farbe.SCHWARZ))
            p.restore()
        self.knoepfe_zeichnen(p)
        self.tabellen_zeichnen(p)
        self.blasen_zeichnen(p)
        if self.nach_zeichnen is not None:
            self.nach_zeichnen(p)
        p.end()

    def _hilfen_zeichnen(self, b, erg, i: int, marke) -> None:
        """Gitter, Textgrenzen und Zeilenfokus über dem Blatt."""
        einr = erg.seiten[i].einrichtung
        if einr is None:
            return
        links, oben = mm_to_px(einr.margin_left_mm), mm_to_px(einr.margin_top_mm)
        breite, hoehe = einr.content_width_px, einr.content_height_px
        if self.gitter:
            raster = Style(color=(160, 170, 185, 90), width=0.5)
            for x in range(0, int(mm_to_px(einr.width_mm)), 20):
                b.draw_line(Point(x, 0), Point(x, mm_to_px(einr.height_mm)), raster)
            for y in range(0, int(mm_to_px(einr.height_mm)), 20):
                b.draw_line(Point(0, y), Point(mm_to_px(einr.width_mm), y), raster)
        if self.textgrenzen:
            ecke, linie = 12.0, Style(color=(130, 140, 160, 200), width=1.0)
            for x, y, dx, dy in ((links, oben, 1, 1), (links + breite, oben, -1, 1), (links, oben + hoehe, 1, -1), (links + breite, oben + hoehe, -1, -1)):
                b.draw_line(Point(x, y), Point(x + dx * ecke, y), linie)
                b.draw_line(Point(x, y), Point(x, y + dy * ecke), linie)
        if self.lesefokus < 0.999:
            ort = erg.absaetze.get(self.sitzung.auswahl.kopf.absatz_id)
            alpha = round((1.0 - self.lesefokus) * 255)
            papier = rgba(self.papier, alpha)
            for p in erg.seiten[i].plaetze:
                if p.art == "zeile" and p.block_id != self.sitzung.auswahl.kopf.absatz_id:
                    b.draw_rect(p.rect, Style(color=papier, width=0, filled=True))
        if self.zeilenfokus and marke is not None and marke[0] == i:
            r = marke[1]
            b.draw_rect(Rect(links, r.y, breite, r.height), Style(color=(255, 214, 0, 45), width=0, filled=True))

    def _blinken(self) -> None:
        self._an = not self._an
        r = self.cursor_flaeche() if self._erg is not None else None
        if r is not None:
            self.update(r.adjusted(-2, -2, 2, 2).toAlignedRect())

    def focusInEvent(self, ev) -> None:
        super().focusInEvent(ev)
        self._an = True
        self.update()

    def focusOutEvent(self, ev) -> None:
        super().focusOutEvent(ev)
        self.update()
