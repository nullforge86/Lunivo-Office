"""Das ☰ Menü: links die Datei-Befehle, rechts der Inhalt (zuletzt verwendete Dateien oder die Punkte eines Untermenüs)."""
from __future__ import annotations

import os
from datetime import datetime

from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil, trennlinie
from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import md_escape, md_label, text_label
from lunivo_writer.oberflaeche.baukasten.medien.datei_symbole import datei_symbol
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    ABSTAND_KEIN,
    ABSTAND_BLOCK,
    BREITE_MENUETAFEL,
    BREITE_NAVIGATION_OPTIONEN,
    ICON_KNOPF_GROSS,
    ICON_MITTEL,
    RAND_PANEL_KLEIN,
)
from lunivo_writer.oberflaeche.baukasten.dropdown.zeile import dropdown_zeile
from lunivo_writer.oberflaeche.baukasten.dropdown.popup_lage import PopupVerhalten


# Symbolnamen aus dem zentralen Lucide-Katalog.
_MENUE_SYMBOLE = {
    "Neu": "file-plus", "Neu aus Vorlage": "files", "Öffnen": "folder-open", "Speichern": "save",
    "Speichern unter": "file-plus", "Drucken": "printer", "Druckvorschau": "panels-top-left",
    "Druckereinstellungen": "settings-2", "Dokumenteigenschaften": "info", "Umbenennen": "file-pen",
    "Schließen": "x", "Hilfe": "circle-question-mark", "Optionen": "settings", "Beenden": "log-out",
    "Vorlagenordner": "folder-open", "Zuletzt geöffnet": "clock-arrow-up",
}


def _menue_symbol(name: str) -> QIcon:
    if name == "Als PDF exportieren":
        return datei_symbol(".pdf")
    return symbole.icon(_MENUE_SYMBOLE.get(name, "file"), ICON_MITTEL)


def _datum(pfad: str) -> str:
    """Änderungsdatum der Datei für die Liste „Zuletzt verwendet“ (leer, wenn es sie nicht mehr gibt)."""
    try:
        return datetime.fromtimestamp(os.path.getmtime(pfad)).strftime("%d.%m. %H:%M")
    except OSError:
        return "nicht mehr da"


