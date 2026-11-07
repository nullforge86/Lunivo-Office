"""KIChat: fachlich abgegrenzte KI-Dienstlogik."""
from __future__ import annotations

import os  # noqa: F401
import threading  # noqa: F401
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal  # noqa: F401
from PySide6.QtWidgets import QMessageBox  # noqa: F401
from lunivo_writer.services.settings_service import data_dir  # noqa: F401
from lunivo_writer.ai import ki as K  # noqa: F401
from lunivo_writer.ai import assistent_lauf as AL  # noqa: F401
from lunivo_writer.ai import modellfaehigkeit as MF  # noqa: F401
from lunivo_writer.ai import chat_bezug as CB  # noqa: F401
from lunivo_writer.ai.chat_modell import ChatModell  # noqa: F401
from lunivo_writer.ai.arbeitslauf import _Lauf  # noqa: F401


class KIChatMixin:
    """Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden."""

    def chat_senden(self, text: str, bild: str | None = None) -> bool:
        """Neue Nutzernachricht in ``chat_modell`` aufnehmen und senden. False, wenn nichts gesendet wurde (leer, beschäftigt, keine Zustimmung).
        ``bild``: Pfad eines Anhangs; er wird vorher geprüft (Format, Größe), bei einem Fehler kommt die Meldung über ``status`` und nichts geht raus."""
        if (not text.strip() and not bild) or self._arbeit_laeuft:
            return False
        bilder = None
        if bild:
            p = MF.bild_pruefen(bild)
            if "fehler" in p:
                self.status.emit(p["fehler"])
                return False
            if not self.kann_bild():
                self.status.emit(self.bild_hinweis())
                return False
            if not self._einwilligung(self.ki.modell("chatbot"), "bild"):      # der Bildinhalt verlässt den Rechner: eigene Einwilligung
                return False
            bilder = [p]
        return self._chat_anfragen(lambda b: self.chat_modell.anfrage(text.strip(), bilder, b))

    # ---- Chat-Einstellungen fürs Menü (Quelle: ``konfig.chat_optionen()``; Änderungen lösen ``geaendert`` aus)

    def denktiefe(self) -> str:
        return MF.denkstufe(self.konfig.chat_optionen().get("denktiefe"))

    def denktiefe_setzen(self, stufe: str) -> bool:
        if stufe not in MF.DENKSTUFEN:
            return False
        self.konfig.chat_setzen(denktiefe=stufe)            # dauerhaft
        self.geaendert.emit()
        return True

    def werkzeugmodus(self) -> str:
        return self.konfig.chat_optionen().get("werkzeuge", "fragen")

    def werkzeugmodus_setzen(self, modus: str) -> bool:
        """„fragen“ oder „automatisch“. „automatisch“ gilt nur für diese Sitzung (``KIKonfig.speichern`` schreibt es nie) und nur für Lesen und
        Schreiben; Löschen, Netzwerk, Unbekanntes, der Programmstart und die Datenschutz-Einwilligung fragen weiter."""
        if modus not in MF.WERKZEUG_MODI:
            return False
        self.konfig.d["chat"] = {**(self.konfig.d.get("chat") or {}), "werkzeuge": modus}      # nur im Speicher
        self.geaendert.emit()
        return True

    def kann_bild(self) -> bool:
        return self.ki.kann_bild()

    def kann_denken(self) -> bool:
        return self.ki.kann_denken()

    def werkzeuge_vorhanden(self) -> bool:
        """MCP-Server an UND ein Modell, das Werkzeuge im Chat nutzt (Ollama oder eigener Anbieter, nicht Claude)."""
        an = any(m.get("an") and m.get("befehl") for m in self.konfig["mcp"])
        return an and self.ki.modell("chatbot").startswith((K.OLLAMA_MARKE, K.EIGEN_MARKE))

    def bild_hinweis(self) -> str:
        m = self.ki.modell("chatbot")
        if self.kann_bild():
            return "Bild anhängen (PNG, JPEG oder WebP, bis 5 MB)."
        if m.startswith(K.OLLAMA_MARKE):
            return "Dieses Modell kann keine Bilder, oder Ollama hat es noch nicht gemeldet. Ein Modell mit Bildverständnis wählen."
        if m.startswith(K.EIGEN_MARKE):
            return "Dieser Anbieter ist nicht als „Visuelle Analyse“ eingetragen. In den KI-Einstellungen das Etikett setzen."
        return "Das gewählte Modell kann keine Bilder."

    def denken_hinweis(self) -> str:
        if self.kann_denken():
            return "Wie gründlich das Modell nachdenkt. „Automatisch“ lässt es beim Bisherigen."
        return "Das gewählte Modell denkt nicht nach oder meldet es nicht."

    def werkzeuge_hinweis(self) -> str:
        if self.werkzeuge_vorhanden():
            return "Automatisch gilt nur für Lesen und Schreiben und nur in dieser Sitzung; Löschen und Netzwerk fragen immer."
        if not any(m.get("an") and m.get("befehl") for m in self.konfig["mcp"]):
            return "Kein KI-Werkzeug (MCP-Server) eingeschaltet."
        return "Claude nutzt im Chat keine Werkzeuge. Ollama oder einen eigenen Anbieter wählen."

    def chat_wiederholen(self) -> bool:
        """Die letzte Nutzernachricht erneut senden; die davorliegende Antwort/der Fehler fällt weg."""
        if self._arbeit_laeuft:
            return False
        text = self.chat_modell.wiederholen()
        self.chatGeaendert.emit()
        bilder = self.chat_modell.wiederhol_bilder
        return bool(text or bilder) and self.chat_senden(text, bilder[0]["pfad"] if bilder else None)

    def chat_neu(self) -> None:
        self.chat_modell.neues_gespraech()
        self.chatGeaendert.emit()

    def chat_abbrechen(self) -> None:
        """Eine laufende Antwort wird nicht mehr angezeigt. Der Hintergrundfaden selbst lässt sich im Thread-Pool nicht unterbrechen und läuft aus."""
        self._chat_abbruch.set()                   # streamende Verbindung wird sofort geschlossen
        self.chat_modell.abbrechen()
        self.chatGeaendert.emit()

    @staticmethod
    def _aktion_bezug(eing: dict) -> dict | None:
        """Bezug einer Aktion aus ihrer Eingabe (Editor, Text, Basis, Revision zum Start); ganzes Dokument: Einfügen am Ende, kein Ersetzen."""
        try:
            return CB.bezug_bauen(eing["basis"], eing["basis"] + len(eing["text"]), eing["markiert"], eing["rev"], eing["text"], id(eing["ed"]))
        except (KeyError, TypeError):
            return None

    def aktion_in_chat(self, name: str, text: str, cent, bezug=None) -> None:
        self.chat_modell.aktion(name, text, cent, bezug)
        self.chatGeaendert.emit()

    def _chat_anfragen(self, aufnehmen) -> bool:
        if not self._chat_bereit():                      # Zustimmungen zuerst: ohne sie wird nichts aufgenommen
            return False
        kennung = aufnehmen(self.chat_bezug())
        self.chatGeaendert.emit()
        self._chat_los(self.chat_modell.verlauf(), kennung)
        return True

    # ---- Antwort ins Dokument (EIN Weg: Schaltflächen und Option „direkt einfügen“)

    def chat_bezug(self) -> dict | None:
        """Stelle im Text zum SENDEZEITPUNKT: Markierung (markiert=True) oder Schreibmarke; None ohne Editor. Nur im Speicher."""
        ed = self.w.current_editor()
        if ed is None:
            return None
        try:
            c = ed.textCursor()
            alt = c.selectedText().replace("\u2029", "\n") if c.hasSelection() else ""
            von, bis = (min(c.anchor(), c.position()), max(c.anchor(), c.position())) if c.hasSelection() else (c.position(),) * 2
            return CB.bezug_bauen(von, bis, c.hasSelection(), ed.document().revision(), alt, id(ed))
        except RuntimeError:
            return None

    def _bezug_lage(self, index: int):
        """(Bezug, Editor, Grund). Editor nur, wenn Bezug und aktueller Editor noch zusammenpassen."""
        bezug = self.chat_modell.bezug_von(index)
        ed = self.w.current_editor()
        try:
            rev = ed.document().revision() if ed is not None else None
        except RuntimeError:
            ed, rev = None, None
        ok, grund = CB.bezug_pruefen(bezug, rev, id(ed) if ed is not None else None)
        return bezug, (ed if ok else None), grund

    def bezug_gueltig(self, index: int, ersetzen: bool = False) -> tuple[bool, str]:
        """Für die Oberfläche: darf die Antwort ``index`` jetzt eingefügt (bzw. ersetzt) werden? (ok, Grund)."""
        bezug, ed, grund = self._bezug_lage(index)
        if ed is None:
            return False, grund
        if ersetzen and not bezug["markiert"]:
            return False, CB.MELDUNG_OHNE_MARKIERUNG
        return True, ""

    def antwort_vorschau(self, index: int, ersetzen: bool) -> list[tuple[str, str]]:
        """Vorschau als [(art, text)] (gleich/entfernt/neu); leer, wenn nichts anzuwenden ist."""
        ok, _ = self.bezug_gueltig(index, ersetzen)
        if not ok:
            return []
        neu = self.chat_modell.nachrichten[index]["text"]
        return CB.vorschau_stuecke(self.chat_modell.bezug_von(index)["alt"], neu) if ersetzen else CB.vorschau_einfuegen(neu)

    def antwort_einfuegen(self, index: int) -> tuple[bool, str]:
        """Antwort ``index`` hinter der gemerkten Stelle einfügen (ein Schritt für Rückgängig). → (ok, Meldung); bei Ablehnung wird nichts geändert."""
        return self._antwort_anwenden(index, False)

    def antwort_ersetzen(self, index: int) -> tuple[bool, str]:
        """Die beim Fragen markierte Stelle durch die Antwort ersetzen (ein Schritt). Nur bei unverändertem Text. → (ok, Meldung)."""
        return self._antwort_anwenden(index, True)

    def _antwort_anwenden(self, index: int, ersetzen: bool) -> tuple[bool, str]:
        ok, grund = self.bezug_gueltig(index, ersetzen)
        if not ok:
            return False, grund
        bezug, ed, _ = self._bezug_lage(index)
        neu = self.chat_modell.nachrichten[index]["text"]
        von, bis, alt = (bezug["von"], bezug["bis"], bezug["alt"]) if ersetzen else (bezug["bis"], bezug["bis"], "")
        from PySide6.QtGui import QTextCursor
        try:
            sperre = QTextCursor(ed.document())
            sperre.beginEditBlock()
            try:
                geklappt = ed.replace_range(von, bis, neu, erwartet=alt)
            finally:
                sperre.endEditBlock()
        except RuntimeError:                       # Tab/Editor wurde geschlossen
            return False, CB.MELDUNG_EDITOR
        if not geklappt:
            return False, CB.MELDUNG_GEAENDERT
        self.assistant.pruefen()
        return True, ("Ersetzt." if ersetzen else "Eingefügt.") + " Strg+Z macht es rückgängig."

    def _chat_bereit(self) -> bool:
        """Modell da und Zustimmungen erteilt? Bei Markierung gilt der Umfang „auszug“, sonst „dokument“ (die Sperre an der Sendestelle bleibt)."""
        auswahl = self.kontext()[0]
        if self._arbeit_laeuft or not self.verfuegbar() or not self._einwilligung(None, "auszug" if auswahl else "dokument", 12000):
            if not self.verfuegbar():
                self.status.emit("Der Chat braucht einen KI-Schlüssel — oder Ollama. Optionen ▸ Schreibhilfe und KI.")
            return False
        ziel = self.ki.websuche_ziel()
        if ziel and not self.konfig.hat_einwilligung(ziel, "auszug"):
            if QMessageBox.question(self.w, "Frage an die Websuche senden?",
                                    f"Für die Antwort wird Ihre Frage an „{ziel}“ im Internet gesendet.\n\nErlauben Sie das? "
                                    "Widerrufen können Sie es in den KI-Einstellungen unter Datenschutz.") == QMessageBox.Yes:
                self.konfig.einwilligung_geben(ziel, "auszug")
        return True

    def _chat_los(self, verlauf: list, kennung: int) -> None:
        """Kontext des Chats: die Markierung, wenn es eine gibt (weniger Text verlässt den Rechner), sonst das Dokument."""
        ed = self.w.current_editor()
        c = ed.textCursor() if ed else None
        markiert = bool(c is not None and c.hasSelection())
        doc = c.selectedText().replace("\u2029", "\n") if markiert else (ed.document().toPlainText() if ed else "")
        self._arbeit_laeuft = True
        self.laeuft.emit(True)
        self._chat_abbruch = abbruch = threading.Event()
        self._pool.start(_Lauf(("chat", {"anfrage": kennung}),
                               lambda: self.ki.chat(verlauf, doc, markiert, lambda t: self._sig.teil.emit(kennung, t), abbruch), self._sig))

    def _chat_teil(self, kennung: int, text: str) -> None:
        if self.chat_modell.teil_setzen(kennung, text):
            self.chatTeil.emit()
