#!/usr/bin/env python3
"""Probestart für den Git-Haken: startet Lunivo ohne Bildschirm (``QT_QPA_PLATFORM=offscreen``) mit leeren, vorübergehenden Einstellungs- und
Datenordnern. Läuft das Programm nach ``SEKUNDEN`` noch, gilt der Start als gelungen; endet es vorher mit einem Fehler, wird der Commit abgebrochen
und das Ende der Ausgabe gezeigt. Kein Testlauf: Es wird nur geprüft, ob das Programm hochkommt."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

SEKUNDEN = 20
PROJEKT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lunivo-start-") as tmp:
        umgebung = dict(os.environ, QT_QPA_PLATFORM="offscreen", XDG_CONFIG_HOME=os.path.join(tmp, "config"),
                        XDG_DATA_HOME=os.path.join(tmp, "data"), XDG_CACHE_HOME=os.path.join(tmp, "cache"),
                        XDG_STATE_HOME=os.path.join(tmp, "state"), PYTHONFAULTHANDLER="1")
        try:
            r = subprocess.run([sys.executable, os.path.join(PROJEKT, "main.py")], cwd=PROJEKT, env=umgebung,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=SEKUNDEN)
        except subprocess.TimeoutExpired:
            print(f"Probestart: Lunivo läuft nach {SEKUNDEN} s – Start in Ordnung.")
            return 0
        zeilen = [z for z in (r.stdout or "").splitlines() if not z.startswith("qt.")]
        print(f"PROBESTART FEHLGESCHLAGEN (Rückgabe {r.returncode}): Lunivo ist beim Start beendet worden.\n" + "\n".join(zeilen[-30:]), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
