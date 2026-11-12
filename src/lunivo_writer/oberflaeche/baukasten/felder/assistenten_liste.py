"""Die Liste der Assistenten (Schnelle KI-Aktionen und fortlaufende Assistenten) mit Hauptschalter — EIN Baustein für KI-Einstellungen und Optionen.

    AssistentenListe(fenster)      # liest ``fenster.ki.konfig``, schaltet über ``fenster.ki`` (``assistent_an_setzen``, ``dauerbetrieb_setzen``),
                                   # legt über die Befehle ``w.kiAssistentErstellen`` / ``w.schnelleAktionErstellen`` an; folgt ``ki.geaendert``
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, UmbruchSchalter, abschnittstitel
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_NORMAL, RAND_KEIN, RAND_ZEILE
from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil

ART_TEXTE = {"aktion": "Aktion", "fortlaufend": "Fortlaufend"}
TEXT_DAUERBETRIEB = "Fortlaufende Assistenten einschalten"
TEXT_DATENSCHUTZ = ("Fortlaufende Assistenten senden den geänderten Absatz automatisch an das gewählte KI-Modell. Bei einem Anbieter im Internet "
                    "verlässt der Text dabei den Rechner und es können Kosten entstehen. Lokale Modelle (Ollama) kosten nichts und bleiben auf diesem Rechner.")
TEXT_LEER = "Noch keiner angelegt."


class AssistentenListe(QWidget):
    def __init__(self, fenster, parent=None):
        super().__init__(parent)
        self.fenster = fenster
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_NORMAL)
        self.haupt = UmbruchSchalter(TEXT_DAUERBETRIEB)
        self.haupt.clicked.connect(self._haupt_geklickt)
        v.addWidget(self.haupt)
        info = QLabel(TEXT_DATENSCHUTZ); info.setWordWrap(True); hinweis_stil(info)
        v.addWidget(info)
        v.addWidget(abschnittstitel("Assistenten"))
        self._zeilen = QVBoxLayout(); self._zeilen.setContentsMargins(*RAND_KEIN); self._zeilen.setSpacing(ABSTAND_NORMAL)
        v.addLayout(self._zeilen)
        knoepfe = FlussLayout()
        self.neu_assistent = QPushButton("Neuen Assistenten erstellen …")
        self.neu_aktion = QPushButton("Schnelle KI-Aktion erstellen …")
        self.neu_assistent.clicked.connect(lambda: fenster.befehle.tun("w.kiAssistentErstellen"))
        self.neu_aktion.clicked.connect(lambda: fenster.befehle.tun("w.schnelleAktionErstellen"))
        knoepfe.addWidget(self.neu_assistent); knoepfe.addWidget(self.neu_aktion)
        v.addLayout(knoepfe)
        fenster.ki.geaendert.connect(self.neu_lesen)
        self.neu_lesen()

    def _haupt_geklickt(self, an: bool) -> None:
        self.fenster.ki.dauerbetrieb_setzen(an)
        self.neu_lesen()                                                  # lehnt der Dienst ab (z. B. keine Einwilligung), zeigt der Haken den echten Stand

    def neu_lesen(self) -> None:
        ki = self.fenster.ki
        self.haupt.setChecked(ki.dauerbetrieb())
        while self._zeilen.count():
            it = self._zeilen.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None); w.deleteLater()
        liste = ki.konfig.assistenten()
        if not liste:
            self._zeilen.addWidget(QLabel(TEXT_LEER))
        for a in liste:
            z = QWidget(); h = QHBoxLayout(z); h.setContentsMargins(*RAND_ZEILE)
            art = a.get("art", "aktion")
            if art == "fortlaufend":
                an = QCheckBox(); an.setChecked(bool(a.get("an"))); an.setToolTip("Assistent einschalten")
                an.clicked.connect(lambda c, i=a["id"]: (ki.assistent_an_setzen(i, c), self.neu_lesen()))
                h.addWidget(an)
            name = QLabel(f"{a['name']}  ·  {ART_TEXTE.get(art, art)}"); name.setWordWrap(True)
            h.addWidget(name, 1)
            e = QPushButton("Entfernen")
            e.clicked.connect(lambda _=False, i=a["id"]: (ki.konfig.assistent_entfernen(i), ki.geaendert.emit()))
            h.addWidget(e, 0, Qt.AlignTop)
            self._zeilen.addWidget(z)
