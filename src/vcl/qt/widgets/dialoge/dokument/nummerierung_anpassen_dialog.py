"""Nummerierung anpassen dialog: aus ``vcl.qt.widgets.dialoge.dokument.liste_dialog`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QDialog, QLabel
from core.listen.aufzaehlungen import listen as L
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import VorschauFlaeche, fussleiste
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_LISTENVORSCHAU, GROESSE_FENSTER_NUMMERIERUNG_ANPASSEN
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_LISTE_ZAHL_PX, STIFT_STARK
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import gruppe
from vcl.qt.widgets.dialoge.dokument.liste_dialog_hilfen import _Zahlenformat
from vcl.qt.widgets.dialoge.dokument.positionen import _Positionen


PLATZHALTER = "①"


class NummerierungAnpassenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, spec: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nummerierung anpassen"); self.resize(*GROESSE_FENSTER_NUMMERIERUNG_ANPASSEN)
        s = L.liste("dezimal") if not spec or L.STILE[spec["stil"]][1] else spec
        v = _spalte("standard", self)
        self.zf = _Zahlenformat(f"{PLATZHALTER} steht für die Nummer; davor und danach darf Text stehen")
        self.format, self.art, self.start, self.schrift = self.zf.format, self.zf.art, self.zf.start, self.zf.schrift
        v.addWidget(self.zf)
        vg = gruppe("Vorschau"); vh = _reihe("standard", vg)
        self.vorschau = VorschauFlaeche(self._male, 190); self.vorschau.setFixedWidth(BREITE_LISTENVORSCHAU) # schmal und in der Mitte, wie in der Vorlage
        vh.addStretch(1); vh.addWidget(self.vorschau); vh.addStretch(1)
        v.addWidget(vg)
        self.hinweis = QLabel(); eigenschaft(self.hinweis, rolle="warnung"); v.addWidget(self.hinweis)
        self.mehr = knopf("standard", "Erweitern", umschaltbar=True); self.mehr.toggled.connect(self._erweitern)
        self.ok = fussleiste(self, v, self.mehr)
        self.position = _Positionen(); v.addWidget(self.position); self.position.setVisible(False)
        pos = s.get("pos") or {}
        self.position.setze(pos.get("ausr", 0.0), pos.get("ausr_art", "links"), pos.get("tab", pos.get("einzug", 8.0)), pos.get("einzug", 8.0))
        self._pos_geaendert = bool(pos)
        self.zf.setze(s["praefix"] + PLATZHALTER + s["suffix"], s["stil"], s["start"], s.get("zeichen"))
        self.zf.geaendert.connect(self._neu)
        self.position.geaendert.connect(self._pos_neu)
        self._neu()

    def _erweitern(self, an: bool) -> None:
        self.mehr.setText("Reduzieren" if an else "Erweitern"); self.position.setVisible(an)
        self.adjustSize()

    def _pos_neu(self) -> None:
        self._pos_geaendert = True
        self._neu()

    def spec(self) -> dict | None:
        t = self.format.text()
        if t.count(PLATZHALTER) != 1:
            return None
        a, b = t.split(PLATZHALTER)
        return L.liste(self.art.currentData(), a, b, self.start.value(), self._zeichen, self.position.werte() if self._pos_geaendert else None)

    @property
    def _zeichen(self) -> dict:
        return self.zf.zeichen

    @_zeichen.setter
    def _zeichen(self, w: dict) -> None:
        self.zf.zeichen = w

    def _neu(self) -> None:
        ok = self.spec() is not None
        self.hinweis.setText("" if ok else f"Das Zahlenformat braucht genau ein {PLATZHALTER} für die Nummer.")
        self.ok.setEnabled(ok)
        self.vorschau.update()

    def _male(self, p, rect) -> None:
        """Vorschau wie in der Vorlage: oben und unten graue Balken, dazwischen drei Nummern mit je zwei schwarzen Zeilen."""
        s = self.spec()
        r = QRectF(rect)
        grau, schwarz = QPen(QColor(Farbe.GRAU_HELL), STIFT_STARK), QPen(QColor(Farbe.SCHWARZ), STIFT_STARK)
        for y in (r.top() + 6, r.top() + 20):
            p.setPen(grau); p.drawLine(int(r.left() + 4), int(y), int(r.right() - 4), int(y))
        if s:
            marken = L.marke({**s, "start": 1}).split("|") if L.marke({**s, "start": 1}) else ["", "", ""]
            f = p.font(); f.setPixelSize(SCHRIFT_LISTE_ZAHL_PX); p.setFont(f)
            y = r.top() + 50
            for t in marken[:3]:
                p.setPen(QColor(Farbe.TINTE_DUNKEL)); p.drawText(QRectF(r.left() + 6, y - 9, 36, 18), Qt.AlignVCenter | Qt.AlignLeft, t)
                p.setPen(schwarz)
                p.drawLine(int(r.left() + 44), int(y), int(r.right() - 6), int(y))
                p.drawLine(int(r.left() + 6), int(y + 16), int(r.right() - 6), int(y + 16))
                y += 38
        for y in (r.bottom() - 20, r.bottom() - 6):
            p.setPen(grau); p.drawLine(int(r.left() + 4), int(y), int(r.right() - 4), int(y))
