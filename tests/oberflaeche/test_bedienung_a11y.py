"""Barrierefreiheit der Programmoberfläche (nicht der Dokumente — das prüft proofing/barrierefreiheit.py):
Namen für Bildschirmleser, Tastaturerreichbarkeit, erlaubte Ausnahmen mit Begründung."""
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (QAbstractSpinBox, QCheckBox, QComboBox, QLineEdit, QPushButton, QRadioButton, QSlider, QToolButton, QWidget)

from lunivo_writer.services.settings_service import Settings
from lunivo_writer.ui.main_window import MainWindow

ARTEN = (QPushButton, QToolButton, QComboBox, QCheckBox, QRadioButton, QSlider, QAbstractSpinBox, QLineEdit)
# Bedienelemente, die bewusst nicht per Tab erreichbar sind; der Tastaturweg steht daneben. Die Liste darf nur kleiner werden.
OHNE_FOKUS_ERLAUBT = {
    "ui/widgets/mini_leiste.py": "schwebende Leiste über dem Text, nimmt dem Text den Fokus nicht; Tastenkürzel für Fett/Kursiv/Schrift",
    "ui/document/tabelle_griffe.py": "Maus-Ziehgriffe der Tabelle; Tastaturweg über das Tabellen-Fenster",
    "ui/document/absatz_symbol.py": "Maus-Symbol am Absatz; dieselben Befehle stehen im Band",
    "ui/document/document_editor.py": "Vorschlags-Popup: der Fokus bleibt im Editor, Auswahl mit Strg+1…6",
}
MAX_OHNE_NAMEN = 28            # verborgene Panels des Hauptfensters; Ziel 0, darf nur sinken


def _fenster(tmp_path):
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.show(); w.new_document()
    return w


def _namenlos(w):
    r = []
    for x in w.findChildren(QWidget):
        if not isinstance(x, ARTEN) or (isinstance(x, QLineEdit) and isinstance(x.parentWidget(), (QComboBox, QAbstractSpinBox))):
            continue
        name = x.accessibleName() or (x.text() if isinstance(x, (QPushButton, QToolButton, QCheckBox, QRadioButton)) else "") or x.toolTip()
        if not name:
            r.append(x)
    return r


def test_sichtbare_bedienelemente_haben_namen(app, tmp_path):
    w = _fenster(tmp_path)
    app.processEvents()
    ohne = _namenlos(w)
    sichtbar = [type(x).__name__ for x in ohne if x.isVisibleTo(w) and x.objectName() != "qt_menubar_ext_button"]
    assert sichtbar == [], f"sichtbare Bedienelemente ohne Namen: {sichtbar}"
    assert len(ohne) <= MAX_OHNE_NAMEN


def test_wichtige_felder_des_bandes_sind_benannt(app, tmp_path):
    w = _fenster(tmp_path)
    namen = {x.accessibleName() for x in w.findChildren(QComboBox)} | {x.accessibleName() for x in w.findChildren(QSlider)}
    assert {"Schriftart", "Schriftgröße", "Formatvorlage", "Zoom"} <= namen


def test_nicht_fokussierbare_stellen_sind_begruendet():
    """Jede Datei mit ``Qt.NoFocus`` steht in der Ausnahmeliste (mit Begründung); neue Stellen brauchen einen Eintrag hier."""
    import os
    import lunivo_writer
    paket = os.path.dirname(lunivo_writer.__file__)
    gefunden = set()
    for wurzel, _o, dateien in os.walk(paket):
        for n in dateien:
            if n.endswith(".py"):
                pfad = os.path.join(wurzel, n)
                with open(pfad, encoding="utf-8") as fh:
                    if "setFocusPolicy(Qt.NoFocus)" in fh.read():
                        gefunden.add(os.path.relpath(pfad, paket).replace(os.sep, "/"))
    assert gefunden <= set(OHNE_FOKUS_ERLAUBT), f"neue Stellen ohne Fokus: {sorted(gefunden - set(OHNE_FOKUS_ERLAUBT))}"
    assert set(OHNE_FOKUS_ERLAUBT) <= gefunden, f"aus der Liste streichen: {sorted(set(OHNE_FOKUS_ERLAUBT) - gefunden)}"


def test_funktionszeile_nennt_art_zustand_und_kuerzel(app, tmp_path):
    from lunivo_writer.ui.baukasten.controls.werkbank import FunktionsZeile
    w = _fenster(tmp_path)
    zeilen = w.findChildren(FunktionsZeile)
    assert zeilen and all(z.accessibleName() and z.accessibleDescription() for z in zeilen)
    schalter = [z for z in zeilen if z.f.art == "schalter"]
    assert schalter and all(d.accessibleDescription().startswith("Schalter, ") for d in schalter)
    mit_kuerzel = [z for z in zeilen if z.f.kuerzel]
    assert not mit_kuerzel or all("Tastenkürzel" in z.accessibleDescription() for z in mit_kuerzel)
