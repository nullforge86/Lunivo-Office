"""Objekt dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QLabel, QListWidget
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_EINGABE_TEXT
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster_hilfen import _titel


class ObjektDialog(PanelFaehig, QDialog):
    """„Objekt einfügen“ wie in der Vorlage. „Neu“ (ein eingebettetes Objekt eines anderen Programms anlegen) kann Lunivo nicht und bleibt grau;
    „Aus Datei erstellen“ fügt Text, Dokument oder Bild ein, mit „Als Symbol anzeigen“ ein Dateisymbol mit Link auf die Datei."""

    TYPEN = ("DOCX-Dokument", "ODT-Dokument", "XLSX-Tabelle", "PPTX-Präsentation")

    def __init__(self, parent=None, *, als_symbol: bool = False, ordner: str = ""):
        super().__init__(parent)
        from PySide6.QtWidgets import QFrame, QPushButton
        self.setWindowTitle("Objekt einfügen")
        self._ordner = ordner
        v = _spalte("standard", self)
        g = FormularGitter()                                                   # in der Seitenleiste untereinander: Art, Objekttyp, Datei, Symbol
        self.neu = option("standard", "&Neu"); self.aus_datei = option("standard", "&Aus Datei erstellen")
        self.neu.setEnabled(False); self.neu.setToolTip("Eingebettete Objekte anderer Programme kann Lunivo nicht anlegen.")
        self.aus_datei.setChecked(True)
        links = FlussLayout(14); links.addWidget(self.neu); links.addWidget(self.aus_datei)
        g.breit(links)
        self.typen = QListWidget(); self.typen.addItems(list(self.TYPEN)); self.typen.setEnabled(False); self.typen.setMaximumHeight(HOEHE_EINGABE_TEXT)
        g.breit(_titel("Objekt&typ:", self.typen)); g.breit(self.typen)
        self.datei = zeilenfeld("standard", name="Datei")
        such = knopf("klein", "&Durchsuchen …", aktion=self._suchen)
        g.zeile(_titel("&Datei:", self.datei), self.datei); g.breit(such)
        self.symbol = UmbruchSchalter("Als Sym&bol anzeigen"); self.symbol.setChecked(als_symbol)
        g.breit(self.symbol)
        g.breit(abschnittstitel("Ergebnis"))
        v.addLayout(g)
        kasten = rahmen_baustein("panel"); kh = _spalte("standard", kasten)
        self.ergebnis_text = QLabel(); self.ergebnis_text.setWordWrap(True); kh.addWidget(self.ergebnis_text)
        v.addWidget(kasten)
        self.ok = fussleiste(self, v)
        self.datei.textChanged.connect(lambda _t: self._beschreiben()); self.symbol.toggled.connect(lambda _a: self._beschreiben())
        self._beschreiben()

    def _suchen(self) -> None:
        from vcl.qt.widgets.dialoge.dokument.speichern_fenster import datei_waehlen
        pfade = datei_waehlen(self, "Datei für das Objekt wählen", self.datei.text() or self._ordner, "Alle Dateien (*)")
        if pfade:
            self.datei.setText(pfade[0])

    def art(self) -> str:
        """"symbol" | "bild" | "text" | "" (keine Datei)."""
        import os
        pfad = self.datei.text().strip()
        if not pfad or not os.path.isfile(pfad):
            return ""
        if self.symbol.isChecked():
            return "symbol"
        endung = os.path.splitext(pfad)[1].lower()
        if endung in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"):
            return "bild"
        if endung in (".docx", ".odt", ".rtf", ".txt", ".md"):
            return "text"
        return "symbol"

    def _beschreiben(self) -> None:
        import os
        a = self.art()
        name = os.path.basename(self.datei.text().strip())
        self.ok.setEnabled(bool(a))
        self.ergebnis_text.setText({
            "": "Wählen Sie eine Datei. Ihr Inhalt wird in das Dokument eingefügt.",
            "bild": f"Fügt das Bild „{name}“ in Ihr Dokument ein.",
            "text": f"Fügt den Inhalt von „{name}“ in Ihr Dokument ein (Text, Tabellen und Bilder).",
            "symbol": f"Fügt ein Symbol für „{name}“ ein. Ein Klick darauf öffnet die Datei."
                      + ("" if self.symbol.isChecked() else " (Den Inhalt dieser Dateiart kann Lunivo nicht einbetten.)"),
        }[a])
