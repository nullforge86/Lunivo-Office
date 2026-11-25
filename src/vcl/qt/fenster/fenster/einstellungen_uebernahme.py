"""Einmalige Übernahme der früheren QSettings-Werte in die JSON-Einstellungen.

Das braucht QSettings und liegt deshalb in der Oberfläche; geschrieben wird über das Framework. Nach der Übernahme (Marke in der JSON-Datei)
wird QSettings nie mehr gelesen – es gibt keinen dauerhaften Rückfallweg."""
from __future__ import annotations

from PySide6.QtCore import QByteArray, QSettings

from framework.schnittstellen.einstellungen import ORGANISATION, PROGRAMM, Einstellungen


def _umwandeln(wert):
    if isinstance(wert, QByteArray):
        return bytes(wert.toBase64()).decode("ascii")             # JSON kennt keine Bytes; die Oberfläche liest sie als Base64 zurück
    if isinstance(wert, (list, tuple)):
        return [_umwandeln(w) for w in wert]
    if isinstance(wert, (bool, int, float, str)) or wert is None:
        return wert
    return str(wert)


def einmalig_uebernehmen(einstellungen: Einstellungen) -> int:
    """Übernimmt alle QSettings-Werte beim ersten Start; gibt die Zahl der übernommenen Werte zurück (0, wenn schon geschehen)."""
    if einstellungen.qsettings_uebernommen():
        return 0
    q = QSettings(ORGANISATION, PROGRAMM)
    werte = {schluessel: _umwandeln(q.value(schluessel)) for schluessel in q.allKeys()}
    einstellungen.uebernehmen(werte)
    return len(werte)
