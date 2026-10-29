"""Menüs, Galerie und Miniaturen für SmartArt (Reiter „SmartArt-Design“, Schnellleiste am Knoten, Dialog „SmartArt-Grafik auswählen“).

Nur Aussehen: jede Wahl ruft einen Befehl des Bandes (``core/befehle/smartarttools.py``); gerechnet wird in ``editor/smartart.py``.

``form_menue(b)``        Form einfügen unter / über / nach / vor, Assistent einfügen (grau, wenn das Layout keinen Assistenten kennt)
``hierarchie_menue(b)``  Standard · Beide · Hängend links · Hängend rechts (grau bei anderen Layouts als Organigramm/Hierarchie)
``level_menue(b)``       Level erhöhen / reduzieren, Vorwärts, Rückwärts (grau, wo es nicht geht)
``stil_bild(nr)``        Kachel eines Formenstils (zwei Kästen übereinander), ``stile_galerie(b)`` die fünf Kacheln im Band, ``stile_menue(b)`` dasselbe als Popup
``layout_menue(b)``      Layout ändern: die 15 Layouts des Katalogs mit Anzeigenamen
``miniatur(schluessel, grau)``  gezeichnete Miniatur eines Layouts (grau im Raster, blau in der Vorschau) für den Dialog
``KLAPPEN`` / ``GALERIEN``  melden die Bausteine dem Band (``bild_diagramm_menues.py`` fasst sie mit den übrigen zusammen)
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPen, QPixmap, QPolygonF

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
from lunivo_writer.ui.widgets import icons

STIL_KACHEL = QSize(46, 40)


def _sa(b) -> dict:
    from lunivo_writer.editor import smartart as SA
    return (SA.daten_der_auswahl(b.ed) if getattr(b, "ed", None) else None) or {}


def _sym(name: str) -> QIcon:
    return icons.icon(name, 16)


class _Auffrischend(MenueListe):
    """Ein Menü, das seine Zeilen bei jedem Öffnen neu bewertet (grau, Haken) — das Band baut ein Menü nur einmal."""

    def __init__(self, bau, parent=None):
        super().__init__(parent)
        self._bau = bau
        self.aboutToShow.connect(self._neu)
        self._neu()

    def _neu(self) -> None:
        self.clear()
        self._bau(self)


# ---- Form einfügen, Level, Hierarchie ----------------------------------------------------------------------------------------------
def form_menue(b) -> MenueListe:
    def bau(m: MenueListe) -> None:
        geht = bool(b.kann_smartartFormEinfuegen())
        hier = geht and bool(b._sa_kann("hierarchie"))
        for wie, text, sym in (("unter", "Form einfügen unter", "arrow-down"), ("ueber", "Form einfügen über", "arrow-up"),
                               ("nach", "Form einfügen nach", "arrow-right"), ("vor", "Form einfügen vor", "arrow-left")):
            m.eintrag(text, lambda w=wie: b.smartartFormEinfuegen(None, w), symbol=_sym(sym), aktiv=geht)
        m.eintrag("Assistent einfügen", lambda: b.smartartFormEinfuegen(None, "assistent"), symbol=_sym("user-plus"), aktiv=hier)
    return _Auffrischend(bau)


def level_menue(b) -> MenueListe:
    def bau(m: MenueListe) -> None:
        m.eintrag("Level erhöhen", lambda: b.smartartLevelErhoehen(), symbol=_sym("arrow-left"), aktiv=bool(b.kann_smartartLevelErhoehen()))
        m.eintrag("Level reduzieren", lambda: b.smartartLevelReduzieren(), symbol=_sym("arrow-right"), aktiv=bool(b.kann_smartartLevelReduzieren()))
        m.eintrag("Vorwärts", lambda: b.smartartVorwaerts(), symbol=_sym("arrow-up"), aktiv=bool(b.kann_smartartVorwaerts()))
        m.eintrag("Rückwärts", lambda: b.smartartRueckwaerts(), symbol=_sym("arrow-down"), aktiv=bool(b.kann_smartartRueckwaerts()))
    return _Auffrischend(bau)


def hierarchie_menue(b, mit_rechts_links: bool = False) -> MenueListe:
    """Die Layoutvarianten des Organigramms; ``mit_rechts_links``: oben noch „Layout von rechts nach links“ (Schnellleiste am Knoten)."""
    from lunivo_writer.editor import smartart as SA
    sym = {"standard": "network", "beide": "workflow", "haengend_links": "list-tree", "haengend_rechts": "list-tree"}

    def bau(m: MenueListe) -> None:
        geht = bool(b.kann_smartartHierarchie())
        if mit_rechts_links:
            m.eintrag("Layout von rechts nach links", lambda: b.smartartRechtsLinks(), symbol=_sym("arrow-left-right"),
                      haken=bool(b.an_smartartRechtsLinks()), aktiv=bool(b.kann_smartartRechtsLinks()))
        aktuell = _sa(b).get("hierarchie") or "standard"
        for schl, text in SA.HIERARCHIEN:
            m.eintrag(text, lambda s=schl: b.smartartHierarchie(None, s), symbol=_sym(sym[schl]), haken=geht and aktuell == schl, aktiv=geht)
    return _Auffrischend(bau)


def layout_menue(b) -> MenueListe:
    """„Layout ändern“: die 15 Layouts des Katalogs mit ihren Anzeigenamen; das gewählte trägt einen Haken."""
    from lunivo_writer.editor import smartart as SA

    def bau(m: MenueListe) -> None:
        aktuell, geht = _sa(b).get("layout"), bool(b.kann_smartartStil())
        for e in SA.LAYOUT_KATALOG:
            k = e["schluessel"]
            m.eintrag(e["name"], lambda k=k: b.smartartLayout(None, k), symbol=QIcon(miniatur(k, True, QSize(28, 20))), haken=aktuell == k, aktiv=geht)
    return _Auffrischend(bau)


# ---- Stile ---------------------------------------------------------------------------------------------------------------------------
def stil_bild(nr: int, groesse: QSize = STIL_KACHEL, blau: str = Farbe.AKZENT_DUNKEL) -> QPixmap:
    """Zwei übereinanderstehende Kästen im Formenstil ``nr`` (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D)."""
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    w, h = groesse.width(), groesse.height()
    c = QColor(blau)
    kasten = [QRectF(w * 0.18, h * 0.10, w * 0.64, h * 0.34), QRectF(w * 0.18, h * 0.54, w * 0.64, h * 0.34)]
    for r in kasten:
        if nr == 2:                                          # Hell: blasse Fläche
            p.setBrush(c.lighter(160)); p.setPen(QPen(c.lighter(130), 1))
        elif nr == 3:                                        # Kräftig: dunkler Rand
            p.setBrush(c); p.setPen(QPen(c.darker(150), 2))
        elif nr == 4:                                        # 3D: Verlauf
            g = QLinearGradient(r.topLeft(), r.bottomLeft()); g.setColorAt(0, c.lighter(135)); g.setColorAt(1, c.darker(125))
            p.setBrush(g); p.setPen(QPen(c.darker(150), 1))
        elif nr == 1:                                        # Einfach: Fläche mit dünnem Rand
            p.setBrush(c); p.setPen(QPen(c.darker(125), 1))
        else:                                                # Flach
            p.setBrush(c); p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 2, 2) if nr in (1, 4) else p.drawRect(r)
    p.end()
    return pm


def stile_menue(b) -> RasterAuswahl:
    from lunivo_writer.editor import smartart as SA
    m = RasterAuswahl(b.w, spalten=len(SA.STILE), groesse=STIL_KACHEL)
    aktuell = _sa(b).get("stil", 1)
    for i, name in enumerate(SA.STILE):
        m.kachel(str(i), name, stil_bild(i), aktuell=i == aktuell)
    m.gewaehlt.connect(lambda k: b.smartartStil(None, int(k)))
    return m


def stile_galerie(b) -> dict:
    from lunivo_writer.editor import smartart as SA
    return {"kacheln": [(name, stil_bild(i, QSize(56, 34)), lambda i=i: b.smartartStil(None, i)) for i, name in enumerate(SA.STILE)],
            "menue": stile_menue(b), "name": "Formenstile"}


# ---- Miniaturen der Layouts ----------------------------------------------------------------------------------------------------------
def _farben(grau: bool) -> tuple[QColor, QColor, QColor]:
    """(Fläche, Rand, Strich für Text) — grau im Raster des Dialogs, blau in der großen Vorschau."""
    if grau:
        return QColor(Farbe.GRAU_HELL), QColor(Farbe.GRAU), QColor(Farbe.TINTE)
    return QColor(Farbe.AKZENT_DUNKEL), QColor(Farbe.AKZENT), QColor(Farbe.WEISS)


def _kasten(p: QPainter, r: QRectF, fl: QColor, rand: QColor, strich: QColor, text: bool = True, rund: float = 0) -> None:
    p.setBrush(fl); p.setPen(QPen(rand, 1))
    p.drawRoundedRect(r, rund, rund) if rund else p.drawRect(r)
    if text and r.width() > 8 and r.height() > 5:
        p.setPen(QPen(strich, 1)); y = r.center().y(); w = min(r.width() * 0.5, 14)
        p.drawLine(QPointF(r.center().x() - w / 2, y), QPointF(r.center().x() + w / 2, y))


def _pfeil(p: QPainter, a: QPointF, b: QPointF, col: QColor) -> None:
    w = math.atan2(b.y() - a.y(), b.x() - a.x()); l = 4.0
    p.setPen(QPen(col, 1)); p.setBrush(Qt.NoBrush)
    p.drawLine(a, b)
    p.setBrush(col)
    p.drawPolygon(QPolygonF([b, QPointF(b.x() - l * math.cos(w - 0.5), b.y() - l * math.sin(w - 0.5)),
                             QPointF(b.x() - l * math.cos(w + 0.5), b.y() - l * math.sin(w + 0.5))]))


def _m_organigramm(p, W, H, c):
    fl, ra, st = c
    kw, kh = W * 0.26, H * 0.2
    _kasten(p, QRectF(W * 0.37, H * 0.06, kw, kh), fl, ra, st)
    _kasten(p, QRectF(W * 0.08, H * 0.34, kw, kh), fl, ra, st)
    xs = (0.04, 0.37, 0.70)
    p.setPen(QPen(ra, 1))
    p.drawLine(QPointF(W * 0.5, H * 0.26), QPointF(W * 0.5, H * 0.54))             # Stamm vom obersten Kasten
    p.drawLine(QPointF(W * 0.34, H * 0.44), QPointF(W * 0.5, H * 0.44))            # Abzweig zum Kasten links
    p.drawLine(QPointF(W * 0.17, H * 0.54), QPointF(W * 0.83, H * 0.54))           # Verteiler über den drei unteren
    for x in xs:
        p.drawLine(QPointF(x * W + kw / 2, H * 0.54), QPointF(x * W + kw / 2, H * 0.66))
        _kasten(p, QRectF(x * W, H * 0.66, kw, kh), fl, ra, st)


def _m_liste(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        y = H * (0.08 + i * 0.3)
        _kasten(p, QRectF(W * 0.08, y, W * 0.84, H * 0.2), fl, ra, st)


def _m_prozess(p, W, H, c):
    fl, ra, st = c
    kw = W * 0.22
    for i in range(3):
        x = W * (0.04 + i * 0.34)
        _kasten(p, QRectF(x, H * 0.36, kw, H * 0.28), fl, ra, st)
        if i < 2:
            _pfeil(p, QPointF(x + kw + 1, H * 0.5), QPointF(x + W * 0.34 - 1, H * 0.5), ra)


def _m_zyklus(p, W, H, c):
    fl, ra, st = c
    mx, my, r = W / 2, H / 2, min(W, H) * 0.36
    for i in range(4):
        w = math.radians(-90 + i * 90)
        _kasten(p, QRectF(mx + r * math.cos(w) - W * 0.1, my + r * math.sin(w) - H * 0.09, W * 0.2, H * 0.18), fl, ra, st, rund=3)
    p.setPen(QPen(ra, 1)); p.setBrush(Qt.NoBrush)
    p.drawArc(QRectF(mx - r * 0.62, my - r * 0.62, r * 1.24, r * 1.24), 20 * 16, 320 * 16)


def _m_pyramide(p, W, H, c):
    fl, ra, st = c
    p.setPen(QPen(ra, 1)); p.setBrush(fl)
    p.drawPolygon(QPolygonF([QPointF(W * 0.5, H * 0.06), QPointF(W * 0.82, H * 0.9), QPointF(W * 0.18, H * 0.9)]))
    p.setPen(QPen(ra, 1))
    for y in (0.4, 0.65):
        d = (y - 0.06) / 0.84 * 0.32
        p.drawLine(QPointF(W * (0.5 - d), H * y), QPointF(W * (0.5 + d), H * y))


def _m_spalten(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        x = W * (0.08 + i * 0.3)
        _kasten(p, QRectF(x, H * 0.1, W * 0.26, H * 0.18), fl, ra, st)
        p.setBrush(QColor(Farbe.WEISS)); p.setPen(QPen(ra, 1)); p.drawRect(QRectF(x, H * 0.28, W * 0.26, H * 0.6))
        p.setPen(QPen(st if c[0].lightness() > 150 else fl, 1))
        for j in range(2):
            y = H * (0.42 + j * 0.16)
            p.drawPoint(QPointF(x + 4, y)); p.drawLine(QPointF(x + 7, y), QPointF(x + W * 0.2, y))


def _m_gruppen(p, W, H, c):
    fl, ra, st = c
    p.setBrush(Qt.NoBrush); p.setPen(QPen(ra, 1))
    for i in range(2):
        r = QRectF(W * 0.06 + i * W * 0.46, H * 0.12, W * 0.42, H * 0.76)
        p.drawRect(r)
        _kasten(p, QRectF(r.left() + 3, r.top() + 3, r.width() - 6, H * 0.18), fl, ra, st)
        for j in range(2):
            _kasten(p, QRectF(r.left() + 6, r.top() + H * 0.28 + j * H * 0.22, r.width() - 12, H * 0.16), QColor(Farbe.WEISS) if st.lightness() < 150 else fl, ra, st)


def _m_matrix(p, W, H, c):
    fl, ra, st = c
    for i in range(4):
        _kasten(p, QRectF(W * (0.18 + (i % 2) * 0.34), H * (0.06 + (i // 2) * 0.3), W * 0.3, H * 0.26), fl, ra, st)
    _kasten(p, QRectF(W * 0.35, H * 0.7, W * 0.3, H * 0.24), fl, ra, st)


def _m_chevron(p, W, H, c):
    fl, ra, st = c
    p.setBrush(fl); p.setPen(QPen(ra, 1))
    for i in range(3):
        x = W * (0.04 + i * 0.3)
        p.drawPolygon(QPolygonF([QPointF(x, H * 0.3), QPointF(x + W * 0.2, H * 0.3), QPointF(x + W * 0.3, H * 0.5), QPointF(x + W * 0.2, H * 0.7), QPointF(x, H * 0.7),
                                 QPointF(x + W * 0.1, H * 0.5)]))


def _m_radial(p, W, H, c):
    fl, ra, st = c
    mx, my, d = W / 2, H / 2, min(W, H) * 0.3
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        k = QPointF(mx + dx * d * 1.35, my + dy * d * 1.3)
        _pfeil(p, QPointF(mx + dx * d * 0.45, my + dy * d * 0.45), QPointF(mx + dx * d * 0.85, my + dy * d * 0.85), ra)
        p.setBrush(fl); p.setPen(QPen(ra, 1)); p.drawEllipse(k, d * 0.3, d * 0.3)
    p.setBrush(fl); p.setPen(QPen(ra, 1)); p.drawEllipse(QPointF(mx, my), d * 0.38, d * 0.38)


def _m_zielscheibe(p, W, H, c):
    fl, ra, st = c
    mx, my = W / 2, H / 2
    for i, f in enumerate((0.44, 0.31, 0.18)):
        p.setBrush(fl if i % 2 == 0 else QColor(Farbe.WEISS)); p.setPen(QPen(ra, 1))
        r = min(W, H) * f
        p.drawEllipse(QPointF(mx, my), r, r)


def _m_trichter(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        w = W * (0.8 - i * 0.22); y = H * (0.1 + i * 0.28)
        _kasten(p, QRectF(W / 2 - w / 2, y, w, H * 0.22), fl, ra, st)


def _m_zeitachse(p, W, H, c):
    fl, ra, st = c
    p.setPen(QPen(ra, 2)); p.drawLine(QPointF(W * 0.06, H * 0.5), QPointF(W * 0.94, H * 0.5))
    for i in range(4):
        x = W * (0.15 + i * 0.23)
        p.setBrush(fl); p.setPen(QPen(ra, 1)); p.drawEllipse(QPointF(x, H * 0.5), 3.5, 3.5)
        _kasten(p, QRectF(x - W * 0.09, H * (0.16 if i % 2 == 0 else 0.62), W * 0.18, H * 0.22), fl, ra, st)


def _m_stufen(p, W, H, c):
    fl, ra, st = c
    for i in range(4):
        h = H * (0.22 + i * 0.2)
        _kasten(p, QRectF(W * (0.06 + i * 0.22), H * 0.92 - h, W * 0.2, h), fl, ra, st, text=False)


def _zeile(p: QPainter, x: float, y: float, w: float, col: QColor, punkt: bool = True) -> None:
    """Eine Aufzählungszeile: Punkt und Strich."""
    p.setPen(QPen(col, 1))
    if punkt:
        p.drawPoint(QPointF(x, y)); p.drawLine(QPointF(x + 3, y), QPointF(x + w, y))
    else:
        p.drawLine(QPointF(x, y), QPointF(x + w, y))


def _m_punktliste(p, W, H, c):
    fl, ra, st = c
    for i in range(2):
        y = H * (0.06 + i * 0.48)
        _kasten(p, QRectF(W * 0.08, y, W * 0.84, H * 0.22), fl, ra, st)
        _zeile(p, W * 0.1, y + H * 0.31, W * 0.2, st)
        _zeile(p, W * 0.1, y + H * 0.39, W * 0.2, st)


def _m_balkenliste(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        y = H * (0.08 + i * 0.3)
        p.setBrush(QColor(Farbe.WEISS)); p.setPen(QPen(ra, 1)); p.drawRect(QRectF(W * 0.08, y + H * 0.02, W * 0.84, H * 0.16))
        _kasten(p, QRectF(W * 0.08, y, W * 0.56, H * 0.2), fl, ra, st)


def _m_beschreibungsliste(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        y = H * (0.08 + i * 0.3)
        p.setBrush(QColor(Farbe.WEISS)); p.setPen(QPen(ra, 1)); p.drawRect(QRectF(W * 0.42, y, W * 0.5, H * 0.2))
        _kasten(p, QRectF(W * 0.08, y, W * 0.3, H * 0.2), fl, ra, st)
        _zeile(p, W * 0.46, y + H * 0.06, W * 0.2, ra); _zeile(p, W * 0.46, y + H * 0.14, W * 0.3, ra)


def _m_spaltenrahmen(p, W, H, c):
    fl, ra, st = c
    p.setBrush(QColor(Farbe.WEISS)); p.setPen(QPen(ra, 1)); p.drawRect(QRectF(W * 0.08, H * 0.1, W * 0.84, H * 0.8))
    _kasten(p, QRectF(W * 0.08, H * 0.1, W * 0.84, H * 0.16), fl, ra, st)
    _kasten(p, QRectF(W * 0.08, H * 0.76, W * 0.84, H * 0.14), fl, ra, st, text=False)
    p.setPen(QPen(ra, 1))
    for x in (0.08 + 0.28, 0.08 + 0.56):
        p.drawLine(QPointF(W * x, H * 0.26), QPointF(W * x, H * 0.76))


def _m_bildliste(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        y = H * (0.08 + i * 0.3)
        _kasten(p, QRectF(W * 0.08, y, W * 0.84, H * 0.24), fl, ra, st, text=False)
        p.setBrush(QColor(Farbe.WEISS)); p.setPen(QPen(ra, 1)); p.drawRect(QRectF(W * 0.1, y + H * 0.03, H * 0.18, H * 0.18))
        _zeile(p, W * 0.4, y + H * 0.07, W * 0.3, st); _zeile(p, W * 0.4, y + H * 0.15, W * 0.2, st)


def _m_perspektive(p, W, H, c):
    fl, ra, st = c
    p.setBrush(fl); p.setPen(QPen(ra, 1))
    for i in range(3):
        x = W * (0.07 + i * 0.3)
        p.drawPolygon(QPolygonF([QPointF(x, H * 0.18), QPointF(x + W * 0.26, H * 0.06), QPointF(x + W * 0.26, H * 0.94), QPointF(x, H * 0.82)]))
        p.setPen(QPen(st, 1)); p.drawLine(QPointF(x + 4, H * 0.3), QPointF(x + W * 0.16, H * 0.27))
        for j in range(2):
            _zeile(p, x + 4, H * (0.55 + j * 0.1), W * 0.14, st)
        p.setPen(QPen(ra, 1))


def _m_konvergenz(p, W, H, c):
    fl, ra, st = c
    for x, y in ((0.05, 0.22), (0.37, 0.06), (0.69, 0.22)):
        _kasten(p, QRectF(W * x, H * y, W * 0.26, H * 0.2), fl, ra, st)
    for x, y, tx, ty in ((0.18, 0.44, 0.38, 0.66), (0.5, 0.28, 0.5, 0.62), (0.82, 0.44, 0.62, 0.66)):
        _pfeil(p, QPointF(W * x, H * y), QPointF(W * tx, H * ty), ra)
    p.setBrush(fl); p.setPen(QPen(ra, 1)); p.drawEllipse(QPointF(W / 2, H * 0.8), H * 0.14, H * 0.14)


def _m_kartenprozess(p, W, H, c):
    fl, ra, st = c
    for i in range(3):
        x = W * (0.12 + i * 0.3)
        for d in (2, 1, 0):
            r = QRectF(x - d * W * 0.025, H * 0.38 - d * H * 0.06, W * 0.17, H * 0.28)
            p.setBrush(QColor(Farbe.WEISS) if d else fl); p.setPen(QPen(ra, 1)); p.drawRect(r)
        if i < 2:
            _pfeil(p, QPointF(x + W * 0.18, H * 0.52), QPointF(x + W * 0.245, H * 0.52), ra)


def _m_kreisbeziehung(p, W, H, c):
    fl, ra, st = c
    mx, my, r = W / 2, H / 2, min(W, H) * 0.3
    p.setBrush(fl); p.setPen(QPen(ra, 1)); p.drawEllipse(QPointF(mx, my), r, r)
    k = r * 0.52
    p.setBrush(QColor(Farbe.WEISS))
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        p.drawEllipse(QPointF(mx + dx * r, my + dy * r), k, k)
    p.setPen(QPen(st, 1)); p.drawLine(QPointF(mx - r * 0.3, my), QPointF(mx + r * 0.3, my))
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        p.drawLine(QPointF(mx + dx * r * 1.1 - k * 0.3, my + dy * r * 1.1), QPointF(mx + dx * r * 1.1 + k * 0.3, my + dy * r * 1.1))


def _m_segmentzyklus(p, W, H, c):
    fl, ra, st = c
    mx, my, r = W / 2, H / 2, min(W, H) * 0.3
    p.setBrush(fl); p.setPen(QPen(ra, 1)); p.drawEllipse(QPointF(mx, my), r, r)
    p.drawLine(QPointF(mx - r, my), QPointF(mx + r, my)); p.drawLine(QPointF(mx, my - r), QPointF(mx, my + r))
    p.setBrush(QColor(Farbe.WEISS)); p.drawEllipse(QPointF(mx, my), r * 0.38, r * 0.38)
    p.setBrush(Qt.NoBrush); p.drawArc(QRectF(mx - r * 0.2, my - r * 0.2, r * 0.4, r * 0.4), 30 * 16, 290 * 16)
    for x, y in ((0.02, 0.08), (0.76, 0.08), (0.02, 0.72), (0.76, 0.72)):
        _kasten(p, QRectF(W * x, H * y, W * 0.22, H * 0.2), QColor(Farbe.WEISS), ra, st)


_MINIATUR = {"Organigramm": _m_organigramm, "Hierarchie": _m_organigramm, "Liste": _m_liste, "Prozess": _m_prozess, "Zyklus": _m_zyklus,
             "Pyramide": _m_pyramide, "Spalten": _m_spalten, "Gruppen": _m_gruppen, "Matrix": _m_matrix, "Chevron": _m_chevron, "Radial": _m_radial,
             "Zielscheibe": _m_zielscheibe, "Trichter": _m_trichter, "Zeitachse": _m_zeitachse, "Stufen": _m_stufen,
             "Blockraster": _m_matrix, "Punktliste": _m_punktliste, "Balkenliste": _m_balkenliste, "Beschreibungsliste": _m_beschreibungsliste,
             "Spaltenrahmen": _m_spaltenrahmen, "Bildliste": _m_bildliste, "Perspektive": _m_perspektive, "Konvergenz": _m_konvergenz,
             "Kartenprozess": _m_kartenprozess, "Kreisbeziehung": _m_kreisbeziehung, "Segmentzyklus": _m_segmentzyklus}


def zeichne_miniatur(p: QPainter, r: QRectF, schluessel: str, grau: bool = True) -> None:
    """Zeichnet die Miniatur des Layouts in ``r``."""
    p.save(); p.setRenderHint(QPainter.Antialiasing); p.translate(r.topLeft())
    f = _MINIATUR.get(schluessel, _m_liste)
    f(p, r.width(), r.height(), _farben(grau))
    p.restore()


def miniatur(schluessel: str, grau: bool = True, groesse: QSize = QSize(64, 48)) -> QPixmap:
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    zeichne_miniatur(p, QRectF(0, 0, groesse.width(), groesse.height()), schluessel, grau)
    p.end()
    return pm


# ---- Dem Band melden ------------------------------------------------------------------------------------------------------------------
KLAPPEN = {"smartartFormEinfuegen": form_menue, "smartartHierarchie": hierarchie_menue, "smartartLevel": level_menue,
           "smartartStilKlappe": stile_menue, "smartartLayout": layout_menue}
GALERIEN = {"smartartStile": stile_galerie}
