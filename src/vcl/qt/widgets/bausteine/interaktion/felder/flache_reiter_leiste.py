from __future__ import annotations
from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPalette, QPolygonF
from PySide6.QtWidgets import QTabBar, QTabWidget
from vcl.qt.widgets.menues.dropdown.dropdown_knopf import DropdownTaste
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_UNTER_REITER, DROPDOWN_HOEHE, REITER_DROPDOWN_RAND


HAUPT, UNTER = "haupt", "unter"


_RAND = 6                      # Abstand der Beschriftung zum Rand des Reiters


_SYMBOL = 18


_PFEIL = 18                    # Platz für den Teil-Pfeil „▾“ hinter dem Text des Hauptreiters (mit ``TeilMenueKnopf`` als Reiterknopf)


def _gross(text: str) -> str:
    return text                                           # Schreibweise wie im Reiter (die Seitenleisten-Fenster zeigen ihre Reiter ebenso)


def _mische(a: QColor, b: QColor, anteil: float) -> QColor:
    """Farbe a zum Anteil (0…1) mit b gemischt."""
    return QColor(round(a.red() + (b.red() - a.red()) * anteil), round(a.green() + (b.green() - a.green()) * anteil),
                  round(a.blue() + (b.blue() - a.blue()) * anteil))


class ReiterDropdown:
    """Die Leiste als ein Dropdown (statt vieler Reiter nebeneinander): Taste mit dem Namen des aktuellen Reiters, Liste aller sichtbaren Reiter mit Haken am aktuellen;
    nicht wählbare Reiter stehen grau. Reihenfolge: ``class X(ReiterDropdown, QTabBar)``."""

    def _wahl_einrichten(self) -> None:
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        self._wahl = DropdownTaste(self)
        self._wahl.setCursor(Qt.PointingHandCursor); self._wahl.setAccessibleName("Reiter wählen")
        self._wahl_liste = MenueListe(self._wahl)             # die Liste wird bei jedem Öffnen frisch gefüllt (Namen, grau, Haken)
        self._wahl_liste.aboutToShow.connect(self._wahl_fuellen)
        self._wahl.menue_setzen(self._wahl_liste, geteilt=False)
        self._wahl.hide()

    def _wahl_zeigen(self, an: bool) -> None:
        """Dropdown ein/aus; Name und Lage nachziehen."""
        self._wahl.setVisible(an)
        if not an:
            return
        self._wahl.setGeometry(0, REITER_DROPDOWN_RAND, self.width(), DROPDOWN_HOEHE)
        text = self.tabText(self.currentIndex()) if self.currentIndex() >= 0 else ""
        self._wahl.setText(self._wahl.fontMetrics().elidedText(text, Qt.ElideMiddle, max(10, self.width() - 3 * _RAND - _PFEIL)))
        self._wahl.setToolTip(text); self._wahl.raise_()

    def _wahl_fuellen(self) -> None:
        m = self._wahl_liste
        m.clear()
        for i in range(self.count()):
            if self.isTabVisible(i):
                m.eintrag(self.tabText(i), lambda i=i: self.setCurrentIndex(i), haken=i == self.currentIndex(), aktiv=self.isTabEnabled(i))
        m.setMinimumWidth(self._wahl.width())


