"""KIAktionen: fachlich abgegrenzte KI-Dienstlogik."""
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


class KIAktionenMixin:
    """Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden."""

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

    def zusammenfassen(self) -> None:
        self.starte("Die KI fasst zusammen …", self.ki.zusammenfassen,
                    lambda r, e: self.hinweis.emit("Zusammenfassung", r["text"], r.get("cent")))

    def analyse(self) -> None:
        self.starte("Die KI liest den Text …", self.ki.text_analyse,
                    lambda r, e: self.hinweis.emit("Text- und Wortanalyse", r["text"], r.get("cent")))

    def vorschlaege_holen(self) -> None:
        def danach(r, e):
            lst = r.get("vorschlaege", [])
            for v in lst:
                v.update(_ed=e["ed"], _dokument=e["dokument"], _rev=e["rev"])
            self.assistant.ki_fertig(e.get("rev", -1), lst, dokument=e["dokument"])
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
                    lambda r, e: danach({"alt": satz, "neu": r["text"].strip(), "grund": fund.grund,
                                         "_ed": e["ed"], "_dokument": e["dokument"], "_rev": e["rev"]}), eing=eing)

    def vorschlag_einsetzen(self, v: dict) -> bool:
        ed = self.w.current_editor()
        if ed is None:
            return False
        try:
            if (ed is not v.get("_ed") or ed.document() is not v.get("_dokument")
                    or ed.document().revision() != v.get("_rev")):
                self.status.emit("Das Dokument wurde gewechselt oder geändert — der KI-Vorschlag ist veraltet.")
                return False
        except RuntimeError:
            self.status.emit("Das Dokument ist nicht mehr verfügbar — der KI-Vorschlag ist veraltet.")
            return False
        text = ed.document().toPlainText()
        i = text.find(v["alt"])
        if i < 0:
            self.status.emit("Der Satz steht nicht mehr so im Text — nichts geändert.")
            return False
        return ed.replace_range(i, i + len(v["alt"]), v["neu"])

    # ---- Chat ----------------------------------------------------------------------------------
