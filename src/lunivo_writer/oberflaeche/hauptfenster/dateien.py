"""Dateien, Vorlagen, Wiederherstellung."""
from __future__ import annotations

from lunivo_writer.oberflaeche.hauptfenster.dateien_oeffnen import DateienOeffnenBaustein
from lunivo_writer.oberflaeche.hauptfenster.dateien_drucken import DateienDruckenBaustein
from lunivo_writer.oberflaeche.hauptfenster.dateien_vorlagen import DateienVorlagenBaustein
from lunivo_writer.oberflaeche.hauptfenster.dateien_speichern import DateienSpeichernBaustein
from lunivo_writer.oberflaeche.hauptfenster.dateien_export import DateienExportBaustein
from lunivo_writer.oberflaeche.hauptfenster.dateien_reiter import DateienReiterBaustein


class DateienBaustein(DateienOeffnenBaustein, DateienVorlagenBaustein, DateienSpeichernBaustein, DateienExportBaustein, DateienDruckenBaustein, DateienReiterBaustein):
    """Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``)."""


