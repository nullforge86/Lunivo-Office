"""Tastaturbedienung der linken Dokumentnavigation."""
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QTreeWidgetItem

from lunivo_writer.ui.document.dokumentfenster.navigation import NavigationPanel


class _EditorAttrappe:
    def __init__(self):
        self.position = None

    def select_range(self, start, end):
        self.position = (start, end)

    def ensureCursorVisible(self):
        pass


def test_ueberschriften_navigation_folgt_pfeiltasten(app):
    editor = _EditorAttrappe()
    panel = NavigationPanel(lambda: editor)
    baum = panel.baum
    baum.addTopLevelItem(QTreeWidgetItem(["Kapitel eins"]))
    baum.topLevelItem(0).setData(0, Qt.UserRole, 10)
    baum.addTopLevelItem(QTreeWidgetItem(["Kapitel zwei"]))
    baum.topLevelItem(1).setData(0, Qt.UserRole, 42)
    panel.show()
    app.processEvents()

    assert baum.accessibleName() == "Dokumentüberschriften"
    assert baum.focusPolicy() == Qt.StrongFocus
    baum.setCurrentItem(baum.topLevelItem(0))
    assert editor.position == (10, 10)
    baum.setFocus()
    QTest.keyClick(baum, Qt.Key_Down)
    assert baum.currentItem() is baum.topLevelItem(1)
    assert editor.position == (42, 42)
