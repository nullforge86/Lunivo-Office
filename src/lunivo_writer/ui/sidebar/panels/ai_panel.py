"""KI-Chat in der Seitenleiste (Bereich „KI“): nur Verdrahtung — Zustand und Logik liegen im Dienst (``dienst.chat_modell``), die Bausteine in ``ui/baukasten/chat_*.py``."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from lunivo_writer.editor.text import ki_markdown
from lunivo_writer.ui.baukasten.chat.chat_blase import FehlerKarte, KiBlase, NutzerBlase
from lunivo_writer.ui.baukasten.chat.chat_eingabe import ChatEingabe, ChatEingabeKasten      # ChatEingabe bleibt hier importierbar
from lunivo_writer.ui.baukasten.chat.chat_leerzustand import ChatLeerzustand
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_KLEIN, ABSTAND_MITTEL, RAND_KEIN
from lunivo_writer.ui.baukasten.geruest.panel_rahmen import PanelRahmen, rollflaeche
from lunivo_writer.ui.baukasten.basis.texte import hinweis_label


class ChatPanel(QWidget):
    """KI-Chat: Kopf (Neues Gespräch, Verlauf, KI-Einstellungen, Schließen), darunter je nach Phase Leerzustand mit Chips oder Nachrichten, Eingabekasten (mit Befehlen, Modell, Fußzeile). Ohne verbundenes Modell steht der Hinweis „KI-Modell verbinden“ mit dem Weg zu den KI-Einstellungen, die Eingabe ist gesperrt."""
    zurueck = Signal()

    def __init__(self, dienst, fenster):
        super().__init__()
        self.d, self.w = dienst, fenster
        self._phase = "leer"
        aussen = QVBoxLayout(self); aussen.setContentsMargins(*RAND_KEIN); aussen.setSpacing(0)
        rahmen = PanelRahmen("KI-Chat", knoepfe=(("plus", "Neues Gespräch", self._neu), ("clock", "Verlauf", lambda: None),
                                                 ("settings", "KI-Einstellungen", self._einstellungen)))
        rahmen.schliessen.connect(self.zurueck.emit)
        self.neu_knopf, self.verlauf_knopf = rahmen.knoepfe[0], rahmen.knoepfe[1]
        self.verlauf_menue = MenueListe(self.verlauf_knopf)
        self.verlauf_menue.aboutToShow.connect(self._verlauf_fuellen)
        self.verlauf_knopf.menue_setzen(self.verlauf_menue, geteilt=False)
        aussen.addWidget(rahmen)
        v = rahmen.inhalt
        # Hinweis, solange kein Modell verbunden ist
        self.hinweis = QWidget()
        hv = QVBoxLayout(self.hinweis); hv.setContentsMargins(*RAND_KEIN)
        hv.addWidget(hinweis_label("KI-Modell verbinden, um den KI-Chat zu aktivieren"))
        hb = QPushButton("KI-Einstellungen …"); hb.clicked.connect(self._einstellungen)
        hv.addWidget(hb, 0, Qt.AlignLeft)
        v.addWidget(self.hinweis)
        # Leerzustand (Chips) oder Nachrichten
        self.leerzustand = ChatLeerzustand(dienst)
        self.leerzustand.gewaehlt.connect(lambda t: self.eingabe.setText(t))
        v.addWidget(self.leerzustand, 1)
        self.blasen = QVBoxLayout(); self.blasen.setAlignment(Qt.AlignTop); self.blasen.setSpacing(ABSTAND_MITTEL)
        host = QWidget(); host.setLayout(self.blasen)
        self.scroll = rollflaeche(host)
        v.addWidget(self.scroll, 1)
        # Eingabe
        self.eingabezeile = QWidget()
        ev = QVBoxLayout(self.eingabezeile); ev.setContentsMargins(*RAND_KEIN); ev.setSpacing(ABSTAND_KLEIN)
        self.eingabe = ChatEingabeKasten(dienst)
        self.eingabe.senden.connect(self._senden)
        self.eingabe.bild.connect(self._bild)
        self.eingabe.meldung.connect(self._melden)
        self.eingabe.stopp.connect(dienst.chat_abbrechen)
        self.eingabe.neue_aktion.connect(lambda: self.w.befehle.tun("w.schnelleAktionErstellen"))
        self.eingabe.neuer_assistent.connect(lambda: self.w.befehle.tun("w.kiAssistentErstellen"))
        ev.addWidget(self.eingabe)
        v.addWidget(self.eingabezeile)
        dienst.chatGeaendert.connect(self.anzeige)
        dienst.chatTeil.connect(self._teil_zeigen)
        dienst.kontextGeaendert.connect(self._kontext)
        dienst.laeuft.connect(lambda _an: self.zustand())
        dienst.geaendert.connect(self._geaendert)
        self.anzeige()

    # ---- Zustand -> Anzeige
    def _geaendert(self) -> None:
        """KI-Einstellungen oder Modell geändert: Modellfeld, Chips und Zustand neu lesen."""
        self.eingabe.modelle_neu()
        self.leerzustand.neu_aufbauen()
        self.zustand()

    def _kontext(self) -> None:
        """Markierung oder Dokumentinhalt haben sich geändert: Chips neu, Ersetzen-Knöpfe nachziehen."""
        self.leerzustand.neu_aufbauen()
        self.zustand()
        for i in range(self.blasen.count()):
            w = self.blasen.itemAt(i).widget()
            if isinstance(w, KiBlase):
                w.kontext_neu()

    def zustand(self) -> None:
        """Verbunden ja/nein, Phase und Beschäftigung bestimmen, was sichtbar und bedienbar ist."""
        verbunden = self.d.kontext()[2]
        phase = self.d.chat_modell.phase
        self.hinweis.setVisible(not verbunden)
        self.leerzustand.setVisible(phase == "leer")
        self.scroll.setVisible(phase != "leer")
        self.neu_knopf.setVisible(phase != "leer")
        self.verlauf_knopf.setEnabled(True)
        self.eingabe.zustand_setzen(verbunden, self.d.chat_beschaeftigt)

    def anzeige(self) -> None:
        """Nachrichten aus ``dienst.chat_modell`` neu aufbauen."""
        m = self.d.chat_modell
        while self.blasen.count():
            it = self.blasen.takeAt(0)
            w = it.widget()
            if w is not None:
                w.hide(); w.setParent(None); w.deleteLater()
        for i, n in enumerate(m.nachrichten):
            if n["rolle"] == "mensch":
                b = NutzerBlase(n["text"], n.get("bilder")); b.inEingabe.connect(self.eingabe.setText)
            elif n.get("fehler"):
                b = FehlerKarte(self.d, n["fehler"]); b.einstellungen.connect(self._einstellungen)
            else:
                b = KiBlase(self.d, n["text"], n.get("cent"), i); b.meldung.connect(self._melden)
            self.blasen.addWidget(b)
        self._teil_label = None
        if m.phase == "laufend":
            self._teil_label = hinweis_label(m.teil or "Die KI schreibt …", klein=not m.teil)
            self._teil_label.setWordWrap(True)
            self._teil_label_format(m.teil)
            self.blasen.addWidget(self._teil_label)
        if self._phase == "laufend" and m.phase == "bereit" and self.d.konfig.chat_optionen()["direkt"]:
            ok, meldung = self.d.antwort_einfuegen(len(m.nachrichten) - 1)           # Option „direkt ins Dokument einfügen“ (derselbe Weg wie der Knopf)
            if not ok:
                self._melden(meldung)
        self._phase = m.phase
        self.zustand()
        QTimer.singleShot(0, self._zum_ende_scrollen)

    def _zum_ende_scrollen(self) -> None:
        """Scrollt nach dem Neuaufbau nach unten, sofern das Panel noch existiert."""
        try:
            scrollbar = self.scroll.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except RuntimeError:
            # Das Panel bzw. seine Qt-Scrollfläche kann vor dem Timer gelöscht sein.
            return

    def _teil_label_format(self, teil: str) -> None:
        """Streaming-Text wie die fertige Antwort: mit Struktur als Markdown (Qt, ``ki_markdown``), sonst einfacher Text — nie Markup."""
        lb = self._teil_label
        if teil and ki_markdown.hat_struktur(teil):
            lb.setTextFormat(Qt.MarkdownText); lb.setText(ki_markdown.normalisieren(teil))
        else:
            lb.setTextFormat(Qt.PlainText); lb.setText(teil or "Die KI schreibt …")

    def _teil_zeigen(self) -> None:
        """Streaming: nur das Textfeld der laufenden Antwort nachziehen — kein Neuaufbau aller Blasen."""
        lb = getattr(self, "_teil_label", None)
        if lb is None or self.d.chat_modell.phase != "laufend":
            return
        try:
            self._teil_label_format(self.d.chat_modell.teil)
        except RuntimeError:
            self._teil_label = None
            return
        try:
            sb = self.scroll.verticalScrollBar()
            if sb.value() >= sb.maximum() - 40:
                sb.setValue(sb.maximum())
        except RuntimeError:
            # Das Panel oder seine Scrollfläche kann während des Streamings verschwinden.
            self._teil_label = None
            return

    # ---- Aktionen
    def _verlauf_fuellen(self) -> None:
        self.verlauf_menue.clear()
        for i, g in enumerate(self.d.chat_modell.gespraeche):
            self.verlauf_menue.eintrag(g["titel"], lambda i=i: self._gespraech(i))
        if not self.d.chat_modell.gespraeche:
            self.verlauf_menue.eintrag("Noch keine früheren Gespräche", aktiv=False)

    def _gespraech(self, index: int) -> None:
        if self.d.chat_modell.gespraech_laden(index):
            self._phase = self.d.chat_modell.phase
            self.d.chatGeaendert.emit()

    def _neu(self) -> None:
        self.eingabe.anhang_entfernen()
        self.d.chat_neu()

    def _einstellungen(self) -> None:
        self.w.befehle.tun("w.kiEinstellungen")             # derselbe Befehl wie in Band und Schreibhilfe, kein zweites Öffnen
        self.d.geaendert.emit()

    def _melden(self, text: str) -> None:
        self.w.lbl_msg.setText(text)

    def _senden(self, text: str) -> None:
        if self.d.chat_senden(text, self.eingabe.anhang()):
            self.eingabe.leeren()

    def _bild(self, text: str) -> None:
        self.eingabe.leeren()
        self.d.bild_aus_text(text or None)
