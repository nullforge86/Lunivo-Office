"""Prüfdatenbank für die Darstellung: jede DOCX der Sammlung mit Lunivo einlesen, als PDF ausgeben und mit dem Referenz-PDF vergleichen.

Die Sammlung liegt außerhalb des Projekts (Vorgabe: ``~/Lunivo-Testdateien``). Zu ``<Sammlung>/PDF-Referenzen/<Pfad>.pdf`` gehört
``<Sammlung>/<Pfad>.docx``. Die Originale werden nur gelesen.

Verwendung:
    python werkzeuge/pruefungen/darstellung_korpus.py                 → alle Dateien, Bericht nach dokumentation/berichte/
    python werkzeuge/pruefungen/darstellung_korpus.py --nur legal     → nur Dateien, deren Pfad „legal“ enthält (kein Bericht, nur Ausgabe)

Gemessen wird je Datei: lässt sie sich öffnen, Seitenzahl, Papiergröße, Wörter im PDF, Gleichheit der Wortfolge, Zeit — und das Aussehen
der ersten Seiten als Bild: Deckung der Schwärzung, Anteil farbiger Fläche, Zahl der Bilder. Das Seitenbild erfasst alle Bereiche des
Dokuments (Bilder, Formen, Linien, Tabellen, Kopf- und Fußzeilen), nicht nur den Text. Der Bericht nennt
zusätzlich, was sich seit dem letzten Lauf verbessert oder verschlechtert hat (Stand: ``darstellung-korpus.json`` neben dem Bericht).

Ehrliche Grenze: Die Referenz-PDFs stammen aus einem anderen Textprogramm, nicht aus Word; sie sind ein Vorbild, kein Beweis. Das
Seitenbild wird grob verglichen (Raster): es zeigt, ob etwas fehlt oder woanders steht, nicht jede Schrift- oder Abstandsabweichung.
"""
from __future__ import annotations

import argparse
import collections
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.normpath(os.path.join(HIER, "..", ".."))
BERICHT = os.path.join(WURZEL, "dokumentation", "berichte", "darstellung-korpus.md")
STAND = os.path.join(WURZEL, "dokumentation", "berichte", "darstellung-korpus.json")
SAMMLUNG = os.path.join(os.path.expanduser("~"), "Lunivo-Testdateien")
REFERENZEN = "PDF-Referenzen"
ZEITLIMIT_S = 180                # je Datei; eine Datei, die länger braucht, gilt als nicht darstellbar
PROZESSE = max(1, (os.cpu_count() or 2) - 2)
TEXT_GUT = 0.98                  # ab dieser Gleichheit der Wortfolge gilt der Text als gleich
WORT_SPIEL = 0.05                # so viel Abweichung in der Wortzahl gilt noch nicht als Verlust oder Überschuss
LANGSAM_S = 10.0
GENAUER_VERGLEICH_BIS = 40000    # Wörter; darüber vergleicht difflib mit seiner Abkürzung
BILD_SEITEN = 6                  # so viele Seiten vom Anfang werden als Bild verglichen
BILD_DPI = 12                    # Auflösung des Seitenbildes für den Vergleich
RASTER = (12, 16)                # Felder je Seite (Breite, Höhe), auf die beide Seitenbilder gebracht werden
FARBE_AB = 40                    # Abstand zwischen stärkstem und schwächstem Farbkanal, ab dem ein Feld als farbig gilt
BILD_GUT = 0.60                  # ab dieser Deckung der Seitenbilder gilt das Aussehen als gleich
FARBE_SPIEL = 0.02               # so viel Unterschied im farbigen Flächenanteil gilt noch als gleich


# ---------------------------------------------------------------- eine Datei (eigener Prozess)

def _pdf_daten(pfad: str) -> tuple[int, list[int], list[str]]:
    info = subprocess.run(["pdfinfo", pfad], capture_output=True, text=True).stdout
    seiten = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    g = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
    text = subprocess.run(["pdftotext", "-layout", pfad, "-"], capture_output=True, text=True).stdout
    return seiten, [round(float(g.group(1))), round(float(g.group(2)))], re.findall(r"\w+", text.lower())


