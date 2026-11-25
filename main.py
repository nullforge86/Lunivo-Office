#!/usr/bin/env python3
"""Startet Lunivo Writer aus dem Projektordner:  python3 main.py [Datei.docx …]"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from framework.pruefung import importe as waechter  # noqa: E402

waechter.einhaengen()                                   # Schichtensperre: Richtungsregeln gelten ab hier für jeden Import

from vcl.qt.fenster.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
