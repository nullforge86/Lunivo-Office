"""Qt-unabhängiger Kern von Lunivo: Geometrie, später Dokumentenmodell, Textlayout, Layout und Rendering.

Regel (Architektur, siehe ``dokumentation/architektur/qt-entkopplung.md``): Nichts in ``core`` importiert PySide6, PyQt oder Qt-Datentypen —
weder im Code noch in öffentlichen Schnittstellen. Der Wächtertest ``tests/architektur/test_core_ohne_qt.py`` prüft das.
Abhängigkeitsrichtung: ``oberflaeche → adapter/qt → core``; innerhalb von ``core``: document → textlayout → layout → rendering."""
