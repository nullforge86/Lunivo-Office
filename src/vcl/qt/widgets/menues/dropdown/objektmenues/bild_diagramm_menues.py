"""Menüs und Galerien der Reiter „Bildtools“ und „Diagrammtools“ (nur Aussehen; jede Wahl ruft einen Befehl des Bandes).

``zuschneiden_menue(b)``  Klappe von „Zuschneiden“: oben die Reiter „Nach Form zuschneiden“ / „Nach Skala zuschneiden“, darunter die Formen nach
                          Gruppen (Rechteck, Standardformen, Blockpfeile …) oder die Seitenverhältnisse, unten „Form und Größe zurücksetzen“.
``diagramm_stile_galerie(b)``  die vier Stilkacheln im Band samt Menü; ``diagramm_stile_menue(b)`` ist dasselbe Menü neben dem markierten Diagramm.
``KLAPPEN`` und ``GALERIEN`` melden diese Bausteine dem Band (``oberflaeche/band/band_leiste.py``) unter dem Namen aus dem Reiter-Plan.
Die Daten kommen aus ``editor/objekte/bildzuschnitt.py`` (Formen, Seitenverhältnisse) und ``editor/diagramme/diagramm.py`` (Stile); gerechnet wird hier nichts.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf, werkzeugknopf

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QMenu, QPushButton, QScrollArea, QStackedWidget, QToolButton, QWidget, QWidgetAction

from vcl.qt.widgets.menues.dropdown.zeile import dropdown_zeile
from vcl.qt.widgets.bausteine.schrift.texte import trennlinie
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import abschnittsband, reiter_knopf_stil
from vcl.qt.widgets.menues.dropdown.auswahl.raster_auswahl import RasterAuswahl
from vcl.qt.widgets.bausteine.interaktion.felder.karten_raster import kachel_gitter
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_KACHEL_ABZUG_FLACH, RADIUS_ZEICHNUNG_FEIN, STIFT_BILDCHEN_LINIE
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_FORMEN_SPALTEN, DROPDOWN_KACHEL, DROPDOWN_KACHEL_ABSTAND, DROPDOWN_ROLLRAND, HOEHE_FORMENMENUE, ABSTAND_ENG, ABSTAND_KLEIN, GROESSE_DIAGRAMMSTIL_KACHEL, GROESSE_FORMBILD_KACHEL, ICON_GROSS, ICON_KNOPF_GROSS, RAND_KEIN, RAND_MENUE_KOPF, RAND_ZUSCHNEIDEN_KACHELN, RAND_ZUSCHNEIDEN_LISTE

STIL_KACHEL = QSize(*GROESSE_DIAGRAMMSTIL_KACHEL)       # Vorschau eines Diagrammstils
BAND_STILE = 4                    # so viele Stilkacheln stehen im Band; der Pfeil daneben öffnet alle


# ---- Zuschneiden --------------------------------------------------------------------------------------------------------------
def _form_bild(name: str) -> QIcon:
    from vcl.qt.rendering import formen as K
    pm = QPixmap(QSize(*GROESSE_FORMBILD_KACHEL)); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(Farbe.AKZENT), STIFT_BILDCHEN_LINIE)); p.setBrush(Qt.NoBrush)
    p.drawPath(K.formen_katalog_pfad(name, QRectF(4, 4, 20, 20)))
    p.end()
    return QIcon(pm)


def _abschnittsleiste(text: str) -> QLabel:
    return abschnittsband(text)


def zuschneiden_menue(b) -> QMenu:
    """Die Klappe „Zuschneiden“ nach der Vorlage; ``b`` ist der Befehlsbaustein (``bildZuschneidenForm/Skala/Zuruecksetzen``)."""
    from vcl.qt.rendering import formen as BZ
    from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
    m = MenueListe(b.w)
    wid = QWidget()
    v = _spalte("kein", wid)
    kopf = _reihe("popup")
    stapel = QStackedWidget()
    reiter = []
    for i, text in enumerate(("Nach Form zuschneiden", "Nach Skala zuschneiden")):
        t = werkzeugknopf("standard", text, umschaltbar=True, an=i == 0, flach=False); t.setAutoExclusive(True)
        t.setMinimumHeight(DROPDOWN_KACHEL - DROPDOWN_KACHEL_ABZUG_FLACH); t.setAutoRaise(True)
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
    iv = _spalte("eng", inhalt)
    for kat, namen in BZ.formen_kategorien():
        iv.addWidget(_abschnittsleiste(kat))
        kachelreihe = []
        for n, name in enumerate(namen):
            k = werkzeugknopf("standard"); k.setIcon(_form_bild(name)); k.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
            k.setFixedSize(DROPDOWN_KACHEL, DROPDOWN_KACHEL); k.setToolTip(name); k.setAccessibleName(name)
            k.clicked.connect(lambda _=False, name=name: waehlen(b.bildZuschneidenForm, name))
            kachelreihe.append(k)
        iv.addLayout(kachel_gitter(kachelreihe, DROPDOWN_FORMEN_SPALTEN, rand=RAND_ZUSCHNEIDEN_KACHELN, abstand=ABSTAND_ENG, rest_dehnt=True))
    iv.addStretch(1)
    rollen = QScrollArea(); rollen.setWidget(inhalt); rollen.setWidgetResizable(True); rollen.setFrameShape(QFrame.NoFrame)
    rollen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    breite = DROPDOWN_FORMEN_SPALTEN * (DROPDOWN_KACHEL + DROPDOWN_KACHEL_ABSTAND) + DROPDOWN_ROLLRAND + rollen.verticalScrollBar().sizeHint().width()
    rollen.setFixedSize(breite, HOEHE_FORMENMENUE)
    stapel.addWidget(rollen)

    # Seite 2: Seitenverhältnisse als Textliste untereinander, rollbar (wie in der Vorlage)
    liste = QWidget()
    lv = _spalte("panel", liste)
    for text, bb, hh in BZ.VERHAELTNISSE:
        k = knopf("standard", text.replace(":", " : "), ohne_rand=True); k.setMinimumHeight(DROPDOWN_KACHEL)
        dropdown_zeile(k)
        k.setToolTip("Seitenverhältnis " + text); k.setAccessibleName("Seitenverhältnis " + text)
        k.clicked.connect(lambda _=False, t=text: waehlen(b.bildZuschneidenSkala, t))
        lv.addWidget(k)
    lv.addStretch(1)
    skala = QScrollArea(); skala.setWidget(liste); skala.setWidgetResizable(True); skala.setFrameShape(QFrame.NoFrame)
    skala.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    stapel.addWidget(skala)
    stapel.setFixedSize(breite, HOEHE_FORMENMENUE)
    v.addWidget(stapel)

    linie = trennlinie()
    v.addWidget(linie)
    z = knopf("standard", "  Form und Größe zurücksetzen", ohne_rand=True); z.setIcon(symbole.icon("rotate-ccw", ICON_GROSS)); z.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
    z.setMinimumHeight(DROPDOWN_KACHEL); dropdown_zeile(z)
    z.clicked.connect(lambda: waehlen(b.bildZuschneidenZuruecksetzen))
    v.addWidget(z)
    m.widget(wid)
    return m


# ---- Diagrammstile ------------------------------------------------------------------------------------------------------------
_BALKEN = ((0.62, 0.38, 0.28), (0.34, 0.78, 0.30), (0.52, 0.26, 0.46), (0.86, 0.46, 0.92))


def stil_bild(nr: int, groesse: QSize = STIL_KACHEL) -> QPixmap:
    """Vorschau des Diagrammstils ``nr`` (``diagramm.STILE``): Grund, Raster und Schrift wie im fertigen Diagramm, mit drei Säulenreihen."""
    from vcl.qt.rendering.diagramme import diagramm as D
    _n, grund, schrift, raster = _diagramm_stile_modell.stile()[nr]
    pm = QPixmap(groesse); pm.fill(QColor(grund))
    w, h = groesse.width(), groesse.height()
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    s = QColor(schrift)
    leise = QColor(s); leise.setAlpha(70)
    p.setPen(Qt.NoPen); p.setBrush(s)
    p.drawRoundedRect(QRectF(w * 0.30, 5, w * 0.40, 3), RADIUS_ZEICHNUNG_FEIN, RADIUS_ZEICHNUNG_FEIN)                    # Diagrammtitel
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
            p.setBrush(QColor(_diagrammtypen.farben()[si]))
            sx = ox + gi * gruppe + gruppe * 0.12 + si * gruppe * 0.25
            p.drawRect(QRectF(sx, oy + bh * (1 - wert), gruppe * 0.22, bh * wert))
    for si in range(3):                                                                  # Legende
        p.setBrush(QColor(_diagrammtypen.farben()[si]))
        x = w * 0.5 - 24 + si * 18
        p.drawRect(QRectF(x, h - 8, 4, 4)); p.setBrush(leise); p.drawRect(QRectF(x + 6, h - 7.5, 8, 3))
    p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1)); p.setBrush(Qt.NoBrush)
    p.drawRect(QRectF(0.5, 0.5, w - 1, h - 1))
    p.end()
    return pm


def _stilname(nr: int) -> str:
    from vcl.qt.rendering.diagramme import diagramm as D
    return _diagramm_stile_modell.stile()[nr][0]


def diagramm_stile_menue(b) -> RasterAuswahl:
    """Alle Diagrammstile als Kacheln (Name im Tipp); die Wahl ist ``diagrammStil``."""
    from vcl.qt.rendering.diagramme import diagramm as D
    m = RasterAuswahl(b.w, titel="Diagrammstile", spalten=2, groesse=STIL_KACHEL)
    for i in range(len(_diagramm_stile_modell.stile())):
        m.kachel(str(i), _stilname(i), stil_bild(i)).setCheckable(False)
    m.gewaehlt.connect(lambda k: b.diagrammStil(None, int(k)))
    return m


def diagramm_stile_galerie(b) -> dict:
    """Die Galerie im Band: eine Kachel je Stil und das Menü mit allen (Aufbau wie ``galerie_ttFormstile``)."""
    from vcl.qt.rendering import diagramme as D
    kacheln = [(_stilname(i), stil_bild(i), lambda i=i: b.diagrammStil(None, i)) for i in range(BAND_STILE)]      # wie in der Vorlage vier im Band, alle im Popup
    from vcl.qt.widgets.menues.dropdown.objektmenues.diagramm_popups import stile_popup
    return {"kacheln": kacheln, "menue": stile_popup(b, True), "name": "Diagrammstile"}            # der Pfeil zeigt alle Formatvorlagen (die Farben hat „Farbe ändern“)


# Dem Band bekannt: Name im Plan → Baustein. Sie gehen vor die gleichnamigen ``menue_…``/``galerie_…`` des Befehlsbausteins.
from vcl.qt.widgets.menues.dropdown.objektmenues import diagramm_popups as _dp                       # noqa: E402  die Popups am Diagramm
from vcl.qt.widgets.menues.dropdown.objektmenues import form_menues as _fm                           # noqa: E402  (Form bearbeiten, Formstile)
from vcl.qt.widgets.menues.dropdown.objektmenues import smartart_menues as _sm                       # noqa: E402  Menüs und Galerie für SmartArt

KLAPPEN = {"bildZuschneiden": zuschneiden_menue, **_dp.KLAPPEN, **_sm.KLAPPEN, **_fm.KLAPPEN}
from vcl.qt.widgets.objektwerkzeuge.diagramme.smartart_stil_kacheln import stile_galerie_org as _sa_stile  # noqa: E402
from writer.anbindung import diagramm_stile_modell as _diagramm_stile_modell
from writer.anbindung import diagrammtypen as _diagrammtypen

GALERIEN = {"diagrammStile": diagramm_stile_galerie, **_sm.GALERIEN, **_fm.GALERIEN, "smartartStile": _sa_stile}   # SmartArt-Stile mit Organigramm-Motiv wie in der Vorlage
FELDER = {**_dp.FELDER}                                                              # Eingabefelder des Bandes, die die Oberfläche selbst baut
