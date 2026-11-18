"""Vorher/Nachher-Fenster einer KI-Antwort in der Seitenleiste (Einfügen, Ersetzen, Kopieren).

Eine Spalte in voller Breite: „Vorher“ (entfernte Stellen markiert) und „Nachher“ (neue Stellen markiert, Kopieren rechts in der Zeile), beide als
``AenderungsVorschau`` und gleich hoch; unten angeheftet die Knopfzeile (Schließen, Einfügen, Als Rezension, Ersetzen) mit dem Grund, falls etwas nicht geht.
Alles Fachliche liefert der Dienst (``antwort_lage``, ``antwort_einfuegen``, ``antwort_ersetzen``, ``antwort_rezension``); das Fenster liest den Zustand bei
``chatGeaendert``/``kontextGeaendert`` neu und hält keine Widgets der Chat-Blase."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import text_label
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_KLEIN, ABSTAND_NORMAL, AENDERUNG_FELD_MIN, PANEL_HOEHE_ABZUG, RAND_KEIN
from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_label
from lunivo_writer.oberflaeche.baukasten.basis.zwischenablage import in_zwischenablage
from lunivo_writer.oberflaeche.baukasten.chat.chat_blase import SymbolKnopf
from lunivo_writer.oberflaeche.baukasten.dokument.aenderungs_vorschau import AenderungsVorschau
from lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen import PANEL_INHALT_RAND
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig

TITEL_AENDERUNG = "Änderung der KI"
TITEL_VORHER, TITEL_NACHHER = "Vorher", "Nachher"
TEXT_SCHLIESSEN, TEXT_EINFUEGEN, TEXT_ERSETZEN, TEXT_KOPIEREN = "Schließen", "Einfügen", "Ersetzen", "Nachher-Text kopieren"
TEXT_REZENSION = "Als Rezension"
TIPP_REZENSION = "Als nachverfolgte Änderungen eintragen – danach im Reiter „Überprüfen“ einzeln annehmen oder ablehnen"
HAUPTKNOPF = "optFertig"                                   # Objektname des gefüllten Hauptknopfs, siehe ``oberflaeche/thema.py``
TEXT_ANTWORT_WEG = "Diese Antwort steht nicht mehr im Gespräch."


class AenderungsFenster(PanelFaehig, QDialog):
    """``dienst``: der KI-Dienst; ``nr``: Kennung der Chat-Nachricht (nicht der Index). Aktueller Stand: ``self.lage()`` (= ``dienst.antwort_lage``),
    ``self.index()`` ist None, sobald die Antwort nicht mehr im Gespräch ist."""

    def __init__(self, dienst, nr: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TITEL_AENDERUNG)
        self.d, self.nr = dienst, nr
        self._stand = None
        self._nachher = ""
        v = QVBoxLayout(self); v.setContentsMargins(*PANEL_INHALT_RAND); v.setSpacing(ABSTAND_KLEIN)
        self.vorher_bereich, self.vorher = self._bereich(v, TITEL_VORHER)
        self.nachher_bereich, self.nachher = self._bereich(v, TITEL_NACHHER, kopieren=True)
        self.hinweis = hinweis_label("", klein=True); self.hinweis.hide()
        v.addWidget(self.hinweis)
        self.einfuegen = QPushButton(TEXT_EINFUEGEN)
        self.rezension = QPushButton(TEXT_REZENSION)
        self.knoepfe = knopfzeile(self, self.einfuegen, self.rezension, ok_text=TEXT_ERSETZEN, abbrechen_text=TEXT_SCHLIESSEN, bei_ok=self._ersetzen)
        self.ersetzen = self.knoepfe.ok
        self.ersetzen.setObjectName(HAUPTKNOPF)                # gefüllter Hauptknopf in Akzentfarbe (Regel im Thema)
        self.einfuegen.clicked.connect(self._einfuegen)
        self.rezension.clicked.connect(self._rezension)
        v.addWidget(self.knoepfe)                              # die Seitenleiste heftet die Knopfzeile unten an
        self.d.chatGeaendert.connect(self.neu_lesen)
        self.d.kontextGeaendert.connect(self.neu_lesen)
        self.finished.connect(self._trennen)
        self.neu_lesen()

    def _bereich(self, v: QVBoxLayout, titel: str, *, kopieren: bool = False):
        """Überschrift (bei ``kopieren`` mit Kopier-Symbol rechts in derselben Zeile) und darunter das Feld, das den freien Platz teilt."""
        box = QWidget(); bv = QVBoxLayout(box); bv.setContentsMargins(*RAND_KEIN); bv.setSpacing(ABSTAND_NORMAL)
        z = QHBoxLayout(); z.setContentsMargins(*RAND_KEIN)
        z.addWidget(text_label(titel, fett=True, umbruch=False)); z.addStretch(1)      # wie in der Vorlage: fette Überschrift in normaler Schreibweise
        if kopieren:
            z.addWidget(SymbolKnopf("copy", TEXT_KOPIEREN, lambda: in_zwischenablage(self._nachher)))
        bv.addLayout(z)
        feld = AenderungsVorschau(frei=True); feld.setMinimumHeight(AENDERUNG_FELD_MIN); feld.setAccessibleName(titel)
        bv.addWidget(feld, 1)
        v.addWidget(box, 1)
        return box, feld

    def passe_an(self, _breite: int, hoehe: int) -> None:
        """Die Seite nimmt die ganze Höhe der Seitenleiste; die beiden Felder teilen sich, was Überschriften und Knöpfe übrig lassen."""
        self.setMinimumHeight(hoehe - PANEL_HOEHE_ABZUG)

    def index(self) -> int | None:
        return self.d.antwort_index(self.nr)

    def lage(self) -> dict:
        i = self.index()
        return self.d.antwort_lage(i if i is not None else -1)

    # ---- Zustand -> Anzeige
    def neu_lesen(self) -> None:
        """Zustand des Dienstes neu lesen: Texte, Knöpfe, Hinweis. Ist die Antwort nicht mehr im Gespräch, sind die Aktionen gesperrt."""
        lage = self.lage()
        if not lage["gueltig"]:
            self.einfuegen.setEnabled(False); self.ersetzen.setEnabled(False); self.rezension.setEnabled(False)
            self._hinweis(TEXT_ANTWORT_WEG)
            return
        stuecke = lage["stuecke"]
        stand = (lage["vorher"], lage["nachher"], repr(stuecke))
        if stand != self._stand:
            self._stand, self._nachher = stand, lage["nachher"]
            if stuecke:
                vor = [s for s in stuecke if s[0] != "neu"]
                nach = [s for s in stuecke if s[0] != "entfernt"]
            else:
                vor = [("gleich", lage["vorher"])] if lage["vorher"] else []
                nach = [("gleich", lage["nachher"])]
            self.vorher.stuecke_setzen(vor); self.nachher.stuecke_setzen(nach)
            self.vorher_bereich.setVisible(any(t for _a, t in vor))
        gruende: list[str] = []
        for knopf, (ok, grund) in ((self.ersetzen, lage["ersetzen"]), (self.einfuegen, lage["einfuegen"])):
            knopf.setEnabled(ok); knopf.setToolTip("" if ok else grund)
            if not ok and grund and grund not in gruende:
                gruende.append(grund)
        rez_ok, rez_grund = lage.get("rezension", (False, ""))       # nur bei einer Überarbeitung; der Grund steht im Tooltip, nicht in der Hinweiszeile
        self.rezension.setEnabled(rez_ok); self.rezension.setToolTip(TIPP_REZENSION if rez_ok else rez_grund)
        self._hinweis("\n".join(gruende))

    def _hinweis(self, text: str) -> None:
        self.hinweis.setText(text); self.hinweis.setVisible(bool(text))

    def _trennen(self, *_) -> None:
        for signal in (self.d.chatGeaendert, self.d.kontextGeaendert):
            try:
                signal.disconnect(self.neu_lesen)
            except (RuntimeError, TypeError):
                pass

    # ---- Aktionen
    def _einfuegen(self) -> None:
        self._anwenden(self.d.antwort_einfuegen)

    def _ersetzen(self) -> None:
        self._anwenden(self.d.antwort_ersetzen)

    def _rezension(self) -> None:
        self._anwenden(self.d.antwort_rezension)

    def _anwenden(self, aktion) -> None:
        i = self.index()
        if i is None:
            self.neu_lesen()
            return
        ok, meldung = aktion(i)
        if ok:
            self.accept()
            return
        self.neu_lesen()
        if meldung:
            self._hinweis(meldung)
