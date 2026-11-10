"""Accessibility-Namen der Dokumentreiterleiste."""
from PySide6.QtWidgets import QToolButton

from lunivo_writer.ui.document.dokumentfenster.document_tabs import DocTabs


def test_neues_dokument_knopf_hat_accessible_name(app):
    tabs = DocTabs()
    knopf = tabs.leiste.findChild(QToolButton)
    assert knopf is not None
    assert knopf.accessibleName() == "Neues Dokument"
