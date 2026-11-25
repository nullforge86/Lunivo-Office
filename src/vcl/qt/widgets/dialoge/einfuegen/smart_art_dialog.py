"""Smart art dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QLabel, QPlainTextEdit, QSizePolicy, QWidget
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_MINIATUR_LAYOUT, HOEHE_EINGABE_TEXT
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge_hilfen import VorschauMixin, _ok
from vcl.qt.widgets.dialoge.einfuegen.layout_galerie import _LayoutGalerie


class SmartArtDialog(PanelFaehig, QDialog, VorschauMixin):
    """SmartArt auswählen (wie in der Vorlage „Grafik auswählen“): Galerie der Layouts, darunter Name, Beschreibung und Vorschau, OK.
    Beim Bearbeiten (``daten`` gegeben) kommen Farben und der eingerückte Text (zwei Leerzeichen = eine Ebene tiefer) dazu."""
    BESCHREIBUNG = {
        "Spalten": "Zeigt Gruppen mit ihren Unterpunkten nebeneinander in Spalten.",
        "Gruppen": "Fasst zusammengehörige Punkte in umrahmten Gruppen zusammen.",
        "Matrix": "Zeigt vier Teile in einem Quadrat, etwa für eine Stärken-Schwächen-Analyse.",
        "Chevron": "Zeigt einen Ablauf als Reihe von Pfeilen, die nach rechts weisen.",
        "Radial": "Zeigt Beziehungen zu einem zentralen Kern, um den die übrigen Punkte angeordnet sind.",
        "Zielscheibe": "Zeigt Ebenen, die sich wie Ringe um ein Ziel in der Mitte legen.",
        "Trichter": "Zeigt, wie sich Mengen in Stufen verringern, etwa vom Interesse zum Auftrag.",
        "Zeitachse": "Zeigt Ereignisse oder Zeitpunkte entlang einer Linie.",
        "Stufen": "Zeigt Schritte, die treppenartig aufeinander aufbauen.",
        "Liste": "Zeigt nicht aufeinanderfolgende Informationen oder Gruppen von Informationen untereinander. Eingerückte Zeilen bilden Unterpunkte.",
        "Prozess": "Zeigt die Schritte eines Ablaufs oder einer Zeitachse nacheinander, durch Pfeile verbunden.",
        "Hierarchie": "Stellt hierarchische Informationen oder Berichtsbeziehungen dar, etwa den Aufbau einer Organisation. Eingerückte Zeilen sind untergeordnet.",
        "Zyklus": "Zeigt einen fortlaufenden Prozess, dessen Schritte im Kreis wieder von vorn beginnen.",
        "Pyramide": "Zeigt Beziehungen, die nach oben schmaler werden, etwa Grundlagen unten und Spitze oben.",
    }

    def __init__(self, parent, daten: dict | None = None):
        super().__init__(parent)
        from vcl.qt.rendering import smartart as SA
        self.SA = SA
        from writer.funktionen.objekte import smartart as SW
        self.SW = SW
        self.setWindowTitle("SmartArt-Grafik auswählen")
        v = _spalte("standard", self)
        bearbeiten = bool(daten)
        self._bearbeiten = bearbeiten
        daten = daten or {}
        start = daten.get("layout", SW.katalog().standard_layout)
        self.galerie = _LayoutGalerie([e.schluessel for e in SW.katalog().galerie], _layout_bildchen, start)
        v.addWidget(abschnittstitel("Layout")); v.addWidget(self.galerie)
        self.name = QLabel(); eigenschaft(self.name, rolle="fett")
        self.beschreibung = QLabel(); self.beschreibung.setWordWrap(True)
        self.beschreibung.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        v.addWidget(self.name); v.addWidget(self.beschreibung)
        self._vorschau_bauen(v)
        self.farben = Auswahlfeld(); self.farben.addItems(list(SW.katalog().farben))
        self.farben.setCurrentText(daten.get("farben", "Blau"))
        self.text = QPlainTextEdit(daten.get("text") or SW.katalog().muster[start])
        self.text.setMinimumHeight(HOEHE_EINGABE_TEXT)
        self.bearbeiten = QWidget()
        f = FormularGitter(); b = _spalte("standard", self.bearbeiten); b.addLayout(f)
        f.zeile("Farben", self.farben)
        f.breit(QLabel("Text (eine Zeile je Punkt)")); f.breit(self.text)
        v.addWidget(self.bearbeiten); self.bearbeiten.setVisible(bearbeiten)
        v.addStretch(1)
        v.addWidget(_ok(self))
        self.galerie.gewaehlt.connect(self._layout)
        self.farben.currentTextChanged.connect(self.aktualisieren)
        self.text.textChanged.connect(self.aktualisieren)
        self._eigener_text = bool(daten.get("text"))
        self.aktualisieren()

    @property
    def layout_(self):
        return self.galerie

    def _layout(self, name):
        if not self._eigener_text or self.text.toPlainText() in self.SW.katalog().muster.values():
            self.text.blockSignals(True); self.text.setPlainText(self.SW.katalog().muster.get(name, "")); self.text.blockSignals(False)
        self.aktualisieren()

    def daten(self):
        return {"layout": self.galerie.aktuell(), "farben": self.farben.currentText(), "text": self.text.toPlainText()}

    def aktualisieren(self, *_):
        d = self.daten()
        self.name.setText(self.SW.katalog().anzeigenamen.get(d["layout"], d["layout"]))
        self.beschreibung.setText(self.SW.katalog().beschreibungen.get(d["layout"]) or self.BESCHREIBUNG.get(d["layout"], ""))
        if self._bearbeiten:                                           # beim Bearbeiten: die echte Zeichnung mit Text und Farben
            self._zeige(self.SA.zeichnen(d))
        else:                                                          # beim Einfügen: die Miniatur des Layouts, größer und blau
            from vcl.qt.widgets.menues.dropdown.objektmenues.smartart_menues import miniatur
            self._zeige(miniatur(d["layout"], False, QSize(*GROESSE_MINIATUR_LAYOUT)).toImage())


def _layout_bildchen(p, r, name: str) -> None:
    """Graue Miniatur eines SmartArt-Layouts (selbst gezeichnet, ``oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py``)."""
    from vcl.qt.widgets.menues.dropdown.objektmenues.smartart_menues import zeichne_miniatur
    zeichne_miniatur(p, r.adjusted(3, 3, -3, -3), name, True)


class SmartArtDialog(PanelFaehig, QDialog, VorschauMixin):
    """SmartArt auswählen (wie in der Vorlage „Grafik auswählen“): Galerie der Layouts, darunter Name, Beschreibung und Vorschau, OK.
    Beim Bearbeiten (``daten`` gegeben) kommen Farben und der eingerückte Text (zwei Leerzeichen = eine Ebene tiefer) dazu."""
    BESCHREIBUNG = {
        "Spalten": "Zeigt Gruppen mit ihren Unterpunkten nebeneinander in Spalten.",
        "Gruppen": "Fasst zusammengehörige Punkte in umrahmten Gruppen zusammen.",
        "Matrix": "Zeigt vier Teile in einem Quadrat, etwa für eine Stärken-Schwächen-Analyse.",
        "Chevron": "Zeigt einen Ablauf als Reihe von Pfeilen, die nach rechts weisen.",
        "Radial": "Zeigt Beziehungen zu einem zentralen Kern, um den die übrigen Punkte angeordnet sind.",
        "Zielscheibe": "Zeigt Ebenen, die sich wie Ringe um ein Ziel in der Mitte legen.",
        "Trichter": "Zeigt, wie sich Mengen in Stufen verringern, etwa vom Interesse zum Auftrag.",
        "Zeitachse": "Zeigt Ereignisse oder Zeitpunkte entlang einer Linie.",
        "Stufen": "Zeigt Schritte, die treppenartig aufeinander aufbauen.",
        "Liste": "Zeigt nicht aufeinanderfolgende Informationen oder Gruppen von Informationen untereinander. Eingerückte Zeilen bilden Unterpunkte.",
        "Prozess": "Zeigt die Schritte eines Ablaufs oder einer Zeitachse nacheinander, durch Pfeile verbunden.",
        "Hierarchie": "Stellt hierarchische Informationen oder Berichtsbeziehungen dar, etwa den Aufbau einer Organisation. Eingerückte Zeilen sind untergeordnet.",
        "Zyklus": "Zeigt einen fortlaufenden Prozess, dessen Schritte im Kreis wieder von vorn beginnen.",
        "Pyramide": "Zeigt Beziehungen, die nach oben schmaler werden, etwa Grundlagen unten und Spitze oben.",
    }

    def __init__(self, parent, daten: dict | None = None):
        super().__init__(parent)
        from vcl.qt.rendering import smartart as SA
        self.SA = SA
        from writer.funktionen.objekte import smartart as SW
        self.SW = SW
        self.setWindowTitle("SmartArt-Grafik auswählen")
        v = _spalte("standard", self)
        bearbeiten = bool(daten)
        self._bearbeiten = bearbeiten
        daten = daten or {}
        start = daten.get("layout", SW.katalog().standard_layout)
        self.galerie = _LayoutGalerie([e.schluessel for e in SW.katalog().galerie], _layout_bildchen, start)
        v.addWidget(abschnittstitel("Layout")); v.addWidget(self.galerie)
        self.name = QLabel(); eigenschaft(self.name, rolle="fett")
        self.beschreibung = QLabel(); self.beschreibung.setWordWrap(True)
        self.beschreibung.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        v.addWidget(self.name); v.addWidget(self.beschreibung)
        self._vorschau_bauen(v)
        self.farben = Auswahlfeld(); self.farben.addItems(list(SW.katalog().farben))
        self.farben.setCurrentText(daten.get("farben", "Blau"))
        self.text = QPlainTextEdit(daten.get("text") or SW.katalog().muster[start])
        self.text.setMinimumHeight(HOEHE_EINGABE_TEXT)
        self.bearbeiten = QWidget()
        f = FormularGitter(); b = _spalte("standard", self.bearbeiten); b.addLayout(f)
        f.zeile("Farben", self.farben)
        f.breit(QLabel("Text (eine Zeile je Punkt)")); f.breit(self.text)
        v.addWidget(self.bearbeiten); self.bearbeiten.setVisible(bearbeiten)
        v.addStretch(1)
        v.addWidget(_ok(self))
        self.galerie.gewaehlt.connect(self._layout)
        self.farben.currentTextChanged.connect(self.aktualisieren)
        self.text.textChanged.connect(self.aktualisieren)
        self._eigener_text = bool(daten.get("text"))
        self.aktualisieren()

    @property
    def layout_(self):
        return self.galerie

    def _layout(self, name):
        if not self._eigener_text or self.text.toPlainText() in self.SW.katalog().muster.values():
            self.text.blockSignals(True); self.text.setPlainText(self.SW.katalog().muster.get(name, "")); self.text.blockSignals(False)
        self.aktualisieren()

    def daten(self):
        return {"layout": self.galerie.aktuell(), "farben": self.farben.currentText(), "text": self.text.toPlainText()}

    def aktualisieren(self, *_):
        d = self.daten()
        self.name.setText(self.SW.katalog().anzeigenamen.get(d["layout"], d["layout"]))
        self.beschreibung.setText(self.SW.katalog().beschreibungen.get(d["layout"]) or self.BESCHREIBUNG.get(d["layout"], ""))
        if self._bearbeiten:                                           # beim Bearbeiten: die echte Zeichnung mit Text und Farben
            self._zeige(self.SA.zeichnen(d))
        else:                                                          # beim Einfügen: die Miniatur des Layouts, größer und blau
            from vcl.qt.widgets.menues.dropdown.objektmenues.smartart_menues import miniatur
            self._zeige(miniatur(d["layout"], False, QSize(*GROESSE_MINIATUR_LAYOUT)).toImage())
