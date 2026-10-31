"""Orte der Programmdaten: Ressourcen im Paket, Symbole/Bilder/Schriften unter assets/."""
from __future__ import annotations

import os
import sys

if getattr(sys, "frozen", False):                                              # als gepacktes Programm (z. B. PyInstaller)
    WURZEL = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    PAKET = os.path.join(WURZEL, "lunivo_writer")
else:
    PAKET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # …/src/lunivo_writer
    WURZEL = os.path.dirname(os.path.dirname(PAKET))                          # Projektordner
RESSOURCEN = os.path.join(PAKET, "resources")
ASSETS = os.path.join(WURZEL, "assets") if os.path.isdir(os.path.join(WURZEL, "assets")) else os.path.join(PAKET, "assets")
SYMBOLE = os.path.join(ASSETS, "icons")
