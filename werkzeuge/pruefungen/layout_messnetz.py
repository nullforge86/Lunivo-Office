"""Messnetz für die Layout-Schicht (Phase 0): hält je Testdatei fest, wie Lunivo sie heute setzt, und vergleicht später alt gegen neu.

Je Datei: Seiten der Ausgabe (über alle Abschnitte), Zahl der Abschnitte und für jeden Absatz die Seite, auf der er beginnt. Gemessen wird mit
``paginated_copy`` (derselbe Weg wie Anzeige, Druck und PDF), ein Absturz oder eine Zeitüberschreitung ist ein eigener Befund und bricht den Lauf nicht ab.

    .venv/bin/python werkzeuge/pruefungen/layout_messnetz.py festhalten ergebnis.json [Ordner oder Dateien …]
    .venv/bin/python werkzeuge/pruefungen/layout_messnetz.py vergleichen ergebnis.json [Ordner oder Dateien …]

Ohne Angabe gelten die Testdateien des Projekts und der Prüfdatenbank ``~/Lunivo-Testdateien`` (je Ordner höchstens ``MAX_JE_ORDNER``).
Ergebnisse sind JSON (keine Webseite); ``vergleichen`` meldet jede Datei, deren Seitenzahl oder Absatzseiten abweichen, und endet mit Exit-Code 1."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENDUNGEN = (".docx", ".odt", ".rtf", ".fodt")
MAX_JE_ORDNER = 120                       # große Sammlungen (Webkorpus) nur zum Teil, immer dieselben (sortiert)
ZEIT_JE_DATEI = 90                        # Sekunden
STANDARD_QUELLEN = ["tests/dokument/formate/daten", "~/Lunivo-Testdateien/01_DOCX", "~/Lunivo-Testdateien/02_ODT", "~/Lunivo-Testdateien/03_RTF",
                    "~/Lunivo-Testdateien/08_Eigene_DOCX_Tests", "~/Lunivo-Testdateien/11_Microsoft_Originale", "~/Lunivo-Testdateien/12_DOCX_Webkorpus"]


def dateien_sammeln(quellen: list[str]) -> list[str]:
    liste: list[str] = []
    for q in quellen:
        q = os.path.expanduser(q)
        if not os.path.isabs(q):
            q = os.path.join(WURZEL, q)
        if os.path.isfile(q):
            liste.append(q)
            continue
        je = []
        for d, _u, fs in os.walk(q):
            je += [os.path.join(d, f) for f in fs if f.lower().endswith(ENDUNGEN)]
        liste += sorted(je)[:MAX_JE_ORDNER]
    return sorted(set(liste))


def messen(pfad: str) -> dict:
    """Eine Datei setzen und messen (läuft in einem eigenen Prozess)."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, os.path.join(WURZEL, "src"))
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])  # noqa: F841
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.editor.seite import abschnitte as AB
    from lunivo_writer.editor.seite import seiten_aufteilung as SA
    from lunivo_writer.editor.seite.seitenzahl import absatz_oben
    geladen = load(pfad)
    doc, page = geladen.doc, geladen.page
    teile, _h = AB.teile(doc, page)
    absatz_seiten: list[list[int]] = []
    for d, ps, _typ in teile:
        k = SA.paginated_copy(d, ps, None, silben=False)
        lay = k.documentLayout()
        ch, sp = ps.content_height_px, max(1, int(ps.spalten))
        je = []
        b = k.firstBlock()
        while b.isValid():
            je.append(int((absatz_oben(lay, b) + 0.5) // ch) // sp + 1)
            b = b.next()
        absatz_seiten.append(je)
    return {"seiten": SA.seitenzahl(doc, page), "abschnitte": len(teile), "absatzseiten": absatz_seiten}


def _einzeln(pfad: str) -> dict:
    try:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--einzeln", pfad], capture_output=True, text=True, timeout=ZEIT_JE_DATEI)
    except subprocess.TimeoutExpired:
        return {"befund": "Zeitüberschreitung"}
    for zeile in reversed(r.stdout.splitlines()):
        if zeile.startswith("ERGEBNIS "):
            return json.loads(zeile[9:])
    return {"befund": f"Absturz oder Fehler (Exit {r.returncode})"}


def lauf(quellen: list[str]) -> dict:
    dateien = dateien_sammeln(quellen or STANDARD_QUELLEN)
    with ThreadPoolExecutor(max_workers=4) as ex:
        erg = list(ex.map(_einzeln, dateien))
    return {os.path.relpath(p, os.path.expanduser("~")) if p.startswith(os.path.expanduser("~")) else os.path.relpath(p, WURZEL): e for p, e in zip(dateien, erg)}


def vergleichen(alt: dict, neu: dict) -> list[str]:
    funde = []
    for name, a in sorted(alt.items()):
        n = neu.get(name)
        if n is None:
            funde.append(f"{name}: fehlt im neuen Lauf")
        elif a != n:
            if "befund" in a or "befund" in n:
                funde.append(f"{name}: {a.get('befund', 'ok')} → {n.get('befund', 'ok')}")
            elif a["seiten"] != n["seiten"]:
                funde.append(f"{name}: Seiten {a['seiten']} → {n['seiten']}")
            else:
                zahl = sum(1 for x, y in zip(sum(a["absatzseiten"], []), sum(n["absatzseiten"], [])) if x != y)
                funde.append(f"{name}: {zahl} Absätze auf anderer Seite")
    return funde


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[1] == "--einzeln":
        print("ERGEBNIS " + json.dumps(messen(argv[2])))
        return 0
    if len(argv) < 3 or argv[1] not in ("festhalten", "vergleichen"):
        print(__doc__)
        return 2
    ziel, quellen = argv[2], argv[3:]
    ergebnis = lauf(quellen)
    if argv[1] == "festhalten":
        with open(ziel, "w", encoding="utf-8") as f:
            json.dump(ergebnis, f, ensure_ascii=False, indent=1, sort_keys=True)
        ok = sum(1 for e in ergebnis.values() if "befund" not in e)
        print(f"{len(ergebnis)} Dateien gemessen, {ok} ohne Befund → {ziel}")
        return 0
    with open(ziel, encoding="utf-8") as f:
        alt = json.load(f)
    funde = vergleichen(alt, ergebnis)
    print("\n".join(funde) if funde else "Keine Abweichung.")
    print(f"{len(ergebnis)} Dateien verglichen, {len(funde)} Abweichungen")
    return 1 if funde else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
