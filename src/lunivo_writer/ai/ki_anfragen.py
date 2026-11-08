"""KIAnfragen: fachlich abgegrenzte KI-Dienstlogik."""
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


class KIAnfragenMixin:
    """Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden."""

    def _werkzeug_erlaubt(self, name: str, argumente: dict, server: str, art: str = "unbekannt") -> bool:
        """Aus dem Arbeitsfaden: fragt im Hauptfenster, ob die KI das Werkzeug aufrufen darf, und wartet auf die Antwort.
        Jeder Aufruf wird einzeln gefragt, mit allen Angaben; ohne Antwort in fünf Minuten gilt: nicht erlaubt."""
        import json
        import threading
        self._antwort_ereignis = threading.Event()
        self._werkzeug_ok = False
        self.werkzeugFrage.emit(name, json.dumps(argumente, ensure_ascii=False, indent=1)[:20000], f"{server}\x1f{art}")
        self._antwort_ereignis.wait(300)
        return self._werkzeug_ok

    def _werkzeug_fragen(self, name: str, argumente: str, server_art: str) -> None:
        server, _s, art = server_art.partition("\x1f")
        if name == "\x00start":
            k = QMessageBox(QMessageBox.Warning, "KI-Werkzeug starten?",
                            f"Für die Antwort soll das Programm des KI-Werkzeugs „{server}“ (MCP-Server) auf diesem Rechner gestartet werden.\n\n"
                            f"Befehl:\n{argumente}\n\nDas Programm läuft mit Ihren Rechten. Jeder Werkzeugaufruf wird danach einzeln gefragt. Starten?",
                            QMessageBox.Yes | QMessageBox.No, self.w)
            k.setDefaultButton(QMessageBox.No)
            self._werkzeug_ok = k.exec() == QMessageBox.Yes
            self._antwort_ereignis.set()
            return
        warnung = {"löschen": "Löschen von Daten", "schreiben": "Schreiben oder Ändern", "netzwerk": "Zugriff auf das Netzwerk",
                   "lesen": "Lesen", "unbekannt": "unbekannte Wirkung"}.get(art, "unbekannte Wirkung")
        k = QMessageBox(QMessageBox.Question, "Werkzeug aufrufen?",
                        f"Die KI möchte das Werkzeug „{name}“ des KI-Werkzeugs „{server}“ aufrufen.\n\nArt der Aktion: {warnung}\n\nErlauben?",
                        QMessageBox.Yes | QMessageBox.No, self.w)
        k.setDefaultButton(QMessageBox.No)
        k.setDetailedText("Alle Angaben des Aufrufs:\n" + argumente)
        self._werkzeug_ok = k.exec() == QMessageBox.Yes
        self._antwort_ereignis.set()

    def _server_erlaubt(self, name: str, befehl: str) -> bool:
        """Aus dem Arbeitsfaden: zeigt den vollständigen Startbefehl des MCP-Servers und fragt vor dem Start (ein Programm auf diesem Rechner)."""
        import threading
        self._antwort_ereignis = threading.Event()
        self._werkzeug_ok = False
        self.werkzeugFrage.emit("\x00start", befehl, f"{name}\x1fstart")
        self._antwort_ereignis.wait(300)
        return self._werkzeug_ok

    def _hinweis_fenster(self, titel: str, text: str) -> None:
        """Ein Hinweis, den man nicht übersehen kann (statt nur einer Zeile in der Statusleiste)."""
        self.status.emit(text)
        QMessageBox.information(self.w, titel, text)

    def merke_ergebnis(self, titel: str, text: str, vorlage: str = "") -> None:
        import time
        self.ergebnisse.append({"titel": titel, "text": text, "vorlage": vorlage[:300], "zeit": time.strftime("%H:%M")})
        del self.ergebnisse[:-50]

    # ---- Zustand ------------------------------------------------------------------

    @property
    def beschaeftigt(self) -> bool:
        return self._arbeit_laeuft

    def kontext_pruefen(self) -> None:
        """Von Editor-Signalen gerufen: ``kontextGeaendert`` nur, wenn sich Markierung oder Leer-Sein wirklich geändert haben."""
        jetzt = (*self.kontext()[:2], self._bezug_stand())
        if jetzt != getattr(self, "_kontext_alt", None):
            self._kontext_alt = jetzt
            self.kontextGeaendert.emit()

    def _bezug_stand(self):
        """Nur wenn eine Antwort mit Bezug im Chat steht: (Editor, Revision), damit die Oberfläche „Ersetzen/Einfügen“ neu bewertet."""
        if not any(n.get("bezug") for n in self.chat_modell.nachrichten):
            return None
        ed = self.w.current_editor()
        try:
            return (id(ed), ed.document().revision()) if ed is not None else None
        except RuntimeError:
            return None

    def kontext(self) -> tuple[bool, bool, bool, str]:
        """(Markierung da, Dokument leer, Modell für den Chat verbunden, Name des Chat-Modells) aus Editor und Konfiguration."""
        ed = self.w.current_editor()
        auswahl = bool(ed is not None and ed.textCursor().hasSelection())
        leer = ed is None or not ed.document().toPlainText().strip()
        verbunden = self.verfuegbar() and self.ki.verfuegbar_fuer("chatbot")
        mid = self.ki.modell("chatbot") if verbunden else ""
        name = next((m["name"] for m in self.konfig.alle_modelle() if m["id"] == mid), mid[len(K.OLLAMA_MARKE):] if mid.startswith(K.OLLAMA_MARKE) else mid)
        return auswahl, leer, verbunden, name

    def verfuegbar(self) -> bool:
        self.konfig.d["empfaenger"] = self.assistant.thema
        return self.ki.verfuegbar()

    def zettel(self, text: str) -> None:
        self.konfig.d["zettel"] = (text or "")[:K.ZETTEL_GRENZE]

    def _einwilligung(self, modell: str | None = None, umfang: str = "auszug", zeichen: int = 0) -> bool:
        """Fragt vor dem ersten Senden an einen Dienst im Internet. Gespeichert wird je Anbieter und Umfang („auszug“ oder „dokument“), mit Datum;
        widerrufen wird in den KI-Einstellungen (Reiter Datenschutz). Die Sperre an der Sendestelle (``KI.zustimmung_fehlt``) gilt zusätzlich."""
        ziel = self.ki.schickt_nach_aussen(modell)
        if ziel is None or self.konfig.hat_einwilligung(ziel, umfang):
            return True
        was = {"dokument": "den ganzen Text dieses Dokuments", "bild": "das angehängte Bild"}.get(umfang, "den markierten Textauszug") + (f" (etwa {zeichen} Zeichen)" if zeichen else "")
        r = QMessageBox.question(
            self.w, "Text an einen Dienst senden?",
            f"Für diese Funktion wird {was} an „{ziel}“ im Internet gesendet.\n\n"
            "Er verlässt dann diesen Rechner. Auf diesem Rechner bleibt er nur, wenn Sie Ollama (lokal) wählen.\n\n"
            f"Erlauben Sie das für „{ziel}“? Die Erlaubnis lässt sich in den KI-Einstellungen unter Datenschutz jederzeit widerrufen.")
        if r == QMessageBox.Yes:
            self.konfig.einwilligung_geben(ziel, umfang)
            return True
        return False

    # ---- Ablauf -------------------------------------------------------------------------

    def _eingabe(self):
        ed = self.w.current_editor()
        if ed is None:
            return None
        c = ed.textCursor()
        if c.hasSelection():
            von = min(c.anchor(), c.position())
            text = c.selectedText().replace(" ", "\n")
            return {"ed": ed, "text": text, "basis": von, "markiert": True, "rev": ed.document().revision()}
        text = ed.document().toPlainText().rstrip("\n")
        return {"ed": ed, "text": text, "basis": 0, "markiert": False, "rev": ed.document().revision()}

    def starte(self, meldung: str, arbeit, danach, eing: dict | None = None, aufgabe: str | None = None, modell: str | None = None) -> None:
        """arbeit(text) → Ergebnisdict (im Hintergrund); danach(ergebnis, eingabe) im Hauptthread."""
        if self._arbeit_laeuft:
            return
        self.verfuegbar()           # hält Empfänger/Thema in der Konfiguration aktuell
        if not self.ki.verfuegbar_fuer(aufgabe):
            self._hinweis_fenster("KI", "Dafür fehlt ein KI-Modell — Ollama auf diesem Rechner oder ein Schlüssel. Beides richten Sie unter „KI-Einstellungen“ ein.")
            return
        eing = eing or self._eingabe()
        if eing is not None:
            ed = eing.get("ed")
            if ed is not None:
                try:
                    eing.setdefault("dokument", ed.document())
                except RuntimeError:
                    return
            eing["_titel"] = meldung.strip(" .…„“").strip() or "KI"
        if eing is None or not eing["text"].strip():
            self._hinweis_fenster("KI", "Es steht noch kein Text da. Schreiben Sie etwas oder markieren Sie eine Stelle.")
            return
        modell = modell or (self.ki.modell(aufgabe) if aufgabe else None)
        if not self._einwilligung(modell, "auszug" if eing.get("markiert") else "dokument", len(eing["text"])):
            if not (modell or "").startswith(K.AUTO_MARKE):      # Automatisch: bei Ablehnung geht es lokal weiter (Ki.uebersetzen prüft die Zustimmung selbst)
                self.status.emit("Abgebrochen — es wurde nichts gesendet.")
                return
        self._arbeit_laeuft = True
        self.laeuft.emit(True)
        self.status.emit(f"Die KI liest die Markierung ({len(eing['text'])} Zeichen) …" if eing["markiert"] else meldung)
        self._pool.start(_Lauf((danach, eing), lambda: arbeit(eing["text"]), self._sig))

    def _fertig(self, auftrag, r) -> None:
        danach, eing = auftrag
        self._arbeit_laeuft = False
        self.laeuft.emit(False)
        if danach == "bild":
            if not self._eingabe_gueltig(eing):
                self.status.emit("Das Dokument wurde gewechselt oder geändert, während das Bild erzeugt wurde. Das Bild wurde verworfen.")
                return
            pos = eing.get("cursor")
            try:
                ed = eing["ed"]
                cur = ed.textCursor()
                aktuell = (cur.anchor(), cur.position())
            except (KeyError, RuntimeError):
                aktuell = None
            if pos is None or aktuell != pos:
                self.status.emit("Die Schreibposition wurde inzwischen geändert. Das Bild wurde nicht eingefügt.")
                return
            self._bild_fertig(r, eing)
            return
        if danach == "dauer":
            self._dauer_fertig(r, eing)
            return
        if danach == "chat":
            kennung = eing["anfrage"]
            angenommen = (self.chat_modell.fehler(kennung, r["fehler"]) if "fehler" in r else self.chat_modell.antwort(kennung, r["text"], r.get("cent")))
            if not angenommen:                                      # nach „Neues Gespräch“/Abbruch: veraltete Antwort verwerfen
                return
            self.chatGeaendert.emit()
            if "fehler" not in r:
                self.merke_ergebnis("KI-Chat", r["text"])
            return
        if not self._eingabe_gueltig(eing):
            self.status.emit("Das Dokument wurde gewechselt oder geändert, während die KI gelesen hat. "
                             "Die Antwort wurde verworfen.")
            return
        if "fehler" in r:
            self.status.emit(r["fehler"])
            return
        if r.get("text"):
            self.merke_ergebnis(eing.get("_titel", "KI"), r["text"], eing.get("text", ""))
        danach(r, eing)

    @staticmethod
    def _eingabe_gueltig(eing: dict) -> bool:
        """Nur Antworten für genau das Dokument und die Revision vom Sendezeitpunkt dürfen weiterlaufen."""
        ed = eing.get("ed")
        try:
            doc = ed.document()
            return doc is eing.get("dokument") and doc.revision() == eing["rev"]
        except (AttributeError, KeyError, RuntimeError, TypeError):
            return False

    # ---- Bild aus Text ------------------------------------------------------------------------

    def bild_aus_text(self, beschreibung: str | None = None) -> None:
        """Markierter Text (oder der übergebene) ist die Bildbeschreibung; das Bild tritt an die Stelle der Markierung."""
        if self._arbeit_laeuft:
            return
        ed = self.w.current_editor()
        if ed is None:
            return
        c = ed.textCursor()
        text = (beschreibung or (c.selectedText().replace(" ", "\n") if c.hasSelection() else "")).strip()
        if not text:
            self._hinweis_fenster("Text in Bild", "Markieren Sie zuerst den Text, der das Bild beschreibt.")
            return
        if not self.konfig["aufgaben"].get("bildgenerierung", "").startswith(K.EIGEN_MARKE):
            self.status.emit("Dafür fehlt ein Modell mit „Bilder“ — in der KI-Konfiguration eintragen.")
            self.w.befehle.w_kiKonfiguration()
            return
        if not self._einwilligung(self.konfig["aufgaben"]["bildgenerierung"]):
            self.status.emit("Abgebrochen — es wurde nichts gesendet.")
            return
        self._arbeit_laeuft = True
        self.laeuft.emit(True)
        self.status.emit("Die KI erzeugt das Bild …")
        try:
            dokument = ed.document()
            rev = dokument.revision()
            cursor_stand = (c.anchor(), c.position())
        except RuntimeError:
            return
        eing = {"ed": ed, "dokument": dokument, "rev": rev, "cursor": cursor_stand,
                "beschreibung": text, "ersetzen": c.hasSelection()}
        self._pool.start(_Lauf(("bild", eing), lambda: self.ki.bild_erzeugen(text), self._sig))

    def _bild_fertig(self, r, eing) -> None:
        if "fehler" in r:
            self.status.emit(r["fehler"])
            return
        from PySide6.QtGui import QImage
        img = QImage.fromData(r["bild"])
        if img.isNull():
            self.status.emit("Der Anbieter hat etwas geschickt, das kein Bild ist.")
            return
        from lunivo_writer.editor import einfuegen as E
        ed = eing["ed"]
        if eing["ersetzen"] and ed.textCursor().hasSelection():
            ed.textCursor().removeSelectedText()
        E.qimage_einfuegen(ed, img, eing["beschreibung"][:200])
        self.status.emit("Bild eingefügt. Strg+Z macht es rückgängig.")

    # ---- Anwenden ---------------------------------------------------------------------------

    def _preis(self, cent) -> str:
        return (" · " + K.als_geld(cent)) if cent is not None else ""

    def _einsetzen(self, r, eing, ganz_text, markiert_text) -> None:
        if r["text"].strip() == eing["text"].strip():
            self.status.emit("Die KI hat nichts zu ändern gefunden." + self._preis(r.get("cent")))
            return
        ed = eing["ed"]
        ops, ganz, n = K.ersetze_ergebnis(eing["text"], r["text"])
        from PySide6.QtGui import QTextCursor
        sperre = QTextCursor(ed.document())
        sperre.beginEditBlock()
        try:
            for von, bis, t in ops:
                ed.replace_range(eing["basis"] + von, eing["basis"] + bis, t)
        finally:
            sperre.endEditBlock()
        self.assistant.pruefen()
        if eing["markiert"]:
            msg = markiert_text
        else:
            msg = ganz_text if ganz else f"{n} {'Absatz' if n == 1 else 'Absätze'} geändert."
        self.status.emit(msg + " Strg+Z macht es rückgängig." + self._preis(r.get("cent")))

    def _anhaengen(self, r, eing, name: str) -> None:
        """Das Ergebnis hinter die Markierung (ohne Markierung: ans Ende des Textes) setzen — als ein Schritt für Rückgängig."""
        from PySide6.QtGui import QTextCursor
        ed = eing["ed"]
        c = QTextCursor(ed.document())
        c.setPosition(min(eing["basis"] + len(eing["text"]), ed.document().characterCount() - 1))
        c.insertText((" " if eing["markiert"] else "\n") + r["text"].strip())
        self.status.emit(f"{name}: Ergebnis angehängt. Strg+Z macht es rückgängig." + self._preis(r.get("cent")))
