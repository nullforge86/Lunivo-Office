"""Schichtregel: editor/, services/, models/ und proofing/ importieren nichts aus ui/ (die Oberfläche baut auf ihnen auf, nicht umgekehrt).

Die Liste der Ausnahmen darf nur kleiner werden, nie größer."""
import os
import re

import lunivo_writer

PAKET = os.path.dirname(lunivo_writer.__file__)
BEREICHE = ("editor", "services", "models", "proofing")
UI_IMPORT = re.compile(r"^\s*(?:from\s+lunivo_writer\.ui\b|from\s+lunivo_writer\s+import\s+ui\b|import\s+lunivo_writer\.ui\b)", re.M)
NOCH_ERLAUBT = {
    "editor/formular.py",      # ruft EingabeFenster für Datum/Text eines Formularfeldes auf
    "editor/einfuegen.py",     # Piktogramm-Katalog aus ui/widgets/icons.py
}


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
    assert gefunden <= NOCH_ERLAUBT, f"neue Importe aus ui/: {sorted(gefunden - NOCH_ERLAUBT)}"
    assert NOCH_ERLAUBT <= gefunden, f"aus der Ausnahmeliste streichen: {sorted(NOCH_ERLAUBT - gefunden)}"
