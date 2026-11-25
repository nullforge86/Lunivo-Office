"""Zusammensetzung der Backstage-Bausteine."""
from __future__ import annotations

from vcl.qt.widgets.menues.backstage.backstage_objektformat import BackstageObjektformatBaustein
from vcl.qt.widgets.menues.backstage.backstage_dokument import BackstageDokumentBaustein
from vcl.qt.widgets.menues.backstage.backstage_seitenleisten import BackstageSeitenleistenBaustein
from vcl.qt.widgets.menues.backstage.backstage_navigation import BackstageNavigationBaustein
from vcl.qt.widgets.menues.backstage.backstage_fenster import BackstageFensterBaustein


class BackstageBaustein(
    BackstageObjektformatBaustein,
    BackstageDokumentBaustein,
    BackstageSeitenleistenBaustein,
    BackstageNavigationBaustein,
    BackstageFensterBaustein,
):
    """Datei-Ansicht (Backstage). Baustein von MainWindow."""
