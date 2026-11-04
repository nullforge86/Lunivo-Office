"""Popups der Schnellleiste am Diagramm und die Klappen der Diagrammtools — ein Baustein, damit Band und Schnellleiste dasselbe zeigen.

``DiagrammPopup(b, art)`` ist ein ``QMenu`` mit Reitern im Kopf:
    ``"elemente"``  Diagrammelement | Schnelllayout — Haken-Liste (``diagrammElementListe`` / ``diagrammElement``), Kacheln (``diagrammSchnelllayout``)
    ``"stile"``     Formatvorlagen | Farben — Stilminiaturen (``diagrammStil``), Farbzeilen (``diagrammFarben``)
    ``"filter"``    Wert | Name — Reihen und Rubriken mit Haken (Name: Umbenennen, ``diagrammNamenSetzen``), „Übernehmen“ (``diagrammFilterSetzen``), „Daten auswählen …“ (``diagrammDatenBearbeiten``)
``diagramm_bereich_feld(b)`` ist das Auswahlfeld „Diagrammbereich“ der Diagrammtools (Liste ``diagrammTeile``, Wahl ``diagrammTeilWaehlen``).
Die Seiten werden bei jedem Öffnen neu gelesen. Gerechnet wird hier nichts; ``b`` ist der Befehlsbaustein.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton, QRadioButton, QScrollArea,
                               QSizePolicy, QStackedWidget, QToolButton, QVBoxLayout, QWidget, QWidgetAction)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.formular_gitter import FELDHOEHE, abschnittsband, reiter_knopf_stil
from lunivo_writer.ui.widgets import icons

KACHEL = 36
BREITE = 340


def _dg(b) -> dict:
    from lunivo_writer.editor import frei_objekt as FO
    return (FO.daten_lesen(b.ed, "diagramm") if getattr(b, "ed", None) else None) or {}


def _kopfknopf(text: str, i: int, gruppe: QButtonGroup) -> QToolButton:
    t = QToolButton(); t.setText(text); t.setCheckable(True); t.setAutoRaise(True); t.setMinimumHeight(KACHEL)
    reiter_knopf_stil(t)
    gruppe.addButton(t, i)
    return t


def _linie() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.HLine); f.setStyleSheet("color: palette(midlight);")
    return f


def _ueberschrift(text: str) -> QLabel:
    return abschnittsband(text)


# ---- Kacheln -------------------------------------------------------------------------------------------------------------------------
def layout_bild(nr: int, groesse: QSize = QSize(92, 84)) -> QPixmap:
    """Strichbild eines Schnelllayouts aus dessen Einstellungen (``SCHNELLLAYOUTS[nr]``): Titelbalken, Legende (Lage), Datenbeschriftungen,
    Achsen, Achsentitel, Gitternetz, Datentabelle, Trendlinie — grau gezeichnet wie die Kacheln der Vorlage."""
    from lunivo_writer.core.befehle.diagrammtools import SCHNELLLAYOUTS
    from lunivo_writer.editor import diagramm_zusatz as Z
    kw = SCHNELLLAYOUTS[nr][1]
    el = {**Z.STANDARD_ELEMENTE, **(kw.get("elemente") or {})}
    pm = QPixmap(groesse); pm.fill(QColor(Farbe.WEISS))
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    w, h = float(groesse.width()), float(groesse.height())
    hell, mittel, dunkel = QColor("#d4d4d4"), QColor("#9a9a9a"), QColor("#6e6e6e")
    balken = QColor("#c8c8c8")
    fl = QRectF(10, 8, w - 20, h - 16)                                   # Zeichenfläche des Diagramms
    p.setPen(Qt.NoPen); p.setBrush(mittel)
    if kw.get("titel_an"):
        p.drawRect(QRectF(w * 0.34, 8, w * 0.32, 3)); fl.setTop(17)
    if el.get("achsentitel"):
        p.drawRect(QRectF(6, h * 0.36, 3, h * 0.26)); fl.setLeft(fl.left() + 6)
        p.drawRect(QRectF(w * 0.40, h - 9, w * 0.20, 2)); fl.setBottom(fl.bottom() - 6)
    if kw.get("legende"):
        pos = kw.get("legende_pos", "unten")
        feld = lambda r: (p.setPen(QPen(mittel, 1)), p.setBrush(Qt.NoBrush), p.drawRect(r), p.setPen(Qt.NoPen), p.setBrush(mittel))
        if pos == "unten":
            p.drawRect(QRectF(w * 0.30, h - 8, w * 0.40, 3)); fl.setBottom(min(fl.bottom(), h - 12))
        elif pos == "oben":
            feld(QRectF(w * 0.28, fl.top() - 1, w * 0.44, 7)); fl.setTop(fl.top() + 9)
        elif pos == "links":
            feld(QRectF(5, h * 0.40, 10, 14)); fl.setLeft(max(fl.left(), 19))
        else:
            feld(QRectF(w - 15, h * 0.40, 10, 14)); fl.setRight(min(fl.right(), w - 19))
    tab = None
    if el.get("datentabelle"):
        th = 14.0
        tab = QRectF(fl.left(), fl.bottom() - th, fl.width(), th); fl.setBottom(fl.bottom() - th - 1)
    if el.get("achsen"):
        fl.setLeft(fl.left() + 5)
        for k in range(4):                                               # Zahlenmarken links
            y = fl.top() + 2 + k * (fl.height() - 4) / 3
            p.setPen(Qt.NoPen); p.setBrush(hell); p.drawRect(QRectF(fl.left() - 6, y - 0.5, 4, 1.5))
    if el.get("gitter"):
        p.setPen(QPen(hell, 1))
        for k in range(4):
            y = fl.top() + 2 + k * (fl.height() - 4) / 3
            p.drawLine(QPointF(fl.left(), y), QPointF(fl.right(), y))
    p.setPen(QPen(dunkel if not el.get("achsen") else mittel, 1.2)); p.drawLine(fl.bottomLeft(), fl.bottomRight())
    if el.get("achsen"):
        p.drawLine(fl.topLeft(), fl.bottomLeft())
    n = 4
    breite = (fl.width() - 4) / n
    for i, hh in enumerate((0.55, 0.85, 0.40, 0.70)):
        x = fl.left() + 3 + i * breite
        r = QRectF(x, fl.bottom() - (fl.height() - 4) * hh, breite * 0.62, (fl.height() - 4) * hh)
        p.setPen(QPen(mittel, 1)); p.setBrush(balken if i % 2 else QColor(Farbe.WEISS)); p.drawRect(r)
        if kw.get("labels"):
            p.setPen(Qt.NoPen); p.setBrush(dunkel); p.drawRect(QRectF(r.center().x() - 3, r.top() - 4, 6, 1.5))
        if el.get("achsen") and tab is None:
            p.setPen(Qt.NoPen); p.setBrush(hell); p.drawRect(QRectF(r.center().x() - 3, fl.bottom() + 2, 6, 1.5))
    if el.get("trendlinie"):
        pen = QPen(dunkel, 1.2, Qt.DashLine); p.setPen(pen)
        p.drawLine(QPointF(fl.left() + 3, fl.bottom() - fl.height() * 0.30), QPointF(fl.right() - 3, fl.bottom() - fl.height() * 0.78))
    if tab is not None:
        p.setPen(QPen(mittel, 1.2)); p.setBrush(Qt.NoBrush); p.drawRect(tab)
        p.drawLine(QPointF(tab.left(), tab.center().y()), QPointF(tab.right(), tab.center().y()))
        for k in range(1, n):
            xx = tab.left() + k * tab.width() / n
            p.drawLine(QPointF(xx, tab.top()), QPointF(xx, tab.bottom()))
    p.setPen(QPen(mittel, 1)); p.setBrush(Qt.NoBrush); p.drawRect(QRectF(0.5, 0.5, w - 1, h - 1))
    p.end()
    return pm


def _farbzeile(farben: list[str], gewaehlt: bool, klick) -> QWidget:
    z = QToolButton(); z.setAutoRaise(True); z.setCheckable(True); z.setChecked(gewaehlt); z.setMinimumHeight(KACHEL - 4)
    z.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    pm = QPixmap(6 * 46 + 8, 36); pm.fill(Qt.transparent)
    p = QPainter(pm)
    for i, f in enumerate(farben[:6]):
        p.fillRect(QRectF(4 + i * 46, 2, 44, 32), QColor(f))
    p.end()
    z.setIcon(QIcon(pm)); z.setIconSize(pm.size()); z.clicked.connect(klick)
    z.setStyleSheet("QToolButton { border: 1px solid transparent; } QToolButton:checked { background: palette(midlight); border: 1px solid palette(mid); }")
    return z


class DiagrammPopup(QMenu):
    """Ein Popup mit Reitern; ``art``: ``elemente``, ``stile`` oder ``filter``; ``reiter``: der zuerst gezeigte Reiter."""

    SEITEN = {"elemente": ("Diagrammelement", "Schnelllayout"), "stile": ("Formatvorlagen", "Farben"), "filter": ("Wert", "Name")}

    def __init__(self, b, art: str = "elemente", reiter: int = 0, parent=None):
        super().__init__(parent or getattr(b, "w", None))
        self.b, self.art, self._start = b, art, reiter
        self._wid = QWidget()
        v = QVBoxLayout(self._wid); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)
        kopf = QHBoxLayout(); kopf.setContentsMargins(6, 2, 6, 0); kopf.setSpacing(2)
        self.gruppe = QButtonGroup(self); self.gruppe.setExclusive(True)
        for i, t in enumerate(self.SEITEN[art]):
            kopf.addWidget(_kopfknopf(t, i, self.gruppe))
        kopf.addStretch(1)
        v.addLayout(kopf); v.addWidget(_linie())
        self.stapel = QStackedWidget(); v.addWidget(self.stapel)
        self._seiten: list[QWidget] = []
        for _ in self.SEITEN[art]:
            host = QWidget(); QVBoxLayout(host).setContentsMargins(0, 0, 0, 0)
            self.stapel.addWidget(host); self._seiten.append(host)
        self.gruppe.idClicked.connect(self.waehle)
        a = QWidgetAction(self); a.setDefaultWidget(self._wid); self.addAction(a)
        self.setFixedWidth(BREITE)
        self.aboutToShow.connect(self.neu_lesen)
        self.waehle(reiter)

    # ---- Reiter -------------------------------------------------------------------------------------------------------------------
    def waehle(self, i: int) -> None:
        self.gruppe.button(i).setChecked(True)
        self.stapel.setCurrentIndex(i)
        self._fuellen(i)

    def neu_lesen(self) -> None:
        """Beim Öffnen: den Reiter zeigen, den der Aufrufer wollte, mit frisch gelesenen Daten."""
        self.waehle(self._start if self.gruppe.checkedId() < 0 else self.stapel.currentIndex())

    def _fuellen(self, i: int) -> None:
        host = self._seiten[i]
        lay = host.layout()
        while lay.count():
            it = lay.takeAt(0)
            if it.widget() is not None:
                it.widget().hide(); it.widget().deleteLater()
        bau = {("elemente", 0): self._seite_elemente, ("elemente", 1): self._seite_schnelllayout, ("stile", 0): self._seite_vorlagen,
               ("stile", 1): self._seite_farben, ("filter", 0): self._seite_filter, ("filter", 1): self._seite_namen}[(self.art, i)]
        lay.addWidget(bau())
        self.stapel.setFixedHeight(max(60, host.sizeHint().height()))
        self._wid.adjustSize(); self.adjustSize()

    # ---- Diagrammelement -----------------------------------------------------------------------------------------------------------------
    def _seite_elemente(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8, 6, 8, 6); v.setSpacing(0)
        for name, text, an in self.b.diagrammElementListe():
            c = QCheckBox(text); c.setChecked(bool(an)); c.setMinimumHeight(KACHEL - 6); c.setAccessibleName(text)
            c.clicked.connect(lambda _=False, n=name: (self.b.diagrammElement(None, n), self._fuellen(0)))
            v.addWidget(c)
        return w

    def _seite_schnelllayout(self) -> QWidget:
        from lunivo_writer.core.befehle.diagrammtools import SCHNELLLAYOUT_ANZEIGE, SCHNELLLAYOUTS
        w = QWidget(); g = QGridLayout(w); g.setContentsMargins(8, 8, 8, 8); g.setSpacing(6)
        for platz, i in enumerate(SCHNELLLAYOUT_ANZEIGE):                # Reihenfolge wie im Foto der Vorlage; i ist die gespeicherte Layoutnummer
            name = SCHNELLLAYOUTS[i][0]
            k = QToolButton(); k.setAutoRaise(True); k.setIcon(QIcon(layout_bild(i))); k.setIconSize(QSize(92, 84)); k.setToolTip(name)
            k.setFixedSize(100, 92); k.setAccessibleName(name)
            k.clicked.connect(lambda _=False, i=i: (self.close(), self.b.diagrammSchnelllayout(None, i)))
            g.addWidget(k, platz // 3, platz % 3)
        g.setColumnStretch(3, 1)
        return w

    # ---- Formatvorlagen und Farben -----------------------------------------------------------------------------------------------------
    def _seite_vorlagen(self) -> QWidget:
        from lunivo_writer.editor import diagramm as D
        from lunivo_writer.ui.baukasten.bild_diagramm_menues import stil_bild
        STIL_KACHEL = QSize(136, 80)                                  # wie in der Vorlage: zwei große Kacheln je Zeile
        aktuell = int(_dg(self.b).get("stil", 0) or 0)
        inhalt = QWidget(); v = QVBoxLayout(inhalt); v.setContentsMargins(8, 4, 8, 6); v.setSpacing(4)
        v.addWidget(_ueberschrift("Systemstil"))
        g = QGridLayout(); g.setSpacing(6)
        for i, s in enumerate(D.stile_liste()):
            k = QToolButton(); k.setAutoRaise(True); k.setCheckable(True); k.setChecked(i == aktuell)
            k.setIcon(QIcon(stil_bild(s["nr"], STIL_KACHEL))); k.setIconSize(STIL_KACHEL); k.setToolTip(s["name"]); k.setAccessibleName(s["name"])
            k.setFixedSize(STIL_KACHEL + QSize(14, 12))
            k.setStyleSheet(f"QToolButton:checked {{ border: 2px solid {Farbe.AKZENT}; background: transparent; }}")
            k.clicked.connect(lambda _=False, n=s["nr"]: (self.close(), self.b.diagrammStil(None, n)))
            g.addWidget(k, i // 2, i % 2)
        g.setColumnStretch(2, 1)
        v.addLayout(g); v.addStretch(1)
        r = QScrollArea(); r.setWidget(inhalt); r.setWidgetResizable(True); r.setFrameShape(QFrame.NoFrame)
        r.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); r.setFixedHeight(340)
        return r

    def _seite_farben(self) -> QWidget:
        from lunivo_writer.editor import diagramm as D
        akt = [str(f).lower() for f in (_dg(self.b).get("farben") or [])]
        inhalt = QWidget(); v = QVBoxLayout(inhalt); v.setContentsMargins(8, 4, 8, 6); v.setSpacing(2)
        nr = 0
        for gruppe, zeilen in D.farbschemen_gruppen():
            v.addWidget(_ueberschrift(gruppe))
            for name, farben in zeilen:
                z = _farbzeile(farben, [f.lower() for f in farben[:len(akt)]] == akt and bool(akt), lambda _=False, n=nr: (self.close(), self.b.diagrammFarben(None, n)))
                z.setToolTip(name); z.setAccessibleName(name)
                v.addWidget(z); nr += 1
        v.addStretch(1)
        r = QScrollArea(); r.setWidget(inhalt); r.setWidgetResizable(True); r.setFrameShape(QFrame.NoFrame)
        r.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); r.setFixedHeight(340)
        return r

    # ---- Filter ---------------------------------------------------------------------------------------------------------------------------
    def _seite_filter(self) -> QWidget:
        daten = self.b.diagrammFilterDaten()
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8, 4, 8, 6); v.setSpacing(2)
        self._haken: dict[str, list[tuple[str, QCheckBox]]] = {}
        inhalt = QWidget(); iv = QVBoxLayout(inhalt); iv.setContentsMargins(0, 0, 0, 0); iv.setSpacing(0)
        for schl, titel in (("reihen", "Reihe"), ("rubriken", "Rubrik")):
            eintraege = daten.get(schl, [])
            kopf = QToolButton(); kopf.setText(titel); kopf.setCheckable(True); kopf.setChecked(True); kopf.setAutoRaise(True)
            kopf.setArrowType(Qt.DownArrow); kopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); kopf.setMinimumHeight(KACHEL - 6)
            kopf.setStyleSheet(f"QToolButton {{ color: {Farbe.AKZENT}; font-weight: 600; border: none; }}")
            gruppe = QWidget(); gv = QVBoxLayout(gruppe); gv.setContentsMargins(18, 0, 0, 4); gv.setSpacing(0)
            kopf.toggled.connect(lambda an, k=kopf, g=gruppe: (g.setVisible(an), k.setArrowType(Qt.DownArrow if an else Qt.RightArrow), self._hoehe()))
            alle = QCheckBox("(Alle auswählen)"); alle.setMinimumHeight(KACHEL - 6); alle.setTristate(False)
            gv.addWidget(alle)
            boxen = []
            for name, an in eintraege:
                c = QCheckBox(name); c.setChecked(bool(an)); c.setMinimumHeight(KACHEL - 6)
                gv.addWidget(c); boxen.append((name, c))
            alle.setChecked(all(c.isChecked() for _n, c in boxen) and bool(boxen))
            alle.clicked.connect(lambda an, bx=boxen: [c.setChecked(an) for _n, c in bx])
            for _n, c in boxen:
                c.toggled.connect(lambda _=False, a=alle, bx=boxen: (a.blockSignals(True), a.setChecked(all(x.isChecked() for _m, x in bx)), a.blockSignals(False)))
            self._haken[schl] = boxen
            iv.addWidget(kopf); iv.addWidget(gruppe)
        iv.addStretch(1)
        r = QScrollArea(); r.setWidget(inhalt); r.setWidgetResizable(True); r.setFrameShape(QFrame.NoFrame)
        r.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); r.setFixedHeight(min(300, max(120, inhalt.sizeHint().height() + 4)))
        v.addWidget(r)
        v.addWidget(_linie())
        fuss = QHBoxLayout(); fuss.setContentsMargins(0, 2, 0, 0)
        ok = QPushButton(icons.icon("refresh-cw", 16), " Übernehmen"); ok.setFixedHeight(FELDHOEHE); ok.setAccessibleName("Filter übernehmen")
        ok.clicked.connect(self._uebernehmen)
        mehr = QPushButton("Daten auswählen …"); mehr.setFlat(True); mehr.setFixedHeight(FELDHOEHE)
        mehr.setStyleSheet(f"QPushButton {{ color: {Farbe.AKZENT}; border: none; text-decoration: underline; padding: 0 6px; }}")
        mehr.clicked.connect(lambda: (self.close(), self.b.diagrammDatenBearbeiten()))
        fuss.addWidget(ok); fuss.addStretch(1); fuss.addWidget(mehr)
        v.addLayout(fuss)
        return w

    def _seite_namen(self) -> QWidget:
        """Reiter „Name“: Reihen und Rubriken umbenennen; „Übernehmen“ schreibt über ``diagrammNamenSetzen`` in die Diagrammdaten."""
        daten = self.b.diagrammFilterDaten()
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8, 4, 8, 6); v.setSpacing(2)
        self._felder: dict[str, list[tuple[str, QLineEdit]]] = {}
        inhalt = QWidget(); iv = QVBoxLayout(inhalt); iv.setContentsMargins(0, 0, 0, 0); iv.setSpacing(2)
        quelle = self.b.diagrammNamenQuelleLesen()
        for schl, titel, (qwert, qtext) in (("reihen", "Reihe", ("zeile1", "Zeile 1")), ("rubriken", "Rubrik", ("spalte_a", "Spalte A"))):
            iv.addWidget(_ueberschrift(titel))
            gr = QButtonGroup(inhalt)
            for wert, text in ((qwert, qtext), ("keine", "(Keine)")):
                rb = QRadioButton(text); rb.setMinimumHeight(KACHEL - 6); rb.setAccessibleName(f"{titel}: {text}")
                rb.setChecked(quelle == wert); gr.addButton(rb)
                rb.clicked.connect(lambda _=False, wv=wert: (self.close(), self.b.diagrammNamenQuelle(None, wv)))
                iv.addWidget(rb)
                if wert == qwert and daten.get(schl):
                    sub = QLabel(", ".join(n for n, _a in daten[schl])); sub.setWordWrap(True)
                    sub.setContentsMargins(26, 0, 0, 2); sub.setStyleSheet("color: palette(mid);"); iv.addWidget(sub)
            felder = []
            for name, _an in daten.get(schl, []):
                e = QLineEdit(name); e.setFixedHeight(FELDHOEHE); e.setAccessibleName(f"{titel} {name}")
                iv.addWidget(e); felder.append((name, e))
            self._felder[schl] = felder
        iv.addStretch(1)
        r = QScrollArea(); r.setWidget(inhalt); r.setWidgetResizable(True); r.setFrameShape(QFrame.NoFrame)
        r.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); r.setFixedHeight(min(300, max(120, inhalt.sizeHint().height() + 4)))
        v.addWidget(r); v.addWidget(_linie())
        fuss = QHBoxLayout(); fuss.setContentsMargins(0, 2, 0, 0)
        ok = QPushButton(icons.icon("refresh-cw", 16), " Übernehmen"); ok.setFixedHeight(FELDHOEHE); ok.setAccessibleName("Namen übernehmen")
        ok.clicked.connect(self._namen_uebernehmen)
        fuss.addWidget(ok); fuss.addStretch(1)
        v.addLayout(fuss)
        return w

    def _namen_uebernehmen(self) -> None:
        neu = {schl: [(alt, e.text().strip()) for alt, e in felder] for schl, felder in self._felder.items()}
        self.close()
        self.b.diagrammNamenSetzen(None, neu)

    def _hoehe(self) -> None:
        self.stapel.setFixedHeight(max(60, self._seiten[self.stapel.currentIndex()].sizeHint().height()))
        self._wid.adjustSize(); self.adjustSize()

    def _uebernehmen(self) -> None:
        aus = {schl: [n for n, c in boxen if not c.isChecked()] for schl, boxen in self._haken.items()}
        self.close()
        self.b.diagrammFilterSetzen(None, aus)


# ---- Klappen des Bandes und der Schnellleiste ----------------------------------------------------------------------------------------
def elemente_popup(b) -> DiagrammPopup:
    return DiagrammPopup(b, "elemente", 0)


def schnelllayout_popup(b) -> DiagrammPopup:
    return DiagrammPopup(b, "elemente", 1)


def stile_popup(b) -> DiagrammPopup:
    return DiagrammPopup(b, "stile", 0)


def farben_popup(b) -> DiagrammPopup:
    return DiagrammPopup(b, "stile", 1)


def filter_popup(b) -> DiagrammPopup:
    return DiagrammPopup(b, "filter", 0)


# ---- Das Feld „Diagrammbereich“ --------------------------------------------------------------------------------------------------------
def diagramm_bereich_feld(b) -> QWidget:
    """Auswahlfeld „Diagrammbereich“ der Diagrammtools: oben die Liste der Teile (zeigt den gewählten), darunter „Formatieren“ und
    „Formatvorlage zurücksetzen“. ``auffrischen()`` (vom Band bei jeder Änderung gerufen) liest Liste und Auswahl neu."""
    host = QWidget()
    v = QVBoxLayout(host); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(1)
    cb = QComboBox(); cb.setFixedHeight(FELDHOEHE); cb.setMaxVisibleItems(16); cb.view().setMinimumWidth(330)   # schmal im Band, die Liste ganz breit
    cb.setAccessibleName("Diagrammbereich"); cb.setToolTip("Diagrammbereich")
    v.addWidget(cb)
    zeile = QHBoxLayout(); zeile.setContentsMargins(0, 0, 0, 0); zeile.setSpacing(4)          # wie in der Vorlage nebeneinander unter dem Feld
    v.addLayout(zeile)
    for text, sym, f in (("Formatieren", "pinsel", lambda: getattr(b.w, "diagrammformat_seitenleiste", lambda: None)()),
                         ("Formatvorlage zurücksetzen", "undo-2", lambda: b.diagrammZuruecksetzen())):
        k = QToolButton(); k.setAutoRaise(True); k.setIcon(icons.icon(sym, 16)); k.setIconSize(QSize(16, 16)); k.setText("Stil zurück" if text.startswith("Formatvorlage") else text); k.setToolTip(text); k.setAccessibleName(text)
        k.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); k.setMinimumHeight(FELDHOEHE)
        k.clicked.connect(lambda _=False, f=f: f())
        zeile.addWidget(k)
    stumm = [False]

    def auffrischen() -> None:
        if cb.view().isVisible():
            return
        teile = b.diagrammTeile() or []
        aktuell = b.feld_diagrammTeil()
        stumm[0] = True
        cb.clear()
        for schl, name in teile:
            cb.addItem(name, schl)
        i = max(0, cb.findText(aktuell))
        if cb.count():
            cb.setCurrentIndex(i)
        else:
            cb.addItem("Diagrammbereich", "diagrammbereich")
        cb.setEnabled(bool(teile))
        stumm[0] = False

    def gewaehlt(i: int) -> None:
        if stumm[0] or i < 0:
            return
        b.diagrammTeilWaehlen(None, cb.itemData(i))
        ed = getattr(b, "ed", None)
        if ed is not None:
            ed.viewport().update()
        w = getattr(b, "w", None)
        if w is not None and hasattr(w, "diagrammformat_folgen"):
            w.diagrammformat_folgen()
    cb.activated.connect(gewaehlt)
    host.auffrischen = auffrischen
    host.feld = cb
    auffrischen()
    return host


KLAPPEN = {"diagrammElement": elemente_popup, "diagrammSchnelllayout": schnelllayout_popup, "diagrammFarben": farben_popup,
           "diagrammStilKlappe": stile_popup, "diagrammFilter": filter_popup}
FELDER = {"diagrammBereich": diagramm_bereich_feld}
