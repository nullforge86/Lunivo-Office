"""RTF direkt lesen — ohne Umwandlungsprogramm (Microsoft RTF 1.9).

Der Zerleger sammelt Text, Formate, Tabellen und Bildbytes Qt-frei. Der Modell-Leser
setzt diese direkt in ``core.document`` um; nur Bilder in Kopf-/Fußzeilen nutzen
noch den Qt-Rückfall. 15 Twip = 1 px bei 96 dpi.
"""
from lunivo_writer.dienste.rtf.leser import read_rtf

__all__ = ["read_rtf"]
