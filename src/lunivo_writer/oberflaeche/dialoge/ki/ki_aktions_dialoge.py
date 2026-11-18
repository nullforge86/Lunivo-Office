"""KI-Aktionsfenster: Schnelle KI-Aktion, Neuer Assistent, Alle Ergebnisse (Erstellen-Fenster nach dem Baukasten)."""
from __future__ import annotations


from PySide6.QtWidgets import (
    QDialog, QLabel, QListWidget, QPushButton, QVBoxLayout,
)
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld

from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil
from lunivo_writer.ki import ki as K
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter, abschnittstitel


from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    HOEHE_LISTE_AUSWAHL,
    HOEHE_LISTE_KURZ,
    RAND_KEIN,
)
from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_ZEICHEN_LANG
from lunivo_writer.oberflaeche.dialoge.ki.ki_modelle_dialoge import (
    modell_felder_fuellen,
)



from lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_chips import AufklappBereich
from lunivo_writer.oberflaeche.baukasten.dokument.erstellen_fenster import ErstellenFenster




VORLAGEN_AKTION = [
    ("Übersetzen", "Übersetze den Text ins Englische."), ("Ton ändern", "Schreibe den Text in einem freundlicheren, höflichen Ton."),
    ("Professionelle Umschreibung", "Schreibe den Text professionell und sachlich um."),
    ("Zusammenfassung als Liste", "Fasse den Text als kurze Aufzählung zusammen."), ("Text vereinfachen", "Schreibe den Text in einfacher Sprache."),
    ("Text erweitern", "Erweitere den Text um passende Einzelheiten."), ("Grammatik korrigieren", "Korrigiere Grammatik und Rechtschreibung."),
    ("Kürzer machen", "Kürze den Text, ohne Wichtiges wegzulassen."), ("Länger machen", "Mache den Text ausführlicher."),
    ("Kernpunkte herausziehen", "Nenne die Kernpunkte des Textes."), ("Tabelle erstellen", "Fasse die Angaben des Textes in einer Tabelle zusammen."),
    ("Beispiele hinzufügen", "Ergänze passende Beispiele."), ("Einfach erklären", "Erkläre den Inhalt so, dass ihn ein Kind versteht.")]
ERGEBNIS_ARTEN = (("ersetzen", "Ersetzen (ersetzt den markierten Text durch das Ergebnis)"), ("anhaengen", "Anhängen (setzt das Ergebnis hinter den Text)"),
                  ("hinweis", "Als Hinweis zeigen (Karte in der Seitenleiste)"))


class SchnelleAktionDialog(ErstellenFenster):
    """„Schnelle KI-Aktion erstellen“: eine einmalige KI-Aufgabe mit Name, Anweisung, Ergebnisart und Zugriff.

    Speichert als „Eigener Assistent“ (``KIKonfig.assistenten``) — dieselbe Liste wie im Band und in den Optionen."""

    def __init__(self, fenster):
        from PySide6.QtWidgets import QRadioButton
        super().__init__(fenster, TEXTE_AKTION["titel"], TEXTE_AKTION["hinweis"], [n for n, _p in VORLAGEN_AKTION], meldung=TEXTE_AKTION["meldung"])
        g = self.gitter
        self.name_zeile("Name *", TEXTE_AKTION["name"])
        self.prompt_zeile("Was soll die Aktion tun? *", TEXTE_AKTION["prompt"])
        self.ergebnis = Auswahlfeld()
        self.ergebnis.zeichen(DROPDOWN_ZEICHEN_LANG)
        for schl, text in ERGEBNIS_ARTEN:
            self.ergebnis.addItem(text, schl)
        g.zeile("Ergebnis anwenden als", self.ergebnis)
        g.breit(abschnittstitel("Zugriff von"))
        self.r_kontext = QRadioButton("Verfügbar über das Kontextmenü"); self.r_kontext.setChecked(True)
        self.r_schnell = QRadioButton("Schnellzugriff über die Symbolleiste")
        zugriff = FlussLayout(); zugriff.addWidget(self.r_kontext); zugriff.addWidget(self.r_schnell)
        g.breit(zugriff)
        self.abschliessen()

    def vorlage_gewaehlt(self, i: int) -> None:
        self.name.setText(VORLAGEN_AKTION[i][0]); self.prompt.setPlainText(VORLAGEN_AKTION[i][1])

    def werte(self) -> tuple:
        return (self.name.text(), self.prompt.toPlainText(), self.ergebnis.currentData(), "schnell" if self.r_schnell.isChecked() else "kontext")


