"""Die Dokument-Zeichenfläche: zeigt ein Dokument anhand seiner Kennung, mit Schreibmarke, Auswahl, Maus, Tastatur, Zoom und Scrollen.

Die Ansicht hält keinen eigenen Inhalt. Layout, Seitenbilder, Überlagerung und Schreibmarke rechnet und rendert das Framework zur Kennung des Dokuments
(``writer.funktionen.ansicht``); die Ansicht legt die fertigen Bilder auf ihren Zeichner (``QPainter`` ist nur Ausgabe) und fragt Stellen, Seiten und Plätze
als Werte ab. Bei jeder Änderung der Sitzung wird das Layout verworfen und beim nächsten Zugriff neu gerechnet. Eingabe und Zwischenablage stehen in ``eingabe.py``.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPalette
from PySide6.QtWidgets import QAbstractScrollArea, QApplication, QScrollArea, QWidget

from writer.funktionen import ansicht as AN
from writer.funktionen import bearbeiten as ST
from writer.werte import Punkt, Stelle
from writer.werte import mm_zu_px as mm_to_px
from writer.anbindung.geometrie import blatt_abstand_px
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import AUTOR_FARBEN, WELLEN_FARBE, WELLEN_STANDARD

from vcl.qt.widgets.dokumentansicht.ansicht.eingabe import EingabeTeil
from vcl.qt.widgets.dokumentansicht.ansicht.objekt_bedienung import ObjektBedienung
from vcl.qt.widgets.dokumentansicht.ansicht.tabellen_bedienung import TabellenBedienung
from vcl.qt.widgets.dokumentansicht.ansicht.blasen_bedienung import BlasenBedienung

AUSWAHL_DECKKRAFT = 90                 # Deckkraft der Auswahlfarbe über dem Text (0–255)
SICHT_RAND = 40                        # so viel Platz bleibt beim Rollen um die Schreibmarke
BILDCACHE_MAX_BYTES = 256 * 1024 * 1024   # höchstens so viel Speicher für fertig gerenderte Blätter; ältere fallen heraus (ein einzelnes Blatt bleibt immer)
STANDARD_BLATT_MM = (210.0, 297.0)
RAND_OBEN = 28.0                       # Abstand zwischen Reiterleiste und erstem Blatt (Bildpunkte bei 100 % Zoom)
RAND_UNTEN = 28.0
SEITEN_LUECKE = 16.0                    # Abstand der beiden Blätter in der Zwei-Seiten-Ansicht


LAYOUT_OPTIONEN = ("buchstaben", "wort", "zeilenluft", "versteckt", "web")      # bestimmen den Umbruch und damit die Seitenzahlen


class DokumentAnsicht(EingabeTeil, ObjektBedienung, TabellenBedienung, BlasenBedienung, QWidget):
    freiAuswahlGeaendert = Signal()                # ein Objekt wurde gewählt oder die Wahl aufgehoben
    objektKnopf = Signal(str, object)              # Klick auf eine Schaltfläche neben dem Objekt: Name und globale Stelle
    zoomChanged = Signal(float)
    geaendert = Signal()                   # das Dokument wurde geändert (über diese Ansicht oder von außen über die Sitzung)
    cursorBewegt = Signal()
    layoutOptionGeaendert = Signal(str, object)    # Name und Wert einer Layout-Option (``LAYOUT_OPTIONEN``)
    linkAngeklickt = Signal(str)                   # Strg+Klick auf eine Verknüpfung: ihr Ziel
    noteAngeklickt = Signal(str, int)              # Klick auf das Zeichen einer Fuß- oder Endnote: Art und Id
    kontextGewuenscht = Signal(object)             # Rechtsklick: globale Stelle für das Menü
    auswahlBeendet = Signal(object)                # Maus nach dem Auswählen losgelassen: globale Stelle für die Minileiste

    ZOOM_MIN, ZOOM_MAX = 0.1, 5.0

    def __init__(self, kennung: int, beobachten: bool = False, parent=None):
        """``kennung``: das Dokument im Framework. ``beobachten``: die Ansicht folgt den Änderungen des Dokuments (Editor); eine reine Vorschau tut das nicht."""
        super().__init__(parent)
        self.kennung = kennung
        self._erg = None                       # ``Layoutsicht`` zum jetzigen Stand; ``None``: beim nächsten Zugriff neu
        self._ueberlagerungscache: dict = {}
        self._ueberlagerungscache_erg = None
        self._bildcache = None                 # (Layout, Zoom, Papier, {Seite: fertiges Seitenbild}): die Seiten rendert der Kern, die Oberfläche zeigt sie nur
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
        self.wellen: list = []                        # Funde der Schreibhilfe (``ProofingIssue``) als Wellenlinien
        self.suchtreffer: list = []                   # Fundstellen als Stellen im Rohtext
        self.formatzeichen = (False, False)           # Absatzmarken, Leerzeichen und Tabulatoren zeigen
        self.zoom = 1.0
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.IBeamCursor)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setAutoFillBackground(False)
        if beobachten:
            abmelden = ST.dokument_beobachten(kennung, lambda: self._modell_geaendert(None))
            self.destroyed.connect(lambda *_: abmelden())
        self._blink = QTimer(self)
        self._blink.timeout.connect(self._blinken)
        zeit = QApplication.cursorFlashTime()
        if zeit > 0:
            self._blink.start(zeit // 2)

    # ---- Zustand: gesetztes Dokument --------------------------------------------------------------------------------------------
    def ergebnis(self):
        """Das Layout zum jetzigen Stand des Dokuments (bei Änderung neu berechnet) als ``Layoutsicht``."""
        if self._erg is None:
            self._erg = AN.layout_berechnen(self.kennung)
            self._groesse_setzen()
        return self._erg

    def _layout_verwerfen(self) -> None:
        self._erg = None
        AN.layout_verwerfen(self.kennung)

    def _modell_geaendert(self, _aenderung) -> None:
        self._layout_verwerfen()
        if self.gewaehltes_objekt is not None and not ST.objekt_vorhanden(self.kennung, self.gewaehltes_objekt):
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

    def set_ansicht(self, **werte) -> None:
        """Ansichtseinstellungen: ``textgrenzen``, ``gitter``, ``zeilenfokus``, ``papier`` (Farbe) sowie für das Layout ``buchstaben``, ``wort``,
        ``zeilenluft`` und ``versteckt`` (ausgeblendeten Text zeigen)."""
        neu_setzen = False
        for k, v in werte.items():
            if k in ("textgrenzen", "gitter", "zeilenfokus", "papier", "lesefokus"):
                setattr(self, k, v)
            elif AN.layout_option_setzen(self.kennung, k, v):
                neu_setzen = True
                if k in LAYOUT_OPTIONEN:
                    self.layoutOptionGeaendert.emit(k, v)          # der Editor gibt sie ans Framework weiter (Seitenzahlen wie in der Ansicht)
        if neu_setzen:
            self._layout_verwerfen()
        self.update()

    def set_silben(self, einstellung) -> None:
        """Lesehilfe „Silbenfarben“ (``SilbenEinstellung`` vom Framework oder ``None``): reine Anzeige, das Dokument bleibt unverändert."""
        if AN.layout_silben_setzen(self.kennung, einstellung):
            self._layout_verwerfen()
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
        breite_px, hoehe_px, breite_mm, hoehe_mm, _oben = self._erg.blattmasse[i]
        if breite_px:                                                  # Weblayout
            return breite_px, hoehe_px
        b, h = (breite_mm, hoehe_mm) if breite_mm is not None else STANDARD_BLATT_MM
        return mm_to_px(b), mm_to_px(h)

    def set_seitenansicht(self, art: str) -> None:
        """``einzeln`` (Drucklayout), ``doppelt`` (zwei Seiten nebeneinander) oder ``web`` (eine endlose Seite in der Breite des Fensters)."""
        self.seitenansicht = art
        self.set_ansicht(web=(self._web_breite() if art == "web" else None))
        self._layout_verwerfen()
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
            return [(0.0, self._erg.blattmasse[i][4] + RAND_OBEN, masse[i][0], masse[i][1]) for i in range(n)]
        aus, y = [], RAND_OBEN
        for z in range(0, n, 2):
            reihe = masse[z:z + 2]
            for k, (b, h) in enumerate(reihe):
                aus.append((sum(m[0] for m in reihe[:k]) + SEITEN_LUECKE * k, y, b, h))
            y += max(m[1] for m in reihe) + blatt_abstand_px()
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

    def stelle(self, pos) -> Stelle | None:
        """Die Textstelle unter einem Punkt der Ansicht (auf dem nächstgelegenen Blatt)."""
        erg = self.ergebnis()
        if not erg.seiten:
            return None
        i = self._naechstes_blatt(pos)
        r = self.blatt(i)
        return erg.treffer(i, Punkt((pos.x() - r.left()) / self.zoom, (pos.y() - r.top()) / self.zoom))

    def objekt_bei(self, pos) -> int | None:
        """Das frei positionierte Objekt unter einem Punkt der Ansicht."""
        erg = self.ergebnis()
        if not erg.seiten:
            return None
        i = self._naechstes_blatt(pos)
        r = self.blatt(i)
        return erg.objekt_bei(i, Punkt((pos.x() - r.left()) / self.zoom, (pos.y() - r.top()) / self.zoom))

    def cursor_flaeche(self) -> QRectF | None:
        """Die Schreibmarke in den Koordinaten der Ansicht."""
        self.ergebnis()
        c = AN.cursor_rechteck(self.kennung, ST.auswahl(self.kennung).kopf)
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
    def _seitenbild(self, erg, i: int) -> QImage:
        """Das Blatt ``i`` als fertiges Bild, gerendert vom Framework (ohne Qt); gemerkt, bis sich Layout, Zoom oder Papierfarbe ändern."""
        c = self._bildcache
        dpr = self.devicePixelRatioF()                                             # Hochauflösend: in Geräte-Pixeln rendern, sonst streckt Qt das Bild und die Schrift wird weich
        if c is None or c[0] is not erg or c[1] != (self.zoom, dpr) or c[2] != self.papier:
            c = self._bildcache = (erg, (self.zoom, dpr), self.papier, {})
        bild = c[3].get(i)
        if bild is not None:
            c[3][i] = c[3].pop(i)                                                  # zuletzt gezeigt nach hinten
        else:
            while c[3] and sum(b.sizeInBytes() for b in c[3].values()) > BILDCACHE_MAX_BYTES:       # Speicher begrenzen: die am längsten nicht gezeigten Blätter zuerst
                c[3].pop(next(iter(c[3])))
            breite, hoehe, roh = AN.seitenbild(self.kennung, i, self.zoom * dpr, self.papier)
            bild = c[3][i] = QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888).copy()
            bild.setDevicePixelRatio(dpr)
        return bild

    def _ueberlagerung(self):
        """Was über dem Text liegt, als Angaben für das Framework (gezeichnet wird es nicht hier); → (Seite, Rechteck) der Schreibmarke oder ``None``."""
        hell = self.palette().color(QPalette.Highlight)
        wellen = [(fund.von, fund.bis, WELLEN_FARBE.get(fund.art, WELLEN_STANDARD)) for fund in self.wellen[:3000]]
        treffer = [(von, bis) for von, bis in self.suchtreffer[:2000]]
        return AN.ueberlagerung_setzen(self.kennung, self.formatzeichen, (hell.red(), hell.green(), hell.blue(), AUSWAHL_DECKKRAFT), self.gitter, self.textgrenzen,
                                       self.lesefokus, self.zeilenfokus, self.papier, self.markup, AUTOR_FARBEN, wellen, treffer)

    def _ueberlagerungsbild(self, i: int, dpr: float):
        """Die durchsichtige Ebene des Blattes ``i`` — vom Framework gerendert, bis sich ihr Inhalt, der Zoom oder das Layout ändert."""
        nummer, leer = AN.ueberlagerung_stand(self.kennung, i, self.zoom * dpr)
        schluessel = (nummer, dpr)
        c = self._ueberlagerungscache
        if c.get(i, (None,))[0] == schluessel:
            return c[i][1]
        bild = None
        if not leer:
            breite, hoehe, roh = AN.ueberlagerungsbild(self.kennung, i, self.zoom * dpr)
            bild = QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888).copy()
            bild.setDevicePixelRatio(dpr)
        c[i] = (schluessel, bild)
        return bild

    def paintEvent(self, ev) -> None:
        erg = self.ergebnis()
        if self._ueberlagerungscache_erg is not erg:
            self._ueberlagerungscache, self._ueberlagerungscache_erg = {}, erg
        p = QPainter(self)
        marke = self._ueberlagerung()
        auswahl_leer = ST.auswahl(self.kennung).leer
        sicht = QRectF(ev.rect())
        for i in range(len(erg.seiten)):
            blatt = self.blatt(i)
            if not blatt.intersects(sicht):
                continue
            bild = self._seitenbild(erg, i)
            dpr = bild.devicePixelRatio()
            ort = QPointF(round(blatt.x() * dpr) / dpr, round(blatt.y() * dpr) / dpr)
            p.drawImage(ort, bild)                                                          # Blatt, Überlagerung und Schreibmarke: fertige Bilder des Kerns, Pixel 1:1
            ueber = self._ueberlagerungsbild(i, dpr)
            if ueber is not None:
                p.drawImage(ort, ueber)
            p.save()
            p.setClipRect(blatt)
            p.translate(blatt.topLeft())
            p.scale(self.zoom, self.zoom)
            self.objekt_zeichnen(p, i)                                     # Griffe und Rahmen zum Bedienen des gewählten Objekts
            p.restore()
            if marke is not None and marke[0] == i and self._an and self.hasFocus() and not self.nur_lesen and auswahl_leer:
                x, y, (b, h, roh) = AN.cursorbild(self.kennung, self.zoom * dpr, Farbe.SCHWARZ)
                cur = QImage(roh, b, h, b * 4, QImage.Format_RGBA8888).copy()
                cur.setDevicePixelRatio(dpr)
                p.drawImage(QPointF(ort.x() + x / dpr, ort.y() + y / dpr), cur)
        self.knoepfe_zeichnen(p)
        self.tabellen_zeichnen(p)
        self.blasen_zeichnen(p)
        if self.nach_zeichnen is not None:
            self.nach_zeichnen(p)
        p.end()

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
