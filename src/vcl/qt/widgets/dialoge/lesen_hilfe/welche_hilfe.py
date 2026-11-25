"""„Welche Hilfe wann“: die Stufen der Schreibhilfe von der Wellenlinie bis zur KI, die Etiketten der Funde und ein Weg durch einen Brief.

Die Schalter der ersten Stufe sind dieselben wie in der Seitenleiste und in den Optionen (``assistant.setze``); „jetzt“ ruft den Befehl, den auch das Band und die
Tastenkürzel rufen."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein

from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QLabel, QPushButton, QWidget

from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil, trennlinie
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import abschnittstitel
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.schrift.texte import marke_faerben

from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_ENG, ABSTAND_GROSS, ABSTAND_KEIN, ABSTAND_MITTEL, ABSTAND_NORMAL, ABSTAND_ZEILE, BREITE_NUMMER, GROESSE_SCHALTER, GROESSE_STUFE, PADDING_HILFE_CHIP, PADDING_TASTENKUERZEL, RADIUS_MARKE, RADIUS_PILLE, RADIUS_STUFE, RAND_KEIN, RAND_ZEILE_KARTE, SCHRIFT_KLEIN
STUFEN = [
    # (Stufe, Titel, Kürzel, Frage, Hinweis rechts, Schalter | Befehl)
    (1, "Rote Wellenlinien", "", "Gibt es das Wort überhaupt?", "sofort beim Tippen", ("schalter", "wellen")),
    (1, "Wortvorhersage", "", "Wie ging das Wort weiter?", "ab drei Buchstaben", ("schalter", "vorhersage")),
    (1, "AutoKorrektur", "", "Bessert das Offensichtliche beim Tippen", "zum Beispiel „dass“ nach Komma", ("schalter", "autokorr")),
    (2, "Rechtsklick auf ein Wort", "", "Welches Wort war gemeint?", "sucht auch nach dem Klang — F7 meldet ihn ebenfalls", None),
    (3, "Prüfen", "F7", "Ist es das richtige Wort? das/dass, wider/wieder", "die Schreibhilfe rechts", ("tun", "w.pruefen")),
    (4, "Vorlesen", "F4", "Klingt der Satz rund?", "Stimmen aus dem System", ("tun", "vorlesen")),
    (5, "Gründlich prüfen", "", "Stimmt die Grammatik?", "LanguageTool, einmal 400 MB", ("tun", "gruendlichPruefen")),
    (6, "KI-Korrektur", "F8", "Versteht das jemand? Passt der Ton?", "Internet und Guthaben", ("tun", "kiKorrektur")),
]
def _etiketten() -> list:
    return [("SICHER FALSCH", Farbe.WARNUNG, Farbe.AUF_AKZENT, "Da ist kein Zweifel.", "blind übernehmen"),
                ("KOMMT DRAUF AN", Farbe.AKZENT, Farbe.AUF_AKZENT, "Hängt vom Satz ab.", "kurz hinschauen"),
                ("ZUM NACHDENKEN", Farbe.GRAU, Farbe.AUF_AKZENT, "Nur ein Anstoß, keine Regel.", "oft übergehen"),
                ("KI-VORSCHLAG", Farbe.AKZENT_HELL, Farbe.TINTE_DUNKEL, "Die KI hat einen Satz umgeschrieben.", "prüfen, dann annehmen")]
WEG = ["Schreiben, ohne auf die Wellenlinien zu achten.", "F7 drücken und „Alles Eindeutige übernehmen“ wählen.", "Die übrigen Karten einzeln durchgehen.",
       "F4 — einmal vorlesen lassen. Da fällt auf, was keine Regel findet.", "Nur wenn der Text sitzen muss: F8."]


class _Umbruch(QLabel):
    """Text, der umbricht und dabei immer die Höhe bekommt, die er braucht (verschachtelte Layouts reichen „Höhe bei Breite“ nicht sicher weiter)."""

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        h = self.heightForWidth(self.width())
        if h > 0 and h != self.minimumHeight():
            self.setMinimumHeight(h)


def _text(text: str) -> QLabel:
    t = _Umbruch(text); t.setWordWrap(True)
    return t


class HilfeWannDialog(PanelFaehig, QDialog):
    def __init__(self, fenster):
        super().__init__(fenster)
        self.fenster = fenster
        self.schalter: dict[str, QPushButton] = {}
        self.setWindowTitle("Welche Hilfe wann")
        v = _spalte("standard", self)
        host = QWidget(); h = _spalte("standard", host)
        h.addWidget(_text("Jede Stufe ist langsamer als die darüber und klüger als sie. Fang oben an und geh nur so weit hinunter, wie du musst. "
                          "Die Stufen 1 bis 5 brauchen kein Internet und kein Konto."))
        h.addWidget(abschnittstitel("Die Stufen"))
        karte = rahmen_baustein("panel"); kv = _spalte("kein", karte)
        for i, zeile in enumerate(STUFEN):
            kv.addWidget(self._zeile(*zeile, trenner=i > 0))
        h.addWidget(karte)
        h.addWidget(abschnittstitel("Wie sicher ein Fund ist"))
        h.addWidget(_text("Auch innerhalb von F7 gibt es Stufen. Jede Karte in der Seitenleiste trägt eins von vier Etiketten."))
        karte2 = rahmen_baustein("panel"); k2 = _spalte("kein", karte2)
        chips = []
        for i, (name, farbe, schrift, satz, rechts) in enumerate(_etiketten()):
            z = QWidget(); zv = _spalte("karte", z)
            chip = QLabel(name); marke_faerben(chip, farbe, schrift, "font-weight: bold; font-size: " f"{SCHRIFT_KLEIN}" "pt; padding: " f"{PADDING_HILFE_CHIP}" "; border-radius: " f"{RADIUS_MARKE}" "px;")
            chips.append(chip); chip.setAlignment(Qt.AlignCenter)
            kopf = _reihe("standard"); kopf.addWidget(chip); kopf.addStretch(1)
            zv.addLayout(kopf); zv.addWidget(_text(satz))
            r = _text(rechts); hinweis_stil(r); zv.addWidget(r)
            k2.addWidget(self._mit_trenner(z, i > 0))
        h.addWidget(karte2)
        breite = max(c.sizeHint().width() for c in chips)
        for c in chips:
            c.setFixedWidth(breite)                                             # alle Etiketten gleich breit
        h.addWidget(_text("„Alles Eindeutige übernehmen“ fasst nur die erste Sorte an und lässt die anderen beiden in Ruhe. Wenn es eilt, ist das der eine Klick, den du brauchst."))
        h.addWidget(abschnittstitel("Ein Weg durch einen Brief"))
        for n, s in enumerate(WEG, 1):
            zeile = QWidget(); zh = _reihe("inhalt", zeile)
            nr = QLabel(f"{n}."); nr.setFixedWidth(BREITE_NUMMER); nr.setAlignment(Qt.AlignRight | Qt.AlignTop)
            nr.setProperty("akzentSchrift", True); eigenschaft(nr, rolle="stufennummer")
            zh.addWidget(nr); zh.addWidget(_text(s), 1)
            h.addWidget(zeile)
        h.addWidget(_text("Für einen Zettel an die Tür reicht Stufe 1. Für den Widerspruch ans Amt geht man bis 6."))
        v.addWidget(host)
        fussleiste(self, v, ok_text="Schließen")                                # wie in der Vorlage: „Abbrechen“, dann „Schließen“ (die Hauptschaltfläche)
        fenster.assistant.schalterGeaendert.connect(self._nachziehen)

    @staticmethod
    def _mit_trenner(z: QWidget, trenner: bool) -> QWidget:
        if not trenner:
            return z
        w = QWidget(); wv = _spalte("kein", w)
        linie = trennlinie(tief=True)
        wv.addWidget(linie); wv.addWidget(z)
        return w

    def _zeile(self, stufe, titel, kuerzel, frage, rechts, aktion, trenner: bool) -> QWidget:
        """Stufenzeile in drei festen Spalten: Nummer | Text (Titel, Frage, Hinweis) | Schalter rechts, immer oben bündig."""
        z = QWidget(); zh = _reihe("karte", z)
        n = QLabel(str(stufe)); n.setAlignment(Qt.AlignCenter); n.setFixedSize(*GROESSE_STUFE)
        n.setProperty("akzentFlaeche", True); eigenschaft(n, rolle="stufe")
        zh.addWidget(n, 0, Qt.AlignTop)
        mitte_w = QWidget(); mitte = _spalte("eng", mitte_w)
        kopf = _reihe("inhalt")
        t = QLabel(titel); f = t.font(); f.setBold(True); t.setFont(f); kopf.addWidget(t, 0)
        if kuerzel:
            k = QLabel(kuerzel); eigenschaft(k, rolle="tastenchip"); kopf.addWidget(k)
        kopf.addStretch(1)
        mitte.addLayout(kopf)
        mitte.addWidget(_text(frage))
        r = _text(rechts); hinweis_stil(r); mitte.addWidget(r)
        zh.addWidget(mitte_w, 1)
        if aktion and aktion[0] == "schalter":
            b = knopf("standard", umschaltbar=True); b.setFixedSize(*GROESSE_SCHALTER)
            b.setChecked(self.fenster.assistant.an(aktion[1]))
            eigenschaft(b, rolle="pille")
            b.setText("an" if b.isChecked() else "aus")
            b.toggled.connect(lambda an, name=aktion[1], b=b: (b.setText("an" if an else "aus"), self.fenster.assistant.setze(name, an)))
            self.schalter[aktion[1]] = b
            zh.addWidget(b, 0, Qt.AlignTop)
        elif aktion:
            b = knopf("standard", "jetzt"); b.setFixedSize(*GROESSE_SCHALTER)
            b.setProperty("akzentRand", True); eigenschaft(b, rolle="pille_akzent")
            b.clicked.connect(lambda _=False, a=aktion[1]: (self.accept(), self.fenster.befehle.tun(a)))
            zh.addWidget(b, 0, Qt.AlignTop)
        return self._mit_trenner(z, trenner)

    def _nachziehen(self, name: str, an: bool) -> None:
        b = self.schalter.get(name)
        if b is not None and b.isChecked() != an:
            b.blockSignals(True); b.setChecked(an); b.setText("an" if an else "aus"); b.blockSignals(False)
