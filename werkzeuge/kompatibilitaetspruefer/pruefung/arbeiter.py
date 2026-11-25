"""Prüfprozess: prüft **eine Datei** in einem eigenen Prozess und schreibt das Ergebnis als JSON.

    python -m kompatibilitaetspruefer.pruefung.arbeiter AUFTRAG.json ERGEBNIS.json

Ein eigener Prozess je Datei schützt die Prüfsammlung: Ein beschädigtes oder riesiges Dokument kann nur seinen eigenen Prozess abstürzen lassen oder an dessen Zeit- und Speichergrenze
scheitern, nie das Werkzeug oder andere Testdateien. Das Original wird nie geöffnet: Der Prozess arbeitet an einer Kopie in einem privaten temporären Ordner (Rechte 0700), den er am Ende
löscht. Die Speichergrenze überwacht der Elternprozess (tatsächlicher Arbeitsspeicher, ``VmRSS``); eine Adressraumgrenze würde Qt zum Absturz bringen. Größe und Änderungszeit des Originals werden vor und nach der Prüfung verglichen. Makros werden nie ausgeführt (Lunivo liest sie nicht aus)."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
import traceback


def _stamp(pfad: str) -> str:
    try:
        st = os.stat(pfad)
        return f"{st.st_size}:{st.st_mtime_ns}"
    except OSError:
        return "fehlt"


def _technisch(art: str, text: str) -> dict:
    from kompatibilitaetspruefer.pruefung import klassifikation as K
    from kompatibilitaetspruefer.pruefung.pruefarten import abschluss
    return abschluss(art, [K.scheitert("Prüfung", "Technischer Prüffehler", text)])


def ausfuehren(job: dict) -> dict:
    from kompatibilitaetspruefer.pruefung import klassifikation as K
    from kompatibilitaetspruefer.pruefung.pruefarten import ARTEN, Kontext, abschluss
    k = job["konfig"]
    original = job["datei"]["pfad"]
    vorher = _stamp(original)
    ergebnisse = []
    tmp = tempfile.mkdtemp(prefix="lunivo-pruefer-")
    os.chmod(tmp, 0o700)
    try:
        groesse = os.path.getsize(original) if os.path.isfile(original) else -1
        if groesse < 0:
            return {"ergebnisse": [_technisch(a, "Die Datei existiert nicht (mehr)") for a in job["arten"]]}
        if groesse > k["max_dateigroesse_mb"] * 1024 * 1024:
            return {"ergebnisse": [_technisch(a, f"Datei ({groesse // (1024 * 1024)} MB) überschreitet die eingestellte Grenze von {k['max_dateigroesse_mb']} MB; nicht geprüft")
                                   for a in job["arten"]]}
        kopie = os.path.join(tmp, "quelle" + job["datei"]["endung"])
        shutil.copyfile(original, kopie)
        job = {**job, "arbeitskopie": kopie, "tmp": tmp}
        ctx = Kontext(job)
        for art in job["arten"]:
            t0 = time.monotonic()
            try:
                e = ARTEN[art](ctx)
            except MemoryError:
                e = _technisch(art, "Speichergrenze des Prüfprozesses erreicht")
            except Exception as ex:                                                          # noqa: BLE001 — ein Fehler in einer Prüfart darf die anderen nicht verhindern
                e = _technisch(art, f"Prüfart ist mit {type(ex).__name__} abgebrochen: {' '.join(str(ex).split())[:300]} | {traceback.format_exc(limit=3)[-400:]}")
            e["dauer"] = time.monotonic() - t0
            ergebnisse.append(e)
        if _stamp(original) != vorher:
            for e in ergebnisse:
                e["befunde"].append(K.scheitert("Originaldatei", "Technischer Prüffehler", "Die Originaldatei hat sich während der Prüfung verändert; Ergebnis nicht verlässlich"))
                e["status"] = K.FEHLGESCHLAGEN
        return {"ergebnisse": ergebnisse}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str]) -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    with open(argv[1], encoding="utf-8") as f:
        job = json.load(f)
    from PySide6.QtWidgets import QApplication
    app = QApplication(["lunivo-pruefer"])
    app.setApplicationName("Lunivo Writer")
    app.setOrganizationName("Lunivo")
    try:
        ergebnis = ausfuehren(job)
    except MemoryError:
        ergebnis = {"ergebnisse": [_technisch(a, "Speichergrenze des Prüfprozesses erreicht") for a in job["arten"]]}
    tmp = argv[2] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ergebnis, f, ensure_ascii=False, default=str)
    os.replace(tmp, argv[2])
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
    import kompatibilitaetspruefer                                                           # noqa: F401  (richtet den Suchpfad für lunivo_writer ein)
    sys.exit(main(sys.argv))
