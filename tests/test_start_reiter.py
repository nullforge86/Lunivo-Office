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


def test_suchen_feld_aufgeraeumt(app):
    """Unter dem Suchfeld: Pfeile und Trefferzahl, Optionen und Werkzeuge eingeklappt; Eingabe sucht weiter, Umschalt+Eingabe zurück."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    from lunivo_writer.ui.document.suchen_feld import SuchenFeld
    ed = DocumentEditor(); ed.setPlainText("eins zwei eins drei eins")
    f = SuchenFeld(lambda: ed, lambda d: False); f.resize(320, 600); f.show()
    assert not f.optionen_gruppe.ist_offen() and f.erweitern.text() == "Erweitern" and f.spezial_knopf.text() == "Spezial" and f.lese_knopf.text() == "Lesehervorhebung"
    f.erweitern.click(); assert f.erweitern.text() == "Reduzieren"; f.erweitern.click()
    f.suchfeld.setText("eins"); f.zaehlen()
    QTest.keyClick(f.suchfeld, Qt.Key_Return)
    erst = ed.textCursor().selectionStart()
    QTest.keyClick(f.suchfeld, Qt.Key_Return)
    assert ed.textCursor().selectionStart() > erst
    QTest.keyClick(f.suchfeld, Qt.Key_Return, Qt.ShiftModifier)
    assert ed.textCursor().selectionStart() == erst
    assert f.vorherige.accessibleName() and f.weiter.accessibleName()
    f.zeige("Ersetzen"); assert f.ersatz_bereich.isVisible()
    f.zeige("Suchen"); assert not f.ersatz_bereich.isVisible()
    zu = []; f.schliessen.connect(lambda: zu.append(1))
    QTest.keyClick(f, Qt.Key_Escape); assert zu


def test_unterstreichen_klappe_wirkt_am_text(app, tmp_path):
    """Menü am Knopf „Unterstrichen“: acht Linienarten, „Mehr Unterstreichungen …“, Untermenü „Unterstreichungsfarbe“ — jeder Eintrag wirkt."""
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QColor
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.baukasten.farbpalette import FarbPalette
    from lunivo_writer.ui.baukasten.linien import LinienZeile
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.show()
    ed = w.current_editor(); ed.setPlainText("Hallo"); ed.selectAll()
    b = w.befehle; m = b.menue_unterstrichKlappe()
    assert "Mehr Unterstreichungen" in " ".join(a.text() for a in m.actions())
    zeilen = m.findChildren(LinienZeile)
    assert len(zeilen) == 8
    keine = QTextCharFormat.UnderlineStyle.NoUnderline
    for z in zeilen:                                                    # jede Linienart wirkt am markierten Text
        ed.selectAll(); f = QTextCharFormat(); f.setUnderlineStyle(keine); ed._merge(f)
        z.angeklickt.emit()
        assert ed.textCursor().charFormat().underlineStyle() != keine
    pal = m.findChildren(FarbPalette)[0]
    assert pal.title() == "Unterstreichungsfarbe"
    ed.selectAll(); pal.gewaehlt.emit(QColor("#ff0000"))
    cf = ed.textCursor().charFormat()
    assert cf.underlineStyle() != keine and cf.underlineColor() == QColor("#ff0000")


def test_schriftart_fenster_wirkt_am_text(app, tmp_path):
    """Fenster „Schriftart“ (Mehr Unterstreichungen …): Felder beider Reiter landen im Zeichenformat des markierten Textes."""
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QColor
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.baukasten.schriftart_dialog import SchriftartDialog
    from lunivo_writer.ui.baukasten.text_format import zu_format
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.show()
    ed = w.current_editor(); ed.setPlainText("Hallo"); ed.selectAll()
    d = SchriftartDialog(w, {"groesse": 12.0})
    assert [d.reiter.tabText(i) for i in range(2)] == ["Schriftart", "Zeichenabstand"]
    assert d.standard_knopf.text().startswith("Standard") and d.effekt_knopf.text().startswith("Texteffekte")
    d.schrift.setCurrentText("Liberation Serif"); d.schnitt.setCurrentText("Fett Kursiv"); d.groesse.setCurrentText("14")
    d.unter.setCurrentIndex(d.unter.findData("doppelt")); d.unterfarbe.setFarbe("#00aa00")
    d.cb["durch"].setChecked(True); d.cb["hoch"].setChecked(True); d.skala.setCurrentText("150%")
    d.abstand_art.setCurrentIndex(1); d.abstand_wert.setValue(2.0)
    neu = d.werte()
    assert neu["fett"] and neu["kursiv"] and neu["groesse"] == 14 and neu["unter"] == "doppelt" and neu["durch"] and neu["hoch"] and neu["skala"] == 150
    ed._merge(zu_format(neu))
    f = ed.textCursor().charFormat()
    assert f.fontItalic() and f.fontWeight() >= 700 and f.fontStrikeOut() and f.font().pointSizeF() == 14 and f.fontLetterSpacing() != 100 or f.fontLetterSpacing() != 0
    assert "Liberation Serif" in f.fontFamilies() or f.fontFamily() == "Liberation Serif"
    assert f.underlineColor() == QColor("#00aa00") and f.verticalAlignment() == f.VerticalAlignment.AlignSuperScript


def test_durchgestrichen_klappe_wirkt_am_text(app, tmp_path):
    """Menü am Knopf „Durchgestrichen“: Durchgestrichen und Betonungszeichen — jeder Eintrag wirkt, der Knopf wiederholt die letzte Wahl."""
    from PySide6.QtCore import QSettings
    from lunivo_writer.editor.zusatz import P_BETONUNG
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.show()
    ed = w.current_editor(); ed.setPlainText("Hallo"); ed.selectAll()
    b = w.befehle; m = b.menue_durchKlappe()
    assert [a.text() for a in m.actions() if a.text()] == ["Durchgestrichen", "Betonungszeichen"]
    def cf():
        ed.selectAll(); return ed.textCursor().charFormat()
    m.actions()[0].trigger()
    assert cf().fontStrikeOut()
    m.actions()[0].trigger()
    assert not cf().fontStrikeOut()
    m.actions()[1].trigger()
    assert cf().stringProperty(P_BETONUNG)
    b.durchJetzt()                                                      # Knopf führt das zuletzt Gewählte aus (Betonung aus)
    assert not cf().stringProperty(P_BETONUNG)


def test_auswaehlen_klappe_beschriftung(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    m = w.befehle.menue_auswaehlenKlappe()
    assert [a.text().replace("\t", " | ") for a in m.actions()] == [
        "Alles auswählen | Strg+A", "Objekte auswählen", "Tabelle mit gestricheltem Rahmen auswählen",
        "Text mit ähnlicher Formatierung auswählen", "Auswahlbereich(&J)"]
    assert all(not a.icon().isNull() and a.isEnabled() for a in m.actions())


def test_abschnitt_einstellungen_wie_start(app):
    """Reiter Abschnitt: „Einstellungen“ öffnet dieselbe Klappe wie im Reiter Start."""
    import json
    from lunivo_writer.ui.ribbon.tabs import section_tab
    import lunivo_writer.ui.ribbon.tabs.baustein as bs
    reg = json.load(open(bs.__file__.replace("tabs/baustein.py", "../../resources/register.json"), encoding="utf-8"))
    gr = next(g for g in section_tab.bauen(reg)["gruppen"] if g["name"] == "Einstellungen")
    assert gr["knoepfe"][0]["klappe"] == "einstellungenKlappe"
