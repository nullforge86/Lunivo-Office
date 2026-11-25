"""Formular, das sich der Breite anpasst — der Baustein für Felder in Zusatzfenstern (Seitenleiste) und in breiten Fenstern.

Statt Felder in feste Spalten eines ``QGridLayout`` zu setzen, nennt man nur, was zusammengehört:

    f = FormularGitter(gruppe)                       # Layout für eine Gruppe oder Seite
    f.zeile("Vor Text:", self.links)                 # Beschriftung + Feld
    f.zeile("Sondereinzug:", self.sonder)
    f.breit(self.rest_einzug)                        # ein Feld über die ganze Breite (Ankreuzfeld, Liste, Vorschau …)

Das Gitter entscheidet bei jeder Breite neu: reicht der Platz, stehen zwei Paare nebeneinander; sonst eines je Zeile mit der Beschriftung links;
ist es noch enger, steht die Beschriftung über dem Feld. Nichts wird abgeschnitten, kein seitliches Rollen. ``UmbruchSchalter`` ist ein
Ankreuzfeld, dessen langer Text in die nächste Zeile läuft.
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.darstellung import eigenschaft


from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QAbstractSpinBox, QComboBox, QGridLayout, QPushButton, QTabWidget, QCheckBox, QLabel, QLayout, QLayoutItem, QSizePolicy, QStyle, QStyleOptionButton, QWidget)
from lunivo_writer.oberflaeche.baukasten.basis.raster import Anordnung, PlanRaster, RasterLayout, kanten_anordnung
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_UNTER_REITER, MARGIN_OBEN_GRUPPE_ZUSATZ, PADDING_ABSCHNITTSBAND, PADDING_ABSCHNITT_KNOPF, PADDING_GRUPPE_OBEN, PADDING_GRUPPENTITEL, RAND_KEIN, SCHRIFT_KLEIN

ABSTAND = 6
SPALTEN_ABSTAND = 10


def tabellen_gitter(eltern: QWidget | None = None, *, rand: tuple | None = RAND_KEIN, abstand: int | None = None,
                    waagerecht: int | None = None, senkrecht: int | None = None, oben_links: bool = False) -> QGridLayout:
    """DIE eine Stelle im Projekt, an der ein ``QGridLayout`` erzeugt wird. Für Zellen, deren Spalten feste Aufgaben haben (Kachelraster, Zwei-Listen-Gerüst,
    Menüband-Zellen mit Beschriftung und Maßfeld), nicht für Felder: Felder gehören in ``FormularGitter``, Kachelreihen in ``kachel_gitter`` (karten_raster.py).
    ``abstand`` setzt beide Abstände, ``waagerecht``/``senkrecht`` einzeln; ``oben_links``: Zellen bleiben links oben stehen, statt sich zu verteilen."""
    g = RasterLayout(eltern) if eltern is not None else RasterLayout()
    if rand is not None:                                      # ``None``: Standardrand des Stils
        g.setContentsMargins(*rand)
    if abstand is not None:
        g.setSpacing(abstand)
    if waagerecht is not None:
        g.setHorizontalSpacing(waagerecht)
    if senkrecht is not None:
        g.setVerticalSpacing(senkrecht)
    if oben_links:
        g.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    return g


class UmbruchSchalter(QCheckBox):
    """Ankreuzfeld, dessen Text bei Platzmangel umbricht (``QCheckBox`` selbst kann das nicht)."""

    def __init__(self, text: str = "", parent: QWidget | None = None):
        super().__init__(text, parent)
        sp = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        sp.setHeightForWidth(True)
        self.setSizePolicy(sp)

    def natuerliche_breite(self) -> int:
        """Breite des Ankreuzfelds in einer Zeile, ohne Umbruch (damit kurz/lang richtig entschieden wird; ``sizeHint`` ist wegen des Umbruchs klein)."""
        from PySide6.QtGui import QFontMetrics
        return QFontMetrics(self.font()).horizontalAdvance(self.text().replace("&", "")) + self._indikator()

    def _indikator(self) -> int:
        o = QStyleOptionButton(); self.initStyleOption(o)
        return self.style().subElementRect(QStyle.SE_CheckBoxIndicator, o, self).right() + 8

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, breite: int) -> int:
        rand = self._indikator()
        r = self.fontMetrics().boundingRect(QRect(0, 0, max(40, breite - rand), 10000), Qt.TextWordWrap | Qt.TextShowMnemonic, self.text())
        return max(self.fontMetrics().height() + 6, r.height() + 6)

    def sizeHint(self) -> QSize:
        return QSize(self._indikator() + self.fontMetrics().horizontalAdvance(self.text().replace("&", "")), self.heightForWidth(10000))

    def minimumSizeHint(self) -> QSize:
        return QSize(self._indikator() + 60, self.heightForWidth(self._indikator() + 60))

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        o = QStyleOptionButton(); self.initStyleOption(o)
        o.text = ""
        self.style().drawControl(QStyle.CE_CheckBox, o, p, self)
        rand = self._indikator()
        p.setPen(self.palette().color(self.foregroundRole() if self.isEnabled() else self.palette().ColorRole.WindowText))
        if not self.isEnabled():
            p.setPen(self.palette().color(self.palette().ColorGroup.Disabled, self.palette().ColorRole.WindowText))
        p.drawText(QRect(rand, 0, self.width() - rand, self.height()), Qt.TextWordWrap | Qt.TextShowMnemonic | Qt.AlignVCenter | Qt.AlignLeft, self.text())


class FlussLayout(PlanRaster):
    """Elemente in gleich breiten Gitterspalten, die umbrechen: so viele Spalten, wie in die Breite passen, der Rest in den nächsten
    Gitterzeilen — Ankreuzfelder, Optionen und Knöpfe stehen dadurch in sauberen Spalten untereinander. Eine Beschriftung und das Feld dahinter
    bleiben eine Einheit (Beschriftungs- und Feldspalte). ``zentriert``: die Spalten stehen mittig statt links."""

    def __init__(self, abstand: int = 6, zentriert: bool = False):
        super().__init__()
        self._abstand = abstand
        self._zentriert = zentriert

    def _neu_aufnehmen(self, it) -> None:
        self.invalidate()

    def _einheiten(self) -> list[list]:
        """Beschriftung + nächstes Feld sind eine Einheit, alles andere steht für sich (ausgeblendete Elemente zählen nicht)."""
        items = [i for i in self.elemente() if not i.isEmpty()]
        out, i = [], 0
        while i < len(items):
            it = items[i]
            if isinstance(it.widget(), QLabel) and i + 1 < len(items) and not isinstance(items[i + 1].widget(), QLabel):
                out.append([it, items[i + 1]]); i += 2
            else:
                out.append([it]); i += 1
        return out

    def _masse(self, einheiten: list) -> tuple[int, int, int]:
        """→ (Breite der Beschriftungsspalte, Breite der Feldspalte, Breite einer Einheit)."""
        nat = lambda i: max(_natuerlich(i), i.minimumSize().width())
        lb = max((nat(e[0]) for e in einheiten if len(e) == 2), default=0)
        fb = max((nat(e[1]) for e in einheiten if len(e) == 2), default=0)
        for e in einheiten:
            if len(e) == 1:
                fb = max(fb, nat(e[0]) - (lb + self._abstand if lb else 0))
        return lb, fb, lb + (self._abstand if lb else 0) + fb

    def spalten(self, breite: int) -> int:
        einheiten = self._einheiten()
        if not einheiten:
            return 1
        b = self._masse(einheiten)[2]
        return max(1, min(len(einheiten), (breite + self._abstand) // max(1, b + self._abstand)))

    def _anordnung(self, breite: int) -> Anordnung:
        einheiten = self._einheiten()
        a = self._abstand
        an = Anordnung(waagerecht=a, senkrecht=a)
        if not einheiten:
            return an
        lb, fb, _ub = self._masse(einheiten)
        n = self.spalten(breite)
        je = 2 if lb else 1                                                  # Gitterspalten je Einheit
        start = 0
        hoehen: dict[int, int] = {}
        for k, e in enumerate(einheiten):
            zl, sp = divmod(k, n)
            c = start + sp * je
            if len(e) == 2:
                an.zellen.append((e[0], zl, c, 1, 1, Qt.AlignVCenter | Qt.AlignLeft))
                an.zellen.append((e[1], zl, c + 1, 1, 1, Qt.AlignVCenter))
            else:
                an.zellen.append((e[0], zl, c, 1, je, Qt.AlignVCenter))
            hoehen[zl] = max([hoehen.get(zl, 0)] + [i.sizeHint().height() for i in e])
        for sp in range(n):
            c = start + sp * je
            if lb:
                an.spalten[c] = lb
            an.spalten[c + je - 1] = fb
            an.spalten_dehnung[c + je - 1] = 0 if self._zentriert else 1
        an.hoehe = sum(hoehen.values()) + a * (len(hoehen) - 1)
        return an

    def setGeometry(self, r) -> None:
        """``zentriert``: das ganze Gitter (nicht jedes Element) steht mittig in der verfügbaren Breite."""
        if self._zentriert and self._einheiten():
            m = self.contentsMargins()
            innen = max(1, r.width() - m.left() - m.right())
            n, ub = self.spalten(innen), self._masse(self._einheiten())[2]
            b = min(r.width(), n * ub + (n - 1) * self._abstand + m.left() + m.right())
            r = r.adjusted((r.width() - b) // 2, 0, 0, 0); r.setWidth(b)
        super().setGeometry(r)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        m = self.contentsMargins()
        einheiten = self._einheiten()
        b = self._masse(einheiten)[2] if einheiten else 0
        h = max((i.sizeHint().height() for e in einheiten for i in e), default=0)
        return QSize(b + m.left() + m.right(), h + m.top() + m.bottom())


def abschnittstitel(text: str) -> QLabel:
    """Die Überschrift eines Abschnitts: klein, gedämpft, Großbuchstaben — überall gleich (Gruppen, Spalten, Bereiche in Fenstern)."""
    l = QLabel(text.rstrip(":").replace("ß", "ẞ").upper())          # ß groß als ẞ, nicht „SS“
    l.setObjectName("abschnittTitel")
    eigenschaft(l, rolle="abschnittsbeschriftung")
    return l


def reiter_knopf_stil(knopf: QWidget) -> None:
    """Der Reiterknopf (``QToolButton``, ``checkable``) mit Unterstrich in der Hervorhebungsfarbe — für selbst gebaute Reiterleisten."""
    eigenschaft(knopf, rolle="abschnittsknopf")


def abschnittsband(text: str) -> QLabel:
    """Eine Überschrift als graues Band über einer Gruppe von Kacheln (Menüs mit mehreren Gruppen); Schriftgröße der Oberfläche."""
    t = QLabel(text)
    eigenschaft(t, rolle="abschnittsband")
    return t


def mittig(widget: QWidget) -> QWidget:
    """Ein Element fester Größe (Vorschau, Farbraster …) in der Mitte der Breite."""
    host = QWidget()
    g = tabellen_gitter(host, rand=RAND_KEIN, oben_links=False)
    g.setColumnStretch(0, 1)
    g.addWidget(widget, 0, 1, Qt.AlignCenter)
    g.setColumnStretch(2, 1)
    return host


class _Einheit:
    """Ein Paar (Beschriftung + Feld) oder ein breites Element."""

    def __init__(self, beschriftung: QLayoutItem | None, feld: QLayoutItem, reihe: list | None = None, gewichte: tuple | None = None):
        self.b, self.f = beschriftung, feld
        self.reihe, self.gewichte = reihe, gewichte                       # Felder mit der Beschriftung darüber: [(Beschriftung, Feld), …]


def _hoehe_bei(item: QLayoutItem, breite: int) -> int:
    if item.hasHeightForWidth():
        return item.heightForWidth(max(1, breite))
    return item.sizeHint().height()


def _natuerlich(item: QLayoutItem) -> int:
    w = item.widget()
    if w is not None and hasattr(w, "natuerliche_breite"):             # ein Widget mit Umbruch (Policy „Ignored“) meldet über das Layout sonst Breite 0
        return w.natuerliche_breite()
    return max(item.sizeHint().width(), item.minimumSize().width())


FELDHOEHE = 32                                                # einzeilige Felder (Zahl, Text, Farbe) in der Feldspalte der Seitenleiste: alle gleich hoch; Dropdowns nicht: ihre Höhe kommt aus DROPDOWN_HOEHE (mass.py)
_EINZEILIG = ("QComboBox", "QPushButton", "QLineEdit", "QDoubleSpinBox", "QSpinBox", "FarbFeld", "KopfDropdown", "SchrittFeld", "StrichAuswahl")


def ist_dropdown(w: QWidget | None) -> bool:
    """Ein Dropdown (Auswahlfeld, Schriftauswahl, Dropdown-Taste, Kopf-Dropdown, Strichart, Farbfeld; Knöpfe tragen die Eigenschaft ``dropdownFeld``):
    seine Höhe bestimmt allein ``DROPDOWN_HOEHE``; dieses Gitter setzt keine eigene."""
    return isinstance(w, QComboBox) or bool(w is not None and w.property("dropdownFeld"))


def einzeilig(item: QLayoutItem) -> bool:
    w = item.widget()
    return w is not None and any(c.__name__ in _EINZEILIG for c in type(w).__mro__)


def felder_angleichen(wurzel: QWidget) -> None:
    """Alle einzeiligen Felder (Zahl, Text, Farbe) und beschriftete Knöpfe unter ``wurzel`` auf ``FELDHOEHE``; Dropdowns bleiben bei ``DROPDOWN_HOEHE``. Auch für
    Felder, die nicht im ``FormularGitter`` mit Feldspalte stehen (Einheitenfelder, Unterfenster). Knöpfe fester Größe (Kacheln, Symbole) bleiben."""
    for w in wurzel.findChildren(QWidget):
        if ist_dropdown(w) or isinstance(w.parent(), (QAbstractSpinBox, QComboBox)) or not any(c.__name__ in _EINZEILIG for c in type(w).__mro__):
            continue
        if isinstance(w, QPushButton) and (not w.text() or (w.minimumWidth() == w.maximumWidth() and w.minimumWidth() > 0)):
            continue
        w.setFixedHeight(FELDHOEHE)


class FormularGitter(PlanRaster):
    """Formular als ``QGridLayout``: bei jeder Breite werden Beschriftungen und Felder neu auf Gitterzellen verteilt (zwei Paare nebeneinander,
    eines je Zeile oder Beschriftung darüber); die Gitterlinien liegen an den Kanten der Elemente (``kanten_anordnung``)."""
    _einheiten: list = []
    einspaltig = False                                        # True: nie zwei Paare nebeneinander (z. B. Dateiname/Dateityp mit Knopf daneben, Kennwortfelder)
    # Rhythmus-Optionen: Vorgaben = Seitenleiste; Fenster mit eigenem, früher festgelegtem Rhythmus (Optionen, Dateifenster) setzen sie, statt ein eigenes Gitter zu bauen
    zeilenabstand = ABSTAND                                   # senkrechter Abstand zwischen den Zeilen
    beschriftungsabstand = ABSTAND                            # Abstand zwischen Beschriftung (links) und Feld
    beschriftung_voll = False                                 # True: die Beschriftung füllt die Zeilenhöhe (Text bleibt mittig) statt nur ihre eigene Höhe
    beschriftung_natuerlich = False                           # True: jede Beschriftung nur so breit wie ihr Text (Felder beginnen trotzdem in einer Spalte)
    kurz_gruppen = True                                       # False: Ankreuzfelder/Knöpfe nie zu zweit nebeneinander
    angleichen = True                                         # False: Höhen der Felder bleiben, wie sie sind
    feldbreite = 0                                            # > 0: Felder in fester Breite rechtsbündig, Beschriftungen links (Seitenleiste „Formatierung“); 0: Feld füllt den Rest

    def __init__(self, parent: QWidget | None = None):
        self._einheiten: list[_Einheit] = []
        super().__init__(parent)
        self.setContentsMargins(*RAND_KEIN)

    # ---- Aufbau ----------------------------------------------------------------------------------------
    def _nimm(self, objekt) -> QLayoutItem:
        if isinstance(objekt, str):
            objekt = QLabel(objekt)
        if isinstance(objekt, QWidget):
            return self.element_widget(objekt)
        return self.element_layout(objekt)

    def zeile(self, beschriftung, feld) -> None:
        """Beschriftung (Text oder Widget) und das Feld (Widget oder Layout) dahinter."""
        b = self._nimm(beschriftung)
        if isinstance(beschriftung, str) or isinstance(beschriftung, QLabel):
            w = b.widget()
            if isinstance(w, QLabel):
                w.setWordWrap(False)
                if isinstance(feld, QWidget):
                    w.setBuddy(feld)
        self._einheiten.append(_Einheit(b, self._nimm(feld)))
        self.invalidate()

    def breit(self, objekt) -> None:
        self._einheiten.append(_Einheit(None, self._nimm(objekt)))
        self.invalidate()

    def nebeneinander(self, *felder, spalten: int | None = None, abstand: int = SPALTEN_ABSTAND) -> None:
        """Felder ohne Beschriftung gleich breit in einer Zeile; ``spalten`` größer als die Zahl der Felder lässt den Rest der Zeile frei (halbe Zeile)."""
        z = tabellen_gitter(rand=RAND_KEIN, waagerecht=abstand, senkrecht=0)
        anzahl = max(len(felder), spalten or len(felder))
        for i, f in enumerate(felder):
            z.addWidget(f, 0, i)
        for i in range(anzahl):
            z.setColumnStretch(i, 1)
        self.breit(z)

    def reihe(self, *paare, gewichte: tuple | None = None, vorn: bool = False) -> None:
        """Mehrere Felder nebeneinander, jedes mit der Beschriftung darüber: ``reihe(("Schriftart:", a), ("Größe:", b), gewichte=(3, 1))``.
        Zu eng für eine Zeile, brechen die Felder um (im Äußersten eines je Zeile)."""
        liste = []
        for b, f in paare:
            bi = self._nimm(b)
            if isinstance(bi.widget(), QLabel):
                bi.widget().setWordWrap(False)
            liste.append((bi, self._nimm(f)))
        self._einheiten.insert(0 if vorn else len(self._einheiten), _Einheit(None, liste[0][1], liste, gewichte))      # ``vorn``: als erste Reihe
        self.invalidate()

    # ---- Elemente ------------------------------------------------------------------------------------
    def _neu_aufnehmen(self, item: QLayoutItem) -> None:            # ``addWidget``/``addItem`` von QLayout: wie ``breit``
        self._einheiten.append(_Einheit(None, item))
        self.invalidate()

    def _vergessen(self, it: QLayoutItem) -> None:
        s = self._schluessel(it)
        k = lambda x: x is not None and self._schluessel(x) is s
        self._einheiten = [e for e in self._einheiten if not k(e.f) and not k(e.b)]

    def sizeHint(self) -> QSize:
        m = self.contentsMargins()
        paare = [e for e in self._einheiten if e.b is not None and e.reihe is None]
        bw = max((_natuerlich(e.b) for e in paare), default=0)                    # alle Felder beginnen in EINER Spalte: längste Beschriftung + breitestes Feld
        fw = max((_natuerlich(e.f) for e in paare), default=0)
        breit = max([bw + self.beschriftungsabstand + fw if paare else 0] + [_natuerlich(e.f) for e in self._einheiten if e.b is None and e.reihe is None])
        return QSize(breit + m.left() + m.right(), self.heightForWidth(max(breit, 1) + m.left() + m.right()))

    def minimumSize(self) -> QSize:
        m = self.contentsMargins()
        schmal = max((max(e.f.minimumSize().width(), e.b.minimumSize().width() if e.b is not None else 0) for e in self._einheiten if e.reihe is None), default=0)
        for e in self._einheiten:
            for b, f in (e.reihe or []):
                schmal = max(schmal, b.minimumSize().width(), f.minimumSize().width())
        return QSize(schmal + m.left() + m.right(), self.heightForWidth(self.sizeHint().width()))   # so hoch wie bei natürlicher Breite: nichts wird gequetscht

    def _anordnung(self, breite: int) -> Anordnung:
        plaetze, hoehe = self._plan(breite)
        return kanten_anordnung(plaetze, breite, hoehe)

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self._beschriftungen_nachfuehren()

    def _beschriftungen_nachfuehren(self) -> None:
        """Ein ausgeblendetes Feld nimmt seine Beschriftung mit (sonst bliebe sie als Waise am alten Platz stehen); wird das Feld wieder gezeigt, kommt sie zurück."""
        versteckt = self.__dict__.setdefault("_versteckt", set())
        for e in self._einheiten:
            for b, f in (e.reihe or ([(e.b, e.f)] if e.b is not None else [])):
                w = b.widget() if b is not None else None
                if w is None:
                    continue
                if f.isEmpty() and w.isVisibleTo(w.parentWidget() or w):
                    w.setVisible(False); versteckt.add(w)
                elif not f.isEmpty() and w in versteckt:
                    w.setVisible(True); versteckt.discard(w)

    # ---- die Anordnung ---------------------------------------------------------------------------------
    def _reihe_legen(self, e: _Einheit, breite: int, y: int, out: list) -> int:
        felder = e.reihe
        gew = list(e.gewichte or (1,) * len(felder))
        nat = [max(_natuerlich(b), min(_natuerlich(f), 260)) for b, f in felder]
        zeilen, akt, summe = [], [], 0
        for k, w in enumerate(nat):                                               # so viele wie passen in eine Zeile, der Rest darunter
            if akt and summe + w + SPALTEN_ABSTAND > breite:
                zeilen.append(akt); akt, summe = [], 0
            akt.append(k); summe += w + (SPALTEN_ABSTAND if len(akt) > 1 else 0)
        zeilen.append(akt)
        for z in zeilen:
            frei = breite - (len(z) - 1) * SPALTEN_ABSTAND
            tw = sum(gew[k] for k in z)
            x, hmax = 0, 0
            for n, k in enumerate(z):
                w = frei - sum(int(frei * gew[j] / tw) for j in z[:-1]) if n == len(z) - 1 else int(frei * gew[k] / tw)
                b, f = felder[k]
                hb = b.sizeHint().height(); hf = _hoehe_bei(f, w)
                out.append((b, x, y, w, hb)); out.append((f, x, y + hb + 2, w, hf))
                hmax = max(hmax, hb + 2 + hf); x += w + SPALTEN_ABSTAND
            y += hmax + self.zeilenabstand
        return y

    def _kurz(self, e: _Einheit, breite: int) -> bool:
        """Ein einzelnes Ankreuzfeld, Optionsfeld oder ein Knopf, der höchstens eine halbe Zeile braucht."""
        w = e.f.widget()
        if not self.kurz_gruppen or w is None or e.reihe is not None or e.b is not None:
            return False
        if w.property("einspaltig"):                                              # z. B. Füllungsart/Linienart: immer eine Option je Zeile
            return False
        if not any(c.__name__ in ("QCheckBox", "QRadioButton", "QPushButton", "QToolButton") for c in type(w).__mro__):
            return False
        return _natuerlich(e.f) <= (breite - SPALTEN_ABSTAND) // 2

    def _gleich_hoch(self) -> None:
        """Alle einzeiligen Bedienelemente (Menü, Zahl, Text, Knopf) dieses Formulars gleich hoch: die Höhe des höchsten natürlichen Elements, ohne feste Pixelwerte."""
        if not self.angleichen:
            return
        ws: list[QWidget] = []

        def sammle(item) -> None:
            if item is None:
                return
            if item.widget() is not None:
                if einzeilig(item):
                    ws.append(item.widget())
            elif item.layout() is not None:
                for i in range(item.layout().count()):
                    sammle(item.layout().itemAt(i))
        for it in self.elemente():
            sammle(it)
        if len(ws) < 2:
            return
        h = max((w.sizeHint().height() for w in ws if w.sizeHint().height() <= 40), default=0)       # ein ungewöhnlich hohes Element (Bildknopf) bestimmt die Höhe nicht
        for w in ws:
            if h and w.minimumHeight() < h <= w.maximumHeight() and not ist_dropdown(w):         # Dropdowns behalten DROPDOWN_HOEHE
                w.setMinimumHeight(h)

    def _plan(self, breite: int):
        """→ ([(Element, x, y, Breite, Höhe)], Gesamthöhe) bei dieser Breite."""
        self._gleich_hoch()
        einheiten = [e for e in self._einheiten if not e.f.isEmpty()]            # ausgeblendete Felder (und Feldgruppen) lassen keinen Abstand stehen
        bw, spalten, gestapelt = self._spaltenmass([e for e in einheiten if e.b is not None], breite)
        out, y = [], 0
        i = 0
        n = len(einheiten)
        while i < n:
            e = einheiten[i]
            if e.reihe is not None:
                y = self._reihe_legen(e, breite, y, out); i += 1
            elif e.b is None:                                                     # breites Element: eine ganze Zeile
                y, i = self._breit_legen(einheiten, i, breite, y, out)
            else:
                zeile = [e]
                while spalten == 2 and len(zeile) < 2 and i + len(zeile) < n and einheiten[i + len(zeile)].b is not None:
                    zeile.append(einheiten[i + len(zeile)])
                y = self._paarzeile_legen(zeile, (breite, bw, gestapelt), y, out)
                i += len(zeile)
        return out, max(0, y - self.zeilenabstand)

    def _spaltenmass(self, paare: list, breite: int) -> tuple:
        """→ (Breite der Beschriftungen, Spaltenzahl, Beschriftung darüber?)."""
        bw = max((_natuerlich(e.b) for e in paare), default=0)                    # Breite der Beschriftungen
        fw = max((_natuerlich(e.f) for e in paare), default=0)                    # Breite, die ein Feld gern hätte
        wunsch = bw + self.beschriftungsabstand + fw
        spalten = 2 if paare and not self.einspaltig and 2 * wunsch + SPALTEN_ABSTAND <= breite else 1
        gestapelt = bool(paare) and wunsch > breite                               # zu eng für „Beschriftung links“: darüber
        if self.feldbreite and paare:                                             # feste Feldspalte: nur zu schmal für Beschriftung + Feld → Beschriftung darüber
            gestapelt = breite < self.feldbreite + self.beschriftungsabstand + 90
            spalten = 1
            bw = max(0, breite - self.feldbreite - self.beschriftungsabstand)
        return bw, spalten, gestapelt

    def _breit_legen(self, einheiten: list, i: int, breite: int, y: int, out: list) -> tuple:
        """Ein Element ohne Beschriftung; kurze Einzelelemente (Ankreuzfeld, Option, Knopf) stehen zu zweit/zu dritt nebeneinander. → (y, i)."""
        e = einheiten[i]
        if self._kurz(e, breite):
            for n_sp in (3, 2):
                gruppe = einheiten[i:i + n_sp]
                cw = (breite - (n_sp - 1) * SPALTEN_ABSTAND) // n_sp
                if len(gruppe) == n_sp and all(g.reihe is None and g.b is None and self._kurz(g, breite) and _natuerlich(g.f) <= cw for g in gruppe):
                    h = max(_hoehe_bei(g.f, cw) for g in gruppe)
                    for k, g in enumerate(gruppe):
                        out.append((g.f, k * (cw + SPALTEN_ABSTAND), y, cw, h))
                    return y + h + self.zeilenabstand, i + n_sp
        h = _hoehe_bei(e.f, breite)
        out.append((e.f, 0, y, breite, h))
        return y + h + self.zeilenabstand, i + 1

    def _paarzeile_legen(self, zeile: list, mass: tuple, y: int, out: list) -> int:
        """Eine Zeile aus ein oder zwei Beschriftung/Feld-Paaren. → neues y."""
        breite, bw, gestapelt = mass
        sp = (breite - (len(zeile) - 1) * SPALTEN_ABSTAND) // len(zeile) if len(zeile) > 1 else breite
        hmax = 0
        plaetze = []
        for k, u in enumerate(zeile):
            x0 = k * (sp + SPALTEN_ABSTAND)
            if gestapelt:
                hb = u.b.sizeHint().height()
                hf = _hoehe_bei(u.f, sp)
                plaetze.append((u.b, x0, 0, sp, hb)); plaetze.append((u.f, x0, hb + 2, sp, hf)); hmax = max(hmax, hb + 2 + hf)
            else:
                pl, h = self._paar_daneben(u, x0, sp, bw)
                plaetze += pl; hmax = max(hmax, h)
        for it, x, dy, w, h in plaetze:
            out.append((it, x, y + dy, w, h))
        return y + hmax + self.zeilenabstand

    def _paar_daneben(self, u, x0: int, sp: int, bw: int) -> tuple:
        """Beschriftung links, Feld rechts. → ([Plätze], Zeilenhöhe)."""
        fb = self.feldbreite if self.feldbreite else max(40, sp - bw - self.beschriftungsabstand)
        hf = _hoehe_bei(u.f, fb)
        if self.feldbreite and einzeilig(u.f) and not ist_dropdown(u.f.widget()):
            u.f.widget().setFixedHeight(FELDHOEHE); hf = FELDHOEHE
        hb = u.b.sizeHint().height()
        h = max(hb, hf)
        bb = min(bw, _natuerlich(u.b)) if self.beschriftung_natuerlich else bw
        beschr = (u.b, x0, 0, bb, h) if self.beschriftung_voll else (u.b, x0, (h - hb) // 2, bb, hb)
        feld = (u.f, x0 + sp - fb if self.feldbreite else x0 + bw + self.beschriftungsabstand, 0, fb, hf)
        return [beschr, feld], h


class AngepassteReiter(QTabWidget):
    """Reiter, deren Höhe dem gewählten Reiter folgt (ein ``QTabWidget`` richtet sich sonst nach dem höchsten und lässt kürzeren Reitern leeren Platz)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        from lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste import HAUPT, FlacheReiterLeiste
        self.setTabBar(FlacheReiterLeiste(HAUPT))          # EINE Reiterleiste für alle Fenster: flach, die Beschriftung bricht um, nichts wird abgeschnitten
        self.currentChanged.connect(self._aktuelle_seite)
        self.setUsesScrollButtons(False)

    def _aktuelle_seite(self, _i: int = 0) -> None:
        """Nur die gewählte Seite bestimmt die Höhe: die anderen zählen für das Layout nicht mit (sonst bleibt unter kürzeren Reitern leerer Platz)."""
        for k in range(self.count()):
            w = self.widget(k)
            sp = w.sizePolicy()
            sp.setVerticalPolicy(QSizePolicy.Preferred if k == self.currentIndex() else QSizePolicy.Ignored)
            w.setSizePolicy(sp)
        self.updateGeometry()
        e = self.parentWidget()
        while e is not None:                                      # die Layouts darüber merken sich sonst die Höhe des vorigen Reiters
            if e.layout() is not None:
                e.layout().invalidate()
            e = e.parentWidget()

    def tabInserted(self, index: int) -> None:
        super().tabInserted(index)
        self._aktuelle_seite()
        self.tabBar().setTabToolTip(index, self.tabText(index))

    def _mass(self, minimum: bool) -> QSize:
        w = self.currentWidget()
        if w is None:
            return super().minimumSizeHint() if minimum else super().sizeHint()
        ws = w.minimumSizeHint() if minimum else w.sizeHint()
        h = max(ws.height(), w.minimumHeight())                                       # ein Reiter mit fester Höhe (zum Beispiel Kachelraster) gilt mit dieser
        if w.maximumHeight() < 16777215:
            h = min(h, w.maximumHeight())
        ws = QSize(ws.width(), h)
        tb = self.tabBar().sizeHint()
        return QSize(ws.width() + 6, ws.height() + tb.height() + 8 + ABSTAND_UNTER_REITER)               # die Leiste kürzt ihre Namen, sie bestimmt die Breite nicht

    def hasHeightForWidth(self) -> bool:
        w = self.currentWidget()
        return w is not None and w.hasHeightForWidth()

    def heightForWidth(self, breite: int) -> int:
        """Die Höhe der gewählten Seite bei dieser Breite (Seiten aus ``FormularGitter`` brechen um): so bleibt unter kürzeren Reitern kein leerer Platz."""
        w = self.currentWidget()
        tb = self.tabBar().sizeHint()
        return w.heightForWidth(max(1, breite - 6)) + tb.height() + 8 + ABSTAND_UNTER_REITER

    def sizeHint(self) -> QSize:
        return self._mass(False)

    def minimumSizeHint(self) -> QSize:
        return self._mass(True)


def gruppe(titel: str, *, karte: bool = False):
    """Eine Gruppe von Feldern mit Titel: flach wie die Abschnittstitel (Großbuchstaben, Linie darüber); ``karte=True`` = Gruppenkasten des Stils
    (Optionenseiten). EINE Stelle für alle Gruppen in Fenstern und Seitenleiste."""
    from PySide6.QtWidgets import QGroupBox
    g = QGroupBox(titel if karte else titel.rstrip(":").upper())
    if karte:
        g.setProperty("gruppenart", "karte")                      # Aussehen: baukasten/basis/dashboard_regeln.py
    else:
        g.setProperty("gruppenart", "flach")                       # Aussehen: baukasten/basis/dashboard_regeln.py
    return g