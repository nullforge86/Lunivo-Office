#!/usr/bin/env python3
"""Erzeugt aus ressourcen/symbole/varianten/Abstrakt (das Programmsymbol der Anwendung) .ico und .icns.

Aufruf aus dem Projektwurzelordner:  python installationspakete/icons_erzeugen.py
Ergebnis: erstellung/icons/lunivo-office.ico, lunivo-office.icns, lunivo-office.png (erstellung/ ist ignoriert). Braucht Pillow.
"""
import os
import sys

from PIL import Image

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(WURZEL, "ressourcen", "symbole", "varianten", "Abstrakt", "icon-1024.png")
ZIEL = os.path.join(WURZEL, "erstellung", "icons")


def main() -> int:
    if not os.path.exists(QUELLE):
        print(f"Symbol fehlt: {QUELLE}", file=sys.stderr)
        return 1
    os.makedirs(ZIEL, exist_ok=True)
    bild = Image.open(QUELLE).convert("RGBA")
    bild.save(os.path.join(ZIEL, "lunivo-office.ico"), sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    bild.save(os.path.join(ZIEL, "lunivo-office.icns"))
    bild.resize((256, 256), Image.LANCZOS).save(os.path.join(ZIEL, "lunivo-office.png"))
    print("Symbole erzeugt in", ZIEL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
