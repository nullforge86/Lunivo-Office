"""KIDauerbetrieb: fachlich abgegrenzte KI-Dienstlogik."""
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


class KIDauerbetriebMixin:
    """Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden."""

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
                self.assistant.ki_fertig(eing["rev"], [{"alt": alt, "neu": None, "grund": text + (f" ({begruendung})" if begruendung else ""), "konfidenz": 1.0}], dokument=ed.document())
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
