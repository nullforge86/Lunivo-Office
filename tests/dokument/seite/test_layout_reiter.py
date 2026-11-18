"""Reiter Seitenlayout (Anordnung wie in der Vorlage): Maßfelder für die Ränder, Spalten 1 bis 4."""
from PySide6.QtCore import QSettings

from lunivo_writer.dienste.einstellungen_dienst import Settings
from lunivo_writer.oberflaeche.programmfenster import MainWindow


def fenster(tmp_path):
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.show()
    w.new_document()
    return w








