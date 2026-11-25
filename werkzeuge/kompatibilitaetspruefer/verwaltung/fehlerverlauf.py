"""Fehlergruppen, Prüfverlauf und Korrekturverfolgung.

Aus den tatsächlich gespeicherten Prüfergebnissen werden Fehlergruppen gebildet (gleiche Dateiformat-, Prüfart-, Fehlerart- und Prüfpunkt-Kennung, **nicht** ähnlicher Meldungstext),
priorisiert und über mehrere ausdrücklich gestartete Prüfläufe hinweg verfolgt. Jeder abgeschlossene Prüflauf wird unveränderlich als Momentaufnahme festgehalten; frühere Ergebnisse
werden nie überschrieben. Der Verlauf liegt in derselben SQLite-Datei wie die Sitzungsdaten, aber in eigenen Tabellen: Der saubere Programmstart (``sitzung_zuruecksetzen``) berührt ihn nicht.

Grundsätze:
* Der Ursachenbereich einer Gruppe ist immer nur eine **Vermutung**, bis der Benutzer ihn ausdrücklich als bestätigt markiert.
* Eine Behebung gilt erst als bestätigt, wenn ein erneuter, vergleichbarer Prüflauf (gleiche Datei, gleiche Referenz, gleiche Prüfkonfiguration) die Abweichung nicht mehr zeigt
  und **alle** Dokumente der Gruppe erneut geprüft wurden. Eine Korrekturmeldung (auch einer KI) allein ändert nur den Bearbeitungsstatus.
* Es werden keine Werte erfunden: Alle Zahlen stammen aus gespeicherten Ergebnissen.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time

from kompatibilitaetspruefer.pruefung import klassifikation as K

SCHEMA = """
CREATE TABLE IF NOT EXISTS verlauf_laeufe (id INTEGER PRIMARY KEY, zeit REAL, lunivo_version TEXT, konfig_hash TEXT, konfig_json TEXT, anzahl_dateien INTEGER);
CREATE TABLE IF NOT EXISTS verlauf_ergebnisse (id INTEGER PRIMARY KEY, vlauf_id INTEGER REFERENCES verlauf_laeufe(id) ON DELETE CASCADE, pfad TEXT, name TEXT,
    endung TEXT, programm TEXT DEFAULT '', art TEXT, status TEXT, fehlerart TEXT DEFAULT '', schwere TEXT DEFAULT 'hinweis', beschreibung TEXT DEFAULT '',
    datei_stamp TEXT DEFAULT '', referenz_stamp TEXT DEFAULT '', konfig_hash TEXT DEFAULT '', referenz TEXT DEFAULT 'keine', referenz_json TEXT DEFAULT '{}',
    fehlerzahl INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS verlauf_erg_lauf ON verlauf_ergebnisse(vlauf_id, pfad, art);
CREATE TABLE IF NOT EXISTS verlauf_befunde (id INTEGER PRIMARY KEY, vergebnis_id INTEGER REFERENCES verlauf_ergebnisse(id) ON DELETE CASCADE, gruppe_schluessel TEXT,
    punkt TEXT, status TEXT, fehlerart TEXT, schwere TEXT, beschreibung TEXT, soll TEXT, ist TEXT, seite INTEGER, element TEXT);
CREATE INDEX IF NOT EXISTS verlauf_bef_erg ON verlauf_befunde(vergebnis_id);
CREATE INDEX IF NOT EXISTS verlauf_bef_gr ON verlauf_befunde(gruppe_schluessel);
CREATE TABLE IF NOT EXISTS fehlergruppen (schluessel TEXT PRIMARY KEY, gruppe_id TEXT, endung TEXT, art TEXT, fehlerart TEXT, punkt TEXT, bereich TEXT,
    status TEXT DEFAULT 'neu', ursache TEXT DEFAULT 'vermutet', erstellt REAL, geaendert REAL, notiz TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS korrekturen (id INTEGER PRIMARY KEY, gruppe_schluessel TEXT, zeit REAL, beschreibung TEXT DEFAULT '', module TEXT DEFAULT '',
    lunivo_version TEXT DEFAULT '', quelle TEXT DEFAULT 'Benutzer (Meldung, nicht nachgewiesen)', pruefstatus TEXT DEFAULT 'ausstehend');
CREATE INDEX IF NOT EXISTS korrekturen_gr ON korrekturen(gruppe_schluessel);
"""

STATUS_NAMEN = {"neu": "Neu erkannt", "vorgesehen": "Zur Untersuchung vorgesehen", "bearbeitung": "In Bearbeitung", "korrektur": "Korrektur gemeldet",
                "pruefen": "Erneute Prüfung erforderlich", "behoben": "Behebung bestätigt", "weiter": "Weiterhin vorhanden", "erneut": "Erneut aufgetreten",
                "nicht_reproduzierbar": "Nicht reproduzierbar"}
STATUS_REIHE = tuple(STATUS_NAMEN)
UNBEARBEITET = ("neu", "erneut")                                       # „bisher unbearbeitet“
NACHPRUEFBAR = ("bearbeitung", "korrektur", "pruefen", "weiter", "erneut")      # hier kann eine erneute Prüfung die Behebung bestätigen
OFFEN = ("neu", "vorgesehen", "bearbeitung", "korrektur", "pruefen", "weiter", "erneut")
URSACHE_NAMEN = {"vermutet": "nur vermutet", "bestaetigt": "bestätigt"}

KLASSEN_NAMEN = {"behoben": "Behoben", "verbessert": "Verbessert", "unveraendert": "Unverändert", "verschlechtert": "Verschlechtert", "neu": "Neuer Fehler",
                 "nicht_vergleichbar": "Nicht vergleichbar", "nicht_durchgefuehrt": "Nicht erneut geprüft"}

_STATUS_RANG = {K.BESTANDEN: 0, K.TEILWEISE: 1, "nicht_pruefbar": 1, K.AUFFAELLIG: 3, K.FEHLGESCHLAGEN: 4}
_SCHWERE_WERT = {"kritisch": 4, "schwer": 3, "mittel": 2, "gering": 1}
_SCHWERE_PUNKTE = {"kritisch": 100, "schwer": 60, "mittel": 30, "gering": 10, "hinweis": 0}
_OEFFNEN_SPEICHERN = ("Importfehler", "Exportfehler", "Roundtrip-Fehler", "Technischer Prüffehler")
_SPAETE_ARTEN = ("layout", "format", "export", "roundtrip", "darstellung")

_BEREICH_STICHWORTE = (("tabell", "Tabellen"), ("bild", "Bilder"), ("umbruch", "Seitenumbrüche"), ("kopf", "Kopf- und Fußzeilen"), ("fuß", "Kopf- und Fußzeilen"),
                       ("fuss", "Kopf- und Fußzeilen"), ("vorlage", "Formatvorlagen"), ("stil", "Formatvorlagen"), ("zeilen", "Textsatz"), ("schrift", "Textsatz"))
_BEREICH_ART = {"struktur": "Dokumentmodell", "format": "Formatvorlagen", "layout": "Layout", "export": "Export", "roundtrip": "Roundtrip", "darstellung": "Rendering"}


def _t(x) -> str:
    return "" if x is None else str(x)


def format_von(endung: str) -> str:
    return (endung or "").lstrip(".").lower() or "unbekannt"


def schluessel_fuer(endung: str, art: str, fehlerart: str, punkt: str) -> str:
    """Gruppenschlüssel aus strukturierten Feldern. Zahlen im Prüfpunkt werden vereinheitlicht; Meldungstexte und Messwerte gehen nie ein."""
    p = re.sub(r"\d+", "#", (punkt or "").strip().lower())
    return f"{format_von(endung)}|{art}|{fehlerart}|{p}"


def gruppen_id(schluessel: str) -> str:
    return "FG-" + hashlib.sha1(schluessel.encode("utf-8")).hexdigest()[:8].upper()


def vermuteter_bereich(fmt: str, art: str, punkt: str) -> str:
    """Technische Vermutung des Ursachenbereichs (keine Diagnose)."""
    p = (punkt or "").lower()
    for wort, bereich in _BEREICH_STICHWORTE:
        if wort in p:
            return bereich
    if art == "import":
        return f"{fmt.upper()}-Import"
    return _BEREICH_ART.get(art, "Nicht zuordenbar")


def _zahl(x):
    try:
        return float(str(x).replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def fehlerbefunde(rec: dict) -> list[dict]:
    """Die tatsächlich abweichenden Prüfpunkte eines Ergebnisses; fehlen sie bei einem auffälligen/fehlgeschlagenen Ergebnis, steht ein Gesamteintrag mit den Ergebnisdaten."""
    if rec.get("status") not in (K.AUFFAELLIG, K.FEHLGESCHLAGEN):
        return []
    fb = [b for b in rec.get("befunde", []) if b.get("status") == K.ABWEICHEND]
    if not fb:
        fb = [{"punkt": "Gesamtergebnis", "status": K.ABWEICHEND, "fehlerart": rec.get("fehlerart") or "Nicht näher bezeichnet", "schwere": rec.get("schwere") or "mittel",
               "beschreibung": rec.get("beschreibung", ""), "soll": "", "ist": "", "seite": None, "element": ""}]
    return fb


def _ist_verlust(art: str, b: dict) -> bool:
    if art in ("layout", "darstellung"):
        return False
    soll, ist = _zahl(b.get("soll")), _zahl(b.get("ist"))
    return soll is not None and ist is not None and soll > 0 and ist < soll


class Fehlerverlauf:
    def __init__(self, db):
        self.db = db
        with db.sperre:
            db.db.executescript(SCHEMA)
            db.db.commit()

    # ---- Datenzugriff --------------------------------------------------------------------------------------------
    def _q(self, sql: str, par=()) -> list[dict]:
        with self.db.sperre:
            return [dict(r) for r in self.db.db.execute(sql, par).fetchall()]

    def _x(self, sql: str, par=()) -> None:
        with self.db.sperre:
            self.db.db.execute(sql, par)
            self.db.db.commit()

    # ---- Datensätze (aus der laufenden Sitzung oder einer Momentaufnahme) --------------------------------------------
    def datensaetze_live(self) -> list[dict]:
        """Alle Ergebnisse der aktuellen Sitzung mit ihren Prüfpunkten."""
        refs = self.db.alle_referenzen()
        zeilen = self._q("SELECT e.id AS eid, e.datei_id, d.name, d.pfad, d.endung, d.programm, e.art, e.status, e.fehlerart, e.schwere, e.beschreibung, e.datei_stamp, "
                         "e.referenz_stamp, e.konfig_hash, e.bilder_json, e.zeit FROM ergebnisse e JOIN dateien d ON d.id=e.datei_id ORDER BY d.name COLLATE NOCASE, e.art")
        aus = []
        for z in zeilen:
            r = refs.get(z["datei_id"]) or {}
            try:
                bilder = json.loads(z.pop("bilder_json") or "{}")
            except ValueError:
                bilder = {}
            z["bilder"] = bilder
            z["referenz"] = "visuell" if (r.get("pdf") or r.get("bilder")) else ("strukturell" if r else "keine")
            z["referenz_json"] = {k: v for k, v in r.items() if k not in ("datei_id",)}
            z["befunde"] = [dict(b) for b in self.db.befunde(z["eid"])]
            aus.append(z)
        return aus

    def datensaetze_verlauf(self, lauf_id: int) -> list[dict]:
        aus = []
        for z in self._q("SELECT * FROM verlauf_ergebnisse WHERE vlauf_id=? ORDER BY name COLLATE NOCASE, art", (lauf_id,)):
            z["befunde"] = self._q("SELECT * FROM verlauf_befunde WHERE vergebnis_id=? ORDER BY id", (z["id"],))
            try:
                z["referenz_json"] = json.loads(z.get("referenz_json") or "{}")
            except ValueError:
                z["referenz_json"] = {}
            z["bilder"] = {}
            aus.append(z)
        return aus

    # ---- Fehlergruppen ---------------------------------------------------------------------------------------------
    def gruppen_aus(self, datensaetze: list[dict], registrieren: bool = True) -> list[dict]:
        """Bildet die Fehlergruppen, ergänzt Bearbeitungsstatus und Korrekturen aus dem Verlauf und sortiert nach Priorität (höchste zuerst)."""
        gr: dict[str, dict] = {}
        for rec in datensaetze:
            for b in fehlerbefunde(rec):
                fehlerart = b.get("fehlerart") or rec.get("fehlerart") or "Nicht näher bezeichnet"
                punkt = b.get("punkt") or "Gesamtergebnis"
                s = schluessel_fuer(rec["endung"], rec["art"], fehlerart, punkt)
                g = gr.get(s)
                if g is None:
                    fmt = format_von(rec["endung"])
                    g = gr[s] = {"schluessel": s, "gruppe_id": gruppen_id(s), "endung": rec["endung"], "format": fmt, "art": rec["art"], "fehlerart": fehlerart, "punkt": punkt,
                                 "bereich": vermuteter_bereich(fmt, rec["art"], punkt), "schwere": "hinweis", "dokumente": {}, "beispiele": [], "seiten": set(),
                                 "referenzen": {"keine": 0, "strukturell": 0, "visuell": 0}, "inhaltsverlust": False, "oeffnen_speichern": False}
                g["schwere"] = K.schwerer(g["schwere"], b.get("schwere") or "mittel")
                d = g["dokumente"].get(rec["pfad"])
                if d is None:
                    d = g["dokumente"][rec["pfad"]] = {"pfad": rec["pfad"], "name": rec["name"], "referenz": rec.get("referenz", "keine"), "arten": set()}
                    g["referenzen"][rec.get("referenz", "keine")] = g["referenzen"].get(rec.get("referenz", "keine"), 0) + 1
                d["arten"].add(rec["art"])
                try:
                    if b.get("seite"):
                        g["seiten"].add(int(b["seite"]))
                except (TypeError, ValueError):
                    pass
                if len(g["beispiele"]) < 8:
                    g["beispiele"].append({"dokument": rec["name"], "pfad": rec["pfad"], "seite": b.get("seite"), "element": b.get("element", ""), "soll": _t(b.get("soll")),
                                           "ist": _t(b.get("ist")), "beschreibung": b.get("beschreibung", ""), "schwere": b.get("schwere", "")})
                if _ist_verlust(rec["art"], b):
                    g["inhaltsverlust"] = True
                if fehlerart in _OEFFNEN_SPEICHERN:
                    g["oeffnen_speichern"] = True
        gruppen = list(gr.values())
        self._bewerten(gruppen)
        if registrieren:
            self._registrieren(gruppen)
        reg = {r["schluessel"]: r for r in self._q("SELECT * FROM fehlergruppen")}
        korr: dict[str, list[dict]] = {}
        for k in self._q("SELECT * FROM korrekturen ORDER BY zeit"):
            korr.setdefault(k["gruppe_schluessel"], []).append(k)
        for g in gruppen:
            r = reg.get(g["schluessel"], {})
            g["status"] = r.get("status", "neu")
            g["ursache"] = r.get("ursache", "vermutet")
            g["notiz"] = r.get("notiz", "")
            g["korrekturen"] = korr.get(g["schluessel"], [])
            g["dokumentliste"] = sorted(g["dokumente"].values(), key=lambda d: d["name"].casefold())
            g["anzahl"] = len(g["dokumentliste"])
        return gruppen

    @staticmethod
    def _bewerten(gruppen: list[dict]) -> None:
        """Priorität nach nachvollziehbaren Kriterien; jede Punktvergabe wird mit Begründung festgehalten."""
        docs = {g["schluessel"]: set(g["dokumente"]) for g in gruppen}
        for g in gruppen:
            gruende: list[tuple[int, str]] = []
            p = _SCHWERE_PUNKTE.get(g["schwere"], 0)
            gruende.append((p, f"Schweregrad {g['schwere']}"))
            if g["inhaltsverlust"]:
                gruende.append((40, "Hinweis auf Inhaltsverlust (Sollwert größer als Istwert)"))
            if g["oeffnen_speichern"]:
                gruende.append((40, "Fehler beim Öffnen oder Speichern"))
            n = len(g["dokumente"])
            gruende.append((min(40, round(12 * math.log2(1 + n))), f"Häufigkeit: {n} betroffene Dokumente"))
            if g["format"] == "docx":
                gruende.append((8, "DOCX hat bei vergleichbarer Schwere Vorrang"))
            if g["art"] in ("import", "struktur"):
                folge = sum(1 for h in gruppen if h is not g and h["art"] in _SPAETE_ARTEN and docs[h["schluessel"]] & docs[g["schluessel"]])
                if folge:
                    gruende.append((min(20, 5 * folge), f"Mögliche Folgefehler: {folge} weitere Fehlergruppen betreffen dieselben Dokumente"))
            g["prioritaet"] = sum(x for x, _ in gruende)
            g["prioritaet_gruende"] = [f"+{x} {text}" for x, text in gruende if x or text.startswith("Schweregrad")]
        gruppen.sort(key=lambda g: (-g["prioritaet"], g["gruppe_id"]))
        for i, g in enumerate(gruppen, 1):
            g["rang"] = i

    def _registrieren(self, gruppen: list[dict]) -> None:
        jetzt = time.time()
        with self.db.sperre:
            self.db.db.executemany("INSERT OR IGNORE INTO fehlergruppen(schluessel,gruppe_id,endung,art,fehlerart,punkt,bereich,status,ursache,erstellt,geaendert) "
                                   "VALUES(?,?,?,?,?,?,?,'neu','vermutet',?,?)",
                                   [(g["schluessel"], g["gruppe_id"], g["endung"], g["art"], g["fehlerart"], g["punkt"], g["bereich"], jetzt, jetzt) for g in gruppen])
            self.db.db.commit()

    # ---- Bearbeitungsstatus und Korrekturen --------------------------------------------------------------------------
    def status_setzen(self, schluessel: list[str], status: str) -> None:
        if status not in STATUS_NAMEN:
            raise ValueError(f"Unbekannter Status: {status}")
        with self.db.sperre:
            self.db.db.executemany("UPDATE fehlergruppen SET status=?, geaendert=? WHERE schluessel=?", [(status, time.time(), s) for s in schluessel])
            self.db.db.commit()

    def ursache_setzen(self, schluessel: list[str], ursache: str, notiz: str = "") -> None:
        if ursache not in URSACHE_NAMEN:
            raise ValueError(f"Unbekannter Ursachenstatus: {ursache}")
        with self.db.sperre:
            self.db.db.executemany("UPDATE fehlergruppen SET ursache=?, notiz=CASE WHEN ?!='' THEN ? ELSE notiz END, geaendert=? WHERE schluessel=?",
                                   [(ursache, notiz, notiz, time.time(), s) for s in schluessel])
            self.db.db.commit()

    def korrektur_melden(self, schluessel: list[str], beschreibung: str, module: str, lunivo_version: str, quelle: str = "Benutzer (Meldung, nicht nachgewiesen)") -> None:
        """Hält eine gemeldete Korrektur fest. Das ist eine Meldung, kein Nachweis: Die Gruppe wechselt auf „Korrektur gemeldet“, nicht auf „behoben“."""
        jetzt = time.time()
        with self.db.sperre:
            self.db.db.executemany("INSERT INTO korrekturen(gruppe_schluessel,zeit,beschreibung,module,lunivo_version,quelle,pruefstatus) VALUES(?,?,?,?,?,?, 'ausstehend')",
                                   [(s, jetzt, beschreibung, module, lunivo_version, quelle) for s in schluessel])
            self.db.db.executemany("UPDATE fehlergruppen SET status='korrektur', geaendert=? WHERE schluessel=? AND status!='behoben'", [(jetzt, s) for s in schluessel])
            self.db.db.commit()

    # ---- Prüfläufe (Momentaufnahmen) ---------------------------------------------------------------------------------
    def laeufe(self) -> list[dict]:
        """Alle festgehaltenen Prüfläufe, neueste zuerst."""
        return self._q("SELECT * FROM verlauf_laeufe ORDER BY id DESC")

    def letzter_lauf(self) -> int | None:
        r = self._q("SELECT MAX(id) AS m FROM verlauf_laeufe")
        return r[0]["m"] if r and r[0]["m"] is not None else None

    def lauf_festhalten(self, konfig: dict, konfig_hash: str, version: str) -> int | None:
        """Hält den Stand der aktuellen Sitzung als neuen, unveränderlichen Prüflauf fest und aktualisiert danach die Bearbeitungsstatus."""
        daten = [d for d in self.datensaetze_live() if d["status"] not in (K.ABGEBROCHEN, K.OFFEN)]
        if not daten:
            return None
        with self.db.sperre:
            cur = self.db.db.execute("INSERT INTO verlauf_laeufe(zeit,lunivo_version,konfig_hash,konfig_json,anzahl_dateien) VALUES(?,?,?,?,?)",
                                     (time.time(), version, konfig_hash, json.dumps(konfig, default=str), len({d["pfad"] for d in daten})))
            lid = cur.lastrowid
            for d in daten:
                fb = fehlerbefunde(d)
                cur = self.db.db.execute(
                    "INSERT INTO verlauf_ergebnisse(vlauf_id,pfad,name,endung,programm,art,status,fehlerart,schwere,beschreibung,datei_stamp,referenz_stamp,konfig_hash,referenz,"
                    "referenz_json,fehlerzahl) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (lid, d["pfad"], d["name"], d["endung"], d.get("programm", ""), d["art"], d["status"], d.get("fehlerart", ""), d.get("schwere", "hinweis"),
                     d.get("beschreibung", ""), d.get("datei_stamp", ""), d.get("referenz_stamp", ""), d.get("konfig_hash", ""), d.get("referenz", "keine"),
                     json.dumps(d.get("referenz_json", {}), default=str), len(fb)))
                eid = cur.lastrowid
                zeilen = []
                for b in fb:
                    fehlerart = b.get("fehlerart") or d.get("fehlerart") or "Nicht näher bezeichnet"
                    punkt = b.get("punkt") or "Gesamtergebnis"
                    zeilen.append((eid, schluessel_fuer(d["endung"], d["art"], fehlerart, punkt), punkt, b.get("status", ""), fehlerart, b.get("schwere") or "mittel",
                                   b.get("beschreibung", ""), _t(b.get("soll")), _t(b.get("ist")), b.get("seite"), b.get("element", "")))
                self.db.db.executemany("INSERT INTO verlauf_befunde(vergebnis_id,gruppe_schluessel,punkt,status,fehlerart,schwere,beschreibung,soll,ist,seite,element) "
                                       "VALUES(?,?,?,?,?,?,?,?,?,?,?)", zeilen)
            self.db.db.commit()
        self._status_nach_pruefung(lid)
        return lid

    def _status_nach_pruefung(self, lid: int) -> None:
        """Aktualisiert die Bearbeitungsstatus anhand des neuen Prüflaufs. „Behoben“ wird nur bei lückenlosem, vergleichbarem Nachweis gesetzt (siehe Modulkopf)."""
        gruppen = self.gruppen_aus(self.datensaetze_verlauf(lid))                       # registriert neue Gruppen als „neu“
        neu_eintraege = {(e["pfad"], e["art"]): e for e in self._q("SELECT * FROM verlauf_ergebnisse WHERE vlauf_id=?", (lid,))}
        keys_je_eintrag: dict[int, set] = {}
        for r in self._q("SELECT b.gruppe_schluessel AS s, b.vergebnis_id AS v FROM verlauf_befunde b JOIN verlauf_ergebnisse e ON e.id=b.vergebnis_id WHERE e.vlauf_id=?", (lid,)):
            keys_je_eintrag.setdefault(r["v"], set()).add(r["s"])
        vorhanden = {g["schluessel"] for g in gruppen}
        jetzt = time.time()
        for r in self._q("SELECT schluessel, status FROM fehlergruppen"):
            s, status = r["schluessel"], r["status"]
            if status == "behoben" and s in vorhanden:
                self._x("UPDATE fehlergruppen SET status='erneut', geaendert=? WHERE schluessel=?", (jetzt, s))
                continue
            if status not in NACHPRUEFBAR:
                continue
            alt = self._q("SELECT MAX(e.vlauf_id) AS m FROM verlauf_befunde b JOIN verlauf_ergebnisse e ON e.id=b.vergebnis_id WHERE b.gruppe_schluessel=? AND e.vlauf_id<?", (s, lid))
            if not alt or alt[0]["m"] is None:
                continue
            alte = self._q("SELECT DISTINCT e.pfad, e.art, e.datei_stamp, e.referenz_stamp, e.konfig_hash FROM verlauf_befunde b JOIN verlauf_ergebnisse e ON e.id=b.vergebnis_id "
                           "WHERE b.gruppe_schluessel=? AND e.vlauf_id=?", (s, alt[0]["m"]))
            noch = behoben = fehlt = unvergleichbar = 0
            for o in alte:
                n = neu_eintraege.get((o["pfad"], o["art"]))
                if n is None:
                    fehlt += 1
                elif (n["datei_stamp"], n["referenz_stamp"], n["konfig_hash"]) != (o["datei_stamp"], o["referenz_stamp"], o["konfig_hash"]):
                    unvergleichbar += 1
                elif s in keys_je_eintrag.get(n["id"], set()):
                    noch += 1
                else:
                    behoben += 1
            if noch:
                self._x("UPDATE fehlergruppen SET status='weiter', geaendert=? WHERE schluessel=?", (jetzt, s))
                self._x("UPDATE korrekturen SET pruefstatus='Abweichung weiterhin vorhanden' WHERE gruppe_schluessel=? AND pruefstatus='ausstehend'", (s,))
            elif behoben and not fehlt and not unvergleichbar:
                self._x("UPDATE fehlergruppen SET status='behoben', geaendert=? WHERE schluessel=?", (jetzt, s))
                self._x("UPDATE korrekturen SET pruefstatus='durch erneute Prüfung bestätigt' WHERE gruppe_schluessel=? AND pruefstatus='ausstehend'", (s,))

    # ---- Vergleich zweier Prüfläufe -----------------------------------------------------------------------------------
    def vergleiche_laeufe(self, alt_id: int, neu_id: int) -> dict:
        """Vorher-Nachher-Vergleich je Dokument und Prüfart. Nur vergleichbare Paare (gleiche Datei, Referenz und Prüfkonfiguration) werden bewertet."""
        lauf = {r["id"]: r for r in self._q("SELECT * FROM verlauf_laeufe WHERE id IN (?,?)", (alt_id, neu_id))}
        alt = {(e["pfad"], e["art"]): e for e in self._q("SELECT * FROM verlauf_ergebnisse WHERE vlauf_id=?", (alt_id,))}
        neu = {(e["pfad"], e["art"]): e for e in self._q("SELECT * FROM verlauf_ergebnisse WHERE vlauf_id=?", (neu_id,))}
        gruppen: dict[int, list[str]] = {}
        for r in self._q("SELECT b.vergebnis_id AS v, b.gruppe_schluessel AS s FROM verlauf_befunde b JOIN verlauf_ergebnisse e ON e.id=b.vergebnis_id WHERE e.vlauf_id IN (?,?)", (alt_id, neu_id)):
            gid = gruppen_id(r["s"])
            if gid not in gruppen.setdefault(r["v"], []):
                gruppen[r["v"]].append(gid)
        eintraege = []
        for key in sorted(set(alt) | set(neu), key=lambda k: (k[0].casefold(), k[1])):
            a, n = alt.get(key), neu.get(key)
            ref = n or a
            e = {"pfad": key[0], "name": ref["name"], "endung": ref["endung"], "art": key[1], "alt_status": a["status"] if a else "", "neu_status": n["status"] if n else "",
                 "gruppen": sorted(set((gruppen.get(a["id"], []) if a else []) + (gruppen.get(n["id"], []) if n else [])))}
            if a and not n:
                e.update(klasse="nicht_durchgefuehrt", grund="im neuen Lauf nicht erneut geprüft")
            elif n and not a:
                e.update(klasse="nicht_vergleichbar", grund="im früheren Lauf nicht geprüft (kein Vergleichswert)")
            else:
                e.update(self._klasse(a, n))
            eintraege.append(e)
        zaehler = {k: 0 for k in KLASSEN_NAMEN}
        for e in eintraege:
            zaehler[e["klasse"]] += 1
        hinweise = []
        if alt_id in lauf and neu_id in lauf and lauf[alt_id]["lunivo_version"] == lauf[neu_id]["lunivo_version"]:
            hinweise.append("Beide Läufe haben dieselbe Lunivo-Kennung: Es wurde keine Änderung an den geprüften Lunivo-Komponenten erkannt.")
        if zaehler["nicht_vergleichbar"]:
            hinweise.append(f"{zaehler['nicht_vergleichbar']} Paare sind nicht vergleichbar (Dokument, Referenz oder Prüfkonfiguration geändert, oder Prüfung nicht beurteilbar).")
        return {"alt": lauf.get(alt_id), "neu": lauf.get(neu_id), "eintraege": eintraege, "zaehler": zaehler, "hinweise": hinweise}

    @staticmethod
    def _klasse(a: dict, n: dict) -> dict:
        if (a["datei_stamp"], a["referenz_stamp"], a["konfig_hash"]) != (n["datei_stamp"], n["referenz_stamp"], n["konfig_hash"]):
            grund = ("Dokument geändert" if a["datei_stamp"] != n["datei_stamp"] else "Referenz geändert" if a["referenz_stamp"] != n["referenz_stamp"] else "Prüfkonfiguration geändert")
            return {"klasse": "nicht_vergleichbar", "grund": grund}
        if a["status"] == "nicht_pruefbar" or n["status"] == "nicht_pruefbar":
            return {"klasse": "nicht_vergleichbar", "grund": "Prüfung war nicht beurteilbar"}

        def mass(e: dict) -> tuple:
            r = _STATUS_RANG.get(e["status"], 1)
            return (r, _SCHWERE_WERT.get(e["schwere"], 0) if r >= 3 else 0, e.get("fehlerzahl", 0) if r >= 3 else 0)
        ma, mn = mass(a), mass(n)
        if mn < ma:
            if mn[0] <= 1 and ma[0] >= 3:
                return {"klasse": "behoben", "grund": "zuvor festgestellte Abweichung nicht mehr vorhanden"}
            return {"klasse": "verbessert", "grund": "Abweichung nachweislich geringer"}
        if mn > ma:
            if ma[0] <= 1 and mn[0] >= 3:
                return {"klasse": "neu", "grund": "zuvor unauffällige Prüfung schlägt nun fehl"}
            return {"klasse": "verschlechtert", "grund": "Abweichung größer als zuvor"}
        return {"klasse": "unveraendert", "grund": "Abweichung unverändert" if ma[0] >= 3 else "unauffällig wie zuvor"}

    # ---- Entwicklungsübersicht -----------------------------------------------------------------------------------------
    def uebersicht(self) -> dict:
        """Kennzahlen ausschließlich aus gespeicherten Daten."""
        status = {r["status"]: r["n"] for r in self._q("SELECT status, COUNT(*) AS n FROM fehlergruppen GROUP BY status")}
        gruppen = {"gesamt": sum(status.values()), "offen": sum(status.get(s, 0) for s in OFFEN), "behoben": status.get("behoben", 0), "weiter": status.get("weiter", 0),
                   "erneut": status.get("erneut", 0), "nicht_reproduzierbar": status.get("nicht_reproduzierbar", 0)}
        laeufe = []
        rows = self._q("SELECT l.id AS lid, e.pfad, e.endung, e.status FROM verlauf_laeufe l JOIN verlauf_ergebnisse e ON e.vlauf_id=l.id")
        je_lauf: dict[int, dict[str, tuple[str, list[str]]]] = {}
        for r in rows:
            d = je_lauf.setdefault(r["lid"], {}).setdefault(r["pfad"], (r["endung"], []))
            d[1].append(r["status"])
        for l in reversed(self.laeufe()):
            pro_format: dict[str, dict] = {}
            ges = {"bestanden": 0, "auffaellig": 0, "fehlgeschlagen": 0, "andere": 0}
            for endung, stati in je_lauf.get(l["id"], {}).values():
                s = K.gesamt_status(stati)
                k = s if s in ("bestanden", "auffaellig", "fehlgeschlagen") else "andere"
                f = pro_format.setdefault(format_von(endung), {"gesamt": 0, "bestanden": 0, "auffaellig": 0, "fehlgeschlagen": 0, "andere": 0})
                f["gesamt"] += 1
                f[k] += 1
                ges[k] += 1
            laeufe.append({"id": l["id"], "zeit": l["zeit"], "version": l["lunivo_version"], "dateien": l["anzahl_dateien"], **ges, "pro_format": pro_format})
        letzter = None
        ids = [l["id"] for l in self.laeufe()[:2]]
        if len(ids) == 2:
            letzter = self.vergleiche_laeufe(ids[1], ids[0])["zaehler"]
        return {"gruppen": gruppen, "laeufe": laeufe, "letzter_vergleich": letzter}
