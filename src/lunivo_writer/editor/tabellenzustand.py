"""Der Zustand der Schreibmarke gegenüber einer Tabelle - an einer Stelle festgelegt (keine Oberfläche).

    zustand(editor)                                      # einer der Namen unten
    tabellenmodus(editor, rechtsklick=False, per_griff=False)   # True = Tabellenfunktionen anbieten

Zustände: ``aussen`` (nicht in einer Tabelle) · ``text_in_zelle`` (Schreibmarke oder Text innerhalb einer Zelle) · ``mehrere_zellen`` ·
``ganze_tabelle`` · ``einzelzelle_ganz`` (Tabelle mit nur einer Zelle, deren Inhalt ganz markiert ist) · ``nur_lesen``.

Regel: Tabellenfunktionen bei mehreren Zellen, ganzer Tabelle, über den Verschiebegriff und beim Rechtsklick ohne Textmarkierung in einer Zelle.
Nur Textfunktionen bei Text in einer Zelle oder außerhalb; nie im Nur-Lesen-Modus.
"""
from __future__ import annotations

AUSSEN, TEXT_IN_ZELLE, MEHRERE_ZELLEN, GANZE_TABELLE, EINZELZELLE_GANZ, NUR_LESEN = (
    "aussen", "text_in_zelle", "mehrere_zellen", "ganze_tabelle", "einzelzelle_ganz", "nur_lesen")


def zustand(editor) -> str:
    if editor is None:
        return AUSSEN
    if editor.isReadOnly():
        return NUR_LESEN
    c = editor.textCursor()
    t = c.currentTable()
    if t is None:
        return AUSSEN
    if not c.hasSelection():
        return TEXT_IN_ZELLE
    a, e = t.cellAt(c.selectionStart()), t.cellAt(c.selectionEnd())
    if (a.row(), a.column()) == (e.row(), e.column()):
        _r, zeilen, _k, spalten = c.selectedTableCells()                      # Qt meldet auch eine einzelne, ganz markierte Zelle als 1 x 1
        if not (zeilen > 0 and spalten > 0 and zeilen * spalten > 1):
            if t.rows() * t.columns() == 1 and c.selectionStart() <= a.firstPosition() and c.selectionEnd() >= a.lastPosition():
                return EINZELZELLE_GANZ
            return TEXT_IN_ZELLE
    else:
        _r, zeilen, _k, spalten = c.selectedTableCells()
    return GANZE_TABELLE if zeilen >= t.rows() and spalten >= t.columns() else MEHRERE_ZELLEN


def tabellenmodus(editor, rechtsklick: bool = False, per_griff: bool = False) -> bool:
    """``True``, wenn Tabellenfunktionen (Einfügen/Löschen, Rahmen, Schattierung …) angeboten werden."""
    z = zustand(editor)
    if z in (AUSSEN, NUR_LESEN):
        return False
    if per_griff:                                                  # Verschiebegriff: auch bei einer Tabelle mit nur einer Zelle
        return True
    if z in (MEHRERE_ZELLEN, GANZE_TABELLE):
        return True
    if z == TEXT_IN_ZELLE:
        return bool(rechtsklick) and not editor.textCursor().hasSelection()
    return False                                                   # einzelzelle_ganz ohne Griff: nur Text
