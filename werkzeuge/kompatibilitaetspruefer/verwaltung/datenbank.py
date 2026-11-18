"""Persistente Ergebnisverwaltung (SQLite). Gespeichert werden Dateiinformationen, Referenzzuordnungen, Prüfergebnisse, Befunde, Läufe und der
tatsächliche Bearbeitungsstand der Warteschlange. Dokumentinhalte werden nicht gespeichert, nur Zählwerte, Beschreibungen und Verweise auf
Vergleichsbilder im Cache (jedes Bild liegt nur einmal dort)."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS dateien (id INTEGER PRIMARY KEY, pfad TEXT UNIQUE NOT NULL, name TEXT, endung TEXT, groesse INTEGER, mtime_ns INTEGER,
    programm TEXT DEFAULT '', hinzugefuegt REAL);
CREATE TABLE IF NOT EXISTS referenzen (datei_id INTEGER PRIMARY KEY REFERENCES dateien(id) ON DELETE CASCADE, pdf TEXT DEFAULT '', bilder TEXT DEFAULT '',
    programm TEXT DEFAULT '', programmversion TEXT DEFAULT '', betriebssystem TEXT DEFAULT '', schriften TEXT DEFAULT '', seiten_erwartet INTEGER,
    erwartet_json TEXT DEFAULT '{}', notiz TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS laeufe (id INTEGER PRIMARY KEY, start REAL, ende REAL, status TEXT, konfig_json TEXT, konfig_hash TEXT, lunivo_version TEXT,
    arten_json TEXT);
CREATE TABLE IF NOT EXISTS auftraege (id INTEGER PRIMARY KEY, lauf_id INTEGER REFERENCES laeufe(id) ON DELETE CASCADE, datei_id INTEGER, arten_json TEXT,
    status TEXT DEFAULT 'offen');
CREATE INDEX IF NOT EXISTS auftraege_lauf ON auftraege(lauf_id, status);
CREATE TABLE IF NOT EXISTS ergebnisse (id INTEGER PRIMARY KEY, datei_id INTEGER REFERENCES dateien(id) ON DELETE CASCADE, art TEXT, status TEXT,
    fehlerart TEXT DEFAULT '', schwere TEXT DEFAULT 'hinweis', beschreibung TEXT DEFAULT '', seite INTEGER, element TEXT DEFAULT '',
    werte_json TEXT DEFAULT '{}', bilder_json TEXT DEFAULT '{}', datei_stamp TEXT, referenz_stamp TEXT, konfig_hash TEXT, lunivo_version TEXT,
    lauf_id INTEGER, zeit REAL, dauer REAL, UNIQUE(datei_id, art));
CREATE INDEX IF NOT EXISTS ergebnisse_datei ON ergebnisse(datei_id);
CREATE TABLE IF NOT EXISTS befunde (id INTEGER PRIMARY KEY, ergebnis_id INTEGER REFERENCES ergebnisse(id) ON DELETE CASCADE, punkt TEXT, status TEXT,
    fehlerart TEXT, schwere TEXT, beschreibung TEXT, soll TEXT, ist TEXT, seite INTEGER, element TEXT);
CREATE INDEX IF NOT EXISTS befunde_ergebnis ON befunde(ergebnis_id);
"""
ENDGUELTIG = ("bestanden", "teilweise", "auffaellig", "nicht_pruefbar")      # wiederverwendbar; Fehlschläge und Abbrüche werden neu geprüft


def datei_stamp(pfad: str) -> str:
    try:
        st = os.stat(pfad)
        return f"{st.st_size}:{st.st_mtime_ns}"
    except OSError:
        return "fehlt"


def _text(x) -> str:
    return json.dumps(x, ensure_ascii=False, default=str) if not isinstance(x, str) and x is not None else (x or "")


