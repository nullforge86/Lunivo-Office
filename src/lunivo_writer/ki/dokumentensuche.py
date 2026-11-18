"""Lokale Dokumentensuche: Dateien aus vom Benutzer freigegebenen Ordnern in Abschnitte zerlegen, mit SQLite FTS5 durchsuchbar machen
und die besten Abschnitte der KI als Quellen mitgeben. Kein Qt, keine Cloud, kein Hintergrundprozess — der Index wird nur beim Suchen
(mit Zeitgrenze) oder auf Knopfdruck aktualisiert.

Sicherheit: gelesen wird ausschließlich unterhalb der freigegebenen Ordner; symbolische Links werden nicht verfolgt, versteckte Ordner
übersprungen, Zahl und Größe der Dateien sind begrenzt. Das Lesen der Dateiformate steht in ``dokument_abschnitte.py``.
"""
from __future__ import annotations

import os
import re
import sqlite3
import time

ENDUNGEN = (".docx", ".odt", ".rtf", ".txt", ".pdf")
VORGABE = {"an": False, "ordner": [], "anzahl": 4}
MAX_DATEIEN = 20000                      # je Aktualisierung
MAX_DATEI_BYTES = 50 * 1024 * 1024
MAX_ABSCHNITT = 1500                     # Zeichen je Abschnitt; längere werden an Absatzgrenzen geteilt
MIN_ABSCHNITT = 40                       # kürzere Stücke werden dem vorigen Abschnitt angehängt
MAX_TERME = 12
STOPP = frozenset("der die das den dem des ein eine einen einem einer eines und oder aber auch nicht wie was wer wo wann warum welche welcher "
                  "welches ist sind war waren wird werden hat haben mit von für auf aus bei nach zum zur im in an am um über unter dass "
                  "ich du er sie es wir ihr mir mich dir dich sich gibt steht stehen mein dein sein ihre bitte mal noch nur schon".split())
_WORT = re.compile(r"[^\W_]{3,}", re.UNICODE)