class FlacheReiterLeiste(ReiterDropdown, QTabBar):
    def __init__(self, art: str = UNTER, parent=None):
        super().__init__(parent)
        self._art = art
        self._letzte_hoehe = 0
        self.setExpanding(True); self.setDrawBase(False); self.setUsesScrollButtons(False)      # nie Rollpfeile, nie ein angeschnittener Reiter: Überlauf geht in das Menü „…“
        self.setElideMode(Qt.ElideNone); self.setCursor(Qt.PointingHandCursor)
        self._wahl_einrichten()
        self.currentChanged.connect(lambda _i: self._neu_anordnen())

    # ---- Maße ---------------------------------------------------------------------------------------------------------------------
    def _sichtbar(self) -> list[int]:
        return [i for i in range(self.count()) if self.isTabVisible(i)]

    def _knopf_breite(self, i: int) -> int:
        return _PFEIL if self.tabButton(i, QTabBar.RightSide) is not None else 0

    def _schrift(self, groesse: float) -> QFont:
        f = QFont(self.font()); f.setPointSizeF(groesse); f.setBold(self._art == HAUPT)
        return f

    def _breiten(self) -> dict[int, int]:
        """Breite je sichtbarem Reiter: Unterreiter gleich breit, Hauptreiter nach Länge der Beschriftung (der Pfeilknopf zählt mit)."""
        vis = self._sichtbar()
        gesamt = self.width() if self.width() > 60 else 280
        if not vis:
            return {}
        if self._art == UNTER:
            return {i: gesamt // len(vis) for i in vis}
        if self._als_dropdown():
            return {}                                         # das Dropdown ersetzt die Reiter: keine Reiterflächen
        soll = self._soll()
        summe = sum(soll.values())
        if summe > gesamt:                                    # zu schmal und nicht als Dropdown möglich (Reiter mit Knopf): anteilig enger, die Beschriftung bricht um
            return {i: max(20, soll[i] * gesamt // summe) for i in vis}
        extra = (gesamt - summe) // len(vis)                  # Platz genug: der Rest wird gleich verteilt
        return {i: soll[i] + extra for i in vis}

    def _soll(self) -> dict[int, int]:
        """Natürliche Breite jedes sichtbaren Hauptreiters (Beschriftung gemessen, Pfeilknopf zählt mit)."""
        fm = QFontMetrics(self._schrift(9.0))
        return {i: fm.horizontalAdvance(_gross(self.tabText(i))) + 2 * _RAND + self._knopf_breite(i) for i in self._sichtbar()}

    def _als_dropdown(self) -> bool:
        """Passen die Hauptreiter in ihrer natürlichen Breite nicht nebeneinander? Dann zeigt das Dropdown die Wahl (Reiter mit Knopf bleiben Reiter: ihr Pfeil hätte im Dropdown keinen Platz)."""
        vis = self._sichtbar()
        if self._art != HAUPT or len(vis) < 2 or self.width() <= 60 or any(self.tabButton(i, QTabBar.RightSide) is not None for i in vis):
            return False
        return sum(self._soll().values()) > self.width()

    def _neu_anordnen(self) -> None:
        """Größe, aktiver Reiter, Texte oder Reiterzahl haben sich geändert: Dropdown oder Reiterleiste zeigen und neu auslegen."""
        self._wahl_zeigen(self._als_dropdown())
        self.setExpanding(True)                                 # stößt die Neuauslegung an
        self.updateGeometry()

    def _text_flaeche(self, i: int, breite: int) -> int:
        return max(10, breite - 2 * _RAND - (self._knopf_breite(i) if self._art == HAUPT else 0))

    def _groesse(self, breiten: dict[int, int]) -> float:
        """Die Schriftgröße: so groß wie möglich, aber so, dass das längste Wort jedes Reiters ganz hineinpasst (nie „…“)."""
        gr = 9.0 if self._art == HAUPT else 8.5
        while gr > 6.0:
            fm = QFontMetrics(self._schrift(gr))
            if all(fm.horizontalAdvance(w) <= self._text_flaeche(i, b) for i, b in breiten.items() for w in _gross(self.tabText(i)).split()):
                break
            gr -= 0.5
        return gr

    def _text_hoehe(self, fm: QFontMetrics, i: int, breite: int) -> int:
        return fm.boundingRect(QRect(0, 0, self._text_flaeche(i, breite), 10000), Qt.AlignHCenter | Qt.TextWordWrap, _gross(self.tabText(i))).height()

    def _hoehe(self, breiten: dict[int, int], gr: float) -> int:
        if self._als_dropdown():
            return DROPDOWN_HOEHE + 2 * REITER_DROPDOWN_RAND + 1
        fm = QFontMetrics(self._schrift(gr))
        th = max([self._text_hoehe(fm, i, b) for i, b in breiten.items()] or [fm.height()])
        if self._art == HAUPT:
            return th + 10
        symbol = _SYMBOL + 2 if any(not self.tabIcon(i).isNull() for i in breiten) else 0
        return symbol + th + 8

    def tabSizeHint(self, index: int) -> QSize:
        b = self._breiten()
        return QSize(b.get(index, 0), self._hoehe(b, self._groesse(b)))

    def minimumTabSizeHint(self, index: int) -> QSize:
        return QSize(20, self.tabSizeHint(index).height())

    def sizeHint(self) -> QSize:
        b = self._breiten()
        return QSize(max(self.width(), 200), self._hoehe(b, self._groesse(b)))

    def minimumSizeHint(self) -> QSize:
        return QSize(60, self.sizeHint().height())

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._neu_anordnen()
        b = self._breiten()
        h = self._hoehe(b, self._groesse(b))
        if h != self._letzte_hoehe:                           # der Umbruch hat sich geändert: die Leiste meldet die neue Höhe
            self._letzte_hoehe = h
            self.updateGeometry()

    def tabLayoutChange(self) -> None:
        super().tabLayoutChange()
        if getattr(self, "_wahl", None) is not None:           # Reiter hinzugefügt, entfernt, umbenannt, aus-/eingeblendet
            self._wahl_zeigen(self._als_dropdown())
        for i in range(self.count()):                          # der Knopf bleibt unsichtbar: der Pfeil wird im Reiter gezeichnet
            b = self.tabButton(i, QTabBar.RightSide)
            if b is not None:
                b.hide()

    def _pfeil_rect(self, i: int, gr: float) -> QRect:
        """Die Fläche des Pfeils hinter dem Text des Reiters ``i`` (leer ohne Knopf)."""
        if self._art != HAUPT or self.tabButton(i, QTabBar.RightSide) is None:
            return QRect()
        r, fm = self.tabRect(i), QFontMetrics(self._schrift(gr))
        breite = self._text_flaeche(i, r.width())
        br = fm.boundingRect(QRect(0, 0, breite, 10000), Qt.AlignHCenter | Qt.TextWordWrap, _gross(self.tabText(i)))
        th = br.height()
        x = r.left() + _RAND + (breite + br.width()) // 2 + 4
        y = r.top() + (r.height() - 2 - th) // 2 + th - fm.height() // 2
        return QRect(x, y - 5, 10, 10)

    def changeEvent(self, e) -> None:
        super().changeEvent(e)
        if e.type() in (QEvent.StyleChange, QEvent.PaletteChange, QEvent.FontChange, QEvent.EnabledChange):      # Thema oder Schrift gewechselt: neu messen
            self._neu_anordnen()

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.LeftButton:
            b = self._breiten()
            gr = self._groesse(b)
            for i in b:
                if self.isTabEnabled(i) and self._pfeil_rect(i, gr).adjusted(-14, -12, 14, 12).contains(e.position().toPoint()):
                    self.tabButton(i, QTabBar.RightSide).click()
                    return
        super().mousePressEvent(e)

    # ---- Zeichnen -------------------------------------------------------------------------------------------------------------
    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pal = self.palette()
        text, grund, akzent = pal.color(QPalette.WindowText), pal.color(QPalette.Window), pal.color(QPalette.Highlight)
        stumm = _mische(text, grund, 0.45)
        b = self._breiten()
        gr = self._groesse(b)
        p.fillRect(QRect(0, self.height() - 1, self.width(), 1), _mische(text, grund, 0.82))          # feine Grundlinie
        for i in b:                                            # leer, solange das Dropdown die Leiste ersetzt
            r = self.tabRect(i)
            aktiv, an = i == self.currentIndex(), self.isTabEnabled(i)
            if not an:
                farbe = _mische(text, grund, 0.65)
            elif aktiv:
                farbe = akzent if self._art == UNTER else text
            else:
                farbe = stumm
            f = self._schrift(gr)
            f.setBold(self._art == HAUPT and aktiv)
            p.setFont(f); p.setPen(farbe)
            fm = QFontMetrics(f)
            y = r.top() + 3
            icon: QIcon = self.tabIcon(i)
            if self._art == UNTER and not icon.isNull():
                pm = icon.pixmap(QSize(_SYMBOL, _SYMBOL), QIcon.Normal if an else QIcon.Disabled)
                p.drawPixmap(QPoint(r.center().x() - _SYMBOL // 2, y), pm)
                y += _SYMBOL + 2
            breite = self._text_flaeche(i, r.width())
            th = fm.boundingRect(QRect(0, 0, breite, 10000), Qt.AlignHCenter | Qt.TextWordWrap, _gross(self.tabText(i))).height()
            if self._art == HAUPT:
                y = r.top() + (r.height() - 2 - th) // 2
            p.drawText(QRect(r.left() + _RAND, y, breite, th + 2), Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap, _gross(self.tabText(i)))
            pf = self._pfeil_rect(i, gr)
            if not pf.isNull():
                c = pf.center()
                p.setPen(Qt.NoPen); p.setBrush(farbe)
                p.drawPolygon(QPolygonF([QPointF(c.x() - 3.5, c.y() - 1.5), QPointF(c.x() + 3.5, c.y() - 1.5), QPointF(c.x(), c.y() + 2.5)]))
            if aktiv:
                p.fillRect(QRect(r.left() + 2, r.bottom() - 1, r.width() - 4, 2), farbe)
        p.end()


def abstand_unter_reiter(lay, leiste) -> None:
    """Eine freistehende Reiterleiste (ohne ``QTabWidget``) bekommt denselben Abstand zu ihrem Inhalt wie jeder Reiter (``ABSTAND_UNTER_REITER``)."""
    lay.insertSpacing(lay.indexOf(leiste) + 1, ABSTAND_UNTER_REITER)


def flach_machen(reiter: QTabWidget, art: str = UNTER) -> FlacheReiterLeiste:
    """Setzt eine ``FlacheReiterLeiste`` in das ``QTabWidget`` (``setTabBar`` gilt nur vor dem ersten Reiter, darum werden die Seiten neu eingesetzt)."""
    seiten = [(reiter.widget(i), reiter.tabIcon(i), reiter.tabText(i), reiter.isTabVisible(i), reiter.isTabEnabled(i)) for i in range(reiter.count())]
    aktuell = reiter.currentIndex()
    leiste = FlacheReiterLeiste(art)
    reiter.blockSignals(True)
    for _ in range(reiter.count()):
        reiter.removeTab(0)
    reiter.setTabBar(leiste)
    leiste.setExpanding(True); leiste.setElideMode(Qt.ElideNone)
    for w, ic, t, sicht, an in seiten:
        i = reiter.addTab(w, ic, t)
        reiter.setTabVisible(i, sicht); reiter.setTabEnabled(i, an)
    reiter.setCurrentIndex(max(0, aktuell))
    reiter.blockSignals(False)
    reiter.currentChanged.emit(reiter.currentIndex())
    return leiste


def alle_flach(wurzel, art: str = HAUPT) -> None:
    """Alle Reiter unter ``wurzel`` (``QTabWidget``) bekommen dieselbe flache Leiste: EIN Aussehen für alle Reiter in den Seitenleisten-Fenstern."""
    for tw in wurzel.findChildren(QTabWidget):
        if not isinstance(tw.tabBar(), FlacheReiterLeiste):
            flach_machen(tw, art)
