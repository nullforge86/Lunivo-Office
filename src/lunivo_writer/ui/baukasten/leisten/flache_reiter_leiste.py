"""Flache Reiterleiste nach der Vorlage: Beschriftung in Großbuchstaben, kein Kasten, Linie unter dem aktiven Reiter.

Zwei Arten (eine Aufgabe: das Zeichnen der Leiste):
- ``HAUPT``: Hauptreiter (zum Beispiel „DIAGRAMM OPTIONEN | TEXTOPTIONEN“). Der aktive Reiter ist fett, die Linie darunter hat die Textfarbe.
- ``UNTER``: Unterreiter mit Symbol OBEN und Beschriftung DARUNTER. Der aktive Reiter ist blau (Hervorhebungsfarbe) mit blauer Linie.

Trägt ein Hauptreiter einen Knopf (``setTabButton``, z. B. ``TeilMenueKnopf``), zeichnet die Leiste den Pfeil „▾“ selbst direkt hinter dem Text; ein Klick auf den
Pfeil löst den Knopf aus (der Knopf selbst bleibt unsichtbar und liefert nur das Popup).

Passen die Hauptreiter nicht nebeneinander (Beschriftungen gemessen), ersetzt EIN Dropdown (``DropdownTaste`` + ``MenueListe``, zeigt den aktuellen Reiter, Haken in der
Liste) die Leiste; die Wahl geht über ``setCurrentIndex``/``currentChanged`` wie ein Klick. Die ``UeberlaufLeiste`` (Band, Dokumente) behält „•••“: sie hat eine andere Aufgabe.

Die Beschriftung bricht bei Platzmangel um und wird nie mit „…“ gekürzt; passt ein Wort nicht, wird die Schrift etwas kleiner.
``flach_machen(reiter, art)`` setzt die Leiste in ein vorhandenes ``QTabWidget`` (die Seiten, Symbole und Namen bleiben; die Basis ``AngepassteReiter`` bleibt unverändert).
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPalette, QPolygonF
from PySide6.QtWidgets import QTabBar, QTabWidget, QToolButton

from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownTaste
from lunivo_writer.ui.baukasten.mass import BREITE_KNOPF_KLEIN, DROPDOWN_HOEHE, HOEHE_BANDREITER_KNOPF, REITER_DROPDOWN_RAND

HAUPT, UNTER = "haupt", "unter"
_RAND = 6                      # Abstand der Beschriftung zum Rand des Reiters
_SYMBOL = 18
_MEHR = BREITE_KNOPF_KLEIN     # Breite des Knopfes „•••“ (Überlaufmenü der ``UeberlaufLeiste``)
_PFEIL = 18                    # Platz für den Teil-Pfeil „▾“ hinter dem Text des Hauptreiters (mit ``TeilMenueKnopf`` als Reiterknopf)


def _gross(text: str) -> str:
    return text                                           # Schreibweise wie im Reiter (die Seitenleisten-Fenster zeigen ihre Reiter ebenso)


def _mische(a: QColor, b: QColor, anteil: float) -> QColor:
    """Farbe a zum Anteil (0…1) mit b gemischt."""
    return QColor(round(a.red() + (b.red() - a.red()) * anteil), round(a.green() + (b.green() - a.green()) * anteil),
                  round(a.blue() + (b.blue() - a.blue()) * anteil))


MEHR_TEXT = "•••"                 # Beschriftung des Überlaufknopfs aller Reiterleisten (an einer Stelle)
MEHR_TIPP = "Weitere Reiter"      # Tooltip und Name des Überlaufknopfs


class ReiterUeberlauf:
    """Basis der Reiterleisten mit Knopf „•••“ (Band, Dokumente, Register: ``UeberlaufLeiste``) und Menü der Reiter, die nicht mehr in die Leiste passen.
    Reihenfolge: ``class X(ReiterUeberlauf, QTabBar)``. Die Leiste liefert ``_versteckte()`` (Indizes der ausgelagerten Reiter) und setzt den Knopf selbst.
    Die flachen Leisten der Fenster nutzen stattdessen ``ReiterDropdown``."""

    def _mehr_einrichten(self) -> None:
        self._mehr = QToolButton(self)
        self._mehr.setText(MEHR_TEXT); self._mehr.setAutoRaise(True); self._mehr.setCursor(Qt.PointingHandCursor)
        self._mehr.setToolTip(MEHR_TIPP); self._mehr.setAccessibleName(MEHR_TIPP)
        self._mehr.clicked.connect(self._mehr_menue); self._mehr.hide()

    def _mehr_menue(self) -> None:
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe(self)
        for i in self._versteckte():
            m.eintrag(self.tabText(i), lambda i=i: self.setCurrentIndex(i), aktiv=self.isTabEnabled(i))
        m.exec(self.mapToGlobal(QPoint(max(0, self._mehr.x() + self._mehr.width() - m.sizeHint().width()), self.height())))


class ReiterDropdown:
    """Die Leiste als ein Dropdown (statt vieler Reiter nebeneinander): Taste mit dem Namen des aktuellen Reiters, Liste aller sichtbaren Reiter mit Haken am aktuellen;
    nicht wählbare Reiter stehen grau. Reihenfolge: ``class X(ReiterDropdown, QTabBar)``."""

    def _wahl_einrichten(self) -> None:
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
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


class UeberlaufLeiste(ReiterUeberlauf, QTabBar):
    """Gewöhnliche Reiterleiste (Band, Dokumente, Register) nach derselben Regel wie ``FlacheReiterLeiste``: keine Rollpfeile, kein angeschnittener Reiter.

    Zu wenig Platz: so viele Reiter wie ganz passen (der aktive immer), der Rest steht hinter dem Knopf „•••“. ``setTabVisible``/``isTabVisible`` behalten ihren Sinn
    (gewollte Sichtbarkeit, z. B. Kontext-Reiter); ``gezeigt(i)`` sagt, ob der Reiter wirklich in der Leiste steht. ``platz`` (optional) liefert die verfügbare Breite,
    wenn die Leiste nicht den ganzen Platz bekommt (Standard: ihre eigene Breite).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._will: list[bool] = []
        self._im_verteilen = False
        self.platz = None
        self.setUsesScrollButtons(False); self.setElideMode(Qt.ElideNone); self.setExpanding(False)       # Reiter in natürlicher Breite: die Summe stimmt mit der Rechnung überein
        self._mehr_einrichten()
        self.currentChanged.connect(lambda _i: self.neu_verteilen())
        self.tabMoved.connect(self._verschoben)

    # ---- gewollte Sichtbarkeit -------------------------------------------------------------------------------------------------
    def setTabVisible(self, index: int, sichtbar: bool) -> None:
        if 0 <= index < len(self._will):
            self._will[index] = sichtbar
        self.neu_verteilen()

    def isTabVisible(self, index: int) -> bool:
        return self._will[index] if 0 <= index < len(self._will) else QTabBar.isTabVisible(self, index)

    def gezeigt(self, index: int) -> bool:
        return QTabBar.isTabVisible(self, index)

    def tabInserted(self, index: int) -> None:
        self._will.insert(index, True)
        super().tabInserted(index)

    def tabRemoved(self, index: int) -> None:
        if 0 <= index < len(self._will):
            self._will.pop(index)
        super().tabRemoved(index)
        self.neu_verteilen()

    def _verschoben(self, von: int, nach: int) -> None:
        if 0 <= von < len(self._will) and 0 <= nach < len(self._will):
            self._will.insert(nach, self._will.pop(von))

    # ---- Überlauf --------------------------------------------------------------------------------------------------------------
    def _verfuegbar(self) -> int:
        return int(self.platz()) if self.platz else self.width()

    def _versteckte(self) -> list[int]:
        return [i for i in range(min(self.count(), len(self._will))) if self._will[i] and not QTabBar.isTabVisible(self, i)]      # Qt fragt die Größe, bevor ``tabInserted`` den Reiter eingetragen hat

    def neu_verteilen(self) -> None:
        if self._im_verteilen or len(self._will) != self.count():
            return
        gesamt = self._verfuegbar()
        wollen = [i for i in range(self.count()) if self._will[i]]
        if gesamt < 2 * _MEHR or not wollen:
            return
        self._im_verteilen = True
        try:
            breite = {i: self.tabSizeHint(i).width() for i in wollen}
            if sum(breite.values()) <= gesamt:
                zeige = set(wollen)
            else:
                frei, summe, zeige_l = gesamt - _MEHR, 0, []
                for i in wollen:
                    if summe + breite[i] > frei:
                        break
                    zeige_l.append(i); summe += breite[i]
                aktiv = self.currentIndex()
                if aktiv in breite and aktiv not in zeige_l:
                    while zeige_l and summe + breite[aktiv] > frei:
                        summe -= breite[zeige_l.pop()]
                    zeige_l.append(aktiv)
                zeige = set(zeige_l)
            if any(QTabBar.isTabVisible(self, i) != (i in zeige) for i in range(self.count())):
                for i in range(self.count()):
                    QTabBar.setTabVisible(self, i, i in zeige)
                self.setUsesScrollButtons(True); self.setUsesScrollButtons(False)       # setzt den alten Rollversatz von Qt zurück (sonst steht der erste Reiter angeschnitten)
            mehr = bool(self._versteckte())
            self._mehr.setVisible(mehr)
            if mehr:
                letzte = max((self.tabRect(i).right() for i in range(self.count()) if QTabBar.isTabVisible(self, i)), default=0)
                self._mehr.setGeometry(min(letzte + 1, max(0, self.width() - _MEHR)), 0, _MEHR, max(HOEHE_BANDREITER_KNOPF, self.height()))
                self._mehr.raise_()
        finally:
            self._im_verteilen = False
        self.updateGeometry()

    def sizeHint(self) -> QSize:
        sh = super().sizeHint()
        return QSize(sh.width() + (_MEHR if self._versteckte() else 0), sh.height())

    def minimumSizeHint(self) -> QSize:
        return QSize(2 * _MEHR, super().sizeHint().height())

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self.neu_verteilen()

    def tabLayoutChange(self) -> None:
        super().tabLayoutChange()
        if not self._im_verteilen:
            self.neu_verteilen()


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