def _seitenbilder(pfad: str, ordner: str, name: str) -> list:
    """Die ersten ``BILD_SEITEN`` Seiten als kleine Bilder (je ``RASTER`` Felder, RGB)."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage
    vor = os.path.join(ordner, name)
    subprocess.run(["pdftoppm", "-r", str(BILD_DPI), "-f", "1", "-l", str(BILD_SEITEN), pfad, vor], capture_output=True)
    aus = []
    for d in sorted(x for x in os.listdir(ordner) if x.startswith(name + "-") and x.endswith(".ppm")):
        img = QImage(os.path.join(ordner, d)).scaled(RASTER[0], RASTER[1], Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        img = img.convertToFormat(QImage.Format_RGB888)
        roh, zeile = bytes(img.constBits()), img.bytesPerLine()
        aus.append([roh[y * zeile:y * zeile + 3 * RASTER[0]] for y in range(RASTER[1])])
        os.remove(os.path.join(ordner, d))
    return aus


def _seite_werte(bild: list) -> tuple[list[int], float]:
    """(Schwärzung je Feld 0–255, Anteil farbiger Felder) eines Seitenbildes."""
    tinte, farbig = [], 0
    for zeile in bild:
        for i in range(0, len(zeile), 3):
            r, g, b = zeile[i], zeile[i + 1], zeile[i + 2]
            tinte.append(255 - (r + g + b) // 3)
            farbig += max(r, g, b) - min(r, g, b) >= FARBE_AB
    return tinte, farbig / max(1, len(tinte))


def bildvergleich(aus: str, ref: str) -> dict:
    """Aussehen der ersten Seiten: Deckung der Schwärzung (1 = gleiche Stellen gleich dunkel), farbige Fläche und Zahl der Bilder.
    Erfasst alles, was auf der Seite steht — Bilder, Formen, Linien, Tabellen, Kopf- und Fußzeilen —, nicht nur den Text."""
    ordner = os.path.dirname(aus)
    a = [_seite_werte(x) for x in _seitenbilder(aus, ordner, os.path.basename(aus) + "-l")]
    b = [_seite_werte(x) for x in _seitenbilder(ref, ordner, os.path.basename(aus) + "-r")]
    deckung = []
    for (ta, _fa), (tb, _fb) in zip(a, b):
        oben = sum(min(x, y) for x, y in zip(ta, tb))
        unten = sum(max(x, y) for x, y in zip(ta, tb))
        deckung.append(oben / unten if unten else 1.0)
    def bilder(pfad):
        z = subprocess.run(["pdfimages", "-list", pfad], capture_output=True, text=True).stdout.splitlines()[2:]
        return sum(1 for x in z if " image " in x)
    return {"bild_gleich": round(sum(deckung) / len(deckung), 3) if deckung else 0.0,
            "farbe": round(sum(f for _t, f in a) / max(1, len(a)), 3), "farbe_ref": round(sum(f for _t, f in b) / max(1, len(b)), 3),
            "bilder": bilder(aus), "bilder_ref": bilder(ref)}


def eine(docx: str, ref: str, aus: str) -> dict:
    """Lädt ``docx``, schreibt ``aus`` (PDF) und vergleicht mit ``ref``."""
    sys.path.insert(0, os.path.join(WURZEL, "src"))
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    erg: dict = {"ok": False}
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication([])  # noqa: F841
        from lunivo_writer.dienste import datei_dienst
        from lunivo_writer.editor.seite.seiten_aufteilung import export_pdf
        t = time.time()
        g = datei_dienst.load(docx)
        erg["laden_s"] = round(time.time() - t, 2)
        erg["hinweise"] = list(g.report.warnings)
        t = time.time()
        export_pdf(aus, g.doc, g.page)
        erg["pdf_s"] = round(time.time() - t, 2)
        ls, lg, lw = _pdf_daten(aus)
        rs, rg, rw = _pdf_daten(ref)
        genau = len(lw) + len(rw) < GENAUER_VERGLEICH_BIS
        erg.update(ok=True, seiten=ls, seiten_ref=rs, papier=lg, papier_ref=rg, worte=len(lw), worte_ref=len(rw),
                   text_gleich=round(difflib.SequenceMatcher(None, lw, rw, autojunk=not genau).ratio(), 3))
        erg.update(bildvergleich(aus, ref))
    except Exception as ex:  # noqa: BLE001 — jeder Fehler ist ein Befund
        erg["fehler"] = f"{type(ex).__name__}: {ex}"[:300]
    return erg


# ---------------------------------------------------------------- alle Dateien

def paare(sammlung: str, nur: str = "") -> list[tuple[str, str, str]]:
    """(Name, DOCX, Referenz-PDF) für jedes Referenz-PDF, zu dem es eine DOCX gibt."""
    wurzel = os.path.join(sammlung, REFERENZEN)
    aus = []
    for ordner, unter, dateien in os.walk(wurzel):
        unter[:] = [u for u in unter if not u.startswith(".")]
        for d in dateien:
            if not d.lower().endswith(".pdf"):
                continue
            name = os.path.relpath(os.path.join(ordner, d), wurzel)[:-4]
            docx = os.path.join(sammlung, name + ".docx")
            if os.path.isfile(docx) and nur.lower() in name.lower():
                aus.append((name, docx, os.path.join(ordner, d)))
    return sorted(aus)


def _starten(eintrag: tuple[str, str, str], tmp: str, nr: int) -> dict:
    name, docx, ref = eintrag
    aus = os.path.join(tmp, f"{nr}.pdf")
    try:
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--eine", docx, ref, aus], capture_output=True, text=True,
                           timeout=ZEITLIMIT_S)
        zeile = (p.stdout.strip().splitlines() or [""])[-1]
        erg = json.loads(zeile) if zeile.startswith("{") else {"ok": False, "fehler": f"Absturz (Rückgabe {p.returncode})"}
    except subprocess.TimeoutExpired:
        erg = {"ok": False, "fehler": f"Zeitlimit ({ZEITLIMIT_S} s) überschritten"}
    finally:
        if os.path.exists(aus):
            os.remove(aus)
    erg["datei"] = name
    return erg


def messen(sammlung: str, nur: str = "") -> list[dict]:
    liste = paare(sammlung, nur)
    with tempfile.TemporaryDirectory(prefix="lunivo-korpus-") as tmp, ThreadPoolExecutor(PROZESSE) as pool:
        return list(pool.map(lambda x: _starten(x[1], tmp, x[0]), enumerate(liste)))


# ---------------------------------------------------------------- Auswertung

def note(r: dict) -> int:
    """0 = lässt sich nicht darstellen, 1 = Text oder Seiten weichen ab, 2 = Seitenzahl, Text und Aussehen stimmen."""
    if not r["ok"]:
        return 0
    return 2 if r["seiten"] == r["seiten_ref"] and r["text_gleich"] >= TEXT_GUT and _bild_stimmt(r) else 1


def _bild_stimmt(r: dict) -> bool:
    """Aussehen: Seitenbild deckt sich, gleich viel farbige Fläche, keine Bilder weniger als im Vorbild."""
    return r["bild_gleich"] >= BILD_GUT and abs(r["farbe"] - r["farbe_ref"]) <= FARBE_SPIEL and r["bilder"] >= r["bilder_ref"]


def _wortlage(r: dict) -> str:
    if r["worte"] < (1 - WORT_SPIEL) * r["worte_ref"]:
        return "fehlt"
    return "zuviel" if r["worte"] > (1 + WORT_SPIEL) * r["worte_ref"] else "gleich"


def zusammenfassung(erg: list[dict]) -> dict:
    ok = [r for r in erg if r["ok"]]
    return {
        "dateien": len(erg), "geoeffnet": len(ok), "stimmt": sum(note(r) == 2 for r in erg),
        "seiten_gleich": sum(r["seiten"] == r["seiten_ref"] for r in ok),
        "text_gleich": sum(r["text_gleich"] >= TEXT_GUT for r in ok),
        "text_fehlt": sum(_wortlage(r) == "fehlt" for r in ok), "text_zuviel": sum(_wortlage(r) == "zuviel" for r in ok),
        "bild_gleich": sum(r["bild_gleich"] >= BILD_GUT for r in ok),
        "farbe_fehlt": sum(r["farbe_ref"] - r["farbe"] > FARBE_SPIEL for r in ok),
        "bilder_fehlen": sum(r["bilder"] < r["bilder_ref"] for r in ok),
        "papier_falsch": sum(r["papier"] != r["papier_ref"] for r in ok),
        "langsam": sum(r["laden_s"] + r["pdf_s"] > LANGSAM_S for r in ok),
    }


def _aenderungen(erg: list[dict], alt: dict) -> tuple[list[str], list[str]]:
    besser, schlechter = [], []
    for r in erg:
        vor = alt.get(r["datei"])
        if vor is not None and note(r) != vor:
            (besser if note(r) > vor else schlechter).append(r["datei"])
    return besser, schlechter


def _zeile(r: dict) -> str:
    if not r["ok"]:
        return f"| `{r['datei']}` | – | – | – | – | – | – | {r['fehler']} |"
    hinweis = "; ".join(r["hinweise"])
    return (f"| `{r['datei']}` | {r['seiten']} / {r['seiten_ref']} | {r['worte']} / {r['worte_ref']} | {r['text_gleich']:.2f} | "
            f"{r['bild_gleich']:.2f} | {r['farbe']:.0%} / {r['farbe_ref']:.0%} | {r['bilder']} / {r['bilder_ref']} | {hinweis} |")


def bericht_text(erg: list[dict], alt: dict) -> str:
    z = zusammenfassung(erg)
    besser, schlechter = _aenderungen(erg, alt)
    fehler = collections.Counter(re.sub(r"\(.*", "", r["fehler"]).strip()[:90] for r in erg if not r["ok"])
    hinweise = collections.Counter(h for r in erg if r["ok"] for h in r["hinweise"])
    aus = ["# Darstellung: Vergleich mit den Referenz-PDFs", "",
           "Erzeugt mit `werkzeuge/pruefungen/darstellung_korpus.py`. Jede DOCX der Sammlung wird eingelesen, als PDF ausgegeben und mit ihrem "
           "Referenz-PDF verglichen: Seitenzahl, Wortfolge und das Seitenbild der ersten Seiten (Deckung der Schwärzung, farbige Fläche, Zahl der Bilder). Grenzen des Vergleichs: siehe Kopf des Werkzeugs.", "",
           "## Stand", "", "| Messwert | Anzahl |", "|---|---|",
           f"| Dateien | {z['dateien']} |", f"| lassen sich öffnen und ausgeben | {z['geoeffnet']} |",
           f"| Seitenzahl, Text und Aussehen stimmen | {z['stimmt']} |", f"| Seitenzahl stimmt | {z['seiten_gleich']} |",
           f"| Text stimmt (Wortfolge ab {TEXT_GUT:.2f}) | {z['text_gleich']} |", f"| Text fehlt (über {WORT_SPIEL:.0%}) | {z['text_fehlt']} |",
           f"| Text zu viel (über {WORT_SPIEL:.0%}) | {z['text_zuviel']} |", f"| Papiergröße weicht ab | {z['papier_falsch']} |",
           f"| Seitenbild deckt sich (ab {BILD_GUT:.2f}) | {z['bild_gleich']} |",
           f"| farbige Fläche fehlt (Formen, Bilder, Farbbalken) | {z['farbe_fehlt']} |", f"| Bilder fehlen | {z['bilder_fehlen']} |",
           f"| langsamer als {LANGSAM_S:.0f} s | {z['langsam']} |", ""]
    if alt:
        aus += ["## Seit dem letzten Lauf", "", f"Besser: {len(besser)}, schlechter: {len(schlechter)}.", ""]
        aus += [f"- schlechter: `{n}`" for n in schlechter] + [f"- besser: `{n}`" for n in besser] + [""]
    aus += ["## Fehler beim Öffnen oder Ausgeben", "", "| Anzahl | Fehler |", "|---|---|"] + [f"| {n} | {f} |" for f, n in fehler.most_common()]
    aus += ["", "## Hinweise des Importes", "", "| Anzahl | Hinweis |", "|---|---|"] + [f"| {n} | {h} |" for h, n in hinweise.most_common()]
    kopf = ["| Datei | Seiten Lunivo / Vorbild | Wörter Lunivo / Vorbild | Wortfolge | Seitenbild | Farbfläche Lunivo / Vorbild | "
            "Bilder Lunivo / Vorbild | Fehler oder Hinweis |", "|---|---|---|---|---|---|---|---|"]
    for titel, stufe in (("Lässt sich nicht darstellen", 0), ("Weicht ab", 1), ("Stimmt", 2)):
        teil = sorted((r for r in erg if note(r) == stufe), key=lambda r: (r.get("text_gleich", 0), r["datei"]))
        aus += ["", f"## {titel} ({len(teil)})", ""] + (kopf + [_zeile(r) for r in teil] if teil else ["keine"])
    return "\n".join(aus) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Darstellung der DOCX-Sammlung mit den Referenz-PDFs vergleichen")
    ap.add_argument("--sammlung", default=SAMMLUNG)
    ap.add_argument("--nur", default="", help="nur Dateien, deren Pfad diesen Text enthält; schreibt keinen Bericht")
    ap.add_argument("--eine", nargs=3, metavar=("DOCX", "REFERENZ", "AUSGABE"), help="intern: eine Datei messen")
    a = ap.parse_args()
    if a.eine:
        print(json.dumps(eine(*a.eine), ensure_ascii=False))
        return 0
    if not os.path.isdir(os.path.join(a.sammlung, REFERENZEN)):
        print(f"Keine Sammlung gefunden: {os.path.join(a.sammlung, REFERENZEN)}")
        return 2
    erg = messen(a.sammlung, a.nur)
    if a.nur:
        for r in erg:
            print(_zeile(r))
        return 0
    alt = {}
    if os.path.isfile(STAND):
        with open(STAND, encoding="utf-8") as fh:
            alt = json.load(fh)
    with open(BERICHT, "w", encoding="utf-8") as fh:
        fh.write(bericht_text(erg, alt))
    with open(STAND, "w", encoding="utf-8") as fh:
        json.dump({r["datei"]: note(r) for r in erg}, fh, ensure_ascii=False, indent=0, sort_keys=True)
    print(json.dumps(zusammenfassung(erg), ensure_ascii=False))
    print(f"Bericht: {BERICHT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
