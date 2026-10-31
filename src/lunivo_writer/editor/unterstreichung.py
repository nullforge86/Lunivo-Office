"""Unterstreichungsarten als Zeichenformat: was Qt selbst zeichnet und was Lunivo zeichnet (``P_UNTER``). Ohne Oberfläche."""
from __future__ import annotations

from PySide6.QtGui import QTextCharFormat

# Was Qt selbst unterstreicht; alle anderen Arten zeichnet Lunivo (``P_UNTER``) und lässt Qt eine einfache Linie als Rückfall setzen
_UNTER_QT = {"einfach": QTextCharFormat.SingleUnderline, "gepunktet": QTextCharFormat.DotLine, "gestrichelt": QTextCharFormat.DashUnderline,
             "strichpunkt": QTextCharFormat.DashDotLine, "strichpunktpunkt": QTextCharFormat.DashDotDotLine, "wellig": QTextCharFormat.WaveUnderline}
_UNTER_RUECKFALL = {"doppelt": QTextCharFormat.SingleUnderline, "dick": QTextCharFormat.SingleUnderline, "dick_gepunktet": QTextCharFormat.DotLine,
                    "dick_gestrichelt": QTextCharFormat.DashUnderline, "lang": QTextCharFormat.DashUnderline, "dick_lang": QTextCharFormat.DashUnderline,
                    "dick_strichpunkt": QTextCharFormat.DashDotLine, "dick_strichpunktpunkt": QTextCharFormat.DashDotDotLine,
                    "dick_wellig": QTextCharFormat.WaveUnderline, "doppelwellig": QTextCharFormat.WaveUnderline, "woerter": QTextCharFormat.NoUnderline}


def unter_format(art: str) -> QTextCharFormat:
    """Nur die Unterstreichung als Zeichenformat (zum Zusammenführen, ohne anderes anzufassen)."""
    from lunivo_writer.editor.zusatz import P_UNTER
    f = QTextCharFormat()
    f.setUnderlineStyle(_UNTER_QT.get(art) or _UNTER_RUECKFALL.get(art, QTextCharFormat.NoUnderline))
    f.setProperty(P_UNTER, art if art in _UNTER_RUECKFALL else "")                    # nur die Arten, die Lunivo selbst zeichnet
    return f
