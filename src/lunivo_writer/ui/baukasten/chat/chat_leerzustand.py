"""Leerzustand des KI-Chats: Symbol, Text „Ihr KI-Assistent für Dokumente“ und darunter die Vorschläge (Chips) passend zu Markierung und Dokument.

Ein Klick auf einen Chip meldet die Anweisung (``gewaehlt``) — der Chat füllt damit das Eingabefeld, gesendet wird erst mit „Senden“. Die Chips kommen aus
``ai.chat_vorschlaege`` und ``dienst.kontext()``; ``neu_aufbauen`` wird bei ``kontextGeaendert``/``geaendert`` gerufen."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from lunivo_writer.ai.chat_vorschlaege import chat_vorschlaege
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout
from lunivo_writer.ui.baukasten.karte import als_karte
from lunivo_writer.ui.baukasten.mass import ABSTAND_BLOCK, ABSTAND_NORMAL, CHAT_CHIP_HOEHE, CHAT_LEER_ICON, RAND_KEIN
from lunivo_writer.ui.baukasten.texte import hinweis_label
from lunivo_writer.ui.widgets import icons

TEXT = "Ihr KI-Assistent für Dokumente"


class ChatLeerzustand(QWidget):
    gewaehlt = Signal(str)

    def __init__(self, dienst):
        super().__init__()
        self.d = dienst
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_BLOCK)
        v.addStretch(1)
        self.symbol = QLabel(); self.symbol.setAlignment(Qt.AlignCenter)
        v.addWidget(self.symbol)
        t = hinweis_label(TEXT); t.setAlignment(Qt.AlignCenter)
        v.addWidget(t)
        v.addStretch(1)
        self.chips = QWidget()
        self._fluss = FlussLayout(ABSTAND_NORMAL, zentriert=True)
        self.chips.setLayout(self._fluss)
        v.addWidget(self.chips)
        self.neu_aufbauen()

    def _bild(self) -> None:
        self.symbol.setPixmap(icons.icon("sparkles", CHAT_LEER_ICON).pixmap(CHAT_LEER_ICON, CHAT_LEER_ICON))

    def changeEvent(self, e) -> None:
        from PySide6.QtCore import QEvent
        if e.type() in (QEvent.PaletteChange, QEvent.StyleChange) and hasattr(self, "symbol"):
            self._bild()
        super().changeEvent(e)

    def neu_aufbauen(self) -> None:
        """Chips aus Markierung, Dokumentstand und Konfiguration neu bilden."""
        self._bild()
        while self._fluss.count():
            it = self._fluss.takeAt(0)
            w = it.widget()
            if w is not None:
                w.hide(); w.setParent(None); w.deleteLater()
        auswahl, leer = self.d.kontext()[:2]
        for e in chat_vorschlaege(auswahl, leer, self.d.konfig):
            b = QPushButton(e["titel"]); als_karte(b, "chip"); b.setFixedHeight(CHAT_CHIP_HOEHE); b.setToolTip(e["anweisung"][:200])
            b.setCursor(Qt.PointingHandCursor)
            if e.get("hinweis"):                                # klickbar bleibt jeder Chip (füllt das Eingabefeld); der Hinweis sagt nur, worauf er wirkt
                b.setToolTip(e["hinweis"] + "\n\n" + e["anweisung"][:200])
            b.clicked.connect(lambda _=False, a=e["anweisung"]: self.gewaehlt.emit(a))
            self._fluss.addWidget(b)
