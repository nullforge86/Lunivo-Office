"""Öffentliche Fassade des KI-Dienstes; Fachlogik liegt in eigenen Mixins."""
from __future__ import annotations

import os
import threading

from lunivo_writer.services.settings_service import data_dir
from lunivo_writer.ai import ki as K
from lunivo_writer.ai import assistent_lauf as AL
from lunivo_writer.ai.chat_modell import ChatModell

from PySide6.QtCore import QObject, QThreadPool, QTimer, Signal
from lunivo_writer.ai.ki_anfragen import KIAnfragenMixin
from lunivo_writer.ai.ki_aktionen import KIAktionenMixin
from lunivo_writer.ai.ki_dauerbetrieb import KIDauerbetriebMixin
from lunivo_writer.ai.ki_chat import KIChatMixin
from lunivo_writer.ai.arbeitslauf import _Sig



class KIDienst(KIAnfragenMixin, KIAktionenMixin, KIDauerbetriebMixin, KIChatMixin, QObject):
    werkzeugFrage = Signal(str, str, str)     # Werkzeug, Argumente, Server — die Rückfrage läuft im Hauptthread
    status = Signal(str)
    laeuft = Signal(bool)
    vorschlaege = Signal(list)                # Liste von {alt, neu, grund}
    hinweis = Signal(str, str, object)        # Titel, Text, Kosten (cent) — Karte in der Seitenleiste
    aktionErgebnis = Signal(str, str, object, object)  # Name, Text, Kosten, Bezug (dict|None) — das Ergebnis einer Schnellen KI-Aktion (der Chat zeigt es als Antwort)
    geaendert = Signal()                      # Einstellungen haben sich geändert
    chatTeil = Signal()                       # neuer Zwischenstand der streamenden Chat-Antwort (``chat_modell.teil``) — nur die Anzeige des Teils nachziehen
    chatGeaendert = Signal()                  # ``chat_modell`` hat sich geändert (Nachricht, Phase, Gespräch) — die Anzeige liest daraus
    kontextGeaendert = Signal()               # Markierung oder Dokumentinhalt (leer/nicht leer) haben sich geändert — ``kontext()`` neu lesen

    def __init__(self, assistant, fenster, parent=None):
        super().__init__(parent)
        self.w = fenster
        self.assistant = assistant
        self.konfig = K.KIKonfig(os.path.join(data_dir(), "ki.json"))
        self.ki = K.KI(self.konfig, assistant.gelernt.daten)
        self._arbeit_laeuft = False
        self.chat_modell = ChatModell()
        self.ergebnisse: list[dict] = []          # „Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung (neueste zuletzt)
        self._pool = QThreadPool(self)
        self._sig = _Sig()
        self._sig.fertig.connect(self._fertig)
        self._sig.teil.connect(self._chat_teil)
        self._chat_abbruch = threading.Event()       # beendet eine streamende Ollama-Verbindung sofort
        self.werkzeugFrage.connect(self._werkzeug_fragen)
        self.aktionErgebnis.connect(self.aktion_in_chat)         # Verlauf und Anzeige führen dieselbe Quelle
        self.ki.werkzeug_frage = self._werkzeug_erlaubt
        self.ki.server_frage = self._server_erlaubt
        self.ki.faehigkeit_bekannt = self.geaendert.emit          # Ollama hat die Fähigkeiten des Modells gemeldet: Menüs neu lesen
        self.konfig.d["empfaenger"] = assistant.thema
        self._drossel = AL.Drossel()                  # fortlaufende Assistenten: Mindestabstand und Höchstzahl je Stunde
        self._dauer_timer = QTimer(self)
        self._dauer_timer.setSingleShot(True)
        self._dauer_timer.timeout.connect(self._dauer_los)
        self._dauer_art = "absatz"                    # was die letzte Änderung war: „absatz“ (Text) oder „markierung“
        self._dauer_zuletzt: dict = {}                # (Assistent, Stelle) → zuletzt gesendeter Text
        self._dauer_eigen = False                     # der Assistent schreibt selbst ins Dokument: das löst keine neue Runde aus
        self._dauer_pause = False
