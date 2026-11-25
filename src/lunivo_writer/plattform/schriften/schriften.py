"""Schriftordner des Betriebssystems (Qt-frei). Die Textsatz-Schicht fragt hier, statt selbst nach dem System zu unterscheiden."""
from __future__ import annotations

import os
import sys


def schrift_ordner() -> tuple[str, ...]:
    """Übliche Schriftordner des Systems; weitere über die Umgebungsvariable ``LUNIVO_SCHRIFTEN`` (liest die Schriftdatenbank)."""
    if sys.platform == "win32":
        win = os.environ.get("WINDIR", r"C:\Windows")
        return (os.path.join(win, "Fonts"), os.path.join(os.environ.get("LOCALAPPDATA", "~"), "Microsoft", "Windows", "Fonts"))
    if sys.platform == "darwin":
        return ("/System/Library/Fonts", "/Library/Fonts", "~/Library/Fonts")
    return ("/usr/share/fonts", "/usr/local/share/fonts", "~/.fonts", "~/.local/share/fonts")
