"""Schichtregel: editor/, dienste/, modelle/ und korrektur/ importieren nichts aus oberflaeche/ (die Oberfläche baut auf ihnen auf, nicht umgekehrt).

Die Liste der Ausnahmen darf nur kleiner werden, nie größer."""
import os
import re

import lunivo_writer

PAKET = os.path.dirname(lunivo_writer.__file__)
BEREICHE = ("editor", "dienste", "modelle", "korrektur")
UI_IMPORT = re.compile(r"^\s*(?:from\s+lunivo_writer\.oberflaeche\b|from\s+lunivo_writer\s+import\s+oberflaeche\b|import\s+lunivo_writer\.oberflaeche\b)", re.M)
NOCH_ERLAUBT: set[str] = set()      # leer und bleibt leer: eine neue Ausnahme braucht eine dokumentierte Begründung hier und die Freigabe des Eigentümers


def test_keine_ui_importe_in_den_unteren_schichten():
    gefunden = set()
    for bereich in BEREICHE:
        for wurzel, _ordner, dateien in os.walk(os.path.join(PAKET, bereich)):
            for name in dateien:
                if name.endswith(".py"):
                    pfad = os.path.join(wurzel, name)
                    with open(pfad, encoding="utf-8") as fh:
                        if UI_IMPORT.search(fh.read()):
                            gefunden.add(os.path.relpath(pfad, PAKET).replace(os.sep, "/"))
    assert gefunden <= NOCH_ERLAUBT, f"neue Importe aus oberflaeche/: {sorted(gefunden - NOCH_ERLAUBT)}"
    assert NOCH_ERLAUBT <= gefunden, f"aus der Ausnahmeliste streichen: {sorted(NOCH_ERLAUBT - gefunden)}"


PLATTFORM_API = re.compile(r"\bfcntl\b|\bmsvcrt\b|os\.killpg|start_new_session|creationflags|subprocess\.Popen|os\.name\s*==|sys\.platform|platform\.system")


def test_betriebssystemabhaengiges_nur_in_plattform():
    """Prozessstart, Prozessende, Dateisperren und Dateisystem-Besonderheiten liegen in plattform/; alle anderen Teile gehen darüber."""
    treffer = []
    for wurzel, _o, dateien in os.walk(PAKET):
        for name in dateien:
            pfad = os.path.join(wurzel, name)
            rel = os.path.relpath(pfad, PAKET).replace(os.sep, "/")
            if name.endswith(".py") and not rel.startswith("plattform/"):
                with open(pfad, encoding="utf-8") as fh:
                    for n, z in enumerate(fh, 1):
                        if PLATTFORM_API.search(z) and not z.lstrip().startswith("#"):
                            treffer.append(f"{rel}:{n}")
    assert treffer == [], "Betriebssystemaufrufe außerhalb von plattform/: " + ", ".join(treffer)
