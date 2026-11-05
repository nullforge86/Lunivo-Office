"""Flache Reiterleiste nach der Vorlage: Beschriftung in Großbuchstaben, kein Kasten, Linie unter dem aktiven Reiter.

Zwei Arten (eine Aufgabe: das Zeichnen der Leiste):
- ``HAUPT``: Hauptreiter (zum Beispiel „DIAGRAMM OPTIONEN | TEXTOPTIONEN“). Der aktive Reiter ist fett, die Linie darunter hat die Textfarbe.
- ``UNTER``: Unterreiter mit Symbol OBEN und Beschriftung DARUNTER. Der aktive Reiter ist blau (Hervorhebungsfarbe) mit blauer Linie.

Trägt ein Hauptreiter einen Knopf (``setTabButton``, z. B. ``TeilMenueKnopf``), zeichnet die Leiste den Pfeil „▾“ selbst direkt hinter dem Text; ein Klick auf den
Pfeil löst den Knopf aus (der Knopf selbst bleibt unsichtbar und liefert nur das Popup).

Die Beschriftung bricht bei Platzmangel um und wird nie mit „…“ gekürzt; passt ein Wort nicht, wird die Schrift etwas kleiner.
``flach_machen(reiter, art)`` setzt die Leiste in ein vorhandenes ``QTabWidget`` (die Seiten, Symbole und Namen bleiben; die Basis ``AngepassteReiter`` bleibt unverändert).
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPalette, QPolygonF
from PySide6.QtWidgets import QTabBar, QTabWidget, QToolButton

from lunivo_writer.ui.baukasten.mass import BREITE_KNOPF_KLEIN, HOEHE_BANDREITER_KNOPF, HOEHE_KNOPF_GROSS

HAUPT, UNTER = "haupt", "unter"
_RAND = 6                      # Abstand der Beschriftung zum Rand des Reiters
_SYMBOL = 18
_MEHR = BREITE_KNOPF_KLEIN     # Breite des Knopfes „…“ (Überlaufmenü), wenn nicht alle Hauptreiter in eine Zeile passen
_PFEIL = 18                    # Platz für den Teil-Pfeil „▾“ hinter dem Text des Hauptreiters (mit ``TeilMenueKnopf`` als Reiterknopf)


def _gross(text: str) -> str:
    return text                                           # Schreibweise wie im Reiter (die Seitenleisten-Fenster zeigen ihre Reiter ebenso)


def _mische(a: QColor, b: QColor, anteil: float) -> QColor:
    """Farbe a zum Anteil (0…1) mit b gemischt."""
    return QColor(round(a.red() + (b.red() - a.red()) * anteil), round(a.green() + (b.green() - a.green()) * anteil),
                  round(a.blue() + (b.blue() - a.blue()) * anteil))


class FlacheReiterLeiste(QTabBar):
    def __init__(self, art: str = UNTER, parent=None):
        super().__init__(parent)
        self._art = art
        self._letzte_hoehe = 0
        self.setExpanding(True); self.setDrawBase(False); self.setUsesScrollButtons(False)      # nie Rollpfeile, nie ein angeschnittener Reiter: Überlauf geht in das Menü „…“
        self.setElideMode(Qt.ElideNone); self.setCursor(Qt.PointingHandCursor)
        self._mehr = QToolButton(self)
        self._mehr.setText("•••"); self._mehr.setAutoRaise(True); self._mehr.setCursor(Qt.PointingHandCursor)
        self._mehr.setToolTip("Weitere Reiter"); self._mehr.clicked.connect(self._mehr_menue); self._mehr.hide()
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
        fm = QFontMetrics(self._schrift(9.0))
        soll = {i: fm.horizontalAdvance(_gross(self.tabText(i))) + 2 * _RAND + self._knopf_breite(i) for i in vis}
        summe = sum(soll.values())
        if summe > gesamt:                                    # zu schmal: so viele Reiter wie ganz passen, der Rest steht im Menü „…“
            return {i: soll[i] for i in self._passende(soll, gesamt)}
        if summe <= gesamt:                                   # Platz genug: der Rest wird gleich verteilt
            extra = (gesamt - summe) // len(vis)
            return {i: soll[i] + extra for i in vis}
        return soll

    def _passende(self, soll: dict[int, int], gesamt: int) -> list[int]:
        """Die Reiter, die neben dem Knopf „…“ ganz passen (in Reihenfolge); der aktive Reiter ist immer dabei."""
        frei, zeige, summe = gesamt - _MEHR, [], 0
        for i in soll:
            if summe + soll[i] > frei:
                break
            zeige.append(i); summe += soll[i]
        aktiv = self.currentIndex()
        if aktiv in soll and aktiv not in zeige:
            while zeige and summe + soll[aktiv] > frei:
                summe -= soll[zeige.pop()]
            zeige = sorted(zeige + [aktiv])
        return zeige

    def _versteckte(self) -> list[int]:
        b = self._breiten()
        return [i for i in self._sichtbar() if i not in b]

    def _mehr_menue(self) -> None:
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe(self)
        for i in self._versteckte():
            m.eintrag(self.tabText(i), lambda i=i: self.setCurrentIndex(i), aktiv=self.isTabEnabled(i))
        m.exec(self.mapToGlobal(QPoint(self.width() - m.sizeHint().width(), self.height())))

    def _neu_anordnen(self) -> None:
        """Der Überlauf hat sich geändert (Größe, aktiver Reiter, Texte): Knopf „…“ setzen und die Reiter neu auslegen."""
        if self._art != HAUPT:
            return
        mehr = bool(self._versteckte())
        self._mehr.setVisible(mehr)
        if mehr:
            self._mehr.setGeometry(self.width() - _MEHR, 0, _MEHR, max(HOEHE_KNOPF_GROSS, self.height() - 1))
            self._mehr.raise_()
        self.setExpanding(not self._ueberlauf())                # setExpanding stößt die Neuauslegung an

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
        if self._ueberlauf():                                  # nicht zusammenschieben: die Reiter behalten ihre Breite, der Rest steht im Menü „…“
            return self.tabSizeHint(index)
        return QSize(20, self.tabSizeHint(index).height())

    def sizeHint(self) -> QSize:
        b = self._breiten()
        return QSize(max(self.width(), 200), self._hoehe(b, self._groesse(b)))

    def minimumSizeHint(self) -> QSize:
        return QSize(60, self.sizeHint().height())

    def _ueberlauf(self) -> bool:
        """Passen die Hauptreiter in ihrer natürlichen Breite nicht nebeneinander?"""
        if self._art != HAUPT or not self._sichtbar():
            return False
        fm = QFontMetrics(self._schrift(9.0))
        return sum(fm.horizontalAdvance(_gross(self.tabText(i))) + 2 * _RAND + self._knopf_breite(i) for i in self._sichtbar()) > self.width()

    def resizeEvent(self, e) -> None:
        self.setExpanding(not self._ueberlauf())               # überlaufend: nicht auf die Breite zusammenschieben, sondern rollen
        super().resizeEvent(e)
        self._neu_anordnen()
        b = self._breiten()
        h = self._hoehe(b, self._groesse(b))
        if h != self._letzte_hoehe:                           # der Umbruch hat sich geändert: die Leiste meldet die neue Höhe
            self._letzte_hoehe = h
            self.updateGeometry()

    def tabLayoutChange(self) -> None:
        super().tabLayoutChange()
        if self._art == HAUPT and getattr(self, "_mehr", None) is not None:
            self._mehr.setVisible(bool(self._versteckte()))
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
        for i in b:                                            # nur die gezeigten Reiter (die übrigen stehen im Menü „…“)
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


class UeberlaufLeiste(QTabBar):
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
        self._mehr = QToolButton(self)
        self._mehr.setText("•••"); self._mehr.setAutoRaise(True); self._mehr.setCursor(Qt.PointingHandCursor)
        self._mehr.setToolTip("Weitere Reiter"); self._mehr.setAccessibleName("Weitere Reiter"); self._mehr.clicked.connect(self._mehr_menue); self._mehr.hide()
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
        return [i for i in range(self.count()) if self._will[i] and not QTabBar.isTabVisible(self, i)]

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

    def _mehr_menue(self) -> None:
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe(self)
        for i in self._versteckte():
            m.eintrag(self.tabText(i), lambda i=i: self.setCurrentIndex(i), aktiv=self.isTabEnabled(i))
        m.exec(self.mapToGlobal(QPoint(max(0, self._mehr.x() + _MEHR - m.sizeHint().width()), self.height())))

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
