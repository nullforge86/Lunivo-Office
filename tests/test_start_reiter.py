"""Reiter Start nach den Vorlagen: Suchmaschine, Gehe zu, Wort-Extras, Text sortieren und die Klappmenüs des Bandes."""
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextDocument


def _doc(text):
    d = QTextDocument(); d.setPlainText(text)
    return d


def test_suche_optionen_und_platzhalter(app):
    from lunivo_writer.editor import suche as S
    d = _doc("Haus haus Hausboot Gartenhaus\nZweite Zeile")
    assert len(S.treffer(d, S.Suchauftrag("haus"))) == 4
    assert len(S.treffer(d, S.Suchauftrag("haus", gross=True))) == 2
    assert len(S.treffer(d, S.Suchauftrag("haus", ganz=True))) == 2
    assert len(S.treffer(d, S.Suchauftrag("haus", praefix=True))) == 3
    assert len(S.treffer(d, S.Suchauftrag("haus", suffix=True))) == 3
    assert len(S.treffer(d, S.Suchauftrag("H?us", platzhalter=True, gross=True))) == 2
    assert len(S.treffer(d, S.Suchauftrag("haus^pZweite"))) == 1                 # ^p findet die Absatzmarke
    assert S.naechster(d, S.Suchauftrag("haus"), 25) == (25, 29)
    assert S.naechster(d, S.Suchauftrag("haus"), 26) == (0, 4)                   # am Ende geht es vorn weiter
    assert S.naechster(d, S.Suchauftrag("haus"), 26, umlauf=False) is None


def test_suche_ersetzen_und_formate(app):
    from lunivo_writer.editor import suche as S
    d = _doc("eins zwei eins")
    assert S.ersatz_text(S.Suchauftrag("eins"), "[^&]", "eins") == "[eins]"
    assert S.alle_ersetzen(d, S.Suchauftrag("eins"), "drei") == 2 and d.toPlainText() == "drei zwei drei"
    d.undo()
    assert d.toPlainText() == "eins zwei eins"                                   # ein einziger Rückgängig-Schritt
    c = QTextCursor(d); c.setPosition(5); c.setPosition(9, QTextCursor.KeepAnchor)
    f = QTextCharFormat(); f.setFontWeight(QFont.Bold); c.mergeCharFormat(f)
    fett = S.Suchauftrag("", zeichen=[lambda cf: cf.fontWeight() >= QFont.Bold])
    assert S.treffer(d, fett) == [(5, 9)]                                         # nur nach Format suchen


def test_gehe_zu_ziel(app):
    from lunivo_writer.editor import gehe_zu as G
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    ed = DocumentEditor(); ed.setPlainText("\n".join(f"Zeile {i}" for i in range(1, 11)))
    assert len(G.ELEMENTE) == 13
    p = G.ziel(ed, "Zeile", "4")
    assert ed.document().findBlock(p).text() == "Zeile 4"
    G.springen(ed, p)
    assert ed.document().findBlock(G.ziel(ed, "Zeile", "+2")).text() == "Zeile 6"
    assert ed.document().findBlock(G.ziel(ed, "Zeile", "", -1)).text() == "Zeile 3"


def test_wort_extras_neue_eintraege(app):
    from lunivo_writer.editor import wortextras as W
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    ed = DocumentEditor(); ed.setPlainText("   eins\n\tzwei")
    assert W.fuehrende_leerzeichen_loeschen(ed) == 2 and ed.toPlainText() == "eins\nzwei"
    ed.setPlainText(f"a{W.ZEILENUMBRUCH}b")
    assert W.zeilenumbrueche_loeschen(ed) == 1 and ed.toPlainText() == "a b"
    ed.setPlainText("a\nb\nc")
    W.leerabsatz_modus_wechseln(ed); assert ed.document().blockCount() == 5      # leere Absätze dazwischen
    W.leerabsatz_modus_wechseln(ed); assert ed.document().blockCount() == 3      # und wieder weg
    eintraege = [e for e in W.MENUE if e != "-"]
    assert eintraege[0][0] == "Absätze neu anordnen" and any(isinstance(e[2], list) for e in eintraege)   # „Löschen“ ist ein Untermenü


def test_text_sortieren(app):
    from lunivo_writer.editor import schreibweise as S
    from lunivo_writer.ui.baukasten.sortieren_dialog import SortierenDialog, SortierOptionenDialog
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
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
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
    from lunivo_writer.ui.baukasten.schriftart_dialog import SchriftartDialog
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
