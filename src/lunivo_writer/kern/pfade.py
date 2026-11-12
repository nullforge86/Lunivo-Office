"""Orte der Programmdaten: Ressourcen im Paket, Symbole/Bilder/Schriften unter ressourcen/."""
from __future__ import annotations

import os
import sys

if getattr(sys, "frozen", False):                                              # als gepacktes Programm (z. B. PyInstaller)
    WURZEL = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    PAKET = os.path.join(WURZEL, "lunivo_writer")
else:
    PAKET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # …/src/lunivo_writer
    WURZEL = os.path.dirname(os.path.dirname(PAKET))                          # Projektordner
RESSOURCEN = os.path.join(PAKET, "ressourcen")
ASSETS = os.path.join(WURZEL, "ressourcen") if os.path.isdir(os.path.join(WURZEL, "ressourcen")) else os.path.join(PAKET, "ressourcen")
SYMBOLE = os.path.join(ASSETS, "icons")
