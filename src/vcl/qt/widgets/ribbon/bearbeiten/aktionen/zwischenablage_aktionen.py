"""Aktionen der Zwischenablage: Einfügen (mit Formatierung, passend, unformatiert, Inhalte wählen), Ausschneiden, Kopieren. Die Zwischenablage liest die Oberfläche;
die Änderungen am Dokument führt das Farmwork aus."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication

from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster


class ZwischenablageAktionen:
    def einfuegen(self, k=None):
        fw = self._bearbeiten()
        if fw is not None:
            fw.einfuegen()

    def einfuegenOhne(self, k=None):
        self.w.paste_plain()

    def einfuegenUnformatiert(self, k=None):
        """Nur der Text der Zwischenablage, ohne jede Formatierung (auch nicht die der Einfügestelle): Schrift und Größe des Dokuments."""
        if not self.ed:
            return
        t = QApplication.clipboard().text()
        if t:
            self.w.paste_plain()

    def inhalteEinfuegen(self, k=None):
        """„Inhalte einfügen …“: aus den Formaten der Zwischenablage eines wählen (mit Formatierung, nur Text, Bild)."""
        fw = self._bearbeiten()
        if fw is None:
            return
        md = QApplication.clipboard().mimeData()
        optionen = []
        if md.hasText() or md.hasUrls() or md.formats():
            optionen.append(("Mit Formatierung", "formatiert"))
        if md.hasText():
            optionen.append(("Unformatierter Text", "text"))
        if md.hasImage():
            optionen.append(("Bild", "bild"))
        if not optionen:
            return
        text, ok = EingabeFenster.getItem(self.w, "Inhalte einfügen", "Als:", [t for t, _a in optionen], 0)
        if not ok:
            return
        art = dict(optionen)[text]
        if art == "text":
            self.w.paste_plain()
        elif art == "bild":
            self._bild_einfuegen(QApplication.clipboard().image(), "Bild")
        else:
            fw.einfuegen_formatiert()

    def ausschneiden(self, k=None):
        fw = self._bearbeiten()
        if fw is not None:
            fw.ausschneiden()

    def kopieren(self, k=None):
        fw = self._bearbeiten()
        if fw is not None:
            fw.kopieren()
