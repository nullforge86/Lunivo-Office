"""Dialoge zu Sendungen: Umschlag, Etiketten, Seriendruck, Regeln, Vorschau."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QDialog, QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QVBoxLayout,
)
from lunivo_writer.ui.baukasten.dokument.speichern_fenster import Dateifenster

from lunivo_writer.editor import sendungen as S
from lunivo_writer.ui.baukasten.controls.formular_gitter import FlussLayout, FormularGitter
from lunivo_writer.ui.baukasten.basis.mass import (
    GROESSE_FENSTER_SENDUNG,
    HOEHE_TEXT_KURZ,
    HOEHE_TEXT_MITTEL,
    HOEHE_TEXT_NORMAL,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld


def _hinweis(text: str) -> QLabel:
    lb = QLabel(text.replace("\n", " "))
    lb.setWordWrap(True)
    return lb


def _ok(dlg, text_ok: str | None = None):
    return knopfzeile(dlg, ok_text=text_ok or "OK")


from lunivo_writer.ui.baukasten.controls.zusatz_panel import PanelFaehig
from lunivo_writer.ui.baukasten.basis.dialog_rahmen import knopfzeile
class UmschlagDialog(PanelFaehig, QDialog):
    def __init__(self, parent, absender: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Umschlag")
        f = FormularGitter(self)
        f.breit(_hinweis("Das Blatt wird auf Umschlagformat gestellt und beides eingesetzt.\nDanach steht der Umschlag allein im Dokument."))
        self.format = Auswahlfeld(); self.format.addItems(list(S.UMSCHLAEGE))
        self.absender = QPlainTextEdit(absender); self.absender.setFixedHeight(HOEHE_TEXT_KURZ)
        self.empfaenger = QPlainTextEdit("Vorname Nachname\nStraße 1\n12345 Ort"); self.empfaenger.setFixedHeight(HOEHE_TEXT_MITTEL)
        f.zeile("Format", self.format); f.zeile("Absender", self.absender); f.zeile("Empfänger", self.empfaenger)
        f.breit(_ok(self, "Anlegen"))


class EtikettenDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Etiketten")
        f = FormularGitter(self)
        f.breit(_hinweis("Ein Bogen wird angelegt. Steht überall dasselbe, kommt der Text in jedes Feld; sonst je Zeile eines."))
        self.bogen = Auswahlfeld(); self.bogen.addItems(list(S.ETIKETTEN))
        self.text = QPlainTextEdit("Vorname Nachname\nStraße 1\n12345 Ort"); self.text.setFixedHeight(HOEHE_TEXT_NORMAL)
        self.gleich = Auswahlfeld(); self.gleich.addItems(["ja — derselbe Text", "nein — je Zeile ein Etikett"])
        f.zeile("Bogen", self.bogen); f.zeile("Aufschrift", self.text); f.zeile("Überall dasselbe", self.gleich)
        f.breit(_ok(self, "Anlegen"))


class SeriendruckDialog(PanelFaehig, QDialog):
    def __init__(self, parent, felder: list[str], gespeichert: str):
        super().__init__(parent)
        self.setWindowTitle("Seriendruck")
        self.resize(*GROESSE_FENSTER_SENDUNG)
        v = QVBoxLayout(self)
        v.addWidget(QLabel(
            ("Im Text gefunden: " + ", ".join("{{" + x + "}}" for x in felder) + "\nDie erste Zeile unten muss diese Namen enthalten.")
            if felder else "Im Text stehen noch keine Platzhalter. Fügen Sie Felder über Sendungen ▸ Seriendruckfeld ein\n"
                           "(oder schreiben Sie {{Name}} in den Text) und kommen Sie dann hierher zurück."))
        self.daten = QPlainTextEdit(gespeichert or (";".join(felder) + "\n" if felder else "Name;Ort\nFrau Meier;Kiel\nHerr Schmidt;Bonn"))
        v.addWidget(self.daten)
        z = FlussLayout()
        b = QPushButton("Aus Datei laden (CSV/TXT) …"); b.clicked.connect(self._laden); z.addWidget(b)
        v.addLayout(z)
        v.addWidget(_ok(self, "Briefe erzeugen"))

    def _laden(self):
        pfad, _ = Dateifenster.getOpenFileName(self, "Empfängerliste", "", "Tabellen (*.csv *.txt *.tsv);;Alle Dateien (*)")
        if pfad:
            for enc in ("utf-8-sig", "cp1252"):
                try:
                    self.daten.setPlainText(open(pfad, encoding=enc).read()); break
                except (UnicodeDecodeError, OSError):
                    continue


class RegelDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Regel")
        f = FormularGitter(self)
        f.breit(_hinweis("Wenn das Feld den Wert hat, steht der erste Text da — sonst der zweite."))
        self.feld = QLineEdit("Geschlecht"); self.wert = QLineEdit("w")
        self.dann = QLineEdit("Sehr geehrte Frau"); self.sonst = QLineEdit("Sehr geehrter Herr")
        for lab, w in (("Feld", self.feld), ("ist gleich", self.wert), ("dann", self.dann), ("sonst", self.sonst)):
            f.zeile(lab, w)
        f.breit(_ok(self, "Einfügen"))
