"""Qt-unabhängiger Kern von Lunivo: Geometrie, später Dokumentenmodell, Textlayout, Layout und Rendering.

Regel (Architektur, siehe ``dokumentation/architektur/qt-entkopplung.md``): Nichts in ``core`` importiert PySide6, PyQt oder Qt-Datentypen —
weder im Code noch in öffentlichen Schnittstellen. Der Wächtertest ``tests/architektur/test_core_ohne_qt.py`` prüft das.
Abhängigkeitsrichtung: ``oberflaeche → adapter/qt → core``; innerhalb von ``core``: document → textlayout → layout → rendering.

ARCHITEKTURSPERRE (verbindlich): ``core`` und ``modelle`` sowie die Qt-freien Dokument-Adapter in ``dienste`` (Liste ``GESCHUETZT_DATEIEN`` in
``werkzeuge/pruefungen/architekturpruefung.py``) bleiben frei von PySide6/PyQt, von Qt-Dokumentklassen (``QTextDocument``, ``QTextCursor``, ``QTextEdit``,
``QPlainTextEdit``, ``QTextBlock``, ``QTextFrame``, ``QTextTable``, ``QTextLayout``, ``QTextDocumentLayout``) und von Abhängigkeiten auf Oberfläche,
``adapter``, ``kern`` oder ``editor`` — auch über Zwischenmodule. Nie: Kern → GUI, Kern → Qt-Dokumentklassen, Layout/Textsatz → Qt-Textlayout, Import/Export →
zweite (Qt-)Dokument-Engine oder Qt-Rückfallweg. Qt-Zeichnen gehört in ``adapter/qt``; neue Ausnahmen nur mit Genehmigung des Eigentümers.
Technische Durchsetzung: ``architekturpruefung.py`` (statisch) und ``architektursperre_hook.py`` (blockiert Änderungen mit neuem Verstoß)."""


__all__ = [
    "document",
    "geometry",
    "textlayout",
    "editing",
    "layout",
    "rendering",
]
