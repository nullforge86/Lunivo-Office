"""Einfügen ▸ Leere Seite: ein neues, leeres Blatt HINTER der Seite der Schreibmarke. Der vorhandene Text wird nicht geteilt.

    leere_seite(doc, letzter_block, einrichtung, quer=None)   # → Cursor auf dem neuen Blatt

``letzter_block`` ist der letzte Absatz, der auf der aktuellen Seite beginnt (``DocumentEditor.seite_letzter_block``). Hat das neue Blatt
dieselbe Ausrichtung wie der Abschnitt, genügen Seitenumbrüche; sonst bekommt es einen eigenen Abschnitt (wie Hoch-/Querformat in DOCX),
und der Text danach geht in der alten Ausrichtung weiter. Alles ist ein Schritt für Rückgängig.
"""
from __future__ import annotations

from PySide6.QtGui import QTextBlock, QTextBlockFormat, QTextCursor, QTextFormat

from lunivo_writer.editor import abschnitte as AB
from lunivo_writer.models.page import PageSettings


def _umbruch_davor(block: QTextBlock) -> None:
    c = QTextCursor(block)
    bf = c.blockFormat(); bf.setPageBreakPolicy(bf.pageBreakPolicy() | QTextFormat.PageBreak_AlwaysBefore); c.setBlockFormat(bf)


def leere_seite(doc, letzter: QTextBlock, einrichtung: PageSettings, quer: bool | None = None) -> QTextCursor:
    eigene = quer is not None and bool(quer) != einrichtung.landscape
    c = QTextCursor(letzter); c.movePosition(QTextCursor.EndOfBlock)
    c.beginEditBlock()
    vorher = letzter.blockFormat().property(AB.B_ABSCHNITT) if letzter.blockFormat().hasProperty(AB.B_ABSCHNITT) else None
    leer = QTextBlockFormat()
    leer.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)          # auch im eigenen Abschnitt: die Bearbeitungsansicht kennt nur Umbrüche
    c.insertBlock(leer, letzter.charFormat())
    neu = QTextCursor(c)                                         # steht im neuen, leeren Absatz
    davor = QTextCursor(letzter)
    AB._setze(neu, vorher)                                       # ein Abschnittsende am alten Absatz wandert ans neue Blatt
    if eigene:
        blatt = einrichtung.copy(); blatt.set_orientation(bool(quer))
        AB._setze(davor, AB.eintrag("naechste", blatt))          # das neue Blatt ist ein eigener Abschnitt …
        if vorher is None and neu.block().next().isValid():
            AB._setze(neu, AB.eintrag("naechste", einrichtung))  # … danach geht es wie vorher weiter
    else:
        AB._setze(davor, None)
    if neu.block().next().isValid():
        _umbruch_davor(neu.block().next())                       # der Text danach beginnt wieder auf einem eigenen Blatt
    c.endEditBlock()
    return neu
