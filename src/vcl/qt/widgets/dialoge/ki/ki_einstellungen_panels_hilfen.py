"""Ki einstellungen panels hilfen: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QSizePolicy, QLabel, QMessageBox, QPushButton, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_KNOPF_GROSS


class _NetzLauf(QRunnable):
    """Ein Netzaufruf der Sprachpakete im Hintergrund; das Ergebnis kommt als Signal zurück."""

    def __init__(self, sender, funktion, *args):
        super().__init__()
        self.sender, self.funktion, self.args = sender, funktion, args

    def run(self) -> None:
        try:
            erg = self.funktion(*self.args)
        except Exception as e:                     # nie den Thread mit Ausnahme beenden
            erg = {"fehler": str(e)}
        try:
            self.sender.fertig.emit(erg)
        except RuntimeError:                       # Fenster schon geschlossen
            pass


class _NetzSender(QObject):
    fertig = Signal(object)


class OfflineSprachen(QWidget):
    """„Offline-Sprachen“: installierte Richtungen der lokalen Übersetzung und das Nachladen weiterer Sprachpakete (nur auf Klick, im Hintergrund)."""

    def __init__(self):
        super().__init__()
        self._pool = QThreadPool(self)
        self._sender = _NetzSender(self)
        self._sender.fertig.connect(self._ergebnis)
        self._modus = ""
        self._ziel: tuple[str, str] | None = None
        v = _spalte("standard", self)
        self.installiert = QLabel(); self.installiert.setWordWrap(True)
        v.addWidget(self.installiert)
        self.laden = knopf("gross", "Weitere Sprachen laden …")
        self.laden.clicked.connect(self._verfuegbare_holen)
        fl = FlussLayout(6); fl.addWidget(self.laden); v.addLayout(fl)
        self.stand = QLabel(); self.stand.setWordWrap(True); hinweis_stil(self.stand); v.addWidget(self.stand)
        self.auswahl = QWidget(); self._av = _spalte("standard", self.auswahl)
        self.auswahl.setVisible(False)
        v.addWidget(self.auswahl)
        self.aktualisieren()

    def aktualisieren(self) -> None:
        from writer.funktionen import ki as argos
        r = argos.argos_installierte_richtungen()                       # lokal, kein Netz
        self.installiert.setText("Installiert: " + ", ".join(x["name"] for x in r) if r else
                                 "Keine Sprachpakete gefunden. Deutsch ↔ Englisch gehört zum Programm; weitere Sprachen laden Sie bei Bedarf.")

    def _sperren(self, an: bool) -> None:
        self.laden.setEnabled(not an)
        for b in self.auswahl.findChildren(QPushButton):
            b.setEnabled(not an)

    def _verfuegbare_holen(self) -> None:
        from writer.funktionen import ki as argos
        self._modus = "liste"; self._sperren(True)
        self.stand.setText("Verfügbare Sprachen werden aus dem Internet abgefragt …")
        self._pool.start(_NetzLauf(self._sender, argos.argos_verfuegbare_richtungen))

    def _herunterladen(self, von: str, nach: str, name: str, mb) -> None:
        gr = f" (ca. {mb} MB)" if mb else ""
        if QMessageBox.question(self, "Sprachpaket laden", f"„{name}“{gr} jetzt aus dem Internet herunterladen und installieren?") != QMessageBox.Yes:
            return
        from writer.funktionen import ki as argos
        self._modus = "paket"; self._ziel = (von, nach); self._sperren(True)
        self.stand.setText(f"„{name}“ wird geladen und installiert … Das kann etwas dauern.")
        self._pool.start(_NetzLauf(self._sender, argos.argos_richtung_installieren, von, nach))

    def _ergebnis(self, erg: dict) -> None:
        self._sperren(False)
        if erg.get("fehler"):
            self.stand.setText(erg["fehler"])
            return
        if self._modus == "paket":
            self.stand.setText(f"Fertig: „{erg.get('name', '')}“ ist jetzt offline verfügbar.")
            self.aktualisieren()
            self._ziel = None
            self._verfuegbare_holen()                            # Liste ohne das neue Paket
            return
        while self._av.count():
            w = self._av.takeAt(0).widget()
            if w is not None:
                w.setParent(None); w.deleteLater()
        liste = erg.get("richtungen", [])
        self.stand.setText("Wählen Sie eine Sprache zum Herunterladen." if liste else "Es gibt keine weiteren Sprachpakete.")
        for r in liste:
            mb = r.get("groesse_mb")
            b = knopf("standard", f"{r['name']}" + (f" · {mb} MB" if mb else "") + "  –  Herunterladen")
            b.setMinimumHeight(HOEHE_KNOPF_GROSS); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(lambda _=False, r=r: self._herunterladen(r["von"], r["nach"], r["name"], r.get("groesse_mb")))
            self._av.addWidget(b)
        self.auswahl.setVisible(bool(liste))
