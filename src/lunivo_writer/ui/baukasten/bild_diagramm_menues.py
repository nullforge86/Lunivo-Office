"""Menüs und Galerien der Reiter „Bildtools“ und „Diagrammtools“ (nur Aussehen; jede Wahl ruft einen Befehl des Bandes).

``zuschneiden_menue(b)``  Klappe von „Zuschneiden“: oben die Reiter „Nach Form zuschneiden“ / „Nach Skala zuschneiden“, darunter die Formen nach
                          Gruppen (Rechteck, Standardformen, Blockpfeile …) oder die Seitenverhältnisse, unten „Form und Größe zurücksetzen“.
``diagramm_stile_galerie(b)``  die vier Stilkacheln im Band samt Menü; ``diagramm_stile_menue(b)`` ist dasselbe Menü neben dem markierten Diagramm.
``KLAPPEN`` und ``GALERIEN`` melden diese Bausteine dem Band (``ui/ribbon/ribbon_bar.py``) unter dem Namen aus dem Reiter-Plan.
Die Daten kommen aus ``editor/bildzuschnitt.py`` (Formen, Seitenverhältnisse) und ``editor/diagramm.py`` (Stile); gerechnet wird hier nichts.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QMenu, QPushButton, QScrollArea, QStackedWidget,
                               QToolButton, QVBoxLayout, QWidget, QWidgetAction)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.formular_gitter import abschnittsband, reiter_knopf_stil
from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
from lunivo_writer.ui.widgets import icons

KACHEL = 36                       # Seitenlänge einer Formkachel (Knöpfe nicht schmaler als 36 px)
SPALTEN = 10
STIL_KACHEL = QSize(88, 56)       # Vorschau eines Diagrammstils
BAND_STILE = 4                    # so viele Stilkacheln stehen im Band; der Pfeil daneben öffnet alle


# ---- Zuschneiden --------------------------------------------------------------------------------------------------------------
def _form_bild(name: str) -> QIcon:
    from lunivo_writer.editor import formen_katalog as K
    pm = QPixmap(QSize(28, 28)); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(Farbe.AKZENT), 1.3)); p.setBrush(Qt.NoBrush)
    p.drawPath(K.pfad(name, QRectF(4, 4, 20, 20)))
    p.end()
    return QIcon(pm)


def _skala_bild(b: int, h: int) -> QIcon:
    pm = QPixmap(QSize(30, 22)); pm.fill(Qt.transparent)
    f = 24.0 / max(b, h)
    w, hh = b * f, h * f
    if w > 28:
        hh, w = hh * 28 / w, 28.0
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QApplication.palette().text().color(), 1.3)); p.setBrush(Qt.NoBrush)
    p.drawRect(QRectF((30 - w) / 2, (22 - hh) / 2, w, hh))
    p.end()
    return QIcon(pm)


def _abschnittsleiste(text: str) -> QLabel:
    return abschnittsband(text)


def zuschneiden_menue(b) -> QMenu:
    """Die Klappe „Zuschneiden“ nach der Vorlage; ``b`` ist der Befehlsbaustein (``bildZuschneidenForm/Skala/Zuruecksetzen``)."""
    from lunivo_writer.editor import bildzuschnitt as BZ
    m = QMenu(b.w)
    wid = QWidget()
    v = QVBoxLayout(wid); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(0)
    kopf = QHBoxLayout(); kopf.setContentsMargins(6, 4, 6, 4); kopf.setSpacing(2)
    stapel = QStackedWidget()
    reiter = []
    for i, text in enumerate(("Nach Form zuschneiden", "Nach Skala zuschneiden")):
        t = QToolButton(); t.setText(text); t.setCheckable(True); t.setAutoExclusive(True); t.setChecked(i == 0)
        t.setMinimumHeight(KACHEL - 4); t.setAutoRaise(True)
        reiter_knopf_stil(t)
        t.clicked.connect(lambda _=False, i=i: stapel.setCurrentIndex(i))
        kopf.addWidget(t); reiter.append(t)
    kopf.addStretch(1)
    v.addLayout(kopf)

    def waehlen(aktion, *args):
        m.close()
        aktion(None, *args)

    # Seite 1: Formen nach Gruppen, rollbar
    inhalt = QWidget()
    iv = QVBoxLayout(inhalt); iv.setContentsMargins(0, 0, 0, 0); iv.setSpacing(4)
    for kat, namen in BZ.formen_kategorien():
        iv.addWidget(_abschnittsleiste(kat))
        g = QGridLayout(); g.setContentsMargins(6, 0, 6, 0); g.setSpacing(2)
        for n, name in enumerate(namen):
            k = QToolButton(); k.setAutoRaise(True); k.setIcon(_form_bild(name)); k.setIconSize(QSize(28, 28))
            k.setFixedSize(KACHEL, KACHEL); k.setToolTip(name); k.setAccessibleName(name)
            k.clicked.connect(lambda _=False, name=name: waehlen(b.bildZuschneidenForm, name))
            g.addWidget(k, n // SPALTEN, n % SPALTEN)
        g.setColumnStretch(SPALTEN, 1)
        iv.addLayout(g)
    iv.addStretch(1)
    rollen = QScrollArea(); rollen.setWidget(inhalt); rollen.setWidgetResizable(True); rollen.setFrameShape(QFrame.NoFrame)
    rollen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    breite = SPALTEN * (KACHEL + 2) + 12 + rollen.verticalScrollBar().sizeHint().width()
    rollen.setFixedSize(breite, 330)
    stapel.addWidget(rollen)

    # Seite 2: Seitenverhältnisse
    skala = QWidget()
    sg = QGridLayout(skala); sg.setContentsMargins(6, 6, 6, 6); sg.setSpacing(4)
    for n, (text, bb, hh) in enumerate(BZ.VERHAELTNISSE):
        k = QToolButton(); k.setAutoRaise(True); k.setIcon(_skala_bild(bb, hh)); k.setIconSize(QSize(30, 22)); k.setText(text)
        k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); k.setFixedSize(64, 52); k.setToolTip("Seitenverhältnis " + text)
        k.clicked.connect(lambda _=False, t=text: waehlen(b.bildZuschneidenSkala, t))
        sg.addWidget(k, n // 5, n % 5)
    sg.setColumnStretch(5, 1); sg.setRowStretch(len(BZ.VERHAELTNISSE) // 5 + 1, 1)
    stapel.addWidget(skala)
    stapel.setFixedSize(breite, 330)
    v.addWidget(stapel)

    linie = QFrame(); linie.setFrameShape(QFrame.HLine); linie.setStyleSheet("color: palette(midlight);")
    v.addWidget(linie)
    z = QPushButton(icons.icon("rotate-ccw", 18), "  Form und Größe zurücksetzen"); z.setFlat(True); z.setIconSize(QSize(18, 18))
    z.setMinimumHeight(KACHEL); z.setStyleSheet("text-align: left; padding: 4px 10px; border: none;")
    z.clicked.connect(lambda: waehlen(b.bildZuschneidenZuruecksetzen))
    v.addWidget(z)
    a = QWidgetAction(m); a.setDefaultWidget(wid); m.addAction(a)
    return m


# ---- Diagrammstile ------------------------------------------------------------------------------------------------------------
_BALKEN = ((0.62, 0.38, 0.28), (0.34, 0.78, 0.30), (0.52, 0.26, 0.46), (0.86, 0.46, 0.92))


def stil_bild(nr: int, groesse: QSize = STIL_KACHEL) -> QPixmap:
    """Vorschau des Diagrammstils ``nr`` (``diagramm.STILE``): Grund, Raster und Schrift wie im fertigen Diagramm, mit drei Säulenreihen."""
    from lunivo_writer.editor import diagramm as D
    _n, grund, schrift, raster = D.STILE[nr]
    pm = QPixmap(groesse); pm.fill(QColor(grund))
    w, h = groesse.width(), groesse.height()
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    s = QColor(schrift)
    leise = QColor(s); leise.setAlpha(70)
    p.setPen(Qt.NoPen); p.setBrush(s)
    p.drawRoundedRect(QRectF(w * 0.30, 5, w * 0.40, 3), 1.5, 1.5)                    # Diagrammtitel
    ox, oy, bw, bh = 8.0, 14.0, w - 16.0, h - 14.0 - 14.0
    if raster:
        p.setPen(QPen(leise, 1))
        for i in range(5):
            y = oy + bh * i / 4
            p.drawLine(QPointF(ox, y), QPointF(ox + bw, y))
    p.setPen(QPen(s, 1)); p.drawLine(int(ox), int(oy + bh), int(ox + bw), int(oy + bh))
    p.setPen(Qt.NoPen)
    gruppe = bw / len(_BALKEN)
    for gi, werte in enumerate(_BALKEN):
        for si, wert in enumerate(werte):
            p.setBrush(QColor(D.FARBEN[si]))
            sx = ox + gi * gruppe + gruppe * 0.12 + si * gruppe * 0.25
            p.drawRect(QRectF(sx, oy + bh * (1 - wert), gruppe * 0.22, bh * wert))
    for si in range(3):                                                                  # Legende
        p.setBrush(QColor(D.FARBEN[si]))
        x = w * 0.5 - 24 + si * 18
        p.drawRect(QRectF(x, h - 8, 4, 4)); p.setBrush(leise); p.drawRect(QRectF(x + 6, h - 7.5, 8, 3))
    p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1)); p.setBrush(Qt.NoBrush)
    p.drawRect(QRectF(0.5, 0.5, w - 1, h - 1))
    p.end()
    return pm


def _stilname(nr: int) -> str:
    from lunivo_writer.editor import diagramm as D
    return D.STILE[nr][0]


def diagramm_stile_menue(b) -> RasterAuswahl:
    """Alle Diagrammstile als Kacheln (Name im Tipp); die Wahl ist ``diagrammStil``."""
    from lunivo_writer.editor import diagramm as D
    m = RasterAuswahl(b.w, titel="Diagrammstile", spalten=2, groesse=STIL_KACHEL)
    for i in range(len(D.STILE)):
        m.kachel(str(i), _stilname(i), stil_bild(i)).setCheckable(False)
    m.gewaehlt.connect(lambda k: b.diagrammStil(None, int(k)))
    return m


def diagramm_stile_galerie(b) -> dict:
    """Die Galerie im Band: eine Kachel je Stil und das Menü mit allen (Aufbau wie ``galerie_ttFormstile``)."""
    from lunivo_writer.editor import diagramm as D
    kacheln = [(_stilname(i), stil_bild(i), lambda i=i: b.diagrammStil(None, i)) for i in range(BAND_STILE)]      # wie in der Vorlage vier im Band, alle im Popup
    from lunivo_writer.ui.baukasten.diagramm_popups import stile_popup
    return {"kacheln": kacheln, "menue": stile_popup(b), "name": "Diagrammstile"}                  # der Pfeil öffnet dasselbe Popup wie die Schnellleiste


# Dem Band bekannt: Name im Plan → Baustein. Sie gehen vor die gleichnamigen ``menue_…``/``galerie_…`` des Befehlsbausteins.
from lunivo_writer.ui.baukasten import diagramm_popups as _dp                       # noqa: E402  (die Popups am Diagramm)
from lunivo_writer.ui.baukasten import form_menues as _fm                           # noqa: E402  (Form bearbeiten, Formstile)
from lunivo_writer.ui.baukasten import smartart_menues as _sm                       # noqa: E402  (Menüs und Galerie für SmartArt)

KLAPPEN = {"bildZuschneiden": zuschneiden_menue, **_dp.KLAPPEN, **_sm.KLAPPEN, **_fm.KLAPPEN}
GALERIEN = {"diagrammStile": diagramm_stile_galerie, **_sm.GALERIEN, **_fm.GALERIEN}
FELDER = {**_dp.FELDER}                                                              # Eingabefelder des Bandes, die die Oberfläche selbst baut
