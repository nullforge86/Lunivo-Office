"""Rahmen seite: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QToolButton, QWidget
from core.objekte.formen.linie import LINIENBREITEN, STILE, Linie
from vcl.qt.widgets.menues.dropdown.auswahl.farb_feld import FarbFeld
from vcl.qt.widgets.bausteine.rahmen.linien import RahmenSeiten, rahmen_symbol
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_LINIENBREITE_BILD, GROESSE_LINIENBREITE_BILD_STANDARD, GROESSE_RAHMENART_BILD, GROESSE_RAHMENSEITE_KNOPF, ICON_KNOPF_GROSS, ICON_MITTEL, RAND_RAHMEN_SEITE
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_ZEICHEN_ZAHL, STIFT_BETONT
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf, werkzeugknopf
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.dialoge.formatierung.kanten_flaeche import _KantenFlaeche
from vcl.qt.widgets.dialoge.formatierung.polster_dialog import _PolsterDialog
from vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_hilfen import _KANTE, _Vorschau
from vcl.qt.widgets.dialoge.formatierung.seiten_optionen_dialog import _SeitenOptionenDialog


KANTEN = (("t", "Oben", RahmenSeiten.OBEN), ("b", "Unten", RahmenSeiten.UNTEN), ("l", "Links", RahmenSeiten.LINKS),
          ("r", "Rechts", RahmenSeiten.RECHTS), ("h", "Zwischen Absätzen", RahmenSeiten.INNEN_H))


HINWEIS = "Diagramm oder Schaltflächen klicken, um Rahmen hinzuzufügen"


def _einstellung_symbol(art: str, px: int = 28) -> QIcon:
    """Kleines Blatt mit Textzeilen und dem Rahmen, den die Einstellung setzt."""
    pm = QPixmap(px, px); pm.fill(Qt.transparent)
    p = QPainter(pm)
    r = QRectF(4, 4, px - 8, px - 8)
    p.setPen(Qt.NoPen); p.setBrush(QColor(Farbe.GRAU_HELL))
    for i in range(5):
        p.drawRect(QRectF(r.left() + 3, r.top() + 4 + i * (r.height() - 8) / 5, r.width() - 6 - (i == 4) * 6, 1.6))
    stark, blass = QPen(QColor(Farbe.GITTER), STIFT_BETONT), QPen(QColor(Farbe.GRAU), 1, Qt.DotLine)
    p.setBrush(Qt.NoBrush)
    if art == "kontur":
        p.setPen(stark); p.drawRect(r)
    elif art == "alle":
        p.setPen(stark); p.drawRect(r); p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))
        p.drawLine(QPointF(r.center().x(), r.top()), QPointF(r.center().x(), r.bottom()))
    elif art == "raster":
        p.setPen(blass); p.drawRect(r); p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))
        p.drawLine(QPointF(r.center().x(), r.top()), QPointF(r.center().x(), r.bottom()))
    elif art == "anpassen":
        p.setPen(blass); p.drawRect(r)
        p.setPen(stark); p.drawLine(r.topLeft(), r.bottomLeft()); p.drawLine(r.bottomLeft(), r.bottomRight())
    p.end()
    return QIcon(pm)


def _stil_symbol(art: str, groesse: QSize = QSize(*GROESSE_RAHMENART_BILD)) -> QIcon:
    """Probe einer Linienart für die Liste „Formatvorlage“."""
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    Linie(Farbe.GITTER, 1.5, art).zeichne(p, 3, groesse.height() / 2, groesse.width() - 3, groesse.height() / 2, 96 / 72)
    p.end()
    return QIcon(pm)


def _breite_symbol(pt: float, groesse: QSize = QSize(*GROESSE_LINIENBREITE_BILD_STANDARD)) -> QIcon:
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setPen(QPen(QColor(Farbe.GITTER), max(1.0, pt * 96 / 72), Qt.SolidLine, Qt.FlatCap))
    p.drawLine(0, groesse.height() // 2, groesse.width(), groesse.height() // 2)
    p.end()
    return QIcon(pm)


class _RahmenSeite(QWidget):
    """Einstellung · Linienart · Farbe · Breite · Vorschau mit Kantenknöpfen · Übernehmen für."""
    geaendert = Signal()

    def __init__(self, linie: Linie | None, *, seitenrand: bool = False, innen_h: bool = False, fuer: list[str] | None = None,
                 abstand_mm: float | None = None):
        super().__init__()
        self.seitenrand, self.innen_h = seitenrand, innen_h
        self.abstand_mm = abstand_mm if abstand_mm is not None else 8.0
        self.rand_optionen = {"messen": "text", "abstand": (1.0, 1.0, 4.0, 4.0), "ausrichten": False, "vordergrund": True, "kopf": False, "fuss": False}   # Seitenrand ▸ Optionen
        basis = linie or Linie(Farbe.SCHWARZ, 0.75, "einfach")
        self.seiten = linie.seiten if linie else ""
        g = FormularGitter(self); g.setContentsMargins(*RAND_RAHMEN_SEITE)
        self._bauen_einstellung(g)
        self._bauen_vorschau(g)
        self._bauen_farbe_breite_art(g, basis)
        self._bauen_linienart(g)
        self._bauen_fuer(g, fuer, linie)
        self._anfangswerte(basis)

    def _bauen_einstellung(self, g) -> None:
        """Einstellung: eine Reihe Symbole (der Name steht im Tipp), bei Platzmangel in der nächsten Zeile weiter."""
        innen_h, seitenrand = self.innen_h, self.seitenrand
        g.breit(abschnittstitel("Einstellung"))
        reihe = FlussLayout(4)
        self.einstellung: dict[str, QToolButton] = {}
        for art, text in (("ohne", "Ohne"), ("kontur", "Kontur"), ("alle", "Alle"), ("raster", "Raster"), ("anpassen", "Anpassen")):
            b = werkzeugknopf("standard", umschaltbar=True, tooltip=text, name=text, flach=False); b.setAutoExclusive(True)
            b.setIcon(_einstellung_symbol("ohne" if art == "ohne" else art)); b.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS)); b.setFixedSize(*GROESSE_RAHMENSEITE_KNOPF); b.setAutoRaise(True)
            eigenschaft(b, rolle="rahmenwahl")
            b.clicked.connect(lambda _c=False, a=art: self._setze_einstellung(a))
            self.einstellung[art] = b
            reihe.addWidget(b)
        g.breit(reihe)
        self.einstellung["raster"].setEnabled(False); self.einstellung["raster"].setToolTip("Raster: nur für Tabellen")
        self.einstellung["alle"].setEnabled(innen_h)
        self.einstellung["alle"].setToolTip("Alle" if innen_h else "Alle: nur, wenn mehrere Absätze oder Tabellenzellen gemeint sind")
        if seitenrand:                                           # um eine Seite gibt es nur Ohne, Kontur und Anpassen
            self.einstellung["alle"].setVisible(False); self.einstellung["raster"].setVisible(False)

    def _bauen_vorschau(self, g) -> None:
        """Vorschau mit Kantenknöpfen (wächst mit der Breite)."""
        innen_h = self.innen_h
        g.breit(abschnittstitel("Vorschau"))
        self.vorschau = _Vorschau(); self.vorschau.setToolTip(HINWEIS)
        self.vorschau.mit_h = innen_h
        self.kantenknoepfe: dict[str, QToolButton] = {}
        for k, text, flagge in KANTEN:
            if k == "h" and not innen_h:
                continue
            b = werkzeugknopf("standard", umschaltbar=True, flach=False); b.setIcon(rahmen_symbol(flagge, 22)); b.setToolTip(text); b.setIconSize(QSize(ICON_MITTEL, ICON_MITTEL))
            b.setAutoRaise(True); b.setFixedSize(_KANTE, _KANTE)
            eigenschaft(b, rolle="rahmenknopf")
            b.toggled.connect(lambda an, k=k: self._kante(k, an))
            self.kantenknoepfe[k] = b
        self.kasten = _KantenFlaeche(self.vorschau, [self.kantenknoepfe[k] for k in ("t", "h", "b") if k in self.kantenknoepfe],
                                     self.kantenknoepfe["l"], self.kantenknoepfe["r"])
        g.breit(self.kasten)
        self.vorschau.kante.connect(lambda k: self.kantenknoepfe[k].toggle() if k in self.kantenknoepfe else None)

    def _bauen_farbe_breite_art(self, g, basis) -> None:
        seitenrand = self.seitenrand
        self.farbe = FarbFeld("" if basis.farbe in ("", Farbe.SCHWARZ) else basis.farbe, "Rahmenfarbe", keine_text="Automatisch")
        self.breite = Auswahlfeld(); self.breite.setIconSize(QSize(*GROESSE_LINIENBREITE_BILD))
        for b in LINIENBREITEN:
            self.breite.addItem(_breite_symbol(b, QSize(*GROESSE_LINIENBREITE_BILD)), f"{b:g}".replace(".", ",") + " Pt", b)
        self.breite.zeichen(DROPDOWN_ZEICHEN_ZAHL)
        g.reihe(("Farbe:", self.farbe), ("Breite:", self.breite))
        self.kunst = Auswahlfeld()                                 # Art: Kunstrahmen aus Figuren statt einer Linie (nur um die Seite)
        from core.formatierung.rahmen.seitenrahmen import KUNST
        for k, name in KUNST:
            self.kunst.addItem(name, k)
        self.kunst.setVisible(seitenrand)
        g.reihe(("Art:", self.kunst))
        self.kunst.currentIndexChanged.connect(lambda _i: self._neu())

    def _bauen_linienart(self, g) -> None:
        seitenrand = self.seitenrand
        g.breit(abschnittstitel("Linienart"))
        self.arten = QListWidget(); self.arten.setIconSize(QSize(*GROESSE_RAHMENART_BILD)); self.arten.setFixedHeight(46 if seitenrand else 104)    # Seitenrand hat zusätzlich „Art:“: sonst rollt die Seite
        for k in STILE:
            it = QListWidgetItem(_stil_symbol(k), ""); it.setData(Qt.UserRole, k); it.setToolTip(STILE[k][0])
            self.arten.addItem(it)
        g.breit(self.arten)

    def _bauen_fuer(self, g, fuer, linie) -> None:
        """Übernehmen für, Optionen."""
        self.fuer = Auswahlfeld(); self.fuer.addItems(fuer or ["Absatz"]); self.fuer.setToolTip("Übernehmen für")
        self.optionen = knopf("standard", "Optionen …")
        self.optionen.clicked.connect(self._optionen)
        self.polster = linie.polster() if linie and linie.polster() else (1.0, 1.0, 4.0, 4.0)    # Abstand zum Text: oben, unten, links, rechts (pt)
        g.reihe(("Für:", self.fuer))
        g.breit(self.optionen)

    def _anfangswerte(self, basis) -> None:
        """Anfangswerte, Verkabelung."""
        i = self.arten.row(next((self.arten.item(r) for r in range(self.arten.count()) if self.arten.item(r).data(Qt.UserRole) == basis.art), self.arten.item(0)))
        self.arten.setCurrentRow(i)
        self.breite.setCurrentIndex(min(range(self.breite.count()), key=lambda j: abs(self.breite.itemData(j) - basis.breite_pt)))
        self.arten.currentRowChanged.connect(lambda _r: self._neu())
        self.breite.currentIndexChanged.connect(lambda _i: self._neu())
        self.farbe.farbeGeaendert.connect(lambda _f: self._neu())
        self._zeige_seiten()

    # ---- Zustand
    def linie_wert(self) -> Linie:
        it = self.arten.currentItem()
        ab = ",".join(f"{x:g}" for x in self.polster) if not self.seitenrand and self.polster != (1.0, 1.0, 4.0, 4.0) else ""
        return Linie(self.farbe.farbe or Farbe.SCHWARZ, float(self.breite.currentData()), it.data(Qt.UserRole) if it else "einfach", abstand=ab)

    def _setze_einstellung(self, art: str) -> None:
        if art == "ohne":
            self.seiten = ""
        elif art == "kontur":
            self.seiten = "tblr"
        elif art == "alle" and self.innen_h:
            self.seiten = "tblrh"
        self._zeige_seiten()

    def _kante(self, k: str, an: bool) -> None:
        s = set(self.seiten)
        (s.add if an else s.discard)(k)
        self.seiten = "".join(c for c in "tblrh" if c in s)
        self._zeige_seiten()

    def _zeige_seiten(self) -> None:
        for k, b in self.kantenknoepfe.items():
            b.blockSignals(True); b.setChecked(k in self.seiten); b.blockSignals(False)
        gewaehlt = "ohne" if not self.seiten else "kontur" if self.seiten == "tblr" else "alle" if self.seiten == "tblrh" and self.innen_h else "anpassen"
        self.einstellung[gewaehlt].setChecked(True)
        self._neu()

    def _neu(self) -> None:
        v = self.vorschau
        v.seiten, v.linie = self.seiten, self.linie_wert()
        if self.seitenrand:
            v.seitenrand = (self.linie_wert(), self.abstand_mm)
        v.update()
        self.geaendert.emit()

    def _abstand_vorschau(self) -> None:
        """Der Abstand, den die Vorschau des Seitenrahmens zeigt (in mm)."""
        o = self.rand_optionen
        self.abstand_mm = sum(o["abstand"]) / 4 / 72 * 25.4 if o["messen"] == "seitenrand" else 6.0

    def _optionen(self) -> None:
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
        if self.seitenrand:                              # Rahmen um die Seite: Abstand, Gemessen von, Optionen
            d = _SeitenOptionenDialog(self, self.rand_optionen, self.linie_wert())

            def fertig_seite() -> None:
                self.rand_optionen = d.werte()
                self._abstand_vorschau()
                self._neu()
            zeige_unter(self, d, fertig_seite)
            return
        d = _PolsterDialog(self, self.polster, self.linie_wert())      # Absatzrahmen: Abstand zum Text auf allen vier Seiten

        def fertig_absatz() -> None:
            self.polster = d.werte()
            self._neu()
        zeige_unter(self, d, fertig_absatz)