class MenueTafel(PopupVerhalten, QFrame):
    def __init__(self, punkte: list, befehle, fenster):
        super().__init__(fenster, Qt.Popup)
        self.setFrameShape(QFrame.StyledPanel); self.setProperty("dropdownFenster", True)
        self.punkte, self.b, self.w = punkte, befehle, fenster
        h = QHBoxLayout(self)
        h.setContentsMargins(*RAND_PANEL_KLEIN)
        h.setSpacing(ABSTAND_BLOCK)
        self.links = QVBoxLayout()
        self.links.setSpacing(ABSTAND_KEIN)
        host = QWidget()
        host.setLayout(self.links)
        host.setFixedWidth(BREITE_NAVIGATION_OPTIONEN)
        h.addWidget(host)
        self.rechts = QVBoxLayout()
        self.rechts.setAlignment(Qt.AlignTop)
        rh = QWidget()
        rh.setLayout(self.rechts)
        rh.setFixedWidth(BREITE_MENUETAFEL)
        h.addWidget(rh)
        for p in punkte:
            if p.get("trenner"):
                s = trennlinie(tief=True)
                self.links.addWidget(s)
                continue
            name = p["name"]
            taste = p.get("taste", "")
            b = QPushButton(name)
            sym = _menue_symbol(name)
            if not sym.isNull():
                b.setIcon(sym); b.setIconSize(QSize(ICON_MITTEL, ICON_MITTEL))
            b.setFlat(True)
            dropdown_zeile(b)
            if taste:
                b.setToolTip(taste)
            ok = bool(p.get("unter")) or name in ("Optionen", "Zuletzt geöffnet") or (p.get("tun") and self.b.hat(p["tun"]))
            if p.get("tun") and not self.b.hat(p["tun"]) and name != "Optionen":
                ok = False
            b.setEnabled(bool(ok))
            if not ok:
                b.setToolTip(f"{name} — in der nativen Fassung noch nicht umgesetzt")
            b.clicked.connect(lambda _=False, pp=p: self._klick(pp))
            b.installEventFilter(self)
            b._punkt = p
            self.links.addWidget(b)
        self.links.addStretch(1)
        self._zeige_zuletzt()

    def eventFilter(self, obj, ev):
        from PySide6.QtCore import QEvent
        if ev.type() == QEvent.Enter and hasattr(obj, "_punkt"):
            p = obj._punkt
            if p.get("unter"):
                self._zeige_unter(p)
            elif p["name"] == "Zuletzt geöffnet" or not p.get("tun"):
                self._zeige_zuletzt()
            else:
                self._zeige_zuletzt()
        return super().eventFilter(obj, ev)

    def _leeren(self):
        while self.rechts.count():
            it = self.rechts.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def _zeige_zuletzt(self):
        self._leeren()
        kopf = QHBoxLayout()
        t = text_label("Zuletzt verwendete Dokumente", fett=True, umbruch=False)
        kopf.addWidget(t)
        kopf.addStretch(1)
        r = QToolButton(); r.setText("↻"); r.setAutoRaise(True); r.setToolTip("Liste neu holen")
        r.clicked.connect(self._zeige_zuletzt)
        kopf.addWidget(r)
        kw = QWidget(); kw.setLayout(kopf)
        self.rechts.addWidget(kw)
        items = self.w.settings.recent()
        if not items:
            self.rechts.addWidget(QLabel("Noch keine Dokumente geöffnet."))
        for pfad in items[:10]:
            z = QHBoxLayout()
            b = QPushButton(f"{os.path.basename(pfad)}\n{os.path.dirname(pfad)}")
            b.setIcon(datei_symbol(pfad)); b.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
            b.setFlat(True)
            dropdown_zeile(b, hinweis=True)
            b.clicked.connect(lambda _=False, p=pfad: (self.close(), self.b.zuletztOeffnen(p)))
            x = QToolButton(); x.setText("×"); x.setAutoRaise(True)
            x.setToolTip("Aus der Liste nehmen — die Datei bleibt liegen")
            x.clicked.connect(lambda _=False, p=pfad: (self.b.zuletztEntfernen(p), self._zeige_zuletzt()))
            datum = text_label(_datum(pfad), umbruch=False)
            hinweis_stil(datum, klein=True)
            z.addWidget(b, 1); z.addWidget(datum); z.addWidget(x)
            zw = QWidget(); zw.setLayout(z)
            self.rechts.addWidget(zw)

    def _zeige_unter(self, p: dict):
        self._leeren()
        self.rechts.addWidget(text_label(p["name"], fett=True, umbruch=False))
        for u in p["unter"]:
            if u.get("trenner"):
                continue
            b = QPushButton(u["name"])
            if u.get("datei"):                                     # passendes, lokal gebündeltes Dateiformat-SVG
                b.setIcon(datei_symbol(u["datei"])); b.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
            b.setFlat(True)
            dropdown_zeile(b)
            ok = bool(u.get("tun")) and self.b.hat(u["tun"])
            b.setEnabled(ok)
            if not ok:
                b.setToolTip(f"{u['name']} — in der nativen Fassung noch nicht umgesetzt")
            b.clicked.connect(lambda _=False, t=u.get("tun"): (self.close(), self.b.tun(t)))
            self.rechts.addWidget(b)

    def _klick(self, p: dict):
        if p.get("unter"):
            self._zeige_unter(p)
            return
        self.close()
        if p["name"] == "Optionen":
            self.b.optionen()
        elif p.get("tun") and self.b.hat(p["tun"]):
            self.b.tun(p["tun"])

    def zeigen_unter(self, widget):
        self.adjustSize()
        self.move(widget.mapToGlobal(QPoint(0, widget.height())))
        self.show()
