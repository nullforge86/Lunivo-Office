"""Dateien, Vorlagen, Wiederherstellung."""
from __future__ import annotations

from lunivo_writer.ui.hauptfenster.dateien_oeffnen import DateienOeffnenBaustein
from lunivo_writer.ui.hauptfenster.dateien_drucken import DateienDruckenBaustein
from lunivo_writer.ui.hauptfenster.dateien_vorlagen import DateienVorlagenBaustein
from lunivo_writer.ui.hauptfenster.dateien_speichern import DateienSpeichernBaustein
from lunivo_writer.ui.hauptfenster.dateien_export import DateienExportBaustein
from lunivo_writer.ui.hauptfenster.dateien_reiter import DateienReiterBaustein


class DateienBaustein(DateienOeffnenBaustein, DateienVorlagenBaustein, DateienSpeichernBaustein, DateienExportBaustein, DateienDruckenBaustein, DateienReiterBaustein):
    """Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""


