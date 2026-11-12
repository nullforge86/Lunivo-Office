"""KIChat: fachlich abgegrenzte KI-Dienstlogik."""
from __future__ import annotations

import os  # noqa: F401
import threading  # noqa: F401
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal  # noqa: F401
from PySide6.QtWidgets import QMessageBox  # noqa: F401
from lunivo_writer.dienste.einstellungen_dienst import data_dir  # noqa: F401
from lunivo_writer.ki import ki as K  # noqa: F401
from lunivo_writer.ki import assistent_lauf as AL  # noqa: F401
from lunivo_writer.ki import modellfaehigkeit as MF  # noqa: F401
from lunivo_writer.ki import chat_bezug as CB  # noqa: F401
from lunivo_writer.ki import chat_antwort as CA
from lunivo_writer.editor.text import ki_markdown
from lunivo_writer.editor.dokument.zusatz import KI_AUTOR
from lunivo_writer.ki.chat_modell import ChatModell  # noqa: F401
from lunivo_writer.ki.arbeitslauf import _Lauf  # noqa: F401


class KIChatMixin:
    """Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden."""

    def chat_senden(self, text: str, bild: str | None = None) -> bool:
        """Neue Nutzernachricht in ``chat_modell`` aufnehmen und senden. False, wenn nichts gesendet wurde (leer, beschäftigt, keine Zustimmung).
        ``bild``: Pfad eines Anhangs; er wird vorher geprüft (Format, Größe), bei einem Fehler kommt die Meldung über ``status`` und nichts geht raus."""
        if (not text.strip() and not bild) or not self.dauer_verdraengen():      # der Chat hat Vorrang vor fortlaufenden Assistenten
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
        if not self.dauer_verdraengen():
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
            return CB.bezug_bauen(eing["basis"], eing["basis"] + len(eing["text"]), eing["markiert"],
                                  eing["rev"], eing["text"], id(eing["ed"]),
                                  editor_obj=eing["ed"], dokument_obj=eing.get("dokument"))
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
            doc = ed.document()
            return CB.bezug_bauen(von, bis, c.hasSelection(), doc.revision(), alt, id(ed),
                                  editor_obj=ed, dokument_obj=doc, ganz="" if c.hasSelection() else doc.toPlainText())
        except RuntimeError:
            return None

    def _bezug_lage(self, index: int):
        """(Bezug, Editor, Grund). Editor nur, wenn Bezug und aktueller Editor noch zusammenpassen."""
        bezug = self.chat_modell.bezug_von(index)
        ed = self.w.current_editor()
        try:
            doc = ed.document() if ed is not None else None
            rev = doc.revision() if doc is not None else None
        except RuntimeError:
            ed, doc, rev = None, None, None
        ok, grund = CB.bezug_pruefen(bezug, rev, id(ed) if ed is not None else None,
                                     dokument_jetzt=doc, editor_obj_jetzt=ed)
        return bezug, (ed if ok else None), grund

    def bezug_gueltig(self, index: int, ersetzen: bool = False) -> tuple[bool, str]:
        """Für die Oberfläche: darf die Antwort ``index`` jetzt eingefügt (bzw. ersetzt) werden? (ok, Grund)."""
        bezug, ed, grund = self._bezug_lage(index)
        if ed is None:
            return False, grund
        if ersetzen and not bezug["markiert"]:           # ohne Markierung: nur eine Überarbeitung des ganzen Dokuments, und nur wortweise (Formatierung bleibt)
            n = self.chat_modell.nachrichten[index]
            ganz = CB.vorher_der_nachricht(n, bezug)
            if not ganz or CB.ersetz_schritte(ganz, CA.kern_von(n)) is None:
                return False, CB.MELDUNG_OHNE_MARKIERUNG
        return True, ""

    def rezension_gueltig(self, index: int) -> tuple[bool, str]:
        """Für die Oberfläche: darf die Antwort ``index`` als nachverfolgte Änderungen eingetragen werden? (ok, Grund).
        Wie Ersetzen (``bezug_gueltig``), dazu: die Antwort ist eine wortweise Überarbeitung und der Editor kann Änderungen verfolgen."""
        ok, grund = self.bezug_gueltig(index, True)
        if not ok:
            return False, grund
        bezug, ed, _ = self._bezug_lage(index)
        alt = CB.vorher_der_nachricht(self.chat_modell.nachrichten[index], bezug)
        if not alt or CB.ersetz_schritte(alt, CA.kern_von(self.chat_modell.nachrichten[index])) is None:
            return False, CB.MELDUNG_KEINE_REZENSION
        if not hasattr(ed, "ersetze_verfolgt"):
            return False, CB.MELDUNG_OHNE_VERFOLGUNG
        return True, ""

    def antwort_vorschau(self, index: int, ersetzen: bool) -> list[tuple[str, str]]:
        """Vorschau als [(art, text)] (gleich/entfernt/neu); leer, wenn nichts anzuwenden ist."""
        ok, _ = self.bezug_gueltig(index, ersetzen)
        if not ok:
            return []
        neu = CA.kern_von(self.chat_modell.nachrichten[index])
        return CB.vorschau_stuecke(self.chat_modell.bezug_von(index)["alt"], neu) if ersetzen else CB.vorschau_einfuegen(neu)

    def antwort_diff(self, index: int) -> list[tuple[str, str]] | None:
        """Für die Oberfläche: Stücke [(art, text)] Kern gegen die beim Fragen markierte Stelle, ohne Klick; None, wenn der Bezug ungültig ist oder (ohne Markierung) die Antwort keine Überarbeitung des Dokuments ist."""
        if self._bezug_lage(index)[1] is None:          # nur Revision/Editor prüfen; die Markierung ist hier nicht nötig
            return None
        return CB.vorschau_der_nachricht(self.chat_modell.nachrichten[index], self.chat_modell.bezug_von(index))

    def antwort_index(self, nr: int | None) -> int | None:
        """Kennung (``nr``) einer Nachricht → aktueller Index im Chat; None, wenn sie nicht mehr da ist."""
        return self.chat_modell.index_von_nr(nr)

    def antwort_lage(self, index: int) -> dict:
        """Alles für das Vergleichsfenster in einem Aufruf: {gueltig, nr, vorher, nachher, stuecke, einfuegen, ersetzen, rezension}.
        ``vorher``: Stelle zum Fragezeitpunkt (Markierung, sonst ganzes Dokument bei einer Überarbeitung, sonst ""); ``nachher``: Kern der Antwort;
        ``stuecke``: wie ``antwort_diff`` (oder None); ``einfuegen``/``ersetzen``: (ok, Grund) wie ``bezug_gueltig``; ``rezension``: (ok, Grund) wie ``rezension_gueltig``.
        Kein KI-Eintrag unter ``index`` (oder Fehlernachricht): ``gueltig`` False, alles leer, nichts wird ausgelöst."""
        m = self.chat_modell.nachrichten
        if not 0 <= index < len(m) or m[index]["rolle"] != "ki" or m[index].get("fehler"):
            return {"gueltig": False, "nr": None, "vorher": "", "nachher": "", "stuecke": None,
                    "einfuegen": (False, CB.MELDUNG_KEIN_BEZUG), "ersetzen": (False, CB.MELDUNG_KEIN_BEZUG), "rezension": (False, CB.MELDUNG_KEIN_BEZUG)}
        n = m[index]
        return {"gueltig": True, "nr": n.get("nr"), "vorher": CB.vorher_der_nachricht(n, self.chat_modell.bezug_von(index)),
                "nachher": CA.kern_von(n), "stuecke": self.antwort_diff(index),
                "einfuegen": self.bezug_gueltig(index, False), "ersetzen": self.bezug_gueltig(index, True), "rezension": self.rezension_gueltig(index)}

    def antwort_einfuegen(self, index: int) -> tuple[bool, str]:
        """Antwort ``index`` hinter der gemerkten Stelle einfügen (ein Schritt für Rückgängig). → (ok, Meldung); bei Ablehnung wird nichts geändert."""
        return self._antwort_anwenden(index, False)

    def antwort_ersetzen(self, index: int) -> tuple[bool, str]:
        """Die beim Fragen markierte Stelle durch die Antwort ersetzen (ein Schritt); ohne Markierung das ganze Dokument, wenn die Antwort es überarbeitet. Nur bei unverändertem Text. → (ok, Meldung)."""
        return self._antwort_anwenden(index, True)

    def antwort_rezension(self, index: int) -> tuple[bool, str]:
        """Die Überarbeitung als nachverfolgte Änderungen (Autor „KI“) eintragen: Altes bleibt durchgestrichen stehen, Neues ist markiert (ein Schritt für Rückgängig).
        Der Nutzer nimmt jede Änderung danach einzeln an oder lehnt sie ab. Nur für wortweise Überarbeitungen. → (ok, Meldung); bei Ablehnung wird nichts geändert."""
        return self._antwort_anwenden(index, True, rezension=True)

    def _antwort_anwenden(self, index: int, ersetzen: bool, rezension: bool = False) -> tuple[bool, str]:
        ok, grund = self.rezension_gueltig(index) if rezension else self.bezug_gueltig(index, ersetzen)
        if not ok:
            return False, grund
        bezug, ed, _ = self._bezug_lage(index)
        neu = CA.kern_von(self.chat_modell.nachrichten[index])
        if not ersetzen:
            von, bis, alt = bezug["bis"], bezug["bis"], ""
        elif bezug["markiert"]:
            von, bis, alt = bezug["von"], bezug["bis"], bezug["alt"]
        else:                                          # ganzes Dokument (von ``bezug_gueltig`` nur für Überarbeitungen freigegeben)
            von, bis, alt = 0, ed.document().characterCount() - 1, bezug.get("ganz") or ""
        from PySide6.QtGui import QTextCursor
        try:
            sperre = QTextCursor(ed.document())
            sperre.beginEditBlock()
            try:
                schritte = CB.ersetz_schritte(alt, neu) if ersetzen else None
                if schritte is None:               # Einfügen oder ganz anderer Text: die Stelle als Ganzes
                    geklappt = ed.replace_range(von, bis, neu, erwartet=alt, markdown=ki_markdown.hat_struktur(neu))
                else:                              # Überarbeitung: nur die geänderten Wörter tauschen, die Formatierung des Dokuments bleibt
                    pruef = QTextCursor(ed.document()); pruef.setPosition(von); pruef.setPosition(bis, QTextCursor.KeepAnchor)
                    geklappt = pruef.selectedText().replace("\u2029", "\n") == alt
                    if geklappt:
                        for a, b, t in schritte:                       # von hinten nach vorn: die Stellen davor verschieben sich nicht
                            if rezension:
                                ed.ersetze_verfolgt(von + a, von + b, t, KI_AUTOR)
                            else:
                                ed.replace_range(von + a, von + b, t)
            finally:
                sperre.endEditBlock()
        except RuntimeError:                       # Tab/Editor wurde geschlossen
            return False, CB.MELDUNG_EDITOR
        if not geklappt:
            return False, CB.MELDUNG_GEAENDERT
        self.assistant.pruefen()
        if rezension:
            return True, CB.MELDUNG_REZENSION
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
        def teil_senden(text: str) -> None:
            try:
                self._sig.teil.emit(kennung, text)
            except RuntimeError:
                abbruch.set()                         # Oberfläche wurde geschlossen; Stream abbrechen

        self._pool.start(_Lauf(("chat", {"anfrage": kennung}),
                               lambda: self.ki.chat(verlauf, doc, markiert, teil_senden, abbruch), self._sig))

    def _chat_teil(self, kennung: int, text: str) -> None:
        if self.chat_modell.teil_setzen(kennung, text):
            self.chatTeil.emit()