TEXTE_AKTION = {"titel": "Schnelle KI-Aktion erstellen", "hinweis": "Eine schnelle KI-Aktion führt einmalige KI-Aufgaben aus.",
                "meldung": "Name und Beschreibung werden gebraucht.", "name": "Geben Sie einen kurzen Namen für die Aktion ein",
                "prompt": "Beschreiben Sie die Aktion, die die KI ausführen soll, z. B. „Grammatik korrigieren“ oder „In einem formellen Ton umschreiben“"}
TEXTE_ASSISTENT = {"titel": "Neuen Assistenten erstellen", "hinweis": "Ein KI-Assistent kann fortlaufend arbeiten und auf Änderungen im Dokument reagieren.",
                    "meldung": "Name und Prompt werden gebraucht.", "name": "Geben Sie Ihrem Werkzeug einen kurzen Namen für die Symbolleiste",
                    "prompt": "Sagen Sie der KI, was Sie mit dem Text tun möchten (z. B. „Faktenfehler finden“ oder „Zusammenfassung“)"}
AKTION_TEXTE = {"ersetzen": "Ersetzen (Ersetzt den ausgewählten Text mit dem KI-Ergebnis)",
                "anhaengen": "Anhängen (Setzt das KI-Ergebnis hinter den Text)",
                "hinweis": "Hinweis (Zeigt das Ergebnis als Karte in der Seitenleiste)",
                "kommentar": "Kommentar (Legt das Ergebnis als Kommentar am Text an)",
                "hervorheben": "Hervorheben (Meldet Funde in der Schreibhilfe)"}
AUSLOESER_TEXTE = {"knopf": "Nur auf Knopfdruck (keine Überwachung)", "absatz": "Wenn ein Absatz geändert wird", "markierung": "Wenn Text markiert wird"}
UMFANG_TEXTE = {"absatz": "Der geänderte Absatz", "markierung": "Die Markierung"}
ASSISTENT_DATENSCHUTZ = ("Ein fortlaufender Assistent sendet den geänderten Absatz an das gewählte KI-Modell. Bei einem Anbieter im Internet verlässt der Text "
                         "den Rechner und kann Kosten verursachen; er läuft nur bei eingeschaltetem Hauptschalter und gesetztem Haken.")


