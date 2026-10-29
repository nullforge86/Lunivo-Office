"""Die Popups für ein markiertes Bild oder eine Form: Formstile, Füllung, Kontur (wie in der Vorlage).

    FuellMenue()    → gewaehlt(QColor | None), verlauf_gewaehlt(QColor), muster_gewaehlt(str)
    KonturMenue()   → gewaehlt(QColor | None), breite_gewaehlt(float pt), strich_gewaehlt(str), weitere_linien()
    formstile()     → RasterAuswahl mit 6 × 7 Stilen (Raster aus editor/formen_stile.py); gewaehlt(Schlüssel); ``formstil_werte(schluessel)`` übersetzt in Füllung und Kontur

Die Menüs bauen auf den vorhandenen Bausteinen auf (``FarbPalette``, ``RasterAuswahl``, ``Linie``, ``muster``) und ändern nichts am Objekt:
sie melden die Wahl, ``editor/bildlayout.py`` schreibt sie ins Bild.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QMenu

from lunivo_writer.editor import muster as M
from lunivo_writer.editor.linie import LINIENBREITEN, Linie
from lunivo_writer.ui.baukasten.farbpalette import FarbPalette
from lunivo_writer.ui.baukasten.linien import linien_menue_zeile, linien_symbol
from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl

from lunivo_writer.editor.linie import OBJEKT_STRICHE as STRICHARTEN                        # die eine Liste der Strichlinien (editor/linie.py)
from lunivo_writer.core.farben import Farbe


def _linien_symbol(art: str, breite: float, groesse: QSize = QSize(120, 16)) -> QIcon:
    return linien_symbol(art, groesse, Farbe.TINTE, breite)                # der vorhandene Baustein


def _textur(name: str, groesse: int = 26) -> QPixmap:
    """Eine kleine, selbst gezeichnete Textur (Vorschau und Füllung): ``papier``, ``granit``, ``holz``, ``stoff``, ``marmor``, ``sand``."""
    import random
    rnd = random.Random(name)
    pm = QPixmap(groesse, groesse)
    basis = {"papier": QColor("#f1ead8"), "granit": QColor("#9a9a9a"), "holz": QColor("#c8955a"), "stoff": QColor("#8aa4c8"),
             "marmor": QColor("#e6e6ea"), "sand": QColor("#e3cf9f")}[name]
    pm.fill(basis)
    p = QPainter(pm)
    for _ in range(groesse * 3):
        x, y = rnd.randrange(groesse), rnd.randrange(groesse)
        d = rnd.randint(-28, 28)
        p.setPen(QColor(max(0, min(255, basis.red() + d)), max(0, min(255, basis.green() + d)), max(0, min(255, basis.blue() + d))))
        if name == "holz":
            p.drawLine(0, y, groesse, y + rnd.randint(-1, 1))
        elif name == "stoff":
            p.drawLine(x, 0, x, groesse); p.drawLine(0, y, groesse, y)
        else:
            p.drawPoint(x, y)
    p.end()
    return pm


TEXTUREN = [("papier", "Papier"), ("granit", "Granit"), ("holz", "Holz"), ("stoff", "Stoff"), ("marmor", "Marmor"), ("sand", "Sand")]
GRADUELL = [("#e03131", "#ffc9c9"), ("#f08c00", "#ffe8cc"), ("#f2c200", "#fff3bf"), (Farbe.GRUEN, "#d3f9d8"), ("#1971c2", "#d0ebff"), ("#7048e8", "#e5dbff"),
            (Farbe.TINTE_DUNKEL, "#dee2e6"), (Farbe.GRAU, "#f8f9fa")]


def graduell_pixmap(dunkel: str, hell: str, w: int = 34, h: int = 24) -> QPixmap:
    from PySide6.QtGui import QLinearGradient
    pm = QPixmap(w, h); p = QPainter(pm)
    g = QLinearGradient(0, 0, 0, h); g.setColorAt(0, QColor(hell)); g.setColorAt(1, QColor(dunkel))
    p.fillRect(pm.rect(), g); p.end()
    return pm


class FuellMenue(FarbPalette):
    """Füllung wie in der Vorlage: Keine Farbe · Thema-Farben · Standard-Farben · Farbverlauf · Automatisch · Weitere Füllfarben · Pipette ·
    Graduell · Textur · Muster · Bild."""
    muster_gewaehlt = Signal(str)
    graduell_gewaehlt = Signal(str, str)        # dunkle, helle Farbe
    textur_gewaehlt = Signal(str)
    bild_gewaehlt = Signal()
    weitere_fuellung = Signal(str)              # „verlauf“, „textur“, „muster“: die Seitenleiste „Formatierung“ mit dieser Füllungsart öffnen

    def __init__(self, parent=None, start=None):
        super().__init__(parent, keine_text="Keine Farbe", start=start, titel="Füllfarbe", verlauf=True, verlauf_titel="Farbverlauf",
                         weitere_text="Weitere Füllfarben(M)…", automatisch="Automatisch", zuletzt=False)
        self.addSeparator()
        self._raster_untermenue("Graduell", "verlauf", "Weitere Farbverläufe…", [
            (f"{d}|{h}", "Graduell", graduell_pixmap(d, h)) for d, h in GRADUELL], QSize(34, 24), 4,
            lambda k: self.graduell_gewaehlt.emit(*k.split("|")))
        self._raster_untermenue("Textur", "textur", "Weitere Texturen…", [(k, n, _textur(k, 30)) for k, n in TEXTUREN], QSize(30, 30), 6,
                                self.textur_gewaehlt.emit)
        muster = [(k, n, M.kachel(k, Farbe.TINTE, Farbe.WEISS).scaled(30, 30)) for k, n, _o in M.MUSTER if k != "loeschen"]
        self._raster_untermenue("Muster(N)", "muster", "Weitere Muster…", muster, QSize(30, 30), 8, self.muster_gewaehlt.emit)
        self.addAction("Bild(P)").triggered.connect(lambda: (self.close(), self.bild_gewaehlt.emit()))

    def _raster_untermenue(self, text: str, art: str, weitere: str, kacheln: list, groesse: QSize, spalten: int, gewaehlt) -> RasterAuswahl:
        """Ein Untermenü mit Kacheln (Graduell, Textur, Muster) und darunter „Weitere …“, das die Seitenleiste „Formatierung“ öffnet."""
        r = RasterAuswahl(self, spalten=spalten, groesse=groesse)
        for schl, name, bild in kacheln:
            r.kachel(schl, name, bild)
        r.gewaehlt.connect(lambda k: (self.close(), gewaehlt(k)))
        r.fuss(weitere, lambda: (self.close(), self.weitere_fuellung.emit(art)))
        self.addAction(text).setMenu(r)
        return r

    def _untermenue(self, text: str, icon: str) -> QMenu:
        m = self.addMenu(text)
        return m

    @staticmethod
    def _einsetzen(menue: QMenu, inhalt: RasterAuswahl) -> None:
        """Das Raster steht als Inhalt des Untermenüs."""
        from PySide6.QtWidgets import QWidgetAction
        a = QWidgetAction(menue); a.setDefaultWidget(inhalt._wid); menue.addAction(a)


class KonturMenue(FarbPalette):
    """Kontur wie in der Vorlage: Keine Linie · Thema-Farben · Standard-Farben · Farbverlauf · Weitere Linienfarben · Pipette · Linienart ▸ · Strichart ▸ · Pfeilart ▸."""
    breite_gewaehlt = Signal(float)
    strich_gewaehlt = Signal(str)
    weitere_linien = Signal()

    def __init__(self, parent=None, start=None):
        super().__init__(parent, keine_text="Keine Linie", start=start, titel="Linienfarbe", verlauf=True, verlauf_titel="Farbverlauf",
                         weitere_text="Weitere Linienfarben(M)…", zuletzt=False)
        self.verlauf_gewaehlt.connect(self.gewaehlt)               # in der Kontur ist der „Farbverlauf“ eine Reihe Farben
        self.addSeparator()
        art = self.addMenu("Linienart(W)")
        for b in LINIENBREITEN:                                    # „0,25 pt.“ und die Linie in dieser Stärke, wie in der Vorlage
            linien_menue_zeile(art, f"{b:g}".replace(".", ",") + " pt.", "einfach", b, lambda b=b: self.breite_gewaehlt.emit(b))
        art.addSeparator()
        art.addAction("Weitere Linien(M)…", self.weitere_linien.emit)
        strich = self.addMenu("Strichart")
        for schl, _name in STRICHARTEN:                            # nur die Linie in ihrer Art, ohne Text — alle Strichlinien des Bausteins ``Linie``
            linien_menue_zeile(strich, "", schl, 1.5, lambda s=schl: self.strich_gewaehlt.emit(s))
        pfeil = self.addMenu("Pfeilart"); pfeil.setEnabled(False)                # wie in der Vorlage: nur für Linien und Pfeile, nicht für Bilder


# ---- Formstile (das eine Raster: editor/formen_stile.py, 6 Zeilen × 7 Spalten) -----------------------------------------------------------
def formstil_werte(schluessel: str) -> dict:
    """Füllung und Kontur des Stils ``z{Zeile}{Spalte}`` für Bilder und Textfelder: {"fuell": …, "rand": …} (``None`` = keine). Die Werte kommen aus
    ``formen_stile.formstil`` (dasselbe Raster wie ``formStilRaster`` bei Formen); Effekte (3D) und Glanz gelten nur bei Formen."""
    from lunivo_writer.editor import formen_stile as S
    w = S.formstil(int(schluessel[1]), int(schluessel[2]))
    fuell = None
    if w["fuell"]:
        fuell = {"art": "verlauf" if w["fuell_art"] in ("verlauf", "glanz") else "farbe", "farbe": w["fuell"]}
    return {"fuell": fuell, "rand": {"b": w["strich"] * 96 / 72, "farbe": w["linie"], "art": "einfach"}}


def formstil_zeichner(schluessel: str):
    """Zeichnet die Kachel „Abc“ des Stils: Füllung (auch Verlauf), Rand und Schrift in passender Farbe."""
    from lunivo_writer.editor import formen_stile as S

    def zeichne(p: QPainter, r: QRectF) -> None:
        w = S.formstil(int(schluessel[1]), int(schluessel[2]))
        kachel = r.adjusted(2, 2, -2, -2)
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        if w["fuell"]:
            c = QColor(w["fuell"])
            if w["fuell_art"]:
                from PySide6.QtGui import QLinearGradient
                g = QLinearGradient(kachel.topLeft(), kachel.bottomLeft()); g.setColorAt(0, c.lighter(135)); g.setColorAt(1, c.darker(115) if w["fuell_art"] != "abgestuft" else c)
                p.setBrush(g)
            else:
                p.setBrush(c)
        else:
            p.setBrush(QColor("white"))
        p.setPen(QPen(QColor(w["linie"]), min(2.5, max(1.0, w["strich"] * 0.6))))
        p.drawRoundedRect(kachel, 5, 5)
        hell = not w["fuell"] or QColor(w["fuell"]).lightness() > 150
        p.setPen(QColor(Farbe.TINTE_DUNKEL) if hell else QColor("white")); p.drawText(kachel, Qt.AlignCenter, "Abc")
        p.restore()
    return zeichne


def formstile(parent=None) -> RasterAuswahl:
    """Das Popup „Formstile“: sechs Zeilen zu sieben Stilen; ``gewaehlt`` meldet ``z{Zeile}{Spalte}`` (Namen im Tipp). Darunter steht „Weitere Effekte …“."""
    from lunivo_writer.editor import formen_stile as S
    m = RasterAuswahl(parent, spalten=len(S.SPALTEN), groesse=QSize(46, 32))
    for z in range(len(S.ZEILEN)):
        for s in range(len(S.SPALTEN)):
            m.kachel(f"z{z}{s}", f"{S.ZEILEN[z]} – {S.SPALTEN[s][0]}", formstil_zeichner(f"z{z}{s}"))
    return m
