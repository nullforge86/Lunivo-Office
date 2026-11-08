"""Reglerblock für den KI-Chat: Länge, Temperatur, Top P, Stoppfolgen, „Antwort direkt einfügen“ — als zugeklappter Abschnitt in den KI-Einstellungen.

Liest und schreibt nur die KI-Konfiguration (``chat_optionen``/``chat_setzen``); der Chat liest ``direkt`` beim Antwortende aus derselben Konfiguration."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QSlider, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.basis.beschriftung import text_label
from lunivo_writer.ui.baukasten.controls.formular_gitter import FormularGitter, UmbruchSchalter
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_KLEIN, ICON_NORMAL, RAND_KEIN
from lunivo_writer.ui.widgets import icons


class ChatReglerBlock(QWidget):
    def __init__(self, konfig):
        super().__init__()
        self.k = konfig
        o = konfig.chat_optionen()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_KLEIN)
        self.mehr = QPushButton(); self.mehr.setFlat(True); self.mehr.setCursor(Qt.PointingHandCursor)
        v.addWidget(self.mehr, 0, Qt.AlignLeft)
        self.inhalt = QWidget()
        ew = QVBoxLayout(self.inhalt); ew.setContentsMargins(*RAND_KEIN); ew.setSpacing(ABSTAND_KLEIN)
        k = konfig

        def regler(titel: str, tipp: str, maximum: int, wert: int, anzeige, speichern):
            zeile = QWidget(); g = FormularGitter(zeile); g.setContentsMargins(*RAND_KEIN)
            zahl = QLabel(anzeige(wert)); zahl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            g.zeile(text_label(titel, fett=True), zahl)
            sl = QSlider(Qt.Horizontal); sl.setRange(0, maximum); sl.setValue(wert); sl.setToolTip(tipp)
            sl.valueChanged.connect(lambda w: (zahl.setText(anzeige(w)), speichern(w)))
            g.breit(sl)
            ew.addWidget(zeile)
            return sl
        self.s_laenge = regler("Maximale Länge", "0 = Vorgabe des Anbieters", 4096, int(o["maxLaenge"]),
                               lambda w: str(w) if w else "Standard", lambda w: k.chat_setzen(maxLaenge=w))
        self.s_temp = regler("Temperatur", "Niedrig = sachlich und gleichbleibend, hoch = freier. Gilt für Ollama und eigene Anbieter.", 20,
                             int(round(float(o["temperatur"]) * 10)), lambda w: f"{w / 10:g}", lambda w: k.chat_setzen(temperatur=w / 10))
        self.s_top = regler("Top P", "Wie viele der wahrscheinlichsten Wörter zur Wahl stehen. Gilt für Ollama und eigene Anbieter.", 10,
                            int(round(float(o["topP"]) * 10)), lambda w: f"{w / 10:g}", lambda w: k.chat_setzen(topP=w / 10))
        from lunivo_writer.ai import ki as _ki
        stufen = _ki.NUM_CTX_STUFEN
        self.s_alive = regler("Modell im Speicher halten", "Minuten, die Ollama das Modell nach der letzten Antwort geladen lässt. "
                              "Länger = schneller, belegt aber Arbeitsspeicher. 0 = sofort entladen.", _ki.KEEP_ALIVE_MAX,
                              _ki.keep_alive_begrenzen(o["keepAlive"]), lambda w: f"{w} min" if w else "sofort entladen",
                              lambda w: k.chat_setzen(keepAlive=w))
        self.s_ctx = regler("Kontextgröße (Ollama)", "Wie viel Gespräch und Dokument das Modell auf einmal sieht. Größer = mehr Speicher, "
                            "langsamer. Wird bei langem Verlauf automatisch erhöht.", len(stufen) - 1,
                            stufen.index(_ki.num_ctx_begrenzen(o["numCtx"])), lambda w: f"{stufen[w]} Tokens",
                            lambda w: k.chat_setzen(numCtx=stufen[w]))
        import os as _os
        self.s_thread = regler("Rechenkerne (Ollama)", "Wie viele Prozessorkerne Ollama nutzt. Automatisch ist meist am besten; weniger kann "
                               "den Rechner kühler und ruhiger halten, bei Bedarf kleiner stellen.", _os.cpu_count() or 8,
                               _ki.num_thread_begrenzen(o["numThread"]), lambda w: str(w) if w else "automatisch",
                               lambda w: k.chat_setzen(numThread=w))
        self.streaming = UmbruchSchalter("Antwort Stück für Stück anzeigen (Ollama)"); self.streaming.setChecked(bool(o["streaming"]))
        self.streaming.toggled.connect(lambda an: k.chat_setzen(streaming=an))
        ew.addWidget(self.streaming)
        ew.addWidget(text_label("Stoppfolgen", fett=True))
        self.stopp = QLineEdit(str(o["stopp"])); self.stopp.setPlaceholderText("durch Komma getrennt")
        self.stopp.textChanged.connect(lambda t: k.chat_setzen(stopp=t))
        ew.addWidget(self.stopp)
        self.direkt = UmbruchSchalter("Antwort direkt ins Dokument einfügen"); self.direkt.setChecked(bool(o["direkt"]))
        self.direkt.toggled.connect(lambda an: k.chat_setzen(direkt=an))
        ew.addWidget(self.direkt)
        v.addWidget(self.inhalt)
        self.mehr.clicked.connect(lambda: self.umschalten(not self.inhalt.isVisible()))
        self.umschalten(False)

    def umschalten(self, an: bool) -> None:
        self.inhalt.setVisible(an)
        self.mehr.setText("Chat-Einstellungen ausblenden" if an else "Chat-Einstellungen anzeigen")
        self.mehr.setIcon(icons.icon("chevron-up" if an else "chevron-down", ICON_NORMAL))