def abschnitte_bilden(zeilen) -> list[tuple[str, str]]:
    """Aus ``(ebene, text)`` je Absatz (ebene > 0 = Überschrift) die Abschnitte ``(titel, text)``: ein neuer Abschnitt beginnt bei jeder Überschrift
    und wird bei zu großer Länge an Absatzgrenzen geteilt; sehr kurze Reste hängen am Vorgänger."""
    aus: list[list] = []
    titel, teile, laenge = "Anfang", [], 0

    def abschliessen() -> None:
        nonlocal teile, laenge
        text = "\n".join(teile).strip()
        if text:
            if aus and len(text) < MIN_ABSCHNITT and aus[-1][0] == titel:
                aus[-1][1] += "\n" + text
            else:
                aus.append([titel, text])
        teile, laenge = [], 0

    for ebene, text in zeilen:
        text = (text or "").strip()
        if not text:
            continue
        if ebene:
            abschliessen()
            titel = text[:120]
            teile.append(text)                         # die Überschrift gehört auch in den durchsuchbaren Text
            laenge = len(text)
            continue
        if len(text) > MAX_ABSCHNITT:                  # ein einzelner sehr langer Absatz: für sich, am Satzende oder Leerzeichen geteilt
            abschliessen()
            while len(text) > MAX_ABSCHNITT:
                schnitt = max(text.rfind(". ", 0, MAX_ABSCHNITT), text.rfind(" ", 0, MAX_ABSCHNITT), MAX_ABSCHNITT // 2) + 1
                teile.append(text[:schnitt].strip())
                abschliessen()
                text = text[schnitt:].strip()
        if laenge + len(text) > MAX_ABSCHNITT:
            abschliessen()
        teile.append(text); laenge += len(text)
    abschliessen()
    return [(t, x) for t, x in aus]


def frage_zu_fts(frage: str) -> str:
    """FTS5-Abfrage aus einer Frage in ganzen Sätzen: Füllwörter fallen weg, die übrigen Wörter gelten als Anfang (Wortstamm) und werden mit ODER
    verbunden — Reihenfolge und Beugung der Frage müssen nicht zum Text passen. Leer, wenn nichts Suchbares darin steht."""
    terme = []
    for w in _WORT.findall((frage or "").lower()):
        if w not in STOPP and w not in terme:
            terme.append(w)
    return " OR ".join('"%s"*' % t.replace('"', "") for t in terme[:MAX_TERME])


def _ohne_versteckte(namen: list[str]) -> list[str]:
    return [n for n in namen if not n.startswith(".")]


def dateien_in(ordner: str):
    """(Pfad, Änderungszeit, Größe) aller lesbaren Dokumente unter ``ordner``; Links werden nicht verfolgt."""
    wurzel = os.path.realpath(ordner)
    n = 0
    for pfad, dirs, namen in os.walk(wurzel, followlinks=False):
        dirs[:] = _ohne_versteckte(dirs)
        for name in _ohne_versteckte(namen):
            if os.path.splitext(name)[1].lower() not in ENDUNGEN:
                continue
            voll = os.path.join(pfad, name)
            try:
                if os.path.islink(voll):
                    continue
                st = os.stat(voll)
            except OSError:
                continue
            if st.st_size > MAX_DATEI_BYTES or not os.path.isfile(voll):
                continue
            n += 1
            if n > MAX_DATEIEN:
                return
            yield voll, st.st_mtime, st.st_size


def _bestand(ordner: list[str]) -> dict[str, tuple[float, int]]:
    """{Pfad: (Änderungszeit, Größe)} aller lesbaren Dateien in den freigegebenen Ordnern."""
    aktuell: dict[str, tuple[float, int]] = {}
    for o in ordner:
        if os.path.isdir(o):
            for p, m, g in dateien_in(o):
                aktuell[p] = (m, g)
    return aktuell


def _datei_aufnehmen(db, pfad: str, stand: tuple[float, int], lesen) -> bool:
    """Die Abschnitte einer Datei neu in den Index schreiben. → False, wenn sie nicht zu lesen war (sie steht dann ohne Abschnitte im Index:
    eine kaputte Datei darf den Rest nicht aufhalten und wird erst nach einer Änderung wieder versucht)."""
    db.execute("delete from abschnitte where pfad = ?", (pfad,))
    try:
        stuecke, gelesen = lesen(pfad), True
    except Exception:
        stuecke, gelesen = [], False
    db.executemany("insert into abschnitte(pfad, ort, titel, text) values (?,?,?,?)", [(pfad, o, t, x) for o, t, x in stuecke])
    db.execute("insert or replace into dateien values (?,?,?)", (pfad, *stand))
    return gelesen


class Index:
    """SQLite-Datei mit der Tabelle ``dateien`` (Stand je Datei) und der FTS5-Tabelle ``abschnitte``. Jede Methode öffnet die Verbindung selbst:
    sie darf aus jedem Arbeitsfaden gerufen werden."""

    def __init__(self, pfad: str):
        self.pfad = pfad

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.pfad, timeout=10)
        db.execute("create table if not exists dateien(pfad text primary key, mtime real, groesse integer)")
        db.execute("create virtual table if not exists abschnitte using fts5(pfad unindexed, ort unindexed, titel, text, "
                   "tokenize='unicode61 remove_diacritics 2')")
        return db

    def aktualisieren(self, ordner: list[str], lesen=None, zeitgrenze: float | None = None, abbruch=None) -> dict:
        """Neue und geänderte Dateien lesen, entfernte (und nicht mehr freigegebene) vergessen. ``lesen(pfad)`` liefert ``[(ort, titel, text)]``
        (Vorgabe: ``dokument_abschnitte.lesen``). Mit ``zeitgrenze`` (Sekunden) endet der Lauf rechtzeitig; Rest folgt beim nächsten Mal."""
        if lesen is None:
            from lunivo_writer.ki.dokument_abschnitte import lesen as lesen
        ende = time.monotonic() + zeitgrenze if zeitgrenze else None
        db = self._db()
        bericht = {"neu": 0, "geaendert": 0, "entfernt": 0, "fehler": 0, "offen": 0}
        try:
            vorhanden = {p: (m, g) for p, m, g in db.execute("select pfad, mtime, groesse from dateien")}
            aktuell = _bestand(ordner)
            for p in set(vorhanden) - set(aktuell):                      # gelöscht oder nicht mehr freigegeben
                db.execute("delete from abschnitte where pfad = ?", (p,)); db.execute("delete from dateien where pfad = ?", (p,))
                bericht["entfernt"] += 1
            faellig = [p for p, st in aktuell.items() if vorhanden.get(p) != st]
            for i, p in enumerate(faellig):
                if (abbruch is not None and abbruch.is_set()) or (ende is not None and time.monotonic() > ende):
                    bericht["offen"] = len(faellig) - i
                    break
                if not _datei_aufnehmen(db, p, aktuell[p], lesen):
                    bericht["fehler"] += 1
                bericht["geaendert" if p in vorhanden else "neu"] += 1
                db.commit()
            db.commit()
        finally:
            db.close()
        return bericht

    def suchen(self, frage: str, ordner: list[str], anzahl: int = 4) -> list[dict]:
        """[{datei, pfad, ort, titel, text}] der besten Abschnitte, nur aus Dateien unterhalb der freigegebenen ``ordner``."""
        q = frage_zu_fts(frage)
        wurzeln = [os.path.realpath(o) + os.sep for o in ordner if os.path.isdir(o)]
        if not q or not wurzeln or not os.path.exists(self.pfad):
            return []
        db = self._db()
        try:
            zeilen = db.execute("select pfad, ort, titel, text from abschnitte where abschnitte match ? order by bm25(abschnitte, 0, 0, 3.0, 1.0) limit ?",
                                (q, max(1, anzahl) * 4)).fetchall()
        except sqlite3.OperationalError:
            return []
        finally:
            db.close()
        aus = []
        for pfad, ort, titel, text in zeilen:
            if any(pfad.startswith(w) for w in wurzeln):                 # frühere Freigaben dürfen nicht mehr durchscheinen
                aus.append({"datei": os.path.basename(pfad), "pfad": pfad, "ort": ort, "titel": titel, "text": text})
            if len(aus) >= anzahl:
                break
        return aus

    def anzahl(self) -> tuple[int, int]:
        """(Dateien, Abschnitte) im Index."""
        if not os.path.exists(self.pfad):
            return 0, 0
        db = self._db()
        try:
            return db.execute("select count(*) from dateien").fetchone()[0], db.execute("select count(*) from abschnitte").fetchone()[0]
        finally:
            db.close()


def fundstelle(t: dict) -> str:
    return f"{t['datei']} — {t['ort']}"


def als_text(treffer: list[dict]) -> str:
    """Die Auszüge als nummerierte Quellenliste für die Anweisung an die KI."""
    return "\n\n".join(f"[{i}] {fundstelle(t)}\n{t['text']}" for i, t in enumerate(treffer, 1))


def fundstellen_zeilen(treffer: list[dict]) -> str:
    """Kurzliste für die Anzeige unter der Antwort."""
    return "\n".join(f"[{i}] {fundstelle(t)}" for i, t in enumerate(treffer, 1))
