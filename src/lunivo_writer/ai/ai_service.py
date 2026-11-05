"""KI im Programm: Anfragen im Hintergrund, Zustimmung vor jedem Weg nach außen, Ergebnis ins Dokument."""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QMessageBox

from lunivo_writer.services.settings_service import data_dir
from lunivo_writer.ai import ki as K


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
    chatAntwort = Signal(str, object)
    aktionErgebnis = Signal(str, str, object)  # Name, Text, Kosten — das Ergebnis einer Schnellen KI-Aktion (der Chat zeigt es als Antwort)
    geaendert = Signal()                      # Einstellungen haben sich geändert

    def __init__(self, assistant, fenster, parent=None):
        super().__init__(parent)
        self.w = fenster
        self.assistant = assistant
        self.konfig = K.KIKonfig(os.path.join(data_dir(), "ki.json"))
        self.ki = K.KI(self.konfig, assistant.gelernt.daten)
        self._beschaeftigt = False
        self.ergebnisse: list[dict] = []          # „Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung (neueste zuletzt)
        self._pool = QThreadPool(self)
        self._sig = _Sig()
        self._sig.fertig.connect(self._fertig)
        self.werkzeugFrage.connect(self._werkzeug_fragen)
        self.ki.werkzeug_frage = self._werkzeug_erlaubt
        self.ki.server_frage = self._server_erlaubt
        self.konfig.d["empfaenger"] = assistant.thema

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
            k = QMessageBox(QMessageBox.Warning, "MCP-Server starten?",
                            f"Für die Antwort soll das Programm des MCP-Servers „{server}“ auf diesem Rechner gestartet werden.\n\n"
                            f"Befehl:\n{argumente}\n\nDas Programm läuft mit Ihren Rechten. Jeder Werkzeugaufruf wird danach einzeln gefragt. Starten?",
                            QMessageBox.Yes | QMessageBox.No, self.w)
            k.setDefaultButton(QMessageBox.No)
            self._werkzeug_ok = k.exec() == QMessageBox.Yes
            self._antwort_ereignis.set()
            return
        warnung = {"löschen": "Löschen von Daten", "schreiben": "Schreiben oder Ändern", "netzwerk": "Zugriff auf das Netzwerk",
                   "lesen": "Lesen", "unbekannt": "unbekannte Wirkung"}.get(art, "unbekannte Wirkung")
        k = QMessageBox(QMessageBox.Question, "Werkzeug aufrufen?",
                        f"Die KI möchte das Werkzeug „{name}“ des MCP-Servers „{server}“ aufrufen.\n\nArt der Aktion: {warnung}\n\nErlauben?",
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
        was = ("den ganzen Text dieses Dokuments" if umfang == "dokument" else "den markierten Textauszug") + (f" (etwa {zeichen} Zeichen)" if zeichen else "")
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

    def starte(self, meldung: str, arbeit, danach, eing: dict | None = None, aufgabe: str | None = None) -> None:
        """arbeit(text) → Ergebnisdict (im Hintergrund); danach(ergebnis, eingabe) im Hauptthread."""
        if self._beschaeftigt:
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
        modell = self.ki.modell(aufgabe) if aufgabe else None
        if not self._einwilligung(modell, "auszug" if eing.get("markiert") else "dokument", len(eing["text"])):
            if not (modell or "").startswith(K.AUTO_MARKE):      # Automatisch: bei Ablehnung geht es lokal weiter (Ki.uebersetzen prüft die Zustimmung selbst)
                self.status.emit("Abgebrochen — es wurde nichts gesendet.")
                return
        self._beschaeftigt = True
        self.laeuft.emit(True)
        self.status.emit(f"Die KI liest die Markierung ({len(eing['text'])} Zeichen) …" if eing["markiert"] else meldung)
        self._pool.start(_Lauf((danach, eing), lambda: arbeit(eing["text"]), self._sig))

    def _fertig(self, auftrag, r) -> None:
        danach, eing = auftrag
        self._beschaeftigt = False
        self.laeuft.emit(False)
        if danach == "bild":
            self._bild_fertig(r, eing)
            return
        if danach == "chat":
            self.chatAntwort.emit("⚠ " + r["fehler"] if "fehler" in r else r["text"], r.get("cent"))
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
        if self._beschaeftigt:
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
        self._beschaeftigt = True
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
                self.aktionErgebnis.emit(titel_m, r["text"], r.get("cent"))
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

        def melden(r) -> None:
            self.aktionErgebnis.emit(a["name"], r["text"], r.get("cent"))
        if a["modus"] == "ersetzen":
            self.starte(f"„{a['name']}“ …", arbeit, lambda r, e: (self._einsetzen(r, e, a["name"] + ".", "Markierung: " + a["name"] + "."), melden(r)))
        elif a["modus"] == "anhaengen":
            self.starte(f"„{a['name']}“ …", arbeit, lambda r, e: (self._anhaengen(r, e, a["name"]), melden(r)))
        else:
            self.starte(f"„{a['name']}“ …", arbeit, lambda r, e: (self.hinweis.emit(a["name"], r["text"], r.get("cent")), melden(r)))

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
    def chat(self, verlauf: list) -> None:
        if self._beschaeftigt or not self.verfuegbar() or not self._einwilligung(None, "dokument", 12000):
            if not self.verfuegbar():
                self.status.emit("Der Chat braucht einen KI-Schlüssel — oder Ollama. Optionen ▸ Schreibhilfe und KI.")
            return
        ziel = self.ki.websuche_ziel()
        if ziel and not self.konfig.hat_einwilligung(ziel, "auszug"):
            if QMessageBox.question(self.w, "Frage an die Websuche senden?",
                                    f"Für die Antwort wird Ihre Frage an „{ziel}“ im Internet gesendet.\n\nErlauben Sie das? "
                                    "Widerrufen können Sie es in den KI-Einstellungen unter Datenschutz.") == QMessageBox.Yes:
                self.konfig.einwilligung_geben(ziel, "auszug")
        ed = self.w.current_editor()
        doc = ed.document().toPlainText() if ed else ""
        self._beschaeftigt = True
        self.laeuft.emit(True)
        self._pool.start(_Lauf(("chat", None), lambda: self.ki.chat(verlauf, doc), self._sig))
