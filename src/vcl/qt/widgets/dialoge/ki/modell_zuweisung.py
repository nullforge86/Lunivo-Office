"""Modell zuweisung: aus ``vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QComboBox, QLabel, QWidget
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from framework.ki.dienst import ki as K
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld


def modell_passt(m: dict, aufgabe: str) -> bool:
    """Lokale Übersetzung („argos:“) und „Automatisch“ („auto:“) gelten nur für ihre Aufgabe (``verwendungFuer``); Bildgenerierung hat ihre eigene Regel."""
    if m["id"].startswith((K.ARGOS_MARKE, K.AUTO_MARKE)) and aufgabe not in m["verwendungFuer"]:
        return False
    if aufgabe == "bildgenerierung":               # nur Anbieter mit „Bilder“ — Claude und Text-Modelle kennen das nicht
        return "bilder" in m["verwendungFuer"] and m["id"].startswith(K.EIGEN_MARKE)
    return True


def modell_felder_fuellen(combo: QComboBox, konfig: K.KIKonfig, aufgabe: str, gewaehlt: str | None = None, standard: str = "Standard (KI-Modell der Optionen)") -> None:
    """Die eine Stelle, die ein Modell-Auswahlfeld füllt (Modellzuweisung, Optionen, Chat): Eintrag „Standard“, dann alle passenden Modelle; Signale ruhen dabei."""
    combo.blockSignals(True)
    combo.clear()
    combo.addItem(standard, "")
    for m in konfig.alle_modelle():
        if modell_passt(m, aufgabe):
            combo.addItem(m["name"] + ("  · lokal" if m["lokal"] else ""), m["id"])
    g = konfig["aufgaben"].get(aufgabe, "") if gewaehlt is None else gewaehlt
    combo.setCurrentIndex(max(0, combo.findData(g)))
    combo.blockSignals(False)


def modell_combo(konfig: K.KIKonfig, aufgabe: str, gewaehlt: str | None = None) -> QComboBox:
    """Die Auswahl „welches Modell für diese Aufgabe?“ — dieselbe in der Modellzuweisung und in den erweiterten Einstellungen des Chats."""
    c = Auswahlfeld()                                                            # lange Modellnamen machen das Feld nicht breiter als die Seitenleiste
    modell_felder_fuellen(c, konfig, aufgabe, gewaehlt)
    return c


class ModellZuweisung(QWidget):
    """Je Aufgabe ein Modell: Chatbot, Zusammenfassen, Übersetzung, Textanalyse, Bildgenerierung."""

    def __init__(self, fenster):
        super().__init__()
        self.fenster = fenster
        self.k = fenster.ki.konfig
        self._v = v = _spalte("standard", self)
        hinweis = QLabel("Fügen Sie hinzu und wählen Sie KI-Modelle für verschiedene Aufgaben aus."); hinweis.setWordWrap(True)
        v.addWidget(hinweis)
        self.halter: QWidget | None = None
        self.felder: dict[str, QComboBox] = {}
        v.addStretch(1)
        self.aufbauen()

    def aufbauen(self) -> None:
        alt = {a: c.currentData() for a, c in self.felder.items()}
        if self.halter is not None:
            self._v.removeWidget(self.halter); self.halter.setParent(None); self.halter.deleteLater()
        self.felder.clear()
        self.halter = QWidget(); g = FormularGitter(self.halter)               # Beschriftung links, bei 300 px über dem Feld
        for aufgabe, name in K.AUFGABEN:
            c = modell_combo(self.k, aufgabe, alt.get(aufgabe, self.k["aufgaben"].get(aufgabe, "")))
            self.felder[aufgabe] = c
            g.zeile(name, c)
        self._v.insertWidget(1, self.halter)

    def uebernehmen(self) -> None:
        for aufgabe, c in self.felder.items():
            self.k.aufgabe_setzen(aufgabe, c.currentData() or "")
        self.fenster.ki.geaendert.emit()