class KIAssistentDialog(ErstellenFenster):
    """„Neuen Assistenten erstellen“: ein KI-Assistent, der fortlaufend arbeitet und auf Änderungen im Dokument reagiert.

    ``werte()`` liefert ``(name, prompt, modus, mehr)``; der Befehl ``w_kiAssistentErstellen`` speichert mit ``art="fortlaufend"``."""

    def __init__(self, fenster):
        from lunivo_writer.ki.assistent_lauf import VERZOEGERUNG_MAX, VERZOEGERUNG_MIN, VERZOEGERUNG_VORGABE
        from lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.symbol_auswahl import SymbolWahl
        from lunivo_writer.oberflaeche.baukasten.felder.mass_feld import spin
        t = TEXTE_ASSISTENT
        super().__init__(fenster, t["titel"], t["hinweis"], [e[0] for e in K.VORLAGEN_ASSISTENT], meldung=t["meldung"])
        g = self.gitter
        self.symbol = SymbolWahl()
        self.name_zeile("Name *", t["name"], symbol=self.symbol)
        self.aktion = Auswahlfeld(); self.aktion.zeichen(DROPDOWN_ZEICHEN_LANG)
        for schl in K.FORTLAUFEND_MODI:
            self.aktion.addItem(AKTION_TEXTE[schl], schl)
        g.zeile("Aktion", self.aktion)
        self.prompt_zeile("Prompt *", t["prompt"])
        self.kommentar = UmbruchSchalter("Erklärender Kommentar")
        self.kommentar.setToolTip("Die KI begründet jede Änderung kurz in einem Kommentar.")
        g.breit(self.kommentar)
        self.erweitert = AufklappBereich("Erweiterte Einstellungen")
        eg = FormularGitter(self.erweitert.inhalt); eg.setContentsMargins(*RAND_KEIN)
        self.modell = Auswahlfeld(); modell_felder_fuellen(self.modell, fenster.ki.konfig, "assistent", "")
        eg.zeile("Modell", self.modell)
        self.ausloeser = Auswahlfeld(); self.ausloeser.zeichen(DROPDOWN_ZEICHEN_LANG)
        for schl in K.ASSISTENT_AUSLOESER:
            self.ausloeser.addItem(AUSLOESER_TEXTE[schl], schl)
        self.ausloeser.setCurrentIndex(max(0, self.ausloeser.findData(K.ASSISTENT_AUSLOESER[1])))
        eg.zeile("Auslöser", self.ausloeser)
        self.verzoegerung = spin(VERZOEGERUNG_VORGABE, VERZOEGERUNG_MIN, VERZOEGERUNG_MAX, " s", 1, 0)
        eg.zeile("Verzögerung", self.verzoegerung)
        self.umfang = Auswahlfeld()
        for schl in K.ASSISTENT_UMFAENGE:
            self.umfang.addItem(UMFANG_TEXTE[schl], schl)
        eg.zeile("Umfang", self.umfang)
        self.an = UmbruchSchalter("Sofort einschalten"); self.an.setChecked(True)
        eg.breit(self.an)
        hinweis = QLabel(ASSISTENT_DATENSCHUTZ); hinweis.setWordWrap(True); hinweis_stil(hinweis)
        eg.breit(hinweis)
        g.breit(self.erweitert)
        self.abschliessen()

    def vorlage_gewaehlt(self, i: int) -> None:
        name, prompt, modus, kommentar = K.VORLAGEN_ASSISTENT[i]
        self.name.setText(name); self.prompt.setPlainText(prompt); self.aktion.setCurrentIndex(max(0, self.aktion.findData(modus)))
        self.kommentar.setChecked(bool(kommentar))

    def werte(self) -> tuple:
        mehr = {"symbol": self.symbol.wert(), "kommentar": self.kommentar.isChecked(), "modell": self.modell.currentData() or "",
                "ausloeser": self.ausloeser.currentData(), "umfang": self.umfang.currentData(), "verzoegerung": int(self.verzoegerung.value()),
                "an": self.an.isChecked()}
        return (self.name.text().strip(), self.prompt.toPlainText().strip(), self.aktion.currentData(), mehr)


class ErgebnisseDialog(PanelFaehig, QDialog):
    """„Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung; Kopieren oder an der Schreibmarke einfügen."""

    def __init__(self, fenster):
        super().__init__(fenster)
        from PySide6.QtWidgets import QApplication, QPlainTextEdit
        self.fenster = fenster
        self.setWindowTitle("Alle Ergebnisse")
        self.liste_daten = list(reversed(fenster.ki.ergebnisse))                     # neueste oben
        v = QVBoxLayout(self)
        self.liste = QListWidget()
        self.liste.setMaximumHeight(HOEHE_LISTE_AUSWAHL)
        for e in self.liste_daten:
            self.liste.addItem(f"{e['zeit']}  {e['titel']}")
        v.addWidget(self.liste)
        self.text = QPlainTextEdit(); self.text.setReadOnly(True); self.text.setMinimumHeight(HOEHE_LISTE_KURZ)
        v.addWidget(self.text, 1)
        if not self.liste_daten:
            v.addWidget(QLabel("In dieser Sitzung hat die KI noch nichts geliefert."))
        bb = knopfzeile(self, schliessen=True)
        self.kopieren = bb.zusatz_knopf(QPushButton("Kopieren"))
        self.einfuegen = bb.zusatz_knopf(QPushButton("Einfügen"))
        self.kopieren.clicked.connect(lambda: QApplication.clipboard().setText(self.text.toPlainText()))
        self.einfuegen.clicked.connect(self._einfuegen)
        v.addWidget(bb)
        self.liste.currentRowChanged.connect(self._zeigen)
        if self.liste_daten:
            self.liste.setCurrentRow(0)
        self._zeigen(self.liste.currentRow())

    def _zeigen(self, i: int) -> None:
        an = 0 <= i < len(self.liste_daten)
        self.text.setPlainText(self.liste_daten[i]["text"] if an else "")
        self.kopieren.setEnabled(an); self.einfuegen.setEnabled(an)

    def _einfuegen(self) -> None:
        e = self.fenster.current_editor()
        if e is not None and self.text.toPlainText():
            e.textCursor().insertText(self.text.toPlainText())
