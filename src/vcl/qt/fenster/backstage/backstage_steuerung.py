"""Zusammensetzung der Backstage-Bausteine."""
from __future__ import annotations

from vcl.qt.fenster.backstage.backstage_objektformat import BackstageObjektformatBaustein
from vcl.qt.fenster.backstage.backstage_dokument import BackstageDokumentBaustein
from vcl.qt.fenster.backstage.backstage_seitenleisten import BackstageSeitenleistenBaustein
from vcl.qt.fenster.backstage.backstage_navigation import BackstageNavigationBaustein
from vcl.qt.fenster.backstage.backstage_fenster import BackstageFensterBaustein


class BackstageBaustein(
    BackstageObjektformatBaustein,
    BackstageDokumentBaustein,
    BackstageSeitenleistenBaustein,
    BackstageNavigationBaustein,
    BackstageFensterBaustein,
):
    """Datei-Ansicht (Backstage). Baustein von MainWindow."""
