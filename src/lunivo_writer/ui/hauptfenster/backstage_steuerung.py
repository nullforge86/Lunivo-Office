"""Zusammensetzung der Backstage-Bausteine."""
from __future__ import annotations

from lunivo_writer.ui.hauptfenster.backstage_objektformat import BackstageObjektformatBaustein
from lunivo_writer.ui.hauptfenster.backstage_dokument import BackstageDokumentBaustein
from lunivo_writer.ui.hauptfenster.backstage_seitenleisten import BackstageSeitenleistenBaustein
from lunivo_writer.ui.hauptfenster.backstage_navigation import BackstageNavigationBaustein
from lunivo_writer.ui.hauptfenster.backstage_fenster import BackstageFensterBaustein


class BackstageBaustein(
    BackstageObjektformatBaustein,
    BackstageDokumentBaustein,
    BackstageSeitenleistenBaustein,
    BackstageNavigationBaustein,
    BackstageFensterBaustein,
):
    """Datei-Ansicht (Backstage). Baustein von MainWindow."""
