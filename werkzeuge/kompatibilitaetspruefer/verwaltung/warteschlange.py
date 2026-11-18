"""Prüfwarteschlange: verteilt Dateien auf Prüfprozesse (``QProcess``, asynchron — der GUI-Thread wird nie blockiert) und speichert jedes Ergebnis sofort in der Datenbank.

* Zeitgrenze je Datei: Der Prozess wird nach ``zeitlimit_s`` beendet, das Ergebnis lautet „fehlgeschlagen (Zeitüberschreitung)“.
* Absturz oder Speichergrenze: ein Prozessende ohne Ergebnisdatei wird als „fehlgeschlagen (Technischer Prüffehler)“ gespeichert; die übrigen Dateien laufen weiter.
* Abbruch: laufende Prozesse werden beendet, ihre Ergebnisse als „abgebrochen“ gespeichert (nie „bestanden“); noch offene Aufträge bleiben für die Fortsetzung erhalten.
* Fortsetzung: Der Bearbeitungsstand liegt in der Datenbank (Tabellen ``laeufe``/``auftraege``). Ergebnisse mit unveränderter Datei, Referenz, Konfiguration und Lunivo-Version
  werden wiederverwendet statt neu geprüft.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, Signal

from kompatibilitaetspruefer.pruefung import klassifikation as K
from kompatibilitaetspruefer.verwaltung import konfiguration as KF
from kompatibilitaetspruefer.verwaltung.datenbank import Datenbank, datei_stamp

WERKZEUGE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


class _Lauf:
    """Ein laufender Prüfprozess."""
    def __init__(self, auftrag: dict, datei: dict, arten: list, prozess: QProcess, job_pfad: str, ergebnis_pfad: str, stamps: dict):
        self.auftrag, self.datei, self.arten, self.prozess = auftrag, datei, arten, prozess
        self.job_pfad, self.ergebnis_pfad, self.stamps = job_pfad, ergebnis_pfad, stamps
        self.zeitgrenze = False
        self.speichergrenze = 0
        self.speicher_timer = QTimer()
        self.abgebrochen = False
        self.start = time.monotonic()
        self.timer = QTimer()
        self.timer.setSingleShot(True)


class Warteschlange(QObject):
    fortschritt = Signal(dict)          # gesamt, fertig, offen, fehlgeschlagen, wiederverwendet, aktuell (Liste von Namen)
    ergebnis_fertig = Signal(int)       # datei_id
    beendet = Signal(str)               # "fertig" oder "abgebrochen"

    def __init__(self, db: Datenbank, parent=None):
        super().__init__(parent)
        self.db = db
        self.konfig = KF.Konfiguration()
        self.lauf_id: int | None = None
        self.version = ""
        self._offen: list[dict] = []
        self._aktiv: dict[int, _Lauf] = {}
        self._arbeitsordner: str | None = None
        self._abbruch = False
        self.darstellungen: dict = {}
        self._zaehler = {"gesamt": 0, "fertig": 0, "fehlgeschlagen": 0, "wiederverwendet": 0}

    # ---- Steuerung -----------------------------------------------------------------------------------------------
    @property
    def laeuft(self) -> bool:
        return self.lauf_id is not None                      # bis zum ordentlichen Ende (_ende) gilt der Lauf als aktiv; so ist kein zweiter Start im Übergang möglich

    def starten(self, konfig: KF.Konfiguration, auftraege: list[tuple[int, list[str]]], neu_pruefen: bool = False) -> int | None:
        """``auftraege``: (Datei-Id, Prüfarten). Arten mit gültigem gespeicherten Ergebnis werden übersprungen (außer ``neu_pruefen``).
        → Lauf-Id, oder ``None``, wenn nichts zu tun war."""
        from kompatibilitaetspruefer.pruefung.lunivo_zugang import lunivo_version
        if self.laeuft:
            return None
        self.konfig = konfig
        self.version = lunivo_version()
        h = konfig.pruefsumme()
        arbeit, wieder = [], 0
        for datei_id, arten in auftraege:
            d = self.db.datei(datei_id)
            if d is None:
                continue
            st, rs = datei_stamp(d["pfad"]), self.db.referenz_stamp(datei_id)
            nötig = []
            for a in arten:
                if not neu_pruefen and a != "darstellung" and self.db.wiederverwendbar(datei_id, a, st, rs, h, self.version):
                    wieder += 1
                else:
                    nötig.append(a)
            if nötig:
                arbeit.append((datei_id, nötig))
        self._zaehler = {"gesamt": len(arbeit), "fertig": 0, "fehlgeschlagen": 0, "wiederverwendet": wieder}
        if not arbeit:
            self.fortschritt.emit(self._stand())
            return None
        arten_alle = sorted({a for _d, arten in arbeit for a in arten})
        self.lauf_id = self.db.lauf_neu(konfig.als_dict(), h, self.version, arten_alle, arbeit)
        self._offen = self.db.offene_auftraege(self.lauf_id)
        self._beginnen()
        return self.lauf_id

    def fortsetzen(self, lauf: dict) -> bool:
        """Einen unterbrochenen Lauf mit seinen ursprünglichen Einstellungen weiterführen."""
        from kompatibilitaetspruefer.pruefung.lunivo_zugang import lunivo_version
        if self.laeuft:
            return False
        self.konfig = KF.Konfiguration.aus_dict(json.loads(lauf["konfig_json"]))
        self.version = lunivo_version()
        self.lauf_id = lauf["id"]
        z = self.db.lauf_zaehler(self.lauf_id)
        self._offen = self.db.offene_auftraege(self.lauf_id)
        self._zaehler = {"gesamt": z["gesamt"], "fertig": z.get("fertig", 0), "fehlgeschlagen": 0, "wiederverwendet": 0}
        self.db.lauf_status(self.lauf_id, "laufend")
        self._beginnen()
        return True

    def _beginnen(self) -> None:
        self._abbruch = False
        self._arbeitsordner = tempfile.mkdtemp(prefix="lunivo-pruefer-auftraege-")
        os.chmod(self._arbeitsordner, 0o700)
        self.fortschritt.emit(self._stand())
        self._verteilen()

    def abbrechen(self) -> None:
        """Bricht den Lauf wirklich ab: nichts Neues wird mehr gestartet, laufende Prozesse werden beendet, noch offene Aufträge verfallen (keine Fortsetzung)."""
        if self.lauf_id is None or self._abbruch:
            return
        self._abbruch = True
        self._offen = []
        self.db.auftraege_abbrechen(self.lauf_id)
        for l in list(self._aktiv.values()):
            l.abgebrochen = True
            l.timer.stop()
            l.speicher_timer.stop()
            l.prozess.kill()
        if not self._aktiv:
            self._ende()
            return
        self.fortschritt.emit(self._stand())
        lauf = self.lauf_id
        QTimer.singleShot(3000, lambda: self._abbruch_erzwingen(lauf))          # Sicherung: hängt ein Prozess, wird der Lauf trotzdem beendet

    def _abbruch_erzwingen(self, lauf_id: int) -> None:
        if self.lauf_id != lauf_id:
            return
        for l in list(self._aktiv.values()):
            l.prozess.kill()
            l.prozess.waitForFinished(1000)
            if l.auftrag["id"] in self._aktiv:
                self._abschliessen(l, None, "abgebrochen")
        if self.lauf_id == lauf_id:
            self._ende()

    # ---- Verteilung ----------------------------------------------------------------------------------------------
    def _verteilen(self) -> None:
        while not self._abbruch and self._offen and len(self._aktiv) < max(1, self.konfig.parallel):
            self._starte(self._offen.pop(0))
        if not self._offen and not self._aktiv:
            self._ende()

    def _starte(self, auftrag: dict) -> None:
        datei = self.db.datei(auftrag["datei_id"])
        arten = json.loads(auftrag["arten_json"])
        if datei is None or not os.path.isfile(datei["pfad"]):
            for a in arten:
                self._speichere_technisch(auftrag["datei_id"], a, "Die Datei existiert nicht mehr", {})
            self.db.auftrag_status(auftrag["id"], "fertig")
            self._zaehler["fertig"] += 1
            self._zaehler["fehlgeschlagen"] += 1
            self.ergebnis_fertig.emit(auftrag["datei_id"])
            self.fortschritt.emit(self._stand())
            QTimer.singleShot(0, self._verteilen)
            return
        ref = self.db.referenz(datei["id"]) or {}
        stamps = {"datei_stamp": datei_stamp(datei["pfad"]), "referenz_stamp": self.db.referenz_stamp(datei["id"]), "konfig_hash": self.konfig.pruefsumme(),
                  "lunivo_version": self.version, "lauf_id": self.lauf_id}
        schluessel = hashlib.sha1(f"{stamps['datei_stamp']}|{stamps['referenz_stamp']}|{stamps['konfig_hash']}".encode()).hexdigest()[:12]
        job = {"datei": {"id": datei["id"], "pfad": datei["pfad"], "endung": datei["endung"], "name": datei["name"]}, "referenz": ref, "arten": arten,
               "konfig": self.konfig.als_dict(), "bildordner": os.path.join(KF.cacheordner(), f"d{datei['id']}", schluessel)}
        job_pfad = os.path.join(self._arbeitsordner, f"{auftrag['id']}.job.json")
        erg_pfad = os.path.join(self._arbeitsordner, f"{auftrag['id']}.ergebnis.json")
        with open(job_pfad, "w", encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False, default=str)
        p = QProcess(self)
        env = QProcessEnvironment.systemEnvironment()
        env.insert("QT_QPA_PLATFORM", "offscreen")
        env.insert("PYTHONDONTWRITEBYTECODE", "1")
        p.setProcessEnvironment(env)
        p.setWorkingDirectory(WERKZEUGE)
        p.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        l = _Lauf(auftrag, datei, arten, p, job_pfad, erg_pfad, stamps)
        self._aktiv[auftrag["id"]] = l
        self.db.auftrag_status(auftrag["id"], "laeuft")
        p.finished.connect(lambda code, status, l=l: self._fertig(l, code, status))
        p.errorOccurred.connect(lambda err, l=l: self._fehler(l, err))
        l.timer.timeout.connect(lambda l=l: self._zeit(l))
        l.timer.start(max(5, self.konfig.zeitlimit_s) * 1000)
        if self.konfig.speicher_mb > 0:
            l.speicher_timer.timeout.connect(lambda l=l: self._speicher_pruefen(l))
            l.speicher_timer.start(1000)
        p.start(sys.executable, ["-m", "kompatibilitaetspruefer.pruefung.arbeiter", job_pfad, erg_pfad])
        self.fortschritt.emit(self._stand())

    def _speicher_pruefen(self, l: _Lauf) -> None:
        """Tatsächlich belegter Arbeitsspeicher (Linux: /proc); über der Grenze wird der Prozess beendet."""
        pid = int(l.prozess.processId())
        if pid <= 0:
            return
        try:
            with open(f"/proc/{pid}/status", encoding="ascii") as f:
                for z in f:
                    if z.startswith("VmRSS:"):
                        mb = int(z.split()[1]) // 1024
                        if mb > self.konfig.speicher_mb:
                            l.speichergrenze = mb
                            l.prozess.kill()
                        return
        except OSError:
            pass

    def _zeit(self, l: _Lauf) -> None:
        l.zeitgrenze = True
        l.prozess.kill()

    def _fehler(self, l: _Lauf, err) -> None:
        if err == QProcess.ProcessError.FailedToStart:                       # finished() kommt dann nicht
            self._abschliessen(l, None, "Der Prüfprozess ließ sich nicht starten")

    def _fertig(self, l: _Lauf, code: int, status) -> None:
        l.timer.stop()
        l.speicher_timer.stop()
        ausgabe = bytes(l.prozess.readAll()).decode("utf-8", "replace").strip()
        ergebnis = None
        if os.path.isfile(l.ergebnis_pfad) and not l.zeitgrenze and not l.speichergrenze and not l.abgebrochen:
            try:
                with open(l.ergebnis_pfad, encoding="utf-8") as f:
                    ergebnis = json.load(f)
            except (OSError, ValueError):
                ergebnis = None
        if ergebnis is not None:
            self._abschliessen(l, ergebnis, "")
            return
        if l.abgebrochen:
            text = "abgebrochen"
        elif l.speichergrenze:
            text = f"Speichergrenze überschritten ({l.speichergrenze} MB > {self.konfig.speicher_mb} MB); Prozess beendet"
        elif l.zeitgrenze:
            text = f"Zeitüberschreitung: nach {self.konfig.zeitlimit_s} s ohne Ergebnis beendet"
        elif status == QProcess.ExitStatus.CrashExit:
            text = f"Der Prüfprozess ist abgestürzt (Signal), Dokument vermutlich beschädigt oder zu groß. {self._letzte(ausgabe)}"
        else:
            text = f"Der Prüfprozess endete mit Code {code} ohne Ergebnis. {self._letzte(ausgabe)}"
        self._abschliessen(l, None, text)

    @staticmethod
    def _letzte(ausgabe: str) -> str:
        zeilen = [z for z in ausgabe.splitlines() if z.strip()]
        return ("Letzte Meldung: " + zeilen[-1][:250]) if zeilen else ""

    def _abschliessen(self, l: _Lauf, ergebnis: dict | None, fehlertext: str) -> None:
        if l.auftrag["id"] not in self._aktiv:
            return
        del self._aktiv[l.auftrag["id"]]
        schlecht = False
        if ergebnis is not None:
            for e in ergebnis["ergebnisse"]:
                art = e.pop("art")
                if art == "darstellung":
                    self._darstellung_merken(l, e)
                    continue
                self.db.ergebnis_speichern(l.datei["id"], art, {**e, **l.stamps})
                schlecht = schlecht or e["status"] == K.FEHLGESCHLAGEN
            self.db.auftrag_status(l.auftrag["id"], "fertig")
        elif l.abgebrochen:
            for a in l.arten:
                if a != "darstellung":
                    self._speichere_abgebrochen(l.datei["id"], a, l.stamps)
            self.db.auftrag_status(l.auftrag["id"], "abgebrochen")
        else:
            for a in l.arten:
                if a != "darstellung":
                    self._speichere_technisch(l.datei["id"], a, fehlertext, l.stamps)
            schlecht = True
            self.db.auftrag_status(l.auftrag["id"], "fertig")
        for pfad in (l.job_pfad, l.ergebnis_pfad):
            try:
                os.remove(pfad)
            except OSError:
                pass
        l.timer.deleteLater()
        l.speicher_timer.deleteLater()
        l.prozess.deleteLater()
        if not l.abgebrochen:
            self._zaehler["fertig"] += 1
            self._zaehler["fehlgeschlagen"] += 1 if schlecht else 0
        self.ergebnis_fertig.emit(l.datei["id"])
        self.fortschritt.emit(self._stand())
        if self._abbruch:
            if not self._aktiv:
                self._ende()
        else:
            QTimer.singleShot(0, self._verteilen)

    def _darstellung_merken(self, l: _Lauf, e: dict) -> None:
        self.darstellungen[l.datei["id"]] = e.get("bilder", {}) if e["status"] != K.FEHLGESCHLAGEN else {"fehler": e.get("beschreibung", "")}

    def _speichere_technisch(self, datei_id: int, art: str, text: str, stamps: dict) -> None:
        b = [K.scheitert("Prüfung", "Technischer Prüffehler", text)]
        self.db.ergebnis_speichern(datei_id, art, {"status": K.FEHLGESCHLAGEN, "fehlerart": "Technischer Prüffehler", "schwere": "kritisch", "beschreibung": text,
                                                   "befunde": b, **stamps})

    def _speichere_abgebrochen(self, datei_id: int, art: str, stamps: dict) -> None:
        text = "Prüfung vom Benutzer abgebrochen; kein Ergebnis"
        self.db.ergebnis_speichern(datei_id, art, {"status": K.ABGEBROCHEN, "fehlerart": "", "schwere": "hinweis", "beschreibung": text,
                                                   "befunde": [K.nicht_pruefbar("Prüfung", text)], **stamps})

    def _ende(self) -> None:
        if self.lauf_id is None:
            return
        abgebrochen = self._abbruch
        self.db.lauf_status(self.lauf_id, "abgebrochen" if abgebrochen else "fertig")
        self.lauf_id = None
        self._offen = []
        if self._arbeitsordner:
            shutil.rmtree(self._arbeitsordner, ignore_errors=True)
            self._arbeitsordner = None
        self.fortschritt.emit(self._stand())
        self.beendet.emit("abgebrochen" if abgebrochen else "fertig")

    def _stand(self) -> dict:
        z = self._zaehler
        return {"gesamt": z["gesamt"], "fertig": z["fertig"], "fehlgeschlagen": z["fehlgeschlagen"], "wiederverwendet": z["wiederverwendet"],
                "offen": max(0, z["gesamt"] - z["fertig"]), "aktuell": [l.datei["name"] for l in self._aktiv.values()], "laeuft": self.lauf_id is not None,
                "abbrechend": self.lauf_id is not None and self._abbruch}

    def beenden_erzwingen(self) -> None:
        """Beim Schließen des Programms: alle Prüfprozesse beenden und auf ihr Ende warten; es bleibt kein Hintergrundprozess zurück."""
        self._abbruch = True
        self._offen = []
        for l in list(self._aktiv.values()):
            l.abgebrochen = True
            l.timer.stop()
            l.speicher_timer.stop()
            l.prozess.kill()
        for l in list(self._aktiv.values()):
            l.prozess.waitForFinished(2000)
            if l.auftrag["id"] in self._aktiv:
                self._abschliessen(l, None, "abgebrochen")
        if self.lauf_id is not None:
            self.db.auftraege_abbrechen(self.lauf_id)
            self.db.lauf_status(self.lauf_id, "abgebrochen")
            self.lauf_id = None
        if self._arbeitsordner:
            shutil.rmtree(self._arbeitsordner, ignore_errors=True)
            self._arbeitsordner = None
