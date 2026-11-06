"""KI im Programm: Anfragen im Hintergrund, Zustimmung vor jedem Weg nach außen, Ergebnis ins Dokument."""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import QMessageBox

from lunivo_writer.services.settings_service import data_dir
from lunivo_writer.ai import ki as K
from lunivo_writer.ai import assistent_lauf as AL
from lunivo_writer.ai import modellfaehigkeit as MF
from lunivo_writer.ai import chat_bezug as CB
from lunivo_writer.ai.chat_modell import ChatModell


class _Sig(QObject):
    fertig = Signal(object, object)       # (Auftrag, Ergebnisdict)


class _Lauf(QRunnable):
    def __init__(self, auftrag, arbeit, sig):
        super().__init__()
        self.auftrag, self.arbeit, self.sig = auftrag, arbeit, sig

    def run(self):
        try:
            r = self.arbeit()
        except Exception as e:                    # eine abstürzende Anfrage darf das Schreiben nie stören
            r = {"fehler": f"Es hat nicht geklappt: {e}"}
        self.sig.fertig.emit(self.auftrag, r)


class KIDienst(QObject):
    werkzeugFrage = Signal(str, str, str)     # Werkzeug, Argumente, Server — die Rückfrage läuft im Hauptthread
    status = Signal(str)
    laeuft = Signal(bool)
    vorschlaege = Signal(list)                # Liste von {alt, neu, grund}
    hinweis = Signal(str, str, object)        # Titel, Text, Kosten (cent) — Karte in der Seitenleiste
    aktionErgebnis = Signal(str, str, object, object)  # Name, Text, Kosten, Bezug (dict|None) — das Ergebnis einer Schnellen KI-Aktion (der Chat zeigt es als Antwort)
    geaendert = Signal()                      # Einstellungen haben sich geändert
    chatGeaendert = Signal()                  # ``chat_modell`` hat sich geändert (Nachricht, Phase, Gespräch) — die Anzeige liest daraus
    kontextGeaendert = Signal()               # Markierung oder Dokumentinhalt (leer/nicht leer) haben sich geändert — ``kontext()`` neu lesen

    def __init__(self, assistant, fenster, parent=None):
        super().__init__(parent)
        self.w = fenster
        self.assistant = assistant
        self.konfig = K.KIKonfig(os.path.join(data_dir(), "ki.json"))
        self.ki = K.KI(self.konfig, assistant.gelernt.daten)
        self._arbeit_laeuft = False
        self.chat_modell = ChatModell()
        self.ergebnisse: list[dict] = []          # „Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung (neueste zuletzt)
        self._pool = QThreadPool(self)
        self._sig = _Sig()
        self._sig.fertig.connect(self._fertig)
        self.werkzeugFrage.connect(self._werkzeug_fragen)
        self.aktionErgebnis.connect(self.aktion_in_chat)         # Verlauf und Anzeige führen dieselbe Quelle
        self.ki.werkzeug_frage = self._werkzeug_erlaubt
        self.ki.server_frage = self._server_erlaubt
        self.ki.faehigkeit_bekannt = self.geaendert.emit          # Ollama hat die Fähigkeiten des Modells gemeldet: Menüs neu lesen
        self.konfig.d["empfaenger"] = assistant.thema
        self._drossel = AL.Drossel()                  # fortlaufende Assistenten: Mindestabstand und Höchstzahl je Stunde
        self._dauer_timer = QTimer(self)
        self._dauer_timer.setSingleShot(True)
        self._dauer_timer.timeout.connect(self._dauer_los)
        self._dauer_art = "absatz"                    # was die letzte Änderung war: „absatz“ (Text) oder „markierung“
        self._dauer_zuletzt: dict = {}                # (Assistent, Stelle) → zuletzt gesendeter Text
        self._dauer_eigen = False                     # der Assistent schreibt selbst ins Dokument: das löst keine neue Runde aus
        self._dauer_pause = False

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
        if "fehler" in r:
            self.status.emit(r["fehler"])
            return
        if r.get("text"):
            self.merke_ergebnis(eing.get("_titel", "KI"), r["text"], eing.get("text", ""))
        ed = eing["ed"]
        try:
            neu_rev = ed.document().revision()
        except RuntimeError:
            return
        if neu_rev != eing["rev"]:
            self.status.emit("Sie haben weitergeschrieben, während die KI gelesen hat. Ihre Antwort passt nicht mehr "
                             "zu dem, was jetzt dasteht — nichts wurde geändert. Noch einmal drücken fragt sie neu.")
            return
        danach(r, eing)

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
        eing = {"ed": ed, "beschreibung": text, "ersetzen": c.hasSelection()}
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

    def korrigieren(self) -> None:
        self.ki.gelernt = self.assistant.gelernt.daten
        self.starte("Die KI liest den ganzen Text …", self.ki.korrigieren,
                    lambda r, e: self._einsetzen(r, e, "Korrigiert.", "Markierung korrigiert."))

    def uebersetzen(self, sprache: str | None = None, modus: str = "auto") -> None:
        """Übersetzen in die gewählte Sprache. ``modus``: „ersetzen“ setzt die Übersetzung an die Stelle der Markierung, „zeigen“ zeigt sie in der Schreibhilfe
        und im Chat (der Text bleibt unberührt), „auto“ ersetzt eine Markierung und zeigt sonst die Übersetzung des ganzen Textes."""
        s = sprache or self.konfig["sprache"]
        ed = self.w.current_editor()
        markiert = bool(ed is not None and ed.textCursor().hasSelection())
        if modus == "zeigen" or (modus == "auto" and not markiert):
            titel = f"Übersetzung nach {s}"

            def zeigen(r, e):
                titel_m = titel + (f" ({r['methode']})" if r.get("methode") else "")
                self.hinweis.emit(titel_m, r["text"], r.get("cent"))
                self.aktionErgebnis.emit(titel_m, r["text"], r.get("cent"), self._aktion_bezug(e))
            self.starte(f"Wird nach {s} übersetzt …", lambda t: self.ki.uebersetzen(t, s), zeigen, aufgabe="uebersetzung")
            return
        self.starte(f"Wird nach {s} übersetzt …", lambda t: self.ki.uebersetzen(t, s),
                    lambda r, e: self._einsetzen(r, e, f"Nach {s} übersetzt{self._methode(r)}.", f"Markierung nach {s} übersetzt{self._methode(r)}."),
                    aufgabe="uebersetzung")

    @staticmethod
    def _methode(r) -> str:
        return f" ({r['methode']})" if r.get("methode") else ""

    def text_aktion(self, aktion: str) -> None:
        namen = dict(K.TEXT_AKTIONEN)
        n = namen.get(aktion, aktion)
        self.starte(f"„{n}“ …", lambda t: self.ki.text_aktion(t, aktion),
                    lambda r, e: self._einsetzen(r, e, n + ".", "Markierung: " + n + "."))

    def assistent(self, a: dict) -> None:
        """Schnelle KI-Aktion (Eigener Assistent): ein Name und ein Prompt. Wirkung „ersetzen“ wie Korrigieren, „anhaengen“ hinter den Text, „hinweis“ wie
        Zusammenfassen. Das Ergebnis geht außerdem als Antwort in den KI-Chat."""
        arbeit = lambda t: self.ki.eigener_assistent(t, a["prompt"])           # noqa: E731

        def melden(r, e=None) -> None:         # ersetzen/anhängen haben das Ergebnis schon ins Dokument geschrieben: kein zweites Anwenden
            self.aktionErgebnis.emit(a["name"], r["text"], r.get("cent"), self._aktion_bezug(e) if e else CB.bezug_angewendet())
        if a["modus"] == "ersetzen":
            self.starte(f"„{a['name']}“ …", arbeit, lambda r, e: (self._einsetzen(r, e, a["name"] + ".", "Markierung: " + a["name"] + "."), melden(r)))
        elif a["modus"] == "anhaengen":
            self.starte(f"„{a['name']}“ …", arbeit, lambda r, e: (self._anhaengen(r, e, a["name"]), melden(r)))
        else:
            self.starte(f"„{a['name']}“ …", arbeit, lambda r, e: (self.hinweis.emit(a["name"], r["text"], r.get("cent")), melden(r, e)))

    # ---- Fortlaufende Assistenten ---------------------------------------------------------------------------------------
    def dauerbetrieb(self) -> bool:
        """Hauptschalter: nur wenn er an ist, läuft irgendein fortlaufender Assistent."""
        return bool(self.konfig["assistenten_dauerbetrieb"])

    def _dauer_einwilligung(self, modell: str | None) -> bool:
        """Klartext-Frage (nur bei Anbietern außerhalb dieses Rechners): „Sendet bei jeder Änderung den geänderten Absatz an <Anbieter>“."""
        ziel = self.ki.schickt_nach_aussen(modell or None)
        if ziel is None or self.konfig.hat_einwilligung(ziel, "dauer"):
            return True
        r = QMessageBox.question(
            self.w, "Fortlaufende Assistenten erlauben?",
            f"Ein fortlaufender Assistent sendet bei jeder Änderung den geänderten Absatz an „{ziel}“ im Internet. "
            "Das kann Kosten verursachen und geschieht, solange der Assistent eingeschaltet ist.\n\n"
            "Die Erlaubnis lässt sich in den KI-Einstellungen unter Datenschutz jederzeit widerrufen. Erlauben?")
        if r != QMessageBox.Yes:
            return False
        self.konfig.einwilligung_geben(ziel, "dauer")
        if not self.konfig.hat_einwilligung(ziel, "auszug"):
            self.konfig.einwilligung_geben(ziel, "auszug")
        return True

    def dauerbetrieb_setzen(self, an: bool) -> bool:
        """Hauptschalter ein-/ausschalten; False, wenn das Einschalten abgelehnt wurde oder nicht möglich ist."""
        an = bool(an)
        if an:
            if not self.verfuegbar():
                self._hinweis_fenster("KI", "Dafür fehlt ein KI-Modell — Ollama auf diesem Rechner oder ein Schlüssel. Beides richten Sie unter „KI-Einstellungen“ ein.")
                return False
            if not self._dauer_einwilligung(None):
                return False
        else:
            self._dauer_timer.stop()
        self._dauer_pause = False
        self.konfig.setze("assistenten_dauerbetrieb", an)
        self.geaendert.emit()
        return True

    def assistent_an_setzen(self, id_: str, an: bool) -> bool:
        """Einen fortlaufenden Assistenten an-/ausschalten (läuft erst, wenn auch ``dauerbetrieb()`` an ist); False bei Ablehnung."""
        a = self.konfig.assistent_holen(id_)
        if a is None or a.get("art") != "fortlaufend":
            return False
        if an and not self._dauer_einwilligung(a.get("modell") or None):
            return False
        self.konfig.assistent_aendern(id_, an=bool(an))
        self.geaendert.emit()
        return True

    def _dauer_aus(self, a: dict, grund: str) -> None:
        """Fehler oder fehlende Erlaubnis: den Assistenten ausschalten und es sagen — nie stumm wiederholen."""
        self.konfig.assistent_aendern(a["id"], an=False)
        self.geaendert.emit()
        self._hinweis_fenster(f"Assistent „{a['name']}“", f"„{a['name']}“ wurde ausgeschaltet: {grund}")

    def dauer_geaendert(self, art: str = "absatz") -> None:
        """Von Dokument-/Markierungssignalen gerufen (ui/main_window.py): startet die Ruhezeit des Assistenten neu."""
        if self._dauer_eigen or not self.dauerbetrieb():
            return
        aktiv = [a for a in self.konfig.assistenten("fortlaufend") if a["an"] and a["ausloeser"] == art]
        if not aktiv:
            return
        self._dauer_art = art
        self._dauer_timer.start(int(min(AL.verzoegerung_begrenzen(a["verzoegerung"]) for a in aktiv) * 1000))

    def _dauer_eingabe(self, a: dict):
        ed = self.w.current_editor()
        if ed is None or ed.isReadOnly():
            return None
        c = ed.textCursor()
        if a["ausloeser"] == "markierung" or a["umfang"] == "markierung":
            if not c.hasSelection():
                return None
            text, basis = c.selectedText().replace("\u2029", "\n"), c.selectionStart()
            stelle = "markierung"
        else:
            b = c.block()
            text, basis, stelle = b.text(), b.position(), "absatz"
        return {"ed": ed, "text": AL.eingabe_kuerzen(text), "basis": basis, "markiert": True, "rev": ed.document().revision(), "stelle": stelle}

    def _dauer_los(self) -> None:
        """Nach der Ruhezeit: den ersten fälligen Assistenten starten (die übrigen kommen nach seinem Ergebnis dran)."""
        if self._arbeit_laeuft or not self.dauerbetrieb():
            return
        wartet = self._drossel.warten_noch()
        if wartet == float("inf"):
            if not self._dauer_pause:
                self._dauer_pause = True
                self.status.emit("Fortlaufende Assistenten pausieren: Höchstzahl der Anfragen in dieser Stunde erreicht.")
            return
        if wartet > 0:
            self._dauer_timer.start(int(wartet * 1000) + 50)
            return
        self._dauer_pause = False
        for a in self.konfig.assistenten("fortlaufend"):
            if not a["an"] or a["ausloeser"] != self._dauer_art:
                continue
            eing = self._dauer_eingabe(a)
            if eing is None:
                continue
            schluessel = (a["id"], eing["stelle"] if eing["stelle"] == "markierung" else eing["ed"].textCursor().blockNumber())
            if not AL.absatz_geaendert(self._dauer_zuletzt.get(schluessel), eing["text"]):
                continue
            modell = a.get("modell") or None
            if not self.ki.verfuegbar():
                self._dauer_aus(a, "Es ist kein KI-Modell eingerichtet.")
                return
            if (sperre := self.ki.zustimmung_fehlt(modell, "auszug")) is not None or \
                    (self.ki.schickt_nach_aussen(modell) and not self.konfig.hat_einwilligung(self.ki.schickt_nach_aussen(modell), "dauer")):
                self._dauer_aus(a, (sperre or {}).get("fehler", "Die Erlaubnis für fortlaufende Assistenten fehlt."))
                return
            self._dauer_zuletzt[schluessel] = eing["text"]
            eing.update(assistent=a["id"], _titel=a["name"])
            self._drossel.gesendet()
            nur = a["modus"] == "kommentar"
            self.starte(f"„{a['name']}“ …", lambda t, a=a, nur=nur: self.ki.eigener_assistent(t, a["prompt"], a["kommentar"] and not nur, a.get("modell", ""), nur),
                        "dauer", eing, modell=modell)
            return

    def _dauer_fertig(self, r, eing) -> None:
        a = self.konfig.assistent_holen(eing.get("assistent"))
        if a is None:
            return
        if "fehler" in r:
            self._dauer_aus(a, r["fehler"])
            return
        modus, alt = a["modus"], eing["text"]
        text, begruendung = AL.trenne_begruendung(r.get("text", ""))
        wirkt = AL.ergebnis_wirkt(alt, text) if modus in ("ersetzen", "anhaengen", "hervorheben") else bool(text.strip())
        if not wirkt:
            self.status.emit(f"„{a['name']}“: nichts zu ändern." + self._preis(r.get("cent")))
            return
        self.merke_ergebnis(a["name"], text + (f"\n\nBegründung: {begruendung}" if begruendung else ""), alt)
        ed = eing["ed"]
        try:
            if ed.document().revision() != eing["rev"]:
                self.status.emit(f"„{a['name']}“: Sie haben weitergeschrieben — die Antwort passt nicht mehr und wurde verworfen.")
                return
        except RuntimeError:
            return
        k = self._preis(r.get("cent"))
        self._dauer_eigen = True
        try:
            if modus == "kommentar":
                self._dauer_kommentar(ed, eing, text, a["name"])
                self.status.emit(f"„{a['name']}“: Kommentar angelegt." + k)
            elif modus == "hervorheben":
                self.assistant.ki_fertig(eing["rev"], [{"alt": alt, "neu": None, "grund": text + (f" ({begruendung})" if begruendung else ""), "konfidenz": 1.0}])
                self.status.emit(f"„{a['name']}“: Stelle in der Schreibhilfe markiert." + k)
            elif modus == "ersetzen":
                self._dauer_ersetzen(a, eing, text, begruendung, r)
            else:                                           # hinweis (anhängen wäre unaufgefordert zu eingreifend)
                self.hinweis.emit(a["name"], text, r.get("cent"))
                self.aktionErgebnis.emit(a["name"], text, r.get("cent"), self._aktion_bezug(eing))
        finally:
            self._dauer_eigen = False
        if self._dauer_timer.isActive() is False and self.dauerbetrieb():
            self._dauer_timer.start(int(AL.MINDESTABSTAND * 1000))      # weitere Assistenten derselben Änderung kommen nach dem Mindestabstand

    def _dauer_kommentar(self, ed, eing, text: str, autor: str) -> None:
        from PySide6.QtGui import QTextCursor
        alt_c = ed.textCursor()
        c = QTextCursor(ed.document())
        c.setPosition(eing["basis"])
        c.setPosition(min(eing["basis"] + len(eing["text"]), ed.document().characterCount() - 1), QTextCursor.KeepAnchor)
        ed.setTextCursor(c)
        try:
            ed.kommentar_neu(text, autor)
        finally:
            ed.setTextCursor(alt_c)

    def _dauer_ersetzen(self, a: dict, eing, text: str, begruendung: str, r) -> None:
        """Ersetzen nur nach Bestätigung; ein Undo-Schritt (``_einsetzen``)."""
        ed = eing["ed"]
        vorher = eing["text"] if len(eing["text"]) <= 400 else eing["text"][:400] + " …"
        nachher = text if len(text) <= 400 else text[:400] + " …"
        f = QMessageBox.question(self.w, f"„{a['name']}“ übernehmen?", f"Vorher:\n{vorher}\n\nNachher:\n{nachher}\n\nDen Text ersetzen? Strg+Z macht es rückgängig.")
        if f != QMessageBox.Yes:
            self.status.emit(f"„{a['name']}“: nicht übernommen.")
            return
        if ed.document().revision() != eing["rev"]:
            self.status.emit(f"„{a['name']}“: Der Text hat sich inzwischen geändert — nichts wurde ersetzt.")
            return
        self._einsetzen({"text": text, "cent": r.get("cent")}, eing, a["name"] + ".", a["name"] + ".")
        self._dauer_zuletzt[(a["id"], "markierung" if eing["stelle"] == "markierung" else ed.textCursor().blockNumber())] = text
        if begruendung and a["kommentar"]:
            self._dauer_kommentar(ed, {**eing, "text": text}, begruendung, a["name"])

    def zusammenfassen(self) -> None:
        self.starte("Die KI fasst zusammen …", self.ki.zusammenfassen,
                    lambda r, e: self.hinweis.emit("Zusammenfassung", r["text"], r.get("cent")))

    def analyse(self) -> None:
        self.starte("Die KI liest den Text …", self.ki.text_analyse,
                    lambda r, e: self.hinweis.emit("Text- und Wortanalyse", r["text"], r.get("cent")))

    def vorschlaege_holen(self) -> None:
        def danach(r, e):
            lst = r.get("vorschlaege", [])
            self.assistant.ki_fertig(e.get("rev", -1), lst)
            self.vorschlaege.emit(lst)
            self.status.emit((f"{len(lst)} Vorschläge." if lst else "Die KI findet nichts, was sich leichter sagen ließe.")
                             + self._preis(r.get("cent")))
        self.starte("Die KI sucht Sätze, die sich leichter lesen ließen …", self.ki.vorschlaege, danach)

    def thesaurus(self, danach) -> None:
        """Synonyme zum Wort am Zeiger; danach(wort, woerter, von, bis) im Hauptthread."""
        ed = self.w.current_editor()
        if ed is None:
            return
        c = ed.textCursor()
        if not c.hasSelection():
            c.select(c.SelectionType.WordUnderCursor)
        wort = c.selectedText().strip()
        if not wort:
            self._hinweis_fenster("Thesaurus", "Markieren Sie ein Wort oder setzen Sie die Schreibmarke hinein.")
            return
        von, bis = c.selectionStart(), c.selectionEnd()
        text = ed.document().toPlainText()
        umgebung = text[max(0, von - 120):bis + 120]
        eing = {"ed": ed, "text": umgebung, "basis": von, "markiert": False, "rev": ed.document().revision()}

        def fertig(r, e):
            lst = r.get("woerter", [])
            if not lst:
                self.status.emit("Dazu ist der KI nichts eingefallen." + self._preis(r.get("cent")))
                return
            danach(wort, lst, von, bis)
        self.starte(f"Suche Wörter für „{wort}“ …", lambda _t: self.ki.synonyme(wort, umgebung), fertig, eing)

    def satz_vorschlag(self, fund, danach) -> None:
        """Zu einem Hinweis („Langer Satz …“) einen Umschreibe-Vorschlag holen; ``danach(vorschlag)`` bekommt {alt, neu, grund} im Hauptthread."""
        ed = self.w.current_editor()
        if ed is None:
            return
        satz = fund.stelle or ed.document().toPlainText()[fund.von:fund.bis]
        eing = {"ed": ed, "text": satz, "basis": fund.von, "markiert": True, "rev": ed.document().revision()}
        self.starte("Die KI schlägt kürzere Sätze vor …", lambda t: self.ki.satz_umschreiben(t, fund.grund),
                    lambda r, e: danach({"alt": satz, "neu": r["text"].strip(), "grund": fund.grund}), eing=eing)

    def vorschlag_einsetzen(self, v: dict) -> bool:
        ed = self.w.current_editor()
        if ed is None:
            return False
        text = ed.document().toPlainText()
        i = text.find(v["alt"])
        if i < 0:
            self.status.emit("Der Satz steht nicht mehr so im Text — nichts geändert.")
            return False
        return ed.replace_range(i, i + len(v["alt"]), v["neu"])

    # ---- Chat ----------------------------------------------------------------------------------
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
        self._pool.start(_Lauf(("chat", {"anfrage": kennung}), lambda: self.ki.chat(verlauf, doc, markiert), self._sig))
