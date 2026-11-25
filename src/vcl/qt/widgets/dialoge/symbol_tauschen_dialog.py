"""Symbol tauschen dialog: aus ``vcl.qt.widgets.dialoge.oberflaeche_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf, werkzeugknopf
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
import json
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QScrollArea, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from writer.werkzeugleisten.plan import plan
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_UEBERSCHRIFT_PLUS_PT
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_KNOPF_KACHEL, GROESSE_SYMBOL_JETZT, HOEHE_LISTE_MITTEL, ICON_KACHEL, ICON_KNOPF_GROSS, RAND_BOX, RAND_GITTER
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.eigene_zeichnung_dialog import EigeneZeichnungDialog
from vcl.qt.widgets.dialoge.oberflaeche_dialoge_hilfen import _satz, lade_json


class SymbolTauschenDialog(PanelFaehig, QDialog):
    """Ein Symbol austauschen — wie in der ersten Fassung: Getauscht wird die Zeichnung, nicht der Knopf; sie ändert sich überall,
    wo sie benutzt wird. Oben steht, wo das ist. Dazu Suche, 1800 Zeichnungen, eigene Zeichnung und Zurücksetzen."""
    GRENZE = 240

    def __init__(self, parent, settings, name: str | None = None):
        super().__init__(parent)
        self.w, self.settings = parent, settings
        self.setWindowTitle("Symbol austauschen")
        self.tausch = lade_json(settings, "ui/symbol_tausch", {})
        self._anfang = dict(self.tausch)
        self.geaendert = False
        namen = symbole.pfade_original()
        self.welches = name if name in namen else next(iter(namen))
        v = _spalte("standard", self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        t = QLabel("Symbol austauschen"); f = t.font(); f.setBold(True); f.setPointSizeF(f.pointSizeF() + SCHRIFT_UEBERSCHRIFT_PLUS_PT); t.setFont(f)
        g.breit(t)
        g.breit(_satz("Getauscht wird die Zeichnung, nicht der Knopf — sie ändert sich überall, wo sie benutzt wird. Oben steht, wo das ist.", True))
        kopf = rahmen_baustein("flach", name="tauschKopf")
        eigenschaft(kopf, rolle="rahmen")
        kh = FormularGitter(kopf); kh.setContentsMargins(*RAND_BOX)           # Symbol, darunter der Text: bei 300 px bricht nichts ab
        self.jetzt = QLabel(); self.jetzt.setFixedSize(*GROESSE_SYMBOL_JETZT); self.jetzt.setAlignment(Qt.AlignCenter)
        self.wo = QLabel(); self.wo.setWordWrap(True)
        kh.breit(self.jetzt); kh.breit(self.wo)
        g.breit(kopf)
        self.suche = zeilenfeld("frei", name="Zeichnung suchen"); self.suche.setClearButtonEnabled(True)
        self.suche.setPlaceholderText("Zeichnung suchen … (englisch: table, clock, save)")
        g.breit(self.suche)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sc.setMinimumHeight(HOEHE_LISTE_MITTEL)
        self.gitter_halter = QWidget(); self.gitter = FlussLayout(4)                  # so viele Zeichnungen je Zeile, wie in die Breite passen
        self.gitter.setContentsMargins(*RAND_GITTER); self.gitter_halter.setLayout(self.gitter)
        sc.setWidget(self.gitter_halter)
        g.breit(sc)
        self.treffer = QLabel(); self.treffer.setWordWrap(True); hinweis_stil(self.treffer); g.breit(self.treffer)
        fuss = FlussLayout(6)
        self.b_eigene = knopf("standard", "Eigene Zeichnung …"); self.b_dieses = knopf("standard", "Dieses zurücksetzen"); self.b_alle = knopf("standard", "Alle zurücksetzen")
        for b in (self.b_eigene, self.b_dieses, self.b_alle):
            fuss.addWidget(b)
        g.breit(fuss)
        self.meldung = QLabel(); hinweis_stil(self.meldung); self.meldung.setWordWrap(True); g.breit(self.meldung)
        v.addWidget(inhalt)
        fussleiste(self, v, ok_text="Fertig")
        self.suche.textChanged.connect(self._gitter_zeigen)
        self.b_eigene.clicked.connect(self._eigene)
        self.b_dieses.clicked.connect(self._dieses_zurueck)
        self.b_alle.clicked.connect(self._alle_zurueck)
        self._kopf_zeigen()
        self._gitter_zeigen()

    # ---- Kopf: welches Symbol, und wo es steht --------------------------------------------------------------------
    def _befehle(self) -> list[str]:
        namen: list[str] = []
        try:
            for r in plan(self.w.band.daten):
                for g in r.get("gruppen", []):
                    for k in g.get("knoepfe", []):
                        if k.get("symbol") == self.welches and k.get("name") and k["name"] not in namen:
                            namen.append(k["name"])
        except Exception:
            pass
        return namen

    def _kopf_zeigen(self) -> None:
        self.jetzt.setPixmap(symbole.icon(self.welches, ICON_KACHEL).pixmap(ICON_KACHEL, ICON_KACHEL))
        b = self._befehle()
        self.wo.setText((", ".join(b[:4]) + (" und weitere" if len(b) > 4 else "")) if b else "Wird zurzeit nirgends im Register benutzt.")
        self.b_dieses.setEnabled(self.welches in self.tausch)

    # ---- Auswahl --------------------------------------------------------------------------------------------------
    def _gitter_zeigen(self) -> None:
        while self.gitter.count():
            it = self.gitter.takeAt(0)
            w = it.widget()
            if w is not None:
                w.hide(); w.setParent(None); w.deleteLater()
        wort = self.suche.text().strip().lower()
        gezeigt = gefunden = 0
        farbe = self.palette().color(self.foregroundRole()).name()
        for n, pfad in symbole.katalog().items():
            if wort and wort not in n.lower():
                continue
            gefunden += 1
            if gezeigt >= self.GRENZE:
                continue
            k = werkzeugknopf("fest", groesse=GROESSE_KNOPF_KACHEL, tooltip=n)
            k.setIcon(QIcon(QPixmap.fromImage(symbole.pfad_bild(pfad, 56, farbe)))); k.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
            k.clicked.connect(lambda _=False, n=n: self._waehle(n))
            self.gitter.addWidget(k)
            gezeigt += 1
        self.treffer.setText("Keine Zeichnung mit diesem Namen." if not gefunden else
                             f"{gefunden} gefunden, {self.GRENZE} gezeigt — die Suche genauer machen." if gefunden > self.GRENZE else "")
        self.treffer.setVisible(bool(self.treffer.text()))
        self.gitter.invalidate()

    # ---- Wirkung --------------------------------------------------------------------------------------------------
    def _anwenden(self, meldung: str) -> None:
        self.settings.set("ui/symbol_tausch", json.dumps(self.tausch))
        symbole.uebersteuern(self.tausch)
        self.geaendert = True
        self._kopf_zeigen()
        self.meldung.setText(meldung)

    def _waehle(self, katalogname: str) -> None:
        self.tausch[self.welches] = katalogname
        self._anwenden(f"Symbol getauscht: {katalogname}.")

    def _eigene(self) -> None:
        d = EigeneZeichnungDialog(self)
        if d.exec() and d.wert:
            self.tausch[self.welches] = d.wert
            self._anwenden("Eigene Zeichnung übernommen.")

    def _dieses_zurueck(self) -> None:
        self.tausch.pop(self.welches, None)
        self._anwenden("Zurückgesetzt.")

    def _alle_zurueck(self) -> None:
        self.tausch = {}
        self._anwenden("Alle Symbole wieder wie ausgeliefert.")

    def reject(self) -> None:
        """Abbrechen (auch Esc und ✕) nimmt zurück, was in diesem Fenster getauscht wurde."""
        if self.tausch != self._anfang:
            self.tausch = dict(self._anfang)
            self.settings.set("ui/symbol_tausch", json.dumps(self.tausch))
            symbole.uebersteuern(self.tausch)
            self.geaendert = True
        super().reject()