class Datenbank:
    def __init__(self, pfad: str):
        self.pfad = pfad
        self.sperre = threading.RLock()
        self.db = sqlite3.connect(pfad, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.db.commit()

    def schliessen(self) -> None:
        with self.sperre:
            self.db.commit()
            self.db.close()

    def _ex(self, sql: str, par=()):
        with self.sperre:
            return self.db.execute(sql, par)

    def _alle(self, sql: str, par=()) -> list:
        with self.sperre:
            return self.db.execute(sql, par).fetchall()

    def _commit(self) -> None:
        with self.sperre:
            self.db.commit()

    # ---- Dateien -------------------------------------------------------------------------------------------------
    def dateien_hinzufuegen(self, pfade: list[str]) -> int:
        neu = 0
        with self.sperre:
            for p in pfade:
                p = os.path.abspath(p)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                cur = self.db.execute("INSERT OR IGNORE INTO dateien(pfad,name,endung,groesse,mtime_ns,hinzugefuegt) VALUES(?,?,?,?,?,?)",
                                      (p, os.path.basename(p), os.path.splitext(p)[1].lower(), st.st_size, st.st_mtime_ns, time.time()))
                neu += cur.rowcount
            self.db.commit()
        return neu

    def dateien_entfernen(self, ids: list[int]) -> None:
        with self.sperre:
            self.db.executemany("DELETE FROM dateien WHERE id=?", [(i,) for i in ids])
            self.db.commit()

    def dateien_leeren(self) -> None:
        with self.sperre:
            self.db.execute("DELETE FROM dateien")
            self.db.commit()

    def dateien(self) -> list[dict]:
        return [dict(r) for r in self._alle("SELECT * FROM dateien ORDER BY name COLLATE NOCASE")]

    def datei(self, datei_id: int) -> dict | None:
        r = self._alle("SELECT * FROM dateien WHERE id=?", (datei_id,))
        return dict(r[0]) if r else None

    def programm_setzen(self, ids: list[int], programm: str) -> None:
        with self.sperre:
            self.db.executemany("UPDATE dateien SET programm=? WHERE id=?", [(programm, i) for i in ids])
            self.db.commit()

    def datei_aktualisieren(self, datei_id: int) -> None:
        d = self.datei(datei_id)
        if d and os.path.exists(d["pfad"]):
            st = os.stat(d["pfad"])
            self._ex("UPDATE dateien SET groesse=?, mtime_ns=? WHERE id=?", (st.st_size, st.st_mtime_ns, datei_id))
            self._commit()

    # ---- Referenzen ----------------------------------------------------------------------------------------------
    def referenz(self, datei_id: int) -> dict | None:
        r = self._alle("SELECT * FROM referenzen WHERE datei_id=?", (datei_id,))
        if not r:
            return None
        d = dict(r[0])
        try:
            d["erwartet"] = json.loads(d.pop("erwartet_json") or "{}")
        except ValueError:
            d["erwartet"] = {}
        return d

    def alle_referenzen(self) -> dict[int, dict]:
        aus = {}
        for r in self._alle("SELECT * FROM referenzen"):
            d = dict(r)
            try:
                d["erwartet"] = json.loads(d.pop("erwartet_json") or "{}")
            except ValueError:
                d["erwartet"] = {}
            aus[d["datei_id"]] = d
        return aus

    def referenz_setzen(self, datei_id: int, r: dict) -> None:
        with self.sperre:
            self.db.execute("INSERT OR REPLACE INTO referenzen(datei_id,pdf,bilder,programm,programmversion,betriebssystem,schriften,seiten_erwartet,"
                            "erwartet_json,notiz) VALUES(?,?,?,?,?,?,?,?,?,?)",
                            (datei_id, r.get("pdf", ""), r.get("bilder", ""), r.get("programm", ""), r.get("programmversion", ""),
                             r.get("betriebssystem", ""), r.get("schriften", ""), r.get("seiten_erwartet"),
                             json.dumps(r.get("erwartet", {}), ensure_ascii=False), r.get("notiz", "")))
            if r.get("programm"):
                self.db.execute("UPDATE dateien SET programm=? WHERE id=?", (r["programm"], datei_id))
            self.db.commit()

    def referenz_loeschen(self, datei_id: int) -> None:
        self._ex("DELETE FROM referenzen WHERE datei_id=?", (datei_id,))
        self._commit()

    def referenz_stamp(self, datei_id: int) -> str:
        """Ändert sich, wenn Zuordnung, erwartete Werte oder die verknüpften Dateien sich ändern."""
        r = self.referenz(datei_id)
        if r is None:
            return "ohne"
        teile = [json.dumps({k: v for k, v in r.items() if k != "datei_id"}, sort_keys=True, default=str)]
        if r.get("pdf"):
            teile.append(datei_stamp(r["pdf"]))
        if r.get("bilder") and os.path.isdir(r["bilder"]):
            teile.append(",".join(f"{n}:{datei_stamp(os.path.join(r['bilder'], n))}" for n in sorted(os.listdir(r["bilder"]))))
        return hashlib.sha1("|".join(teile).encode()).hexdigest()[:16]

    # ---- Ergebnisse ----------------------------------------------------------------------------------------------
    def ergebnis_speichern(self, datei_id: int, art: str, e: dict) -> int:
        """``e``: status, fehlerart, schwere, beschreibung, seite, element, werte, bilder, befunde, stamps. Ersetzt das frühere Ergebnis dieser Art."""
        with self.sperre:
            self.db.execute("DELETE FROM ergebnisse WHERE datei_id=? AND art=?", (datei_id, art))
            cur = self.db.execute(
                "INSERT INTO ergebnisse(datei_id,art,status,fehlerart,schwere,beschreibung,seite,element,werte_json,bilder_json,datei_stamp,referenz_stamp,"
                "konfig_hash,lunivo_version,lauf_id,zeit,dauer) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (datei_id, art, e["status"], e.get("fehlerart", ""), e.get("schwere", "hinweis"), e.get("beschreibung", ""), e.get("seite"),
                 e.get("element", ""), json.dumps(e.get("werte", {}), default=str), json.dumps(e.get("bilder", {})), e.get("datei_stamp", ""),
                 e.get("referenz_stamp", ""), e.get("konfig_hash", ""), e.get("lunivo_version", ""), e.get("lauf_id"), time.time(), e.get("dauer", 0.0)))
            rid = cur.lastrowid
            self.db.executemany("INSERT INTO befunde(ergebnis_id,punkt,status,fehlerart,schwere,beschreibung,soll,ist,seite,element) VALUES(?,?,?,?,?,?,?,?,?,?)",
                                [(rid, b["punkt"], b["status"], b.get("fehlerart", ""), b.get("schwere", "hinweis"), b.get("beschreibung", ""),
                                  _text(b.get("soll")), _text(b.get("ist")), b.get("seite"), b.get("element", "")) for b in e.get("befunde", [])])
            self.db.commit()
        return rid

    def wiederverwendbar(self, datei_id: int, art: str, datei_stamp_: str, referenz_stamp: str, konfig_hash: str, version: str) -> bool:
        r = self._alle("SELECT status,datei_stamp,referenz_stamp,konfig_hash,lunivo_version FROM ergebnisse WHERE datei_id=? AND art=?", (datei_id, art))
        return bool(r) and r[0]["status"] in ENDGUELTIG and (r[0]["datei_stamp"], r[0]["referenz_stamp"], r[0]["konfig_hash"], r[0]["lunivo_version"]) == (
            datei_stamp_, referenz_stamp, konfig_hash, version)

    def ergebnisse_von(self, datei_id: int) -> list[dict]:
        return [dict(r) for r in self._alle("SELECT * FROM ergebnisse WHERE datei_id=? ORDER BY art", (datei_id,))]

    def befunde(self, ergebnis_id: int) -> list[dict]:
        return [dict(r) for r in self._alle("SELECT * FROM befunde WHERE ergebnis_id=? ORDER BY id", (ergebnis_id,))]

    def ergebnis(self, ergebnis_id: int) -> dict | None:
        r = self._alle("SELECT * FROM ergebnisse WHERE id=?", (ergebnis_id,))
        return dict(r[0]) if r else None

    def ergebniszeilen(self) -> list[dict]:
        """Eine Zeile je Ergebnis mit Dateiangaben und dem Referenzzustand — für Ergebnistabelle, Filter und Export."""
        return [dict(r) for r in self._alle(
            "SELECT e.id AS ergebnis_id, e.datei_id, d.name, d.pfad, d.endung, d.programm, e.art, e.status, e.fehlerart, e.schwere, e.beschreibung, "
            "e.seite, e.element, e.konfig_hash, e.lunivo_version, e.zeit, "
            "CASE WHEN r.datei_id IS NULL THEN 'keine' WHEN r.pdf!='' OR r.bilder!='' THEN 'visuell' ELSE 'strukturell' END AS referenz "
            "FROM ergebnisse e JOIN dateien d ON d.id=e.datei_id LEFT JOIN referenzen r ON r.datei_id=d.id ORDER BY d.name COLLATE NOCASE, e.art")]

    def dateistatus(self) -> dict[int, list[str]]:
        aus: dict[int, list[str]] = {}
        for r in self._alle("SELECT datei_id, status FROM ergebnisse"):
            aus.setdefault(r["datei_id"], []).append(r["status"])
        return aus

    def referenzstatus(self) -> dict[int, str]:
        return {r["datei_id"]: ("visuell" if r["pdf"] or r["bilder"] else "strukturell") for r in self._alle("SELECT datei_id,pdf,bilder FROM referenzen")}

    def ergebnisse_loeschen(self, ids: list[int] | None = None) -> None:
        with self.sperre:
            if ids is None:
                self.db.execute("DELETE FROM ergebnisse")
            else:
                self.db.executemany("DELETE FROM ergebnisse WHERE datei_id=?", [(i,) for i in ids])
            self.db.commit()

    # ---- Läufe und Warteschlange (Bearbeitungsstand) -------------------------------------------------------------
    def lauf_neu(self, konfig: dict, konfig_hash: str, version: str, arten: list[str], auftraege: list[tuple[int, list[str]]]) -> int:
        with self.sperre:
            cur = self.db.execute("INSERT INTO laeufe(start,status,konfig_json,konfig_hash,lunivo_version,arten_json) VALUES(?,?,?,?,?,?)",
                                  (time.time(), "laufend", json.dumps(konfig), konfig_hash, version, json.dumps(arten)))
            lid = cur.lastrowid
            self.db.executemany("INSERT INTO auftraege(lauf_id,datei_id,arten_json,status) VALUES(?,?,?,'offen')",
                                [(lid, d, json.dumps(a)) for d, a in auftraege])
            self.db.commit()
        return lid

    def lauf_status(self, lauf_id: int, status: str) -> None:
        self._ex("UPDATE laeufe SET status=?, ende=? WHERE id=?", (status, time.time() if status != "laufend" else None, lauf_id))
        self._commit()

    def auftrag_status(self, auftrag_id: int, status: str) -> None:
        self._ex("UPDATE auftraege SET status=? WHERE id=?", (status, auftrag_id))
        self._commit()

    def offene_auftraege(self, lauf_id: int) -> list[dict]:
        return [dict(r) for r in self._alle("SELECT * FROM auftraege WHERE lauf_id=? AND status IN ('offen','laeuft') ORDER BY id", (lauf_id,))]

    def lauf_zaehler(self, lauf_id: int) -> dict:
        z = {r["status"]: r["n"] for r in self._alle("SELECT status, COUNT(*) AS n FROM auftraege WHERE lauf_id=? GROUP BY status", (lauf_id,))}
        return {"gesamt": sum(z.values()), **z}

    def unterbrochener_lauf(self) -> dict | None:
        """Der jüngste Lauf, der nicht ordentlich endete (Programm beendet oder abgestürzt) und noch offene Aufträge hat."""
        for r in self._alle("SELECT * FROM laeufe WHERE status IN ('laufend','unterbrochen') ORDER BY id DESC"):
            if self.offene_auftraege(r["id"]):
                return dict(r)
        return None

    def auftraege_abbrechen(self, lauf_id: int) -> None:
        self._ex("UPDATE auftraege SET status='abgebrochen' WHERE lauf_id=? AND status IN ('offen','laeuft')", (lauf_id,))
        self._commit()

    def sitzung_zuruecksetzen(self) -> None:
        """Programmstart/„Neue Prüfung“: Dateiliste, Referenzzuordnungen, Ergebnisse und Läufe der Sitzung verwerfen. Dokumente und exportierte Ergebnisse bleiben unberührt."""
        with self.sperre:
            for t in ("befunde", "ergebnisse", "auftraege", "laeufe", "referenzen", "dateien"):
                self.db.execute(f"DELETE FROM {t}")
            self.db.commit()

    def laeufe_abschliessen_verwaist(self) -> None:
        """Beim Programmstart: Aufträge im Zustand „laeuft“ wurden nicht fertig; der Lauf gilt als unterbrochen."""
        with self.sperre:
            self.db.execute("UPDATE auftraege SET status='offen' WHERE status='laeuft'")
            self.db.execute("UPDATE laeufe SET status='unterbrochen' WHERE status='laufend'")
            self.db.commit()
