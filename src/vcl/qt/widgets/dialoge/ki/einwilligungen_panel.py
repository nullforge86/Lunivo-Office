"""Einwilligungen panel: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QMessageBox, QWidget
from framework.ki.dienst import ki as K
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_KNOPF_GROSS


class EinwilligungenPanel(QWidget):
    """Wer darf welchen Text bekommen: die gespeicherten Einwilligungen, einzeln oder alle widerrufbar. Ohne Einwilligung wird nichts gesendet."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        self.k = konfig
        v = _spalte("oben", self)
        info = QLabel("Diese Dienste im Internet dürfen Text von Ihnen bekommen. Ohne Eintrag fragt Lunivo vor dem Senden und sendet bei „Nein“ nichts. "
                      "Modelle auf diesem Rechner (Ollama, lokale Adressen) brauchen keine Erlaubnis.")
        info.setWordWrap(True); v.addWidget(info)
        self.liste = QListWidget(); self.liste.setAccessibleName("Erteilte Einwilligungen"); v.addWidget(self.liste, 1)
        self.liste.setWordWrap(True); self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)          # lange Einträge brechen um statt zu rollen
        z = FlussLayout(6)
        self.widerruf = knopf("standard", "Widerrufen", name="Widerrufen", tooltip="Nimmt die ausgewählte Erlaubnis zurück")
        self.alle = knopf("standard", "Alle widerrufen")
        for b in (self.widerruf, self.alle):
            b.setMinimumHeight(HOEHE_KNOPF_GROSS); z.addWidget(b)
        v.addLayout(z)
        self.widerruf.clicked.connect(self._widerrufen); self.alle.clicked.connect(self._alle)
        self.liste.currentRowChanged.connect(self._knoepfe)
        self.fuellen()

    def fuellen(self) -> None:
        self.liste.clear()
        for e in self.k.einwilligungen():
            seit = f" — seit {e['seit']}" if e["seit"] else ""
            it = QListWidgetItem(f"{e['anbieter']}: darf {K.UMFAENGE[e['umfang']]} bekommen{seit}")
            it.setData(Qt.UserRole, (e["anbieter"], e["umfang"])); self.liste.addItem(it)
        if not self.liste.count():
            it = QListWidgetItem("Keine Einwilligung gespeichert — es wird nichts ohne Rückfrage gesendet."); it.setFlags(Qt.NoItemFlags); self.liste.addItem(it)
        else:
            self.liste.setCurrentRow(0)
        self._knoepfe()

    def _knoepfe(self, *_) -> None:
        self.widerruf.setEnabled(self.liste.currentItem() is not None and self.liste.currentItem().data(Qt.UserRole) is not None)
        self.alle.setEnabled(bool(self.k.einwilligungen()))

    def _widerrufen(self) -> None:
        d = self.liste.currentItem().data(Qt.UserRole) if self.liste.currentItem() else None
        if d:
            self.k.einwilligung_widerrufen(*d); self.fuellen()

    def _alle(self) -> None:
        if QMessageBox.question(self, "Alle widerrufen", "Alle gespeicherten Einwilligungen zurücknehmen?") == QMessageBox.Yes:
            self.k.einwilligung_widerrufen(); self.fuellen()
