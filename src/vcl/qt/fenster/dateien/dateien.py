"""Dateien, Vorlagen, Wiederherstellung."""
from __future__ import annotations

from vcl.qt.fenster.dateien.dateien_oeffnen import DateienOeffnenBaustein
from vcl.qt.fenster.dateien.dateien_drucken import DateienDruckenBaustein
from vcl.qt.fenster.dateien.dateien_vorlagen import DateienVorlagenBaustein
from vcl.qt.fenster.dateien.dateien_speichern import DateienSpeichernBaustein
from vcl.qt.fenster.dateien.dateien_export import DateienExportBaustein
from vcl.qt.fenster.dateien.dateien_reiter import DateienReiterBaustein


class DateienBaustein(DateienOeffnenBaustein, DateienVorlagenBaustein, DateienSpeichernBaustein, DateienExportBaustein, DateienDruckenBaustein, DateienReiterBaustein):
    """Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``)."""


