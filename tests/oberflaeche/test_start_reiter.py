"""Reiter Start nach den Vorlagen: Suchmaschine, Gehe zu, Wort-Extras, Text sortieren und die Klappmenüs des Bandes."""
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextDocument


def _doc(text):
    d = QTextDocument(); d.setPlainText(text)
    return d










def test_text_sortieren(app):
    from lunivo_writer.editor.text import schreibweise as S
    from lunivo_writer.oberflaeche.baukasten.dokument.sortieren_dialog import SortierenDialog, SortierOptionenDialog
    t = ["Name\tAlter", "Özil\t30", "apfel\t5", "Zebra\t12"]
    assert [t[i] for i in S.reihenfolge(t, [(None, "text", False)], kopfzeile=True)] == ["Name\tAlter", "apfel\t5", "Özil\t30", "Zebra\t12"]
    assert [t[i] for i in S.reihenfolge(t, [(1, "zahl", True)], kopfzeile=True)][1] == "Özil\t30"
    d = _doc("c\nb\na")
    c = QTextCursor(d); c.setPosition(2); c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
    f = QTextCharFormat(); f.setFontWeight(QFont.Bold); c.mergeCharFormat(f)
    b = S.absaetze(d)
    S.umstellen(d, b, S.reihenfolge([x.text() for x in b], [(None, "text", False)]))
    assert d.toPlainText() == "a\nb\nc" and d.findBlockByNumber(1).begin().fragment().charFormat().fontWeight() == QFont.Bold
    dlg = SortierenDialog(None, t)
    assert dlg.schluessel[0].feld.count() == 3 and dlg.schluessel[1].feld.isEnabled()        # Absätze, Feld 1, Feld 2
    assert SortierenDialog(None, ["a", "b"]).schluessel[1].feld.isEnabled() is False          # ohne Felder kein „Anschließend nach“
    assert SortierOptionenDialog(None, ";").trenner() == ";"


def test_start_klappmenues(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.show()
    b = w.befehle
    erwartet = {"einfuegenKlappe": "Unformatierter Text", "unterstrichKlappe": "Mehr Unterstreichungen", "durchKlappe": "Betonungszeichen",
                "wortExtrasKlappe": "Absätze neu anordnen", "suchenKlappe": "Gehe zu", "auswaehlenKlappe": "Auswahlbereich",
                "einstellungenKlappe": "Formatvorlagen und Formatierung"}
    for klappe, text in erwartet.items():
        m = getattr(b, "menue_" + klappe)()
        texte = " | ".join(a.text() for a in m.actions())
        assert text in texte or any(text in (a.toolTip() or "") for a in m.actions()) or text in str([c.text() for c in m.findChildren(object)
                                                                                                        if hasattr(c, "text")]), klappe
    rechts = (w.sidebar.isVisible(), w.sidebar.stapel.currentWidget(), w.sidebar.werk_stapel.currentWidget())
    b.tun("suchen", None)
    assert w.navigation.isVisible() and w.navigation.aktuelle_seite == "suche"
    assert (w.sidebar.isVisible(), w.sidebar.stapel.currentWidget(), w.sidebar.werk_stapel.currentWidget()) == rechts   # rechts ändert sich nichts
    from PySide6.QtCore import QTimer
    from lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog import SchriftartDialog
    gesehen = []

    def pruefen():                                                             # Format ▸ Schriftart öffnet sich links, rechts bleibt alles
        d = next(x for x in w.navigation.findChildren(SchriftartDialog))
        gesehen.append((w.navigation.stapel._zusatz_seite is not None,
                        (w.sidebar.stapel.currentWidget(), w.sidebar.werk_stapel.currentWidget()) == rechts[1:]))
        d.reject()
    QTimer.singleShot(0, pruefen)
    w.navigation.suchen_feld._format_schrift()
    assert gesehen == [(True, True)]
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


